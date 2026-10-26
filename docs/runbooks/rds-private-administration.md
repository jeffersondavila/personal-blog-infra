# Administración privada de RDS: migraciones, purga y recuperación

**Runbook Vigente.** Diseño de `Task/029-Preparar-PostgreSQL-Produccion-en-RDS`,
**aprobada** el 2026-09-27, ampliado en `Task/031`, **aprobada** el 2026-10-21. *(Hasta `Task/031`: no
ejecutado; no existían RDS, VPC, ejecutor ni credenciales.)* `Task/031` ejecutó en AWS las identidades
SQL, `verify`, `export` y el restore sintético (H-031-6 y H-031-7); las migraciones y `purge` son de
`Task/036`. **Este documento no autoriza ejecutar nada**: cada operación exige su tarea propietaria y la
autorización explícita del usuario.
Contrato completo:
[paquete de decisiones §8](../architecture/production-postgresql-rds-decisions.md#8-d-24--canal-privado-de-administración-y-migraciones--resuelta).

Owners: `Task/031` provisiona el ejecutor y hace el primer restore · `Task/036` ejecuta la
primera migración, la recuperación del administrador y la purga · `Task/038` automatiza el
canal · `Task/040` lo valida.

> **Estado por fases (`Task/031` H-031-5, 2026-10-06).** RDS y la red existen desde H-031-3. La ejecutora
> llega por fases:
>
> - **H-031-5:** el *shell* sin base de datos. Responde `selfcheck` y declara los modos de este runbook
>   como `NOT_IMPLEMENTED`.
> - **H-031-6:** la conexión con `verify-full`, la entrega de credenciales y el modo `verify`.
> - **`Task/036`:** Alembic, las migraciones y `purge`.
>
> - **H-031-6 a H-031-9, preparados offline (2026-10-07):** `verify`, `identidades`, `sintetico` y `export` están implementados en el artefacto h0316, con integración local real, pero **no desplegados**. La cuota de concurrencia de Lambda bloquea el apply ([reporte §46](../task-reports/TASK-031-report.md#46-remainder--h-031-6-a-h-031-9-preparados-offline-aws-bloqueado-por-la-cuota-de-lambda-2026-10-07)).
> - **2026-10-15:** H-031-8 (alarmas) y H-031-9 (rol de Grafana) se aplicaron sin la ejecutora, que sigue fuera del root hasta la cuota. Este canal **no cambia** y sigue sin desplegarse ([reporte §47](../task-reports/TASK-031-report.md#47-h-031-8-y-h-031-9--alarmas-de-d-11-y-rol-de-d-20-aplicados-y-convergentes-2026-10-08-a-2026-10-15)).
>
> - **2026-10-18 — D-24 modificada, aprobada por el usuario el 2026-10-19:** la ejecutora vuelve al root **sin concurrencia reservada**; las escrituras administrativas se excluyen con un bloqueo de aviso de PostgreSQL y la cuota de Lambda deja de bloquear. **Desplegada el 2026-10-19 como *shell* h0315**: responde `selfcheck`, y los modos de este runbook siguen `NOT_IMPLEMENTED` hasta H-031-6 y `Task/036` ([reporte §49.15](../task-reports/TASK-031-report.md#4915-aprobación-de-d-24-y-40-y-apply-de-h-031-5-2026-10-19)).
>
> - **2026-10-20 y 2026-10-21:** H-031-6 (`identidades`, `verify` y `export`) y H-031-7 (marcador sintético,
>   restore PITR y limpieza) se ejecutaron en AWS ([reporte §51](../task-reports/TASK-031-report.md#51-h-031-6-aplicada-y-verificada-y-h-031-7-completa-2026-10-20-y-2026-10-21)). El canal quedó **aprobado con
>   `Task/031` el 2026-10-21**; Alembic, las migraciones y `purge` siguen en `Task/036`.
>
> Ningún procedimiento de este runbook es ejecutable antes de su fase
> ([reporte §44](../task-reports/TASK-031-report.md#44-h-031-5--ejecutora-privada-de-d-24-por-fases-implementación-offline-y-cuota-lambda-2026-10-06)).

## 1. Por qué existe este canal

RDS será **privado** (`publicly_accessible = false`). Eso implica tres cosas que este
runbook asume sin discutirlas:

- **No hay SSH ni *host***: RDS no da acceso al sistema operativo.
- **Un *runner* público de GitHub Actions no alcanza la base de datos** solo por tener
  identidad OIDC. Le falta la **ruta de red**, no el permiso.
- **Abrir la base de datos a Internet, aunque sea «temporalmente», está prohibido.**
  ADR-010 y **R-30**. No hay excepción por conveniencia ni por urgencia.

El mecanismo es una **Lambda ejecutora dedicada** en las subnets privadas, invocada por el
plano de control de AWS.

## 2. Requisitos previos

Ninguna operación de este runbook empieza sin **todos** estos puntos:

1. **D-06 resuelta y aprobada** (`Task/030`): backend de *state* en S3 con
   `use_lockfile = true`, y **EX-028-C7 extinguida**. No existe RDS antes de esto.
2. **Conciencia del vencimiento de la cuenta.** El usuario decidió el 2026-09-27 **conservar
   el plan gratuito**: el Paid Plan **no** es prerrequisito. A cambio, la fecha
   **2027-03-15** y el saldo de créditos son un **gate operativo** (**R-47**): antes de
   llegar a cualquiera de los dos hace falta una decisión explícita entre continuar pagando
   o desmontar, y la **§6.1** debe haberse ejecutado con éxito si la respuesta es desmontar.
   **Ninguna operación de este runbook renueva nada por inercia.**
3. Autorización explícita del usuario para la operación concreta, con su alcance.
4. Identidad humana operativa con MFA. **Nunca root. Nunca *access keys*.**
5. Artefacto del ejecutor identificado por **digest**, con Alembic, `psycopg`, el bundle
   de la CA de RDS y las migraciones.
6. Terraform **1.16.7** y provider AWS **6.70.0**, con el *lock* del repositorio.

**Nunca:** `TF_LOG`, `set -x`, *endpoints* alternativos, perfiles ajenos, un segundo
escritor del *state*, ni volcar la `DATABASE_URL` o una contraseña en la salida.

## 3. Identidades

| Identidad | Uso | Quién la posee |
| --- | --- | --- |
| `blogadmin` (*master*) | **Solo** recuperación autorizada | Generada en `Task/031` por procedimiento privado |
| `blog_migrate` | Migraciones y purga. DDL sobre el esquema | Ejecutor privado |
| `blog_app` | La aplicación. **Sin DDL** | Lambda de la aplicación |

Que `blog_app` no tenga DDL es lo que garantiza que **una migración no puede ocurrir como
efecto lateral del arranque de la Lambda**: el motor lo rechazaría.

El rol IAM del ejecutor es **propio**: distinto del rol de la Lambda de aplicación, del rol
de validación de `Task/028`, del de despliegue y del de Terraform.

## 4. Procedimiento — migración (owner `Task/036`, automatiza `Task/038`)

1. **Comprobar el estado.** Instancia `available`; sin acciones de mantenimiento
   pendientes; `LatestRestorableTime` avanzando.
2. **Tomar un *snapshot* manual** y esperar a que esté `available`. Registrar su
   identificador. Un *backup* automático **no** es un punto de control elegido.
3. **Verificar la revisión objetivo.** `alembic history` local frente a la revisión que el
   artefacto contiene; confirmar que el `downgrade` está probado en local. Si no es seguro,
   documentar el *roll-forward* **antes** de continuar.
4. **Confirmar la serialización.** Ninguna otra operación administrativa en curso.
   *Modificado el 2026-10-18 y aprobado por el usuario el 2026-10-19:* el ejecutor ya **no** reserva
   concurrencia. `upgrade`, `downgrade` y `purge` toman `pg_try_advisory_xact_lock(3364, 1)` en su
   misma conexión (criterio que hereda `Task/036`). Si el ejecutor responde `OPERACION_EN_CURSO`,
   **no reintentar**: averiguar qué operación tiene el bloqueo y esperar a que termine. El bloqueo
   ordena SQL; restores, PITR y *snapshots* conservan sus propias guardas.
5. **Invocar el ejecutor** en modo `upgrade`, por el plano de control, con la identidad
   autorizada.
6. **Medir la duración.** Techo duro de Lambda: **900 s**. Si la migración no cabe,
   **detenerse y pedir decisión explícita**; no partirla en trozos sin registrarlo ni
   introducir un servicio excluido.
7. **Verificar.** Revisión aplicada leída de `alembic_version`; comprobaciones funcionales
   mínimas del esquema.
8. **Registrar** fecha, revisión, duración, *snapshot* previo y quién ejecutó.

### Si falla

No improvisar. En este orden:

1. **No reintentar a ciegas.** Leer la salida saneada y determinar si la transacción quedó
   abierta o revertida.
2. Si la revisión quedó a medias y el `downgrade` es seguro: invocar en modo `downgrade` a
   la revisión anterior y verificar.
3. Si el `downgrade` no es seguro o el esquema quedó inconsistente: **restaurar desde el
   *snapshot* del paso 2** siguiendo la §6, y cambiar `DATABASE_URL`.
4. Registrar el incidente y la causa **antes** de volver a intentarlo.

## 5. Procedimiento — purga y retención (R-44, owner `Task/036`)

Mismo ejecutor, modo `purge`, invocación programada. Identidad SQL `blog_migrate`:
**nunca `blog_app`**, porque la aplicación no debe poder borrar su propio historial.

| Tabla | Criterio de borrado |
| --- | --- |
| `login_rate_limits` | Ventana expirada hace más de **7 días** |
| `administrator_sessions` | Caducadas o revocadas con más de **30 días** |

Reglas: sentencias **acotadas por la condición de retención**, nunca un `DELETE` de tabla
completa; contar filas antes y después y registrar ambos números; ninguna de las dos tablas
alimenta un listado, así que la purga no afecta a ninguna vista.

## 3.1 Procedimiento — identidades SQL (`Task/031` H-031-6)

Con el operador `scripts/terraform_datos/operar_ejecutora.py` y sus dependencias fijadas (`scripts/terraform_datos/requirements-operador.txt`), con `aws login --profile personal-blog`. **Nada toca el disco ni la línea de órdenes.**

1. Las contraseñas de `blog_migrate` y `blog_app` se generan en memoria en el proceso que aplica `terraform-datos` y se custodian en sus SecureString con `value_wo` (módulo `credenciales_sql`).
2. `python -m scripts.terraform_datos.operar_ejecutora identidades`: lee la master y las dos contraseñas en memoria, calcula los verificadores SCRAM y los envía. La ejecutora crea o ajusta los roles y relee: si algo no coincide con D-23, **revierte todo**.
3. `verify --usuario blogadmin --controles-negativos`, `verify --usuario blog_app` (el `CREATE TABLE` debe fallar) y `verify --usuario blog_migrate`.
4. **Rotación:** incrementar la versión de esa identidad en Terraform, aplicar y repetir el paso 2.

El verificador SCRAM queda en el log de PostgreSQL por `log_statement = ddl`; la contraseña, no.

## 6. Procedimiento — restore y PITR

PITR y restore de *snapshot* **crean una instancia nueva**; no sobrescriben la existente.
Objetivos: **RPO ≤ 15 min**, **RTO ≤ 4 h**.

1. **Decidir el punto de recuperación**: *snapshot* concreto, o instante para PITR dentro
   de la ventana de retención de 7 días.
2. **Restaurar a una instancia nueva**, con el **mismo** DB subnet group, security group
   `sg-rds`, *parameter group* personalizado y clave KMS. Sin acceso público.
3. **Verificar integridad** con el ejecutor privado: revisión de `alembic_version`, conteos
   por tabla y comprobaciones de consistencia.
4. **Medir y registrar** el tiempo total desde la decisión hasta la verificación
   completa — ese es el RTO real, no el tiempo de creación de la instancia.
5. **Cambiar `DATABASE_URL`** al nuevo *endpoint* solo si el restore sustituye a la
   productiva. Redesplegar para que la nueva configuración llegue a la Lambda.
6. **Limpieza autorizada.** Una instancia temporal olvidada cuesta lo mismo que la
   productiva: ≈ 0.92 USD por una prueba de 48 h. Registrar la autorización del borrado.

**Un *backup* existente no es un restore probado.** Ni `available`, ni un
`LatestRestorableTime` que avanza, demuestran recuperación.

**Restore sintético de `Task/031` H-031-7.** `scripts/terraform_datos/restore_sintetico.py`, con un manifiesto local sin host, cuenta ni ARN:

1. `preflight` (solo lectura).
2. `sembrar` (marcador no sensible por la ejecutora).
3. `restaurar --identificador blog-prod-restore-h0317-AAAAMMDDhhmmss`: registra el identificador **antes** de crear; temporal privada, sin *backups*, sin exportar logs y etiquetada `Temporal=true`.
4. `verificar` (misma huella).
5. `limpiar`: solo la temporal de esa corrida; lista lo que borra y demuestra la ausencia por API.
6. `informe` (RPO y RTO observados).

Con la retención de 1 día del plan FREE, el PITR cubre aproximadamente las últimas 24 horas.

## 6.1 Procedimiento — exportación fuera de la cuenta (owner del diseño `Task/029`)

**Este procedimiento existe porque los *backups* administrados no sobreviven al cierre de la
cuenta.** El usuario decidió el 2026-09-27 conservar el plan gratuito y decidir la continuidad
antes del agotamiento de los créditos o del **2027-03-15**. Si esa decisión es **no
continuar**, los datos tienen que estar **fuera de AWS** antes de la fecha. Diseño:
[paquete de decisiones §10.1](../architecture/production-postgresql-rds-decisions.md#101-vía-de-salida-exportación-fuera-de-la-cuenta).

`Task/031` añade el modo `export` al ejecutor · `Task/040` **demuestra** que el artefacto es
restaurable fuera de AWS · `Task/041` es el gate fechado.

1. **Comprobar el punto de partida.** Instancia `available`; anotar la revisión de
   `alembic_version`. El **esquema no se exporta**: son las revisiones de Alembic ya
   versionadas en Git.
2. **Invocar el ejecutor en modo `export`**, con `blog_migrate`. Exporta cada tabla con
   `COPY … TO STDOUT` en CSV mediante `psycopg`. **No se añade el binario `pg_dump`** al
   artefacto: sería una dependencia y una superficie nuevas.
3. **Escribir al prefijo dedicado del bucket**, por el gateway endpoint de S3. **Sin NAT.**
   El ejecutor solo tiene permiso de escritura sobre ese prefijo.
4. **Descargar a la estación del autor** con la identidad humana autorizada, desde fuera de
   la VPC. **Este es el único tramo que saca los datos de la cuenta**, y lo hace una persona,
   no la Lambda.
5. **Sincronizar los medios** del bucket a la estación con AWS CLI.
6. **Custodiar el resultado** con el mecanismo de respaldo local de `Task/004`, que ya está
   documentado como sensible y **fuera de Git** (**R-12**).
7. **Verificar que se puede restaurar**: `alembic upgrade head` sobre un PostgreSQL **17.11**
   local y carga de los CSV. Contar filas por tabla y comparar con el origen.

**Implementación de `Task/031` H-031-6:** `python -m scripts.terraform_datos.operar_ejecutora export --bucket <bucket de medios> --marca AAAAMMDDThhmmssZ`. Escribe `exportaciones/<marca>/` con un manifiesto final (filas, bytes y SHA-256 por tabla) y escritura condicional: una marca repetida da `EXPORTACION_YA_EXISTE`.

**Un CSV en un bucket no es una salida probada.** La vía de salida no cuenta como existente
hasta que `Task/040` restaure desde ella.

**Si el volcado no cupiera** en el almacenamiento efímero o en los 900 s: **detenerse y pedir
decisión explícita**, igual que con las migraciones. No trocear en silencio ni introducir un
servicio excluido.

## 7. Procedimiento — recuperación del administrador (R-43, owner `Task/036`)

Cinco intentos fallidos bloquean la cuenta 15 minutos, y la API responde **igual** que ante
credenciales inválidas: es deliberado, para no revelar que el correo existe. El propietario
puede quedar fuera sin saber por qué.

1. **Diagnosticar primero.** Buscar el evento `authentication.account_locked` en la
   auditoría. Si no está, **no es un bloqueo**: es una credencial equivocada y este
   procedimiento no aplica.
2. **Esperar es la opción correcta por defecto.** El bloqueo es temporal y **no se
   prolonga**: un intento durante el bloqueo no desplaza `locked_until`.
3. Si hay que actuar antes: por el ejecutor, con `blog_migrate`, poner `locked_until` en el
   pasado **para la cuenta afectada**. Sentencia acotada a **una fila**.
4. Si además se perdió la contraseña: rotar el hash Argon2id por el mismo canal, con un
   valor generado fuera del ejecutor y **nunca registrado en la salida**.
5. Registrar la operación con fecha, motivo y quién la ejecutó.

**No** se añade un *endpoint* de recuperación a la API pública: sería superficie de ataque
permanente para un problema que ocurre cada varios años.

## 8. Prohibiciones

- Abrir la base de datos a Internet, ni «temporalmente».
- Ampliar un security group a `0.0.0.0/0`.
- Ejecutar migraciones desde el arranque de la Lambda de aplicación.
- Ejecutar dos migraciones en paralelo.
- Migrar sin *snapshot* previo.
- Usar `blogadmin` para operación normal.
- Usar `blog_app` para DDL o para purgar.
- Registrar la `DATABASE_URL`, una contraseña o un volcado de datos en la salida o en logs.
- Deshabilitar o programar el borrado de una clave KMS como parte de una prueba.
- `destroy` real automático desde CI.
- Introducir EC2, ECS, EKS, ECR, ALB o NAT Gateway sin decisión explícita previa.

## 9. Referencias

- [Paquete de decisiones de `Task/029`](../architecture/production-postgresql-rds-decisions.md)
  — §8 canal privado, §10 recuperación, §11 checkpoint humano.
- [Canónico RDS](../architecture/production-postgresql-rds.md) — **Vigente**.
- [ADR-010](../adr/ADR-010-production-postgresql-on-rds.md) — **Aceptada**.
- [Decisiones diferidas](../architecture/open-decisions.md) — D-10, D-12, D-22 a D-24.
- [Runbooks de despliegue](README.md) — creación, validación, *rollback*, recuperación y
  destrucción del grafo existente. `Task/031` los extiende antes de operar los recursos
  nuevos.
