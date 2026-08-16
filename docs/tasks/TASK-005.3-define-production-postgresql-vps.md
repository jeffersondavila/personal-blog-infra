# TASK-005.3 — Definir PostgreSQL de producción en VPS

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Nombre** | Definir PostgreSQL de producción en VPS externo |
| **Tipo** | **Mantenimiento de arquitectura y gobierno documental** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**5 de 41**) ni la ETAPA 02 (**1 de 3**) |
| **Etapa de referencia** | Afecta al alcance futuro de la [ETAPA 09](../stages/STAGE-09-cloud-accounts.md), con reflejo en la [ETAPA 08](../stages/STAGE-08-cloud-ready.md) y la [ETAPA 10](../stages/STAGE-10-cloud-deployment.md) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` — **Aprobada** ✔, PR `#8` **fusionado** (merge `5583947`) y normalización `main → dev` completada |
| **Rama** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS`, creada desde `dev` (**`a563de6`**). **Publicada en el cierre** |
| **Fecha de inicio** | 2026-08-15 |
| **Fecha de aprobación** | 2026-08-15 |
| **Última actualización** | 2026-08-15 — cierre aprobado |
| **Próxima tarea** | `Task/006-Fundacion-Frontend-React` — **Pendiente, no iniciada** |

---

## 1. Contexto

[ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md) adoptó una arquitectura serverless de
escalado a cero y dejó escrita su única excepción:

> «La base de datos administrada es el **único componente con costo fijo** de la
> arquitectura.»

Esa excepción se aceptó sin datos. Al acercarse la ETAPA 09 aparecen dos problemas:

1. **Costo desproporcionado.** En una arquitectura donde API Gateway, Lambda, S3, SSM y
   CloudWatch cuestan prácticamente cero en reposo, una base de datos administrada **domina
   la factura** y cuesta más que todo lo demás junto — para servir un blog de tráfico bajo.
2. **Pérdida del aprendizaje operacional.** El proyecto es también formación. Pagar por que
   un proveedor gestione el sistema operativo, PostgreSQL, la seguridad, los backups y la
   recuperación **elimina justo lo que se quiere aprender**.

Al mismo tiempo, **no se quiere abandonar AWS ni serverless**: es un objetivo explícito del
proyecto y el motivo de [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md).

## 2. Objetivo

Formalizar, por escrito y de forma versionada:

> **PostgreSQL de producción será autogestionado en un VPS económico, independiente de AWS,
> mientras el backend FastAPI permanece en AWS Lambda.**

Y hacerlo **antes** de la ETAPA 09, porque la decisión cambia el alcance de `Task/029` y la
forma de escribir la infraestructura desde el primer archivo.

El resultado es un documento canónico —
[`docs/architecture/production-postgresql-vps.md`](../architecture/production-postgresql-vps.md)
— más un ADR en estado **Propuesta** y las referencias necesarias en decisiones, roadmap,
estado, fichas de etapa, arquitectura, seguridad e instrucciones de Claude.

## 3. Dentro del alcance

- [x] Crear el documento canónico `docs/architecture/production-postgresql-vps.md`.
- [x] Formalizar la arquitectura: **Cloudflare → API Gateway → Lambda → TLS → PgBouncer →
      PostgreSQL en VPS**, con diagramas Mermaid.
- [x] Separar los *boundaries* **Cloudflare / AWS / VPS** y sus responsabilidades.
- [x] Declarar explícitamente **qué no cambia**: Lambda, API Gateway, S3, SSM, CloudWatch,
      IAM, Terraform, Floci, Cloudflare Pages y el entorno local.
- [x] Registrar las responsabilidades que el proyecto **asume** al autogestionar.
- [x] Documentar **PgBouncer** y su propósito, **sin fijar ningún número**.
- [x] Fijar la regla: **PostgreSQL nunca se expone a Internet**, y que un puerto distinto
      **no** es un control de seguridad.
- [x] Fijar el baseline de conexión: **TLS obligatorio**, validación de certificado,
      **SCRAM-SHA-256** preferente y **mTLS evaluable pero no obligatorio**.
- [x] Preservar la abstracción **`DATABASE_URL`**: la aplicación no conoce el destino.
- [x] Registrar **Reserved Concurrency** como control futuro, sin fijar `N`.
- [x] Declarar que la Lambda **permanece fuera de VPC** y que **no se introduce NAT Gateway**,
      con la precisión —basada en documentación oficial de AWS— de que **NAT Gateway no es
      una consecuencia inherente de RDS**.
- [x] Registrar el requisito de **latencia y región**, con **RTT medido**.
- [x] Formalizar **backups fuera del host** y la regla **«un backup no está validado hasta
      haberse restaurado»**.
- [x] Dejar **PITR/WAL** como evaluación futura, no requisito del MVP.
- [x] Aceptar explícitamente el **SPOF** y no introducir alta disponibilidad.
- [x] Registrar **RPO/RTO** como intención, **nunca como SLA**.
- [x] Documentar **Terraform multi-provider** y la regla de no crear abstracciones ficticias.
- [x] Actualizar el impacto en **Floci**, conservando los hallazgos históricos sobre RDS.
- [x] Registrar la **resolución propuesta de D-01**, separando *modelo* de *proveedor*.
- [x] Ampliar el alcance de **D-10**.
- [x] Renombrar `Task/029` **conservando su identificador** y redefinir su alcance.
- [x] Crear **ADR-007** en estado `Propuesta`, con alternativas A–D y criterios de revisión.
- [x] Marcar en **ADR-003** que su fila «Base de datos» queda modificada parcialmente.
- [x] Ampliar **security-boundaries** con **C-13**, **C-14**, **C-15** y la nueva §9.
- [x] Registrar los riesgos **R-29** a **R-35**.
- [x] Añadir la sección **PRODUCTION DATABASE LAW** a `PROJECT_INSTRUCTIONS.md`.
- [x] Registrar en `STATUS.md` el cierre de `Task/005.2` y esta tarea.
- [x] Crear ficha y reporte, y actualizar el índice de reportes.

## 4. Fuera del alcance

| Elemento | Motivo o tarea |
| --- | --- |
| Contratar un VPS o crear cuenta en un proveedor | Tarea **exclusivamente documental**. `Task/029`. |
| **Seleccionar proveedor, región o tamaño** | `Task/029`, con **precios actuales**, no heredados. |
| Instalar PostgreSQL o PgBouncer | `Task/029`. |
| Fijar `pool_size`, `max_client_conn`, `max_connections`, `pool_mode` o *timeouts* | Deben salir de **pruebas**, no de intuición. `Task/029`, `Task/032`. |
| Crear `docker-compose` del VPS o modificar el actual | El entorno local no se toca. |
| Modificar FastAPI, el frontend, SQLAlchemy, psycopg o `DATABASE_URL` real | La abstracción ya existe; por eso este cambio no toca código. |
| Crear secretos, certificados o claves | `Task/029`. Ningún secreto se versiona. |
| Abrir puertos, configurar firewall o crear usuarios SSH | `Task/029`. |
| Ejecutar `pg_dump` o subir backups | `Task/029`, `Task/026`. |
| Crear buckets nuevos | `Task/030`. |
| Crear Terraform, providers, *state* o ejecutar `init/plan/apply/destroy` | `Task/025`, `Task/029`. |
| Crear RDS, NAT Gateway o mover Lambda a VPC | Excluidos por [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md) y [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md). |
| Crear recursos AWS o instalar Floci | Fuera de alcance. |
| Resolver **D-06** — backend de estado de Terraform | `Task/025`. |
| Decidir si se adopta **mTLS** o **PITR** | `Task/029`. |
| Fijar frecuencia y retención de backups | `Task/029`, **D-10**. |
| Añadir, eliminar o renumerar tareas del roadmap | Las 41 se conservan intactas. |
| Modificar `BACKEND_TESTING_STRATEGY.md` | La política TDD sigue íntegra y no la toca esta tarea. |
| Modificar, regenerar o mover `images/Infraestructura.png` | Es un asset del usuario. Se reetiqueta como *arquitectura objetivo inicial, anterior a esta decisión*. |
| Iniciar `Task/006` | No se inicia la tarea siguiente sin cerrar la actual. |

## 5. Entregables

| Entregable | Ruta | Acción |
| --- | --- | --- |
| **Documento canónico** de la capa de datos de producción | `docs/architecture/production-postgresql-vps.md` | **Creado** |
| **ADR-007** — PostgreSQL de producción en VPS (**Propuesta**) | `docs/adr/ADR-007-production-postgresql-on-vps.md` | **Creado** |
| Ficha de esta tarea | `docs/tasks/TASK-005.3-define-production-postgresql-vps.md` | **Creado** |
| Reporte de esta tarea | `docs/task-reports/TASK-005.3-report.md` | **Creado** |
| Decisiones diferidas — **D-01** y **D-10** | `docs/architecture/open-decisions.md` | Modificado |
| Ficha de la ETAPA 09 — `Task/029` redefinida | `docs/stages/STAGE-09-cloud-accounts.md` | Modificado |
| Ficha de la ETAPA 08 — RDS ya no es destino | `docs/stages/STAGE-08-cloud-ready.md` | Modificado |
| Visión general de arquitectura | `docs/architecture/overview.md` | Modificado |
| Correspondencia local → nube | `docs/architecture/local-to-cloud-mapping.md` | Modificado |
| Límites de seguridad — **C-13/C-14/C-15** y §9 | `docs/architecture/security-boundaries.md` | Modificado |
| Paridad AWS local — §8 y §6.9 | `docs/architecture/aws-local-parity.md` | Modificado |
| Arquitectura de software — pooling | `docs/architecture/software-architecture.md` | Modificado |
| ADR-003 — nota de modificación parcial | `docs/adr/ADR-003-serverless-low-cost-cloud.md` | Modificado |
| Roadmap — `Task/029` | `docs/project-management/ROADMAP.md` | Modificado |
| Estado del proyecto | `docs/project-management/STATUS.md` | Modificado |
| Ley compacta para las sesiones de Claude | `docs/claude/PROJECT_INSTRUCTIONS.md` | Modificado |
| Alcance del MVP | `docs/product/MVP_SCOPE.md` | Modificado |
| Runbook de backup local — enlace al futuro | `docs/runbooks/local-backup-and-recovery.md` | Modificado |
| Índice de reportes | `docs/task-reports/README.md` | Modificado |
| README del repositorio | `README.md` | Modificado |

**4 creados · 16 modificados · 0 eliminados — 20 archivos afectados.** Todos en
`personal-blog-infra`. **0 archivos** en `personal-blog-backend` y **0** en
`personal-blog-frontend`. **0 archivos Terraform. 0 cambios en `docker-compose.yml`. 0
cambios en `images/`.**

## 6. Criterios de aceptación

| # | Criterio | Estado |
| --- | --- | --- |
| 1 | `main` y `dev` verificados, sincronizados y con `main` contenida en `dev`. | Cumplido — validación 1 |
| 2 | Rama `Task/005.3` creada desde `dev` normalizado, sin sobrescribir nada. | Cumplido — validación 2 |
| 3 | Backend y frontend verificados y **sin modificar**. | Cumplido — validación 3 |
| 4 | Existe un único documento canónico con la estrategia completa. | Cumplido — validación 4 |
| 5 | La arquitectura queda representada en **Mermaid**, con los tres *boundaries*. | Cumplido — validación 4 |
| 6 | Está declarado explícitamente **qué no cambia**. | Cumplido — validación 5 |
| 7 | **PgBouncer** documentado, **sin fijar ningún número**. | Cumplido — validación 6 |
| 8 | **PostgreSQL nunca público**, y el puerto no cuenta como control. | Cumplido — validación 7 |
| 9 | **TLS obligatorio**, **SCRAM** preferente, **mTLS** no obligatorio. | Cumplido — validación 8 |
| 10 | La abstracción **`DATABASE_URL`** se conserva y se declara. | Cumplido — validación 9 |
| 11 | La Lambda **permanece fuera de VPC** y **no se introduce NAT Gateway**; la relación real entre RDS, VPC y NAT queda precisada con fuente oficial. | Cumplido — validación 10 |
| 12 | **Reserved Concurrency** registrada como control futuro, sin fijar `N`. | Cumplido — validación 10 |
| 13 | Latencia y región registradas con **RTT medido** como criterio. | Cumplido — validación 11 |
| 14 | **Backups fuera del host** y **restore probado** como reglas obligatorias. | Cumplido — validación 12 |
| 15 | **PITR** queda como futuro, no como requisito del MVP. | Cumplido — validación 12 |
| 16 | **SPOF aceptado**; no se introduce alta disponibilidad. | Cumplido — validación 13 |
| 17 | **RPO/RTO** como intención, nunca como SLA. | Cumplido — validación 13 |
| 18 | **Proveedor de VPS no seleccionado**; ningún nombre elegido. | Cumplido — validación 14 |
| 19 | El objetivo de costo se registra **sin convertirlo en compromiso**. | Cumplido — validación 14 |
| 20 | **Terraform multi-provider** documentado, sin crear archivos. | Cumplido — validación 15 |
| 21 | **Floci** actualizado: RDS ya no es destino; hallazgos históricos **conservados**. | Cumplido — validación 16 |
| 22 | **D-01** con resolución propuesta durante la ejecución; **Resuelta** en cuanto al **modelo** al aprobarse la tarea. El proveedor sigue en `Task/029`. | Cumplido — validación 17 |
| 23 | **Task/029** conserva el ID `029` y cambia nombre y alcance. | Cumplido — validación 18 |
| 24 | **ADR-007** creado en estado `Propuesta` durante la ejecución y **`Aceptada`** al aprobarse la tarea; **ADR-006** sigue `Aceptada`. | Cumplido — validación 19 |
| 25 | Seguridad: **C-13**, **C-14**, **C-15**, §9 y reglas **V-01 a V-13**. | Cumplido — validación 20 |
| 26 | Riesgos **R-29** a **R-35** registrados. `Propuesto` durante la ejecución; **`Abierto`** tras la aprobación. **Ninguno cerrado.** | Cumplido — validación 21 |
| 27 | Exactamente **41 tareas**, ninguna renumerada; avance **5 de 41**; ETAPA 02 **1 de 3**; `Task/006` **Pendiente**. | Cumplido — validación 22 |
| 28 | `PROJECT_INSTRUCTIONS.md` enlaza al canónico sin duplicarlo. | Cumplido — validación 23 |
| 29 | Todos los enlaces relativos resuelven. | Cumplido — validación 24 |
| 30 | `images/Infraestructura.png` **intacta**. | Cumplido — validación 25 |
| 31 | Cero implementación: sin VPS, PostgreSQL, PgBouncer, Terraform, RDS, NAT ni recursos AWS. | Cumplido — validaciones 26 a 28 |
| 32 | Sin commit, sin push, sin merge y sin PR **mientras la tarea no estuvo aprobada**; quedó `Lista para validación`. El commit, la integración en `dev` y el PR se ejecutaron **solo tras la aprobación explícita del usuario**. | Cumplido — validación 29 |

## 7. TDD / Plan test-first

**No aplica.** Esta tarea no introduce comportamiento funcional del backend: es
documentación de arquitectura y gobierno. **`BACKEND_TESTING_STRATEGY.md` no se modifica** y
la regla **RED → GREEN → REFACTOR** sigue íntegra.

La verificación equivalente consiste en:

| Verificación equivalente |
| --- |
| **Consistencia documental** entre los 20 archivos afectados |
| **Consistencia arquitectónica**: lo que permanece en AWS y lo que vive en el VPS |
| **Integridad del roadmap**: 41 tareas, IDs únicos, sin renumerar |
| **Estado de Git** verificado, no asumido |
| **Ausencia de implementación** comprobada explícitamente |

> Cuando una tarea futura modifique el código de persistencia o el comportamiento del
> backend —por ejemplo al adaptar el patrón de conexión a PgBouncer— **la política TDD
> vigente sigue siendo obligatoria**.

## 8. Plan de validación

Cada criterio se comprueba por: verificación del estado real de Git y de GitHub; búsqueda de
términos en los documentos afectados; verificación de enlaces relativos; recuento de las
tareas del roadmap; y comprobación de **ausencia** —de archivos Terraform, de secretos, de
cambios en repositorios ajenos y de cualquier recurso creado.

## 9. Comandos de validación

```powershell
$env:PATH = "$env:PATH;C:\Program Files\GitHub CLI"
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra
$bt = [char]96

# 1. Estado de Git
git branch --show-current
git status --porcelain -b
git log --oneline dev..main          # vacio
git diff --stat main dev             # vacio
git ls-remote --heads origin "Task/*"

# 2. Recuento del roadmap: deben seguir siendo 41
(Select-String -Path docs\project-management\ROADMAP.md -Pattern ('^\| ' + $bt + 'Task/0')).Count

# 3. Task/029 conserva su ID y cambia de nombre
Select-String -Path docs\project-management\ROADMAP.md,docs\project-management\STATUS.md `
  -Pattern "Task/029-Preparar-PostgreSQL-Produccion-en-VPS"

# 4. Estados propuestos, no aceptados
Select-String -Path docs\adr\ADR-007-production-postgresql-on-vps.md -Pattern "Propuesta"
Select-String -Path docs\architecture\open-decisions.md -Pattern "D-01" | Select-Object -First 3

# 5. Ausencias
(Get-ChildItem -Path .. -Recurse -File -Include *.tf,*.tfvars,*.tfstate,*.hcl).Count
git status --porcelain -- docker-compose.yml images/

# 6. Repositorios no implicados
git -C ..\personal-blog-backend  status --porcelain -b
git -C ..\personal-blog-frontend status --porcelain -b

# 7. Higiene
git diff --check
```

## 10. Resultado de las validaciones

Ejecutadas el 2026-08-15. **Ninguna se declara sin haberse ejecutado.** Resultados completos
en el [reporte](../task-reports/TASK-005.3-report.md) §8.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-29 | **Nuevo.** *Single point of failure* del VPS. | Medio | Aceptado conscientemente; backups fuera del host, restore probado, infraestructura reproducible y runbook. |
| R-30 | **Nuevo.** Nueva superficie de ataque: PgBouncer expuesto, SSH y software sin parchear. Compromiso ⇒ exposición de datos. | **Alto** | Firewall *deny-by-default*, SSH por llave, PostgreSQL privado, TLS y SCRAM, política de parcheo. |
| R-31 | **Nuevo.** Backup inexistente, corrupto o no restaurable. | **Alto** | Un backup no está validado hasta haberse restaurado; el restore es criterio de salida de `Task/029`. |
| R-32 | **Nuevo.** Pérdida del VPS o del disco; agotamiento de recursos. | **Alto** | Backups fuera del host; monitoreo de disco y recursos con alertas. |
| R-33 | **Nuevo.** Agotamiento de conexiones desde Lambda. | Medio | PgBouncer con pool limitado más *Reserved Concurrency*; números derivados de pruebas. |
| R-34 | **Nuevo.** Latencia `Lambda ↔ VPS`. | Medio | Región elegida con **RTT medido**; no elegir un VPS lejano por ahorrar poco. |
| R-35 | **Nuevo.** Error humano de operación. | Medio | Infraestructura reproducible, runbooks, backups como red de seguridad. |
| R-03 | La base de datos condiciona el patrón de conexión desde Lambda. | Medio | **Actualizado**: la mitigación concreta pasa a ser PgBouncer + concurrencia reservada. Ver R-33. |

**Ninguno se cierra en esta tarea.**

## 12. Decisiones técnicas

| # | Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- | --- |
| 1 | **Crear ADR.** | Tratarlo como mantenimiento sin ADR, como `Task/005.1`. | Cambia la **arquitectura de producción** y modifica una fila de ADR-003. Es estructural, no una práctica de trabajo. | **Sí — ADR-007** |
| 2 | **ADR-007 en estado `Propuesta`.** | Marcarlo `Aceptada` directamente. | Ninguna decisión de una tarea no aprobada puede marcarse aceptada ([WORKFLOW](../project-management/WORKFLOW.md) §6). | — |
| 3 | **Modificar ADR-003 parcialmente en lugar de reemplazarlo.** | Crear un ADR que lo reemplace por completo. | Solo cambia **una fila** de su tabla. Su decisión serverless, sus exclusiones y su principio de costo siguen íntegros — de hecho ADR-007 los **refuerza**. Reemplazarlo entero destruiría contexto válido. | — |
| 4 | **Separar *modelo* de *proveedor* en D-01.** | Resolver D-01 entera aquí, eligiendo también proveedor. | Elegir proveedor exige **precios actuales** y medir RTT: hacerlo hoy sería adivinar, y quedaría obsoleto antes de llegar a `Task/029`. | No |
| 5 | **Renombrar `Task/029` conservando el ID.** | Crear una tarea nueva, o `Task/029.1`. | Añadir tareas rompería el conteo de 41 y la numeración; renumerar destruiría todas las referencias cruzadas. El **alcance** cambia, la **identidad** no. | No |
| 6 | **No fijar ningún número de pool ni de concurrencia.** | Proponer valores iniciales razonables. | Concurrencia reservada, pool de PgBouncer y `max_connections` forman **un sistema**: fijarlos sin medir crearía una falsa referencia que nadie revisaría después. | No |
| 7 | **Mantener la Lambda fuera de VPC.** | Conectarla a una VPC y alcanzar la base de datos por red privada. | Fuera de VPC, la Lambda **conserva la salida a Internet gestionada** y alcanza PgBouncer directamente. Dentro de una VPC la perdería y habría que reponerla con un mecanismo de *egress*; si fuese **NAT Gateway**, aparecería un **costo fijo** ya excluido por ADR-003. **Precisión registrada:** NAT Gateway **no es inherente a RDS** — ver [production-postgresql-vps](../architecture/production-postgresql-vps.md) §12.1. | No |
| 8 | **mTLS opcional, no obligatorio.** | Declararlo obligatorio desde ya. | Añade un modo de fallo nuevo —un certificado caducado deja el sitio sin base de datos— y exige resolver rotación y entrega a Lambda. TLS con validación correcta ya cubre la amenaza principal. | No |
| 9 | **PITR como futuro, no requisito del MVP.** | Exigir PITR desde el principio. | Un PITR mal operado es peor que un `pg_dump` diario que sí se sabe restaurar. Prioridad: backup correcto → restore probado → procedimiento reproducible. | No |
| 10 | **Aceptar el SPOF.** | Introducir réplica o *failover* desde la primera versión. | Multiplicaría costo y complejidad para proteger un blog personal de una caída que se resuelve reconstruyendo desde backup. Es la sobreingeniería que ADR-003 evita. | No |
| 11 | **Registrar el rango de costo como referencia, no como objetivo.** | Fijar un presupuesto exacto para la base de datos. | Un número escrito hoy se leería mañana como requisito y se usaría para elegir proveedor sin verificar precios. La motivación real es *que no domine la factura*. | No |
| 12 | **Conservar los hallazgos de `Task/005.2` sobre RDS en Floci.** | Borrarlos por haber quedado sin uso. | Eran correctos cuando se hicieron y siguen siéndolo: lo que cambió es el **destino elegido**, no el hallazgo. Borrarlos ocultaría por qué la decisión es informada. | No |
| 13 | **Diagramas en Mermaid, no PNG.** | Regenerar `Infraestructura.png`. | El usuario no lo pidió y el PNG es suyo. Mermaid se versiona, se diferencia en Git y se edita. | No |

## 13. Documentación creada o actualizada

Ver sección 5. **20 archivos**, todos en `personal-blog-infra`.

## 14. Resultado de pruebas

**No aplica en el sentido habitual:** la tarea no ejecuta código de aplicación ni de
infraestructura. Su equivalente son las **29 validaciones** de consistencia documental y de
estado de Git del [reporte](../task-reports/TASK-005.3-report.md) §8, todas ejecutadas.

La suite del backend **no se reejecutó**: esta tarea no toca `personal-blog-backend`, cuyo
árbol permanece limpio en `main`.

## 15. Pasos de validación para el usuario

```powershell
$env:PATH = "$env:PATH;C:\Program Files\GitHub CLI"
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra
$bt = [char]96

# 1. Rama y estado
git branch --show-current     # Task/005.3-Definir-PostgreSQL-Produccion-en-VPS
git status --porcelain -b     # 20 archivos (16 M + 4 ??), sin commit

# 2. main y dev siguen sincronizadas y sin ramas Task remotas
git diff --stat main dev                 # vacio
git ls-remote --heads origin "Task/*"    # sin resultados

# 3. Lee la estrategia y la decision
code docs\architecture\production-postgresql-vps.md
code docs\adr\ADR-007-production-postgresql-on-vps.md

# 4. El ADR NO esta aceptado y D-01 NO esta resuelta
Select-String -Path docs\adr\ADR-007-production-postgresql-on-vps.md -Pattern "Propuesta"
Select-String -Path docs\architecture\open-decisions.md -Pattern "RESOLUCION PROPUESTA|Resolución propuesta"

# 5. Task/029 conserva el ID 029
Select-String -Path docs\project-management\ROADMAP.md -Pattern "Task/029"

# 6. El roadmap sigue en 41 tareas y 5 aprobadas
(Select-String -Path docs\project-management\ROADMAP.md -Pattern ('^\| ' + $bt + 'Task/0')).Count   # 41
Select-String -Path docs\project-management\ROADMAP.md -Pattern "5 de 41"

# 7. Cero implementacion
(Get-ChildItem -Path .. -Recurse -File -Include *.tf,*.tfvars,*.tfstate,*.hcl).Count   # 0
git status --porcelain -- docker-compose.yml images/                                   # vacio

# 8. Los otros repositorios no se tocaron
git -C ..\personal-blog-backend  status --porcelain -b
git -C ..\personal-blog-frontend status --porcelain -b
```

Ningún comando es destructivo.

## 16. Deuda documental pendiente

- **No hay proveedor de VPS elegido.** Es deliberado, pero deja abierta la decisión más
  concreta hasta `Task/029`.
- **No hay números.** Pool, `max_connections` y concurrencia reservada quedan sin valores
  hasta que existan pruebas; hasta entonces **R-33** no tiene mitigación cuantificada.
- **El procedimiento de backup y restore está descrito, no escrito.** Hasta que `Task/029` y
  `Task/026` lo produzcan, **R-31** sigue sin mitigación operativa real.
- **`images/Infraestructura.png` ya no refleja la arquitectura vigente** de la capa de datos.
  Se conserva y se reetiqueta; si el usuario quiere un diagrama actualizado, debe pedirlo.

## 17. Próxima tarea

`Task/006-Fundacion-Frontend-React` — **Pendiente, no iniciada**. No comienza hasta que el
usuario fusione el PR de `Task/005.3` y se complete la normalización `main → dev`.

## 18. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Efecto en el avance** | **Ninguno.** Es mantenimiento: no cuenta dentro de las 41 tareas. Avance global **5 de 41 (12 %)**; ETAPA 02 **1 de 3**; `Task/006` **Pendiente** |

Promociones ejecutadas en el cierre:

| Elemento | Antes | Después |
| --- | --- | --- |
| [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) | `Propuesta` | **`Aceptada`** ✔ |
| [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) | `Propuesta` | **`Vigente`** ✔ |
| **D-01** | Resolución propuesta | **`Resuelta`** en cuanto al **modelo** — PostgreSQL autogestionado en VPS externo. **El proveedor, la región y el tamaño siguen pendientes en `Task/029`** |
| Riesgos **R-29** a **R-35** | `Propuesto` | **`Abierto`** — los siete. **Ninguno cerrado** |
| `security-boundaries.md` §9 y **C-13/C-14/C-15** | `Propuesta` | **`Vigente`** ✔ |
| `PROJECT_INSTRUCTIONS.md` §16 — *PRODUCTION DATABASE LAW* | `Propuesta` | **Vigente y de cumplimiento obligatorio** ✔ |
| **D-06** | Abierta | **Abierta** — sin cambios, por diseño |

> El usuario autorizó explícitamente el cierre con la expresión exacta requerida por
> [WORKFLOW.md](../project-management/WORKFLOW.md) §3, y autorizó el flujo completo: commit,
> integración en `dev`, publicación de la rama y creación del pull request
> `Task/005.3 → main`. **La fusión del PR sigue siendo responsabilidad exclusiva del
> usuario.**
