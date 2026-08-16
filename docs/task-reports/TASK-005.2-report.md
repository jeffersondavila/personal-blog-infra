# Reporte — TASK-005.2 · Documentar la estrategia de IaC local con Floci

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Tipo** | **Mantenimiento de arquitectura y gobierno documental** |
| **Cuenta en el roadmap** | **No.** Avance global y ETAPA 02 **sin cambios** |
| **Estado final** | **Aprobada** ✔ — cerrada el 2026-08-15 |
| **Expresión de aprobación** | `approved: Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Repositorio** | `personal-blog-infra` **únicamente** |
| **Rama** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local`, creada desde `dev` (`4e6bfaa`). **Publicada en el cierre** |
| **Fecha** | 2026-08-15 |
| **Ficha** | [TASK-005.2](../tasks/TASK-005.2-document-floci-local-iac-strategy.md) |
| **Commits** | **1**, creado **después** de la aprobación explícita del usuario |
| **Pull request** | `Task/005.2 → main` — **abierto, sin fusionar** |

---

## 1. Estado inicial encontrado

Verificado en Git y GitHub al comenzar la sesión, sin asumir nada de conversaciones
previas.

| Repositorio | `main` | `dev` | Rama activa | Árbol | Ramas `Task/*` remotas |
| --- | --- | --- | --- | --- | --- |
| `personal-blog-infra` | `af8a04c` — **4 commits por detrás** de `origin/main` | `b44e36b` | `main` | Limpio | Ninguna — `origin/Task/005.1` aparece como `[deleted]` en el primer `fetch --prune` |
| `personal-blog-backend` | `db6ab18` | `ce4f1bc` | `main` | Limpio | Ninguna |
| `personal-blog-frontend` | `144a401` | `8823cc3` | `main` | Limpio | Ninguna |

El repositorio de infraestructura estaba **desincronizado en local**: el usuario había
fusionado el PR `#7` en GitHub, pero el clon local todavía apuntaba al estado anterior.

## 2. Verificación del PR `#7`

`gh pr view 7 --repo jeffersondavila/personal-blog-infra`:

| Campo | Valor real devuelto |
| --- | --- |
| `number` | **7** |
| `state` | **`MERGED`** ✔ |
| `baseRefName` | **`main`** ✔ |
| `headRefName` | **`Task/005.1-Formalizar-TDD-Backend`** ✔ |
| `mergeCommit.oid` | **`2f56a13456dd2d4c774560a4ab4269b204bb2ce6`** |
| `mergedAt` | **`2026-08-16T00:25:21Z`** (UTC) — 2026-08-15 en hora local |
| `url` | `https://github.com/jeffersondavila/personal-blog-infra/pull/7` |

**Rama remota eliminada — confirmado sin ejecutar ningún borrado:**

- El `git fetch --prune origin` inicial reportó
  `- [deleted] (none) -> origin/Task/005.1-Formalizar-TDD-Backend`.
- `git ls-remote --heads origin "Task/*"` devuelve **vacío**.
- `git branch -r` lista solo `origin/HEAD`, `origin/dev` y `origin/main`.

**No se ejecutó `git push --delete` en ningún momento.** El listado completo de PR confirma
además que `#1`–`#7` están todos en estado `MERGED` y que **no existe ningún PR de
`Task/005.2`**.

## 3. Merge commit real del PR `#7`

**`2f56a13456dd2d4c774560a4ab4269b204bb2ce6`**

> `Merge pull request #7 from jeffersondavila/Task/005.1-Formalizar-TDD-Backend`

El `pull --ff-only` de `main` trajo 4 commits y 11 archivos (`af8a04c..2f56a13`), entre
ellos `BACKEND_TESTING_STRATEGY.md`, la ficha y el reporte de `Task/005.1` y
`images/Infraestructura.png`.

## 4. Normalización `main → dev` en `personal-blog-infra`

Estado antes de normalizar, tras actualizar ambas ramas:

| Comprobación | Resultado |
| --- | --- |
| `git log --oneline dev..main` | `2f56a13` — el merge del PR **faltaba en `dev`** |
| `git log --oneline main..dev` | `b44e36b` — el merge de la rama Task en `dev` |
| `git diff --stat main dev` | **vacío** — mismo contenido, historiales divergentes |

Es exactamente el patrón previsto: el cierre de `Task/005.1` había integrado la tarea en
`dev` mientras `main` esperaba el PR.

**Acción ejecutada:**

```
git merge --no-ff main -m "merge: sincronizar dev con main despues de Task/005.1"
git push origin dev
```

Estado después:

| Comprobación | Resultado |
| --- | --- |
| `main` | **`2f56a13`** |
| `dev` | **`4e6bfaa`** — `merge: sincronizar dev con main despues de Task/005.1` |
| `git log --oneline dev..main` | **vacío** ✔ |
| `git diff --stat main dev` | **vacío** ✔ |
| `git merge-base --is-ancestor 2f56a13 dev` | **`2f56a13` es ancestro de `dev`** ✔ |
| Publicación | `b44e36b..4e6bfaa dev -> dev` ✔ |
| Ramas locales antes de crear `005.2` | **solo `main` y `dev`** ✔ |

## 5. Backend y frontend

Verificados **sin modificar nada**: `fetch --prune`, `pull --ff-only` en `main` y en `dev`,
inspección de divergencias y regreso a `main`.

| Repositorio | `main` | `dev` | `dev..main` | `git diff main dev` | Árbol | Rama final |
| --- | --- | --- | --- | --- | --- | --- |
| `personal-blog-backend` | `db6ab18` | `ce4f1bc` | **vacío** | **vacío** | Limpio | `main` |
| `personal-blog-frontend` | `144a401` | `8823cc3` | **vacío** | **vacío** | Limpio | `main` |

Ambos estaban **ya al día**: los `pull` reportaron `Already up to date`. **No hizo falta
ninguna acción correctiva** y **no se creó rama `Task/005.2`** en ninguno de los dos.

## 6. Rama `Task/005.2`

Comprobaciones **previas** a crearla, todas negativas como se esperaba:

| Comprobación | Resultado |
| --- | --- |
| `git branch --list "Task/005.2*"` | vacío |
| `git ls-remote --heads origin "Task/005.2*"` | vacío |
| `gh pr list --search "005.2" --state all` | `[]` |

| Campo | Valor |
| --- | --- |
| **Nombre** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Base** | `dev` normalizado |
| **Commit base** | **`4e6bfaa2936fb91786759b974b44a79e614fb4f0`** |
| **Publicada** | **No** |

No se sobrescribió ni eliminó nada.

---

## 7. Validaciones ejecutadas

Ejecutadas el 2026-08-15. **Ninguna se declara sin haberse ejecutado.**

| # | Validación | Resultado real |
| --- | --- | --- |
| 1 | PR `#7` fusionado | **`MERGED`**, base `main`, head `Task/005.1`, merge `2f56a13`, `mergedAt 2026-08-16T00:25:21Z`. |
| 2 | Normalización `main → dev` | **Completada.** `dev..main` vacío, `git diff main dev` vacío, `2f56a13` ancestro de `dev`. `dev` = `4e6bfaa`, publicado. |
| 3 | Rama remota `Task/005.1` | **Ausente.** `git ls-remote --heads origin "Task/*"` vacío. **Ningún borrado ejecutado por la sesión.** |
| 4 | Backend y frontend | **Verificados y sin modificar.** Árboles limpios en `main`, `main`/`dev` coherentes, sin rama `005.2`. |
| 5 | Creación de `Task/005.2` | **Creada desde `dev` (`4e6bfaa`).** Sin colisiones previas. No publicada. |
| 6 | Documento canónico | **Creado.** `docs/architecture/aws-local-parity.md`, 16 secciones: objetivo, límites, tres vistas, portabilidad, verificación de Floci, capacidades, matriz, PostgreSQL, seguridad, *learning loop*, roadmap, criterios de éxito, transición, riesgos, criterio de abandono y referencias. |
| 7 | Fuentes de la investigación | **Solo oficiales**, consultadas el **2026-08-15**: repositorio `floci-io/floci` (README, `docs/services/`, `docs/configuration/`, CHANGELOG, `docker-compose.yml`, `compatibility-tests/compat-terraform/`, listado de releases) y `floci.io/floci/`. **0 blogs, 0 artículos de terceros.** |
| 8 | Vocabulario prudente | **Cumplido.** Las 6 coincidencias de «paridad completa» / «idéntico a AWS» en los dos documentos nuevos son **prohibiciones o negaciones explícitas**, nunca afirmaciones. |
| 9 | Portabilidad y diferencias legítimas | **Presentes.** §4 fija «una sola definición, un solo grafo»; §4.3 rechaza expresamente la promesa de «cero cambios»; §4.4 es una tabla **cerrada** de 10 diferencias admisibles. |
| 10 | Matriz de paridad | **Creada.** 12 filas, 6 estados definidos. **Todas las filas evaluables están en `No evaluada`**; ninguna celda declara paridad. |
| 11 | Versión de Floci | **No fijada**, deliberadamente. §5.4 establece la regla: se elige una release estable en `Task/025`; **`latest` y `nightly` nunca**. |
| 12 | Dos modos locales y MinIO | **Documentados** en §3.1, §3.2 y §3.4. MinIO, PostgreSQL local, Traefik, Portainer y Docker Compose **se conservan**; §3.4 los declara complementarios, no sustitutivos. |
| 13 | **D-01** y **D-06** | **Siguen abiertas.** §8 y §4.5 del canónico lo declaran; `open-decisions.md` añade a ambas una aclaración fechada. **D-14** se añade con *respuesta propuesta*, no resuelta. |
| 14 | **ADR-006** | **Creado** en `docs/adr/ADR-006-local-aws-parity-with-floci.md`, estado **`Propuesta — pendiente de aprobación`**. Alternativas **A–D**, límites de fidelidad, riesgos y criterio de revisión/abandono. Número libre confirmado: existían solo ADR-001 a ADR-005. |
| 15 | Seguridad | **Ampliada.** Componente **C-12** en `security-boundaries.md`, nueva §8 con controles **S-01 a S-11**, guardas *fail-closed* **G-01 a G-05**, 4 comunicaciones permitidas y 4 prohibidas nuevas, 3 superficies de ataque y un principio transversal nuevo. |
| 16 | Etapas 08, 10 y 11 | **Actualizadas.** ETAPA 08 renombrada a *Preparación Cloud + AWS Local Parity* con 18 criterios de salida; ETAPA 10 con sección «reutilizar, no reinventar»; ETAPA 11 con el encaje de CI, **sin duplicar** responsabilidades de `Task/020`, `037`, `038` ni `039`. |
| 17 | Riesgos | **R-19 a R-28** registrados en `STATUS.md` como **`Propuesto`**, cada uno con impacto, mitigación y tarea que lo valida. Numeración verificada: el último riesgo previo era **R-18**. |
| 18 | Recuento e integridad del roadmap | **41 filas de tarea** en `ROADMAP.md` y **41** en la tabla completa de `STATUS.md`. **41 identificadores únicos**, de `001` a `041`. **Ninguna renumerada, añadida ni eliminada.** Avance **5 de 41 (12 %)**, ETAPA 02 **1 de 3**, `Task/006` **Pendiente**. |
| 19 | `PROJECT_INSTRUCTIONS.md` | **Actualizado.** Nueva sección **15. AWS LOCAL PARITY LAW** (10 reglas compactas + enlace al canónico); la antigua §15 pasa a §16 y la §16 a §17, sin pérdida de contenido. |
| 20 | Enlaces Markdown relativos | Barrido final sobre los **16 archivos** afectados: **241 enlaces relativos comprobados, 0 rotos**. Un barrido **intermedio** anterior, sobre los 15 archivos que existían antes de crearse este reporte, había señalado 5 referencias a `TASK-005.2-report.md`; quedaron resueltas al crearlo. |
| 21 | `images/Infraestructura.png` | **Intacta.** `git status --porcelain -- images/` **vacío**. Blob `eaa775f`, 2 147 031 bytes, SHA-256 `215FF326…37420B`. No modificada, no regenerada, no movida, no reemplazada. |
| 22 | Búsqueda de secretos | **0 coincidencias** sobre todos los archivos nuevos y modificados (patrones de clave AWS, clave privada, token de GitHub y contraseña literal). |
| 23 | Archivos Terraform | **0** en todo el workspace: `*.tf`, `*.tfvars`, `*.tfstate` y `*.hcl`. |
| 24 | Docker Compose y repositorios ajenos | `docker-compose.yml` **sin cambios**. `personal-blog-backend` y `personal-blog-frontend`: **`git status --porcelain -b`** devuelve solo la línea de rama — **0 archivos modificados** en ambos. |
| 25 | Floci no instalado | `docker ps -a --filter name=floci` **vacío**; `docker images --filter reference=*floci*` **vacío**. Sin `docker pull`, sin contenedores, sin `terraform`, sin AWS CLI. |
| 26 | `git diff --check` | **Sin errores** de espacios en blanco. |

---

## 8. Hallazgos de la investigación oficial de Floci

**Fecha de verificación: 2026-08-15.** Fuentes exclusivamente oficiales.

### 8.1 Estado del proyecto

| Dato | Valor observado |
| --- | --- |
| Repositorio | `floci-io/floci` — MIT, creado el 2026-02-18, activo |
| Última release estable | **1.6.0** (2026-08-06) |
| Cadencia observada | Una release cada **3–4 días** (1.5.16 → 1.6.0) |
| Páginas de servicio | **74** en `docs/services/`, sin contar `index.md` |
| Puerto e integración | **4566**, `AWS_ENDPOINT_URL`, credenciales `test`/`test`, región `us-east-1` |
| IaC declarada | Terraform, OpenTofu y AWS CDK, con suites de compatibilidad **versionadas en el repositorio** |

La cadencia es el motivo directo de **no fijar versión aquí**: cualquier número escrito hoy
estaría obsoleto antes de llegar a `Task/025`.

### 8.2 Lo relevante para este proyecto

| Servicio | Hallazgo principal |
| --- | --- |
| **Terraform** | La suite oficial usa el provider **`hashicorp/aws ~> 6.0`** con bloque `endpoints` y los flags `skip_credentials_validation`, `skip_metadata_api_check`, `skip_requesting_account_id` y `s3_use_path_style`, más un backend `s3` local con bloqueo en DynamoDB. **Es exactamente el patrón de portabilidad que la estrategia adopta.** |
| **Lambda** | Ejecución en **contenedores Docker reales** con las imágenes oficiales de runtime de AWS; ZIP e imagen; invocación síncrona y asíncrona; *function URLs*. **Requiere montar `/var/run/docker.sock`.** Sin *layers*, sin concurrencia aprovisionada, sin *response streaming*. |
| **API Gateway** | v1 REST, **v2 HTTP API** y v2 WebSocket; `AWS_PROXY` completo; URL local sobre un dominio comodín resuelto por DNS embebido. **Sin dominios personalizados, VPC Links ni certificados de cliente.** |
| **S3** | Cobertura amplia, incluidas **URLs prefirmadas**, CORS, políticas, versionado y *lifecycle* — todo lo que el MVP necesita. Sin replicación, *access logging*, *inventory* ni métricas. |
| **SSM** | Parameter Store completo para el uso previsto, pero **`SecureString` conserva el tipo y NO cifra el valor en reposo**. |
| **IAM** | API de gestión amplia y ~50 políticas gestionadas pre-cargadas, **todas con comodines permisivos**. **La aplicación de políticas está DESACTIVADA por omisión**: se aceptan cualesquiera credenciales y pasan todas las peticiones. El modo opcional mantiene exenciones. |
| **CloudWatch** | Logs con retención y consulta; **los filtros de suscripción se almacenan pero no entregan**; **Logs Insights degrada en silencio** (un filtro con `and`/`or` conserva solo la primera condición). Alarmas con estado **manual**, sin motor de evaluación documentado. |
| **RDS** | Motores **reales** en Docker (`postgres:16-alpine`, `mysql:8.0`, `mariadb:11`). Plano de datos de DB Proxy solo como metadatos. |

### 8.3 Hallazgo más importante — origen de **R-25**

La suite oficial de compatibilidad Terraform (`compatibility-tests/compat-terraform`)
ejercita S3, SQS, SNS, DynamoDB, IAM, SSM, Secrets Manager, RDS, Cognito, alarmas de
CloudWatch, VPC/EC2, Route53, Firehose, Application Auto Scaling y SES.

**No incluye `aws_lambda_function`, ni recursos `aws_apigatewayv2_*`, ni
`aws_cloudwatch_log_group`.**

Es decir: **el camino crítico exacto de este proyecto —API Gateway v2 → Lambda →
CloudWatch Logs, definido con Terraform— no está demostrado por el proyecto upstream.** Los
servicios están documentados por separado; su combinación con Terraform, no.

No es motivo para descartar la estrategia —es precisamente lo que `Task/025` tiene que
demostrar—, pero **sí** es motivo para no darla por hecha. De ahí que la matriz nazca vacía
y que el criterio de revisión contemple reducir el alcance del laboratorio.

---

## 9. Documentos creados y modificados

**4 creados · 12 modificados · 0 eliminados — 16 archivos afectados.** Todos en
`personal-blog-infra`. Coincide con el `git status --porcelain` final: 12 líneas `M` y 4
líneas `??`.

### Creados

| Archivo | Contenido |
| --- | --- |
| `docs/architecture/aws-local-parity.md` | **Documento canónico.** Fuente única de la estrategia. |
| `docs/adr/ADR-006-local-aws-parity-with-floci.md` | Decisión arquitectónica, estado **`Propuesta`**. |
| `docs/tasks/TASK-005.2-document-floci-local-iac-strategy.md` | Ficha de la tarea. |
| `docs/task-reports/TASK-005.2-report.md` | Este reporte. |

### Modificados

| Archivo | Cambio |
| --- | --- |
| `docs/stages/STAGE-08-cloud-ready.md` | Renombrada a *Preparación Cloud + AWS Local Parity*; objetivo y alcance de `Task/023`–`Task/026` ampliados; 18 criterios de salida; 6 exclusiones nuevas; 5 riesgos añadidos. **IDs y nombres intactos.** |
| `docs/stages/STAGE-10-cloud-deployment.md` | Sección «reutilizar, no reinventar»; clasificación de diferencias en 5 categorías; 2 criterios de salida nuevos. |
| `docs/stages/STAGE-11-deployment-automation.md` | Encaje de la validación local en `Task/039`, con las reglas de `destroy` intactas. |
| `docs/architecture/overview.md` | Nueva §4.1 con el tercer entorno; principio de diseño 8; referencia a `Infraestructura.png`; corregido el recuento de decisiones abiertas. |
| `docs/architecture/local-to-cloud-mapping.md` | Tercera columna *AWS Local Parity Lab*; matiz en «Infraestructura»; 4 diferencias nuevas (9–12). |
| `docs/architecture/security-boundaries.md` | Componente **C-12**; comunicaciones permitidas y prohibidas; 3 superficies de ataque; principio transversal 9; **nueva §8** completa. |
| `docs/architecture/open-decisions.md` | **D-14** con respuesta propuesta y lo que sigue pendiente; aclaraciones fechadas en **D-01** y **D-06**. |
| `docs/project-management/ROADMAP.md` | ETAPA 08 renombrada y descrita; nota en ETAPA 10; matiz en `Task/039`; mantenimiento `005.2`; **corregido** el ejemplo de cálculo de avance, que decía `4 / 41 = 10 %`. |
| `docs/project-management/STATUS.md` | Vista rápida; cierre y normalización de `Task/005.1`; nueva sección «Mantenimiento en curso»; riesgos **R-19 a R-28**; estado real de los tres repositorios con SHA; notas de estado. |
| `docs/claude/PROJECT_INSTRUCTIONS.md` | Nueva **§15 AWS LOCAL PARITY LAW**; renumeración de §15→§16 y §16→§17; restricción añadida en la lista de arquitectura. |
| `docs/task-reports/README.md` | Índice con `Task/005.2`. |
| `README.md` | Sección *AWS Local Parity*; referencia a `Infraestructura.png`; árbol de `docs/` con el documento canónico. |

> `README.md` no figuraba en la lista de documentos sugerida por el prompt, pero contiene un
> **índice del árbol de `docs/`** y una sección de arquitectura cloud que habrían quedado
> desactualizados. El cambio es mínimo y evita un índice incompleto.

---

## 10. Decisiones y su estado

| Elemento | Durante la ejecución | **Estado final tras la aprobación** |
| --- | --- | --- |
| **ADR-006** | `Propuesta` | **`Aceptada`** ✔ (2026-08-15) |
| `aws-local-parity.md` | `Propuesta` | **`Vigente`** ✔ |
| **D-14** — ¿emulador AWS local para la IaC? | Respuesta propuesta | **`Resuelta`** — **sí, Floci**, con AWS real como autoridad final |
| Riesgos **R-19** a **R-28** | `Propuesto` | **`Abierto`** — los diez. **Ninguno cerrado** |
| `security-boundaries.md` §8 y **C-12** | `Propuesta` | **`Vigente`** ✔ |
| `PROJECT_INSTRUCTIONS.md` §15 | `Propuesta` | **Vigente y obligatoria** ✔ |
| **D-01** — proveedor de PostgreSQL administrado | Abierta | **Abierta.** `Task/029`. Explícitamente **no** la afecta que Floci soporte RDS |
| **D-06** — backend de estado de Terraform | Abierta | **Abierta.** `Task/025`. Se documenta la tensión, no la solución |
| **D-11**, **D-12** | Abiertas | **Abiertas**, sin cambios. Se anota que **no deben decidirse con mediciones locales** |
| **ADR-001 a ADR-005** | Aceptadas | **Aceptadas**, sin modificar |
| **ADR-003** | Sin cambios | **Sin cambios.** El laboratorio no introduce ningún servicio nuevo en la arquitectura de producción ni toca la lista de servicios excluidos |

---

## 11. Riesgos

**10 riesgos nuevos**, **abiertos** desde la aprobación: **R-19** a **R-28**. Detalle en
[`STATUS.md`](../project-management/STATUS.md) y en
[`aws-local-parity.md`](../architecture/aws-local-parity.md) §14.

De impacto **alto**: **R-20** (falsa sensación de paridad), **R-22** (privilegio sobre
Docker), **R-23** (endpoint expuesto), **R-24** (actuar sobre AWS real por accidente),
**R-25** (camino crítico no cubierto upstream) y **R-28** (IAM sin aplicación de políticas).

Riesgos previos: **sin cambios**. Ninguno se cierra en esta tarea. **R-09** queda
explícitamente **agravado** por **R-22**: pasaría a haber más de un componente con
capacidad administrativa sobre el mismo demonio de Docker.

---

## 12. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | El comando de recuento de tareas heredado de `Task/005.1` usaba el patrón `Task/0\d{3}-` — **mencionado aquí solo como registro histórico del defecto; no usarlo**. No coincide con ningún identificador real: `Task/001` lleva el `0` dentro del literal y solo dos dígitos después. Devolvía **0** en lugar de 41 —un falso negativo que podría haberse leído como «el roadmap se rompió». | Se corrigió el patrón a `^\| ` + backtick + `Task/0` y se verificó **enumerando las 41 filas** una a una: `001`–`041`, 41 identificadores únicos, sin huecos ni duplicados. **El patrón defectuoso no aparece en ningún comando activo** de la ficha ni de este reporte: los de la ficha §9 y §15 usan ya el corregido. |
| 2 | Al barrer los enlaces relativos aparecieron **5 rotos**, todos apuntando a `TASK-005.2-report.md`. | Falso positivo del orden de trabajo: el reporte aún no existía. Resuelto al crearlo; barrido final con **0 rotos**. |
| 3 | `ROADMAP.md` §«Cálculo del avance» arrastraba `Actualmente: 4 / 41 = 10 %`, en contradicción con el `5 de 41 (12 %)` del resto del documento. No lo introdujo esta tarea. | Se corrigió a `5 / 41 = 12 %` y se añadió la aclaración de que las tareas de mantenimiento no entran en el cálculo. Es una corrección de coherencia, no un cambio de alcance. |

Ninguna operación falló. **No se ejecutó ninguna acción destructiva.**

---

## 13. Confirmación explícita de límites respetados

> **Dos momentos distintos.** Hasta la aprobación no hubo commit, push, merge ni PR. El
> usuario aprobó con la expresión exacta y autorizó el flujo completo; las operaciones de
> Git posteriores son **parte del cierre autorizado**, no una excepción a los límites.

| Límite | Antes de la aprobación | Tras la aprobación |
| --- | --- | --- |
| Commits | **0** | **1**, autorizado |
| Push de la rama `Task/005.2` | **0** — no publicada | Publicada, autorizado |
| Merge de `Task/005.2` **en `dev`** | **0** | Merge `--no-ff`, autorizado |
| Pull request de `Task/005.2` | **0** — verificado con `gh pr list --state all` | **1**, `Task/005.2 → main`, **abierto** |
| **Fusión del PR hacia `main`** | — | **NO ejecutada.** Responsabilidad exclusiva del usuario |
| Modificación directa de `main` | **0** | **0** — `main` solo cambiará al fusionar el usuario |
| `gh pr merge` | **No ejecutado** | **No ejecutado** |

Límites que se cumplen **igual antes y después** del cierre:

| Límite | Cumplimiento |
| --- | --- |
| Borrado de ramas remotas | **0** — la de `Task/005.1` ya la había eliminado el usuario |
| Recreación de `Task/005.1` | **No** |
| Cierre de `Task/005.1` | **No** — ya estaba cerrada y fusionada |
| Instalación de Floci | **No** — sin `docker pull`, sin contenedores, sin imágenes |
| Archivos Terraform | **0** en todo el workspace |
| `terraform init/plan/apply/destroy` | **No ejecutados** |
| AWS CLI contra AWS real | **No ejecutado** |
| Cuentas AWS o Cloudflare | **0 creadas** |
| Recursos cloud | **0 creados** |
| Cambios en `docker-compose.yml` | **0** |
| Cambios en `personal-blog-backend` | **0 archivos** |
| Cambios en `personal-blog-frontend` | **0 archivos** |
| `images/Infraestructura.png` | **Intacta** — blob `eaa775f`, sin modificar en ningún momento |
| Tareas del roadmap | **41**, ninguna añadida, eliminada ni renumerada |
| Avance global | **5 de 41 (12 %)** — sin cambios |
| ETAPA 02 | **1 de 3** — sin cambios |
| `Task/006` | **Pendiente, no iniciada** |
| ADR marcado como aceptado **por decisión propia** | **No.** `ADR-006` pasó a `Aceptada` **solo** por la aprobación explícita del usuario |
| **D-01** y **D-06** | **No resueltas** |
| Riesgos cerrados | **0** — **R-19** a **R-28** quedan **abiertos** |
| Secretos versionados | **0** |
| Operaciones destructivas | **0** |

---

## 14. Instrucciones de validación para el usuario

Ver [ficha §15](../tasks/TASK-005.2-document-floci-local-iac-strategy.md). Resumen mínimo:

```powershell
$env:PATH = "$env:PATH;C:\Program Files\GitHub CLI"
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

git branch --show-current                  # Task/005.2-Documentar-Estrategia-Floci-IaC-Local
git status --porcelain -b                  # 16 archivos (12 M + 4 ??), sin commit
git diff --stat main dev                   # vacio: main y dev sincronizadas
git ls-remote --heads origin "Task/*"      # vacio: sin ramas Task remotas

code docs\architecture\aws-local-parity.md
code docs\adr\ADR-006-local-aws-parity-with-floci.md
```

Ningún comando es destructivo.

---

## 15. Próxima tarea

`Task/006-Fundacion-Frontend-React` — **Pendiente, no iniciada**. No comienza hasta que el
usuario fusione el PR de `Task/005.2` y se complete la normalización `main → dev`.

---

## 16. Estado final

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Efecto en el avance** | **Ninguno.** Avance global **5 de 41 (12 %)**; ETAPA 02 **1 de 3**; `Task/006` **Pendiente** |

> La tarea quedó `Lista para validación` **sin commit, sin push, sin merge y sin PR**. El
> usuario la aprobó con la expresión exacta requerida por
> [WORKFLOW.md](../project-management/WORKFLOW.md) §3 y autorizó el flujo completo de
> cierre. Solo **entonces** se creó el commit, se integró la rama en `dev`, se publicó y se
> abrió el pull request. **La fusión del PR hacia `main` sigue siendo responsabilidad
> exclusiva del usuario y no se ejecutó.**
