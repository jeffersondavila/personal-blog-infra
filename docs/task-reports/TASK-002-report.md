# Reporte — TASK-002 Definir MVP y Arquitectura

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/002-Definir-MVP-y-Arquitectura` |
| **Etapa** | ETAPA 00 — Fundación y Gobierno |
| **Estado final** | **Lista para validación** |
| **Fecha** | 2026-07-26 |
| **Repositorios afectados** | `personal-blog-infra` (documentación); frontend y backend solo en la sincronización de ramas |
| **Ficha completa** | [TASK-002](../tasks/TASK-002-define-mvp-and-architecture.md) |

---

## 1. Sincronización `main` → `dev`

**Problema encontrado:** los pull requests de `Task/001` se integraron desde la rama
`Task/001` **directamente hacia `main`**. `main` y `dev` quedaron con el mismo contenido
pero distintos commits de merge, y `origin/main` tenía un commit ausente en `dev`.

**Secuencia ejecutada** en cada repositorio: `fetch --prune` → `main` + `pull --ff-only` →
`dev` + `pull --ff-only` → `merge --no-ff origin/main` → `push origin dev` → vuelta a
`main`.

| Repositorio | `dev` antes | `dev` después | `main` | `diff dev↔main` |
| --- | --- | --- | --- | --- |
| `personal-blog-infra` | `f4f32a9` | **`cc3aad8`** | `8fd61ea` | Vacío |
| `personal-blog-frontend` | `2d18231` | **`8823cc3`** | `144a401` | Vacío |
| `personal-blog-backend` | `e61a848` | **`0f94abb`** | `76c09f5` | Vacío |

Mensaje del merge: `merge: sincronizar dev con main despues de Task/001`.
Se publicó **únicamente** esa sincronización de `dev`. Los tres árboles quedaron limpios.

## 2. Rama activa y estado de cada repositorio

| Repositorio | Rama activa | Ramas | Estado del árbol |
| --- | --- | --- | --- |
| `personal-blog-infra` | `Task/002-Definir-MVP-y-Arquitectura` | `main`, `dev`, `Task/002` | 9 modificados + 10 entradas sin seguimiento (**12 archivos nuevos**), **todo documentación, sin confirmar** |
| `personal-blog-frontend` | `main` | `main`, `dev` | Limpio |
| `personal-blog-backend` | `main` | `main`, `dev` | Limpio |

`Task/002` se creó desde `dev` **solo en `personal-blog-infra`**, tal como se pidió: la
tarea modifica exclusivamente documentación central.

## 3. Archivos creados y modificados

**12 creados · 9 modificados · 0 eliminados.** Todos son `.md`, todos en
`personal-blog-infra`.

> `git status` muestra **10 entradas sin seguimiento** para esos 12 archivos nuevos: Git
> agrupa `docs/product/` como una **sola entrada de directorio**, y ese directorio
> contiene 3 archivos. 9 entradas individuales + 3 archivos en `docs/product/` = **12
> archivos nuevos**.

### Creados

```
docs/product/MVP_SCOPE.md
docs/product/USER_FLOWS.md
docs/product/CONTENT_MODEL.md
docs/architecture/software-architecture.md
docs/architecture/api-contracts.md
docs/architecture/non-functional-requirements.md
docs/architecture/security-boundaries.md
docs/architecture/open-decisions.md
docs/adr/ADR-004-modular-monolith.md
docs/adr/ADR-005-markdown-content.md
docs/tasks/TASK-002-define-mvp-and-architecture.md
docs/task-reports/TASK-002-report.md
```

### Modificados

```
README.md                                          (estructura docs/, estado, alcance)
docs/project-management/STATUS.md                  (Task/002, B-01 cerrado, ramas)
docs/project-management/ROADMAP.md                 (Task/002 lista para validación)
docs/stages/STAGE-00-foundation.md                 (estado y documentos producidos)
docs/architecture/overview.md                      (remite al detalle; qué falta decidir)
docs/architecture/local-to-cloud-mapping.md        (nota de consistencia)
docs/task-reports/README.md                        (índice)
docs/tasks/TASK-001-initial-workspace-and-roadmap.md   (cierre real)
docs/task-reports/TASK-001-report.md               (cierre real, B-01)
```

## 4. Resumen del MVP definido

**Sitio público** — 10 secciones: Inicio, Quién soy, Artículos, Detalle de artículo,
Reviews, Detalle de review, Videos, Proyectos, Contacto, 404. Solo lectura, con slugs
legibles, paginación, filtro por etiquetas, búsqueda básica, contenido destacado,
imágenes, embeds de video sin alojarlos, Open Graph y comportamiento responsive.

**Panel administrativo** — un único administrador. 17 capacidades: sesión (login, logout,
consultar sesión), perfil, ciclo de vida de artículos y reviews (crear, editar,
previsualizar, publicar, despublicar, archivar), de proyectos (crear, editar,
previsualizar, publicar, archivar) y de videos (crear, editar, publicar, archivar),
etiquetas, medios (cargar, seleccionar, eliminar solo si no están en uso), dashboard
básico, fechas y auditoría.

**Editor Markdown y vista previa:** aplican a **`Post`, `BookReview` y `Project`**, los
tres tipos cuyo contenido principal es Markdown. **`Video` queda excluido** porque su
contenido principal es el video externo. La vista previa **no publica ni expone** el
contenido y usa **el mismo pipeline de render y sanitización que el sitio público**.

**Despublicación:** solo artículos y reviews vuelven de `published` a `draft`; videos y
proyectos se archivan. Esta es la única diferencia de ciclo de vida entre tipos — no la
vista previa.

**Estados de contenido:** `draft` → `published` → `archived`. Ninguna edición pública sin
autenticación.

**Contacto:** página con correo y enlaces configurables. **Sin formulario** ni
persistencia.

**Contenido:** 9 tipos — `Profile`, `Post`, `BookReview`, `Video`, `Project`, `Tag`,
`MediaAsset`, `Administrator`, `AuditEvent` — descritos a nivel **conceptual**, con
aplicabilidad de campos por tipo. Sin tablas SQL ni migraciones (eso es `Task/008`).

**Flujos:** 11 públicos y 12 administrativos, cada uno con sus datos, reglas y errores.

## 5. Resumen del fuera de alcance

**Producto:** registro público de usuarios, múltiples administradores y roles, comentarios,
reacciones, newsletter, suscripciones, pagos, contenido premium, chat, notificaciones en
tiempo real, app móvil, edición colaborativa, redes sociales internas, analítica avanzada
propia, alojamiento o streaming de video, internacionalización completa.

**Arquitectura e infraestructura:** microservicios, EC2, ECS Fargate, EKS, ECR,
Application Load Balancer, NAT Gateway, Portainer en producción, entornos cloud
permanentes de desarrollo o staging.

Nada de lo anterior puede introducirse sin un ADR que reemplace la decisión
correspondiente.

## 6. Arquitectura de backend acordada

**Monolito modular con Clean Architecture pragmática** ([ADR-004](../adr/ADR-004-modular-monolith.md)).

```
app/
├── modules/   profile, posts, book_reviews, videos, projects,
│              tags, media, authentication, audit
└── shared/    database, storage, security, logging,
               pagination, errors, configuration
```

Cada módulo puede tener `domain`, `application`, `infrastructure` y `presentation`, con
dependencias hacia adentro (`presentation → application → domain ← infrastructure`).
**Prohibido crear capas vacías o abstracciones sin uso.**

Principios: dominio separado de frameworks · endpoints delgados · casos de uso explícitos
· repositorios para persistencia · adaptadores para servicios externos · DI simple · sin
patrones innecesarios · sin microservicios · **no compartir modelos ORM con la API** · sin
acoplar la lógica a Lambda, MinIO ni S3.

**`ObjectStorage`:** interfaz con `MinIOStorage` (local) y `S3Storage` (producción). La
base de datos guarda metadatos y claves de objeto, **nunca binarios**. Videos solo con
URL, proveedor y metadatos. Nombres de objeto no predecibles, bucket privado, URLs
prefirmadas en producción.

## 7. Arquitectura de frontend acordada

Orientada a funcionalidades:

```
src/  app, pages, features, entities, components,
      services, hooks, lib, styles, assets
```

Reglas: solo `services` habla HTTP · `components` no conoce el dominio · `lib` no importa
de nadie · sitio público y panel comparten sistema de diseño · **el código del panel no se
descarga en las páginas públicas** · el frontend **no autoriza**, solo presenta · la URL
del API entra por variable de entorno en build · nada en el build es secreto.

**No se seleccionó biblioteca visual** (decisión D-03, `Task/013`).

## 8. Contratos generales de API acordados

Base `/api/v1`. Técnicos: `GET /health`, `GET /ready`.
10 recursos públicos (solo lectura, nunca `draft` ni `archived`) y 10 administrativos
(autenticados salvo `login`).

Convenciones: JSON · UTF-8 · fechas **ISO 8601 en UTC** · identificadores internos no
expuestos innecesariamente · slugs estables y únicos · paginación `page`/`page_size` ·
orden por defecto `published_at` descendente · filtros por query parameters · códigos HTTP
coherentes · correlation/request ID en petición, respuesta, logs y auditoría.

**Colección paginada:**

```json
{ "items": [], "page": 1, "page_size": 12, "total": 0, "pages": 0 }
```

**Error común:**

```json
{ "error": { "code": "string", "message": "string", "details": {}, "request_id": "string" } }
```

Regla de no filtración: un slug inexistente y uno no publicado devuelven **el mismo
`404`**.

## 9. Requisitos no funcionales acordados

**57 requisitos** en 7 categorías, cada uno con la tarea que lo verifica:

| Categoría | Nº | Ejemplos |
| --- | --- | --- |
| Seguridad | 12 | Mínimo privilegio, validación de entrada, sanitización, CORS por ambiente, headers, sin trazas internas, sin secretos en logs. |
| Rendimiento | 8 | Paginación obligatoria, lazy loading, imágenes optimizadas, backend stateless, compatible con cold starts. |
| Accesibilidad | 8 | Teclado, HTML semántico, labels, texto alternativo, contraste, foco visible. Objetivo **WCAG 2.1 AA**. |
| SEO | 8 | Slugs legibles, title/description, Open Graph, canonical, sitemap, robots.txt, datos estructurados. |
| Observabilidad | 8 | Logs JSON, correlation ID, health, ready, auditoría, CloudWatch con retención limitada, logs locales en Portainer. |
| Portabilidad | 7 | Config por variables de entorno, PostgreSQL estándar, `ObjectStorage`, independencia de Lambda y de Cloudflare Pages. |
| Mantenibilidad | 6 | Lint, tipado estático, pruebas, migraciones reversibles, sin capas vacías. |
| **Total** | **57** | |

**Límites de seguridad:** 11 componentes con matriz de comunicaciones permitidas y
prohibidas, 13 superficies de ataque con su control, y reglas explícitas de Portainer
(solo local, ajeno a `/admin`, no publicado, no administra contenido, acceso al socket de
Docker considerado privilegiado).

## 10. ADR creados

> **Ambos están en estado `Propuesta — pendiente de aprobación de Task/002`, no
> `Aceptada`.** Las decisiones están documentadas pero no son firmes: pasarán a
> *Aceptada* cuando el usuario escriba `approved: Task/002-Definir-MVP-y-Arquitectura`.

| ADR | Decisión | Puntos clave |
| --- | --- | --- |
| [ADR-004](../adr/ADR-004-modular-monolith.md) | Monolito modular con Clean Architecture pragmática | Sin microservicios; división por módulos de negocio, no por capas técnicas; adaptadores para base de datos, almacenamiento y Lambda; incluye **7 señales** que justificarían reconsiderarla. |
| [ADR-005](../adr/ADR-005-markdown-content.md) | Contenido principal en Markdown | Aplica a **`Post`, `BookReview` y `Project`**; backend almacena el Markdown original; render sanitizado **siempre**, sin excepciones; editor y vista previa para esos tres tipos, con el mismo pipeline que el sitio público y sin publicar ni exponer nada; sin HTML arbitrario; **`Video` no usa Markdown**, solo URL, proveedor y metadatos, y por tanto no tiene esa vista previa. |

## 11. Decisiones diferidas

13 registradas en [open-decisions.md](../architecture/open-decisions.md), cada una con
tarea, información necesaria y partes afectadas:

| # | Decisión | Tarea |
| --- | --- | --- |
| D-01 | Proveedor de PostgreSQL administrado | `Task/029` |
| D-02 | Mecanismo de autenticación (cookie o token), duración, CSRF | `Task/011` |
| D-03 | Biblioteca de componentes visuales | `Task/013` |
| D-04 | Editor Markdown | `Task/015` |
| D-05 | Reverse proxy local concreto | `Task/003` |
| D-06 | Backend de estado de Terraform | `Task/025` |
| D-07 | Dominio definitivo | `Task/035` |
| D-08 | Estrategia de CDN para medios | `Task/030` |
| D-09 | Herramienta de rate limiting | `Task/011` |
| D-10 | Estrategia de backups cloud | `Task/029` |
| D-11 | Retención exacta de CloudWatch | `Task/031` |
| D-12 | Límites exactos de Lambda | `Task/032` |
| D-13 | Presupuesto mensual objetivo | `Task/027` |

**Ninguna se resolvió en esta tarea.** De autenticación quedó fijado *qué* debe cumplirse
(un solo administrador, todo autenticado salvo login, hash seguro, protección ante fuerza
bruta, logout, auditoría, secretos fuera de Git) pero **no el mecanismo**.

## 12. Correcciones al estado de `Task/001`

| Documento | Corrección |
| --- | --- |
| `STATUS.md` | Bloqueos activos 1 → **0**. B-01 **Cerrado** con su resolución. Sección de repositorios reescrita: ramas publicadas, `Task/001` eliminada, sincronización explicada. |
| Ficha de `Task/001` | Publicación **completada**; rama eliminada local y remotamente; pasos 7–9 y 11 del flujo de cierre pasan a *Hecho*. |
| Reporte de `Task/001` | Nota de cierre en 7.2 (GitHub CLI instalado y autenticado, push completados, PR aceptados, `main` actualizado, ramas eliminadas); sección 8.2 marcada como *ya ejecutada*; sección 10 con el estado remoto y los PR `#1`. |
| `README.md` de infra | Estado de ramas actualizado. |

**El registro histórico se conservó.** El reporte sigue describiendo que B-01 ocurrió, por
qué y con qué error exacto. No se reescribió para simular que nunca sucedió.

## 13. Validaciones ejecutadas y resultados

| # | Validación | Resultado |
| --- | --- | --- |
| 1 | `git status` ×3 | Frontend y backend **limpios** en `main`. Infra en `Task/002`: **9 modificados** + **10 entradas sin seguimiento** = **12 archivos nuevos** (Git agrupa `docs/product/` como una entrada de directorio con 3 archivos). Todo `.md`, sin confirmar. |
| 2 | `git branch -vv` ×3 | `main` y `dev` con seguimiento correcto. `Task/002` solo en infra, sin upstream. |
| 3 | `git branch -r` ×3 | `origin/main`, `origin/dev` y `origin/HEAD` en los tres. **Ninguna rama `Task/001` remota.** |
| 4 | `git log --graph` | Historial esperado: commit inicial → trabajo → merge en `dev` → PR `#1` a `main` → merge de sincronización. |
| 5 | `main` y `dev` con el mismo contenido | `git diff --stat dev origin/main` **vacío** en los tres. |
| 6 | Listado de archivos | **12 creados, 9 modificados, 0 eliminados.** Todos `.md`. |
| 7 | Enlaces Markdown relativos | **254 verificados, 0 rotos.** |
| 8 | Búsqueda de secretos | **0 coincidencias reales.** La única aparición es la lista de patrones citada como texto en el reporte de `Task/001`. |
| 9 | Archivos fuera de alcance | **Ninguno.** Sin `*.py`, `*.ts`, `*.tsx`, `*.jsx`, `*.tf`, `*.tfvars`, `package.json`, `pyproject.toml`, `Dockerfile` ni `docker-compose*.yml`. |
| 10 | Coherencia entre documentos | 9 comprobaciones cruzadas, todas correctas (ver ficha §11). |
| 11 | Decisiones que debían diferirse | Ninguna tomada — las 13 siguen abiertas. |

Ningún comando destructivo fue ejecutado.

## 14. Riesgos e inconsistencias encontradas

**Inconsistencia encontrada y corregida:** `main` y `dev` con distintos commits de merge
tras los PR de `Task/001` (sección 1).

**Inconsistencia encontrada y corregida:** la documentación describía el bloqueo B-01 como
activo cuando ya estaba resuelto (sección 12).

**Observación sin impacto:** `gh` está instalado en `C:\Program Files\GitHub CLI\gh.exe`
pero no en el `PATH` de la shell de trabajo. No afecta a nada: el helper de credenciales
de Git lo invoca por ruta absoluta y todas las operaciones remotas funcionaron.

**Riesgos abiertos:** R-02 (costo cloud), R-03 (PostgreSQL ↔ Lambda), R-04 (roadmap
desactualizado), R-05 (enlaces entre repositorios), **R-06 nuevo** (el alcance del MVP
puede crecer durante la implementación), **R-07 nuevo** (el render de Markdown en cliente
puede resultar insuficiente para SEO).

R-01 y B-01 quedan **cerrados**.

## 15. Pasos exactos para validar localmente

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal

# a) Ramas, sincronización e historial
foreach ($r in @('personal-blog-backend','personal-blog-frontend','personal-blog-infra')) {
  Write-Output "=== $r ==="
  git -C $r status --porcelain -b
  git -C $r branch -vv
  git -C $r branch -r
  git -C $r log --oneline --graph --all -12
}

# b) main y dev tienen el mismo contenido (debe no imprimir nada)
foreach ($r in @('personal-blog-backend','personal-blog-frontend','personal-blog-infra')) {
  git -C $r diff --stat dev origin/main
}

# c) No hay código ni infraestructura (debe no devolver nada)
Get-ChildItem -Recurse -File . -Include *.py,*.ts,*.tsx,*.jsx,*.tf,*.tfvars,`
  package.json,pyproject.toml,Dockerfile,docker-compose*.yml |
  Where-Object { $_.FullName -notmatch '\\\.git\\' }

# d) Documentos nuevos de Task/002
Get-ChildItem -Recurse personal-blog-infra\docs\product,`
  personal-blog-infra\docs\architecture, personal-blog-infra\docs\adr -File
```

Orden de lectura sugerido:

1. [MVP_SCOPE.md](../product/MVP_SCOPE.md) — qué construimos y qué no.
2. [USER_FLOWS.md](../product/USER_FLOWS.md) — cómo se usa.
3. [CONTENT_MODEL.md](../product/CONTENT_MODEL.md) — qué datos existen.
4. [software-architecture.md](../architecture/software-architecture.md) — cómo se organiza el código.
5. [api-contracts.md](../architecture/api-contracts.md) — cómo se comunican.
6. [non-functional-requirements.md](../architecture/non-functional-requirements.md) — qué debe cumplirse siempre.
7. [security-boundaries.md](../architecture/security-boundaries.md) — qué puede hablar con qué.
8. [ADR-004](../adr/ADR-004-modular-monolith.md) y [ADR-005](../adr/ADR-005-markdown-content.md).
9. [open-decisions.md](../architecture/open-decisions.md) — qué falta decidir.
10. [STATUS.md](../project-management/STATUS.md) — estado vigente.

**Qué revisar con atención:** si el alcance del MVP coincide con lo que quieres construir,
si falta o sobra alguna sección o capacidad, y si alguna decisión diferida debería
adelantarse.

## 15.b Correcciones aplicadas tras la revisión del usuario

Ronda del 2026-07-26, sobre la misma rama, **sin cambiar el alcance general**. La tarea
permanece `Lista para validación`.

### C-1 — Vista previa de `Project`

**Contradicción detectada:** ADR-005 incluía `Project` entre los tipos con contenido
principal en Markdown y establecía editor y vista previa para ese contenido, mientras que
`USER_FLOWS` limitaba la vista previa a artículos y reviews y `MVP_SCOPE` describía los
proyectos como contenido estructurado que no la necesitaba.

**Cómo queda definida:**

| Tipo | Contenido principal | Editor Markdown | Vista previa |
| --- | --- | :---: | :---: |
| `Post` | Markdown | Sí | **Sí** |
| `BookReview` | Markdown | Sí | **Sí** |
| `Project` | Markdown | Sí | **Sí** |
| `Video` | URL, proveedor y metadatos | **No** | **No** |

- La vista previa **no publica** el contenido ni lo expone: no cambia su estado, no genera
  URL pública y no lo hace accesible a visitantes.
- La vista previa usa **el mismo pipeline de render y sanitización que el sitio público**.
- La diferencia de ciclo de vida entre tipos es la **despublicación** —solo artículos y
  reviews vuelven de `published` a `draft`—, **no** la vista previa.

**Corregidos:** `MVP_SCOPE.md` (§3.1: capacidad de proyectos y nota), `USER_FLOWS.md`
(B.6 con matriz por tipo y entrada de la matriz de recursos), `CONTENT_MODEL.md` (§2,
notas y tabla), `ADR-005-markdown-content.md` (decisión 6, alcance explícito), la ficha y
este reporte.

### C-2 — Total de requisitos no funcionales

**Error:** se declaraban **43** requisitos. La suma real de las categorías es
`12 + 8 + 8 + 8 + 8 + 7 + 6 = 57`.

**Total correcto: 57 requisitos no funcionales.**

No se eliminó ni fusionó ningún requisito individual: no había duplicaciones, solo un
total mal sumado. Se añadió una tabla de recuento por categoría en
`non-functional-requirements.md` para que el total quede verificable.

**Corregidos:** `non-functional-requirements.md`, la ficha, este reporte, `README.md` y
`overview.md`.

### C-3 — Resultados finales de validación

| Métrica | Valor final |
| --- | --- |
| Archivos creados | **12** |
| Archivos modificados | **9** |
| Archivos eliminados | **0** |
| Entradas sin seguimiento en `git status` | **10** |
| Enlaces Markdown relativos verificados | **254** |
| Enlaces rotos | **0** |

> El recuento pasó de 252 a **254** en esta ronda: los dos enlaces cruzados nuevos entre
> `USER_FLOWS.md` y `CONTENT_MODEL.md`, añadidos para que ambos documentos apunten a la
> definición de la vista previa. Ninguno está roto.

**Aclaración 10 vs 12:** `git status` muestra **10 entradas** sin seguimiento para **12
archivos nuevos** porque Git agrupa `docs/product/` como una **sola entrada de
directorio**, y ese directorio contiene 3 archivos. Son 9 entradas individuales más 3
archivos dentro de `docs/product/`.

Se corrigieron las referencias previas a "8 sin seguimiento" y "226 enlaces".

---

## 16. Próxima tarea prevista

**`Task/003-Crear-Infraestructura-Local`** — Docker Compose, PostgreSQL, MinIO, Portainer,
redes, volúmenes y healthchecks.

**No ha sido iniciada.** Requiere la aprobación de `Task/002`.

## 17. Confirmación de límites respetados

- **No se hizo commit de `Task/002`.** Los cambios están en el árbol de trabajo, sin
  confirmar.
- **No se hizo merge de `Task/002`.**
- **No se hizo push de `Task/002`.** La rama existe solo localmente.
- **No se creó pull request de `Task/002`.**
- **No se creó código funcional**: ni React, ni FastAPI, ni `package.json`, ni
  `pyproject.toml`, ni migraciones, ni SQL, ni `Dockerfile`, ni Docker Compose, ni
  Terraform, ni workflows.
- **No se levantó** PostgreSQL, MinIO ni Portainer.
- **No se creó ningún recurso cloud** ni ninguna cuenta.
- **No se eligió el proveedor de PostgreSQL cloud** ni ninguna otra decisión diferida.
- **No se implementó autenticación** ni se decidió su mecanismo.
- **No se creó especificación OpenAPI completa.**
- **No se diseñó visualmente la interfaz.**
- **No se agregó ningún secreto.**
- **No se inició `Task/003`.**
- Todo el trabajo se realizó dentro de `C:\Users\jeffe\Downloads\Blog_Personal`.

**Excepción autorizada:** el push de la sincronización `main` → `dev` en los tres
repositorios, solicitado explícitamente como mantenimiento previo (paso 7 de la
preparación de ramas). No incluye ningún contenido de `Task/002`.

`Task/002` queda **Lista para validación**, a la espera de
`approved: Task/002-Definir-MVP-y-Arquitectura`.
