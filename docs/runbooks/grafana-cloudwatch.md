# Grafana Cloud ← CloudWatch: integración de D-20

**Runbook de `Task/031` H-031-9.** Contrato:
- [D-20 en open-decisions](../architecture/open-decisions.md#d-20--mecanismo-de-integración-cloudwatch--grafana-cloud);
- [reporte de Task/031, §47](../task-reports/TASK-031-report.md).

**Estado.** Propuesta — pendiente de aprobación: se consolida con el `approved` de `Task/031`.

**Ejecución en AWS (2026-10-15):**
- el rol y su política en línea existen, creados por Terraform en H-031-9;
- readback exacto de la confianza (cuenta de Grafana y `sts:ExternalId`) y de la política;
- simulación IAM 20/20: 3 positivos y 17 negativos, entre ellos todo `logs:*` consultado y toda escritura;
- convergencia con la guarda original.

**«Save & test» en Grafana Cloud (resultado comunicado por el usuario el 2026-10-16):**
- «Successfully queried the CloudWatch metrics API»: **PASS**. La conexión con la API de métricas queda validada.
- Logs: `AccessDeniedException` en `logs:DescribeLogGroups`. Es la **denegación prevista** por D-20.
- La prueba combinada sale en rojo **solo** por esa denegación.
- CloudTrail confirma que el rol lo asume solo la cuenta de Grafana, con su ExternalId (§2, paso 4).

**Explore con métricas reales de RDS (consulta del usuario, comunicada el 2026-10-16): PASS.** Se consultó
`AWS/RDS` · `CPUUtilization` · `Average` · `DBInstanceIdentifier = blog-prod-postgres`, con periodo de 300 s y las
últimas 3 h. Grafana mostró la serie y la tabla con valores reales, entre ≈ 4.1 % y 5.2 %. Queda **validada la ruta
Grafana Cloud → `AssumeRole` → CloudWatch → métricas de RDS**.

**Estados de alarma: no validados.** Con estos permisos no se pueden mostrar en Grafana (§1.1).

**Pendiente:** el §4, al terminar el trial.

Grafana Cloud lee **métricas** de CloudWatch, en la cuenta del proyecto y en us-east-2. Para ello asume un rol de
**solo lectura** con «Grafana Assume Role», de modo que ninguna clave estática queda en manos del tercero.

## 1. Qué concede el rol y qué no

| Concede | No concede |
| --- | --- |
| `cloudwatch:GetMetricData` y `cloudwatch:ListMetrics`, solo en us-east-2 | Logs: el log de PostgreSQL puede llevar verificadores SCRAM y sentencias DDL (R-39) |
| `cloudwatch:DescribeAlarms`, solo sobre las alarmas `blog-prod-*`: no basta para las anotaciones de Grafana (§1.1) | Ninguna escritura en CloudWatch ni en ningún servicio |
| — | SQL, secretos, S3, Lambda, despliegues, IAM y STS |

**Confianza.** Solo la cuenta AWS de Grafana, y solo con el `sts:ExternalId` del stack. Ambos valores viven en el
archivo de variables **privado** del destino, `integracion_grafana`, nunca en Git.

**Gestión.** El rol `PersonalBlogLecturaGrafana` lo crea y lo cambia **solo Terraform**, desde el root
`terraform-datos` (módulo `lectura_grafana`). Nunca se crea desde la consola ni desde Grafana.

### 1.1 Estados de alarma en Grafana

Grafana muestra las alarmas de CloudWatch como **anotaciones**. Según su documentación, consultada el 2026-10-16, las
anotaciones siempre leen el historial con `cloudwatch:DescribeAlarmHistory`. Además usan `DescribeAlarmsForMetric`
(búsqueda por métrica, el modo por omisión) o `DescribeAlarms` (búsqueda por prefijo).

El rol solo concede `DescribeAlarms` sobre `blog-prod-*`. La simulación IAM da `implicitDeny` para
`DescribeAlarmHistory` y `DescribeAlarmsForMetric`, así que **las anotaciones de alarmas fallarían con acceso
denegado**.

Esto **no se corrige ampliando permisos** sin una decisión específica que modifique D-20. El estado de las 8 alarmas se
consulta en la consola de CloudWatch; además, no tienen acciones.

## 2. Conectar el origen de datos

1. En Grafana Cloud, en el origen de datos **CloudWatch**, configurar:
   - *Authentication Provider*: **Grafana Assume Role**;
   - *Default Region*: **us-east-2**.
2. En *Assume Role ARN*, pegar el ARN del rol. Se obtiene con la identidad operativa:

   ```bash
   aws iam get-role --role-name PersonalBlogLecturaGrafana --query Role.Arn --output text \
     --profile personal-blog --region us-east-2
   ```

   El root no lo publica como salida porque lleva la cuenta: no se copia a documentos ni a tickets.
3. **Save & test.** Resultado esperado:
   - «Successfully queried the CloudWatch metrics API» → **correcto**;
   - el paso de **logs falla con acceso denegado** (`AccessDeniedException` en `logs:DescribeLogGroups`) →
     **esperado por contrato**: el rol no tiene `logs:*`. La prueba combinada sale en rojo solo por eso. No es una
     avería y no se corrige ampliando permisos.
4. Comprobar en CloudTrail, en *Event history* y filtrando por `AssumeRole`, que quien asumió el rol es la cuenta de
   Grafana.
5. En **Explore**, consultar una métrica de `AWS/RDS` de la instancia, por ejemplo `CPUUtilization` o
   `FreeableMemory`, y comprobar que devuelve datos reales. Es la validación de la visualización: «Save & test» solo
   prueba la API. Hecho el 2026-10-16 con `CPUUtilization`: **PASS**. Consulta puntual: sin *dashboards*, alertas ni
   refresco automático (§3).

## 3. Política de uso: costo

`GetMetricData` **se cobra siempre**: USD 0.01 por 1.000 métricas en us-east-2, sin *free tier*. Para que el costo
siga en céntimos:
- **Paneles bajo demanda.** Sin *auto-refresh* por debajo de 5 minutos y con rangos de tiempo moderados.
- **Sin reglas de alerta de Grafana** que consulten CloudWatch: cada evaluación es una petición cobrada. Las alertas
  son las **8 alarmas de CloudWatch** de H-031-8, gratuitas, y Grafana solo muestra su estado.
- Solo las métricas de `AWS/RDS` necesarias.
- **Revisión:** `Task/041` revisa el consumo real con Cost Explorer (tipo de uso `USE2-CW:GMD-Metrics`).

## 4. Verificación al terminar el trial de Grafana

**Cuándo:** el día en que termina el trial de 14 días del stack, hacia el 2026-10-22.

1. En el portal de Grafana, comprobar que el stack quedó en el plan **Free**, sin cargos y sin método de pago.
2. Repetir **Save & test**: las métricas deben seguir respondiendo.
3. Anotar el resultado en el reporte de la tarea vigente.

## 5. Retirar la integración

- Quitar el rol es **destruir un recurso IAM productivo**. Exige la autorización explícita del usuario y un plan de
  Terraform revisado con su guarda. Nunca se borra a mano.
- En Grafana, borrar el origen de datos o vaciar su *Assume Role ARN*.
