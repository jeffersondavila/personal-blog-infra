# Identidad operativa mínima de `Task/031`

| Campo | Valor |
| --- | --- |
| Estado | **Implementada sin uso operativo** — aceptada con la aprobación de `Task/031` el 2026-10-21, que acepta también la excepción 6: la identidad operativa es `PersonalBlogAdministrator`. *(Hasta entonces: propuesta pendiente de aprobación.)* Diseño entregado en `H-031-1` y endurecido en **`H-031-1A`** (2026-10-03), que quedó **READY FOR H-031-IAM** tras resolver su gate de laboratorio ([reporte §15](../task-reports/TASK-031-report.md#15-h-031-1a--resolución-del-bloqueo-de-domain_dns_ips-2026-10-03)). `H-031-IAM`: plan de **8 creates** revisado ([reporte §16](../task-reports/TASK-031-report.md#16-h-031-iam--plan-guardado-sin-apply-2026-10-03)) y **aplicado** con readback verde; **BLOQUEADO en la simulación**: S-10 sale `allowed` cuando hay `aws:ResourceTag` ([reporte §17](../task-reports/TASK-031-report.md#17-h-031-iam--apply-ejecutado-stop-en-la-simulación-2026-10-03)), corregido y verificado (§22). **H-031-IAM COMPLETE (2026-10-04):** por decisión operacional del usuario, el operador se conserva creado y validado pero **no** es el contexto operativo; Task/031 continúa con `personal-blog` / `PersonalBlogAdministrator`, que `terraform-datos` exige ya en exclusiva ([§25](../task-reports/TASK-031-report.md#25-h-031-2-align--terraform-datos-exige-personalblogadministrator-2026-10-04)) ([reporte §24](../task-reports/TASK-031-report.md#24-h-031-iam--complete-por-decisión-operacional-del-usuario-2026-10-04)). Ningún recurso de red ni RDS |
| Origen | `H-031-1`, **DH-3 modificada** por el usuario: la identidad administrativa no opera red ni RDS |
| Código (aplicado en H-031-IAM; sin uso operativo) | [`bootstrap/operador-datos/`](../../bootstrap/operador-datos/main.tf) · políticas en [`politicas/`](../../bootstrap/operador-datos/politicas/) |
| Se crea en | **`H-031-IAM`**, checkpoint propio, con `PersonalBlogAdministrator` **solo** como bootstrap (§10) |
| Fuentes verificadas | Referencia de servicios de AWS en formato JSON (`servicereference.us-east-1.amazonaws.com`, descargada el 2026-10-03); código del provider `hashicorp/aws` **v6.64.0**; lógica de evaluación de políticas de IAM |

## 1. Por qué existe

La documentación canónica asigna a `Task/031` **materializar** la «identidad humana
operativa, mínima y autorizada» (ROADMAP, identidades separadas; paquete RDS §12.3). El
usuario rechazó en `H-031-1` operar red y RDS con `PersonalBlogAdministrator`, que tiene
`AdministratorAccess`. Desde que esta identidad exista y se valide, **cualquier operación
de `Task/031` con la administrativa fuera de un bootstrap explícito es STOP**, y el root de
datos lo hace cumplir en código: su postcondición rechaza cualquier sesión que no sea de
`PersonalBlogDataOperator` ([`terraform-datos/main.tf`](../../terraform-datos/main.tf)).

## 2. La identidad

| Atributo | Valor | Motivo |
| --- | --- | --- |
| Nombre | **`PersonalBlogDataOperator`** | Mismo esquema que `PersonalBlogAdministrator` y `PersonalBlogGitHubOidcValidation` |
| Tipo | Rol IAM. **Sin usuario nuevo, sin access keys** | Credenciales solo temporales, por STS |
| Sesión máxima | **3600 s** | La de la administrativa. Un apply de RDS cabe; si una operación no cabe, se renueva y se repite el paso, nunca se alarga la sesión |
| Permissions boundary | No | El rol tiene **denegado** crear o modificar identidades (§7): un boundary no acotaría nada más |
| Etiquetas | `Proyecto`, `Entorno`, `Gestion`, `Componente=identidad-operativa`, `Tarea` | Atribución y auditoría |
| Políticas | **Tres administradas** bajo `/personal-blog/`, adjuntas solo a este rol | H-031-1 superaba el límite agregado de las inline (10 240), por lo que se separó por servicio. Se conserva esa estructura. Tras H-031-1A miden **3 964**, **4 015** y **2 225** caracteres, bajo el límite de 6 144 |

## 3. Cómo se asume

Trust **exacto** —el mismo mecanismo que ya funciona para la administrativa desde `Task/027`—:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "UsuarioDeEntradaConMfa",
    "Effect": "Allow",
    "Principal": { "AWS": "arn:aws:iam::<CUENTA>:user/personal-blog-entry-admin" },
    "Action": "sts:AssumeRole",
    "Condition": { "Bool": { "aws:MultiFactorAuthPresent": "true" } }
  }]
}
```

- **Principal por ARN exacto**: ni la raíz de la cuenta, ni comodines, ni federación.
- **MFA obligatorio**, con la misma condición que la administrativa.
- **El usuario de entrada no se modifica.** En la misma cuenta, IAM evalúa la **unión** de
  la política basada en identidad y la basada en recurso
  ([lógica de evaluación](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html)):
  un trust que nombra al usuario por ARN basta. Se **comprueba** en H-031-IAM asumiendo el
  rol; si AWS lo negara, es STOP y decisión humana —no se amplía el usuario por inercia—.
- **Decisión del usuario (2026-10-04):** `personal-blog-datos` **no se configura**; ver [reporte §24](../task-reports/TASK-031-report.md#24-h-031-iam--complete-por-decisión-operacional-del-usuario-2026-10-04). Lo
  que sigue de este apartado se conserva como diseño histórico.
- **Perfil local** `personal-blog-datos`: `role_arn` de este rol, `source_profile` del
  inicio de sesión del usuario de entrada (`aws login`) y región `us-east-2`. Lo configura
  el operador fuera de Git, igual que `personal-blog`.
- **Hallazgo de H-031-IAM (2026-10-04) — pendiente de decisión.** `aws login` necesita permisos del servicio
  `signin` (`AuthorizeOAuth2Access`, `CreateOAuth2Token`; política administrada de AWS
  `SignInLocalDevelopmentAccess`). El operador no los tiene —simulado: `implicitDeny`—. **Corrección (§23):** el
  usuario de entrada **sí** los tiene, por una inline no documentada (`PersonalBlogLocalDevelopmentSignIn`), así
  que el perfil de arriba sigue siendo una vía candidata; falta probar que el trust baste para asumir el rol
  ([reporte §23](../task-reports/TASK-031-report.md#23-h-031-iam-login-prep--stop-el-usuario-de-entrada-ya-tiene-permisos-signin-2026-10-04)). Antes se escribió que el usuario tampoco los tenía «por diseño»: era incorrecto
  ([reporte §22.4](../task-reports/TASK-031-report.md#22-h-031-iam-s10-fix--aplicada-y-verificada-login-del-operador-pendiente-2026-10-04)).
- **Comprobación previa a cada operación**: `aws sts get-caller-identity --profile
  personal-blog-datos` debe devolver `assumed-role/PersonalBlogDataOperator/<sesión>` en la
  cuenta verificada. Cualquier otro ARN: STOP.

## 4. Permisos de la fase 1 — los únicos que concede H-031-IAM

Texto exacto: [`fase-1-red.json.tftpl`](../../bootstrap/operador-datos/politicas/fase-1-red.json.tftpl),
[`fase-1-rds-y-custodia.json.tftpl`](../../bootstrap/operador-datos/politicas/fase-1-rds-y-custodia.json.tftpl)
y [`fase-1-denegaciones.json.tftpl`](../../bootstrap/operador-datos/politicas/fase-1-denegaciones.json.tftpl).
**Todas las acciones se comprobaron contra la referencia de servicios de AWS**: ninguna es
inventada ni está mal escrita. Toda sentencia regional exige `aws:RequestedRegion =
us-east-2`.

> **Corrección S-10 — aceptada con la aprobación de `Task/031` (2026-10-21).** La tabla describe la plantilla corregida del
> workspace: Red pasa de 6 a 8 sentencias con las mismas 68 acciones Allow. **Aplicada el 2026-10-04**: es la
> versión *default* en AWS; la original queda como versión no *default* ([reporte §22](../task-reports/TASK-031-report.md#22-h-031-iam-s10-fix--aplicada-y-verificada-login-del-operador-pendiente-2026-10-04)). Diseño: ([reporte §18](../task-reports/TASK-031-report.md#18-h-031-iam-s10-fix--diseño-simulación-y-plan-stop-por-resource_drift-2026-10-03)).

| Sid | Acciones | Recurso | Condición | Para qué |
| --- | --- | --- | --- | --- |
| `LecturaRegionalSinRecurso` | 17 `ec2:Describe*` exactas, 13 lecturas de RDS, `ssm:DescribeParameters`, `logs:DescribeLogGroups` | `*` | Región | Refresh de Terraform, preflight de colisiones y readback. Ver §5 |
| `CrearLaVpcEtiquetada` | `ec2:CreateVpc` | `vpc/*` | `RequestTag` `Proyecto`/`Componente=datos`; claves de etiqueta cerradas | Crear la VPC solo etiquetada como del root de datos |
| `CrearRecursosNuevosEtiquetados` | `CreateSubnet`, `CreateRouteTable`, `CreateSecurityGroup`, `AuthorizeSecurityGroup{Ingress,Egress}` | `subnet/*`, `route-table/*`, `security-group/*`, `security-group-rule/*` | `RequestTag` | Lo nuevo nace etiquetado |
| `CrearSoloElGatewayEndpointDeS3` | `ec2:CreateVpcEndpoint` | `vpc-endpoint/*` | `RequestTag` + **`ec2:VpceServiceName = com.amazonaws.us-east-2.s3`** | La **única** vía para autorizar el endpoint nuevo: ningún otro servicio |
| `GatewayDeS3SobreVpcYTablasPropias` *(corrección S-10)* | `ec2:CreateVpcEndpoint` | `vpc/*`, `route-table/*` | **`ResourceTag`** `Proyecto`/`Componente=datos` | Los padres que un **gateway** hace autorizar; sin `subnet` ni `security-group`, que solo usan los de interfaz |
| `OperarSoloRecursosPropios` | Las de creación de subred, tabla, grupo y reglas sobre el **padre**, `AssociateRouteTable`, `Modify{Vpc,Subnet}Attribute`, `ModifySecurityGroupRules`, `RevokeSecurityGroupEgress` —el provider retira con ella la salida por defecto de **nuestros** grupos recién creados—. **Sin** `CreateVpcEndpoint` ni `ModifyVpcEndpoint` desde la corrección S-10 | `vpc/*`, `subnet/*`, `route-table/*`, `security-group/*`, `security-group-rule/*` | **`ResourceTag`** `Proyecto`/`Componente=datos` | Solo se toca lo que ya es del root de datos |
| `ModificarSoloEndpointsPropios` *(corrección S-10)* | `ec2:ModifyVpcEndpoint` | `vpc-endpoint/*`, `route-table/*` | **`ResourceTag`** | Cambiar política o tablas del endpoint propio, sin añadirle subredes ni grupos |
| `EtiquetarAlCrear` | `ec2:CreateTags` | Los seis tipos | `ec2:CreateAction` ∈ las siete acciones de creación + `RequestTag` | El etiquetado en la creación, que EC2 autoriza aparte |
| `ReetiquetarSoloRecursosPropios` | `ec2:CreateTags` | Los seis tipos | `ResourceTag` + `RequestTag` *IfExists* | Cambiar `Name` sin poder quitar la pertenencia |
| `RdsCrearGruposPropios` | `CreateDBSubnetGroup`, `CreateDBParameterGroup` | `subgrp:blog-prod-*`, `pg:blog-prod-*` | `RequestTag` | Grupos del root de datos |
| `RdsCrearLaInstanciaProductiva` | `rds:CreateDBInstance` | `db:blog-prod-postgres` + su `pg`, `subgrp` y el `og` `default:postgres-17` | `RequestTag` + **`rds:PubliclyAccessible = false`** | Una instancia, con nombre exacto, nunca pública |
| `RdsOperarRecursosPropios` | `AddTagsToResource`, `ModifyDBInstance`, `ModifyDBParameterGroup`, `ModifyDBSubnetGroup` | Los mismos ARN | `RequestTag` *IfExists* | Rotar la contraseña (`password_wo_version`), ajustar parámetros, etiquetar |
| `CustodiaDeLaContrasenaMaster` | `ssm:PutParameter`, `GetParameter(s)`, `AddTagsToResource`, `ListTagsForResource` | `parameter/blog-prod/datos/*` | Región | Custodia de DH-2 y lectura humana para recuperación |
| `GrupoDeLogsDePostgreSQL` | `logs:CreateLogGroup`, `PutRetentionPolicy`, `Tag*`, `ListTags*` | El grupo exacto de la instancia | Región | Retención de 14 días desde el primer día |
| `StateRemotoSoloDelRootDeDatos` · `LeerYEscribirElStateYSuLock` · `LiberarSoloElLock` | `s3:ListBucket`; `GetObject`/`PutObject`; `DeleteObject` | El bucket de D-06; **solo** `application/data/terraform.tfstate` y su `.tflock`; borrar **solo** el lock | — | El backend remoto con lock nativo. Sin acceso a las otras tres keys |

**KMS: ningún permiso.** `aws/rds` y `aws/ssm` son claves **administradas por AWS**, cuya
política autoriza a los principales de la cuenta a través del servicio
(`kms:ViaService`). Se **verifica** en H-031-3: un `AccessDenied` de KMS es STOP, no un
permiso que se añade sin revisar.

## 5. Dónde AWS exige `Resource: "*"` — y por qué se acepta

Según la referencia de servicios, las lecturas `ec2:Describe*` de esta lista, y además
`rds:DescribeDBEngineVersions`, `DescribeOrderableDBInstanceOptions`, `DescribeCertificates`,
`DescribeEngineDefaultParameters`, `ssm:DescribeParameters` y `logs:DescribeLogGroups`,
**no admiten recurso** o, sin identificador, se evalúan contra toda la cuenta. Se acotan
como se puede: **solo lecturas** (`Describe`/`List`), **solo `us-east-2`**, y la prueba offline
rechaza cualquier `Allow` con `Resource: "*"` que no sea una lectura. Las lecturas de RDS que sí
admiten recurso se dejan en `*` a propósito: el preflight de H-031-2 tiene que poder **ver**
colisiones fuera del prefijo `blog-prod-`.

## 6. Etiquetas como frontera, y el grupo por omisión sin uso

EC2 autoriza por etiqueta: se crea con `RequestTag`, el etiquetado en la creación pide
`ec2:CreateTags` con `ec2:CreateAction`, y lo existente se modifica con `ResourceTag`. **Toda**
sentencia que etiqueta exige una de las dos cosas: o se etiqueta al crear, o el recurso ya es del
root de datos. Ninguna depende de la **ausencia** de etiquetas, y la prueba offline lo exige.

**El grupo de seguridad por omisión de la VPC no se gestiona** (H-031-1A, decisión del usuario).
H-031-1 lo vaciaba con `aws_default_security_group`, y para eso el provider **etiqueta antes de
revocar** —comprobado en el código de la v6.64.0—: el rol habría necesitado etiquetar un grupo
**sin** etiquetas del proyecto y después retirarle reglas, un permiso sobre recursos que no son
propios. Se retiró la sentencia que lo permitía, y también `ec2:RevokeSecurityGroupIngress`,
que la fase 1 solo usaba para eso.

El aislamiento se preserva por **no uso**, no por mutarlo:

| Garantía | Dónde se exige |
| --- | --- |
| RDS lleva **exactamente** `sg-rds` | `vpc_security_group_ids = [var.id_sg_rds]` en el módulo; prueba de Terraform (`grupos_de_seguridad == ["sg-rds"]`); la guarda del plan exige esa única referencia en la sección `configuration` |
| Ningún recurso del proyecto declara ni referencia el grupo por omisión | Prueba estática de las fuentes y guarda del plan (`DEFAULT_SG_USED`); la lista cerrada del laboratorio rechaza `aws_default_security_group` |
| Los tres grupos son explícitos: `sg-lambda`, `sg-admin`, `sg-rds` | Prueba estática y conjunto exacto de direcciones de la guarda |
| El gateway endpoint de S3 no usa grupos ni subredes | Los endpoints de tipo `Gateway` no los admiten; la prueba y la guarda exigen que no se declaren |
| **Task/032** adjuntará `sg-lambda` a la Lambda de aplicación de forma **explícita** | Contrato en la salida `id_sg_lambda`; criterio de aceptación de Task/032 |
| **H-031-5** adjuntará `sg-admin` a la ejecutora de forma **explícita** | Contrato en la salida `id_sg_admin`; condición `lambda:SecurityGroupIds` exacta de la fase 2 |

El grupo por omisión conserva sus reglas originales; el proyecto **no le adjunta ningún
recurso**. El readback de H-031-3 debe confirmar esa ausencia de uso. Las pruebas inspeccionan
el root de datos actual; Task/032 y H-031-5 deberán verificar sus propias asociaciones explícitas.
DN-3 queda cerrada por eliminación del problema; no se acepta el riesgo de reclamar grupos ajenos.

**`ModifyDBInstance` no admite condición sobre `PubliclyAccessible`.** El rol podría pedir que
la instancia sea pública, pero **no** puede crear Internet Gateway (denegado), así que RDS
rechaza la petición en una VPC sin IGW. La guarda del plan y el readback lo verifican.

## 7. Denegaciones explícitas

| Sid | Qué cierra |
| --- | --- |
| `SinSalidaPublicaNiComputo` | Internet/Egress-only Gateway, NAT, Elastic IP, peering, Transit Gateway, VPN, Client VPN, `RunInstances` |
| `SinBorradoDeProduccion` | Borrar VPC, subredes, grupos, tablas, endpoints, grupos de RDS, el grupo de logs, su retención y el SecureString |
| `SinBorrarLaInstanciaProductiva` | `rds:DeleteDBInstance` sobre `db:blog-prod-postgres`. Se deja acotado a ese ARN para que la fase 4 pueda borrar **solo** instancias de restore |
| `SinRdsPublico` | Crear o restaurar con `rds:PubliclyAccessible = true` |
| `SinSecretsManagerAdministrado` | `rds:ManageMasterUserPassword = true` (D-23: SSM, no Secrets Manager) |
| `SinServiciosRdsExcluidos` | Proxy, clúster, global, réplica, blue/green |
| `SinIdentidadesNiClavesNuevas` | Toda escritura de IAM salvo `iam:PassRole`, claves KMS y su política, Secrets Manager y `sts:AssumeRole` (sin encadenar roles) |

**Destruir infraestructura productiva no es una operación de este rol.** Si algún día hay que
hacerlo, va por un plan propio, revisado, con la administrativa como break-glass y autorización
explícita. Es coherente con `deletion_protection` y con que ninguna automatización ejecute
`destroy` contra AWS real.

## 8. Lo que NO se concede, expresamente

**Cualquier** acción de IAM, también de lectura (`iam:Get*`, `iam:List*`) y
`iam:SimulatePrincipalPolicy`: la simulación se hace desde el bootstrap (§10).
`iam:CreateServiceLinkedRole` (§9), `iam:PassRole` (llega en la fase 2 y acotado), `sts:AssumeRole`, KMS administrativo, Secrets Manager, Lambda, API Gateway,
CloudWatch (alarmas o métricas), `rds:RestoreDBInstance*`, `rds:CreateDBSnapshot`,
`rds:DeleteDBInstance`, `rds:RebootDBInstance`, cualquier `Delete*` de EC2, `ec2:CreateRoute`,
`ec2:ReplaceRoute`, `ec2:RevokeSecurityGroupIngress`, `ec2:CreateTags` sobre recursos sin
las etiquetas del root de datos, cualquier acción de S3 fuera de la key del root de datos, Billing,
Organizations y CloudShell.

## 9. El rol vinculado de RDS

Si la cuenta no tiene `AWSServiceRoleForRDS`, el primer `CreateDBInstance` intenta crearlo y
pide `iam:CreateServiceLinkedRole` **al operador**. En lugar de concedérselo, el bootstrap lo
crea de forma explícita y revisada (`aws_iam_service_linked_role`, condicionado por
`crear_rol_vinculado_de_rds`). Si el preflight lo encuentra ya creado, **no se gestiona ni se
importa**: se registra como preexistente legítimo.

## 10. Checkpoint `H-031-IAM` — propuesta exacta

**Autoriza exclusivamente**: el bootstrap de `PersonalBlogDataOperator`, sus tres políticas
exactas y sus tres adjuntos, `AWSServiceRoleForRDS` **solo si** el preflight prueba que falta, y
el state dedicado `bootstrap/operador-datos/terraform.tfstate`. `PersonalBlogAdministrator` solo
para ese bootstrap. **No** red, **no** RDS, **no** SSM ni CloudWatch de producción.

| # | Paso | Identidad | Muta AWS |
| --- | --- | --- | --- |
| 1 | **Identidad bootstrap verificada**: `sts get-caller-identity --profile personal-blog` → `assumed-role/PersonalBlogAdministrator/…` en la cuenta verificada, `us-east-2` | Bootstrap | No |
| 2 | **Preflight sin mutar**: verificar también que `blog-prod-postgres` y `/blog-prod/datos/blogadmin` no existen antes de las pruebas negativas del paso 10 (si existen o no se puede comprobar, STOP); `iam get-role --role-name PersonalBlogDataOperator` → **NoSuchEntity** (si existe, STOP); `iam get-role --role-name AWSServiceRoleForRDS` → fija `crear_rol_vinculado_de_rds`; `iam list-policies --scope Local --path-prefix /personal-blog/` → sin colisión; `s3api head-object` de la key → 404 | Bootstrap | No |
| 3 | **Access Analyzer**: `accessanalyzer validate-policy` de las tres políticas renderizadas (`IDENTITY_POLICY`) y del trust (`RESOURCE_POLICY`, `AWS::IAM::AssumeRolePolicyDocument`): cero `ERROR` y cero `SECURITY_WARNING`; cualquier `WARNING` se revisa | Bootstrap | No |
| 4 | **`init` + plan guardado + guarda**: backend S3 con la key dedicada; JSON privado; exactamente el rol, tres políticas, tres adjuntos y, si procede, el rol vinculado; solo `create`; trust y políticas **idénticos** a las plantillas renderizadas. Guarda: [`check_plan_operador.py`](../../scripts/terraform_datos/check_plan_operador.py) | Bootstrap | Solo el `.tflock` transitorio |
| 5 | **Revisión humana** del plan y autorización de aplicar **ese** binario | Usuario | — |
| 6 | **Apply exacto** del plan guardado | Bootstrap | Sí: solo esta lista |
| 7 | **Readback**: `get-role` y trust; `list-attached-role-policies` (3); `get-policy-version` de cada una; `list-role-policies` vacío; ninguna access key; rol vinculado según el paso 2 | Bootstrap | No |
| 8 | **Simulación DESDE EL BOOTSTRAP**, antes de abandonarlo: `iam simulate-principal-policy --policy-source-arn arn:aws:iam::<CUENTA>:role/PersonalBlogDataOperator` con los casos de §10.1 y sus claves de contexto. Cualquier decisión distinta de la esperada: STOP | Bootstrap | No |
| 9 | **Cambio de contexto** a `personal-blog-datos` | — | No |
| 10 | **STS y pruebas reales no mutantes** de §10.2 | Operativa | No |
| 11 | **Convergencia del bootstrap**: plan normal 0/0/0 | Bootstrap | No |

El operador **no** recibe `iam:SimulatePrincipalPolicy` ni ninguna lectura de IAM para
probarse a sí mismo: la simulación la ejecuta la identidad de bootstrap, que ya tiene ese
permiso, contra el ARN exacto del rol creado. *(Superado por la decisión del usuario del 2026-10-04: H-031-2
y H-031-3 se operan con `personal-blog`, §24 del reporte.)* Desde el paso 9, **H-031-2 y H-031-3 usan solo
`personal-blog-datos`**, y cualquier IAM que no sea exactamente esta lista es «IAM inesperado»
(H-031-4).

### 10.1 Casos de la simulación (paso 8)

Región `us-east-2` y etiquetas `Proyecto=personal-blog`, `Componente=datos` salvo que se diga
otra cosa. La simulación evalúa la **lógica de las políticas**; no ejecuta las llamadas
internas de un servicio ni las políticas de clave de KMS, y no sustituye al apply.

| Caso | Acción | Recurso y contexto | Esperado |
| --- | --- | --- | --- |
| S-01 | `ec2:DescribeVpcs` | `*` | `allowed` |
| S-02 | `ec2:CreateVpc` | `vpc/*`, `RequestTag` del proyecto, `TagKeys` cerradas | `allowed` |
| S-03 | `ec2:CreateTags` | `vpc/*`, `ec2:CreateAction=CreateVpc` | `allowed` |
| S-04 | `ec2:CreateVpcEndpoint` | `vpc-endpoint/*`, `ec2:VpceServiceName=com.amazonaws.us-east-2.s3` | `allowed` |
| S-05 | `ec2:RevokeSecurityGroupEgress` | `security-group/*` con `ResourceTag` del proyecto | `allowed` |
| S-06 | `rds:CreateDBInstance` | `db:blog-prod-postgres`, `rds:PubliclyAccessible=false` | `allowed` |
| S-07 | `ssm:PutParameter` | `parameter/blog-prod/datos/blogadmin` | `allowed` |
| S-08 | `s3:PutObject` | `<bucket de estado>/application/data/terraform.tfstate` | `allowed` |
| S-09 | `ec2:CreateInternetGateway` | `*` | `explicitDeny` |
| S-10 | `ec2:CreateVpcEndpoint` | `ec2:VpceServiceName=com.amazonaws.us-east-2.ssm` | `implicitDeny` |
| S-11 | `ec2:CreateTags` | `security-group/*` **sin** etiquetas y sin `ec2:CreateAction` | `implicitDeny` |
| S-12 | `ec2:RevokeSecurityGroupIngress` | `security-group/*` con `ResourceTag` del proyecto | `implicitDeny` |
| S-13 | `ec2:RevokeSecurityGroupEgress` | `security-group/*` **sin** etiquetas del proyecto | `implicitDeny` |
| S-14 | `ec2:CreateVpc` | `aws:RequestedRegion=us-east-1` | `implicitDeny` |
| S-15 | `rds:CreateDBInstance` | `rds:PubliclyAccessible=true` | `explicitDeny` |
| S-16 | `rds:DeleteDBInstance` | `db:blog-prod-postgres` | `explicitDeny` |
| S-17 | `rds:CreateDBProxy` | `*` | `explicitDeny` |
| S-18 | `iam:CreateRole` · `kms:CreateKey` · `sts:AssumeRole` | `*` | `explicitDeny` |
| S-19 | `iam:GetRole` · `iam:SimulatePrincipalPolicy` · `iam:PassRole` | `*` | `implicitDeny` |
| S-20 | `s3:GetObject` | `<bucket de estado>/application/media/terraform.tfstate` | `implicitDeny` |
| S-21 | `ssm:DeleteParameter` | `parameter/blog-prod/datos/blogadmin` | `explicitDeny` |

> **Hallazgo de H-031-IAM (2026-10-03) — pendiente de decisión.** Ejecutada contra el rol ya
> creado, con etiquetas de petición **y** de recurso en el contexto, la simulación dio 24/25. **S-10
> salió `allowed`**: la sentencia `OperarSoloRecursosPropios` de la política Red concede
> `ec2:CreateVpcEndpoint` sobre `vpc-endpoint/*` condicionada solo por `aws:ResourceTag`, sin
> `ec2:VpceServiceName`. Con solo etiquetas de petición, S-10 sí es `implicitDeny`. La restricción
> «solo el *gateway* de S3» depende, por tanto, de cómo evalúe EC2 `aws:ResourceTag` en un endpoint
> que se está creando, y eso no está demostrado. No se cambió ninguna política: la corrección
> requiere su propio checkpoint de IAM y una simulación que cubra también ese contexto
> ([reporte §17](../task-reports/TASK-031-report.md#17-h-031-iam--apply-ejecutado-stop-en-la-simulación-2026-10-03)).
>
> **Corrección diseñada (2026-10-03).** `CreateVpcEndpoint` y `ModifyVpcEndpoint` salen de
> `OperarSoloRecursosPropios` a sentencias propias, según las claves que la referencia de AWS admite por
> acción y recurso. La matriz completa —los casos de arriba, S-10 con y sin `aws:ResourceTag` y los nuevos
> negativos y positivos— pasa en `simulate-custom-policy`, igual que en el evaluador offline. Su plan de
> reparación se aplicó y `simulate-principal-policy` contra el rol vivo da 62/62 ([reporte §22](../task-reports/TASK-031-report.md#22-h-031-iam-s10-fix--aplicada-y-verificada-login-del-operador-pendiente-2026-10-04)). Historia: ([reporte §18](../task-reports/TASK-031-report.md#18-h-031-iam-s10-fix--diseño-simulación-y-plan-stop-por-resource_drift-2026-10-03)).

### 10.2 Pruebas reales con la identidad operativa (paso 10)

**Regla: una prueba negativa nunca usa una operación que mutaría si la denegación fallara.** Por
eso solo hay lecturas, `--dry-run` y operaciones sobre recursos cuya inexistencia se comprueba
justo antes con bootstrap. Sin ventana exclusiva que descarte una creación concurrente, se omiten
las dos llamadas de borrado y se conserva la simulación: no se arriesga una mutación accidental.

| Prueba | Esperado |
| --- | --- |
| `sts get-caller-identity --profile personal-blog-datos` | `assumed-role/PersonalBlogDataOperator/…` en la cuenta verificada |
| `ec2 describe-vpcs`, `ec2 describe-availability-zones --zone-ids use2-az1 use2-az2` | Éxito: lecturas que el preflight de H-031-2 necesita |
| `rds describe-db-engine-versions --engine postgres --engine-version 17.11` | Éxito |
| `ssm describe-parameters`, `logs describe-log-groups --log-group-name-prefix /aws/rds/instance/blog-prod` | Éxito |
| `s3api list-objects-v2 --bucket <bucket de estado> --prefix application/data/` | Éxito, sin objetos |
| `ec2 create-vpc --dry-run` con el CIDR y las etiquetas del proyecto | `DryRunOperation` (permitido) |
| `ec2 create-vpc --dry-run` sin etiquetas | `UnauthorizedOperation` |
| `ec2 create-internet-gateway --dry-run` · `ec2 allocate-address --dry-run` | `UnauthorizedOperation` |
| `iam get-role --role-name PersonalBlogDataOperator` | `AccessDenied`: el operador no lee IAM |
| `s3api get-object` de `application/media/terraform.tfstate` | `AccessDenied` |
| `rds delete-db-instance --db-instance-identifier blog-prod-postgres` (aún no existe) | `AccessDenied`; si saliera `DBInstanceNotFound`, la denegación falla: STOP, sin haber mutado nada |
| `ssm delete-parameter --name /blog-prod/datos/blogadmin` (aún no existe) | `AccessDenied`, con la misma lógica |

No se concede ningún permiso extra para facilitar estas pruebas.

## 11. Fases posteriores — diseño, NO concedido

Cada una se añade a este mismo bootstrap en **su** checkpoint de IAM, con plan propio y la
misma guarda. Ninguna amplía las anteriores en silencio.

| Fase | Checkpoint | Se concede al operador | Lo crea el bootstrap |
| --- | --- | --- | --- |
| 2 — ejecutora D-24 | H-031-5-IAM | `lambda:CreateFunction`, `UpdateFunctionCode`, `UpdateFunctionConfiguration`, `GetFunction*`, `PutFunctionConcurrency` *(innecesario desde la modificación de D-24, aprobada el 2026-10-19: sin concurrencia reservada)*, `TagResource`, `InvokeFunction` **solo** sobre `function:blog-prod-ejecutor`, con `lambda:SubnetIds`, `lambda:SecurityGroupIds` y `lambda:VpcIds` **exactos** —ya conocidos tras H-031-3—. **`iam:PassRole` solo** sobre el rol de la ejecutora con `iam:PassedToService = lambda.amazonaws.com`. Logs de `/aws/lambda/blog-prod-ejecutor` | Rol `PersonalBlogEjecutorDatos`: trust `lambda.amazonaws.com` con `aws:SourceAccount` y `aws:SourceArn` de la función; ENI en las dos subredes y con `sg-admin`; escritura **solo** en `<bucket de medios>/exportaciones/*` |
| 3 — identidades SQL | H-031-6 | Nada nuevo: invocar la ejecutora (fase 2) y `ssm:PutParameter` bajo `/blog-prod/datos/*` (fase 1) | — |
| 4 — restore y PITR | H-031-7-IAM | `rds:RestoreDBInstanceToPointInTime` desde `db:blog-prod-postgres` hacia `db:blog-prod-restore-*` (más `subgrp`, `pg`, `og` y `auto-backup`), con `rds:PubliclyAccessible = false`; `rds:AddTagsToResource` y **`rds:DeleteDBInstance` solo** sobre `db:blog-prod-restore-*`; `rds:CreateDBSnapshot`/`DeleteDBSnapshot` solo sobre `snapshot:blog-prod-sintetico-*`. La denegación sobre la productiva **no** se toca | — |
| 5 — alarmas D-11 | H-031-8-IAM | `cloudwatch:PutMetricAlarm`, `DescribeAlarms`, `TagResource`, `ListTagsForResource` sobre `alarm:blog-prod-*`, con `cloudwatch:AlarmActions` acotado a lo que se decida; `GetMetricData`/`GetMetricStatistics`/`ListMetrics` de solo lectura | — |
| 6 — D-20 | H-031-9-IAM | **Nada**: el operador no administra la integración | Rol de solo lectura para Grafana Cloud, con `sts:ExternalId`, tras verificar D-19 |

**Así se gestionan los roles de la ejecutora y de D-20 sin IAM amplio:** el operador **nunca**
escribe IAM. Todo rol lo crea el bootstrap, en su checkpoint, con plan revisado; el operador
solo recibe `iam:PassRole` **exacto**, y únicamente para el rol de la ejecutora, que es el
único que tiene que pasar a un servicio.

> **Fase 2 superada: `Task/031` H-031-5 (2026-10-06).** Desde la decisión operacional del usuario del
> 2026-10-04 (reporte §24), `terraform-datos` lo opera `PersonalBlogAdministrator`, y H-031-5 se autorizó
> dentro de ese root.
>
> - El rol `PersonalBlogEjecutorDatos` lo crea el módulo `ejecutor_privado`, no este bootstrap.
> - El operador **no** recibe la fase 2: `PersonalBlogDataOperator` no se modifica.
> - El trust es el del principal de servicio de Lambda que documenta AWS. Según la guía de Lambda,
>   `aws:SourceArn` «applies only to policies where your Lambda function is the target resource».
> - La escritura en `exportaciones/*` llega con el modo `export`.
>
> Detalle: [reporte §44](../task-reports/TASK-031-report.md#44-h-031-5--ejecutora-privada-de-d-24-por-fases-implementación-offline-y-cuota-lambda-2026-10-06).

## 12. Riesgos

| Riesgo | Mitigación |
| --- | --- |
| Falta una acción que Terraform necesita y el apply se detiene a medias | Simulación desde el bootstrap en H-031-IAM y STOP en H-031-2/3. Se corrige en un checkpoint de IAM y se repite el plan, nunca ampliando por conveniencia |
| La simulación no reproduce llamadas internas del servicio ni políticas de clave | Se declara en §10.1; el readback y la convergencia de H-031-3 son la evidencia final |
| Alguien asocia el grupo por omisión a un recurso del proyecto | Aislamiento por no uso: prueba estática, guarda del plan y lista cerrada del laboratorio lo rechazan (§6) |
| La sesión de 3600 s caduca durante un apply largo de RDS | Comprobar el tiempo restante antes de aplicar y renovar antes de empezar; el lock nativo impide un segundo escritor |
| El trust no basta y AWS exige una política en el usuario de entrada | STOP y decisión humana. El usuario de entrada no se toca sin autorización |
| Los nombres de acciones cambian en la referencia de AWS | Revalidar contra la referencia el día de H-031-IAM; la prueba offline fija la estructura |
