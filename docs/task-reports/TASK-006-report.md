# TASK-006 — Reporte de ejecución

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/006-Fundacion-Frontend-React` |
| **Ficha** | [TASK-006-react-frontend-foundation.md](../tasks/TASK-006-react-frontend-foundation.md) |
| **Etapa** | [ETAPA 02 — Fundaciones de las Aplicaciones](../stages/STAGE-02-application-foundations.md) |
| **Estado final** | **Aprobada** ✔ (2026-08-18) |
| **Fecha** | 2026-08-18 |
| **Repositorios modificados** | `personal-blog-frontend`, `personal-blog-infra` |
| **Repositorios intactos** | `personal-blog-backend` |

> **Aprobada por el usuario el 2026-08-18** con la expresión
> `approved: Task/006-Fundacion-Frontend-React`. Con ella el avance pasa a **6 de 41 (15 %)**
> y la ETAPA 02 a **2 de 3** tareas aprobadas.
>
> El pull request `Task/006 → main` queda **abierto**: aceptarlo y fusionarlo es
> responsabilidad exclusiva del usuario. Claude **no** lo fusiona.

---

## 1. Estado inicial encontrado

| Repositorio | `main` | Working tree | Ramas Task |
| --- | --- | --- | --- |
| `personal-blog-frontend` | `21cb51d8ac44d1c691c7c5d26ecf5d9e5aad957a` | Limpio | Ninguna |
| `personal-blog-infra` | `ccc1947396565e167948a9093c1e545b9d69b3dc` | Limpio | Ninguna |
| `personal-blog-backend` | `2290a9fbb726f97f6d1cbdb5e4c6b1f1ce147e4c` | Limpio | Ninguna |

En los tres repositorios `main` coincidía con `origin/main`, `main` era ancestro de `dev` y
`git diff main dev` estaba vacío.

`personal-blog-frontend` contenía únicamente `.editorconfig`, `.gitattributes`,
`.gitignore`, `README.md` y `CONTRIBUTING.md`. **No había `package.json` ni código React.**

Ambas ramas Task se crearon **desde `main`**, con `HEAD == main` y `0` commits de
diferencia verificados inmediatamente después de crearlas.

## 2. Toolchain seleccionado

| Pieza | Versión | Por qué esa y no otra |
| --- | --- | --- |
| Node / npm | v24.14.1 / 11.11.0 | Entorno local; npm porque `.gitattributes` ya versionaba `package-lock.json` |
| React / React DOM | 19.2.8 | Exigido por el roadmap |
| TypeScript | 5.9.3 | **No la 7.0.2**: `typescript-eslint` declara peer `<6.1.0` |
| Vite | 8.2.1 | Exigido por el roadmap |
| React Router | 8.3.0 | Enrutado estándar del ecosistema |
| Vitest | 4.1.11 | Comparte configuración y transformaciones con Vite |
| jsdom | 29.1.1 | **No la 30.0.1**: exige Node `^24.15.0` y emitía `EBADENGINE` |
| ESLint | 10.8.1 | Anticipado por `.gitattributes` (`Task/005.6`) |
| Prettier | 3.9.6 | Ídem |

Versiones **fijadas sin rango**, coherente con el backend, que fija con `==`. Instalación:
252 paquetes, **0 warnings**, **0 vulnerabilidades**.

## 3. Cambios realizados

### 3.1 `personal-blog-frontend`

```
src/
├── app/          App.tsx · routes.tsx · appConfigContext.ts   (+2 archivos de prueba)
├── pages/        HomePage.tsx · NotFoundPage.tsx
├── services/     http/{httpClient,httpError,index}.ts         (+1 archivo de prueba)
├── lib/          config/env.ts                                (+1 archivo de prueba)
├── styles/       global.css
├── test/         setup.ts
├── main.tsx
└── vite-env.d.ts
```

Solo se crearon las carpetas de
[software-architecture.md](../architecture/software-architecture.md) §4.1 que ya tienen
contenido. `features/`, `entities/`, `components/`, `hooks/` y `assets/` llegarán cuando
exista comportamiento que las justifique: una carpeta vacía no documenta una decisión.

Piezas destacables:

- **Configuración validada al arrancar** (T-01). `readAppConfig` es pura: recibe la fuente
  en lugar de leer `import.meta.env`, así que ninguna prueba depende del `.env` de quien la
  ejecute. Su mensaje de error nombra la variable pero **no repite el valor recibido**, que
  podría ser una URL interna.
- **`VITE_API_BASE_URL` es el origen**, sin `/api/v1` y sin barra final: `/api/v1` versiona
  el contrato, pero `/health` vive fuera de ese prefijo a propósito
  ([api-contracts.md](../architecture/api-contracts.md) §2).
- **Rutas como datos.** `routes.tsx` exporta un `RouteObject[]`; producción usa
  `createBrowserRouter` y las pruebas `createMemoryRouter` sobre la misma tabla.
- **Cliente HTTP con `fetch` inyectable.** Rechaza rutas absolutas hacia otros dominios y
  propaga `AbortError` sin disfrazarlo de fallo de red.
- **`HttpError` no filtra el cuerpo crudo** de la respuesta al mensaje; la excepción
  original queda en `cause`.

### 3.2 `personal-blog-infra`

Solo documentación de gobierno de esta tarea. **No se tocó** Compose, scripts, runbooks,
arquitectura productiva, ADR ni Terraform.

## 4. Validaciones ejecutadas

### 4.1 Ciclo test-first

| Fase | Resultado real |
| --- | --- |
| **RED-1** | Pruebas escritas primero: 3 archivos fallan, `no tests` — `Failed to resolve import "./env"`, `"./httpError"`, `"./httpClient"` |
| **RED-2** | Con las firmas creadas pero sin comportamiento: **26 fallidos / 1 pasa (27)** |
| **GREEN** | Tras implementar: **27/27**; **31/31** con las regresiones añadidas después |

### 4.2 Quality gates — códigos de salida reales

Capturados **sin tubería**, ejecutando cada *gate* y leyendo `$?` inmediatamente. La
ejecución previa usaba `npm run <gate> | tail -3`, que devuelve el código de `tail` y puede
enmascarar un fallo.

| Gate | Comando | Exit code real |
| --- | --- | --- |
| Lint | `npm run lint` | **0** |
| Tipado | `npm run typecheck` | **0** |
| Formato | `npm run format:check` | **0** |
| Pruebas | `npm run test:coverage` | **0** |
| Build | `npm run build` | **0** |

Suite: **31 pruebas, 31 pasadas, 0 fallidas**, en 4 archivos.
Cobertura: *statements* **100 %** (72/72), *branches* **98.36 %** (60/61), *functions*
**100 %** (19/19), *lines* **100 %** (72/72).

### 4.3 Instalación limpia con *fail-fast* real

Copia del árbol a un directorio temporal, `npm ci` y los cinco *gates* encadenados,
deteniéndose ante el primer fallo.

| Paso | Exit code real |
| --- | --- |
| `npm ci` | **0** — 252 paquetes, 0 warnings, 0 vulnerabilidades |
| `lint` → `typecheck` → `format:check` → `test:coverage` → `build` | **0** en los cinco |

El `dist/` resultante es **byte a byte idéntico** al del repositorio (mismo SHA-256 en los
tres archivos): el build es reproducible.

El mecanismo de *fail-fast* se verificó provocando un fallo deliberado: la cadena se detuvo
en `format:check` con código 1 y **no ejecutó** `test:coverage` ni `build`.

### 4.4 Build e inspección del artefacto

`dist/` contiene tres archivos: `index.html` (0.39 kB), un CSS (0.37 kB) y un JS (282.34 kB;
89.89 kB comprimido).

Escaneo: **0 coincidencias** de `C:\Users`, `/Users/…`, `node_modules`, `SECRET`,
`PASSWORD`, `TOKEN`, `AKIA`, `ghp_` ni claves privadas. **0** archivos de prueba y **0**
*sourcemaps*.

> **El cliente HTTP no aparece en el bundle.** Ningún módulo del grafo de la aplicación lo
> importa todavía, así que Rollup lo elimina por *tree-shaking*. Es lo esperado en esta
> tarea —`Task/006` no debe inventar endpoints— y explica que el hash del `dist` no cambie
> al corregir el cliente. `Task/007` lo conectará al `/health` real.

### 4.5 Consola del navegador

Comprobado con **Chrome 151 en modo *headless*** sobre el build real servido por
`vite preview`, mediante el Chrome DevTools Protocol. Se capturaron `console.error`,
`console.warn`, excepciones no capturadas, entradas de log del navegador, fallos de carga
de recursos y respuestas HTTP ≥ 400 de subrecursos.

No se añadió Playwright ni Puppeteer: el verificador usa el `WebSocket` nativo de Node y
vive fuera del repositorio.

| Ruta | React montó | `h1` | Hallazgos |
| --- | --- | --- | --- |
| `/` | Sí | «Blog personal — fundacion del frontend» | **0** |
| `/una-ruta-inexistente` | Sí | «404 — pagina no encontrada» | **0** |

La primera pasada sí encontró un error: un **`404` de `/favicon.ico`** en ambas rutas.
Corregido y vuelto a verificar.

### 4.6 Seguridad

**0** secretos, tokens, credenciales, `.env` reales versionados, URL privadas y rutas
locales en código productivo. Escaneo con 8 patrones sobre los archivos nuevos y
modificados: **0 coincidencias**. Ningún `dangerouslySetInnerHTML`.

## 5. Problemas encontrados

### 5.1 `304` declarado como éxito sin cuerpo, pero tratado como error

El conjunto de estados sin cuerpo incluía `204`, `205` y `304`, pero el flujo evalúa
`!response.ok` **antes** de consultarlo. Como `304` no es 2xx, jamás alcanzaba ese
conjunto: la entrada era inalcanzable y describía un comportamiento que el cliente no
tenía. **El reporte inicial repitió esa afirmación falsa.**

Reproducción, con una prueba que codificaba la afirmación del reporte:

```
FAIL  afirma que 304 devuelve undefined como los demas estados sin cuerpo
AssertionError: promise rejected "HttpError: La peticion al API fallo con e…" instead of resolving
Serialized Error: { kind: 'http', status: 304, code: undefined, … }
```

**Semántica elegida: `304` es un error, no un éxito vacío.** Tres razones:

1. No es 2xx, así que la ruta de error es la que le corresponde por construcción.
2. [api-contracts.md](../architecture/api-contracts.md) §8 **no lo declara**, y el proyecto
   no hace peticiones condicionales.
3. El cache HTTP del navegador resuelve un `304` de red antes de entregarlo a `fetch`: uno
   que llegue al código de aplicación es una anomalía.

Se retiró `304` del conjunto, se renombró a `ESTADOS_EXITOSOS_SIN_CUERPO`, se documentó en
el propio código **por qué** `304` no está ahí, y se añadió regresión permanente. Se añadió
además la prueba que faltaba para `205`. Detectado por el usuario en la revisión.

### 5.2 Fuga de aislamiento entre pruebas

Con `globals: false`, Testing Library no registra su limpieza automática. El DOM de una
prueba sobrevivía a la siguiente y una consulta encontraba elementos duplicados: un fallo
dependiente del orden de ejecución. Corregido con `cleanup()` explícito en
`src/test/setup.ts`.

### 5.3 `AbortError` clasificado como fallo de red

`fetch` rechaza con un `DOMException`, que **según la especificación no hereda de `Error`**.
La comprobación `cause instanceof Error && cause.name === 'AbortError'` compilaba sin
quejas y clasificaba toda cancelación como fallo de red. Detectado por su prueba.

### 5.4 `404` de `/favicon.ico`

El *smoke* por HTTP no podía verlo; solo apareció al comprobar la consola con un navegador
real. Resuelto con `<link rel="icon" href="data:," />`: declara que aún no hay icono en
lugar de inventar uno, y deja la decisión visual a `Task/013`.

### 5.5 Finales de línea CRLF

Tres archivos quedaron en CRLF por una herramienta de edición que traduce saltos de línea
en Windows — exactamente el problema que documenta `.gitattributes`. Detectados archivo por
archivo y normalizados a LF antes de cerrar. `git diff --check` pasa.

### 5.6 `set -e` inoperante en el shell de la sesión

La cadena de *gates* no se detenía ante un fallo pese a `set -euo pipefail`. Se comprobó que
ni siquiera el caso mínimo `( set -e; false; echo … )` interrumpe la ejecución en este
entorno. Se sustituyó por comprobación explícita del código de salida, verificada
provocando un fallo deliberado (§4.3).

### 5.7 Cuatro hallazgos de lint corregidos uno a uno

Tres aserciones de tipo innecesarias y un archivo fuera del proyecto de TypeScript, más el
uso obsoleto de `tseslint.config`. **No se usó `--fix` como sustituto de revisarlos ni se
desactivó ninguna regla** para conseguir verde.

## 6. Riesgos y decisiones pendientes

- **No se abre ninguna decisión nueva.** Ninguna elección de esta tarea es estructural: no
  se crea ni se modifica ningún ADR.
- La selección de biblioteca visual sigue **abierta** y pertenece a `Task/013`.
- Riesgos vivos de la tarea, en la [ficha](../tasks/TASK-006-react-frontend-foundation.md)
  §11. Ninguno exige atención antes de la aprobación.

## 7. Estado Git

### 7.1 Antes de la aprobación

| Repositorio | Rama | Commits | Push | Merge | PR | Staging |
| --- | --- | --- | --- | --- | --- | --- |
| `personal-blog-frontend` | `Task/006-Fundacion-Frontend-React` | 0 | 0 | 0 | 0 | Vacío |
| `personal-blog-infra` | `Task/006-Fundacion-Frontend-React` | 0 | 0 | 0 | 0 | Vacío |
| `personal-blog-backend` | `main` | — | — | — | — | Limpio, sin rama Task |

`git diff --check` pasó en ambos repositorios. En los dos, `HEAD` seguía en el SHA de `main`
y `main` era ancestro de `HEAD`.

### 7.2 Cierre aprobado (2026-08-18)

Ejecutado según [PROJECT_INSTRUCTIONS](../claude/PROJECT_INSTRUCTIONS.md) §8, en los dos
repositorios afectados:

1. Aprobación registrada en la ficha, el reporte y el estado de gobierno.
2. **Ningún ADR cambia de estado**: la tarea no produjo decisiones estructurales.
3. Contadores actualizados a **6 de 41 (15 %)** y ETAPA 02 a **2 de 3**.
4. Validaciones finales repetidas antes de comprometer los cambios.
5. Un commit por repositorio.
6-9. `dev` actualizado con `pull --ff-only` e integrada la rama Task con merge `--no-ff`;
   `dev` publicado.
10. Rama Task publicada en `origin`.
11-12. Pull request **`Task/006-Fundacion-Frontend-React → main`** en cada repositorio.
   **Ninguno usa `dev` como *head*.**
13. **Ningún pull request fusionado por Claude.**
14-16. Vuelta a `main`, `fetch --prune`, `pull --ff-only` y borrado de la rama Task local
   con `git branch -d` (nunca `-D`).
17-18. Las ramas Task **remotas se conservan**: eliminarlas es decisión del usuario.

Los detalles verificados —SHA, URL de los pull request y estado final de cada
repositorio— se entregaron al usuario en el reporte de cierre.

## 8. Instrucciones de validación para el usuario

Ver [ficha](../tasks/TASK-006-react-frontend-foundation.md) §17.

## 9. Próxima tarea propuesta

`Task/007-Integracion-Local`. **No se ha iniciado.** No comienza hasta que el usuario fusione
el pull request `Task/006 → main` en ambos repositorios y se complete la normalización
`main → dev` descrita en [PROJECT_INSTRUCTIONS](../claude/PROJECT_INSTRUCTIONS.md) §10.

## 10. Límites respetados

| Límite | Cumplimiento |
| --- | --- |
| Commits solo tras la aprobación | ✔ 0 antes de `approved`; 1 por repositorio en el cierre |
| Push solo tras la aprobación | ✔ |
| Sin merge hacia `main` | ✔ Solo integración en `dev`; `main` lo modifica el usuario al fusionar el PR |
| Pull request `Task → main` | ✔ Uno por repositorio, **abierto**, sin fusionar |
| Sin recursos cloud | ✔ Ninguno creado |
| Sin modificar `personal-blog-backend` | ✔ Worktree limpio, en `main`, sin rama Task |
| Sin tocar infraestructura funcional | ✔ Solo documentación de gobierno de esta tarea |
| Sin ADR nuevos ni modificados | ✔ |
| Sin secretos | ✔ Escaneo con 0 coincidencias |
| Sin avanzar a `Task/007` | ✔ No iniciada |
| Aprobación solo del usuario | ✔ Expresión exacta recibida el 2026-08-18 |
| Avance actualizado tras la aprobación | ✔ **6 / 41 (15 %)**, ETAPA 02 **2 / 3** |
| 41 identificadores intactos | ✔ Ninguna tarea añadida, renumerada ni eliminada |
