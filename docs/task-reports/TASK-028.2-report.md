# TASK-028.2 — Reporte: reconsiderar PostgreSQL de producción en RDS

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS` |
| **Tipo** | Mantenimiento de arquitectura y gobierno. **No cuenta entre las 41** y no altera el avance |
| **Estado** | **Aprobada** el 2026-09-27 |
| **Fecha** | 2026-09-27 |
| **Ejecución** | Iniciada por Codex; Claude Code completó la validación y comenzó el cierre. Codex retomó el cierre aprobado desde el mismo *working tree*, sin reescribir el commit validado |
| **Avance del proyecto** | **28/41 ≈ 68 %**; **ETAPA 09 2/3 ≈ 67 %** (sin cambios) |
| **ADR-010** | **Aceptada** el 2026-09-27 (fue Propuesta durante la validación) |
| **Task/029** | **Pendiente** |
| **Ficha** | [TASK-028.2](../tasks/TASK-028.2-reconsider-production-postgresql-rds.md) |
| **Expresión de aprobación** | `approved: Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS` |

> **Registro histórico de validación:** las secciones 1–11 describen la entrega
> fijada en `6c61e8e`. Los estados posteriores a la aprobación se registran en §12.
> La auditoría enlazada en §9 conserva la evidencia de aquella entrega.

## 1. Rama y base

Rama **solo en infra**: `Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS`, creada desde
`main` actualizado y limpio, con base `2f434ed45857bb9365ae4e202144b37749eec10e`.
Backend y frontend, en `main`, **sin rama**.

*Observado el 2026-09-27, antes de editar y sin `fetch` para no alterar nada antes de
inspeccionar:*

| Repositorio | Rama activa | `HEAD` | `main` / `origin/main` | `dev` / `origin/dev` | Árbol |
| --- | --- | --- | --- | --- | --- |
| infra | `Task/028.2-…` | `2f434ed` | `2f434ed` / `2f434ed` | `36f7d2a` / `36f7d2a` | 37 modificados + 6 nuevos, sin *staging* |
| backend | `main` | `4a40364` | `4a40364` / `4a40364` | `8f0bf66` / `8f0bf66` | limpio |
| frontend | `main` | `7dce98a` | `7dce98a` / `7dce98a` | `b261e65` / `b261e65` | limpio |

Sin commits de la tarea, sin rama remota `Task/028.2` y sin PR: `gh pr list` solo muestra
hasta el #51, de `Task/028.1`. `merge-base HEAD main = 2f434ed`.

## 2. Estado inicial recuperado de Codex

Antes de tocar nada se guardó fuera del repositorio una copia íntegra del *working tree*
de Codex: el *patch* de los archivos rastreados, los 6 nuevos y `tmp/task0282/`.

Codex dejó **43 archivos** —no los 17 que llegó a reportar—: ADR-010, canónico RDS, fichas
de 028.2 y 029, reporte, auditoría, notas en ADR-003/006/007/008, arquitectura, decisiones,
riesgos, roadmap, siete fichas de etapa, cinco runbooks, índices y cuatro archivos
técnicos. La dirección técnica de ADR-010 y del canónico RDS era **correcta**: subnet
group en dos AZ incluso para Single-AZ, una subnet pública no da IP a la Lambda,
*gateway endpoint* de S3 sin tarifa, `aws:SourceVpce` frente a URLs prefirmadas, PITR a una
instancia nueva y clave KMS elegida antes de crear.

## 3. Qué dejó Codex incompleto o incorrecto

| # | Problema | Consecuencia |
| --- | --- | --- |
| 1 | **Reescritura con pérdida** de 12 documentos vigentes: `target-production-architecture.md` de 827 a 187 líneas; STAGE-10/11/12 a menos de la mitad; `local-to-cloud-mapping.md` de 206 a 73 | Desaparecían contenido **no ligado al VPS**: decisiones A–P, reglas transversales, *ownership* completo, prohibiciones, supuestos de costo, las reglas de `destroy` del emulador efímero, el checklist de migraciones de Task/038, tablas de riesgos, la regla «el emulador no decide la arquitectura de datos», la columna `Repos` del ROADMAP y notas históricas de 005.3/005.5/005.6/006.2 |
| 2 | **Historia reescrita** en lugar de anotada | D-13 resuelta, R-02, R-03, la tabla fechada del 2026-09-07, O-09/O-10, filas de índices y el guardrail de Task/007 perdían su texto aprobado |
| 3 | **Estado transitorio versionado** | «Task/028 y 028.1 integradas», «postmerge … SUCCESS» en STATUS, ROADMAP, README y en la tabla de tareas, contra WORKFLOW §6.1 |
| 4 | **El validador trataba el BOM como error** | Para pasarlo, Codex quitó el BOM de 6 archivos: bytes cambiados sin necesidad |
| 5 | **Auditoría D = 0 por construcción** | Toda aparición de VPS/PgBouncer que habría sido C pasaba a B; nunca asignaba D; no buscaba R-38 a R-42; inventario anterior a las últimas ediciones |
| 6 | **51 enlaces rotos** en la auditoría | El contexto volcaba `[texto](ruta)` sin escapar y se renderizaba como enlace relativo desde `docs/task-reports/`. Causa: **el generador**, no los documentos |
| 7 | Reporte con marcadores vacíos | Los comentarios HTML reservados para los resultados de validación y para el estado Git final seguían sin contenido |
| 8 | Ficha incoherente | Decía «Solo Markdown en infra» y excluía `.tf`, pero había cuatro archivos técnicos modificados; la misma frase de TDD, seis veces |
| 9 | Inventario de egress incompleto | Solo nombraba HEAD y borrado de S3; el código también hace `PutObject`, `GetObject` y la sonda `ListObjectsV2` |
| 10 | `terraform/variables.tf` | La `description` pasaba a afirmar alcance futuro («backups RDS y restore … Task/031») dentro de un input Terraform |
| 11 | Detalles | Guarda con repetición absurda («cuenta AWS … y cuenta/región AWS»); «EX-028-C7 fue cerrada» sin distinguir custodia de excepción; `backend` añadido a Task/032 sin condición; rename de «Decisiones no diferidas» que etiquetaba como historia decisiones vigentes; D-22 a D-24 fuera de orden y de formato |

## 4. Reparaciones realizadas

1. **Doce documentos reconstruidos desde `main`**, con la versión de Codex a mano:
   `target-production-architecture.md`, `ROADMAP.md`, STAGE-02/05/08/09/10/11/12,
   `local-to-cloud-mapping.md`, `security-boundaries.md`, `overview.md`,
   `aws-local-parity.md` y `README.md`. Método: **no se borra texto aprobado**. Se añade la
   enmienda propuesta; las secciones enteramente VPS se pliegan en un bloque «Historia», y
   las filas afectadas llevan su texto propuesto al lado. Así, el *diff* de estos archivos
   es casi solo de inserciones.
2. **Historia restaurada y anotada**: D-13, la fila de D-14, «Decisiones no diferidas»,
   R-02, R-03, R-12, R-36, R-43, R-44, O-09, O-10, `software-architecture`, `MVP_SCOPE` y
   el runbook de backups locales. Los owners nuevos van a una tabla propia de la
   reconciliación de STATUS.
3. **Estado transitorio retirado** y sustituido por entradas fechadas en orden
   cronológico, en STATUS y ROADMAP, y por una instantánea fechada en el README.
4. **BOM restaurado** en los 6 archivos. El validador pasa a exigir «BOM sin cambios
   respecto a `main`».
5. **Auditoría rehecha** —§9—: contexto escapado, R-38 a R-42 incluidos, A solo por
   ubicación verificable, B solo por marcador explícito en el mismo bloque, y **revisión
   manual** del resto.
6. **Validador corregido y endurecido**: grafo completo leído por cabecera y sin
   dependencias hacia tareas posteriores, estados exactos de ADR-010, ADR-007, Task/029 y
   028.2, ETAPA 09 2/3 y superficie de Task/028 intacta.
7. **Notas de ADR reescritas con precisión**: ADR-003 nombra las filas que cambiarían,
   incluida la inferencia «VPC ⇒ NAT»; ADR-007 separa lo que sobrevive de lo que pierde
   objeto; ADR-008 nombra K, L y G-01/04/05 y conserva Grafana.
8. **ADR-010 al formato del proyecto** —«Propuesta — pendiente de aprobación», canónico,
   decisiones que abre—, con los componentes **no adoptados**, incluidos NAT y *endpoints*,
   y la advertencia de que RDS no es serverless ni escala a cero.
9. **Ficha de Task/029** reescrita con la separación decide / prepara / puede provisionar
   —**nada**— / se valida después, y el gate económico.
10. **Nuevas secciones** donde faltaba un sustituto explícito: mapeo señal a señal del
    *baseline* Alloy a métricas nativas de RDS; reglas DB-01 a DB-10 con traslado V→DB;
    estado de cada regla G; §8.4 de paridad; filas de riesgo RDS en STAGE-10/11/12;
    D-22 a D-24 en el formato del registro.

### 4.1 Cambios de Codex revertidos o reducidos por salir del alcance

| Cambio de Codex | Decisión | Motivo |
| --- | --- | --- |
| `description` de `bucket_de_medios` en `terraform/variables.tf` | **Reducido** a retirar la afirmación VPS falsa | Introducía un alcance futuro de RDS en un input Terraform; la tarea no adelanta Task/029/031 |
| BOM retirado de 6 archivos | **Revertido** | Cambio de bytes ajeno al alcance, provocado por un validador mal planteado |
| Versiones comprimidas de 12 documentos | **Revertidas** y rehechas como enmiendas aditivas | Borraban contenido vigente e historia |
| Rename de «Decisiones no diferidas» y reescritura de filas de D-13 y D-14 | **Revertidos** | Reescribían historia; se anotan en su lugar |
| Repos de Task/032 «infra, backend» | **Condicionado** a D-23 | Hoy no hay lector de secretos; si hace falta lo decide D-23 |
| Comentarios de `docker-compose.yml`, `inventario.py` y *docstring* del test | **Conservados** | Solo retiran la afirmación VPS falsa; comportamiento idéntico, verificado |

**Qué cambió en cada archivo técnico, si hacía falta y si pertenece a la tarea:**

| Archivo | Qué cambió | ¿Necesario para dejar el VPS? | ¿Contrato o implementación? | ¿Cambia comportamiento? | ¿De Task/028.2? |
| --- | --- | --- | --- | --- | --- |
| `docker-compose.yml` | Dos comentarios: «PostgreSQL en VPS, tras PgBouncer» → «RDS privado propuesto»; «Docker, un VPS o PgBouncer» → «Docker o RDS» | Sí: el comentario afirmaba el destino VPS | Descripción | **No**: `docker compose config` idéntico y validado | Sí |
| `scripts/laboratorio/inventario.py` | Comentario de `TIPOS_PREVISTOS`: «ADR-007 sitúa PostgreSQL en un VPS» → «el grafo de Task/025 no incluye RDS; hasta implementarlo, la guarda sigue rechazando RDS» | Sí | Descripción | **No**: AST sin *docstrings* idéntico; la lista cerrada y el rechazo de `aws_db_*`/`aws_rds_*` no cambian | Sí |
| `tests/laboratorio/test_inventario.py` | *Docstring* del test de RDS | Sí | Descripción | **No**: AST idéntico; el test sigue exigiendo el rechazo | Sí |
| `terraform/variables.tf` | Se **elimina** «y el de backups del VPS pertenece a Task/029 y Task/030» de la `description` | Sí: era falso con RDS | Descripción; **sin** afirmación nueva | **No**: la `description` no entra en plan ni *state*; HCL idéntico fuera de ella; `validate` en verde | Sí, reducido |

## 5. Archivos tocados

Solo en `personal-blog-infra`.

**Nuevos (6):** `docs/adr/ADR-010-production-postgresql-on-rds.md` ·
`docs/architecture/production-postgresql-rds.md` ·
`docs/tasks/TASK-028.2-reconsider-production-postgresql-rds.md` ·
`docs/tasks/TASK-029-prepare-production-postgresql-rds.md` ·
`docs/task-reports/TASK-028.2-report.md` · `docs/task-reports/TASK-028.2-reference-audit.md`.

**Modificados (37):** `README.md` · `docker-compose.yml` · ADR-003, ADR-006, ADR-007 y
ADR-008 · `aws-local-parity.md`, `local-to-cloud-mapping.md`,
`non-functional-requirements.md`, `open-decisions.md`, `overview.md`,
`production-postgresql-vps.md`, `security-boundaries.md`, `software-architecture.md` y
`target-production-architecture.md` · `docs/claude/PROJECT_INSTRUCTIONS.md` ·
`docs/product/MVP_SCOPE.md` · `ROADMAP.md` y `STATUS.md` · `docs/runbooks/README.md`, los
cinco `deployment-*.md` y `local-backup-and-recovery.md` · STAGE-02, 05, 08, 09, 10, 11 y
12 · `docs/task-reports/README.md` · `scripts/laboratorio/inventario.py` ·
`terraform/variables.tf` · `tests/laboratorio/test_inventario.py`.

`git diff --stat` final:

```text
 README.md                                          | 102 ++--
 docker-compose.yml                                 |   4 +-
 docs/adr/ADR-003-serverless-low-cost-cloud.md      |  25 +
 docs/adr/ADR-006-local-aws-parity-with-floci.md    |   9 +
 docs/adr/ADR-007-production-postgresql-on-vps.md   |  18 +
 ...DR-008-observability-grafana-cloud-and-alloy.md |  13 +
 docs/architecture/aws-local-parity.md              |  69 ++-
 docs/architecture/local-to-cloud-mapping.md        |  75 ++-
 docs/architecture/non-functional-requirements.md   |  18 +-
 docs/architecture/open-decisions.md                | 232 ++++++++-
 docs/architecture/overview.md                      |  68 ++-
 docs/architecture/production-postgresql-vps.md     |  11 +
 docs/architecture/security-boundaries.md           | 150 +++++-
 docs/architecture/software-architecture.md         |   2 +-
 .../architecture/target-production-architecture.md | 526 ++++++++++++++++++---
 docs/claude/PROJECT_INSTRUCTIONS.md                |  74 ++-
 docs/product/MVP_SCOPE.md                          |   3 +
 docs/project-management/ROADMAP.md                 | 141 +++++-
 docs/project-management/STATUS.md                  | 104 +++-
 docs/runbooks/README.md                            |   6 +
 docs/runbooks/deployment-create.md                 |   9 +
 docs/runbooks/deployment-destroy.md                |   9 +
 docs/runbooks/deployment-recovery.md               |   9 +
 docs/runbooks/deployment-rollback.md               |   9 +
 docs/runbooks/deployment-validate.md               |   9 +
 docs/runbooks/local-backup-and-recovery.md         |   1 +
 docs/stages/STAGE-02-application-foundations.md    |   6 +
 docs/stages/STAGE-05-quality-security.md           |  11 +-
 docs/stages/STAGE-08-cloud-ready.md                |   5 +
 docs/stages/STAGE-09-cloud-accounts.md             |  90 +++-
 docs/stages/STAGE-10-cloud-deployment.md           |  70 ++-
 docs/stages/STAGE-11-deployment-automation.md      |  29 ++
 docs/stages/STAGE-12-launch-and-operations.md      |  42 ++
 docs/task-reports/README.md                        |   6 +
 scripts/laboratorio/inventario.py                  |   3 +-
 terraform/variables.tf                             |   2 +-
 tests/laboratorio/test_inventario.py               |   2 +-
 37 files changed, 1733 insertions(+), 229 deletions(-)
```

Herramientas de validación en `tmp/task0282/` —ignorado por Git (`.gitignore`: `tmp/`)—:
`validate.py`, `audit_references.py`, `build_manual_review.py` y los scripts de edición de
Codex. **No son entregables** y no entran en el alcance versionado.

## 6. Propuesta arquitectónica

**ADR-010 (Propuesta — pendiente de aprobación).** Amazon RDS for PostgreSQL **privado**;
Lambda conectada a la VPC; subnets privadas, DB subnet group y security groups
restrictivos; TLS verificado, cifrado en reposo, identidades SQL mínimas, backups y
restore demostrado. Reemplazaría a ADR-007 y modificaría parcialmente ADR-003 y ADR-008;
conserva ADR-006. Motivo: créditos AWS y prioridad de aprendizaje; ADR-007 **no** se
califica de error. **No adopta** Aurora, RDS Proxy, Multi-AZ, IAM DB auth, Secrets Manager,
NAT ni *endpoints* concretos. RDS **no** es serverless ni escala a cero.

**ADR-007.** Sigue **Aceptada** hasta la aprobación, con el cuerpo **intacto**, verificado
por el validador. Una nota superior explica el reemplazo propuesto, qué sobrevive
—`DATABASE_URL`, base de datos nunca pública, TLS verificado, restore probado— y qué pierde
objeto: host, SSH, PgBouncer, D-16 a D-18 y backups desde el host.

**ADR-003.** Cuerpo intacto. La nota nombra las filas que cambiarían: «Base de datos»
vuelve a administrada —RDS—; la alternativa «Lambda dentro de VPC» pasa a ser la propuesta
**sin NAT**, porque **VPC no implica NAT**; consecuencias de costo fijo, incluidos los
*interface endpoints*. **NAT Gateway sigue excluido.**

**ADR-008.** Cuerpo intacto. Pierden objeto **solo** K —Alloy—, su credencial de host y
G-01/04/05. **Grafana Cloud se conserva** como plano central, junto con CloudWatch mínimo
(I), la privacidad y el control de costo. D-20 pasa a decidirse **e implementarse** en
Task/031.

**Lambda / VPC / egress.** Inventario A–E sobre el código real, en el canónico §2:

- **A** — PostgreSQL dentro de la VPC.
- **B** — S3 (`PutObject`, `GetObject`, `HeadObject`, `DeleteObject` y `ListObjectsV2`;
  firmar URLs es local) por *gateway endpoint* candidato, y SSM por *interface endpoint*
  solo si se lee en *runtime*, que hoy no ocurre.
- **C** — logs de Lambda, credenciales del rol y operaciones administradas, sin *endpoint*
  de aplicación.
- **D** — ninguna API externa.
- **E** — Cloudflare, Grafana y el emulador no son destinos del *runtime*.

**RDS no requiere NAT**; el candidato sin NAT es viable y se prueba en Task/032.

**Secretos / SSM / KMS.** SSM `SecureString` sigue siendo la base. D-23 compara Secrets
Manager por rotación, RDS Proxy y precio, **sin adoptarlo**. La *master* queda fuera del
runtime. KMS tiene dos usos —la instancia y los secretos—, y la clave de la instancia se
elige antes de crearla. `sensitive` no saca un valor del *state*.

**Backups / PITR / restore.** D-10 en Task/029: backups automáticos, PITR, snapshots,
retención, RPO/RTO, *deletion protection* y snapshot final. **Restore sintético y PITR**
demostrados en Task/031, backup previo a las primeras migraciones en Task/036, y **restore
reciente con esquema real** en Task/040. Un backup administrado o una instancia
`available` no son evidencia.

***Pooling* / RDS Proxy.** Pool por proceso —hoy 5 + 5 en local— derivado en Task/029
(D-12), medido en Task/032 y probado bajo carga en Task/040. RDS Proxy solo con evidencia
de carga, *pinning*, autenticación y precio. PgBouncer no se instala por inercia.

**Observabilidad.** CloudWatch mínimo con señales de RDS, Lambda y API. Cada señal del
antiguo *baseline* Alloy tiene equivalente nativo (arquitectura objetivo §11). Grafana
recibe datos solo por D-20, con un principal dedicado de solo lectura. D-19 se verifica
antes de integrar.

**Costos y créditos.** **D-13 intacta**: USD 5/mes AWS y USD 20/mes global. Task/029
separa costo bruto, crédito elegible consumido, desembolso, vencimiento y escenario
poscrédito. Si no cabe, hace falta una **decisión explícita** antes del primer `apply` de
aplicación. Detener RDS no lo deja en costo cero.

## 7. Task/029, reparto 030–041, decisiones y riesgos

**Task/029-Preparar-PostgreSQL-Produccion-en-RDS — Pendiente.** Depende de 027 y 028, y
requiere 028.2 aprobada.

- **Decide:** D-22, D-23, D-24, D-10 y si se evalúa RDS Proxy.
- **Prepara:** egress A–E, D-12 preliminar, costo y créditos frente a D-13, contratos,
  planes de prueba, runbooks, y el diseño de R-12, R-43 y R-44.
- **Puede provisionar:** **nada**, porque el backend D-06 es de Task/030 y EX-028-C7 no se
  extiende.
- **Se valida después:** en 031, 032, 036, 038, 040 y 041.

| Task | Depende de | Entrega |
| --- | --- | --- |
| 030 | 029 | Backend de estado D-06 —bootstrap separado, migración del *state* OIDC y extinción de EX-028-C7— antes de cualquier `apply` de aplicación; S3 de medios y D-08 |
| 031 | **030** *(antes 029)* | Red, RDS, KMS, SSM, CloudWatch (D-11), D-20 implementada, acceso privado D-24, restore sintético y PITR, runbooks y guardas. Renombrada `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch` |
| 032 | 030, 031 | Lambda en VPC, TLS, secretos (D-23), pool y límites medidos (D-12), egress real sin NAT |
| 033–035 | cadena | API Gateway con logs D-11 · Pages · DNS, D-07 y D-15 |
| 036 | 035 | Primeras migraciones por D-24 con backup previo; R-43 y R-44 |
| 037–039 | 036 / 037+038 | CI frontend · backend y canal de migraciones sobre D-24 · Terraform para AWS y Cloudflare con red y RDS en guardas y borrado protegido |
| 040 | 039 | Validación integral: negativos de red, SG, IAM y TLS; carga y conexiones; restore reciente y RPO/RTO; DR; alertas |
| 041 | 040 | Costo real bruto frente a crédito, vencimiento y poscrédito; D-19 |

Grafo verificado: **15 nodos (027–041), sin ciclos**, ninguna dependencia hacia una tarea
posterior y **41 tareas**.

**Decisiones:**

| ID | Estado |
| --- | --- |
| D-01 | Resuelta históricamente; sustitución propuesta |
| D-10, D-11, D-12, D-19, D-20 | Abiertas con owners propuestos: 029/031/040 · 031 · 029→032 · 029/031/041 · 031 decide e implementa |
| D-13 | **Resuelta intacta**, con nota de créditos |
| D-16, D-17, D-18 | Abiertas, con **cierre por no aplicabilidad propuesto** y texto conservado |
| D-22, D-23, D-24 | **Nuevas propuestas** |

Registro: **24 IDs, 14 abiertas y 10 resueltas**.

**Riesgos:**

- R-29, R-30, R-32, R-34, R-35, R-39, R-40 y R-42 **reformulados**.
- R-31, R-33 y R-38 **se mantienen**.
- R-41 con **cierre N/A propuesto**.
- R-02 cubre créditos que caducan; R-03 sin PgBouncer.
- R-12, R-36, R-43 y R-44 cambian de owner.
- **No se crean IDs**: exposición y SG → R-30; capacidad → R-32; borrado, migraciones y
  KMS → R-35.
- Recuento sin cambios: **48 abiertos**.

## 8. Gates — cada uno con su RC

Cada gate se ejecutó **por separado**, con su RC. Herramientas: Terraform **1.16.2**, del
lanzador fijado del proyecto; actionlint **1.7.12**, zip `6e7241b5…f6e9` y ejecutable
idéntico al del zip; Gitleaks **8.30.1**, zip `d29144de…fc4e` y ejecutable idéntico.

| # | Gate | Comando | RC | Resultado |
| --- | --- | --- | --- | --- |
| 1 | Espacios y conflictos | `git diff --check` | 0 | Sin salida |
| 2 | Workflows | `actionlint ci-infra.yml verify-aws-oidc.yml` | 0 | Sin hallazgos |
| 3 | Laboratorio | `python -B -m unittest discover -s tests/laboratorio -p 'test_*.py'` | 0 | **176 tests OK** |
| 4 | OIDC | `python -B -m unittest discover -s tests/oidc` | 0 | **60 tests OK**, 1 omitido |
| 5 | Seguridad | `python -B -m unittest discover -s tests/security -p 'test_*.py'` | 0 | **88 tests OK** |
| 6 | Coherencia S-09 | `vulnerability_gate.py --baseline security/vulnerability-baseline.json --comprobar-coherencia .` | 0 | **CORRECTO** |
| 7a | Compose | `docker compose --env-file .env.example --profile admin config --quiet` | 0 | 7 servicios |
| 7b | Compose del laboratorio | `docker compose --file laboratorio/docker-compose.laboratorio.yml --env-file laboratorio/.env.laboratorio.example config --quiet` | 0 | Válido |
| 7c | Variables del Compose | Paso «Compose declares every variable it uses» del CI | 0 | 26 usadas, ninguna sin declarar |
| 8 | Formato Terraform | `terraform fmt -check -recursive` en `terraform/` y en `bootstrap/github-oidc/` | 0 / 0 | Sin cambios |
| 9 | Terraform de aplicación | `init -backend=false -input=false -lockfile=readonly` · `validate` | 0 · 0 | Lock sin cambios; configuración válida |
| 10 | Terraform de bootstrap | `init -backend=false -lockfile=readonly` · `validate` · `test` | 0 · 0 · 0 | Lock sin cambios; **9 passed / 0 failed**, con mocks. **Sin *state*, sin `apply`** |
| 11 | Compilación Python | `compile()` de `scripts/` y `tests/`, como el CI | 0 | 37 archivos, 0 fallos |
| 12–14 | CRLF, caracteres de control, BOM y enlaces | Validador de la tarea | 0 | Sin errores; 1820 enlaces en 166 Markdown |
| 15 | Secretos | `gitleaks dir <entregable de git ls-files> --redact=100 --no-banner`, con `.gitleaks.toml` | 0 | **Sin hallazgos** en 260 archivos (5,49 MB). **Control positivo**: el mismo valor `go.sum` en otro archivo **sí** se detecta (RC 1). Con ruta absoluta aparecen los 5 `go.sum` conocidos del parche de MinIO, porque la exención de `.gitleaks.toml` está anclada a rutas relativas; el CI escanea `.` desde la raíz |
| 16 | Validador Task/028.2 | `python -B tmp/task0282/validate.py` | 0 | Contadores en §9 |
| 17 | Auditoría de referencias | `python -B tmp/task0282/audit_references.py` | 0 | **D = 0**, REVISAR = 0 |

**Mensaje `usage: laboratorio [-h] --modo MODO … error: the following arguments are
required: --modo`.** Aparece en el *stderr* del gate 3 y **no es un fallo**. Lo emite
argparse durante `SeleccionExplicitaDelDestinoTests.test_el_modo_no_tiene_valor_por_omision`
(`tests/laboratorio/test_lanzador.py`), una prueba negativa de **R-24** que exige
`SystemExit` cuando falta `--modo`. Ejecutada aislada: el mismo mensaje, `ok`. La suite
termina `Ran 176 tests … OK`, RC 0. En la ejecución de Codex quedó mezclado con otros
comandos encadenados; aquí cada gate tiene su RC propio.

**No aplica:** `terraform test` en la raíz de aplicación, porque no tiene `*.tftest.hcl`.
Tampoco se ejecutaron el build ni el escaneo de imágenes S-09: esta tarea no toca
imágenes, Dockerfiles ni el baseline.

## 9. Validador y auditoría

**Validador** (`tmp/task0282/validate.py`), RC 0:

```text
task028_surface_touched: 0
changed_markdown: 39
changed_documentation_comments: 4
behavior_equivalence_checks: 4
markdown_files: 166
local_links: 1820
task_ids: 41
approved: 28
pending: 13
decision_ids: 24
future_nodes: 15
cycles: 0
preserved_historical_bodies: 5
```

**Auditoría de referencias**, en
[TASK-028.2-reference-audit.md](TASK-028.2-reference-audit.md): 2162
apariciones —A=1490, B=585, C=86, D=0, O=1, N=0; 156 revisadas a mano, 0 sin revisar—, **D = 0 tras revisión manual, no por construcción**.

- **A** solo por ubicación verificable.
- **B** solo por marcador explícito en el mismo bloque.
- Lo demás, por revisión manual.

Una **O** es la observación preexistente del *docstring* del backend sobre D-07 (ficha
§18). Lo que la auditoría encontró en documentos vigentes que afirmaba el modelo VPS
**sin** enmienda se corrigió en la fuente antes de cerrar.

## 10. Estado Git final

```text
 M README.md
 M docker-compose.yml
 M docs/adr/ADR-003-serverless-low-cost-cloud.md
 M docs/adr/ADR-006-local-aws-parity-with-floci.md
 M docs/adr/ADR-007-production-postgresql-on-vps.md
 M docs/adr/ADR-008-observability-grafana-cloud-and-alloy.md
 M docs/architecture/aws-local-parity.md
 M docs/architecture/local-to-cloud-mapping.md
 M docs/architecture/non-functional-requirements.md
 M docs/architecture/open-decisions.md
 M docs/architecture/overview.md
 M docs/architecture/production-postgresql-vps.md
 M docs/architecture/security-boundaries.md
 M docs/architecture/software-architecture.md
 M docs/architecture/target-production-architecture.md
 M docs/claude/PROJECT_INSTRUCTIONS.md
 M docs/product/MVP_SCOPE.md
 M docs/project-management/ROADMAP.md
 M docs/project-management/STATUS.md
 M docs/runbooks/README.md
 M docs/runbooks/deployment-create.md
 M docs/runbooks/deployment-destroy.md
 M docs/runbooks/deployment-recovery.md
 M docs/runbooks/deployment-rollback.md
 M docs/runbooks/deployment-validate.md
 M docs/runbooks/local-backup-and-recovery.md
 M docs/stages/STAGE-02-application-foundations.md
 M docs/stages/STAGE-05-quality-security.md
 M docs/stages/STAGE-08-cloud-ready.md
 M docs/stages/STAGE-09-cloud-accounts.md
 M docs/stages/STAGE-10-cloud-deployment.md
 M docs/stages/STAGE-11-deployment-automation.md
 M docs/stages/STAGE-12-launch-and-operations.md
 M docs/task-reports/README.md
 M scripts/laboratorio/inventario.py
 M terraform/variables.tf
 M tests/laboratorio/test_inventario.py
?? docs/adr/ADR-010-production-postgresql-on-rds.md
?? docs/architecture/production-postgresql-rds.md
?? docs/task-reports/TASK-028.2-reference-audit.md
?? docs/task-reports/TASK-028.2-report.md
?? docs/tasks/TASK-028.2-reconsider-production-postgresql-rds.md
?? docs/tasks/TASK-029-prepare-production-postgresql-rds.md
```

- **`main`**: `2f434ed` = `origin/main`, **intacto**.
- **`dev`**: `36f7d2a` = `origin/dev`, **intacto**.
- **Backend y frontend**: en `main`, limpios, sin rama.
- **Sin *staging***, sin commit, sin push, sin PR y sin merge.

## 11. Límites y aprobación

**Ningún recurso** AWS, Cloudflare ni Grafana creado o modificado; **cero** `apply`,
`import`, `destroy` o `-target`; **ningún** *state* tocado; **cero** secretos creados o
leídos. El proveedor OIDC, su trust y `PersonalBlogGitHubOidcValidation`, **intactos**:
ningún archivo de `bootstrap/`, `.github/`, `scripts/oidc/` ni `tests/oidc/` cambió.
`Task/029` **no se inició**. Este reporte **no es una aprobación**.

**`Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS` — Lista para validación.**

## 12. Aprobación y cierre

**APROBADA** el 2026-09-27 por el usuario mediante
`approved: Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS`.

Las secciones 1 a 11 son el registro de lo que se entregó para validación: el contenido
exacto que se aprobó quedó fijado en el commit `6c61e8e`, antes de promover nada. El
cierre, en un commit aparte, registra la aprobación y promueve:

| Elemento | Antes | Después |
| --- | --- | --- |
| ADR-010 | Propuesta — pendiente de aprobación | **Aceptada** ✔ |
| ADR-007 | Aceptada | **Reemplazada** por ADR-010; cuerpo intacto como historia |
| ADR-003 y ADR-008 | Aceptadas | Aceptadas, **modificadas parcialmente** por ADR-010 (fila «Modificado parcialmente por» y nota de vigencia) |
| ADR-006 | Aceptada | Sin cambios; nota de aplicación futura |
| `production-postgresql-rds.md` | Propuesta | **Vigente** |
| `production-postgresql-vps.md` | Vigente | **Histórico**, reemplazado |
| D-16, D-17, D-18 | Abiertas, cierre N/A propuesto | **Cerradas por no aplicabilidad** |
| D-22, D-23, D-24 | Propuestas | **Abiertas**, owner `Task/029` |
| R-41 | Abierto, cierre N/A propuesto | **Cerrado por no aplicabilidad**; riesgos abiertos 48 → **47** |
| R-29 a R-40 y R-42 | Reformulación propuesta | **Reformulados**, abiertos |
| Enmiendas en arquitectura, roadmap, etapas, runbooks, NFR y README | Propuestas | **Vigentes**; la historia VPS sigue plegada |
| `Task/029` | Pendiente | **Pendiente** —no se inicia— |

Registro de decisiones tras el cierre: **24 IDs — 11 abiertas, 10 resueltas y 3 cerradas
por no aplicabilidad**. **D-13 no cambia.** El avance no cambia: **28/41 ≈ 68 %**, ETAPA 09
**2/3 ≈ 67 %**.

**La aprobación no crea recursos.** Cada recurso de ADR-010 exige su tarea propietaria y
la autorización explícita del usuario. Nada se aplicó en AWS durante el cierre.

### 12.1 Validación posterior a la aprobación

Los validadores temporales se adaptaron a los estados aprobados, conservando las
comprobaciones de alcance, codificación, enlaces, grafo e historia. La comparación
técnica usa la base original `2f434ed`; los cuerpos históricos de los cinco documentos
anteriores se comparan desde su primera sección. Las secciones 1–11 de este reporte y
la auditoría histórica se comprobaron contra `6c61e8e` sin alterar su evidencia.

La revisión de marcadores separó historia, reglas generales y condiciones técnicas de
los estados activos de este cierre. Se corrigieron el mapeo local/nube, la fecha de las
reglas de seguridad, los criterios añadidos de ETAPAS 11–12 y las fichas. Se conservaron
las entradas fechadas de validación, los estados de otras decisiones y los condicionales
de funcionalidades futuras. El inventario por aparición queda en la herramienta
temporal `tmp/task0282/marker-review.json`.

| Gate posterior a la promoción | RC | Resultado |
| --- | --- | --- |
| `git diff --check` | 0 | Sin errores de espacios |
| `python -B tmp/task0282/validate.py` | 0 | 41 tareas: 28 aprobadas, 13 pendientes; ETAPA 09 2/3; 15 nodos futuros, 0 ciclos; 24 decisiones: 11 abiertas, 10 resueltas y 3 N/A; 47 riesgos abiertos; equivalencia de los cuatro archivos técnicos; superficie OIDC intacta |
| Enlaces, anclas y codificación — mismo validador | 0 | 1842 enlaces locales en 166 Markdown; 0 rotos; UTF-8, LF, BOM y bloques históricos conservados |
| `python -B tmp/task0282/audit_references.py` | 0 | 2211 apariciones: A=1562, B=527, C=121, D=0, O=1, N=0; 179 con revisión manual; 0 sin revisar. Salida posterior en `tmp/task0282/reference-audit-post-approval.md`; auditoría histórica versionada intacta |
| Laboratorio — `python -B -m unittest discover -s tests/laboratorio -p 'test_*.py'` | 0 | 176 tests OK en la repetición completa; incidencia inicial detallada abajo |
| OIDC — `python -B -m unittest discover -s tests/oidc` | 0 | 60 tests, 1 omitido, OK |
| Seguridad — `python -B -m unittest discover -s tests/security -p 'test_*.py'` | 0 | 88 tests OK |
| S-09 — `python -B scripts/security/vulnerability_gate.py --baseline security/vulnerability-baseline.json --comprobar-coherencia .` | 0 | CORRECTO |
| Python — `compile()` sobre `scripts/` y `tests/` | 0 | 37 archivos; sin escribir bytecode |
| Compose — `docker compose --env-file .env.example --profile admin config --quiet` | 0 | Válido |
| Compose laboratorio — `docker compose --file laboratorio/docker-compose.laboratorio.yml --env-file laboratorio/.env.laboratorio.example config --quiet` | 0 | Válido |
| Terraform `fmt -check -recursive`, aplicación / bootstrap | 0 / 0 | Sin cambios |
| Terraform `init -backend=false -input=false -lockfile=readonly`, aplicación / bootstrap | 0 / 0 | Sin configurar backend; locks intactos |
| Terraform `validate`, aplicación / bootstrap | 0 / 0 | Configuraciones válidas |
| Terraform `test`, bootstrap | 0 | 9 passed / 0 failed, proveedores simulados, todos los casos con `command = plan`; sin operación AWS ni modificación del estado real |
| actionlint, ambos workflows | 0 | Sin hallazgos |
| Gitleaks sobre copia de los archivos versionados del entregable, rutas relativas y `--redact=100` | 0 | 0 hallazgos |

**Incidencia conservada:** la primera ejecución del laboratorio terminó con RC 1:
`test_http_200_y_seis_servicios_running` recibió RC 3328 del proceso Bash. El diagnóstico
aislado del mismo caso devolvió RC 0 y stderr vacío; la repetición de la suite completa
dio 176 tests OK, RC 0. No se reprodujo la causa; no se cambió la sonda ni el test.
La primera auditoría posterior detectó 65 apariciones sin revisión manual (RC 1);
se revisaron sus 55 líneas en contexto y se registraron las clasificaciones explícitas.

### 12.2 Flujo de cierre autorizado

Flujo de cierre de
[WORKFLOW §3](../project-management/WORKFLOW.md): commit en la rama Task, integración
`--no-ff` en `dev`, publicación de `dev` y de la rama Task, y PR `Task/028.2 → main`, que
**solo el usuario fusiona**. El estado de ramas y PR se consulta en Git y GitHub
([WORKFLOW §6.1](../project-management/WORKFLOW.md)).

**`Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS` — Aprobada el 2026-09-27.**
