# TASK-025 — Terraform Cloud

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/025-Terraform-Cloud` |
| **Nombre** | Terraform portable con laboratorio AWS local |
| **Etapa** | ETAPA 08 — Preparación Cloud + AWS Local Parity |
| **Estado** | **Aprobada** el 2026-09-14 por el usuario mediante `approved: Task/025-Terraform-Cloud`. La aprobación **incluye expresamente** las dos excepciones humanas: la del laboratorio para **H-025-1** (criterio 7) y la temporal de S-09 (**H-025-6**, **H-025-7**) |
| **Repositorios involucrados** | `personal-blog-infra` (único modificado) · `personal-blog-backend` y `personal-blog-frontend` **solo lectura** |
| **Dependencias** | `Task/022` ✔ · `Task/024` ✔ (ambas **Aprobadas**) |
| **Rama** | `Task/025-Terraform-Cloud` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | `c25642b8e4a7a06375a080a3f3cdf2512f5514d8` |
| **Fecha de inicio** | 2026-09-13 |
| **Última actualización** | 2026-09-14 |

> **Las decisiones de esta ficha quedaron APROBADAS el 2026-09-14.** Versiones, **D-06**,
> los valores de laboratorio y el *stage* local pasan de **Propuesta — pendiente de
> aprobación** a **Aceptadas y Vigentes**. Lo que la aprobación **no** convierte en hecho
> de AWS real sigue escrito donde estaba: el laboratorio es hipótesis hasta la ETAPA 10
> (ADR-006), y **D-11**, **D-12** y **D-13** siguen **abiertas**.
>
> **S-09 ya está decidido.** El 2026-09-14 el usuario autorizó una excepción **temporal y
> limitada** de **79 identidades** — 70 del emulador, ligadas a su digest exacto, y 9 de
> Terraform 1.16.2 `linux_amd64` —, registrada en el baseline canónico y revalidada con prueba
> positiva y ocho controles negativos. **H-025-6** y **H-025-7** dejan de ser bloqueantes.
>
> **No** se declaran resueltos: el riesgo sigue enumerado, el residual de cobertura del binario
> nativo del emulador sigue **vivo**, y cada entrada lleva sus condiciones de reevaluación.
> Detalle: [reporte](../task-reports/TASK-025-report.md) §15 quater.
>
> **H-025-1 también quedó decidido el 2026-09-14.** El usuario autorizó aceptar la divergencia
> del criterio **7** como **excepción explícita del laboratorio local**. Deja de ser bloqueante
> — y **no** significa que Terraform sea idempotente en Floci sin excepciones, ni que el
> criterio 7 sea un PASS literal, ni que el emulador reproduzca AWS (§6.1).

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | Resultado |
| --- | --- | --- |
| 1 | `main == origin/main` | ✔ `c25642b8e4a7a06375a080a3f3cdf2512f5514d8` en ambas |
| 2 | Working tree limpio antes de crear la rama | ✔ `git status --porcelain` vacío |
| 3 | Rama creada **desde `main`** | ✔ `git switch -c` sobre `main` |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | ✔ ambos `c25642b8…` |
| 5 | `dev` **no** es ancestro de `HEAD` | ✔ comprobado explícitamente |

Estado heredado verificado al iniciar, sin confiar en la transcripción previa:

| Repositorio | `main` | `dev` | Árbol | Rama Task |
| --- | --- | --- | --- | --- |
| `personal-blog-infra` | `c25642b8…` = `origin/main` | `e990d774…` = `origin/dev` | limpio | creada aquí |
| `personal-blog-backend` | `4a40364b…` | `8f0bf664…` | limpio | **no se crea** |
| `personal-blog-frontend` | `7dce98af…` | — | limpio | **no se crea** |

---

## 1. Objetivo

Entregar **una sola definición de Terraform** —provider oficial `hashicorp/aws`, un único
grafo de recursos— capaz de apuntar al laboratorio AWS local y, más adelante, a AWS real; y
**ejecutarla de verdad** en el laboratorio: `init`, `plan`, `apply`, pruebas funcionales,
idempotencia, `destroy`, verificación de ausencia, reconstrucción y segundo `destroy`,
**sin crear un solo recurso AWS real**.

## 2. Contexto

`Task/023` entregó el adaptador `app.lambda_handler.handler` y `Task/024` el ZIP
reproducible. La ETAPA 08 se comprometía originalmente solo a `terraform fmt` y
`validate` —sintaxis, no comportamiento—;
[ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**) amplió el alcance a
ejecutar la IaC contra un emulador local.

El camino crítico del proyecto —**Terraform + API Gateway v2 + Lambda + CloudWatch Logs**—
**no está cubierto por la suite oficial de compatibilidad del emulador**
([aws-local-parity.md](../architecture/aws-local-parity.md) §6.8, riesgo **R-25**).
Demostrarlo es el objetivo central de esta tarea.

Aquí se resuelve **D-06** (backend de estado de Terraform) — como **propuesta** hasta la
aprobación.

## 3. Dentro del alcance

- [x] Fuentes Terraform únicas en `terraform/`, con módulos compartidos por ambos destinos.
- [x] `versions.tf` con `required_version` y `required_providers` **exactos**.
- [x] `.terraform.lock.hcl` **versionado**, para `windows_amd64` y `linux_amd64`.
- [x] Corregir `.gitignore`, que hoy ignora el lock.
- [x] Recursos: S3 (medios), SSM, IAM, CloudWatch Logs, Lambda, API Gateway HTTP API v2.
- [x] Laboratorio Compose **separado** del Compose ordinario del blog.
- [x] Guardas *fail-closed* con controles negativos, antes de cualquier `plan`.
- [x] Lanzador Python que prepara **solo** la configuración de `init`/backend.
- [x] Consumo del ZIP de `Task/024` por **ruta explícita**, con hash congelado.
- [x] Ciclo completo ejecutado de verdad, incluida reconstrucción.
- [x] Matriz de paridad rellenada **con evidencia real**.
- [x] **D-06** resuelta documentalmente (como propuesta).
- [x] CI Infra ampliado con gates Terraform reales.
- [x] Auditoría Criterion12 de contradicciones heredadas.

> **Marcar estas casillas describe lo ENTREGADO, no una aprobación.** Los criterios
> de salida de la ETAPA 08 **no** se marcan aquí: eso pertenece al cierre aprobado
> ([`WORKFLOW.md`](../project-management/WORKFLOW.md) §8).

## 4. Fuera del alcance

| Queda fuera | Dónde corresponde |
| --- | --- |
| Cualquier recurso AWS real, cuenta AWS o credencial real | ETAPA 09 / ETAPA 10 |
| Runbook operativo completo de *drift*, *rollback*, recuperación y `destroy` | **`Task/026`** |
| `plan`/`apply`/`destroy` automatizados en GitHub Actions | **`Task/039`** |
| Dimensionar Lambda con mediciones reales (**D-12**) | **`Task/032`** |
| Retención definitiva de CloudWatch (**D-11**) | **`Task/031`** |
| Decidir *stage* y *base path* productivos | **`Task/033`** |
| Recursos RDS (ADR-007: PostgreSQL vive en VPS externo) | **`Task/029`** |
| Bucket de backups del VPS | **`Task/029`** / **`Task/030`** |
| Lectura de SSM **desde la aplicación** (hoy no existe) | tarea futura, no se inventa aquí |
| Verificar **mínimo privilegio** IAM | **AWS-only** — `Task/028`, `Task/032` |
| **Aceptar** el residual de seguridad del emulador (**H-025-6**) | Fue **decisión exclusiva del usuario**, tomada el 2026-09-14. Esta tarea lo midió y lo reportó; la aceptación la autorizó él |
| Crear el bucket de estado S3 en AWS | tarea de *bootstrap* futura |

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Fuentes Terraform | infra | `terraform/` |
| Lock del provider | infra | `terraform/.terraform.lock.hcl` |
| Lanzador y guardas | infra | `scripts/laboratorio/` |
| Fijación del runtime por digest (H-025-3) | infra | `scripts/laboratorio/runtime.py` |
| Compose del laboratorio | infra | `laboratorio/docker-compose.laboratorio.yml` |
| Pruebas del lanzador | infra | `tests/laboratorio/` |
| Ficha | infra | `docs/tasks/TASK-025-terraform-cloud.md` |
| Reporte | infra | `docs/task-reports/TASK-025-report.md` |
| Matriz de paridad rellenada | infra | `docs/architecture/aws-local-parity.md` §7 |
| **D-06** propuesta | infra | `docs/architecture/open-decisions.md` |
| CI ampliado | infra | `.github/workflows/ci-infra.yml` |

## 6. Criterios de aceptación

1. Una sola definición Terraform; **cero** módulos o recursos duplicados local/producción.
2. `terraform fmt -check -recursive` y `terraform validate` correctos.
3. `.terraform.lock.hcl` versionado con las dos plataformas; `init -lockfile=readonly` pasa.
4. Las guardas *fail-closed* rechazan **cada** control negativo de §7.2 **sin** salir a la red.
5. `terraform apply` crea los recursos contra el destino local.
6. `GET /health` **HTTP real** atravesando API Gateway v2 → Lambda → *handler* del ZIP.
7. Segundo `plan -detailed-exitcode` → **exit 0** (idempotencia).
8. `terraform destroy` elimina, y la **ausencia** se comprueba contra las APIs locales.
9. Reconstrucción completa desde cero, *smoke* repetido y segundo `destroy`.
10. Matriz de paridad con evidencia real y **sin** ninguna celda «paridad completa».
11. **Cero** recursos AWS reales y **cero** credenciales AWS reales.
12. El ejecutor **rechaza** el modo `production` durante esta tarea.

### 6.1 Resultado de la validación — **11 de 12 estrictamente**

> Los criterios de arriba se escribieron **antes** de implementar y **no se reescriben**
> para que coincidan con el resultado. Se conservan tal cual, y aquí se registra qué pasó.

| Criterio | Resultado |
| --- | --- |
| 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12 | **Cumplidos estrictamente** (11 de 12) |
| **7** | **NO SATISFECHO ESTRICTAMENTE EN FLOCI 2.0.1** |

**Criterio 7 — detalle.** El segundo `plan -detailed-exitcode` devolvió **exit 2**, no
`exit 0`. La **única** divergencia es `tags_all` de los cuatro `aws_ssm_parameter`.

| Campo | Valor |
| --- | --- |
| Resultado esperado por el criterio | `exit 0` |
| Resultado real | **`exit 2`** |
| Única divergencia | `aws_ssm_parameter.tags_all` (4 recursos) |
| Clasificación | **Diferencia demostrada del emulador / paridad parcial** |
| **NO es** | *drift* aceptado de AWS |
| Ocultación en Terraform | **Ninguna.** No se añadió `ignore_changes` **sobre las etiquetas** ni ninguna otra excepción para acomodar la divergencia. *(El módulo sí tiene un `ignore_changes` sobre `value`, decidido por otra razón y registrado en §12: no oculta esto.)* |
| Hallazgo | **H-025-1** |

Reproducido y diagnosticado con llamadas directas a la API: Floci 2.0.1 descarta las
etiquetas enviadas en `PutParameter`; `ListTagsForResource` queda vacío; `AddTagsToResource`
por separado **sí** las persiste; y otros recursos —el grupo de CloudWatch Logs— **sí**
conservan sus etiquetas por omisión. Contra AWS real `PutParameter` honra `Tags` y el plan
converge.

**Decisión humana del 2026-09-14: ACEPTADO COMO EXCEPCIÓN DEL EMULADOR.**

> El criterio **7 no se cumple literalmente** en Floci 2.0.1: el segundo plan devuelve
> **`exit 2`** por `aws_ssm_parameter.tags_all`. Floci 2.0.1 no reproduce correctamente la
> persistencia y lectura de etiquetas de SSM Parameter Store en esta ruta. La divergencia está
> **aislada a `tags_all`** y no se demostró ningún otro *drift* del grafo de recursos.
> **No** se introdujo `ignore_changes` **sobre las etiquetas** y **no** se modificó Terraform
> para esconderla.
> **AWS real sigue siendo la autoridad final** y deberá confirmar la idempotencia definitiva.
> Esta excepción aplica **únicamente** al laboratorio y **no** redefine el comportamiento
> esperado en AWS.

Lo que esta aceptación **no** dice: que Terraform sea idempotente en Floci sin excepciones,
que el criterio 7 sea un PASS literal, que Floci reproduzca AWS, ni que el problema esté
resuelto.

**El DoD lo permite** (comprobado en lectura, no supuesto):

| Dónde | Qué dice | Consecuencia |
| --- | --- | --- |
| DoD §1, criterio 1 | «Cumple todo el alcance. Cada elemento de *Dentro del alcance* está entregado» | Se refiere al **alcance** (§3), completo: 14 de 14 |
| DoD §1, criterio 4 | «el resultado se registra **tal cual, incluidos fallos**» | Registrar un criterio no satisfecho es exactamente lo que pide |
| DoD §1, nota final | «Si un criterio **no aplica**… debe declararse explícitamente con su justificación» | Se declara explícitamente |
| DoD §3, infraestructura cloud, **C-1…C-11** | **No existe** ningún criterio que exija `exit 0` en un segundo plan. **C-4** pide un plan «sin cambios **inesperados**» | La divergencia está **prevista, reproducida y diagnosticada**: no es inesperada |
| DoD §3, **C-5** | «Evidencia registrada distinguiendo emulación de validación real… **es el criterio que no debe relajarse**» | Se cumple: la limitación se declara, no se disimula |
| DoD §4, «Qué invalida una tarea» | La lista **no incluye** que un criterio propio no se cumpla literalmente | No invalida la tarea |

Por eso el estado **no** pasó a `Bloqueada` por **H-025-1**: el DoD no exige el 100 % de los
criterios propios y admite excepciones declaradas. La decisión era del usuario, y la tomó el
2026-09-14 aceptando la excepción.

### 6.2 Matriz FINAL de los 12 criterios

| # | Criterio | Resultado | Evidencia |
| --- | --- | --- | --- |
| 1 | Una sola definición, sin duplicar | **PASS literal** | 21 recursos en un solo grafo; no existen dos conjuntos por destino |
| 2 | `fmt -check -recursive` y `validate` | **PASS literal** | Ambos correctos |
| 3 | Lock versionado, dos plataformas, `readonly` | **PASS literal** | `zh:` de `linux_amd64` y `windows_amd64` iguales a los `SHA256SUMS` oficiales |
| 4 | Guardas rechazan cada control negativo sin salir a la red | **PASS literal** | 13 controles de CLI, todos `exit 1`, más la suite |
| 5 | `apply` crea los recursos | **PASS literal** | `Apply complete! Resources: 21 added` |
| 6 | `GET /health` HTTP real por API Gateway v2 → Lambda | **PASS literal** | **HTTP 200**, mismo cuerpo byte a byte que el entorno local |
| **7** | **Segundo plan `exit 0`** | **PASS PARA APROBACIÓN CON EXCEPCIÓN HUMANA DEL LABORATORIO** | Resultado real: **`exit 2`** por `aws_ssm_parameter.tags_all`. Causa demostrada: Floci 2.0.1 descarta las etiquetas enviadas en `PutParameter` —`ListTagsForResource` queda vacío, `AddTagsToResource` por separado sí las persiste y el grupo de CloudWatch Logs sí conserva las suyas—. **Sin** `ignore_changes`. **No es PASS literal** |
| 8 | `destroy` y ausencia verificada por API | **PASS literal** | Dos veces; S3, Lambda, API, Logs y SSM en 0 |
| 9 | Reconstrucción, *smoke* y segundo `destroy` | **PASS literal** | 21 recreados, `GET /health` 200, 21 destruidos |
| 10 | Matriz con evidencia real, sin «paridad completa» | **PASS literal** | 9 filas re-observadas; ese estado no existe en la matriz |
| 11 | Cero recursos y credenciales AWS reales | **PASS literal** | Guardas, perímetro y revisión |
| 12 | El ejecutor rechaza `production` | **PASS literal** | Control negativo explícito, `exit 1` |

**11 PASS literales + 1 PASS con excepción humana explícita.** Ningún FAIL.

## 7. TDD / Plan test-first

> No es una tarea de **backend funcional**: la **BACKEND TEST-FIRST LAW** (B-1…B-12) no es
> su clasificación formal y la suite del backend **no se toca**. Pero la lógica Python de
> orquestación y seguridad **sí** es lógica no trivial, así que se construye con disciplina
> `RED → GREEN → REFACTOR`.

### 7.1 Comportamientos a construir

- Resolver el **destino** de una operación y **abortar** ante cualquier indicio de que
  podría alcanzar AWS real.
- Congelar la identidad del **artefacto ZIP** y detectar que cambió entre `plan` y `apply`.
- Verificar la identidad de la **herramienta Terraform** por checksum antes de usarla.
- Verificar que el **plan** solo contiene los recursos esperados.
- Verificar la **ausencia** de recursos tras `destroy`.
- Firmar peticiones AWS (SigV4) para inspeccionar el laboratorio sin acoplarse al emulador.

### 7.2 Matriz de casos

Cerrada **antes** de implementar. Capa `guarda` = `scripts/laboratorio/destino.py`;
`artefacto` = `artefacto.py`; `herramienta` = `herramientas.py`; `plan` = `inventario.py`;
`firma` = `firma_aws.py`.

| # | Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- | --- |
| 1 | Modo local válido | `modo=local`, entorno completo y ficticio | endpoints locales | destino resuelto | guarda |
| 2 | **Modo ausente** | `modo=None` | — | **aborta** | guarda |
| 3 | **Modo desconocido** | `modo=staging` | — | **aborta** | guarda |
| 4 | **Modo production** | `modo=production` | — | **aborta**: sin autorización AWS | guarda |
| 5 | **Endpoint omitido** | falta `lambda` | resto correcto | **aborta**, nombra el servicio | guarda |
| 6 | **Endpoint externo** | `s3=https://s3.amazonaws.com` | — | **aborta** | guarda |
| 7 | **Host inesperado** | `s3=http://192.168.1.9:4566` | — | **aborta** | guarda |
| 8 | **Endpoint con userinfo** | `s3=http://u:p@127.0.0.1:4566` | — | **aborta** | guarda |
| 9 | **Endpoint sin puerto** | `s3=http://127.0.0.1` | — | **aborta** | guarda |
| 10 | **Esquema no HTTP** | `s3=ftp://127.0.0.1:4566` | — | **aborta** | guarda |
| 11 | **Credencial no ficticia** | `AWS_ACCESS_KEY_ID=AKIA…` | — | **aborta** sin imprimir el valor | guarda |
| 12 | **Secreto no ficticio** | `AWS_SECRET_ACCESS_KEY` real | — | **aborta** sin imprimir el valor | guarda |
| 13 | **Session token inesperado** | `AWS_SESSION_TOKEN` presente | — | **aborta** | guarda |
| 14 | **Perfil heredado** | `AWS_PROFILE=default` | — | **aborta** | guarda |
| 15 | **Archivos de credenciales** | `AWS_SHARED_CREDENTIALS_FILE` | — | **aborta** | guarda |
| 16 | **Web identity / SSO** | `AWS_WEB_IDENTITY_TOKEN_FILE`, `AWS_ROLE_ARN` | — | **aborta** | guarda |
| 17 | **Credenciales de contenedor** | `AWS_CONTAINER_CREDENTIALS_FULL_URI` | — | **aborta** | guarda |
| 18 | **Metadata habilitada** | `AWS_EC2_METADATA_DISABLED` ausente o `false` | — | **aborta** | guarda |
| 19 | **Endpoint de metadata** | `AWS_EC2_METADATA_SERVICE_ENDPOINT` presente | — | **aborta** | guarda |
| 20 | **Proxy externo** | `HTTPS_PROXY=http://proxy:3128` | — | **aborta** | guarda |
| 21 | **Override Terraform heredado** | `TF_CLI_ARGS_plan=-refresh=false` | — | **aborta** | guarda |
| 22 | **`AWS_ENDPOINT_URL` global externo** | apunta a AWS | — | **aborta** | guarda |
| 23 | **Región inesperada** | `AWS_REGION=eu-west-1` | lab en `us-east-1` | **aborta** | guarda |
| 24 | Entorno hijo curado | destino válido | — | solo variables de la *allowlist* | guarda |
| 25 | **Cuenta STS inesperada** | STS devuelve `123456789012` | destino válido | **aborta** | guarda |
| 26 | Cuenta STS esperada | STS devuelve `000000000000` | destino válido | continúa | guarda |
| 27 | **ZIP inexistente** | ruta que no existe | — | **aborta** | artefacto |
| 28 | ZIP descrito | ZIP válido | — | tamaño y sha256 | artefacto |
| 29 | **ZIP modificado** | cambian los bytes tras describirlo | — | **aborta** | artefacto |
| 30 | **Mismo tamaño, contenido distinto** | misma longitud, bytes distintos | — | **aborta** | artefacto |
| 31 | **Checksum de herramienta erróneo** | binario alterado | — | **aborta** | herramienta |
| 32 | Checksum correcto | artefacto oficial | — | acepta | herramienta |
| 33 | **Plan con recurso inesperado** | plan JSON con `aws_db_instance` | — | **aborta** | plan |
| 34 | **Plan con acción inesperada** | `delete` en el primer apply | — | **aborta** | plan |
| 35 | Plan conforme | solo tipos y acciones previstos | — | acepta | plan |
| 36 | **Destroy incompleto** | queda un recurso en el inventario | — | **aborta** | plan |
| 37 | **Lock sin una plataforma** | falta `windows_amd64` | — | **aborta** | herramienta |
| 38 | **Escritura concurrente** | dos ejecuciones a la vez | lock tomado | la segunda **aborta** | guarda |
| 39 | **Segundo plan con cambios** | `exit 2` | tras apply | **aborta** | plan |
| 40 | **Limpieza incompleta** | queda contenedor del laboratorio | tras bajar | **aborta** | plan |
| 41 | SigV4 canónica | petición conocida | — | firma estable y reproducible | firma |

**Ningún control negativo intenta alcanzar AWS real.** Todos usan entradas sintéticas,
temporales y destinos locales falsos; el fallo ocurre **antes** de abrir cualquier socket.

### 7.3 Tests RED esperados

| Test | Capa | Motivo de fallo esperado |
| --- | --- | --- |
| `test_modo_ausente_aborta` | guarda | el módulo no existe todavía |
| `test_modo_production_aborta` | guarda | el módulo no existe todavía |
| `test_endpoint_externo_aborta` | guarda | el módulo no existe todavía |
| `test_credencial_real_aborta_sin_filtrar_el_valor` | guarda | el módulo no existe todavía |
| `test_metadata_habilitada_aborta` | guarda | el módulo no existe todavía |
| `test_zip_modificado_aborta` | artefacto | el módulo no existe todavía |
| `test_plan_con_recurso_inesperado_aborta` | plan | el módulo no existe todavía |
| `test_lock_sin_una_plataforma_aborta` | herramienta | el módulo no existe todavía |

`RED` se demuestra ejecutando la suite **antes** de escribir la implementación y
conservando la salida en el reporte.

### 7.4 Integración necesaria

El laboratorio necesita **Docker real** —el emulador ejecuta Lambda en contenedores— y el
**ZIP real** de `Task/024`. No se sustituyen por dobles: el objetivo de la tarea es
precisamente ejecutar lo real. PostgreSQL **no** se levanta: el *smoke* del camino crítico
usa `GET /health`, que por diseño **no** consulta dependencias (`app/api/health.py`);
`/ready` sí las consultaría y queda fuera del *smoke* mínimo.

### 7.5 Casos negativos y de seguridad

Los casos 2–23, 25, 27, 29–31, 33–34, 36–40 de §7.2. Cubren el riesgo **R-24** (actuar
sobre AWS real por accidente) en sus vectores conocidos y el **R-22** (privilegio del
socket de Docker) mediante el perímetro de red.

### 7.6 Regresiones relevantes

- `tests/security/test_vulnerability_gate.py` sigue pasando sin cambios.
- Los gates existentes de CI Infra (Compose, variables, PowerShell, Python, Gitleaks,
  Trivy, S-09, baseline) **no se relajan**.
- El Compose ordinario del blog **no se modifica**: el laboratorio es un archivo aparte.

### 7.7 Impacto en costo (DoD C-10)

| Concepto | Valor |
| --- | --- |
| **Costo incurrido por esta tarea** | **Cero.** No se creó ninguna cuenta AWS ni ningún recurso real. Todo lo ejecutado corrió en Docker local |
| Precios consultados | **Ninguno, y no aplica**: sin recursos reales no hay nada que tarifar. Los precios vigentes se consultan en `Task/027` (presupuesto, **D-13**) y en `Task/029` (proveedor del VPS) |
| Herramientas | Terraform, el provider y el emulador son gratuitos. El emulador es **MIT** |

**Decisiones de esta tarea que evitan costo futuro**, tomadas a propósito y no por descuido:

| Decisión | Costo que evita en AWS real |
| --- | --- |
| Cifrado S3 con `AES256` gestionado por S3, **sin KMS** | Una clave KMS y sus peticiones |
| `use_lockfile = true` para el backend S3 futuro, **sin DynamoDB** | Una tabla dedicada solo al bloqueo |
| **HTTP API** v2 en lugar de REST API v1 | La diferencia de tarifa que ya fijó ADR-003 |
| Carga directa del ZIP, **sin bucket de despliegue** | Un bucket más |
| Retención de logs explícita de 7 días, **nunca infinita** | Almacenamiento creciendo sin límite |
| **Sin RDS** (ADR-007: PostgreSQL en VPS externo) | La instancia administrada entera |
| Sin NAT Gateway ni VPC | El cargo por hora y por GB del NAT |

Lo que esta tarea **no** dimensiona: memoria y *timeout* de Lambda (**D-12**, `Task/032`),
retención definitiva de CloudWatch (**D-11**, `Task/031`) ni el presupuesto mensual objetivo
(**D-13**, `Task/027`). Los valores de laboratorio **no** son dimensionamiento.

## 8. Plan de validación

| Criterio | Cómo se comprueba |
| --- | --- |
| 1 | Inspección del árbol: no existen dos conjuntos de recursos por destino |
| 2 | `terraform fmt -check -recursive` y `terraform validate` |
| 3 | `terraform providers lock` para ambas plataformas + `init -lockfile=readonly` |
| 4 | Suite `tests/laboratorio` con los controles negativos |
| 5 | `terraform apply` del plan guardado + inventario por API local |
| 6 | Petición HTTP real contra la URL del API, esperando 200 y el cuerpo del *handler* |
| 7 | `terraform plan -detailed-exitcode`, exigiendo exit 0 |
| 8 | `terraform destroy` + consultas a S3/SSM/IAM/Lambda/API/Logs |
| 9 | Segundo ciclo completo desde estado inicial |
| 10 | Revisión de §7 de `aws-local-parity.md` |
| 11 | Ausencia de credenciales reales: guardas + revisión + Gitleaks |
| 12 | Control negativo explícito del modo `production` |

## 9. Comandos de validación

```powershell
# Guardas y lógica del lanzador (no tocan la red)
python -m unittest discover -s tests/laboratorio -p "test_*.py" -v

# Ciclo del laboratorio (cada paso revalida el destino)
python scripts/laboratorio/laboratorio.py herramientas
python scripts/laboratorio/laboratorio.py levantar
python scripts/laboratorio/laboratorio.py ciclo --lambda-zip <ruta-al-zip>
python scripts/laboratorio/laboratorio.py bajar

# Terraform estatico, con la herramienta verificada
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform validate
```

## 10. Evidencia esperada

Versiones y checksums verificados contra la fuente oficial; digest efectivo del emulador;
`RED` y `GREEN` de la suite; rechazo de cada control negativo; salidas de `init`, `fmt`,
`validate`, `plan`, `apply`; respuesta HTTP real del camino crítico; `exit 0` del segundo
plan; `destroy` con verificación de ausencia; reconstrucción; matriz de paridad.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | El camino crítico (APIGWv2 + Lambda + Logs por Terraform) no está cubierto upstream (**R-25**) | Alto | Es el objetivo; si falla, se clasifica `AWS-only` con evidencia, **sin fabricar sustitutos** |
| 2 | Un comando del laboratorio alcanza AWS real (**R-24**) | Alto | Guardas *fail-closed* por capas, revalidadas antes de cada operación destructiva |
| 3 | Falsa sensación de paridad (**R-20**) | Alto | Vocabulario obligatorio; prohibido «paridad completa»; AWS real es la autoridad final |
| 4 | Socket de Docker (**R-22**) | Alto | Solo local, publicado en `127.0.0.1`, red de ejecución `internal` |
| 5 | El emulador resuelve el runtime Lambda por **etiqueta móvil** | Medio | **Se FIJA por digest** (H-025-3 corregido): se descarga la referencia inmutable que declara el `manifiesto.json` de `Task/024` y se asocia la etiqueta a ese contenido, verificado con el contenedor real. La etiqueta se movió el 2026-09-14 y dejó de importar |
| 6 | El emulador es una **major** posterior a la verificada por ADR-006 (1.6.0 → 2.0.1) | Medio | Se fija por digest, se revisa el CHANGELOG y toda afirmación de paridad se re-observa |
| 7 | Acumular condicionales acaba creando dos IaC (**R-26**) | Medio | Tabla cerrada de diferencias legítimas de `aws-local-parity.md` §4.4 |
| 8 | El *daemon* de Docker descarga imágenes aunque la red sea `internal` | Medio | Pre-descarga verificada antes de aislar; el ciclo no depende de descargas |

## 12. Decisiones técnicas

Todas **Aceptadas y Vigentes** desde el 2026-09-14 con la aprobación de la tarea.
Se conservan con su justificación original; ninguna se reescribió al aprobarse.

| Decisión | Alternativas | Justificación | ¿ADR? |
| --- | --- | --- | --- |
| Terraform CLI `= 1.16.2` | rango `~>`, versión anterior | Última 1.16.x; checksum y **firma GPG** verificados | No |
| `hashicorp/aws` `= 6.64.0` | `~> 6.0` | Última publicada; constraint exacta = reproducible | No |
| Emulador fijado por digest del índice OCI `2.0.1` | `latest`, `nightly` | ADR-006 §5.4 y S-10 prohíben etiquetas móviles | No |
| Laboratorio en Compose **separado** | añadirlo al Compose del blog | No contaminar el entorno ordinario con infraestructura privilegiada | No |
| Backend de estado generado **solo** para `init` | dos árboles Terraform | `-backend-config` no cambia el **tipo** de backend; el grafo sigue siendo único | No |
| **D-06**: local en disco fuera de Git; S3 privado dedicado en el futuro | Terraform Cloud, DynamoDB para *locking* | Costo cero ahora; `use_lockfile` evita una tabla nueva | No |
| Cliente AWS propio con **SigV4 de stdlib** | añadir `boto3` o AWS CLI a infra | Infra no tiene hoy **ninguna** dependencia de terceros; habla el protocolo AWS estándar, no una API del emulador | No |
| *Stage* `$default` **solo laboratorio** | *stage* nombrado | Simplifica la validación; el *stage* productivo es de `Task/033` | No |
| `memory_size = 512`, `timeout = 30` | otros valores | **Valores de laboratorio**, no dimensionamiento; **D-12** sigue abierta | No |
| Retención de logs 7 días | 1, 14, 30 | Valor de laboratorio; **D-11** sigue abierta en `Task/031` | No |
| `ignore_changes` sobre el **`value`** de `aws_ssm_parameter` | no ignorarlo; ignorar también el tipo | El valor de un parámetro **no es infraestructura**: puede rotarse fuera de Terraform —y en producción se espera que se rote— sin que eso sea *drift* que haya que revertir. Lo que Terraform posee es la **existencia** del parámetro y su **tipo**. **Afecta también a AWS real, a propósito**, y es independiente de **H-025-1**: no ignora `tags` ni `tags_all` | No |

## 13. Documentación creada o actualizada

- `docs/tasks/TASK-025-terraform-cloud.md` — esta ficha.
- `docs/task-reports/TASK-025-report.md` — reporte con evidencia real.
- `docs/architecture/aws-local-parity.md` — matriz de paridad §7 con evidencia.
- `docs/architecture/open-decisions.md` — **D-06** como propuesta de resolución.
- `docs/project-management/STATUS.md`, `ROADMAP.md`, `docs/stages/STAGE-08-cloud-ready.md`.

## 14. Archivos modificados

Se completa en el reporte, §Archivos.

## 15. Resultado de pruebas

| Prueba | Comando | Resultado |
| --- | --- | --- |
| Guardas del laboratorio | `unittest discover -s tests/laboratorio -p 'test_*.py'` | **143 tests, OK** |
| Seguridad | `unittest discover -s tests/security -p 'test_*.py'` | **40 tests, OK** — las **13** preexistentes intactas y **27** nuevas de la politica `pinned-artifact` |
| Formato | `terraform fmt -check -recursive` | **correcto** |
| Lock en solo lectura | `terraform init -backend=false -lockfile=readonly` | **correcto**; el lock no cambió |
| Validación | `terraform validate` | `Success! The configuration is valid.` |
| Ciclo completo | `laboratorio.py ciclo` | **exit 0** |
| Camino crítico | `GET /health` por API Gateway v2 | **HTTP 200**, mismo cuerpo que el entorno local |
| Idempotencia | `plan -detailed-exitcode` | **exit 2 solo** por `tags_all` de SSM — defecto del emulador demostrado |
| Controles negativos de CLI | 13 casos | **13/13 abortan** con `exit=1`, sin salir a la red |
| Coherencia de identidad (S-09) | `vulnerability_gate.py --comprobar-coherencia .` | **exit 0**: mismo `sha256` en baseline, workflow y lanzador |
| Secretos | Gitleaks 8.30.1, invocacion exacta del CI | **0 hallazgos** tras corregir **DEF-025-2** (reporte, §23.2) |

Detalle completo y evidencia literal: [reporte](../task-reports/TASK-025-report.md).
Si algo falla, se registra tal cual.

## 16. Problemas encontrados

Se completa en el reporte, §Problemas.

## 17. Pasos de validación para el usuario

```powershell
# 1. Rama y arbol
git -C personal-blog-infra branch --show-current
git -C personal-blog-infra status --porcelain

# 2. Guardas (no tocan la red)
cd personal-blog-infra
python -m unittest discover -s tests/laboratorio -p "test_*.py" -v

# 3. Terraform estatico (sin destino)
python scripts/laboratorio/laboratorio.py herramientas
```

El ciclo completo con Docker se detalla en el reporte, §Reproducción.

## 18. Deuda técnica pendiente

| Pendiente | Tarea |
| --- | --- |
| Runbook operativo de *drift*, *rollback*, recuperación y `destroy` | `Task/026` |
| Automatizar el ciclo en CI con emulador efímero | `Task/039` |
| Dimensionar Lambda (**D-12**) | `Task/032` |
| Retención definitiva de CloudWatch (**D-11**) | `Task/031` |
| *Bootstrap* real del bucket de estado en AWS | tarea de ETAPA 10 |
| Integrar el emulador en S-09 con baseline exacto (**H-025-6**) | Tras la decisión del usuario. El mecanismo existente lo admite sin crear una segunda política |
| Residual de Terraform CLI (**H-025-7**) y del runtime Lambda (**H-025-8**) | Sin aceptar; revisar al actualizar cada componente |
| Verificar mínimo privilegio IAM | `Task/028`, `Task/032` |

## 19. Próxima tarea

`Task/026-Runbooks-de-Despliegue` — procedimientos escritos de creación, validación,
*rollback*, destrucción y recuperación. **No se inicia hasta que el usuario apruebe esta.**

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | *(pendiente)* |
| **Aprobado por** | *(pendiente — solo el usuario)* |
| **Expresión de aprobación** | `approved: Task/025-Terraform-Cloud` |

> Esta sección solo se completa cuando el usuario autoriza explícitamente la aprobación.
> Claude nunca la completa por iniciativa propia.
