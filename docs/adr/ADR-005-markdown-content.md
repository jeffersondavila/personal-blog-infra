# ADR-005 — Contenido principal en Markdown

| Campo | Valor |
| --- | --- |
| **Estado** | **Propuesta — pendiente de aprobación de `Task/002`** |
| **Fecha** | 2026-07-26 |
| **Tarea** | `Task/002-Definir-MVP-y-Arquitectura` (Lista para validación) |
| **Reemplaza a** | — |
| **Reemplazada por** | — |

> **Esta decisión está propuesta y documentada, no aceptada.** Pasará a estado *Aceptada*
> cuando el usuario apruebe la tarea escribiendo
> `approved: Task/002-Definir-MVP-y-Arquitectura`. Hasta entonces no debe tratarse como
> una decisión firme.

---

## Contexto

El blog publica artículos técnicos, reviews de libros y descripciones de proyectos: texto
extenso con encabezados, listas, enlaces, imágenes y bloques de código. Hace falta decidir
**en qué formato se escribe y se almacena** ese contenido.

Las opciones habituales son: Markdown, HTML mediante un editor enriquecido, un formato
estructurado en bloques (JSON), o texto plano.

Restricciones que condicionan la decisión:

- El autor es una persona técnica que ya escribe Markdown a diario.
- El contenido debe durar años y sobrevivir a cambios de editor y de framework.
- Los bloques de código deben representarse con naturalidad.
- Todo contenido almacenado se acabará renderizando en un navegador, lo que convierte el
  render en una **superficie de XSS**.

## Decisión

### 1. El contenido principal se escribe en Markdown

**Artículos (`Post`), reviews (`BookReview`) y proyectos (`Project`)** tienen su contenido
principal en Markdown. La biografía del perfil (`Profile.biography`) también.

### 2. El backend almacena el Markdown original

La base de datos guarda **el Markdown tal como lo escribió el autor**, sin transformar.
No se almacena HTML pre-renderizado como fuente de verdad.

Consecuencias directas: el contenido se puede reeditar sin pérdida, migrar sin conversión
y versionar de forma legible.

### 3. El frontend renderiza el contenido de forma segura

El render de Markdown a HTML ocurre **en el frontend**, tanto en el sitio público como en
la vista previa del panel.

### 4. Debe existir sanitización

**El HTML resultante del render se sanitiza siempre**, antes de insertarse en el
documento. Sin excepciones, sin modo "confiable", sin desactivarlo para el administrador.

Se aplica una lista de elementos y atributos permitidos, no una lista de prohibidos.

### 5. No se almacena HTML arbitrario sin controles

No se acepta ni se guarda HTML libre. Si en el futuro se admite HTML incrustado dentro del
Markdown, será mediante una lista cerrada de elementos permitidos, decidida
explícitamente.

### 6. El panel tendrá editor y vista previa

El panel administrativo ofrece un editor de Markdown y una vista previa que usa
**exactamente el mismo pipeline de render y sanitización** que el sitio público. Lo que se
ve en la vista previa es lo que se publicará.

**Alcance:** editor Markdown y vista previa aplican a **`Post`, `BookReview` y
`Project`** — los tres tipos cuyo contenido principal es Markdown, según la decisión 1.
**`Video` queda excluido** por la decisión 7: su contenido principal no es Markdown.

La vista previa **no publica ni expone** el contenido: no cambia su estado, no genera URL
pública y no lo hace accesible a visitantes.

### 7. Los videos no usan Markdown como contenido principal

`Video` **no tiene campo `content` en Markdown**. Su contenido real es el video alojado
externamente: se almacenan **URL, proveedor y metadatos**, más una descripción breve. El
sistema nunca aloja archivos de video.

## Consecuencias

### Positivas

- **Escritura fluida** para un autor técnico, sin pelear con un editor visual.
- **Portabilidad**: el Markdown se lee sin la aplicación y se migra sin conversión.
- **Durabilidad**: sobrevive a cambios de editor, de framework y de plataforma.
- **Bloques de código naturales**, con lenguaje declarado para el resaltado.
- **Diffs legibles** si en el futuro se versiona el contenido.
- **Superficie de ataque acotada**: el sistema nunca confía en HTML de entrada.
- **Vista previa fiel**, porque comparte pipeline con el render público.
- **Almacenamiento eficiente**: texto plano, sin marcado redundante.

### Negativas

- **Barrera para autores no técnicos.**
  *Mitigación:* irrelevante en el MVP, que tiene un único administrador técnico.
- **Menos control de maquetación** que con HTML libre: no hay diseños complejos por
  contenido.
  *Aceptado:* es un blog, no un constructor de páginas. La coherencia visual la aporta el
  sistema de diseño (`Task/013`).
- **El render en cliente añade peso al bundle** y trabajo en el navegador.
  *Mitigación:* carga diferida del renderizador donde aplique; se mide en `Task/016`.
- **La sanitización es un punto crítico**: si falla o se configura mal, se convierte en
  XSS almacenado.
  *Mitigación:* sanitización obligatoria, con configuración única y compartida entre sitio
  y vista previa; se audita en `Task/018`.
- **Riesgo de dos pipelines divergentes** (público y vista previa).
  *Mitigación:* la decisión 6 exige explícitamente que sea **el mismo** pipeline.
- **El render en cliente limita el SEO** frente a un HTML servido ya renderizado.
  *Mitigación:* metadatos, Open Graph, canonical, sitemap y datos estructurados se
  gestionan aparte (`Task/016`). Si resulta insuficiente, se reconsidera con un ADR.

### Neutras

- Que el render sea en cliente y no en servidor es una consecuencia de la arquitectura
  (frontend estático en Cloudflare Pages, backend en Lambda), no una decisión de este ADR.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
| --- | --- |
| **Editor WYSIWYG que almacena HTML** | Obliga a confiar en HTML de entrada, ampliando la superficie de XSS. El HTML generado por editores es sucio, difícil de migrar y queda atado al editor concreto. Un cambio de editor rompería el contenido existente. |
| **Formato estructurado en bloques (JSON)** | Ofrece más control sobre el render y es lo que usan los CMS modernos, pero exige construir un editor de bloques y un renderizador propios: mucho más trabajo del que justifica un blog personal, y con un formato propietario que solo la aplicación entiende. |
| **Markdown renderizado en el servidor y almacenado como HTML** | Mejoraría el SEO y aligeraría el cliente, pero obliga a mantener dos representaciones sincronizadas, complica la reedición y exige re-renderizar todo el contenido al cambiar el pipeline. |
| **Texto plano** | Insuficiente: no hay encabezados, enlaces, imágenes ni bloques de código. |
| **Markdown con HTML incrustado libre** | Aporta flexibilidad puntual a cambio de reintroducir exactamente el riesgo que la decisión 5 evita. |

## Cumplimiento

Esta decisión se verifica en:

- `Task/008` — el modelo de datos almacena Markdown, no HTML.
- `Task/014` y `Task/015` — el render y la vista previa comparten pipeline y sanitizan.
- `Task/018` — auditoría de la sanitización.
- `Task/016` — comprobación de que el SEO es suficiente pese al render en cliente.

Ningún camino de código puede insertar HTML sin sanitizar en el documento. Si aparece uno,
es un defecto de seguridad, no una excepción.

## Referencias

- [CONTENT_MODEL.md](../product/CONTENT_MODEL.md)
- [security-boundaries.md](../architecture/security-boundaries.md)
- [non-functional-requirements.md](../architecture/non-functional-requirements.md) — S-03
- [open-decisions.md](../architecture/open-decisions.md) — D-04, editor concreto
