# Supervisión manual de los backups de RDS

**Runbook de `Task/031`, bloqueo B3.** El usuario aprobó la opción A el 2026-10-16: supervisión **manual** de solo
lectura, sin EventBridge, SNS, métricas personalizadas ni alarmas nuevas. Contexto en el
[reporte de Task/031, §48](../task-reports/TASK-031-report.md#48-bloqueos-b1-b3-y-b4--decisiones-del-usuario-del-2026-10-16).

**Estado.** Propuesta — pendiente de aprobación: se consolida con el `approved` de `Task/031`.

## 1. Por qué es manual y qué hueco cubre

RDS **no publica ningún evento de «backup fallido»** para instancias. Solo publica:
- el inicio (`RDS-EVENT-0001`) y el fin (`RDS-EVENT-0002`) del backup diario;
- `RDS-EVENT-0028`, cuando se desactivan los backups automáticos;
- los eventos de la categoría `failure`.

Por eso el fallo se detecta por **ausencia**. Las 8 alarmas de D-11 no lo cubren. Esta comprobación tampoco avisa a
nadie: solo detecta cuando alguien la ejecuta.

## 2. Cuándo ejecutarlo

- Al menos **una vez por semana**.
- **Antes** de cualquier operación sobre RDS: restore, migración o cambio de configuración.
- Después de una ventana de mantenimiento.
- **Fuera** de la ventana de backup (07:00-07:30 UTC). Durante esa ventana la instancia puede estar en
  `backing-up`, y el diagnóstico la marca como no disponible.

## 3. Cómo ejecutarlo

Requisito: una sesión vigente de `personal-blog`. Primero hay que volver a cambiar al rol en la consola y después
ejecutar `aws login --profile personal-blog --region us-east-2`. El comando se lanza desde la raíz de
`personal-blog-infra`.

```bash
python -m scripts.terraform_datos.diagnostico_backups
```

Es de **solo lectura**. Hace tres llamadas de la AWS CLI: `sts get-caller-identity`, `rds describe-db-instances` y
`rds describe-events` (14 días). Devuelve un JSON sin cuentas ni ARN.

## 4. Qué comprueba y por qué esos umbrales

| Comprobación | Umbral | Justificación |
| --- | --- | --- |
| Instancia disponible | `available` | Cualquier otro estado necesita revisión |
| Retención | **1 día** | Excepción vigente del plan FREE (§34 del reporte); 0 significa backups desactivados |
| Último backup **terminado** | **26 h** como máximo | Hay un backup al día en la ventana 07:00-07:30 UTC. Justo antes de que acabe la siguiente ventana, el último tiene hasta 24 h 30 min. El margen cubre la duración observada (2-5 min) y el retraso de los eventos |
| Backup iniciado sin terminar | **2 h** como máximo | Los observados tardan de 2 a 5 minutos |
| Retraso de `LatestRestorableTime` | **15 min** como máximo | Es el objetivo de RPO de D-10. Un retraso acotado implica que el PITR sigue avanzando |
| Eventos de backups desactivados (`0028`) o de categoría `failure` | **Ninguno** en 14 días | Es todo lo que guarda RDS |

**La ausencia de datos es un fallo, nunca un OK:** sin eventos o sin `LatestRestorableTime`, el resultado es FALLO.

## 5. Interpretar el resultado

| Salida | Estado | Qué hacer |
| --- | --- | --- |
| 0 | `OK` | Nada. Anotar la fecha de la comprobación |
| 1 | `FALLO` y su lista de `hallazgos` | Revisar cada hallazgo (tabla siguiente). **No** cambiar la retención, la instancia ni los backups sin una decisión |
| 3 | `ERROR_DE_AWS` con un `codigo` | Repetir más tarde. Si persiste, revisar la CLI o los permisos. No es un OK |
| 4 | `CREDENCIALES_CADUCADAS` | Renovar el rol en la consola, hacer `aws login` y repetir |
| 5 | `IDENTIDAD_NO_AUTORIZADA` | El perfil no es `PersonalBlogAdministrator`. Detenerse |

| Hallazgo | Lectura |
| --- | --- |
| `INSTANCIA_NO_DISPONIBLE` | Si es `backing-up`, repetir fuera de la ventana. Cualquier otro estado necesita revisión |
| `INSTANCIA_INEXISTENTE` | Incidente: la instancia productiva no existe |
| `BACKUPS_DESACTIVADOS` o `BACKUPS_DESACTIVADOS_EN_EVENTOS` | Alguien desactivó los backups automáticos. Incidente |
| `RETENCION_DISTINTA` | La retención cambió respecto de la excepción de §34. Revisar si hubo una decisión |
| `SIN_BACKUP_RECIENTE` | No hay ningún backup terminado en 26 h. Mirar los eventos en la consola de RDS |
| `BACKUP_ATASCADO` | Hay un backup iniciado hace más de 2 h que no ha terminado |
| `PITR_RETRASADO` o `PITR_SIN_DATOS` | El PITR no cumple el RPO de D-10 |
| `RELOJ_DESFASADO` | El reloj local va adelantado o atrasado: corregirlo antes de interpretar nada |
| `FALLO_DE_INSTANCIA` | Hay un evento `failure` de RDS. Incidente |

## 6. Límites

- Ningún aviso automático: la detección depende de la frecuencia de ejecución.
- RDS conserva 14 días de eventos. Un incidente más antiguo ya no aparece.
- No demuestra que se pueda **restaurar**: eso es el restore probado de H-031-7 y `Task/040`.
- La alternativa automática, EventBridge → CloudWatch Logs → filtro de métrica → alarma, queda como mejora posterior
  y requiere una aprobación propia.
