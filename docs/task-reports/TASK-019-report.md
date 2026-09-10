# TASK-019 — Reporte de CI Frontend

**Estado: Aprobada el 2026-09-08** mediante `approved: Task/019-CI-Frontend`.
Fechas de ejecución: 2026-09-08 (Guatemala) para el trabajo local;
**2026-09-09 UTC** para la ejecución remota.
[Ficha y matriz](../tasks/TASK-019-ci-frontend.md).

## A. Preflight

Participan frontend e infra, este último exclusivamente por la documentación
central exigida en WORKFLOW §2 y §6. Backend queda fuera del alcance.

Observado el 2026-09-08, después de `fetch --prune origin`, `switch main` y
`pull --ff-only origin main`: ambos árboles estaban limpios y `main` coincidía
con `origin/main`. No existía Task019 local ni remota. Se creó
`Task/019-CI-Frontend` desde `main` en ambos y se verificó inmediatamente
`HEAD == main`, cero commits adicionales y árbol limpio. Los SHA base históricos:

| Repositorio | SHA |
| --- | --- |
| frontend | `2ee153422642b8cfcf41b230bfd8ff32b5da8210` |
| infra | `4ca82210a1eef7f53f9cc654eeea2b3750d830da` |

El contenido de `main` y `origin/dev` también coincidía en ese preflight. Este
registro es histórico; el estado operativo debe consultarse en Git.

## B. Alcance reconstruido

STAGE-06 y ROADMAP asignan a Task019 lint, type-check, tests y build. README y
CONTRIBUTING añaden `format:check` a los gates frontend. NFR S-09 exige versiones
fijadas y escaneo de vulnerabilidades en CI; Task018 dejó `npm audit` del árbol
completo en cero y difirió su automatización a Task019–021.

| Criterio | Responsabilidad |
| --- | --- |
| Triggers, gates, logs, duración y fallos del frontend | Task019 |
| S-09 frontend | Task019: npm ci + npm audit del árbol completo |
| CI, lock y escaneo backend | Task020; no se toca backend |
| CI infra y escaneo de secretos de todo el historial disponible | Task021; verificación global al cerrar STAGE-06 |
| Checks Terraform | Task025 cuando cree la IaC; no checks vacíos en Task019/021 |
| Verde sobre dev en los tres repositorios | Cierres aprobados y salida global de STAGE-06 |
| Ejecución real del PR frontend | Cierre ordinario aprobado de Task019 |
| Cambio roto remoto | Criterio global conservado; requiere permiso adicional |

El propietario del escaneo histórico se deriva de la asignación explícita de
Task021, no de asumir un scanner adicional por cada repositorio. La auditoría
local de archivos versionables de esta tarea no se presenta como escaneo del
historial. No se introducen matrices, coverage threshold, E2E, Docker build,
Lighthouse, deploy, cloud, OIDC ni configuración externa de GitHub.

## C. Baseline original

Observado el 2026-09-08 en Windows: Node **24.14.1**, npm **11.11.0**. Antes de
crear el workflow se ejecutaron los comandos canónicos en secuencia, con
`CI=true` y orígenes públicos ficticios `https://api.example.test` y
`https://example.test`. No se usaron credenciales ni servicios del stack local.

| Comando | Exit | Duración del proceso | Resultado |
| --- | ---: | ---: | --- |
| `npm ci` | 0 | 36,50 s | 332 instalados, 333 auditados, 0 vulnerabilidades |
| `npm run format:check` | 0 | 8,58 s | Formato correcto |
| `npm run lint` | 0 | 53,46 s | Sin errores |
| `npm run typecheck` | 0 | 7,62 s | Sin errores |
| `npm run test:run` | 1 | 99,62 s | 702 verdes, 1 fallo, 74 archivos; Vitest 95,13 s |
| `npm run build` | 0 | 14,08 s | Artefacto generado |
| `npm audit` | 0 | 2,44 s | 0 vulnerabilidades |
| **Total** | | **222,30 s** | Se conserva el fallo, no se reemplaza por una repetición |

**Fallo preexistente — R-016-1:** el baseline quedó en **702 de 703** pruebas.
Falló `src/pages/admin/formularios.test.tsx:260`, vista previa Markdown, por
**timeout de 5000 ms**. Es el mismo caso registrado en Task018 bajo **R-016-1**.
**No se oculta, no se omite y no se sustituye por una repetición favorable.**
El tiempo agregado de preparación de entornos fue 373,09 s. **No se modificó
ningún timeout, worker ni expectativa** para obtener verde. La reproducción
posterior con Node 22 (§D) pasó entera pese a tener 455,30 s agregados de
preparación: se conserva el riesgo de sensibilidad local y **no se atribuye su
cierre a cambiar de Node**.

**Warnings:** Vite 8.2.1 avisó de los dos imports sin extensión, tanto al cargar
tests como al construir (§E). No hubo warnings de instalación/deprecación ni
avisos de ESLint o TypeScript en los logs del baseline.

Manifiestos auditados: cinco dependencias de producción y veinte de desarrollo,
todas con versión exacta. Lockfile v3 con **357 entradas** (incluida la raíz);
cada paquete tiene versión, URL resuelta e integridad. Ninguna dependencia se
añadió ni actualizó; `npm install` no se ejecutó.

| Archivo | SHA-256 conservado |
| --- | --- |
| package.json | `9776ef3fd88f7da29edf73ad88f97c63a4b441533ed8e808f7efe013ad882c3c` |
| package-lock.json | `5d36f6295f8c5e4642e3d0da20029139e9b25f42e43467458aba6aab0e7b5d2a` |

## D. Node y npm de CI

El runtime de CI es **Node 22.23.2**, el mismo parche del builder del Dockerfile,
con el npm incluido. Antes de publicar nada se reprodujeron localmente **los
mismos comandos del YAML, en el mismo orden**, con ese runtime.

Observado el 2026-09-08 con **Node 22.23.2 / npm 10.9.8**, runtime portable
oficial verificado con el SHA-256 de `SHASUMS256.txt`; sin instalación global y
sin cambiar dependencias. Las variables de build se aplicaron solo a ese paso.

| Comando | Exit | Duración |
| --- | ---: | ---: |
| `node --version` / `npm --version` | 0 / 0 | 0,03 / 0,31 s |
| `npm ci` | 0 | 39,30 s |
| `npm run format:check` | 0 | 12,89 s |
| `npm run lint` | 0 | 68,03 s |
| `npm run typecheck` | 0 | 11,52 s |
| `npm run build` | 0 | 15,20 s |
| `npm run test:run` | 0 | 108,36 s; Vitest 105,01 s |
| `npm audit` | 0 | 3,67 s |
| **Total** | | **259,31 s** |

**704 pruebas en 75 archivos, 0 fallos, 0 omisiones**, cero vulnerabilidades y
ningún aviso de Vite. Los hashes de `package.json` y del lockfile permanecieron
iguales a los de §C. **No se usó `--maxWorkers=2`** ni ningún otro ajuste de
paralelismo o de timeout.

El mismo par de versiones quedó impreso por el paso `Runtime versions` de la
ejecución remota: `v22.23.2` y `10.9.8` (§J). La coincidencia entre la
reproducción local y el runner es evidencia observada, no un supuesto.

## E. Advertencia de Vite — RED → corrección → GREEN

**Causa real.** El analizador de compatibilidad del loader `bundle` de Vite
8.2.1 detecta que `./robots.config` y `./security.config` necesitan resolución
de extensiones, que el cargador nativo ESM no realiza. El loader vigente sí
resuelve esos imports: **el aviso no era un fallo de build**, sino una
incompatibilidad declarada con el loader que Vite planea hacer predeterminado.
Node 22.23.2 puede cargar TypeScript nativamente, pero CI **conserva el loader
predeterminado**; no se migra a `native`.

**RED primero.** La prueba `vite.config.test.ts` carga el archivo real mediante
la API `loadConfigFromFile` de Vite, instala un logger propio y exige que `warn`
no se invoque. La variable de supresión `VITE_CONFIG_NATIVE_IGNORE_WARNING` se
fuerza vacía dentro de la prueba, de modo que **un entorno local no pueda ocultar
el defecto**. La advertencia no se silencia: se exige que no se produzca.

**Corrección mínima.** Dos imports terminados en `.ts` en `vite.config.ts` y
`allowImportingTsExtensions: true` en `tsconfig.node.json`, donde ya existía
`noEmit`. Es el único proyecto TypeScript afectado y no emite JavaScript. La
configuración de aplicación no cambia y el artefacto tampoco.

| Regresión | Resultado observado el 2026-09-08 |
| --- | --- |
| Antes del arreglo (RED) | 1 test fallido; `warn` llamado con los dos imports incompatibles; proceso 4,60 s |
| Después del arreglo (GREEN) | 1 test verde; proceso 2,24 s |
| Suite completa | 704 verdes en 75 archivos; ninguna omisión |
| Baseline frente al build corregido | Los 10 archivos de `dist` coinciden byte a byte por SHA-256 |

La comprobación adicional del build con `--configLoader native` se registra
junto con los controles negativos en §I. No se cambia el comportamiento HTTP,
robots, SEO ni el modelo de rendering aprobado.

## F. Diseño del workflow

Archivo funcional: `personal-blog-frontend/.github/workflows/ci-frontend.yml`.

| Elemento | Diseño y motivo |
| --- | --- |
| Nombre/job | `CI Frontend` / `Frontend quality` (`quality`) |
| Triggers | `push` y `pull_request`, sin filtros de ramas, paths ni exclusión de borradores |
| Runner | `ubuntu-24.04`, un único job sin matrix ni servicios |
| Node | `22.23.2`, mismo parche del builder Docker; npm incluido, 10.9.8 observado |
| Instalación | `npm ci`, una sola vez, sin modificar lockfile |
| Caché | setup-node `cache: npm`, `cache-dependency-path: package-lock.json`; descargas, no node_modules |
| Permisos | `contents: read`; resto no concedido |
| Credenciales checkout | `persist-credentials: false`; no necesita Git autenticado tras checkout |
| Concurrency | workflow + event_name + ref; cancela solo obsoletas del mismo grupo |
| Timeout | 10 minutos por job; medición y margen debajo |
| Variables build | `VITE_API_BASE_URL=https://api.example.test`, `VITE_SITE_BASE_URL=https://example.test` |
| Publicación de artefactos | Ninguna; es CI sin CD |

`github.ref` distingue ramas y refs de PR; `event_name` impide que push y PR de
una misma tarea se cancelen. PR distintos y main/dev tienen grupos distintos.
La clave se evalúa como dato de configuración, nunca se inserta en un shell.

**Timeout medido:** baseline Windows 222,30 s y reproducción con Node 22 de todos
los comandos 259,31 s. El límite de 600 s ofrecía **340,69 s de margen** frente a
la segunda medición, unas **2,31 veces** su duración. La ejecución remota real
resultó bastante más rápida —**76 s de job** (§J)—, de modo que el margen
observado sobre el runner fue de **524 s**, unas **7,9 veces** la duración real.
Es un límite de job; **no modifica los timeouts de las pruebas**.

**Validación del YAML antes de publicar.** `actionlint` no estaba disponible y
**no se instaló un validador arbitrario**. Se analizó el archivo con el parser
YAML ya incluido en Prettier 3.9.6 y se revisó a mano el schema usado, triggers,
permisos, SHA de las acciones, nombres reales de inputs, variables, orden de
pasos y equivalencia con los comandos locales. Esa inspección **no sustituye** la
validación del workflow por GitHub, registrada en §J.

## G. Gates

En orden, sin `continue-on-error`, filtros de tests ni comandos de resultado
incondicionalmente exitoso:

1. Versiones de Node y npm.
2. `npm ci`.
3. `npm run format:check`.
4. `npm run lint`.
5. `npm run typecheck`.
6. `npm run build` con ambos orígenes ficticios.
7. `npm run test:run`.
8. `npm audit`.

El orden build/tests es necesario: las guardas SEO y P-05 usan
`describe.skipIf(!hayBuild)`. En un checkout limpio con tests primero se omitirían.
Se preservan sus pruebas y se construye antes; no se añaden umbrales ni gates
vacíos. `typecheck` y `build` conservan los scripts oficiales aunque ambos
ejecuten `tsc --build --force`: no se cambia el contrato para ahorrar ese paso.

## H. S-09 frontend

Se automatiza el comando `npm audit` de Task018, sobre producción y desarrollo.
Su política predeterminada falla ante cualquier vulnerabilidad conocida y ante
error de consulta. STAGE-05 fija como mínimo la ausencia de críticas/altas;
mantener el comando existente, sin flags de tolerancia, preserva la comprobación
previa en cero y satisface ese mínimo. **No se inventa un umbral ni una excepción.**

La instalación usa versiones exactas e integridad del lockfile. Al registrar
la evidencia pre-aprobación, S-09 frontend estaba **implementado para revisión**
y Task019 todavía no había sido aprobada. Posteriormente el usuario la aprobó
el 2026-09-08 mediante `approved: Task/019-CI-Frontend`; S-09 frontend quedó
vigente. S-09 **global** conserva pendientes backend e infra con Task020 y
Task021. El escaneo de secretos es un control distinto y **no** un sustituto
de `npm audit`.

## I. Controles negativos LOCALES

**Estos controles se ejecutaron en la máquina local. No son ejecuciones de
GitHub Actions y no demuestran que GitHub haya rechazado un commit roto.**

Procedimiento: guardar bytes y SHA-256; aplicar una única mutación; ejecutar el
mismo comando del YAML; exigir exit no cero y diagnóstico del defecto inyectado;
restaurar en `finally`, comprobar el hash y volver a ejecutar el gate en verde.
No se publican mutaciones. Resultados observados el 2026-09-08:

| Mutación | Comando | Exit negativo / restaurado | Duración negativo / restaurado |
| --- | --- | --- | --- |
| Añadir `console.log` a `src/lib/config/env.ts` | `npm run lint` | 1 (`no-console`) / 0 | 28,57 / 28,52 s |
| Asignar número a string en el mismo archivo | `npm run typecheck` | 2 (TS2322) / 0 | 9,16 / 9,17 s |
| Invertir `toStrictEqual` de un caso válido de configuración | `npm run test:run` | 1 (assertion) / 0 | 73,28 / 73,73 s |
| Apuntar index.html a un módulo inexistente | `npm run build` | 1 (resolución Vite) / 0 | 10,19 / 10,21 s |

La suite negativa tuvo **703 verdes y exactamente 1 fallo**, en la expectativa
mutada de `src/lib/config/env.test.ts`. Tras restaurarla pasó **704/704**, 75
archivos, Vitest **72,19 s**, sin omisiones ni warnings. No se modificaron
time limits ni paralelismo para ninguna ejecución.

| Archivo restaurado | SHA-256 original = restaurado |
| --- | --- |
| `src/lib/config/env.ts` (ambas mutaciones) | `8a9fa69be14a0ecf16bcfd77c6f251bad37d9dfde11e62fdd3f7bcca1568ee82` |
| `src/lib/config/env.test.ts` | `5ce33f16d539bab312255fc196711a431b3d410f7905532bcfd3daed5331daf8` |
| `index.html` | `93cdae4bf50370efaaddfa6f7e426ea9b3e724e1b97ab95b52e927e8cc803986` |

**Compatibilidad del loader:** `npm run build -- --configLoader native` pasó con
exit 0 en 11,21 s. Sus **11 archivos** —10 en `dist` y la configuración Nginx de
cabeceras— coincidieron por SHA-256 con el build canónico previo. Esta ejecución
adicional **no cambia** el loader del workflow ni del proyecto.

## J. Ejecución real de GitHub Actions

Ejecución **real y remota**, no simulada. Observada el 2026-09-08 (Guatemala) /
**2026-09-09 UTC**:

| Campo | Valor observado |
| --- | --- |
| Run | **34305529115** |
| URL | https://github.com/jeffersondavila/personal-blog-frontend/actions/runs/34305529115 |
| Evento | `push` |
| Rama | `Task/019-CI-Frontend` |
| SHA de cabecera | `6f3a2928dc9750f056a15338fe56ed1f8d8d02b7` |
| Estado / conclusión | `completed` / **`success`** |
| Inicio → fin del run | 2026-09-09T03:01:57Z → 03:03:16Z — **79 s** |
| Inicio → fin del job | 2026-09-09T03:01:59Z → 03:03:15Z — **76 s** |
| Job | `Frontend quality`, `ubuntu-24.04`, sin matrix |

**Todos los pasos concluyeron `success`.** Duraciones derivadas de las marcas de
tiempo del log:

| # | Paso | Duración | Conclusión |
| ---: | --- | ---: | --- |
| 1 | Set up job | 0,7 s | success |
| 2 | Checkout | 1,0 s | success |
| 3 | Setup Node | 0,8 s | success |
| 4 | Runtime versions | 0,1 s | success |
| 5 | Install dependencies | 4,8 s | success |
| 6 | Check formatting | 3,2 s | success |
| 7 | Lint | 12,3 s | success |
| 8 | Type-check | 4,1 s | success |
| 9 | Production build | 4,5 s | success |
| 10 | Tests | 37,5 s | success |
| 11 | Audit dependencies (S-09) | 0,3 s | success |
| — | Post Setup Node · Post Checkout · Complete job | 4,2 / 0,2 / 0,0 s | success |

Salidas verificadas dentro del log del run:

| Comprobación | Salida real |
| --- | --- |
| Runtime | `v22.23.2` y npm `10.9.8` |
| Instalación | `added 332 packages, and audited 333 packages in 5s` |
| Pruebas | `Test Files 75 passed (75)` · `Tests 704 passed (704)` · Vitest `36.98s` |
| Auditoría | `found 0 vulnerabilities` |
| Caché | `Found in cache @ /opt/hostedtoolcache/node/22.23.2/x64`; `npm cache is not found` — caché de npm **fría** en esta primera ejecución |

Las **704 pruebas en 75 archivos** del runner coinciden exactamente con la
reproducción local de §D. El fallo del baseline (§C, R-016-1) **no se reprodujo
en el runner**; eso **no cierra R-016-1**: una única ejecución verde no basta
para declarar resuelto un fallo por sensibilidad temporal.

**Al redactarse el bootstrap, esta ejecución acreditaba únicamente el trigger
`push`.** El trigger `pull_request` estaba declarado en el YAML y solo había sido
inspeccionado. Son dos momentos distintos y no deben confundirse.

*Observado el 2026-09-09 UTC, ya durante el cierre aprobado:* el trigger
`pull_request` quedó acreditado por una ejecución real.

| Run | Evento | Origen | Conclusión |
| --- | --- | --- | --- |
| 34305529115 | `push` | rama `Task/019-CI-Frontend` | `success` |
| 34308234554 | `push` | rama `dev`, tras el merge `--no-ff` | `success` |
| 34308296565 | `pull_request` | pull request `#12` hacia `main` | `success` |

Los **dos triggers declarados en el workflow** tienen ejecución real registrada.
La de `pull_request` recorrió los mismos once pasos y terminó en verde (§P).

## K. Seguridad, permisos y logs

**Acciones.** Únicamente dos acciones oficiales, fijadas a commits de sus
repositorios reales. Observado el 2026-09-08 mediante la API de GitHub, los tags
apuntaban a objetos commit:

| Acción | Release | SHA |
| --- | --- | --- |
| actions/checkout | [v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1) | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| actions/setup-node | [v7.0.0](https://github.com/actions/setup-node/releases/tag/v7.0.0) | `820762786026740c76f36085b0efc47a31fe5020` |

Sus `action.yml` declaraban runtime interno Node 24, independiente del Node
22.23.2 que setup-node coloca para el proyecto. Se verificaron los nombres de
inputs y se leyeron las notas de ambas releases. La elección por SHA es local a
este workflow, **no** una política global nueva para otros repositorios.

**Superficie del workflow.** No hay `pull_request_target`, `workflow_run`,
permisos de escritura, secretos, registry autenticado, OIDC, environments ni
entrada de evento interpolada en `run:`. No se imprimen contextos completos,
`env`, tokens ni cabeceras. Solo se imprimen versiones y las salidas canónicas
de las herramientas. No se publican artefactos.

**Permisos efectivos en el runner.** El propio log del run declara el alcance
concedido al token: **`Contents: read`** y **`Metadata: read`**, y nada más.
Coincide con el `permissions: contents: read` del YAML; `metadata: read` es el
mínimo implícito que GitHub concede siempre.

**Revisión de los logs.** El log completo del run ocupa **48 370 bytes** en
**380 líneas**. Se revisó íntegro buscando material sensible. Resultado:

- **Ningún token, clave ni credencial en claro.** La única línea con forma de
  credencial es la cabecera temporal de `actions/checkout`,
  `http.https://github.com/.extraheader AUTHORIZATION: basic ***`, **enmascarada
  por GitHub**. El paso `Post Checkout` la retira al terminar, y
  `persist-credentials: false` impide que sobreviva al checkout.
- **Ningún valor de las variables `VITE_*`** aparece fuera de su declaración en
  el paso de build; son orígenes ficticios públicos, no secretos.
- **Un único aviso** en todo el log, y es una sugerencia de `git` sobre el nombre
  de la rama por defecto. **Ningún warning de Vite, npm, ESLint ni TypeScript.**

**Auditoría de secretos previa a publicar.** Observado el 2026-09-08: Trivy
**0.74.0**, ya disponible del trabajo de Task018, con
`fs --scanners secret --exit-code 1` sobre una copia de los archivos
versionables: **252 frontend + 135 infra = 387 archivos**, **0 hallazgos**,
exit 0. Los logs del run se sometieron al mismo escáner, también con **0
hallazgos**. Los outputs se mantuvieron fuera de los repositorios y no se
imprimieron valores. **No se escaneó ni modificó backend.**

Esta auditoría cubre archivos versionables y los logs de una ejecución. **No es
el escaneo del historial completo del repositorio**, que sigue asignado a
Task021 y al cierre global de STAGE-06.

## L. Fail-closed de las variables VITE_*

El build conserva la validación *fail-closed* introducida antes de esta tarea:
si falta un origen obligatorio, **no** produce un artefacto con un valor
inventado ni con una cadena vacía. Comprobado el 2026-09-08 con un entorno de
proceso independiente por ejecución:

| Escenario | Comando | Exit | Duración |
| --- | --- | ---: | ---: |
| `VITE_API_BASE_URL` vacía | `npm run build` | **1** | 10,15 s |
| `VITE_SITE_BASE_URL` vacía | `npm run build` | **1** | 10,05 s |
| Ambas restauradas | `npm run build` | 0 | 10,90 s |

El diagnóstico **nombra la variable ausente sin reflejar su valor**. Por eso el
workflow declara ambos orígenes en el paso de build: sin ellos, el gate fallaría
de forma correcta pero inútil. Los dos valores —`https://api.example.test` y
`https://example.test`— son **ficticios y públicos**; no son secretos, no se
resuelven contra ningún servicio real y no requieren backend, Docker ni
credenciales.

## M. Documentación

| Repositorio | Archivo | Acción |
| --- | --- | --- |
| frontend | `.github/workflows/ci-frontend.yml` | Creado |
| frontend | `vite.config.test.ts` | Creado |
| frontend | `vite.config.ts`, `tsconfig.node.json`, `CONTRIBUTING.md` | Modificados |
| infra | `docs/tasks/TASK-019-ci-frontend.md`, este reporte | Creados |
| infra | `docs/project-management/STATUS.md`, `ROADMAP.md` | Modificados |
| infra | `docs/stages/STAGE-06-continuous-integration.md` | Modificado |
| infra | `docs/architecture/non-functional-requirements.md` | Modificado |
| infra | `docs/task-reports/README.md` | Modificado |

**DEFINITION_OF_DONE.md y WORKFLOW.md permanecen intactos.** No se modifica
backend ni se incorporan al repositorio artefactos, dependencias, outputs de
scanners, logs ni archivos temporales.

**Corrección de drift documental, observada el 2026-09-08.** El resumen de
STATUS aún mostraba ETAPA 05 con 0 aprobadas y un total de 15/41 (37 %), pese a
que su vista rápida, su inventario, ROADMAP y las aprobaciones fechadas de
Task016, Task017 y Task018 ya acreditaban 18/41. Se alineó **solo ese resumen
desactualizado** con las aprobaciones existentes: ETAPA 05 **3/3** y **18/41
(44 %)**. Su distribución por estados se ajustó dentro de las mismas 41 tareas.
**No es avance de Task019 ni una aprobación nueva, y no se tocó ningún número
histórico correctamente fechado.**

**Validaciones documentales.** Observado el 2026-09-08: **7 documentos** de infra
tocados por Task019 revisados, **245 enlaces relativos** comprobados y **0 rotos**;
`git diff --check` limpio en ambos repositorios; búsqueda de patrones de secreto
sobre los archivos modificados **sin hallazgos**; ningún directorio de trabajo
temporal, artefacto de build, log ni salida de scanner versionado en ninguno de
los dos repositorios.

## N. Criterion 12

Barrido dirigido sobre **todos** los documentos que Task019 crea o modifica:
ficha, este reporte, STATUS, ROADMAP, STAGE-06, non-functional-requirements e
índice de reportes.

| Clase | Contenido | Recuento |
| --- | --- | ---: |
| **A — reglas y diseño permanentes** | Gates y su orden, runtime, instalación reproducible, permisos mínimos, caché, política *fail-closed*, reparto de responsabilidades de S-09 y del escaneo histórico. Las decisiones técnicas quedaron **vigentes** con la aprobación del 2026-09-08; antes de ella se mantuvieron como *Propuesta* | — |
| **B — hechos históricos fechados** | Preflight y SHA base, autorización de bootstrap, baseline con R-016-1, RED/GREEN de Vite, controles negativos locales, auditorías de secretos, tiempos medidos y las tres ejecuciones remotas —34305529115, 34308234554 y 34308296565— con su fecha, evento y conclusión | — |
| **C — estado transitorio de Git/GitHub persistido como vigente** | Ninguno | **0** |

Criterio de clasificación aplicado: todo enunciado sobre el estado vivo del
repositorio —existencia o ausencia de un pull request, existencia de la rama
remota, limpieza del árbol de trabajo, contenido del *staging*, SHA de `HEAD`,
publicación de una rama o «el workflow está verde ahora»— **no se escribe como
estado vigente en la documentación**. Lo observado en una fecha concreta se
redacta como hecho fechado, con su fecha explícita. El estado operativo se
consulta en vivo con `git fetch --prune`, `git ls-remote --heads origin "Task/*"`
y `gh pr list`, conforme a [WORKFLOW §6.1](../project-management/WORKFLOW.md).

**Resultado del barrido: C = 0.**

## O. Roadmap

Con la aprobación del 2026-09-08: **19/41 — 46 %**; ETAPA 05 completada
**3/3 — 100 %**; ETAPA 06 **1/3 — 33 %**.

La distribución por estados registra **0** tareas En progreso y **0** Listas para
validación, dentro de las mismas 41. Task020 y Task021 siguen **Pendientes, no
iniciadas**, y la etapa **no** está completa. No se modifican identificadores,
orden ni dependencias.

## P. Cierre aprobado y comprobaciones que quedan fuera

La aprobación del 2026-09-08 habilitó el cierre ordinario en ambos repositorios:
integración en `dev` con merge `--no-ff`, publicación de `dev` y de la rama Task,
y apertura del pull request `Task/019-CI-Frontend` hacia `main`. **El estado vivo
de ese cierre** —si el pull request sigue abierto o ya se fusionó, si la rama
remota existe y los SHA concretos— **no se escribe aquí**: se consulta con
`git fetch --prune`, `git ls-remote --heads origin "Task/*"` y `gh pr list`,
conforme a [WORKFLOW §6.1](../project-management/WORKFLOW.md).

*Observado el 2026-09-09 UTC:* el usuario fusionó manualmente los dos pull
request y eliminó las ramas Task remotas. A continuación se ejecutó la
normalización `main` hacia `dev` con merge `--no-ff` en ambos repositorios.

| Repositorio | PR | Merge commit del PR | Merge de normalización |
| --- | --- | --- | --- |
| frontend | `#12` | `7dce98a` | `b261e65` |
| infra | `#34` | `32474e5` | `efeb6b8` |

Lo siguiente **sigue sin estar cubierto por Task019** y no se declara validado:

- **Verde de los tres workflows sobre `dev`**, criterio de salida de la etapa que
  requiere también `Task/020` y `Task/021`. Task019 solo acredita el frontend.
- **Control negativo remoto.** Publicar una mutación deliberadamente rota para
  ver fallar el workflow **exige un permiso adicional** que no se ha concedido.
  Los negativos de §I siguen siendo **locales**.
- **R-016-1**, que no se cierra por ejecuciones remotas verdes aisladas.

La **autorización excepcional de bootstrap del 2026-09-08** cubrió únicamente los
commits y el push de la rama frontend antes de aprobar. **Ya fue utilizada y no
se extiende**; el resto del cierre se ampara en la aprobación ordinaria, no en
aquel permiso. No se tocaron settings, secretos, environments ni deployments de
GitHub.

## Q. Bloqueos y deuda

- **Sin bloqueos que detengan la validación.** Task019 está completa para revisión.
- **R-016-1 permanece abierto.** El baseline lo reprodujo (§C) y el runner no,
  pero una ejecución aislada verde no cierra un riesgo de sensibilidad temporal.
- **Negativo remoto no autorizado.** Publicar una mutación deliberadamente rota
  para ver fallar el workflow exige un permiso adicional del usuario. Los
  negativos de §I son **locales**.
- **S-09 global abierto:** backend en Task020, infra en Task021.
- **Escaneo del historial de secretos:** Task021 y cierre global de STAGE-06.
- **Gates de Terraform:** Task025, cuando exista IaC real. No se declaran checks
  vacíos ahora.

## R. Veredicto

**TASK019 APROBADA Y CERRADA — 2026-09-08.**

Los gates canónicos del frontend y la porción frontend de S-09 quedan
automatizados en GitHub Actions y demostrados por una ejecución remota real
(`success`, 79 s, 704 pruebas, 0 vulnerabilidades). La advertencia heredada de
Vite fue reproducida, corregida y protegida con una regresión permanente. Los
controles negativos locales acreditan que cada gate rechaza su defecto y vuelve
a verde tras restaurar. La documentación está completa y **Criterion 12 cierra
en C = 0**.

Aprobada por el usuario mediante `approved: Task/019-CI-Frontend` el 2026-09-08.
El avance tras esa aprobación fue **19/41 — 46 %** y ETAPA 06 **1/3 — 33 %**,
**no completada**. Durante el cierre aprobado se crearon los pull request
`Task/019-CI-Frontend → main` y se dejaron sin fusionar para revisión del usuario.
Su estado operativo se consulta en GitHub; la fusión manual del 2026-09-09 UTC
está registrada como observación histórica en §P. Aceptar o rechazar un PR es
responsabilidad exclusiva del usuario. **Task020 no se inició en esta tarea.**

Fuentes técnicas consultadas el 2026-09-08: documentación oficial de
[carga de configuración Vite](https://vite.dev/config/#config-loading),
[npm audit](https://docs.npmjs.com/cli/v11/commands/npm-audit/),
[checkout](https://github.com/actions/checkout) y
[setup-node](https://github.com/actions/setup-node). El código instalado de Vite
8.2.1 y los `action.yml` de los SHA citados se inspeccionaron directamente.
