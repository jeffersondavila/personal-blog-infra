"""Matriz de casos de la identidad operativa y un evaluador offline de sus politicas.

Por que existe (H-031-IAM, hallazgo S-10)
-----------------------------------------
La simulacion contra el rol ya creado descubrio que `ec2:CreateVpcEndpoint` de un
servicio distinto de S3 salia `allowed` cuando el contexto traia `aws:ResourceTag`.
Las pruebas offline no lo veian porque solo inspeccionaban la FORMA de la politica,
nunca sus decisiones.

Este modulo da a las pruebas offline la misma matriz que despues ejecuta el
simulador de IAM (`simulate-custom-policy`), con UN solo origen de verdad: los casos
viven aqui y el runner privado los importa. El evaluador modela EXACTAMENTE los
operadores que usan las tres politicas de fase 1 y aborta ante cualquier otro: si una
plantilla introduce un operador nuevo, la prueba falla en lugar de adivinar.

Contexto PESIMISTA, igual que el simulador: las claves se aplican tal como se dan,
sin preguntar si AWS las rellenaria para ese recurso. Asi una politica solo pasa si
es segura aunque el contexto traiga mas de lo que AWS aportaria.

No sustituye al simulador de IAM ni al readback: los complementa y los anticipa.
"""
import fnmatch

REGION = "us-east-2"
OTRA_CUENTA = "999999999999"

#: Claves de condicion de `ec2:CreateVpcEndpoint` y `ec2:ModifyVpcEndpoint` por tipo de
#: recurso, copiadas de la referencia oficial de servicios de AWS
#: (`servicereference.us-east-1.amazonaws.com/v1/ec2/ec2.json`, descargada el
#: 2026-10-03, SHA-256 e4ef8c6a50fab1fac407e7756a538d3ce5d60f08f1dbd169006e8db9f3ec5184).
#: `aws:RequestedRegion` es global y vale para todas.
CLAVES_POR_RECURSO = {
    "ec2:CreateVpcEndpoint": {
        "route-table": {"aws:ResourceTag/${TagKey}", "ec2:ResourceTag/${TagKey}", "ec2:RouteTableID"},
        "security-group": {"aws:ResourceTag/${TagKey}", "ec2:ResourceTag/${TagKey}", "ec2:SecurityGroupID"},
        "subnet": {"aws:ResourceTag/${TagKey}", "ec2:ResourceTag/${TagKey}", "ec2:SubnetID"},
        "vpc": {"aws:ResourceTag/${TagKey}", "ec2:ResourceTag/${TagKey}", "ec2:VpcID"},
        "vpc-endpoint": {"aws:RequestTag/${TagKey}", "aws:TagKeys", "ec2:VpceMultiRegion",
                         "ec2:VpcePrivateDnsPreference", "ec2:VpcePrivateDnsSpecifiedDomains",
                         "ec2:VpceServiceName", "ec2:VpceServiceOwner", "ec2:VpceServiceRegion"},
    },
    "ec2:ModifyVpcEndpoint": {
        "route-table": {"aws:ResourceTag/${TagKey}", "ec2:ResourceTag/${TagKey}", "ec2:RouteTableID"},
        "security-group": {"aws:ResourceTag/${TagKey}", "ec2:ResourceTag/${TagKey}", "ec2:SecurityGroupID", "ec2:Vpc"},
        "subnet": {"aws:ResourceTag/${TagKey}", "ec2:AvailabilityZone", "ec2:AvailabilityZoneId",
                   "ec2:ResourceTag/${TagKey}", "ec2:SubnetID", "ec2:Vpc"},
        "vpc-endpoint": {"aws:ResourceTag/${TagKey}", "ec2:Attribute", "ec2:Attribute/${AttributeName}",
                         "ec2:ResourceTag/${TagKey}", "ec2:VpceMultiRegion", "ec2:VpceServiceRegion"},
    },
}
CLAVES_GLOBALES = {"aws:RequestedRegion"}

#: Recursos que un gateway endpoint de S3 hace autorizar: el endpoint nuevo, su VPC y
#: las tablas de rutas asociadas. `subnet` y `security-group` solo intervienen en los
#: endpoints de interfaz y de Gateway Load Balancer.
RECURSOS_DEL_GATEWAY_S3 = {"vpc-endpoint", "vpc", "route-table"}

OPERADORES = ("StringEquals", "StringEqualsIfExists", "ForAllValues:StringEquals", "Bool")


def _lista(valor):
    return valor if isinstance(valor, list) else [valor]


def _cumple(operador, bloque, contexto):
    for clave, esperado in bloque.items():
        esperados = [str(v) for v in _lista(esperado)]
        presente = clave in contexto
        valores = [str(v) for v in _lista(contexto.get(clave, []))]
        if operador == "StringEquals":
            if not presente or not any(v in esperados for v in valores):
                return False
        elif operador == "StringEqualsIfExists":
            if presente and not any(v in esperados for v in valores):
                return False
        elif operador == "ForAllValues:StringEquals":
            # Semantica de IAM: con la clave ausente, ForAllValues es verdadero.
            if presente and not all(v in esperados for v in valores):
                return False
        elif operador == "Bool":
            if not presente or not any(v.lower() in [e.lower() for e in esperados] for v in valores):
                return False
        else:
            raise ValueError(f"operador no modelado: {operador}")
    return True


def evaluar(documentos, accion, recurso, contexto):
    """Decision de IAM para UNA accion sobre UN recurso: allowed, explicitDeny o implicitDeny."""
    permitido = False
    for documento in documentos:
        for sentencia in documento["Statement"]:
            if {"NotAction", "NotResource", "NotPrincipal"} & set(sentencia):
                raise ValueError("elemento de politica no modelado")
            if not any(fnmatch.fnmatchcase(accion.lower(), a.lower()) for a in _lista(sentencia["Action"])):
                continue
            if not any(fnmatch.fnmatchcase(recurso, r) for r in _lista(sentencia["Resource"])):
                continue
            if not all(_cumple(op, b, contexto) for op, b in sentencia.get("Condition", {}).items()):
                continue
            if sentencia["Effect"] == "Deny":
                return "explicitDeny"
            permitido = True
    return "allowed" if permitido else "implicitDeny"


def tipo_de_clave(clave, valor):
    """Tipo de la clave de contexto para `simulate-custom-policy`."""
    if isinstance(valor, list):
        return "stringList"
    if clave in ("rds:PubliclyAccessible", "rds:ManageMasterUserPassword"):
        return "boolean"
    return "string"


def casos(cuenta, bucket):
    """(id, accion, recurso, contexto, decision esperada). Una sola fuente para offline y AWS."""
    c, r = cuenta, REGION
    region = {"aws:RequestedRegion": r}
    peticion = {"aws:RequestTag/Proyecto": "personal-blog", "aws:RequestTag/Componente": "datos",
                "aws:TagKeys": ["Componente", "Proyecto"]}
    propio = {"aws:ResourceTag/Proyecto": "personal-blog", "aws:ResourceTag/Componente": "datos"}
    ajeno = {"aws:ResourceTag/Proyecto": "otro", "aws:ResourceTag/Componente": "otro"}
    etiquetas = {**peticion, **propio}
    ec2 = f"arn:aws:ec2:{r}:{c}"
    rds = f"arn:aws:rds:{r}:{c}"
    ssm = f"arn:aws:ssm:{r}:{c}"
    estado = f"arn:aws:s3:::{bucket}"

    def servicio(nombre, region_=r):
        return {"ec2:VpceServiceName": f"com.amazonaws.{region_}.{nombre}"}

    return [
        # --- §10.1 de identidad-operativa-datos.md, mismo contexto que la simulacion de H-031-IAM
        ("S-01", "ec2:DescribeVpcs", "*", {**region, **etiquetas}, "allowed"),
        ("S-02", "ec2:CreateVpc", f"{ec2}:vpc/*", {**region, **etiquetas}, "allowed"),
        ("S-03", "ec2:CreateTags", f"{ec2}:vpc/*", {**region, **etiquetas, "ec2:CreateAction": "CreateVpc"}, "allowed"),
        ("S-04", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*", {**region, **etiquetas, **servicio("s3")}, "allowed"),
        ("S-05", "ec2:RevokeSecurityGroupEgress", f"{ec2}:security-group/*", {**region, **propio}, "allowed"),
        ("S-06", "rds:CreateDBInstance", f"{rds}:db:blog-prod-postgres",
         {**region, **etiquetas, "rds:PubliclyAccessible": "false"}, "allowed"),
        ("S-07", "ssm:PutParameter", f"{ssm}:parameter/blog-prod/datos/blogadmin", {**region, **etiquetas}, "allowed"),
        ("S-08", "s3:PutObject", f"{estado}/application/data/terraform.tfstate", {**region, **etiquetas}, "allowed"),
        ("S-09", "ec2:CreateInternetGateway", "*", {**region, **etiquetas}, "explicitDeny"),
        ("S-10", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*", {**region, **etiquetas, **servicio("ssm")}, "implicitDeny"),
        ("S-11", "ec2:CreateTags", f"{ec2}:security-group/*", dict(region), "implicitDeny"),
        ("S-12", "ec2:RevokeSecurityGroupIngress", f"{ec2}:security-group/*", {**region, **propio}, "implicitDeny"),
        ("S-13", "ec2:RevokeSecurityGroupEgress", f"{ec2}:security-group/*", dict(region), "implicitDeny"),
        ("S-14", "ec2:CreateVpc", f"arn:aws:ec2:us-east-1:{c}:vpc/*",
         {**etiquetas, "aws:RequestedRegion": "us-east-1"}, "implicitDeny"),
        ("S-15", "rds:CreateDBInstance", f"{rds}:db:blog-prod-postgres",
         {**region, **etiquetas, "rds:PubliclyAccessible": "true"}, "explicitDeny"),
        ("S-16", "rds:DeleteDBInstance", f"{rds}:db:blog-prod-postgres", {**region, **etiquetas}, "explicitDeny"),
        ("S-17", "rds:CreateDBProxy", "*", {**region, **etiquetas}, "explicitDeny"),
        ("S-18a", "iam:CreateRole", "*", {**region, **etiquetas}, "explicitDeny"),
        ("S-18b", "kms:CreateKey", "*", {**region, **etiquetas}, "explicitDeny"),
        ("S-18c", "sts:AssumeRole", "*", {**region, **etiquetas}, "explicitDeny"),
        ("S-19a", "iam:GetRole", "*", {**region, **etiquetas}, "implicitDeny"),
        ("S-19b", "iam:SimulatePrincipalPolicy", "*", {**region, **etiquetas}, "implicitDeny"),
        ("S-19c", "iam:PassRole", "*", {**region, **etiquetas}, "implicitDeny"),
        ("S-20", "s3:GetObject", f"{estado}/application/media/terraform.tfstate", {**region, **etiquetas}, "implicitDeny"),
        ("S-21", "ssm:DeleteParameter", f"{ssm}:parameter/blog-prod/datos/blogadmin", {**region, **etiquetas}, "explicitDeny"),
        # --- S-10 y sus variantes: el endpoint nuevo
        ("S-10a", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*", {**region, **peticion, **servicio("ssm")}, "implicitDeny"),
        ("S-10b", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*", {**region, **propio, **servicio("ssm")}, "implicitDeny"),
        ("E-01", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*", {**region, **etiquetas, **servicio("secretsmanager")}, "implicitDeny"),
        ("E-02", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*", {**region, **etiquetas, **servicio("servicio-arbitrario")}, "implicitDeny"),
        ("E-03", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*", {**region, **etiquetas, **servicio("rds")}, "implicitDeny"),
        ("E-04", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*", {**region, **etiquetas}, "implicitDeny"),
        ("E-05", "ec2:CreateVpcEndpoint", f"arn:aws:ec2:us-east-1:{c}:vpc-endpoint/*",
         {**etiquetas, "aws:RequestedRegion": "us-east-1", **servicio("s3", "us-east-1")}, "implicitDeny"),
        ("E-06", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*",
         {**etiquetas, "aws:RequestedRegion": "us-east-1", **servicio("s3")}, "implicitDeny"),
        ("E-07", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*",
         {**region, **peticion, "aws:RequestTag/Proyecto": "otro", **servicio("s3")}, "implicitDeny"),
        ("E-08", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*",
         {**region, **peticion, "aws:TagKeys": ["Componente", "Proyecto", "Ajena"], **servicio("s3")}, "implicitDeny"),
        # --- recursos padre del gateway, y los que un gateway no necesita
        ("E-09", "ec2:CreateVpcEndpoint", f"{ec2}:vpc/*", {**region, **ajeno}, "implicitDeny"),
        ("E-10", "ec2:CreateVpcEndpoint", f"{ec2}:route-table/*", dict(region), "implicitDeny"),
        ("E-11", "ec2:CreateVpcEndpoint", f"arn:aws:ec2:{r}:{OTRA_CUENTA}:vpc/*", {**region, **propio}, "implicitDeny"),
        ("E-12", "ec2:CreateVpcEndpoint", f"{ec2}:subnet/*", {**region, **propio}, "implicitDeny"),
        ("E-13", "ec2:CreateVpcEndpoint", f"{ec2}:security-group/*", {**region, **propio}, "implicitDeny"),
        ("E-14", "ec2:CreateVpcEndpoint", f"{ec2}:vpc/*", {**propio, "aws:RequestedRegion": "us-east-1"}, "implicitDeny"),
        # --- operaciones sobre el endpoint ya creado
        ("E-15", "ec2:ModifyVpcEndpoint", f"{ec2}:vpc-endpoint/*", {**region, **ajeno}, "implicitDeny"),
        ("E-16", "ec2:ModifyVpcEndpoint", f"{ec2}:subnet/*", {**region, **propio}, "implicitDeny"),
        ("E-17", "ec2:ModifyVpcEndpoint", f"{ec2}:security-group/*", {**region, **propio}, "implicitDeny"),
        # --- lo legitimo que la correccion no puede romper
        ("A-01", "ec2:CreateVpcEndpoint", f"{ec2}:vpc-endpoint/*", {**region, **peticion, **servicio("s3")}, "allowed"),
        ("A-02", "ec2:CreateVpcEndpoint", f"{ec2}:vpc/*", {**region, **propio}, "allowed"),
        ("A-03", "ec2:CreateVpcEndpoint", f"{ec2}:route-table/*", {**region, **propio}, "allowed"),
        ("A-04", "ec2:ModifyVpcEndpoint", f"{ec2}:vpc-endpoint/*", {**region, **propio}, "allowed"),
        ("A-05", "ec2:ModifyVpcEndpoint", f"{ec2}:route-table/*", {**region, **propio}, "allowed"),
        ("A-06", "ec2:CreateTags", f"{ec2}:vpc-endpoint/*",
         {**region, **peticion, "ec2:CreateAction": "CreateVpcEndpoint"}, "allowed"),
        ("A-07", "ec2:CreateSubnet", f"{ec2}:vpc/*", {**region, **propio}, "allowed"),
        ("A-08", "ec2:CreateSubnet", f"{ec2}:subnet/*", {**region, **peticion}, "allowed"),
        ("A-09", "ec2:CreateRouteTable", f"{ec2}:vpc/*", {**region, **propio}, "allowed"),
        ("A-10", "ec2:CreateSecurityGroup", f"{ec2}:vpc/*", {**region, **propio}, "allowed"),
        ("A-11", "ec2:AuthorizeSecurityGroupIngress", f"{ec2}:security-group/*", {**region, **propio}, "allowed"),
        ("A-12", "ec2:AuthorizeSecurityGroupEgress", f"{ec2}:security-group-rule/*", {**region, **peticion}, "allowed"),
        ("A-13", "ec2:AssociateRouteTable", f"{ec2}:route-table/*", {**region, **propio}, "allowed"),
        ("A-14", "ec2:AssociateRouteTable", f"{ec2}:subnet/*", {**region, **propio}, "allowed"),
        ("A-15", "ec2:ModifyVpcAttribute", f"{ec2}:vpc/*", {**region, **propio}, "allowed"),
        ("A-16", "ec2:ModifySubnetAttribute", f"{ec2}:subnet/*", {**region, **propio}, "allowed"),
        ("A-17", "ec2:ModifySecurityGroupRules", f"{ec2}:security-group-rule/*", {**region, **propio}, "allowed"),
        ("A-18", "ec2:CreateTags", f"{ec2}:vpc-endpoint/*", {**region, **propio}, "allowed"),
    ]
