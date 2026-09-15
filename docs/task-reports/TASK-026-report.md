# TASK-026 — Reporte de ejecución

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/026-Runbooks-de-Despliegue` |
| **Estado** | **Aprobada** el 2026-09-15 mediante `approved: Task/026-Runbooks-de-Despliegue` |
| **Etapa** | ETAPA 08 — **Completada**: 4 de 4 aprobadas (100 %) |
| **Rama** | `Task/026-Runbooks-de-Despliegue`, sólo infra |
| **Base** | `main` — `940a531827602ae04db37ddc5b15b5722500cc37` |
| **Fecha** | 2026-09-15 |
| **Avance global** | **26/41 ≈ 63 %** tras la aprobación (antes 25/41 ≈ 61 %) |

> **Aprobada por el usuario el 2026-09-15.** La aprobación promueve **D-026-A** a
> **D-026-J** a **Aceptadas y Vigentes** y los cinco runbooks a **Vigentes**, y completa la
> **ETAPA 08**. **No cambia lo que la evidencia demuestra:** ninguna observación local
> equivale a evidencia AWS, el **rollback real sigue sin ejecutarse** y todo lo visto en
> Floci sigue siendo hipótesis hasta la ETAPA 10.

---

## 1. Resultado entregado

- Cinco runbooks separados: crear, validar, rollback, destruir y recuperar.
- `--modo` pasó de implícito a obligatorio.
- R-23 valida el estado efectivo de Docker: un solo binding
  `4566/tcp -> 127.0.0.1:<puerto>`.
- R-24 se repite automáticamente antes de `init`, `plan`, `apply` y `destroy`.
- Operaciones humanas con plan guardado, lista cerrada y confirmación
  `APLICAR <sha256 completo>`; no existe `--force`.
- Inventario adicional con `boto3` cargado desde el ZIP canónico de Task/024.
- Drift controlado sobre un único SSM ficticio, con analizador que rechaza cambios
  colaterales y conserva H-025-1 como única diferencia permitida.

## 2. Contradicciones detectadas antes de implementar

| ID | Contradicción | Resolución |
| --- | --- | --- |
| C-026-1 | `destino.py` dice “sin valor por omisión”, pero el parser usaba `default="local"` | `--modo` obligatorio con regresión |
| C-026-2 | Se comprobaba la red interna, pero no todos los bindings publicados | Inspección fail-closed de Docker |
| C-026-3 | Documentos vivos mezclan Task/025 aprobada con estados/contadores anteriores | Corregir STATUS, ROADMAP y Stage 08; no tocar ficha/reporte históricos |

No hubo contradicción arquitectónica ni necesidad de reabrir Task/023, Task/024 o
Task/025.

## 3. TDD — RED → GREEN

### 3.1 Destino y perímetro

RED: 1 fallo y 6 errores. El parser aceptaba omitir `--modo` y no existía la función que
juzga los bindings.

GREEN: 22/22 pruebas focalizadas. Casos cubiertos: loopback exacto, ausencia, `0.0.0.0`,
`::`, LAN y binding auxiliar.

### 3.2 Operaciones humanas

RED: 10 errores. No existían los cinco subcomandos ni la confirmación de plan.

GREEN: 25/25 focalizadas. Sólo la frase exacta con el SHA-256 completo continúa;
`si`, `APLICAR`, SHA abreviado y `--force` abortan.

### 3.3 Drift controlado

RED: 3 errores del analizador y 1 error de `DeleteParameter`, todos por funcionalidad
ausente.

GREEN inicial: el analizador admite exclusivamente recrear la dirección SSM objetivo y
la diferencia H-025-1; rechaza otro SSM o una actualización de Lambda. La llamada SDK
usa `AmazonSSM.DeleteParameter` con el nombre exacto.

El primer ensayo real descubrió **DEF-026-2**. Al desaparecer el SSM, su ARN queda
desconocido hasta el `apply` y Terraform muestra también
`module.identidad.aws_iam_role_policy.permisos.policy` como actualización dependiente
con `after_unknown.policy = true`. El analizador abortó antes de aplicar. RED: 5/5
pruebas focalizadas fallaron porque la dependencia exacta aún no estaba modelada.
GREEN: 5/5 pasan; se admite únicamente esa dirección, tipo y atributo, sólo como
desconocido. La misma política con un valor posterior conocido continúa rechazada.

### 3.4 AWS SDK

RED: subcomando y función ausentes.

GREEN inicial: el SDK falso demostró que los seis clientes reciben exclusivamente el
endpoint loopback y que se exige el inventario esperado.

El primer ensayo real descubrió **DEF-026-1**: importar desde el ZIP permitía cargar el
código Python de `boto3`, pero `botocore` no podía abrir físicamente
`botocore/data/endpoints.json` y lanzó `DataNotFoundError`. El ciclo abortó antes de
idempotencia, drift y destroy. RED: 2 errores focalizados por la extracción ausente.
GREEN: el ZIP se extrae a un directorio temporal validando rutas, escape y enlaces;
`boto3` se importa desde allí y se purga al terminar. Las pruebas rechazan ZIP Slip y
la ejecución real usa `boto3/1.43.82` del artefacto.

## 4. Guardas efectivas

| Guarda | Conducta |
| --- | --- |
| G-01 | `--modo` obligatorio; `production` reconocido para abortar |
| G-02 | región, ocho endpoints y credenciales ficticias exactas |
| G-03 | cuenta consultada = `000000000000` |
| G-04 | proceso Terraform construido desde allowlist |
| G-05 | destino revalidado antes de cada operación protegida |
| R-23 | único binding Docker en `127.0.0.1`; sin LAN, Internet, IPv6 ni auxiliar |
| Plan humano | SHA completo, sin fuerza |
| Artefacto | hash congelado y runtime tomado del manifiesto Task/024 |

## 5. Validaciones estáticas

| Comprobación | Resultado |
| --- | --- |
| Compilación de todos los scripts Python, sin escribir caché | PASS |
| Suite del laboratorio | **162/162 PASS** |
| Suite del gate de seguridad | **40/40 PASS** |
| Total local | **202/202 PASS** |
| Coherencia del baseline Terraform | PASS — mismo SHA en baseline, CI y lanzador |
| `terraform fmt -check -recursive` / `validate` | PASS con 1.16.2 y provider 6.64.0 |
| `docker compose ... config --quiet` | PASS — exit 0 |
| AWS CLI del host | No disponible; no se instaló |
| `boto3` del host | No disponible; no se instaló |
| Estrategia SDK | Extraer temporalmente el `boto3` versionado dentro del ZIP canónico |

### 5.1 Gates finales reverificados en la revisión de cierre

La primera pasada de la revisión final invocó Compose con rutas de la raíz del
repositorio —`.env.laboratorio.example` y `docker-compose.laboratorio.yml`— y terminó en
**exit 1** con `couldn't find env file`. **No era un defecto de la tarea:** los dos
archivos viven en `laboratorio/` desde `Task/025` (**DEF-025-1**). Se corrigió la
invocación, no la estructura: no se movió ni copió nada, y el Compose no se tocó.

| Gate | Invocación | Resultado |
| --- | --- | --- |
| Compose del laboratorio | `docker compose --file laboratorio/docker-compose.laboratorio.yml --env-file laboratorio/.env.laboratorio.example config --quiet` | **exit 0** |
| Compilación Python | La del workflow: `compile(..., dont_inherit=True)` sobre `scripts/**/*.py` | **12 archivos, 0 fallos**, sin escribir caché |
| `__pycache__` versionable | `git status --porcelain` y `git check-ignore` | **0** — los cuatro directorios existentes están ignorados |
| Espacios y conflictos | `git diff --check` y `git diff --cached --check` | **exit 0** en ambos |
| Pines y baseline | Digest de Floci, runtime `python:3.12`, CLI `1.16.2` y provider `6.64.0` cruzados entre `.env.laboratorio.example`, `versions.tf`, `herramientas.py`, el workflow y el baseline | **Coherentes**; `security/vulnerability-baseline.json` **intacto** |
| Enlaces Markdown | Comprobador que vacía *fences*, código *inline* y bloques indentados antes de resolver destinos y anclas | **11 documentos, 293 destinos renderizados, 0 rotos** |
| Secretos | **Gitleaks 8.30.1**, `sha256` verificado contra el valor fijado en `Task/021`; invocación exacta del CI sobre el historial **y** `gitleaks dir` sobre el entregable | **0 hallazgos, exit 0** en ambos |

**Secretos, alcance exacto.** El historial completo —196 commits alcanzables, 6
referencias— dio **0**. Como esta tarea **no tiene commits**, el historial no ve sus
cambios, así que además se escaneó el **entregable**: los **213** archivos que
`git ls-files` y `git ls-files --others --exclude-standard` declaran, es decir el
contenido exacto que produciría un commit. También **0**.

Un `gitleaks dir` sobre el árbol físico completo devuelve 577 hallazgos, y conviene
decir dónde: **573 en `tmp/`** —el *venv* de auditoría de `Task/018`, 4,21 GB—, **2 en
`.env`** y **2 en `secrets/`**. Las tres rutas están en `.gitignore` desde antes de esta
tarea, **ninguna está versionada** y ninguna entra en el entregable. **No se inventó
ninguna exclusión, no se creó `.gitleaks.toml` y no se usó `gitleaks:allow`:** el
alcance escaneado es el mismo que el del gate canónico del CI, que opera sobre la
historia de Git y por definición tampoco contiene esas rutas.

> El comprobador de enlaces se validó contra un control negativo antes de confiar en su
> cero: sobre un documento sembrado detectó los **3** destinos rotos reales —fichero
> ausente, ancla propia inexistente y ancla inexistente en otro documento— e ignoró
> correctamente los **2** que vivían dentro de un *fence* y de código *inline*. Sin esa
> comprobación, un cero podría significar simplemente que el comprobador no mira.

## 6. Ensayo local completo

**PASS local**, con exit 0 en el ciclo final:

| Paso | Evidencia observada |
| --- | --- |
| Autoridades | Terraform `1.16.2`, provider AWS `6.64.0`, Floci `sha256:4e451c39c7bb88e3cd4f87e8fc0c25d5b47695a51185d521e2241fa00486e8eb` |
| Artefacto | 43,288,578 bytes; SHA-256 `6580410109207f330a329ee235e0424a6bb3f7d96d14f550c4605eb3d8a02841` |
| Runtime | `python:3.12@sha256:a89893d9c93a9ffbf9e35ca32d7cadc635cbf3a9aec94480c75ed07150a05daa`; el contenedor observado coincidió exactamente |
| Perímetro | un único `4566/tcp -> 127.0.0.1:4566`; cuenta STS ficticia `000000000000` |
| CREATE | plan cerrado y apply: `21 added, 0 changed, 0 destroyed` |
| VALIDATE | S3, 4 SSM, rol/política IAM, Lambda, API Gateway y Logs observados; `GET /health` = 200 con versión `0.1.0` |
| SDK | `boto3/1.43.82` encontró S3, SSM, IAM, Lambda, API Gateway v2 y Logs por endpoints loopback |
| Idempotencia | exit 2 únicamente por 4 `aws_ssm_parameter.tags_all`, diferencia H-025-1 ya aprobada; ningún otro cambio |
| Drift | ausencia API de `/blog-lab/local/storage_region`; plan exacto: 1 creación, 3 diferencias H-025-1 y 1 dependencia IAM desconocida; apply efectivo `1 added, 3 changed, 0 destroyed`; presencia final tipo `String` |
| Primer destroy | 21 destruidos; estado 0 y APIs de API Gateway, Lambda, Logs, S3 y SSM en 0 |
| RECOVER/REPEAT | reconstrucción `21 added`; segundo `GET /health` = 200 |
| Segundo destroy | 21 destruidos; estado 0 y las cinco APIs en 0 nuevamente |
| Retirada | 0 contenedores, 0 redes y 0 volúmenes del proyecto y del emulador |

Además se ejercitó una recuperación humana real tras el aborto seguro de DEF-026-2:
plan firmado `beb5761ec16a2984ae2eefd681d27c9e36a41b17d099e10d8be83aaa6ce66976`,
`1 added, 3 changed, 0 destroyed`, `/health` 200 e inventario SDK completo.

Limitación explícita: la lectura S3 anónima devolvió 200 porque Floci no aplica la
autorización S3 por omisión. Esto demuestra configuración aceptada, no privacidad,
enforcement IAM ni cifrado real; esas evidencias siguen siendo AWS-only.

## 7. Rollback

El mecanismo está implementado y documentado: `ref` aprobado anterior, worktree aislado,
reconstrucción y plan que debe actualizar Lambda.

**NO EJECUTADO — precondición ausente.** Task/024 introdujo el primer empaquetador y no
versionó un ZIP histórico. La comparación `5e1b235..4a40364` muestra que entre la versión
aprobada Task/023 y Task/024 sólo se añadió `scripts/empaquetar_lambda.py`; `app/` y las
dependencias desplegables no cambiaron. Reconstruir ese ref con el empaquetador posterior
no sería una versión operacional distinta y el plan no actualizaría Lambda. El gate
`exigir_actualizacion_de_lambda` lo rechaza; no se fingió un rollback.

## 8. Lo que el laboratorio no demuestra

- Enforcement IAM ni privacidad S3.
- Cifrado en reposo de SecureString.
- Alarmas CloudWatch.
- Endpoint público, cuotas, latencia o costos.
- Backend remoto S3, cuyo bucket no existe.
- Rollback de DB.

AWS real conserva la autoridad final en Stage 10.

## 9. Prohibiciones respetadas

- Cero cuentas, credenciales y recursos AWS reales.
- Cero cambios rastreados en backend/frontend.
- Cero segundo IaC.
- Cero commit, push, merge, PR o aprobación.
- Task/027 no iniciada.

## 10. Pasos de validación para el usuario

Reproducibles desde la raíz de `personal-blog-infra`, con la rama
`Task/026-Runbooks-de-Despliegue` activa. Los pasos 1 a 5 **no levantan nada** y no
tocan Docker; el 6 es opcional y sí crea el laboratorio local.

1. **Alcance y limpieza del árbol.**

   ```powershell
   git branch --show-current      # Task/026-Runbooks-de-Despliegue
   git status --porcelain         # 9 modificados y 8 nuevos, todos en infra
   git rev-parse HEAD; git rev-parse main   # ambos 940a5318...
   ```

2. **Compose del laboratorio.** Las rutas son `laboratorio/…`, no la raíz:

   ```powershell
   docker compose --file laboratorio/docker-compose.laboratorio.yml `
     --env-file laboratorio/.env.laboratorio.example config --quiet
   ```

   Se espera **exit 0** y ninguna salida.

3. **Suites.** 162 del laboratorio y 40 del gate de seguridad:

   ```powershell
   python -B -m unittest discover -s tests/laboratorio -p "test_*.py"
   python -B -m unittest discover -s tests/security   -p "test_*.py"
   ```

4. **Espacios y conflictos.** Debe devolver **exit 0** sin imprimir nada:

   ```powershell
   git diff --check
   ```

5. **Controles negativos, sin red y sin Docker.** Comprueban que las guardas abortan.
   Nótese que `--modo` es **global** y va **antes** del subcomando:

   ```powershell
   python -B scripts/laboratorio/laboratorio.py herramientas
   # exit 2 — "the following arguments are required: --modo"

   python -B scripts/laboratorio/laboratorio.py --modo production crear `
     --lambda-zip C:\ruta\que\no\existe.zip
   # exit 1 — "el modo 'production' esta rechazado"
   ```

   El segundo aborta **antes** de leer el ZIP, de invocar Terraform y de cualquier
   salida a la red: el destino se rechaza primero. Un ZIP inexistente basta para
   comprobarlo, y por eso el control no necesita el artefacto real.

6. **Ciclo completo (opcional, ~15 min, sólo local).** Levanta Floci, aplica, valida,
   destruye y retira. Exige escribir `APLICAR <sha256 completo del plan>`; cualquier
   otra respuesta aborta. Al terminar, `docker ps --all --filter "label=floci=true"`
   debe devolver **0** contenedores, y lo mismo redes y volúmenes.

Los cinco runbooks de `docs/runbooks/deployment-*.md` contienen los comandos exactos de
cada operación con su resultado esperado.

## 11. Deuda técnica pendiente

| ID | Deuda | Propietario |
| --- | --- | --- |
| DT-026-1 | **Rollback nunca ejecutado con una versión real.** El mecanismo existe y sus controles negativos pasan, pero no hay evidencia de una ejecución con dos artefactos distintos. Se salda la primera vez que exista una versión desplegable anterior genuina | Primera tarea posterior a `Task/024` que cambie `app/` o las dependencias desplegables |
| DT-026-2 | **Bucket S3 del backend de estado inexistente.** `D-06` está resuelta en cuanto al modelo; el *bootstrap* real no se ha hecho | ETAPA 09/10 |
| DT-026-3 | **Modo `production` bloqueado por diseño.** Requiere *bootstrap*, credenciales efímeras y autorización expresa del usuario | ETAPA 09 en adelante |
| DT-026-4 | **Privacidad S3, *enforcement* IAM y cifrado de `SecureString` sin validar.** Floci no los aplica; la lectura anónima devolvió 200 | ETAPA 10 (`Task/030`–`Task/033`) |
| DT-026-5 | **H-025-1 vigente.** El segundo `plan` sigue dando exit 2 por `aws_ssm_parameter.tags_all`; excepción humana aceptada en `Task/025`, **no** resuelta aquí y **sin** `ignore_changes` | Revisión al actualizar el emulador |
| DT-026-6 | **`tmp/` conserva el *venv* de auditoría de `Task/018`**, 4,21 GB no versionados. No afecta al entregable, pero ensucia cualquier escaneo del árbol físico | Limpieza de mantenimiento |

Riesgos vivos (**R-20**, **R-22**, **R-23**, **R-24**, **R-27**, **R-28**, **R-35**)
siguen replicados en [`STATUS.md`](../project-management/STATUS.md); esta tarea no cierra
ninguno.

## 12. Definition of Done — contraste criterio por criterio

### 12.1 Lista para validación (§1)

| # | Criterio | Resultado |
| --- | --- | --- |
| 1 | Cumple todo el alcance | **PASS** — los 9 elementos de *Dentro* entregados; los 13 criterios de aceptación de la ficha, marcados |
| 2 | No agrega funcionalidad fuera del alcance | **PASS** — 9 modificados y 8 nuevos, todos declarados como entregables; nada fuera de infra |
| 3 | El código compila cuando corresponde | **PASS** — 12/12 Python, `compose config` exit 0, `terraform validate` correcto |
| 4 | Las pruebas pasan cuando corresponde | **PASS** — 162/162 + 40/40 = **202/202** |
| 5 | La documentación está actualizada | **PASS** — STATUS, ROADMAP, Stage 08, ficha, reporte e índice de runbooks |
| 6 | No contiene secretos | **PASS** — Gitleaks 8.30.1: 0 en el historial y 0 en el entregable |
| 7 | Incluye instrucciones para validar | **PASS** — §10, más los cinco runbooks |
| 8 | Registra decisiones importantes | **PASS** — D-026-A a D-026-J, **Propuestas**; ningún ADR nuevo, porque no hay decisión arquitectónica nueva |
| 9 | Registra riesgos y deuda pendiente | **PASS** — §11 y §8; riesgos vivos ya replicados en STATUS |
| 10 | No rompe tareas aprobadas anteriormente | **PASS** — suites previas en verde, baseline intacto, H-025-1 conservada sin reinterpretarla |
| 11 | La rama Task nació de `main` | **PASS** — SHA base `940a5318…` en la ficha; `HEAD == main` |
| 12 | No persiste estado transitorio de Git/GitHub | **PASS** — las menciones a commit, push o PR declaran lo **no** hecho; las históricas de STATUS están fechadas y no se tocaron |

### 12.2 Tareas documentales (§3)

| Criterio | Resultado |
| --- | --- |
| Los documentos declarados existen y son coherentes | **PASS** — los 5 runbooks, el índice, la ficha y el reporte |
| Los enlaces relativos resuelven | **PASS** — 293 destinos renderizados, 0 rotos |
| Sin duplicación innecesaria entre repositorios | **PASS** — sólo infra; backend y frontend intactos |

### 12.3 Tareas de infraestructura cloud (§3)

| # | Criterio | Resultado |
| --- | --- | --- |
| C-1 | `fmt -check` y `validate` sin errores | **PASS** — CLI 1.16.2, provider 6.64.0 |
| C-2 | Destino explícito y verificado antes de actuar | **PASS** — `--modo` obligatorio (D-026-A); omitirlo sale 2; `production` sale 1 |
| C-3 | Guardas *fail-closed* antes de `apply`/`destroy` | **PASS** — G-01…G-05 revalidadas en cada `init`, `plan`, `apply` y `destroy`; el destino se vuelve a resolver y comparar, y un cambio aborta |
| C-4 | `plan` revisado y sin cambios inesperados | **PASS** — plan guardado, lista cerrada de tipos y confirmación `APLICAR <sha256 completo>`; sin `--force` |
| C-5 | Evidencia que distingue emulación de validación real | **PASS** — §6 y §8 marcan lo observado como **hipótesis**; **ninguna celda declara «paridad completa»** |
| C-6 | Matriz de paridad actualizada | **N/A justificado** — no se tocó ningún recurso de la matriz: el grafo de 21 recursos de `Task/025` no cambió. La matriz de **validabilidad** de la ficha §7 sí se aporta |
| C-7 | Estado de Terraform en el backend acordado (D-06) | **PASS** — estado `local` fuera del árbol de Git y fuera del emulador, como resolvió `Task/025`; no queda suelto |
| C-8 | Ningún recurso creado sin autorización | **PASS** — **cero** recursos AWS reales. Los 21 del laboratorio son locales, efímeros y quedaron destruidos |
| C-9 | Recursos realmente creados, enumerados y contrastados | **PASS** — `21 added` contra 21 planificados; tras el drift, `1 added, 3 changed`; dos `destroy` de 21 con ausencia verificada por API |
| C-10 | Impacto en costo estimado y documentado | **N/A justificado** — **0,00 USD**: no hay cuenta, recurso ni servicio AWS. El laboratorio es local y efímero. El costo real se estima en la ETAPA 09 con precios vigentes |
| C-11 | Ningún secreto versionado y ninguna credencial real contra el emulador | **PASS** — Gitleaks en 0; credenciales `test`/`test` **exigidas** por la guarda, cuenta `000000000000` comprobada contra STS, y `AWS_PROFILE`, `AWS_SESSION_TOKEN` o un endpoint externo en el entorno **abortan** |

**Ningún FAIL.** Dos criterios **N/A**, cada uno con su razón escrita. Las secciones §2 y
§4 de la Definition of Done no se invocan: no hay `approved:` del usuario, y no se
implementó funcionalidad no solicitada, ni commits, ni recursos cloud, ni secretos.

## 13. Cierre técnico

- [x] Documentos vivos actualizados: durante la ejecución sin alterar contadores; con la
      aprobación, a **26/41** y **ETAPA 08 completada**.
- [x] Ciclo real con SDK, drift, dos destroys y reconstrucción.
- [x] R-23 negativo por pruebas sin red: LAN, `0.0.0.0`, ausencia y binding auxiliar.
- [x] R-24 real: modo omitido sale 2; `production` sale 1 antes de Terraform/AWS.
- [x] Ausencia por APIs y cero residuos Docker finales.
- [x] 202/202 pruebas y gates estáticos en verde, incluidos los de §5.1.
- [x] Auditoría Git: cambios rastreados sólo en infra; backend/frontend limpios.
- [x] **Aprobada** el 2026-09-15; el cierre aprobado se ejecutó después, no antes.
