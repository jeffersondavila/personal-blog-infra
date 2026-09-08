# TASK-018 — Endurecimiento de Seguridad

| Campo | Valor |
| --- | --- |
| Tarea | `Task/018-Endurecimiento-de-Seguridad` |
| Estado | **Aprobada** el 2026-09-08 por el usuario |
| Fecha de cierre de implementación | 2026-09-07 |
| Inicio | 2026-09-07 |
| Etapa | 05 — Calidad y Seguridad |
| Repositorios | backend, frontend, infra |
| Dependencias | Task016 y Task017, aprobadas el 2026-09-06 |
| Reporte | [TASK-018-report.md](../task-reports/TASK-018-report.md) |

## 0. Preparación Git

Bases históricas verificadas al crear la tarea el 2026-09-07, desde `main`
actualizado y limpio, según [WORKFLOW §2.1](../project-management/WORKFLOW.md):

| Repositorio | SHA base histórico |
| --- | --- |
| backend | `77489e782c5604104e90ec20fc1c7f71561ed7c0` |
| frontend | `0f3c991213f42c66899495b97290c9ebc12a6abe` |
| infra | `4948478b5efca1b50388f6a1d5f780dbba8fabda` |

## 1. Objetivo

Endurecer las superficies del producto y del entorno local con evidencia reproducible
antes de introducir CI. Auditar dependencias, imágenes, secretos, CORS, cabeceras,
archivos y autenticación; conservar las invariantes aprobadas.

## 2. Contexto

La tarea no reabre Task017 ni rota las credenciales de Portainer. La aprobación de
Task016 y Task017 determina **17/41 — 41 %**, ETAPA 05 **2/3 — 67 %**. El saneamiento
documental de ROADMAP autorizado el 2026-09-07 corrige sus recuentos desactualizados;
no suma una aprobación ni modifica otras etapas.

Fuentes: ROADMAP, STATUS, WORKFLOW, DEFINITION_OF_DONE, BACKEND_TESTING_STRATEGY,
STAGE-05; NFR, security-boundaries, software-architecture, api-contracts y
open-decisions; fichas y reportes de Task010/011/014/015/016/017; runbooks del
entorno local y de backup/restore; código, pruebas, manifiestos y Dockerfiles reales.
Se aplica la convención de [TASK_TEMPLATE](../project-management/TASK_TEMPLATE.md).

## 3. Dentro del alcance

- [x] Auditorías puntuales de dependencias e imágenes con herramientas identificadas.
- [x] S-01: permisos reales locales de DB, almacenamiento y contenedores.
- [x] S-03: sanitización pública y preview administrativo.
- [x] S-04: CORS explícito por ambiente, sin wildcard ni apertura por defecto.
- [x] S-05/E-06: cabeceras por superficie y `X-Robots-Tag` administrativo por HTTP.
- [x] S-07/S-08/O-08: errores opacos y política de redacción con señuelos.
- [x] S-10: secretos excluidos de Git, sin exposición de valores reales.
- [x] S-11: archivos validados en servidor, tamaño y contenido adversario.
- [x] Autenticación: bloqueo, sesiones, CSRF, revocación, proxy y crecimiento de tablas.
- [x] Clasificación de R-09/10/12/15/22/36/43/44 y deudas relacionadas.

## 4. Fuera del alcance

CI y S-09 completo: Task019–021. IAM/S3 productivos: Task028/030. Dominio y borde
productivos: Task033/035. Operación de PostgreSQL productivo y D-17: Task029.
No se cambia el modelo de rendering (D-21), la política de medios públicos (D-08),
el mecanismo de sesión ni los proveedores YouTube/Vimeo. No hay scheduler residente.

## 5. Entregables

| Entregable | Repositorio | Ubicación |
| --- | --- | --- |
| Guardas de seguridad y regresiones | backend | `app/`, `tests/` |
| Política HTTP del sitio y pruebas de sanitización | frontend | configuración, `src/` |
| Hardening local y procedimientos verificables | infra | Compose, `scripts/`, runbooks |
| Evidencia, decisiones y deuda clasificada | infra | ficha, reporte y fuentes afectadas |

## 6. Criterios de aceptación

Todo el alcance debe estar probado o clasificado con owner y limitación explícitos;
ninguna decisión imprescindible pendiente permite declarar la tarea lista.
Suites completas, builds, integración real y comprobaciones HTTP; sin secretos,
sin regresiones conocidas sin resolver y Criterion12 C = 0.

## 7. TDD / Plan test-first

Matriz previa a implementación. Se amplía con los casos concretos encontrados;
una comprobación que ya pasa es evidencia de regresión, nunca RED inventado.

| Caso | Entrada / precondición | Resultado esperado | Capa |
| --- | --- | --- | --- |
| CORS autorizado | Origen explícito; petición simple y preflight de POST JSON | Origen exacto, credenciales, métodos y cabeceras explícitos | HTTP |
| CORS hostil | Origen ajeno, `null`, sufijo engañoso, método/cabecera ajenos | Sin concesión CORS; preflight rechazado | HTTP |
| Configuración CORS | Wildcard, URL con credenciales/ruta, puerto inválido | Falla al arrancar sin mostrar valores | configuración |
| CORS vacío | Lista ausente | Sin apertura; escrituras de navegador rechazadas | HTTP |
| Errores CORS | 401/403/404/422/500 desde origen permitido | Cabeceras y correlation ID presentes | HTTP |
| Cabeceras sitio | HTML público, `/admin`, `/admin/*`, assets | CSP compatible, nosniff, referrer, permisos y antiframing | HTTP real |
| Indexación | Público/sitemap/assets frente a panel y APIs | Noindex solo en superficies que no se indexan | HTTP real |
| HSTS | HTTP local frente a HTTPS productivo configurado | Ausente en HTTP; política explícita donde aplique | HTTP/configuración |
| XSS público/preview | script, eventos, javascript/data, iframe, atributos, raw HTML | Sin elementos/atributos/protocolos ejecutables; contenido benigno legible | DOM |
| Embeds | YouTube/Vimeo válidos frente a proveedor/referencia hostil | Solo hosts aprobados, funcionan bajo CSP | DOM/navegador |
| Archivos | Vacío, HTML/SVG renombrado, truncado, tipo no permitido | Rechazo antes de persistir; error sin datos internos | dominio/integración |
| Tamaño | Archivo >5 MiB; cuerpo multipart grande, con/sin Content-Length | Rechazo acotado server-side | HTTP/ASGI |
| Identidad del archivo | Extensión/MIME declarados falsos, nombre traversal | Decide contenido real; clave UUID independiente del nombre | dominio/integración |
| Redacción | Authorization, cookies múltiples, password_confirmation, tokens, secret/api_key, DSN y URL autenticada | Ningún señuelo en salida completa JSON/texto/contexto/excepciones | logging |
| Idempotencia | Aplicar redactor dos veces; diagnóstico benigno | Mismo resultado, diagnóstico y correlation ID útiles | logging |
| Errores | Excepciones HTTP/validación/no controladas con SQL/rutas/señuelos | 4xx/5xx opacos; logs redactados | HTTP |
| R-43 | Umbral, bloqueo vigente, vencimiento y concurrencia | No extiende bloqueo; mismo 401; auditoría diagnóstica | PostgreSQL |
| Sesión | Fixation, logout, replay, caducidad, cookie por ambiente | Nueva credencial; revocadas/caducadas rechazadas; atributos vigentes | PostgreSQL/HTTP |
| Proxy | X-Forwarded-For falsificado y cadena local real | Sin bypass por cabecera aportada por cliente | HTTP/infra |
| R-44 | Filas defensivas vencidas frente a sesiones/ventanas vigentes | Mecanismo operacional acotado o deuda con owner, sin proceso residente | PostgreSQL |
| Privilegio DB | Runtime sobre audit_events y DDL | Lee/inserta historial; no UPDATE/DELETE/TRUNCATE/DDL | PostgreSQL |
| Privilegio MinIO | Identidad runtime frente a bucket permitido y administración | Solo operaciones necesarias, sin administración global | MinIO |
| Contenedores | Usuario, capabilities, no-new-privileges y mounts | Restricciones verificadas sin romper sondas ni datos | Docker |
| Secretos | Archivos locales frente a índice Git/contextos de build | Exclusión demostrada, ejemplos ficticios | estática |

### RED esperado

Matriz HTTP acordada por superficie antes del cambio de servidor del sitio:

| Superficie | CSP | nosniff / referrer / permisos / antiframing | X-Robots-Tag | Cache |
| --- | --- | --- | --- | --- |
| Paginas publicas | scripts/estilos propios; API explicito; imagenes HTTP(S); YouTube nocookie/Vimeo | Si | Ausente | HTML revalidado |
| `/admin` y `/admin/*` | Misma politica del sitio | Si | noindex, nofollow | no-store |
| API publica | default-src none | Si | noindex, nofollow | Contrato del recurso |
| API administrativa, incluidos errores | default-src none | Si | noindex, nofollow | no-store |
| Sitemap XML | default-src none | Si | Ausente | Contrato del sitemap |
| Assets / robots | Misma politica del sitio | Si | Ausente | Assets con hash inmutables |

HSTS ausente en HTTP local; el borde con TLS real corresponde a Task033/034/035.
CSP no permite scripts/estilos inline ni eval. `img-src http: https:` preserva las
imagenes Markdown admitidas y los `access_url` locales; no habilita `data:` ni SVG
inline. `/docs` solo existe en desarrollo y se evalua aparte del producto.

El baseline HTTP demuestra ausencia de cabeceras y preflight `405`; la DB runtime
tiene privilegios de superusuario. Los tests de regresión precisarán cada defecto
antes de corregirlo. Se registran RED, GREEN y refactor en el reporte.

### Integración y regresiones

PostgreSQL solo contra `personal_blog_test`, con marca verificada por el harness.
MinIO solo con buckets efímeros `personal-blog-test-*`. No se ejecutan suites
concurrentes contra esa misma base. Se conservan las pruebas aprobadas y su semántica.

## 8. Plan de validación

Baseline antes de código; pruebas adversarias y controles positivos; implementación
mínima; regresión completa; build; despliegue local conservando volúmenes; HTTP real.
Auditorías puntuales antes/después; ninguna automatización de CI se introduce aquí.

## 9. Comandos de validación

Backend: `python -m ruff check .`, `python -m ruff format --check .`,
`python -m mypy`, `python -m pip check`, `python -m pytest -W error -q` con las
variables de integración del runbook. Frontend: `npm ci`, `npm run format:check`,
`npm run lint`, `npm run typecheck`, `npm run test:run`, `npm run build` con ambos
orígenes canónicos. Infra: `docker compose config --quiet` y verificaciones HTTP.
El reporte registra herramientas y comandos adicionales realmente ejecutados.

## 10. Evidencia esperada

Resultados de suites y builds, inventario de imágenes con digest, auditorías sin
valores secretos, matrices HTTP y de permisos, señuelos ausentes y controles positivos.

## 11. Riesgos

R-09/R-22: socket Docker equivale a privilegio de host, incluso con `:ro`.
R-12: backups locales sensibles sin cifrar. R-10/R-15: bases e imágenes envejecidas.
R-36: superficies textuales de redacción. R-43/R-44: bloqueo temporal y crecimiento.
R-14 y R-37 permanecen con Task020 (lock completo y paralelismo de integración).

## 12. Decisiones técnicas

**Ningún ADR nuevo, y es deliberado.** Task018 no cambia ninguna decisión aceptada: no
toca el modelo de rendering (**D-21**), ni la política de medios públicos (**D-08**), ni
el mecanismo de sesión (**D-15**), ni los proveedores de video, ni la arquitectura
cloud objetivo. Lo que hace es **implementar y comprobar** requisitos ya acordados.

Decisiones de implementación **vigentes desde la aprobación del 2026-09-08**,
dentro del alcance, reversibles y documentadas donde viven:

| Decisión | Motivo | Dónde queda |
| --- | --- | --- |
| **Dos planos de identidad** en PostgreSQL y MinIO, con el runtime limitado | Es la única forma de que **S-01** sea comprobable y no una convención de código | [security-boundaries §13.1](../architecture/security-boundaries.md), runbook §2.2 |
| **Plano administrativo explícito** para migraciones, tras el perfil `admin` de Compose | Consecuencia directa de lo anterior: si la aplicación no tiene DDL, migrar necesita un sitio propio | `docker-compose.yml`, runbook §2.2 y §6.8 |
| **Volumen de paso `/backup`** en PostgreSQL y MinIO | `docker cp` no puede leer de un `tmpfs`; sin él, el endurecimiento habría dejado inservible el respaldo de `Task/004` | `docker-compose.yml`, runbook §2 |
| **El mensaje de una excepción de validación no se refleja** al cliente; sí su ubicación | Un validador propio incrusta `str(ValueError)` en el mensaje, y ahí es donde se demostró la fuga. La ubicación es lo accionable, y el frontend no consume ese texto | `app/shared/errors/handlers.py` |
| **La redacción de una cabecera sensible consume el resto de su línea** | `Cookie: a=1; b=2` no tiene un delimitador fiable donde parar. Se elige el error seguro; en formato `json` los campos estructurados no viajan en el mensaje y sobreviven | `app/shared/logging/redaccion.py` |
| **HSTS ausente** | El entorno local sirve HTTP; anunciar HSTS ahí sería incorrecto. El borde con TLS real es `Task/033`–`Task/035` | [security-boundaries §13.3](../architecture/security-boundaries.md) |
| **`--reissue-runtime-credentials` como flag explícito** | Rotar un secreto nunca puede ser un efecto colateral de otra operación | `scripts/security/runtime_privileges.py` |

**R-09 y R-12 no se resuelven aquí, y no se disimula.** Ambos exigirían una decisión
propia —*socket proxy* y herramienta de cifrado (**D-17**)—, y esta tarea no la toma.

## 13. Documentación creada o actualizada

| Documento | Cambio |
| --- | --- |
| Esta ficha y el [reporte](../task-reports/TASK-018-report.md) | Creados por la tarea |
| [ROADMAP](../project-management/ROADMAP.md) | Saneamiento del avance de ETAPA 05 autorizado el 2026-09-07. Aprobación del 2026-09-08: **18/41 — 44 %**, ETAPA 05 **3/3 — 100 %** |
| [STATUS](../project-management/STATUS.md) | Tarea aprobada, próxima tarea, recuento de riesgos y tabla del efecto de `Task/018` sobre los riesgos vivos |
| [STAGE-05](../stages/STAGE-05-quality-security.md) | Estado de la tarea y criterios de salida de la etapa |
| [non-functional-requirements](../architecture/non-functional-requirements.md) | Alcance local de S-01/03/04/05/07/08/11 y cierre de **E-06** sin JavaScript |
| [security-boundaries](../architecture/security-boundaries.md) | Sección 13: dos planos de identidad, restricciones de contenedor, frontera HTTP y **lo que la tarea NO afirma** |
| [local-environment](../runbooks/local-environment.md) | Nueva sección **2.2**; arranque, verificación 6.8, reconstrucción desde cero, volúmenes y límites vigentes |
| [task-reports/README](../task-reports/README.md) | Índice completado: faltaban `Task/010` a `Task/017` |

## 14. Archivos modificados

**backend** — `Dockerfile`; `app/main.py`; `app/shared/security/http.py` (nuevo);
`app/shared/configuration/settings.py`; `app/shared/errors/handlers.py`;
`app/shared/logging/redaccion.py`;
`app/modules/authentication/presentation/dependencias.py`;
`app/modules/media/domain/validacion.py`;
`app/modules/media/presentation/router_admin.py`; tres suites nuevas
`tests/test_endurecimiento_{http,archivos,redaccion}.py` y un caso añadido a
`tests/integration/test_api_admin_medios.py`.

**frontend** — `Dockerfile`; `docker/nginx.conf`; `docker/nginx-main.conf` (nuevo);
`security.config.ts` y `security.config.test.ts` (nuevos); `vite.config.ts`;
`tsconfig.node.json`; `src/features/markdown/seguridad.test.tsx` (nuevo).

**infra** — `docker-compose.yml`; `.env.example`; `docker/postgres/Dockerfile` (nuevo);
`docker/traefik/Dockerfile` (nuevo); `docker/traefik/traefik.yml`;
`scripts/security/check_http.py` y `scripts/security/runtime_privileges.py` (nuevos);
`scripts/backup/New-LocalBackup.ps1`; `scripts/backup/Restore-LocalBackupTest.ps1`;
`scripts/backup/_BackupCommon.ps1`; y la documentación de §13.

## 15. Resultado de pruebas

| Suite | Resultado |
| --- | --- |
| Backend, completa con `-W error` e integración real (PostgreSQL + MinIO) | **1854 pasadas, 1 omitida** (`time.tzset` no existe en Windows), 305,87 s |
| Backend: Ruff, `ruff format --check`, MyPy, `pip check` | Verde. 312 archivos formateados; 310 comprobados por MyPy |
| Frontend, suite canónica, **ejecución final con la máquina en reposo** | **703 pasadas**, 0 fallidas, 41,16 s |
| Frontend, suite canónica, **ejecución intermedia bajo carga** | **700 pasadas, 2 fallidas** por tiempo agotado a 5000 ms |
| Frontend con `--maxWorkers=2` | **703 pasadas**, 0 fallidas |
| Frontend: `format:check`, `lint`, `typecheck`, `build`, `npm audit` | Verde; **0** vulnerabilidades |
| `pip-audit` sobre `requirements.txt` | **0** vulnerabilidades en 40 paquetes |

**Se registran las dos ejecuciones canónicas, no solo la verde.** La suite canónica falló
dos pruebas por tiempo agotado mientras la máquina estaba cargada, y pasó entera cuando
estuvo en reposo. **No es una regresión, y la evidencia es cuantitativa**: los dos archivos
implicados pasan en **4,45 s** ejecutados en aislamiento, y el tiempo de `environment`
recorre **287,09 s → 158,41 s → 69,87 s** entre las tres ejecuciones. Es contención de la
máquina, es decir **R-016-1**, que ya estaba identificado. **No se modificó ningún tiempo de
espera ni ninguna expectativa** para conseguir el verde.

## 16. Problemas encontrados

Detalle completo, con su corrección, en el reporte §D. En resumen:

1. **Las migraciones dejaron de poder ejecutarse.** Al pasar el backend a un rol sin DDL,
   el procedimiento documentado `docker compose exec backend alembic upgrade head` empezó
   a fallar con `permission denied for table alembic_version`. **Rompía `Task/008`.**
   Corregido con un plano administrativo explícito tras el perfil `admin`.
2. **El respaldo de PostgreSQL y MinIO dejó de funcionar.** `docker cp` **no sabe leer de
   un `tmpfs`**, y el endurecimiento puso `/tmp` en RAM. **Rompía `Task/004`.** Corregido
   con un volumen de paso `/backup`.
3. **La prueba de restauración fallaba al limpiar**: `docker cp` deja el archivo como
   `root` y `/tmp` tiene el bit pegajoso, así que el proceso, que ya no es `root`, no
   podía borrarlo. Corregido ejecutando esa limpieza con `-u 0`.
4. **Dos pruebas eran tautológicas.** Una no distinguía la tabla de mensajes genéricos de
   un respaldo que filtraba `exc.detail`; la otra no ejercitaba el filtro de esquema de
   la configuración de origen. Ambas reforzadas y **vueltas a mutar** para comprobarlo.
5. **Finales de línea CRLF** en `docker/nginx.conf`, contra la política del repositorio.
6. **La recuperabilidad de las identidades runtime no estaba resuelta**: si se perdía el
   archivo de credenciales, el script se detenía sin salida. Añadido
   `--reissue-runtime-credentials`, probado de extremo a extremo.

## 17. Pasos de validación para el usuario

```powershell
# 1. Entorno levantado y sano
cd personal-blog-infra
docker compose up -d --wait
docker compose ps

# 2. Cabeceras, CORS e indexacion, por HTTP real. Debe imprimir FALLOS=0
python .\scripts\security\check_http.py --base-url http://localhost:8081

# 3. Minimo privilegio real. Sin flags SOLO comprueba; codigo de salida 0
..\personal-blog-backend\.venv\Scripts\python.exe .\scripts\security\runtime_privileges.py

# 4. Las migraciones viven en el plano administrativo
docker compose --profile admin run --rm migrations alembic current   # 0003 (head)
docker compose exec backend alembic current                          # debe FALLAR

# 5. Respaldos: integridad de los cinco conjuntos
.\scripts\backup\Test-LocalBackup.ps1 -All

# 6. Suites
cd ..\personal-blog-backend
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m mypy
# La suite completa necesita las variables de integracion del runbook, seccion 9.4
cd ..\personal-blog-frontend
npm run lint
npm run typecheck
npm run build
npm audit
npx vitest run --maxWorkers=2
```

El paso 4 **debe** fallar en su segunda mitad: que la aplicación no pueda migrar es el
resultado buscado, no un defecto.

## 18. Deuda técnica pendiente

| Deuda | Por qué no se resuelve aquí | Propietario |
| --- | --- | --- |
| Escaneo de dependencias e imágenes **en CI** | Una auditoría puntual caduca; **S-09** pide automatización | `Task/019`–`Task/021` |
| **R-09**: capacidad administrativa de Portainer sobre el host | Un *socket proxy* cambia sus capacidades y exige decisión propia | Decisión pendiente; `Task/025` con **R-22** |
| **R-12**: respaldos locales sin cifrar | Herramienta y formato de cifrado son **D-17** | `Task/029` |
| **R-018-3**: imagen de MinIO sin actualizar | Servicio solo local y fuera de la arquitectura de producción; el salto exige compatibilidad comprobada de IAM y consola | Tarea propia, a planificar |
| **R-018-4**: dos *buckets* residuales de pruebas | Borrarlos es una operación destructiva sobre datos que el usuario no autorizó | Usuario; runbook §10.4 |
| **R-44**: purga de tablas de estado de autenticación | Un proceso residente contradiría el destino Lambda | `Task/029` |
| **R-46**: número de saltos de proxy de cada despliegue | Depende del borde real | `Task/033` |
| `og:image` por contenido (**B-016-1**) y rendering sin JavaScript (**B-016-2**) | Heredadas de `Task/016`; **D-08** y **D-21** siguen abiertas | `Task/030`, sin asignar |

## 19. Próxima tarea

Task019 — CI Frontend, **Pendiente, no iniciada**. Su rama nace desde `main`
actualizado y limpio tras la normalización exigida por WORKFLOW §2.1 y §6.1.

## 20. Aprobación

**Aprobada el 2026-09-08** mediante la expresión exacta del usuario
`approved: Task/018-Endurecimiento-de-Seguridad`. Avance: **18/41 — 44 %**;
ETAPA 05 **Completada, 3/3 — 100 %**. Las decisiones de implementación de §12
quedan **vigentes**; no se crea ni se promueve ningún ADR. **D-21** y **ADR-009**
conservan sus estados **Abierta** y **Propuesta**, respectivamente. Los riesgos
y límites de §18 permanecen declarados. Validaciones del cierre: reporte §X.
