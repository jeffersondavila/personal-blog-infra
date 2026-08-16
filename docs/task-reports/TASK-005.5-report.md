# Reporte — TASK-005.5 · Alinear la planificación tras la auditoría global

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.5-Alinear-Planificacion-Tras-Auditoria` |
| **Tipo** | **Mantenimiento** de gobierno, planificación y arquitectura documental |
| **Estado final** | **Aprobada** ✔ el 2026-08-16 por jeffersondavila |
| **Expresión de aprobación** | `approved: Task/005.5-Alinear-Planificacion-Tras-Auditoria` |
| **Fecha** | 2026-08-16 |
| **Repositorios** | `personal-blog-infra`, `personal-blog-backend`, `personal-blog-frontend` |
| **Rama** | `Task/005.5-Alinear-Planificacion-Tras-Auditoria` en los tres, **desde `main`** |
| **Roadmap** | **No cuenta** en las 41 tareas. Avance **5/41 (12 %)** y ETAPA 02 **1/3** sin cambios |
| **Ficha** | [TASK-005.5](../tasks/TASK-005.5-align-planning-after-audit.md) |

---

## 1. Qué se pidió y qué se hizo

Dos auditorías independientes concluyeron que la arquitectura es viable y que **no hay que
replantearla**, pero señalaron inconsistencias de planificación, *ownership* y secuencia.

El encargo explícito **no era aplicar los hallazgos**, sino someterlos a verificación:

```
HALLAZGO → REPRODUCIR EVIDENCIA → ENTENDER INTENCIÓN → CONTRASTAR CON FUENTE CANÓNICA
        → DECIDIR → CORREGIR SOLO SI SE JUSTIFICA → REVALIDAR TRANSVERSALMENTE
```

Ese ciclo se aplicó a cada hallazgo. **Dos no se reprodujeron** y se rechazan con evidencia.

---

## 2. Estado inicial verificado

Antes de crear ninguna rama, en los tres repositorios: `fetch --prune`, `switch main`,
`pull --ff-only`.

| Repositorio | `main` | `origin/main` | *Working tree* | Rama creada | SHA base | `HEAD == main` |
| --- | --- | --- | --- | --- | --- | --- |
| `personal-blog-infra` | `cc90b96` | `cc90b96` ✔ | limpio | `Task/005.5-…` | **`cc90b96`** | ✔ |
| `personal-blog-backend` | `db6ab18` | `db6ab18` ✔ | limpio | `Task/005.5-…` | **`db6ab18`** | ✔ |
| `personal-blog-frontend` | `144a401` | `144a401` ✔ | limpio | `Task/005.5-…` | **`144a401`** | ✔ |

**Hallazgo del propio arranque.** El `--prune` eliminó
`origin/Task/005.4-Corregir-Base-Ramas-Task-Main`, y `gh pr view 10` devolvió:

```
state: MERGED · mergedAt: 2026-08-16T04:20:19Z · mergeCommit: cc90b96
```

`git diff main dev` **vacío** y `main` **ancestro de `dev`** (`f2eb330`).
`git ls-remote --heads origin "Task/*"` **no devuelve nada**.

> Es decir: el PR de `Task/005.4` **ya estaba fusionado y normalizado**, mientras la
> documentación vigente seguía describiéndolo como abierto y a `Task/006` como bloqueada
> por él. Ese fue el primer *drift* confirmado, y con evidencia de Git y de GitHub.

---

## 3. Matriz de hallazgos

**Veredictos:** `CORREGIR AHORA` · `REASIGNAR` (a una tarea futura) · `ACLARAR` (documentar
sin decidir aún) · `RECHAZADO` (el hallazgo no se sostiene).

### 3.1 Workflow

| ID | Hallazgo de la auditoría | Evidencia reproducida | Veredicto | Acción | Archivos |
| --- | --- | --- | --- | --- | --- |
| **AUD-FIX-001** | Backend y frontend siguen ordenando crear ramas Task **desde `dev`** | **6 apariciones vigentes**: `backend/CONTRIBUTING.md:26,42` · `backend/README.md:225` · `frontend/CONTRIBUTING.md:26,42` · `frontend/README.md:60`. No son históricas: son **instrucciones operativas** en presente | **CORREGIR AHORA** | Regla reescrita a `main`, con el invariante y enlace a WORKFLOW §2.1 | 4 archivos en backend y frontend |
| **AUD-FIX-002** | `CLAUDE.md` raíz podría ser incoherente | `CLAUDE.md:5-9` ya declara el invariante correctamente | **RECHAZADO** | **Ninguna.** No se toca por estética | — |

> **Por qué existía AUD-FIX-001.** `Task/005.4` corrigió el invariante **solo en
> `personal-blog-infra`** y en el `CLAUDE.md` raíz. Su propio reporte lo dice: los
> repositorios afectados fueron «`personal-blog-infra` únicamente, más el `CLAUDE.md`
> raíz». La regla antigua sobrevivió intacta en los otros dos.

### 3.2 *Drift* documental posterior a 005.2 / 005.3 / 005.4

| ID | Hallazgo | Evidencia reproducida | Veredicto | Acción |
| --- | --- | --- | --- | --- |
| **AUD-FIX-003** | ADR-006 aparece como `Propuesta` | `STAGE-08-cloud-ready.md:18` | **CORREGIR AHORA** | → **Aceptada** ✔ (2026-08-15) |
| **AUD-FIX-004** | ADR-007 aparece como `Propuesta` | `STATUS.md:666` y `local-to-cloud-mapping.md:3-4` | **CORREGIR AHORA** | → **Aceptada** / **Vigente** |
| **AUD-FIX-005** | **D-01 figura abierta** | **No se reproduce.** `open-decisions.md` la marca `Resuelta` con la distinción modelo/proveedor bien hecha | **RECHAZADO** *(parcial)* | El error real era otro: el **conteo** en `overview.md:188` decía «12 abiertas». Eso sí se corrigió |
| **AUD-FIX-006** | Conteo de decisiones incorrecto | `overview.md:188` «12» frente a **11** reales | **CORREGIR AHORA** | Recalculado a **13** tras añadir D-15 y D-16 |
| **AUD-FIX-007** | PR de `Task/005.4` descrito como abierto | `STATUS.md:15,127,434` y `STAGE-02:53` | **CORREGIR AHORA** | Registrado **fusionado** (`#10`, `cc90b96`) y normalizado |
| **AUD-FIX-008** | `Task/006` bloqueada por un PR ya fusionado | `STATUS.md:17,626-629` | **CORREGIR AHORA** | Bloqueo eliminado; sigue **Pendiente** por no estar aprobada `Task/005.5` |
| **AUD-FIX-009** | PR de `Task/005` descrito como abierto | `STAGE-02:53-56` — fusionados el 2026-08-13 | **CORREGIR AHORA** | Corregido |
| **AUD-FIX-010** | README con estado antiguo y backend «inexistente» | `infra/README.md:36-40,47`: «última tarea aprobada `Task/004`», «4 de 41 (10 %)», «Backend: **No ha comenzado**» — con `Task/005` aprobada y código real en el repositorio | **CORREGIR AHORA** | Estado, avance y tabla de implementación actualizados |
| **AUD-FIX-011** | Frontend README con ramas obsoletas | `frontend/README.md:34,37,65-66`: rama `Task/001` inexistente y «`main` contiene únicamente el commit inicial vacío» | **CORREGIR AHORA** | Corregido |

### 3.3 `Infraestructura.png`

| ID | Hallazgo | Evidencia reproducida | Veredicto | Acción |
| --- | --- | --- | --- | --- |
| **AUD-FIX-012** | El PNG se trata como autoridad canónica de producción | **Contradicción interna en `aws-local-parity.md`**: §3.3 lo declaraba *«la representación canónica»* del Modo C, y **nueve líneas después** dibujaba un Mermaid con PgBouncer y VPS —ADR-007—. También §2 y las referencias | **CORREGIR AHORA** | El diagrama Mermaid pasa a ser la representación canónica vigente; el PNG queda como **registro histórico** explícito |

> **El archivo no se tocó.** `git status --porcelain -- images/` **vacío**. No se modificó,
> no se regeneró, no se movió y no se borró. `overview.md`,
> `production-postgresql-vps.md` y `infra/README.md` **ya lo trataban correctamente**: el
> defecto estaba localizado en `aws-local-parity.md`.

### 3.4 Secuencia y dependencias invertidas

| ID | Hallazgo | Evidencia reproducida | Veredicto | Acción |
| --- | --- | --- | --- | --- |
| **AUD-FIX-013** | `Task/025` depende solo de `Task/022` pese a exigir Lambda real | `STAGE-08:75` y `ROADMAP:222`. Sus criterios exigen `apply` sobre **Lambda y API Gateway v2**, que necesitan el artefacto de `Task/024`. La matriz de paridad §7 **ya lo reconocía**: fila Lambda = «`Task/024`, `Task/025` → `Task/032`» | **CORREGIR AHORA** | `Task/025` depende de **`Task/022` y `Task/024`**. `Task/024` ya dependía de `Task/023`: la cadena queda completa sin cambiar ningún ID |
| **AUD-FIX-014** | `Task/029` exige evidencia de recursos que aún no existen | `STAGE-09:80,85`: «RTT `Lambda ↔ VPS` **medido**» y «**restore demostrado**» como criterios de salida, cuando S3 nace en `Task/030` y la Lambda en `Task/032` | **REASIGNAR** *(gates)* | `Task/029` **define y prepara**; los *gates* que exigen recursos posteriores se mueven a `Task/030`, `Task/032` y `Task/040`. **La tarea no se mueve de etapa** |
| **AUD-FIX-015** | `Task/021` promete `terraform fmt`/`validate` sin Terraform | `STAGE-06:41` y `ROADMAP:182`. `Task/021` es ETAPA 06; el primer `.tf` llega en `Task/025`, ETAPA 08 | **CORREGIR AHORA** | Opción **A+B**: `Task/021` cubre los artefactos existentes; **`Task/025` amplía el workflow** con `fmt` y `validate`. Criterio nuevo: **ningún check pasa por no tener nada que verificar** |
| **AUD-FIX-016** | Topología de dominios diferida hasta `Task/035` | `open-decisions.md:128-129`: D-02 se resuelve en `Task/011` pero *«depende de la topología de dominios, que se define en `Task/035`»* — **24 tareas después** | **CORREGIR AHORA** | **D-07 reformulada** (dominio concreto y DNS) y **D-15 nueva** (topología lógica, `Task/011`). Sin dependencia circular |
| **AUD-FIX-017** | Solape `Task/007` / `Task/010` con MinIO | `ROADMAP:109` y `STAGE-02:70` integran MinIO antes de que exista `ObjectStorage` | **ACLARAR** | `Task/007` integra MinIO **a nivel de infraestructura**; se **prohíbe** el acceso directo temporal de FastAPI. Criterio: al terminar, MinIO sano y **cero objetos leídos o escritos** |

### 3.5 *Ownership* ausente

| ID | Hallazgo | Evidencia reproducida | Veredicto | Owner asignado |
| --- | --- | --- | --- | --- |
| **AUD-FIX-018** | `S3Storage` sin propietario claro | `ROADMAP:131` y `STAGE-03:62` decían *«adaptador **futuro** para Amazon S3»*, y `STAGE-03:103` excluía *«adaptador real … (Etapa 10)»*: ambiguo sobre **quién escribe el código** | **ACLARAR** | **`Task/010`** el código · **`Task/030`** bucket y validación real · **`Task/032`** *wiring*. Mantenerlo en `Task/010` respeta ADR-002: infra **no acepta código de aplicación** |
| **AUD-FIX-019** | Cadena de backup productivo difusa | `production-postgresql-vps.md:549-550` afirmaba que S3 *«ya tendrá credenciales y políticas definidas»* — no las tiene | **ACLARAR** | `Task/029` mecanismo y restore · `Task/030` destino, política y retención · `Task/040` validación final |
| **AUD-FIX-020** | Identidad del VPS hacia AWS sin propietario | `Task/028` cubre **GitHub OIDC → AWS**, que **no** entrega credenciales a un host externo. Nadie poseía la pregunta | **REASIGNAR** *(decisión nueva)* | **D-16**, **abierta**: decide `Task/029`, materializa `Task/030`, valida `Task/040`. **No se elige mecanismo ahora** |
| **AUD-FIX-021** | Certificado TLS de PgBouncer sin ciclo de vida | `security-boundaries.md:176` cubría *«configuración de TLS»*, pero no emisión, CA, *hostname*, renovación ni caducidad | **ACLARAR** | **`Task/029`** el ciclo completo (§10.0 del documento canónico); **`Task/040`** valida vigencia desde la Lambda real |
| **AUD-FIX-022** | Observabilidad del VPS apuntada a `Task/017` | `STATUS.md:373` (R-32) y `local-to-cloud-mapping.md:149` señalaban `Task/017`, que es observabilidad **local** | **CORREGIR AHORA** | ***Baseline*** en **`Task/029`**, validación en **`Task/040`**. `Task/031` es **solo AWS**. **No se adopta CloudWatch Agent** |
| **AUD-FIX-023** | Migraciones productivas sin canal | `Task/036` cubre la **primera** ejecución; el canal repetible no tenía dueño | **ACLARAR** | **`Task/038`**: quién, desde dónde, con qué credencial, orden, *rollback* y protección |
| **AUD-FIX-024** | Medios públicos con URL expirable | **Parcialmente ya resuelto**: `CONTENT_MODEL.md:198` ya exige `object_key` y `software-architecture.md:176` prohíbe binarios en base de datos. **Sin dueño**: el Markdown del contenido y `og:image` | **ACLARAR** | **D-08 ampliada** (`Task/030`) + regla **ya vigente**: nunca se persiste una URL prefirmada. Owners: `Task/010`, `Task/012`, `Task/016` |
| **AUD-FIX-025** | CI/CD multi-provider sin propietario | `STAGE-11` solo contemplaba OIDC → AWS; Terraform es multi-provider desde ADR-007 | **REASIGNAR** | **`Task/039`**: credenciales, rotación, *scopes*, entornos protegidos y **guardas de destino** para AWS, Cloudflare y VPS |

### 3.6 Alcance de tareas finales, DoD y SEO

| ID | Hallazgo | Evidencia reproducida | Veredicto | Acción |
| --- | --- | --- | --- | --- |
| **AUD-FIX-026** | `Task/040` ciega al VPS | `STAGE-12:43-54`: doce criterios, **ninguno** sobre PgBouncer, PostgreSQL, disco, TLS, backup o restore | **CORREGIR AHORA** | Ámbito de verificación ampliado. Se subraya: **verificar no es implementar** |
| **AUD-FIX-027** | `Task/041` ciega al costo del VPS | `STAGE-12:51-54` y `ROADMAP:307`: solo AWS | **CORREGIR AHORA** | Ampliado a VPS, dominio, IPv4, backups, snapshots, transferencia y Cloudflare, con **precios vigentes** |
| **AUD-FIX-028** | DoD cloud anterior a ADR-006 | `DEFINITION_OF_DONE.md:109-113`: 4 criterios, solo sintaxis, `plan` y costo | **CORREGIR AHORA** | **C-1 a C-11**: destino explícito, guardas *fail-closed*, **evidencia que distingue emulación de validación**, matriz de paridad, estado, recursos creados |
| **AUD-FIX-029** | SEO de la SPA dado por bueno | `STAGE-05:52`: *«Cada página pública tiene título, descripción y Open Graph propios»* — comprobable escribiendo código, no verificando comportamiento | **CORREGIR AHORA** | Seis verificaciones concretas, incluida **inspección real de *crawler***, y **criterio de reconsideración** del *rendering*. **No se cambia el stack** |
| **AUD-FIX-030** | R-25 podría darse por demostrado | **No se reproduce.** La matriz §7 sigue **entera en `No evaluada`** y R-25 **Abierto**, con la advertencia explícita de no confundir soporte documentado con paridad demostrada | **RECHAZADO** | **Ninguna.** Ya era correcto |

---

## 4. Cambios por repositorio

### `personal-blog-infra` — 19 modificados, 2 creados

| Archivo | Cambio |
| --- | --- |
| `README.md` | Estado real: `Task/005` aprobada, 5/41, backend **existente**, VPS no contratado |
| `docs/project-management/ROADMAP.md` | Dependencias de `Task/025`; alcance de `010`, `011`, `007`, `016`, `017`, `021`, `028`, `029`, `030`, `031`, `032`, `036`, `038`, `039`, `040`, `041`; **mapa de responsabilidades transversales**; lista de mantenimiento |
| `docs/project-management/STATUS.md` | `Task/005.4` fusionada y normalizada; bloque de `Task/005.5`; tabla de repositorios; R-03 y R-32; 13 decisiones |
| `docs/project-management/DEFINITION_OF_DONE.md` | DoD cloud reescrita: **C-1 a C-11** |
| `docs/architecture/open-decisions.md` | **D-15** y **D-16** nuevas; **D-02**, **D-07**, **D-08** y **D-10** reformuladas; conteo a 13 |
| `docs/architecture/aws-local-parity.md` | PNG deja de ser autoridad canónica; ADR-007 vigente; guardas *fail-closed* multi-provider; typo de referencia |
| `docs/architecture/production-postgresql-vps.md` | §10.0 ciclo de vida del certificado; §15.1 reparto del backup; §15.3.1 observabilidad del VPS; R-32; §18 |
| `docs/architecture/local-to-cloud-mapping.md` | Estado ADR-007; *ownership* de `S3Storage`; regla de claves de objeto; diferencia #13 |
| `docs/architecture/overview.md` | Conteo de decisiones; principio 5 acotado; D-15 y D-16 |
| `docs/architecture/security-boundaries.md` | §7 ampliada con 6 propietarios nuevos; V-12 precisada |
| `docs/stages/STAGE-02` | PR de `Task/005` fusionado; límite `Task/007` ↔ `Task/010` |
| `docs/stages/STAGE-03` | `S3Storage` desambiguado; D-15 en `Task/011`; criterios y exclusiones |
| `docs/stages/STAGE-05` | SEO verificable y criterio de reconsideración; `Task/017` acotada a local |
| `docs/stages/STAGE-06` | `Task/021` sin Terraform inexistente; criterio anti-check-vacío |
| `docs/stages/STAGE-08` | ADR-006 **Aceptada**; `Task/025` depende de `Task/024`; ampliación del CI |
| `docs/stages/STAGE-09` | Qué define `Task/029` y qué no puede validar; D-16; criterios de salida; exclusiones |
| `docs/stages/STAGE-10` | `Task/030` backups e identidad; `Task/031` solo AWS; `Task/032` concurrencia y RTT |
| `docs/stages/STAGE-11` | Canal de migraciones; automatización multi-provider; criterios |
| `docs/stages/STAGE-12` | `Task/040` valida el VPS; `Task/041` contempla su costo |
| `docs/tasks/TASK-005.5-…md` | **Creado** |
| `docs/task-reports/TASK-005.5-report.md` | **Creado** |

### `personal-blog-backend` — 2 modificados · **0 archivos de código**

`CONTRIBUTING.md` (regla de ramas + nota de implementación ya iniciada) y `README.md` §12.

### `personal-blog-frontend` — 2 modificados · **0 archivos de código**

`CONTRIBUTING.md` (regla de ramas) y `README.md` (regla de ramas, fase y ramas obsoletas).

**`CLAUDE.md` raíz: no modificado.** Ya contenía el invariante correcto.

---

## 5. Ownership final

| Cadena | Define / construye | Materializa | Valida |
| --- | --- | --- | --- |
| **`S3Storage`** | `Task/010` | `Task/030` · `Task/032` | `Task/040` |
| **Backup productivo** | `Task/029` | `Task/030` | `Task/040` |
| **Identidad VPS → AWS** (**D-16**) | `Task/029` *(decide)* | `Task/030` | `Task/040` |
| **Certificado TLS de PgBouncer** | `Task/029` | `Task/029` | `Task/040` |
| **Observabilidad del VPS** | `Task/029` | `Task/029` | `Task/040` |
| **Migraciones en producción** | `Task/036` *(primera)* | `Task/038` *(canal)* | `Task/040` |
| **Medios públicos** (**D-08**) | `Task/010` · `Task/016` | `Task/030` | `Task/040` |
| **CI multi-provider** | `Task/028` *(solo AWS)* | `Task/039` | `Task/040` |
| **Topología de dominios** (**D-15**) | `Task/011` | `Task/018` | `Task/035` *(**D-07**)* |

---

## 6. Validaciones ejecutadas

| # | Validación | Resultado |
| --- | --- | --- |
| 1 | `git fetch --prune` + `main == origin/main` en los 3 repositorios | ✔ |
| 2 | `HEAD == main` justo tras crear cada rama | ✔ en los 3 |
| 3 | `git log --oneline main..HEAD` | **vacío** en los 3 — **0 commits propios** |
| 4 | `git diff --check` | **sin salida** en los 3 — 0 espacios finales, 0 conflictos |
| 5 | `git diff --cached --name-only` | **vacío** en los 3 — **nada en *staging*** |
| 6 | Reglas operativas «Task desde `dev`» en README/CONTRIBUTING/CLAUDE | **0 coincidencias** |
| 7 | `ADR-006` y `ADR-007` con estado `Propuesta` en texto **vigente** | **0** — las restantes son fichas y reportes **históricos**, que no se tocan |
| 8 | Estado real de los ADR | ADR-001…005 `Aceptada`; **ADR-006 `Aceptada` ✔**; **ADR-007 `Aceptada` ✔** |
| 9 | Enlaces relativos `.md`/`.png` en infra | **0 rotos** |
| 10 | IDs de tarea en `STATUS.md` | **41**, únicos, `001`–`041`, **0 faltantes, 0 sobrantes** |
| 11 | IDs de tarea en `ROADMAP.md` | **41**, únicos; **diferencia con STATUS = 0** |
| 12 | Avance declarado | **5 / 41 = 12 %**, coherente en las 3 ubicaciones |
| 13 | `git status --porcelain -- images/` | **vacío** — PNG intacto |
| 14 | Archivos Terraform creados | **0** — no existe ningún `.tf` en el workspace |
| 15 | `docker-compose.yml` modificado | **No** |
| 16 | Código funcional modificado (backend/frontend) | **0 archivos** — solo `README.md` y `CONTRIBUTING.md` |
| 17 | Búsqueda de secretos en lo modificado | **0** — ninguna clave, token, contraseña ni `.env` |
| 18 | *Mojibake* en los archivos tocados | **0** |
| 19 | Commits / push / merge / PR | **0 / 0 / 0 / 0** |

---

## 7. Auditoría posterior a las correcciones

Segunda pasada **read-only**, intentando reproducir de nuevo cada problema.

| # | Problema | Resultado | Evidencia |
| --- | --- | --- | --- |
| 1 | Task desde `dev` | **RESUELTO** | 0 reglas operativas en los 3 repositorios |
| 2 | ADR en `Propuesta` antigua | **RESUELTO** | 0 en texto vigente; las históricas se conservan a propósito |
| 3 | RDS como destino productivo | **NO APLICABA** | Todas las menciones lo excluyen o son investigación histórica |
| 4 | PNG canónico | **RESUELTO** | Única representación canónica = Mermaid de `aws-local-parity` §3.3. **Archivo intacto** |
| 5 | `Task/025` sin `Task/024` | **RESUELTO** | `STAGE-08:79` — «Depende de: `Task/022` **y `Task/024`**» |
| 6 | `Task/029` dependiendo de recursos futuros | **RESUELTO** | Tabla «define / se valida de verdad en» + exclusiones explícitas |
| 7 | `S3Storage` sin owner | **RESUELTO** | Tabla en `STAGE-03`, `local-to-cloud-mapping` y ROADMAP |
| 8 | Backup sin owner | **RESUELTO** | Reparto en 3 tramos, `production-postgresql-vps` §15.1 |
| 9 | Observabilidad VPS → `Task/017` | **RESUELTO** | 0 punteros; negado explícitamente en 4 documentos |
| 10 | Certificado sin owner | **RESUELTO** | §10.0 con 7 aspectos y validación en `Task/040` |
| 11 | Migración productiva sin owner | **RESUELTO** | `STAGE-11`, `Task/038` |
| 12 | CI de Terraform antes de Terraform | **RESUELTO** | `Task/021` sin checks vacíos; `Task/025` los añade |
| 13 | `Task/040` ciega al VPS | **RESUELTO** | 6 ámbitos + 4 criterios de salida nuevos |
| 14 | `Task/041` ciega al VPS | **RESUELTO** | Alcance de costo ampliado |
| 15 | Dominio lógico demasiado tardío | **RESUELTO** | **D-15** en `Task/011`; D-07 acotada a DNS |
| 16 | Media con URL expirable persistida | **RESUELTO** *(regla)* · **DELIBERADAMENTE DIFERIDO** *(CDN)* | La regla ya es vigente; la estrategia de CDN y `og:image` es **D-08**, `Task/030` |
| 17 | Credenciales multi-provider sin owner | **RESUELTO** *(ownership)* · **DELIBERADAMENTE DIFERIDO** *(mecanismo)* | `Task/039` es owner; **D-16** abierta para el VPS |
| 18 | R-25 / *critical path* Floci | **NO APLICABA** | Matriz entera en `No evaluada`; **R-25 Abierto** |

**Ningún riesgo se cerró.** Solo se corrigió el *owner* incorrecto de **R-32** y el texto
obsoleto («propuesta») de **R-03**. **R-19 a R-35 siguen abiertos.**

---

## 8. Lo que NO se hizo, deliberadamente

| No se hizo | Por qué |
| --- | --- |
| Crear **ADR-008** | No apareció ninguna decisión arquitectónica independiente. Corregir *ownership* no es arquitectura nueva |
| Elegir el mecanismo de identidad del VPS | Depende del proveedor, **no seleccionado**. **D-16** queda abierta con owner y momento |
| Elegir ACME o proveedor de certificados | Misma razón. Se asigna el ciclo de vida, no la herramienta |
| Adoptar **CloudWatch Agent** para el VPS | Tiene costo, superficie y credenciales propias, ligadas a D-16. Decide `Task/029` |
| Cambiar a Next.js o SSR | Sin evidencia. `Task/016` solo puede **abrir** la reconsideración, con ADR propio |
| Mover `Task/029` después de `Task/032` | Rompería la ETAPA 09. Se movieron los ***gates***, no la tarea |
| Renumerar o fusionar tareas | **41 identificadores intactos** |
| Tocar reportes y fichas históricos | Describen correctamente el estado de su momento |
| Tocar `images/Infraestructura.png` | Prohibido explícitamente; verificado intacto |

---

## 9. Cómo validarlo

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal

# 1. Ninguna regla operativa vigente ordena crear Task desde dev
Select-String -Path personal-blog-*\README.md, personal-blog-*\CONTRIBUTING.md `
  -Pattern 'creado desde .dev.'

# 2. Ramas creadas de main, sin commits ni staging
foreach ($r in 'personal-blog-infra','personal-blog-backend','personal-blog-frontend') {
  Push-Location $r
  "$r : $(git rev-parse --abbrev-ref HEAD)"
  git log --oneline main..HEAD    # vacio
  git diff --check                # vacio
  git status --short
  Pop-Location
}

# 3. PNG intacto y sin Terraform
cd personal-blog-infra
git status --porcelain -- images/ docker-compose.yml   # vacio
```

Luego revisar: [ROADMAP](../project-management/ROADMAP.md) *Mapa de responsabilidades
transversales* · [open-decisions](../architecture/open-decisions.md) **D-15**/**D-16** ·
[STAGE-09](../stages/STAGE-09-cloud-accounts.md) · [STAGE-12](../stages/STAGE-12-launch-and-operations.md).

---

## 10. GO / NO-GO de `Task/006`

> ### **GO** — tras la fusión de los PR de `Task/005.5` y la normalización `main → dev`.

| Comprobación | Resultado |
| --- | --- |
| Dependencia `Task/004` aprobada | ✔ (2026-07-31) |
| `main` y `dev` normalizadas en frontend | ✔ `git diff main dev` vacío |
| PR pendientes que la bloqueen | **Ninguno** — `#10` fusionado |
| Bloqueos activos | **0** |
| ¿Alguna corrección de `Task/005.5` afecta a `Task/006`? | **No.** Todas apuntan a ETAPAS 03 y 05–12 |
| ¿Problemas de la ETAPA 09 la bloquean? | **No.** Tienen owner correcto y no tocan el frontend |

**Único requisito restante:** que el usuario fusione los tres pull request de `Task/005.5` y
se complete la normalización `main → dev`. `Task/006` **nacerá desde `main`**, en
`personal-blog-frontend`.

---

## 11. Estado y límites

**Estado:** **Aprobada** ✔ el **2026-08-16**, con la expresión exacta
`approved: Task/005.5-Alinear-Planificacion-Tras-Auditoria`.

**5 / 41 (12 %) · ETAPA 02 = 1 / 3 · `Task/006` = Pendiente · 41 tareas intactas.**
La aprobación de este mantenimiento **no modifica el conteo del roadmap**.

**0 recursos cloud · 0 código funcional · 0 Terraform · 0 cambios en Compose ·
0 cambios en `images/` · `Task/006` no iniciada.**

### 11.1 Cierre ejecutado tras la aprobación

Hasta recibir `approved:` no hubo **ningún** commit, push, merge ni PR. Después, y solo
entonces, se ejecutó el flujo de [`WORKFLOW.md`](../project-management/WORKFLOW.md) §3 en
los tres repositorios: commit en la rama Task, integración en `dev` con merge `--no-ff`,
publicación de `dev` y de la rama Task, y creación del pull request
**`Task/005.5 → main`** —nunca `dev → main`—.

**Claude no fusionó ningún pull request.** Aceptarlos y decidir si se eliminan las ramas
remotas es responsabilidad exclusiva del usuario. La rama Task local se eliminó con
`git branch -d`; la remota se conserva mientras el PR siga abierto.

**`Task/006` no se inicia** hasta que el usuario fusione los tres PR y se complete la
normalización `main → dev`.
