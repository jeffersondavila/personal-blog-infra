# TASK-028.2 — Reconsiderar-PostgreSQL-Produccion-RDS

| Campo | Valor |
| --- | --- |
| Identificador | `Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS` |
| Tipo / etapa | Mantenimiento de arquitectura y gobierno. **No cuenta entre las 41 tareas** y no altera el avance |
| Estado | **Aprobada** el 2026-09-27 |
| Repositorios | `personal-blog-infra`. Backend y frontend inspeccionados **sin cambios y sin rama** |
| Rama base | `main` actualizado y limpio; **nunca** `dev` |
| Fecha | 2026-09-27 |
| Ejecución | Iniciada por Codex, que agotó su límite de uso a mitad de la tarea; **continuada y cerrada por Claude Code** desde el mismo *working tree*, sin reiniciar ni crear otra rama |

## 0. Preparación Git

Rama creada **solo en infra**, desde `main` actualizado y limpio, con la secuencia de
[WORKFLOW](../project-management/WORKFLOW.md) §2.1. SHA base observado:
`2f434ed45857bb9365ae4e202144b37749eec10e`, con `HEAD == main == origin/main` al crearla.
Backend y frontend permanecieron en `main`, sin rama.

**Checkpoint recuperado al continuar (2026-09-27):** rama activa correcta;
`HEAD == main == origin/main == 2f434ed`; `dev == origin/dev == 36f7d2a`; ningún commit
de la tarea, ninguna rama remota `Task/028.2` y ningún PR. Árbol con 37 archivos
modificados y 6 nuevos, sin *staging*. Se guardó una copia íntegra del *working tree* de
Codex fuera del repositorio antes de tocar nada.

## 1. Objetivo

Sustituir formalmente el modelo PostgreSQL en VPS + PgBouncer por
**Amazon RDS for PostgreSQL privado**. Reparar en una sola tarea planificación,
arquitectura, ADR, decisiones, riesgos, `Task/029`, reparto `Task/030`–`Task/041`,
referencias cruzadas y *drift* documental, **sin crear infraestructura**.

## 2. Contexto

[ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) fue aceptada el 2026-08-15. La
premisa cambió: hay créditos AWS disponibles, la prioridad es aprender RDS, VPC, SG,
KMS, backups/PITR, CloudWatch, IAM y Terraform, y hay menos interés en operar un host
externo. El cambio se entregó como propuesta en
[ADR-010](../adr/ADR-010-production-postgresql-on-rds.md), **Aceptada** tras la aprobación
del usuario el 2026-09-27. `Task/028` y `Task/028.1` están
aprobadas, integradas y **no se reabren**.

## 3. Dentro del alcance

ADR-010 **Aceptada** y canónico RDS **Vigente**; notas de enmienda o reemplazo en ADR-003, ADR-006,
ADR-007 y ADR-008 sin reescribir su cuerpo; arquitectura, seguridad, NFR, paridad y mapeo
local/nube; decisiones D-01, D-10 a D-24; riesgos R-02, R-03, R-12, R-29 a R-44;
`Task/029` redefinida y su ficha; reparto `Task/030`–`Task/041`; STATUS, ROADMAP y fichas
de etapa; runbooks e índices; *drift* documental detectado; auditoría global de
referencias; gates locales.

**Cuatro archivos técnicos**, solo en comentarios, *docstring* o `description`, sin
cambio de comportamiento —verificado por equivalencia de AST y de HCL—: el comentario de
correspondencia y el de `DATABASE_URL` en `docker-compose.yml`, el comentario de
`TIPOS_PREVISTOS` en `scripts/laboratorio/inventario.py`, el *docstring* del test de RDS
en `tests/laboratorio/test_inventario.py` y la `description` de `bucket_de_medios` en
`terraform/variables.tf`. Este último **solo retira** la afirmación falsa «el de backups
del VPS pertenece a Task/029 y Task/030», sin añadir nada.

## 4. Fuera del alcance

Recursos AWS, Cloudflare o Grafana; secretos; `apply`, `import`, `destroy`, `-target` o
manipulación de *state*; Terraform de aplicación o de bootstrap; el proveedor OIDC, su
trust y el rol `PersonalBlogGitHubOidcValidation`; código funcional de backend o frontend;
presupuestos o plan de la cuenta; iniciar `Task/029`. Durante la validación se
excluyeron commit, push, PR y merge. La aprobación habilita exclusivamente el cierre de
WORKFLOW §3: commit, integración en `dev`, publicación y PR hacia `main`; el merge del
PR sigue siendo responsabilidad del usuario.

## 5. Entregables

[ADR-010](../adr/ADR-010-production-postgresql-on-rds.md) ·
[canónico RDS](../architecture/production-postgresql-rds.md) ·
[ficha de Task/029](TASK-029-prepare-production-postgresql-rds.md) ·
[reporte](../task-reports/TASK-028.2-report.md) ·
[auditoría de referencias](../task-reports/TASK-028.2-reference-audit.md) · enmiendas en
arquitectura, decisiones, riesgos, roadmap, etapas, runbooks e índices.

## 6. Criterios de aceptación

1. Una sola dirección **vigente**, RDS privado, con ADR-010 **Aceptada**. ADR-007 queda
   **Reemplazada** y su historia se conserva completa.
2. Ningún documento vigente instruye ejecutar el modelo VPS; D-16 a D-18 y R-41
   **cerrados por no aplicabilidad**, sin reutilizar IDs.
3. `Task/029` **Pendiente**, con ID conservado, que decide y prepara **sin provisionar** y
   sin criterios que exijan recursos futuros.
4. Owners explícitos `Task/030`–`Task/041` para *state*, red, RDS, S3, Lambda, API,
   secretos, KMS, IAM, CloudWatch, migraciones, restore, carga, roles, seguridad, DR y
   validación integral; grafo acíclico; backend de estado antes del primer `apply` de
   aplicación; **EX-028-C7 no extendida**.
5. Costos y créditos, **D-13** intacta, egress A–E sin NAT implícito, secretos y KMS,
   restore, *pooling* y Grafana coherentes. Nada de RDS Proxy, Secrets Manager,
   Multi-AZ, NAT ni IAM DB auth adoptado implícitamente.
6. 41 tareas; **28/41 ≈ 68 %**; **ETAPA 09 2/3 ≈ 67 %**; el mantenimiento no cuenta.
7. Gates locales en verde, cada uno con RC propio; auditoría global con **D = 0** real,
   no por construcción.
8. `Task/028` técnicamente intacta; cero recursos y secretos. Publicaciones de Git
   limitadas al cierre aprobado de WORKFLOW §3.

## 7. TDD / Plan test-first

**No aplica en el modo backend.** La tarea no toca `personal-blog-backend` ni su dominio,
casos de uso, API, persistencia, autenticación o auditoría, así que la
[BACKEND TESTING STRATEGY](../project-management/BACKEND_TESTING_STRATEGY.md) no la
gobierna. Los cuatro archivos técnicos solo cambian comentarios o descripciones: su
**equivalencia de comportamiento** con `main` se comprueba mecánicamente y las suites que
los cubren —laboratorio y seguridad— se ejecutan completas.

## 8. Plan de validación

Validador propio de la tarea —enlaces y anclas en los tres repositorios, UTF-8, LF, BOM
sin cambios, caracteres de control, balance de `<details>`, alcance del *diff*,
equivalencia de los archivos técnicos, tabla completa de tareas, grafo de dependencias,
decisiones y estados—; suites de laboratorio, OIDC y seguridad; coherencia S-09;
Compose; Terraform `fmt`, `init -backend=false`, `validate` y `test` con mocks; compilación
Python; actionlint; Gitleaks sobre el entregable; auditoría global por aparición; revisión
humana del *diff*.

## 9. Comandos de validación

Comandos exactos, RC y salidas en el
[reporte](../task-reports/TASK-028.2-report.md#8-gates--cada-uno-con-su-rc). Ninguno
muta AWS ni lee secretos.

## 10. Evidencia esperada

Reporte con el checkpoint recuperado, las reparaciones y su motivo, cada gate con su RC,
los contadores del validador, la clasificación de referencias y el estado Git final.

## 11. Riesgos

Riesgos del cambio reconciliados en [STATUS](../project-management/STATUS.md): R-29 a R-35
y R-38 a R-42 reconciliados tras la aprobación —R-41 cerrado por no aplicabilidad—; R-02 cubre créditos que caducan; R-12, R-36,
R-43 y R-44 cambian de owner. **Ningún riesgo se declara mitigado por documentación.**

## 12. Decisiones técnicas

ADR-010 **Aceptada** el 2026-09-27. `Task/029` conserva ID y cambia nombre y
alcance. `Task/031` conserva ID, pasa a `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch` y a
depender de `Task/030`, que corrige además una ambigüedad previa: antes podía aplicarse
antes que el backend de estado. D-22, D-23 y D-24 nuevas; D-13 sin cambios. **D-20** pasa a
«decidir e implementar» en `Task/031`, porque sin agente de host es la única vía de datos
hacia Grafana. El *backend* participa en `Task/032` **solo si** D-23 exige leer secretos
en *runtime*.

## 13. Documentación creada o actualizada

Relación completa en el [reporte §5](../task-reports/TASK-028.2-report.md#5-archivos-tocados).

## 14. Archivos modificados

Solo en `personal-blog-infra`: 6 archivos nuevos, todos Markdown, y 37 modificados —33
Markdown y los 4 técnicos de §3—. Lista exacta y `git diff --stat` en el reporte. Las
herramientas de validación viven en `tmp/task0282/`, **ignorado por Git**: no son
entregables.

## 15. Resultado de pruebas

Todos los gates en verde, cada uno con su RC. Detalle en el
[reporte §8](../task-reports/TASK-028.2-report.md#8-gates--cada-uno-con-su-rc).

## 16. Problemas encontrados

Al retomar el trabajo de Codex se encontraron y corrigieron:

1. **Compresión con pérdida de contenido vigente** en 12 documentos, entre ellos
   `target-production-architecture.md`, que pasó de 827 a 187 líneas. Se perdían reglas,
   tablas y criterios **no** ligados al VPS. Se reconstruyeron desde `main` con enmiendas
   aditivas y la historia plegada.
2. **Historia reescrita en lugar de anotada**: D-13 resuelta, R-02, R-03, owners de una
   tabla fechada, O-09 y O-10, filas de índices, guardrails de `Task/007`. Se restauró el
   texto original y se añadió la enmienda al lado.
3. **Estado transitorio versionado** —«integradas», «CI Infra SUCCESS»—, contra
   [WORKFLOW §6.1](../project-management/WORKFLOW.md). Se sustituyó por observaciones
   fechadas y verificables.
4. **El validador exigía quitar el BOM**, y por eso se habían modificado bytes de 6
   archivos fuera del alcance. Se restauró el BOM y la regla pasó a ser «sin cambios
   respecto a `main`».
5. **La auditoría clasificaba D = 0 por construcción**, no buscaba R-38 a R-42 y volcaba
   enlaces Markdown sin escapar: eso causó los 51 enlaces rotos. Se rehízo: A por
   ubicación verificable, B por marcador explícito, **revisión manual** del resto.
6. **Inventario de egress incompleto**: faltaban `PutObject`, `GetObject` y la sonda
   `ListObjectsV2`. Corregido en el canónico y en ADR-010.
7. **`terraform/variables.tf`** afirmaba en su `description` un alcance futuro de RDS en
   `Task/031`. Se redujo a retirar la afirmación falsa.

## 17. Pasos de validación para el usuario

1. Leer [ADR-010](../adr/ADR-010-production-postgresql-on-rds.md), el
   [canónico RDS](../architecture/production-postgresql-rds.md) y la
   [ficha de Task/029](TASK-029-prepare-production-postgresql-rds.md).
2. Revisar las tablas de enmienda de ETAPAS 09–12 y el mapa transversal del
   [ROADMAP](../project-management/ROADMAP.md).
3. Revisar la reconciliación de riesgos de [STATUS](../project-management/STATUS.md) y el
   índice de [decisiones](../architecture/open-decisions.md).
4. En infra: `git status --short`, `git diff --stat` y `git diff --check`.
5. Confirmar que backend y frontend siguen en `main`, limpios.

No hace falta acceso a AWS para esta revisión.

## 18. Deuda técnica pendiente

- **`images/Infraestructura.png`** muestra el modelo VPS. Solo el usuario cambia la
  imagen, así que la divergencia está declarada en
  [target-production-architecture.md](../architecture/target-production-architecture.md)
  §2, y para la capa de datos manda el texto.
- **Observación preexistente, fuera de alcance:** un *docstring* de
  `personal-blog-backend/tests/unit/test_configuracion_del_sitio_publico.py` dice que
  D-07 está «abierta hasta `Task/029`/`Task/035`», cuando D-07 es de `Task/035` desde
  `Task/005.5`. No depende de la capa de datos y el backend queda intacto por
  instrucción; se deja registrada para una tarea de mantenimiento futura.

## 19. Próxima tarea

`Task/029-Preparar-PostgreSQL-Produccion-en-RDS` — **Pendiente**. Esta tarea quedó
aprobada el 2026-09-27; como toda Task, la siguiente nace desde `main` actualizado y
normalizado. No se inicia con este cierre.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| Fecha de aprobación | **2026-09-27** |
| Aprobado por | jeffersondavila (usuario) |
| Expresión de aprobación | `approved: Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS` |

Estado: **Aprobada**. Se entregó para validación sin commit, push, PR ni merge; el cierre
aprobado sigue [WORKFLOW §3](../project-management/WORKFLOW.md). ADR-010 **Aceptada**,
ADR-007 **Reemplazada**, D-16 a D-18 y R-41 **cerrados por no aplicabilidad**. Detalle en el
[reporte §12](../task-reports/TASK-028.2-report.md#12-aprobación-y-cierre).
