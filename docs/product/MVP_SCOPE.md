# Alcance del MVP — Blog Personal

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/002-Definir-MVP-y-Arquitectura` (2026-07-26) |
| **Fecha** | 2026-07-26 |
| **Tarea** | `Task/002-Definir-MVP-y-Arquitectura` |

Este documento define **qué construimos** y, con igual importancia, **qué no**.
Toda tarea posterior debe poder justificarse contra este alcance.

Documentos relacionados: [USER_FLOWS.md](USER_FLOWS.md) ·
[CONTENT_MODEL.md](CONTENT_MODEL.md) ·
[software-architecture.md](../architecture/software-architecture.md) ·
[api-contracts.md](../architecture/api-contracts.md)

---

## 1. Definición del MVP

Un blog personal con **sitio público** y **panel administrativo propio**, operado por un
único administrador, que permite publicar y consultar cinco tipos de contenido:
artículos, reviews de libros, videos, proyectos y el perfil personal.

El MVP se considera alcanzado cuando el administrador puede crear, publicar y gestionar
contenido real desde el panel, y cualquier visitante puede consultarlo en un sitio
público navegable, accesible y descubrible por buscadores.

---

## 2. Sitio público

### 2.1 Rutas y secciones previstas

| # | Sección | Ruta prevista | Contenido |
| --- | --- | --- | --- |
| 1 | Inicio | `/` | Presentación y contenido destacado. |
| 2 | Quién soy | `/quien-soy` | Perfil personal y profesional. |
| 3 | Blog o artículos | `/articulos` | Listado paginado de artículos publicados. |
| 4 | Detalle de artículo | `/articulos/{slug}` | Artículo completo. |
| 5 | Reviews de libros | `/reviews` | Listado paginado de reviews publicadas. |
| 6 | Detalle de review | `/reviews/{slug}` | Review completa. |
| 7 | Videos y explicaciones | `/videos` | Listado de videos publicados. |
| 8 | Proyectos y laboratorio | `/proyectos` | Listado de proyectos publicados. |
| 9 | Contacto y enlaces | `/contacto` | Correo y enlaces a redes. |
| 10 | Página 404 | cualquier ruta inexistente | Error con vuelta a Inicio. |

> Las rutas exactas son una propuesta; se confirman en `Task/014`. El detalle de proyecto
> (`/proyectos/{slug}`) existe a nivel de API desde el inicio; su página de detalle en el
> sitio se decide en `Task/014` según la profundidad del contenido de cada proyecto.

### 2.2 Capacidades del sitio público

El sitio público debe permitir:

- Consultar contenido **publicado** (nunca borradores ni archivados).
- Navegar mediante **slugs legibles**.
- Listar contenido con **paginación**.
- **Filtrar por etiquetas** cuando corresponda.
- Realizar **búsqueda básica**.
- Mostrar **contenido destacado** en Inicio.
- Mostrar **fechas de publicación**.
- Mostrar **imágenes y portadas**.
- Mostrar **enlaces externos seguros**.
- Consumir **videos mediante enlace o embed**, sin alojar archivos de video.
- Compartir páginas mediante **metadatos Open Graph**.
- Navegar correctamente en **escritorio, tablet y móvil**.

### 2.3 Reglas del sitio público

- Es de **solo lectura**. No existe ninguna operación de escritura sin autenticación.
- No descarga datos ni código exclusivos del panel administrativo.
- No expone identificadores internos cuando el slug es suficiente.

---

## 3. Panel administrativo

**Existe un único administrador inicial.** No hay registro público ni gestión de usuarios.

### 3.1 Capacidades

| Grupo | Capacidad |
| --- | --- |
| Sesión | Iniciar sesión |
| Sesión | Cerrar sesión |
| Sesión | Consultar la sesión actual |
| Perfil | Editar el perfil "Quién soy" |
| Artículos | Crear, editar, previsualizar, publicar, despublicar y archivar |
| Reviews | Crear, editar, previsualizar, publicar, despublicar y archivar |
| Videos | Crear, editar, publicar y archivar |
| Proyectos | Crear, editar, previsualizar, publicar y archivar |
| Etiquetas | Gestionar etiquetas |
| Medios | Cargar imágenes |
| Medios | Seleccionar imágenes existentes |
| Medios | Eliminar imágenes **que no estén en uso**, de forma controlada |
| General | Consultar un dashboard básico |
| General | Consultar fechas de creación y actualización |
| General | Registrar acciones administrativas importantes |

> **Editor Markdown y vista previa.** Los tres tipos cuyo contenido principal es Markdown
> — **artículos, reviews y proyectos** — se editan con editor Markdown y tienen **vista
> previa**. **Video no**: su contenido principal es el video externo, no Markdown, por lo
> que no necesita esa vista previa. La vista previa **no publica ni expone** el contenido,
> y usa **el mismo pipeline de render y sanitización que el sitio público**. Ver
> [ADR-005](../adr/ADR-005-markdown-content.md).
>
> La diferencia entre proyectos y los otros dos tipos es la **despublicación**, no la
> vista previa: artículos y reviews pueden volver de `published` a `draft`; videos y
> proyectos se archivan.

### 3.2 Estados de contenido

Los tres estados oficiales del contenido son:

| Estado | Significado | Visible en el sitio público |
| --- | --- | --- |
| `draft` | Borrador en elaboración. | No |
| `published` | Publicado y visible. | Sí |
| `archived` | Retirado, conservado para referencia. | No |

Transiciones previstas:

```
draft ──publicar──> published ──archivar──> archived
  ^                     │                       │
  └────despublicar──────┘                       │
  ^                                             │
  └──────────────restaurar (futuro)─────────────┘
```

Reglas:

- La transición `published → draft` (despublicar) aplica a artículos y reviews.
- `archived` retira el contenido del sitio sin eliminarlo.
- La restauración desde `archived` no es obligatoria en el MVP; si no se implementa, se
  documenta como deuda.
- **No existe edición pública sin autenticación**, en ningún estado.

### 3.3 Dashboard básico

Alcance mínimo: conteo de contenido por tipo y estado, últimos elementos modificados y
últimos eventos de auditoría. Sin gráficas ni analítica.

---

## 4. Contacto

Para el MVP:

- Página de contacto.
- Correo o enlace `mailto:`.
- Enlaces a **GitHub, LinkedIn y otras redes configurables**.
- **Sin formulario de contacto almacenado en base de datos.**

Quedan **fuera del MVP**, salvo aprobación posterior del usuario:

- Formulario de contacto con persistencia.
- Protección antispam (captcha, honeypot, rate limiting del formulario).
- Notificaciones por correo.

Motivo: un formulario obliga a resolver antispam, entrega de correo y almacenamiento de
datos personales — tres problemas que no aportan al objetivo del MVP, que es publicar
contenido.

---

## 5. Contenido

Tipos principales del dominio:

`Profile` · `Post` · `BookReview` · `Video` · `Project` · `Tag` · `MediaAsset` ·
`Administrator` · `AuditEvent`

Sus responsabilidades y atributos conceptuales están en
[CONTENT_MODEL.md](CONTENT_MODEL.md).

> El diseño físico (tablas SQL, migraciones, claves foráneas e índices) **no pertenece a
> esta tarea**: se hace en `Task/008-Modelo-de-Datos`.

---

## 6. Fuera del MVP

Registrado explícitamente como **fuera de alcance inicial**:

### Producto y comunidad

- Registro público de usuarios.
- Múltiples administradores y roles complejos.
- Comentarios.
- Reacciones o *likes*.
- Newsletter.
- Suscripciones.
- Pagos.
- Contenido premium.
- Chat.
- Notificaciones en tiempo real.
- Aplicación móvil.
- Edición colaborativa.
- Redes sociales internas.
- Analítica avanzada propia.
- Alojamiento o *streaming* de videos.
- Internacionalización completa.

### Arquitectura e infraestructura

- Microservicios.
- Amazon EC2.
- Amazon ECS Fargate.
- Amazon EKS.
- Amazon ECR.
- Application Load Balancer.
- NAT Gateway.
- Portainer en producción.
- Entornos cloud permanentes de desarrollo o *staging*.

> La exclusión de los servicios cloud está justificada en
> [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md); la de microservicios, en
> [ADR-004](../adr/ADR-004-modular-monolith.md).

Nada de lo anterior puede introducirse sin un ADR que reemplace la decisión
correspondiente.

---

## 7. Criterios de éxito del MVP

El MVP está completo cuando, en local y luego en producción:

1. El administrador inicia sesión y accede al panel.
2. Crea un borrador de artículo, lo previsualiza y lo publica.
3. Sube una imagen y la usa como portada.
4. El artículo aparece en `/articulos` y en su URL con slug.
5. Publica al menos una review, un video y un proyecto.
6. Edita el perfil "Quién soy" y el cambio se refleja en el sitio.
7. Despublica o archiva contenido y desaparece del sitio público.
8. Un visitante navega, pagina, filtra por etiqueta y busca contenido.
9. El sitio se comporta correctamente en escritorio, tablet y móvil.
10. Las páginas tienen metadatos y Open Graph correctos.
11. Ningún endpoint administrativo responde sin autenticación.
12. Las acciones administrativas quedan registradas en auditoría.

---

## 8. Qué NO define esta tarea

`Task/002` define alcance y arquitectura. **No decide**:

- El mecanismo concreto de autenticación → `Task/011`.
- El esquema físico de base de datos → `Task/008`.
- La biblioteca de componentes visuales ni el diseño visual → `Task/013`.
- El editor Markdown concreto → `Task/015`.
- El proveedor de PostgreSQL administrado → `Task/029`.

Registro completo: [open-decisions.md](../architecture/open-decisions.md).
