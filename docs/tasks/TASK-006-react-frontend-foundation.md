# TASK-006 — Fundación del Frontend React

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/006-Fundacion-Frontend-React` |
| **Nombre** | Fundación del Frontend React |
| **Etapa** | [ETAPA 02 — Fundaciones de las Aplicaciones](../stages/STAGE-02-application-foundations.md) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-frontend` (implementación) · `personal-blog-infra` (gobierno documental) |
| **Dependencias** | `Task/004-Backups-y-Recuperacion-Local` — **Aprobada** ✔ (2026-07-31) · `Task/005-Fundacion-Backend-FastAPI` — **Aprobada** ✔ (2026-08-12) |
| **Rama** | `Task/006-Fundacion-Frontend-React` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base (frontend)** | `21cb51d8ac44d1c691c7c5d26ecf5d9e5aad957a` |
| **SHA base (infra)** | `ccc1947396565e167948a9093c1e545b9d69b3dc` |
| **Fecha de inicio** | 2026-08-18 |
| **Fecha de aprobación** | 2026-08-18 |
| **Última actualización** | 2026-08-18 — cierre aprobado |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | `personal-blog-frontend` | `personal-blog-infra` |
| --- | --- | --- | --- |
| 1 | `main == origin/main` | ✔ `21cb51d8…` | ✔ `ccc19473…` |
| 2 | Working tree limpio antes de crear la rama | ✔ | ✔ |
| 3 | Rama creada **desde `main`** | ✔ | ✔ |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | ✔ | ✔ |
| 5 | `git rev-list --count main..HEAD` == 0 | ✔ | ✔ |

`personal-blog-backend` **no** recibe rama Task: esta tarea no lo modifica.

```powershell
git fetch --prune origin
git switch main
git pull --ff-only origin main
git status --porcelain                          # vacio
git rev-parse main; git rev-parse origin/main   # deben coincidir

git switch -c Task/006-Fundacion-Frontend-React

git rev-parse HEAD; git rev-parse main          # deben coincidir
```

---

## 1. Objetivo

Establecer la base profesional del frontend: una aplicación React + TypeScript + Vite
reproducible que monta, enruta, lee su configuración de variables de entorno **validada al
arrancar**, dispone de un cliente HTTP común con un modelo de error consistente, y supera
pruebas, lint, formato, tipado y build de producción.

Es el **primer código de interfaz del proyecto**: fija la estructura sobre la que se
construirán el sitio público y el panel administrativo.

## 2. Contexto

`Task/005` dejó el backend en pie con `GET /health` y su modelo común de errores, pero el
repositorio `personal-blog-frontend` solo contenía documentación y configuración base: no
había `package.json` ni código React.

La estructura de proyecto, el manejo de configuración y la estrategia de pruebas son
difíciles de cambiar una vez que hay dominio encima
([STAGE-02](../stages/STAGE-02-application-foundations.md)): por eso se fijan antes que las
funcionalidades.

`Task/005.6` instaló la política de finales de línea (`.gitattributes`) **anticipando por
escrito** que esta tarea traería Prettier, ESLint y un `package-lock.json`. Esta ficha
respeta esa previsión.

`Task/007` integrará frontend, backend, PostgreSQL y MinIO tras el reverse proxy.

## 3. Dentro del alcance

- [x] Crear la rama `Task/006` desde `main` en `personal-blog-frontend` y en
      `personal-blog-infra`.
- [x] Proyecto React 19 + TypeScript 5.9 + Vite 8 reproducible, con versiones **fijadas sin
      rango** y `package-lock.json` versionado.
- [x] Composición clara: *bootstrap* (`main.tsx`), raíz (`App.tsx`), router e
      infraestructura compartida.
- [x] Enrutado con React Router: tabla de rutas central, ruta inicial y *fallback* 404.
- [x] Configuración de entorno tipada (`VITE_API_BASE_URL`), **validada al arrancar**
      (requisito T-01).
- [x] `.env.example` con valor ficticio y advertencia de que todo `VITE_*` es público.
- [x] Cliente HTTP común y reutilizable: URL segura, JSON, cabeceras, respuesta vacía.
- [x] Modelo de error que distingue fallo de red, respuesta HTTP no exitosa, cuerpo
      ilegible y petición mal construida, alineado con
      [api-contracts.md](../architecture/api-contracts.md) §7.
- [x] Suite de pruebas base con Vitest + Testing Library, determinista y sin red.
- [x] Lint (ESLint), formato (Prettier) y tipado estricto, con *scripts* reproducibles.
- [x] Build de producción estático y reproducible, verificado desde instalación limpia.
- [x] `README.md` y `CONTRIBUTING.md` del frontend actualizados a la realidad.
- [x] Ficha, reporte y estado de gobierno en `personal-blog-infra`.

## 4. Fuera del alcance

| Excluido | Tarea propietaria |
| --- | --- |
| Sistema de diseño, tokens y componentes | `Task/013` |
| Páginas y navegación del sitio público, SEO, 404 definitiva | `Task/014` |
| Panel administrativo y editor Markdown | `Task/015` |
| Autenticación, sesión y cookies | `Task/011`, `Task/015` |
| Consumo real del API, CORS e integración local | `Task/007` |
| Dominio funcional (artículos, reviews, videos, proyectos) | `Task/008`–`Task/012` |
| Rendimiento, caché y *code splitting* | `Task/016` |
| Docker del frontend, Traefik | `Task/007` |
| CI/CD | ETAPA 06 |
| Cloudflare Pages, DNS, despliegue | `Task/034`, `Task/037` |

**No se modificó `personal-blog-backend`.** En `personal-blog-infra` solo se tocó
documentación de gobierno de esta tarea: ni Compose, ni scripts, ni runbooks, ni Terraform,
ni ADR.

## 5. Arquitectura aplicable

- [software-architecture.md](../architecture/software-architecture.md) §4 — estructura y
  reglas de dependencia del frontend. Se crean **solo** las carpetas con contenido real
  (`app`, `pages`, `services`, `lib`, `styles`); `features`, `entities`, `components`,
  `hooks` y `assets` llegarán cuando exista comportamiento que las justifique.
- §4.3 — *solo `services` habla HTTP; ningún componente hace `fetch` directamente*. El
  cliente HTTP existe para que esa regla sea fácil de cumplir.
- §4.4 — la URL del API llega por variable de entorno en tiempo de build; **todo valor del
  build es público**.
- [api-contracts.md](../architecture/api-contracts.md) §2, §7 y §8 — `/health` fuera de
  `/api/v1`, modelo común de error y códigos HTTP admitidos.
- [non-functional-requirements.md](../architecture/non-functional-requirements.md) — T-01
  (configuración validada al arrancar), T-05 (frontend independiente de Cloudflare Pages),
  M-02 (TypeScript estricto).

## 6. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Manifiesto y lockfile | frontend | `package.json`, `package-lock.json` |
| Documento anfitrión | frontend | `index.html` |
| Configuración de build y pruebas | frontend | `vite.config.ts` |
| Configuración de TypeScript | frontend | `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json` |
| Lint y formato | frontend | `eslint.config.js`, `.prettierrc.json`, `.prettierignore` |
| Variables de entorno de ejemplo | frontend | `.env.example` |
| Punto de entrada y tipos de entorno | frontend | `src/main.tsx`, `src/vite-env.d.ts` |
| Raíz, rutas y contexto de configuración | frontend | `src/app/` |
| Páginas de fundación y 404 | frontend | `src/pages/` |
| Cliente HTTP y modelo de error | frontend | `src/services/http/` |
| Configuración tipada | frontend | `src/lib/config/env.ts` |
| Estilos globales mínimos | frontend | `src/styles/global.css` |
| Preparación de la suite | frontend | `src/test/setup.ts` |
| Documentación del repositorio | frontend | `README.md`, `CONTRIBUTING.md` |
| Ficha y reporte | infra | `docs/tasks/`, `docs/task-reports/` |

## 7. TDD / Plan test-first

> La [BACKEND TEST-FIRST LAW](../claude/PROJECT_INSTRUCTIONS.md) §14 aplica a
> `personal-blog-backend`. Esta tarea **no toca el backend**, así que la ley no la obliga.
> Aun así se siguió el ciclo test-first en el comportamiento que lo merecía, porque es
> donde estaba el riesgo real.

### 7.1 Comportamientos a construir

- La aplicación monta y el router resuelve la ruta inicial.
- Una ruta desconocida cae en la página 404 y ofrece salida.
- La configuración de entorno se lee, valida y llega al árbol de componentes.
- El cliente HTTP compone la URL, procesa una respuesta correcta y traduce cada modo de
  fallo a un error tipado.

### 7.2 Matriz de casos

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| Happy path | Ruta `/` | Configuración válida | Se renderiza la pantalla de fundación | app |
| Happy path | Ruta desconocida | — | Página 404 con enlace al inicio | app |
| Happy path | `VITE_API_BASE_URL` válida | — | `AppConfig` normalizado sin barra final | config |
| Edge | Origen con prefijo de ruta | — | El prefijo se conserva al componer la URL | services |
| Edge | `204` / `205` | — | `undefined`, sin intentar deserializar | services |
| Edge | `304` | — | **Error HTTP**, no éxito vacío | services |
| Error | Variable ausente, vacía, relativa o con esquema no admitido | — | `ConfigurationError` que nombra la variable | config |
| Error | Respuesta `4xx`/`5xx` con modelo común | — | `HttpError` con `code`, `message`, `details`, `requestId` | services |
| Error | Respuesta de error sin modelo común | — | `HttpError` utilizable, mensaje genérico | services |
| Error | `fetch` rechaza | — | `HttpError` de tipo `network` | services |
| Error | Cuerpo `2xx` no deserializable | — | `HttpError` de tipo `invalid_response` | services |
| Seguridad | Cuerpo de error con traza | — | La traza **no** aparece en el mensaje | services |
| Seguridad | Ruta absoluta a otro dominio | — | Rechazada sin llamar a `fetch` | services |
| Seguridad | Valor de configuración inválido | — | El mensaje **no** repite el valor recibido | config |
| Edge | Cancelación (`AbortError`) | — | Se propaga tal cual, no como fallo de red | services |
| Guarda | `useAppConfig` fuera del proveedor | — | Error inmediato | app |

### 7.3 Tests RED esperados

| Test | Capa | Motivo de fallo esperado |
| --- | --- | --- |
| `readAppConfig` (8 casos) | config | Módulo inexistente y después comportamiento sin implementar |
| `createHttpClient` (16 casos) | services | Ídem |
| `App` (4 casos) | app | Tabla de rutas vacía: no hay nada que renderizar |

**RED registrado en dos fases**, ambas en el reporte: primero por módulos inexistentes,
después por aserción con las firmas ya creadas (**26 fallidos / 1 pasa**).

### 7.4 Integración necesaria

**No aplica.** El comportamiento de esta tarea no depende de PostgreSQL, MinIO ni del
backend real. `fetch` se inyecta en el cliente HTTP, así que ninguna prueba toca la red:
depender del backend haría la suite frágil sin cubrir nada adicional. La integración real
entre servicios es `Task/007`.

### 7.5 Casos negativos y de seguridad

Cubiertos en la matriz: configuración inválida en cinco formas, tres modos de fallo HTTP,
no filtración de trazas del servidor, no filtración del valor de configuración recibido, y
rechazo de rutas absolutas hacia dominios ajenos.

### 7.6 Regresiones relevantes

- **`304` no es una respuesta exitosa sin cuerpo.** Defecto detectado durante la revisión
  del usuario y corregido con prueba de regresión permanente. Detalle en §16.
- **Aislamiento del DOM entre pruebas.** Sin limpieza explícita, el DOM de una prueba
  sobrevivía a la siguiente. Corregido en `src/test/setup.ts`.
- **`AbortError` no es un fallo de red.** `DOMException` no hereda de `Error`; la
  comprobación ingenua clasificaba mal toda cancelación.

## 8. Plan de validación

| Criterio | Cómo se comprueba |
| --- | --- |
| Monta, enruta y construye | Suite de pruebas + `npm run build` + *preview* real |
| Configuración validada al arrancar | Pruebas de `readAppConfig` + lectura en `main.tsx` |
| Cliente HTTP y errores | Suite de `createHttpClient`, con `fetch` inyectado |
| Calidad | `lint`, `typecheck`, `format:check`, `test:coverage`, `build` |
| Reproducibilidad | `npm ci` en directorio temporal + cadena *fail-fast* + hash del `dist` |
| Sin errores de consola | Chrome *headless* por CDP sobre el build real, en `/` y en una ruta 404 |
| Sin secretos | Escaneo de patrones sobre los archivos nuevos y sobre `dist/` |

## 9. Comandos de validación

```bash
# En personal-blog-frontend
npm ci
npm run lint
npm run typecheck
npm run format:check
npm run test:coverage
npm run build
npm run preview          # y consultar http://localhost:4173/
```

## 10. Evidencia esperada

- Los cinco *gates* con **código de salida real 0**, capturado sin tuberías que puedan
  enmascararlo.
- Suite en verde con su recuento y su cobertura.
- `dist/` con tres archivos y sin secretos, rutas locales ni archivos de prueba.
- Hash del `dist/` idéntico entre el repositorio y una instalación limpia.
- Salida del verificador de consola con `hallazgos: []` en ambas rutas.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | El cliente HTTP no tiene consumidor y podría divergir del backend real | Medio | Está probado contra el modelo de error documentado; `Task/007` lo conecta al `/health` real |
| 2 | Las versiones fijadas envejecen | Bajo | Actualización deliberada en `Task/019`; el lockfile hace el estado reproducible mientras tanto |
| 3 | `304` u otros códigos fuera de contrato mal interpretados | Bajo | Prueba de regresión permanente; el contrato manda sobre la intuición |
| 4 | La ausencia de `features/`, `entities/` y `components/` se lea como incumplimiento | Bajo | Documentado aquí y en el README: se crean cuando haya comportamiento que las justifique |

## 12. Decisiones técnicas

| Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- |
| npm como gestor | pnpm, yarn | `.gitattributes` (`Task/005.6`) ya versionaba `package-lock.json` en primer lugar | No |
| TypeScript 5.9.3 | TypeScript 7.0.2 | `typescript-eslint` declara peer `<6.1.0`: con la 7 no hay lint con tipos | No |
| jsdom 29.1.1 | jsdom 30.0.1 | La 30 exige Node `^24.15.0`; la máquina tiene 24.14.1 y emitía `EBADENGINE` | No |
| `fetch` nativo | Axios | `fetch` cubre lo necesario, no añade peso ni dependencia | No |
| Versiones sin rango | `^` | Coherente con el backend, que fija con `==` | No |
| Prettier no formatea Markdown | Formatear todo | Los tres repositorios comparten un estilo de Markdown escrito a mano; aplicarlo solo aquí los divergiría | No |
| Contexto de React para la configuración | Módulo con valor ya construido | Un valor de módulo obligaría a cada prueba a cargar `import.meta.env`: el defecto que `Task/005.6` cerró en el backend | No |
| Rutas como datos (`RouteObject[]`) | Construir el router en el módulo | La misma tabla alimenta el router de navegador y el de memoria: lo probado y lo servido no pueden divergir | No |
| `<link rel="icon" href="data:,">` | Añadir un icono real | Evita el `404` de `/favicon.ico` sin tomar una decisión visual que pertenece a `Task/013` | No |
| `304` fuera de los éxitos sin cuerpo | Mantenerlo | No es 2xx, no está en `api-contracts.md` §8 y el proyecto no hace peticiones condicionales | No |

**Ninguna decisión de esta tarea es estructural: no se crea ni se modifica ningún ADR.**

## 13. Documentación creada o actualizada

- `personal-blog-frontend/README.md` — reescrito: stack, requisitos, comandos, entorno,
  estructura real y tabla explícita de lo que aún no existe.
- `personal-blog-frontend/CONTRIBUTING.md` — §5 completada con las herramientas reales y
  las reglas de prueba.
- `docs/tasks/TASK-006-react-frontend-foundation.md` — esta ficha (nueva).
- `docs/task-reports/TASK-006-report.md` — reporte (nuevo).
- `docs/task-reports/README.md` — índice de reportes.
- `docs/project-management/STATUS.md` — estado de la tarea.
- `docs/project-management/ROADMAP.md` — estado de la tarea.
- `docs/stages/STAGE-02-application-foundations.md` — estado de la tarea.

## 14. Archivos modificados

Detalle completo en el [reporte](../task-reports/TASK-006-report.md) §N y §O. Resumen:

| Repositorio | Archivos | Acción |
| --- | --- | --- |
| `personal-blog-frontend` | 29 | 27 creados, 2 modificados |
| `personal-blog-infra` | 6 | 2 creados, 4 modificados |
| `personal-blog-backend` | 0 | **Sin cambios** |

## 15. Resultado de pruebas

| Prueba | Comando | Resultado |
| --- | --- | --- |
| Lint | `npm run lint` | **exit 0**, 0 problemas |
| Tipado | `npm run typecheck` | **exit 0** |
| Formato | `npm run format:check` | **exit 0** |
| Suite | `npm run test:coverage` | **exit 0** — 31/31 en 4 archivos |
| Build | `npm run build` | **exit 0** |
| Instalación limpia | `npm ci` + los cinco *gates* | **exit 0** en todos; `dist` byte a byte idéntico |
| Consola en `/` | Chrome *headless* (CDP) | **0 hallazgos** |
| Consola en ruta 404 | Chrome *headless* (CDP) | **0 hallazgos** |

Cobertura: *statements* 100 %, *branches* 98.36 %, *functions* 100 %, *lines* 100 %.
La única rama sin cubrir es un `details: null` en `httpError.ts`, indistinguible en la
práctica de un `details` ausente; no se persigue para redondear la cifra.

## 16. Problemas encontrados

1. **`304` declarado como éxito sin cuerpo, pero tratado como error.** El conjunto de
   estados sin cuerpo incluía `304`, mientras que el flujo evalúa `!response.ok` **antes**
   de consultarlo. `304` no es 2xx, así que la entrada era inalcanzable y describía un
   comportamiento inexistente; el reporte inicial repitió esa afirmación falsa. Se
   reprodujo con una prueba que falló, se fijó la semántica según
   [api-contracts.md](../architecture/api-contracts.md) §8 —que no declara `304`— y se
   dejó regresión permanente. Detectado por el usuario en la revisión.
2. **Fuga de aislamiento en la suite.** Con `globals: false`, Testing Library no registra
   su limpieza automática: el DOM de una prueba sobrevivía a la siguiente y una consulta
   encontraba elementos duplicados. Corregido con `cleanup()` explícito.
3. **`AbortError` clasificado como fallo de red.** `DOMException` no hereda de `Error`,
   de modo que `cause instanceof Error` era siempre falso. Detectado por su prueba.
4. **`404` de `/favicon.ico` en todas las rutas.** Solo salió a la luz al comprobar la
   consola con un navegador real; el *smoke* HTTP no podía verlo.
5. **Finales de línea CRLF en tres archivos.** Introducidos por una herramienta de edición
   que traduce saltos de línea en Windows: exactamente el problema que `.gitattributes`
   documenta. Detectados y normalizados a LF antes de cerrar.
6. **`set -e` inoperante en el shell de la sesión.** La cadena de *gates* no se detenía
   ante un fallo. Se sustituyó por comprobación explícita del código de salida, verificada
   provocando un fallo deliberado.

## 17. Pasos de validación para el usuario

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-frontend
git branch --show-current           # Task/006-Fundacion-Frontend-React
git status                          # cambios sin commit, staging vacio

npm ci
Copy-Item .env.example .env.local

npm run lint
npm run typecheck
npm run format:check
npm run test:coverage
npm run build

npm run preview                     # abrir http://localhost:4173/ y una ruta inexistente
```

En el navegador: la raíz muestra la pantalla de fundación con el origen del API
configurado; una ruta inexistente muestra la página 404 con enlace al inicio; la consola
no registra errores en ninguna de las dos.

## 18. Deuda técnica pendiente

| Deuda | Tarea |
| --- | --- |
| El cliente HTTP no tiene ningún consumidor todavía; el *bundle* lo elimina por *tree-shaking* | `Task/007` |
| No hay icono propio: `<link rel="icon" href="data:,">` es provisional | `Task/013` |
| No hay *code splitting*: el panel aún no existe, así que no hay nada que separar | `Task/015`, `Task/016` |
| Sin CI que ejecute estos *gates* automáticamente | ETAPA 06 |
| Sin pruebas de extremo a extremo | `Task/022` |

## 19. Próxima tarea

`Task/007-Integracion-Local` — integrar frontend, backend, PostgreSQL y MinIO en un único
Compose, con reverse proxy local y supervisión desde Portainer. **No se ha iniciado.** No
comienza hasta que el usuario fusione el pull request `Task/006 → main` y se complete la
normalización `main → dev`.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | 2026-08-18 |
| **Aprobado por** | jeffersondavila |
| **Expresión de aprobación** | `approved: Task/006-Fundacion-Frontend-React` |

> Esta sección solo se completa cuando el usuario autoriza explícitamente la aprobación.
> Claude nunca la completa por iniciativa propia.

El usuario autorizó la aprobación el 2026-08-18 con la expresión exacta. Con ella el avance
global pasa a **6 de 41 (15 %)** y la **ETAPA 02** a **2 de 3** tareas aprobadas.

**Ningún ADR cambia de estado.** Esta tarea no produjo decisiones estructurales: las diez
decisiones técnicas de §12 son de implementación y quedan registradas en esta ficha, no en
un ADR (ver §12, columna *¿ADR?*, con «No» en todas).
