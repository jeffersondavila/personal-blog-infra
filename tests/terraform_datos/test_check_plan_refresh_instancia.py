"""Refresh-only de la instancia tainted con registro incompleto (Task/031 §38): solo completar el state.

Forma real observada el 2026-10-05: 0 `resource_changes`, una sola entrada de `resource_drift`
(`aws_db_instance.this`, `update`) con 36 atributos distintos y nada mas:
- 18 calculados pasan de `null` al valor que devuelve `describe-db-instances` de la MISMA instancia;
- 18 normalizaciones de forma, `null` a `""` o `[]`;
- la identidad (identifier, base, usuario, motor, version, clase, retencion, SG, subnet group, AZ...) no cambia.
Salidas: `arn_rds`, `endpoint_rds` e `id_de_recurso_rds` de `null` al valor real; el resto `no-op`. El taint se
conserva en el `prior_state`.

H-031-3-MOVING-ATTRIBUTE (§40): `latest_restorable_time` es un atributo MOVIL calculado por AWS. No se compara por
igualdad con un describe fresco: el valor del plan debe ser un instante valido, no posterior al de AWS, y ninguno en
el futuro respecto al reloj (sin tolerancia: el proyecto no tiene convencion de clock skew). Enmienda del
2026-10-18 (aprobada el 2026-10-19): las 24 h miden la FRESCURA del valor de AWS (`ahora - AWS`, PITR
vivo), ya no la antiguedad del state (`AWS - state`). Las pruebas fijan el reloj con `AHORA`.
"""
import copy
from datetime import datetime, timedelta, timezone
import unittest

from scripts.terraform_datos.check_plan import INSTANCIA, PARAMETROS
from scripts.terraform_datos.check_plan_recuperacion import GRUPO, INSTANCIA_RDS
from scripts.terraform_datos.check_plan_refresh_instancia import FORMA_VACIA, VALOR_DESDE_AWS, check, instante_movil
from tests.terraform_datos.test_check_plan_recuperacion import (
    ACCOUNT, MEDIOS, SG_RDS, fixture as fixture_recuperacion, previo,
)

ARN = "arn:aws:rds:us-east-2:123456789012:db:blog-prod-postgres"
ADDRESS = "blog-prod-postgres.x.us-east-2.rds.amazonaws.com"
DBI = "db-ABCDEFGHIJKLMNOPQRSTUVWXYZ"
AHORA = datetime(2026, 10, 5, 21, 0, 0, tzinfo=timezone.utc)


def describe():
    return {"DBInstanceIdentifier": "blog-prod-postgres", "DBName": "personal_blog", "MasterUsername": "blogadmin",
            "Engine": "postgres", "EngineVersion": "17.11", "DBInstanceClass": "db.t4g.micro", "BackupRetentionPeriod": 1,
            "AvailabilityZone": "us-east-2a", "DBSubnetGroup": {"DBSubnetGroupName": "blog-prod-postgres"},
            "VpcSecurityGroups": [{"VpcSecurityGroupId": SG_RDS, "Status": "active"}],
            "DBParameterGroups": [{"DBParameterGroupName": "blog-prod-postgres17", "ParameterApplyStatus": "in-sync"}],
            "DbiResourceId": DBI, "DBInstanceArn": ARN, "DBInstanceStatus": "available", "KmsKeyId": "arn:aws:kms:k",
            "Endpoint": {"Address": ADDRESS, "Port": 5432, "HostedZoneId": "Z2XHWR1WZ565X2"},
            "LicenseModel": "postgresql-license", "OptionGroupMemberships": [{"OptionGroupName": "default:postgres-17"}],
            "Iops": 3000, "StorageThroughput": 125, "DatabaseInsightsMode": "standard", "BackupTarget": "region",
            "LatestRestorableTime": "2026-10-05T19:16:49+00:00", "CustomerOwnedIpEnabled": False,
            "UpgradeRolloutOrder": "second"}


def instancia_completa():
    return {**INSTANCIA, "backup_retention_period": 1, "availability_zone": "us-east-2a",
            "vpc_security_group_ids": [SG_RDS], "password": None, "password_wo": None, "id": "db-id",
            "resource_id": DBI, "arn": ARN, "address": ADDRESS, "endpoint": f"{ADDRESS}:5432",
            "hosted_zone_id": "Z2XHWR1WZ565X2", "status": "available", "kms_key_id": "arn:aws:kms:k",
            "engine_version_actual": "17.11", "license_model": "postgresql-license",
            "option_group_name": "default:postgres-17", "iops": 3000, "storage_throughput": 125,
            "performance_insights_retention_period": 0, "database_insights_mode": "standard",
            "backup_target": "region", "latest_restorable_time": "2026-10-05T19:16:49Z",
            "customer_owned_ip_enabled": False, "upgrade_rollout_order": "second",
            **copy.deepcopy(FORMA_VACIA)}


def fixture():
    plan = fixture_recuperacion()
    plan.pop("resource_changes")
    plan["variables"]["dias_de_retencion_de_backups"] = {"value": 1}
    g = previo(plan, GRUPO)
    g.pop("tainted")
    g["values"]["parameter"] = [{"name": n, "value": v, "apply_method": m} for n, v, m in sorted(PARAMETROS)]
    despues = instancia_completa()
    antes = copy.deepcopy(despues)
    for k in list(VALOR_DESDE_AWS) + list(FORMA_VACIA):
        antes[k] = None
    modulo = next(m for m in plan["prior_state"]["values"]["root_module"]["child_modules"] if m["address"] == "module.base_de_datos")
    modulo["resources"].append({"address": INSTANCIA_RDS, "mode": "managed", "type": "aws_db_instance", "name": "this",
                                "provider_name": "registry.terraform.io/hashicorp/aws", "values": copy.deepcopy(despues),
                                "tainted": True})
    plan["resource_drift"] = [{"address": INSTANCIA_RDS, "mode": "managed", "type": "aws_db_instance",
                               "provider_name": "registry.terraform.io/hashicorp/aws",
                               "change": {"actions": ["update"], "before": antes, "after": despues, "after_unknown": {}}}]
    salidas = {}
    for n, v in plan["output_changes"].items():
        salidas[n] = {"actions": ["no-op"], "before": v["before"], "after": v["before"],
                      "after_unknown": False, "before_sensitive": False, "after_sensitive": False}
    for n, valor in (("identificador_rds", "blog-prod-postgres"), ("nombre_de_base", "personal_blog"), ("puerto_rds", 5432)):
        salidas[n].update(before=valor, after=valor)
    for n, valor in (("arn_rds", ARN), ("endpoint_rds", ADDRESS), ("id_de_recurso_rds", DBI)):
        salidas[n].update(actions=["update"], before=None, after=valor)
    plan["output_changes"] = salidas
    return plan


def deriva(plan):
    return plan["resource_drift"][0]["change"]


class RefreshDeLaInstancia(unittest.TestCase):
    def rechaza(self, plan, codigo, rds=None):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS, rds or describe(), ahora=AHORA)
        self.assertEqual(str(error.exception), codigo)

    def test_forma_real_pasa(self):
        r = check(fixture(), ACCOUNT, MEDIOS, describe(), ahora=AHORA)
        self.assertEqual(r["resource_drift"], [INSTANCIA_RDS])
        self.assertEqual(r["tainted"], [INSTANCIA_RDS])
        self.assertEqual(r["atributos_completados"], 18)
        self.assertEqual(r["normalizaciones_de_forma"], 18)
        self.assertEqual(sorted(r["salidas"]), ["arn_rds", "endpoint_rds", "id_de_recurso_rds"])

    def test_contrato_cerrado_de_36_atributos(self):
        self.assertEqual(len(VALOR_DESDE_AWS), 18)
        self.assertEqual(len(FORMA_VACIA), 18)
        self.assertFalse(set(VALOR_DESDE_AWS) & set(FORMA_VACIA))

    # --- Casos minimos exigidos -------------------------------------------------------------------

    def test_segundo_resource_drift(self):
        plan = fixture()
        otra = copy.deepcopy(plan["resource_drift"][0]); otra["address"] = GRUPO; otra["type"] = "aws_db_parameter_group"
        plan["resource_drift"].append(otra)
        self.rechaza(plan, "DRIFT_ADDRESS")

    def test_identidad_distinta(self):
        for atributo, valor in (("identifier", "otra"), ("engine", "mysql"), ("availability_zone", "us-east-2b"),
                                ("backup_retention_period", 7), ("vpc_security_group_ids", ["sg-otro"]),
                                ("parameter_group_name", "default.postgres17"), ("db_subnet_group_name", "otro"),
                                ("instance_class", "db.t4g.small"), ("engine_version", "17.12"), ("username", "otro"),
                                ("db_name", "otra")):
            with self.subTest(atributo=atributo):
                plan = fixture()
                for lado in ("before", "after"):
                    deriva(plan)[lado][atributo] = valor
                previo(plan, INSTANCIA_RDS)["values"][atributo] = valor
                self.rechaza(plan, "IDENTITY")

    def test_identidad_distinta_de_aws(self):
        for campo, valor in (("DBInstanceIdentifier", "otra"), ("Engine", "mysql"), ("AvailabilityZone", "us-east-2b"),
                             ("BackupRetentionPeriod", 7)):
            with self.subTest(campo=campo):
                rds = describe(); rds[campo] = valor
                self.rechaza(fixture(), "IDENTITY", rds)

    def test_atributo_ya_conocido_cambia(self):
        for atributo, valor in (("allocated_storage", 21), ("deletion_protection", False), ("publicly_accessible", True),
                                ("final_snapshot_identifier", "otro"), ("tags_all", {"x": "y"})):
            with self.subTest(atributo=atributo):
                plan = fixture(); deriva(plan)["after"][atributo] = valor
                self.rechaza(plan, "DRIFT_ATTRIBUTES")

    def test_create_update_delete_replace(self):
        for acciones in (["create"], ["update"], ["delete"], ["delete", "create"], ["create", "delete"]):
            with self.subTest(acciones=acciones):
                plan = fixture()
                plan["resource_changes"] = [{"address": INSTANCIA_RDS, "mode": "managed", "type": "aws_db_instance",
                                             "change": {"actions": acciones}}]
                self.rechaza(plan, "RESOURCE_CHANGES")

    def test_output_extra(self):
        plan = fixture(); plan["output_changes"]["id_de_vpc"].update(actions=["update"], after="otro")
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"]["puerto_rds"].update(actions=["update"], after=5433)
        self.rechaza(plan, "OUTPUTS")

    def test_output_con_valor_distinto_de_aws(self):
        for nombre in ("arn_rds", "endpoint_rds", "id_de_recurso_rds"):
            with self.subTest(nombre=nombre):
                plan = fixture(); plan["output_changes"][nombre]["after"] = "otro"
                self.rechaza(plan, "OUTPUTS")

    def test_deferred(self):
        plan = fixture(); plan["deferred_changes"] = [{"reason": "x"}]
        self.rechaza(plan, "DEFERRED")

    def test_secreto(self):
        plan = fixture(); deriva(plan)["after"]["password"] = "x"
        self.rechaza(plan, "SECRET_IN_PLAN")
        plan = fixture(); plan["variables"]["contrasena_master"] = {"value": None}
        self.rechaza(plan, "EPHEMERAL_LEAK")

    # --- Contrato exacto de los atributos completados -------------------------------------------

    def test_valor_completado_distinto_de_aws(self):
        # Requisito cambiado en §40: `latest_restorable_time` tiene contrato movil propio (clase AtributoMovil).
        for atributo in ("resource_id", "arn", "address", "endpoint", "hosted_zone_id", "status", "kms_key_id",
                         "engine_version_actual", "iops"):
            with self.subTest(atributo=atributo):
                plan = fixture(); deriva(plan)["after"][atributo] = "otro" if atributo != "iops" else 1
                self.rechaza(plan, "DRIFT_VALUE")

    def test_status_no_available(self):
        rds = describe(); rds["DBInstanceStatus"] = "modifying"
        plan = fixture(); deriva(plan)["after"]["status"] = "modifying"; previo(plan, INSTANCIA_RDS)["values"]["status"] = "modifying"
        self.rechaza(plan, "DRIFT_VALUE", rds)

    def test_atributo_completado_que_ya_tenia_valor(self):
        plan = fixture(); deriva(plan)["before"]["arn"] = "previo"
        self.rechaza(plan, "DRIFT_VALUE")

    def test_normalizacion_de_forma_distinta(self):
        for atributo, valor in (("domain_dns_ips", ["10.0.0.1"]), ("domain", "corp"), ("replicas", ["x"])):
            with self.subTest(atributo=atributo):
                plan = fixture(); deriva(plan)["after"][atributo] = valor
                self.rechaza(plan, "DRIFT_SHAPE")

    def test_atributo_calculado_no_contratado(self):
        plan = fixture(); deriva(plan)["before"]["ca_cert_identifier"] = None
        self.rechaza(plan, "DRIFT_ATTRIBUTES")

    def test_otra_direccion_en_el_drift(self):
        plan = fixture(); plan["resource_drift"][0]["address"] = "module.red.aws_vpc.this"
        self.rechaza(plan, "DRIFT_ADDRESS")

    def test_accion_o_desconocido_en_el_drift(self):
        plan = fixture(); deriva(plan)["actions"] = ["delete"]
        self.rechaza(plan, "DRIFT_ADDRESS")
        plan = fixture(); deriva(plan)["after_unknown"] = {"arn": True}
        self.rechaza(plan, "DRIFT_ADDRESS")
        plan = fixture(); deriva(plan)["importing"] = {"id": "x"}
        self.rechaza(plan, "DRIFT_ADDRESS")

    # --- Taint y coherencia ------------------------------------------------------------------------

    def test_taint_perdido_o_trasladado(self):
        plan = fixture(); previo(plan, INSTANCIA_RDS).pop("tainted")
        self.rechaza(plan, "TAINT")
        plan = fixture(); previo(plan, GRUPO)["tainted"] = True
        self.rechaza(plan, "TAINT")

    def test_prior_state_incoherente_con_el_drift(self):
        plan = fixture(); previo(plan, INSTANCIA_RDS)["values"]["status"] = "otro"
        self.rechaza(plan, "DRIFT_COHERENCE")

    def test_parameter_group_del_state_distinto(self):
        plan = fixture(); previo(plan, GRUPO)["values"]["parameter"].append(
            {"name": "rds.force_ssl", "value": "1", "apply_method": "immediate"})
        self.rechaza(plan, "PARAMETERS")


class AtributoMovil(unittest.TestCase):
    """§40: `latest_restorable_time` por contrato temporal; el resto, igualdad exacta."""

    def plan_y_aws(self, plan_valor="2026-10-05T19:16:49Z", aws_valor="2026-10-05T19:16:49+00:00"):
        plan = fixture()
        for valores in (deriva(plan)["after"], previo(plan, INSTANCIA_RDS)["values"]):
            valores["latest_restorable_time"] = plan_valor
        rds = describe(); rds["LatestRestorableTime"] = aws_valor
        return plan, rds

    def pasa(self, plan, rds):
        return check(plan, ACCOUNT, MEDIOS, rds, ahora=AHORA)

    def rechaza(self, plan, rds, codigo="MOVING_ATTRIBUTE"):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS, rds, ahora=AHORA)
        self.assertEqual(str(error.exception), codigo)

    # PASS
    def test_mismo_instante(self):
        self.pasa(*self.plan_y_aws())

    def test_aws_avanzo_algunos_minutos(self):
        self.pasa(*self.plan_y_aws(aws_valor="2026-10-05T19:23:49+00:00"))

    def test_aws_avanzo_varias_horas_dentro_de_24h(self):
        self.pasa(*self.plan_y_aws(plan_valor="2026-10-04T21:16:49Z", aws_valor="2026-10-05T20:06:50+00:00"))

    # FAIL
    def test_plan_posterior_a_aws(self):
        self.rechaza(*self.plan_y_aws(plan_valor="2026-10-05T19:20:00Z", aws_valor="2026-10-05T19:16:49+00:00"))

    def test_delta_mayor_de_24h_con_aws_fresco(self):
        """Enmienda del 2026-10-18: un state antiguo ya no es motivo de rechazo si el valor de AWS es fresco."""
        self.pasa(*self.plan_y_aws(plan_valor="2026-10-04T19:00:00Z", aws_valor="2026-10-05T19:16:49+00:00"))

    def test_aws_con_mas_de_24h_de_antiguedad(self):
        self.rechaza(*self.plan_y_aws(plan_valor="2026-10-04T20:59:59Z", aws_valor="2026-10-04T20:59:59+00:00"))

    def test_plan_invalido(self):
        self.rechaza(*self.plan_y_aws(plan_valor="otro"))

    def test_aws_invalido(self):
        self.rechaza(*self.plan_y_aws(aws_valor="otro"))

    def test_plan_nulo(self):
        # Nulo antes y despues: el atributo no se completo y sale del conjunto de 36.
        self.rechaza(*self.plan_y_aws(plan_valor=None), codigo="DRIFT_ATTRIBUTES")

    def test_aws_nulo(self):
        self.rechaza(*self.plan_y_aws(aws_valor=None))

    def test_instantes_en_el_futuro(self):
        self.rechaza(*self.plan_y_aws(plan_valor="2026-10-05T21:30:00Z", aws_valor="2026-10-05T21:40:00+00:00"))
        self.rechaza(*self.plan_y_aws(aws_valor="2026-10-05T21:10:00+00:00"))

    def test_cualquier_otro_atributo_aws_cambia(self):
        for campo, valor in (("Iops", 3001), ("KmsKeyId", "otra"), ("DBInstanceArn", "otro"), ("DbiResourceId", "otro"),
                             ("StorageThroughput", 126), ("LicenseModel", "otro"), ("UpgradeRolloutOrder", "first")):
            with self.subTest(campo=campo):
                plan, rds = self.plan_y_aws(aws_valor="2026-10-05T19:30:00+00:00")
                rds[campo] = valor
                self.rechaza(plan, rds, "DRIFT_VALUE" if campo not in ("DBInstanceArn", "DbiResourceId") else "DRIFT_VALUE")


class ContratoDeFrescura(unittest.TestCase):
    """§40 enmendado el 2026-10-18 (aprobado el 2026-10-19), comun a TODAS las guardas que lo importan.

    Se conserva: ambos instantes validos y `state <= AWS <= ahora`. Cambia el limite de 24 h: mide la FRESCURA del
    valor de AWS (`ahora - AWS`, PITR vivo) y no la antiguedad del state (`AWS - state`).
    """

    def acepta(self, state, aws):
        return instante_movil(state, aws, AHORA)

    def rechaza(self, state, aws):
        with self.assertRaises(ValueError) as error:
            instante_movil(state, aws, AHORA)
        self.assertEqual(str(error.exception), "MOVING_ATTRIBUTE")

    def test_state_de_ocho_dias_con_aws_fresco(self):
        self.assertEqual(self.acepta("2026-09-27T12:00:00Z", "2026-10-05T20:55:00Z"),
                         timedelta(days=8, hours=8, minutes=55))

    def test_aws_con_mas_de_24_h_aunque_coincida_con_el_state(self):
        self.rechaza("2026-10-04T20:59:59Z", "2026-10-04T20:59:59Z")

    def test_aws_con_mas_de_24_h_y_state_mas_antiguo(self):
        self.rechaza("2026-10-04T18:00:00Z", "2026-10-04T20:59:59Z")

    def test_aws_hace_exactamente_24_h_es_el_limite(self):
        self.assertEqual(self.acepta("2026-10-04T21:00:00Z", "2026-10-04T21:00:00Z"), timedelta(0))

    def test_aws_igual_a_ahora_es_el_limite(self):
        self.assertEqual(self.acepta("2026-10-05T20:00:00Z", "2026-10-05T21:00:00Z"), timedelta(hours=1))

    def test_aws_anterior_al_state(self):
        self.rechaza("2026-10-05T20:00:01Z", "2026-10-05T20:00:00Z")

    def test_aws_en_el_futuro(self):
        self.rechaza("2026-10-05T20:00:00Z", "2026-10-05T21:00:01Z")

    def test_instantes_invalidos_o_sin_zona(self):
        for state, aws in (("otro", "2026-10-05T20:00:00Z"), ("2026-10-05T20:00:00Z", None),
                           ("2026-10-05T20:00:00", "2026-10-05T20:30:00Z"), ("2026-10-05T20:00:00Z", "")):
            with self.subTest(state=state, aws=aws):
                self.rechaza(state, aws)


if __name__ == "__main__":
    unittest.main()
