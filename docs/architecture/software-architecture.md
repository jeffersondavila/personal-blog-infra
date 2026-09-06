# Arquitectura de software

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/002-Definir-MVP-y-Arquitectura` (2026-07-26) |
| **Fecha** | 2026-07-26 · §3.4 precisada y §3.9 añadida por `Task/011-Autenticacion-Administrativa` (2026-09-01) · §3.10 añadida por `Task/012-API-Administrativa` (2026-09-01) |

Define **cómo se organiza el código** de backend y frontend, y cómo se reparten las
responsabilidades entre los tres repositorios.

Relacionados: [ADR-004 — Monolito modular](../adr/ADR-004-modular-monolith.md) ·
[api-contracts.md](api-contracts.md) · [overview.md](overview.md) ·
[security-boundaries.md](security-boundaries.md)

---

## 1. Estilo arquitectónico

**Monolito modular con Clean Architecture pragmática.**

- Un único backend desplegable, dividido en **módulos de negocio**.
- Cada módulo separa dominio, aplicación, infraestructura y presentación **cuando aporta
  valor**.
- **Sin microservicios** (ver [ADR-004](../adr/ADR-004-modular-monolith.md)).
- El dominio no conoce FastAPI, SQLAlchemy, MinIO, S3 ni Lambda.

"Pragmática" significa: se aplican las capas donde resuelven un problema real, y **no se
crean capas vacías ni abstracciones sin uso**.

---

## 2. Responsabilidades por repositorio

| Repositorio | Responsabilidad | Fuera de su responsabilidad |
| --- | --- | --- |
| `personal-blog-frontend` | Sitio público y panel administrativo. Sistema de diseño, componentes, cliente HTTP, rutas, estado de UI, SEO del lado del cliente. | Lógica de dominio, acceso a base de datos, autenticación del lado servidor, infraestructura. |
| `personal-blog-backend` | API pública y administrativa, dominio, casos de uso, persistencia, migraciones, autenticación, auditoría, adaptadores de almacenamiento. | Interfaz de usuario, definición del entorno, Terraform, planificación. |
| `personal-blog-infra` | Fuente de verdad documental. Docker Compose local, Terraform cloud, runbooks, ADR, roadmap. | Código de aplicación de cualquier tipo. |

Regla de oro: **ninguna regla de negocio vive en el frontend ni en la infraestructura**.
El frontend presenta y valida por usabilidad; el backend decide.

---

## 3. Backend

### 3.1 Estructura

```
app/
├── api/                    transporte HTTP transversal, ajeno a un modulo
├── modules/
│   ├── profile/
│   ├── posts/
│   ├── book_reviews/
│   ├── videos/
│   ├── projects/
│   ├── tags/
│   ├── media/
│   ├── authentication/
│   └── audit/
└── shared/
    ├── database/
    ├── storage/
    ├── security/
    ├── logging/
    ├── pagination/
    ├── errors/
    ├── slug.py                 formato y generacion del slug (`Task/012`)
    ├── reloj.py                fuente del instante actual (`Task/012`)
    └── configuration/
```

`app/api` contiene los *endpoints* que **no pertenecen a ningún módulo de negocio**:
operativos y de plataforma, como `GET /health` (`Task/005`) y `/ready` (`Task/017`). No
contiene reglas de negocio ni acceso a datos; los endpoints de contenido viven en la capa
`presentation` de su propio módulo (§3.2).

> Añadido en `Task/005.6`: el paquete existe en `personal-blog-backend` desde `Task/005`,
> pero este diagrama solo mostraba `modules/` y `shared/`.

### 3.2 Capas dentro de un módulo

Cada módulo **puede** contener, según corresponda:

| Capa | Contiene | Depende de |
| --- | --- | --- |
| `domain` | Entidades, objetos de valor, reglas e invariantes, interfaces de repositorio. | Nada del framework. |
| `application` | Casos de uso explícitos, orquestación, DTO de entrada y salida. | Solo de `domain`. |
| `infrastructure` | Implementaciones de repositorio, modelos ORM, adaptadores externos. | De `domain` (implementa sus interfaces). |
| `presentation` / `api` | Routers, validación de entrada, serialización, códigos HTTP. | De `application`. |

**Regla de dependencias:** las dependencias apuntan **hacia adentro**.
`presentation → application → domain ← infrastructure`.
`domain` no importa nada de las otras capas.

> No todos los módulos necesitan las cuatro capas. `tags` puede resolverse con menos
> ceremonia que `posts`. **Crear capas vacías está explícitamente prohibido.**

### 3.3 Responsabilidad de cada módulo

| Módulo | Responsabilidad |
| --- | --- |
| `profile` | Perfil singleton del autor y sus enlaces. |
| `posts` | Artículos: ciclo de vida, publicación, consulta pública. |
| `book_reviews` | Reviews de libros, con datos del libro y valoración. |
| `videos` | Referencias a videos externos y sus metadatos. |
| `projects` | Proyectos y experimentos. |
| `tags` | Etiquetas y su asociación con contenido. |
| `media` | Carga, consulta y borrado controlado de imágenes; comprobación de uso. |
| `authentication` | Login, logout, sesión actual, protección contra fuerza bruta. |
| `audit` | Registro inmutable de acciones administrativas, y su **lectura** paginada para el dashboard (`Task/012.1`). |

### 3.4 Responsabilidad de `shared`

| Paquete | Responsabilidad |
| --- | --- |
| `database` | Sesión, unidad de trabajo, base de los modelos ORM. |
| `storage` | Interfaz `ObjectStorage` y sus implementaciones. |
| `security` | Hash de contraseñas, política de `Origin`, resolución de la dirección del cliente y cabeceras de seguridad. **Primitivas transversales**; la dependencia de autorización vive en el módulo `authentication` (precisión de `Task/011`, abajo). |
| `logging` | Logs JSON y propagación del correlation ID. |
| `pagination` | Parámetros y envoltura de colección paginada. |
| `errors` | Jerarquía de errores de dominio y su traducción a HTTP. |
| `configuration` | Carga y validación de configuración desde variables de entorno. |
| `slug` | Formato y generación del *slug* (`Task/012`). Transformación de texto: no conoce ninguna tabla. |
| `reloj` | Fuente del instante actual (`Task/012`). Mudada desde `authentication` al pasar de un consumidor a cinco. |

`shared` contiene **capacidades técnicas transversales**, nunca reglas de negocio.

> **Precisión de `Task/011` sobre la dependencia de autorización.** Esta tabla asignaba a
> `shared/security` las *dependencias de autorización*. Resolver una exige consultar
> **sesiones y administradores**, que son del módulo `authentication`, así que colocarla
> en `shared` obligaría a que `shared` importara un módulo de negocio — justo lo que la
> regla de dependencias de §3.2 prohíbe.
>
> Queda así: `shared/security` conserva las **primitivas que no conocen ningún módulo**
> —hash de contraseñas, política de `Origin`, dirección del cliente—, y la dependencia
> `requiere_administrador` vive en
> `app/modules/authentication/presentation/`, exportada como **interfaz pública del
> módulo** para que `Task/012` la reutilice sin conocer sus entrañas. Las **cabeceras de
> seguridad** siguen siendo de `Task/018`.

### 3.5 Principios obligatorios

1. **Separar dominio de frameworks.** El dominio es Python plano.
2. **Endpoints delgados.** Un endpoint valida la entrada, invoca un caso de uso y
   serializa la salida. Nada más.
3. **Casos de uso explícitos.** Cada operación de negocio es una unidad con nombre propio
   (`PublishPost`, `UploadMedia`, `ArchiveProject`).
4. **Repositorios para persistencia.** El dominio define la interfaz; la infraestructura
   la implementa.
5. **Adaptadores para servicios externos.** Almacenamiento de objetos y cualquier
   servicio externo se consumen tras una interfaz.
6. **Inyección de dependencias simple.** El mecanismo del framework basta; sin
   contenedores de DI elaborados.
7. **Evitar patrones innecesarios.** Sin CQRS, sin event sourcing, sin bus de mensajes.
8. **No crear microservicios.**
9. **No compartir modelos ORM directamente con la API.** Los esquemas de entrada y salida
   son distintos de los modelos de persistencia.
10. **No acoplar la lógica de negocio a Lambda, MinIO ni S3.**

### 3.6 Flujo de una petición

```
HTTP
 │
 ▼
presentation  ── valida entrada, resuelve dependencias
 │
 ▼
application   ── ejecuta el caso de uso
 │
 ├──────────────> domain          (reglas e invariantes)
 │
 └──────────────> infrastructure  (repositorio, ObjectStorage)
                        │
                        ▼
                  PostgreSQL / MinIO o S3
```

La respuesta recorre el camino inverso. Los errores de dominio se traducen a HTTP en un
único punto (`shared/errors`), nunca dentro del dominio.

### 3.7 Almacenamiento de objetos

Interfaz conceptual:

```
ObjectStorage          (interfaz — vive en shared/storage)
├── MinIOStorage       (implementación local)
└── S3Storage          (implementación producción)
```

Operaciones conceptuales: guardar objeto, obtener objeto, eliminar objeto, generar URL de
acceso temporal, comprobar existencia.

Reglas:

- **MinIO en local, Amazon S3 en producción.**
- **La lógica de dominio no conoce el proveedor**: recibe la interfaz, no la
  implementación.
- **La base de datos almacena metadatos y claves de objeto, nunca binarios.**
- **Los videos solo almacenan URL, proveedor y metadatos**; jamás archivos de video.
- **Validación de MIME y tamaño** en cada carga (`Task/010`, endurecida en
  `Task/018`).
- **Nombres de objeto no predecibles**, para que conocer una URL no permita adivinar
  otras.
- **URLs prefirmadas previstas para producción**, con expiración.
- **Bucket privado por defecto**; sin acceso público directo.

Cambiar de MinIO a S3 debe requerir cambiar **configuración**, no código de dominio.

#### Estado tras `Task/010` (2026-08-28)

Las tres piezas existen con **código real** en `app/shared/storage/`, y las dos
implementaciones superan **la misma** suite de contrato.

| Elemento | Estado |
| --- | --- |
| `ObjectStorage` | Cinco operaciones: guardar, obtener, comprobar, eliminar y generar acceso temporal. Tipos de resultado propios: no se devuelve ningún objeto del SDK |
| `MinIOStorage` | Local. Exige endpoint explícito y **rechaza** cualquier endpoint de AWS |
| `S3Storage` | Producción. Funciona sin endpoint —lo resuelve el SDK— y **nunca** crea un bucket |
| Selector | `app/shared/storage/fabrica.py`, único punto que sabe que hay más de una implementación. `BLOG_STORAGE_PROVIDER` la elige; `minio` está **prohibido** con `BLOG_APP_ENV=production` |

**Un solo SDK, `boto3`, para las dos** (decisión D-010-A). MinIO implementa el
protocolo S3, así que `boto3` lo ejerce de verdad; el SDK propio de MinIO
arrastraría `pycryptodome` y `argon2-cffi` al único `requirements.txt` —y por
tanto al artefacto de Lambda (P-07)— para código que allí nunca se ejecuta. Lo
que impide que `MinIOStorage` sea un alias vacío de `S3Storage` no es el SDK:
son sus **invariantes**, distintas y probadas por separado.

**Dos endpoints, no uno.** El adaptador distingue el endpoint **operativo** —el
que usa el backend para leer y escribir— del endpoint **de acceso**, contra el
que se firma la URL temporal que se devuelve al cliente. En el entorno local no
coinciden: el backend alcanza MinIO como `http://minio:9000` y el navegador del
host, como `http://localhost:9000`.

La separación es obligatoria, no una comodidad: el `Host` forma parte de la
petición canónica de **AWS Signature Version 4**, así que reescribir el
anfitrión de una URL ya firmada la invalida. El enlace tiene que firmarse contra
el anfitrión externo **desde el principio**, lo que exige un cliente configurado
con él. Construirlo no cuesta ninguna petición de red —prefirmar es aritmética
local—, así que ese cliente funciona aunque su endpoint no sea alcanzable desde
el proceso que lo usa.

El endpoint de acceso es **opcional**: omitido, se firma contra el operativo. En
producción se omite y el SDK resuelve el de AWS; si algún día hay un dominio
propio o un CDN delante del bucket, el mecanismo ya existe, pero **la decisión
es de `Task/030`** (**D-08**).

**El contrato no conoce imágenes ni persistencia.** Importar
`app.shared.storage` no carga SQLAlchemy, FastAPI ni el propio `boto3` —que se
importa dentro de `_crear_cliente`—, y hay una prueba en subproceso que lo
comprueba. La comprobación de uso previa al borrado vive en su caso de uso, no
en el adaptador: meter conocimiento de claves foráneas dentro de un cliente de
S3 rompería la separación que esta interfaz existe para mantener.

### 3.8 Autenticación administrativa — cerrada en `Task/011` (2026-09-01)

**Sesión opaca *server-side* con cookie `HttpOnly`** (**D-02**). El mecanismo no se
eligió por ser el más simple, sino porque es **el único que satisface el contrato
vigente sin coste añadido**: USER_FLOWS.md B.12 exige que cerrar sesión invalide **en el
servidor**, y un token autocontenido no puede hacerlo por construcción.

```
POST /api/v1/admin/auth/login     unico endpoint administrativo publico
POST /api/v1/admin/auth/logout    revoca la sesion EN EL SERVIDOR
GET  /api/v1/admin/auth/me        identidad derivada de la sesion
```

| Pieza | Dónde vive | Qué garantiza |
| --- | --- | --- |
| `shared/security/contrasenas.py` | `shared` | **Argon2id** con los parámetros mínimos de OWASP; verificación, rehash y **verificación señuelo** |
| `shared/security/origen.py` | `shared` | Política de `Origin` para los métodos que cambian estado |
| `shared/security/peticiones.py` | `shared` | Dirección del cliente con **confianza en proxies explícita** y *fail-closed* |
| `authentication/domain/` | módulo | Credencial CSPRNG, huella SHA-256, vigencia de la sesión y reglas de bloqueo. **Python plano** |
| `authentication/application/` | módulo | `IniciarSesion` y `CerrarSesion`. Reciben **puertos**, no adaptadores |
| `authentication/infrastructure/` | módulo | Repositorios, limitador de tasa y reloj |
| `authentication/presentation/` | módulo | Los tres endpoints y **`AdministradorRequerido`**, la protección que reutiliza `Task/012` |
| `audit/domain/acciones.py` | módulo | Catálogo cerrado de las **cuatro** acciones de autenticación |

**Sin middleware de autenticación global.** Proteger `/api/v1` entero convertiría en
privados los diez endpoints públicos de `Task/009`. La protección se aplica **endpoint a
endpoint** mediante una dependencia, y hay una prueba que recorre la especificación
OpenAPI exigiendo que ninguna ruta pública declare seguridad.

**El límite transaccional lo decide `application`.** Un intento fallido **escribe**
—contador, bloqueo, contador de tasa y auditoría—, así que el caso de uso confirma su
propia transacción también en el camino de fallo: señalarlo lanzando haría que la
dependencia de sesión revirtiera todo ese estado defensivo, y el bloqueo no llegaría a
existir nunca.

**Ningún secreto nuevo.** La arquitectura elegida no firma nada, así que no hay clave de
firma que custodiar, rotar ni filtrar.

### 3.9 Configuración

Toda la configuración se lee de **variables de entorno**, se valida al arrancar y falla
rápido si falta algo obligatorio. En local proviene de `.env`; en producción, de SSM
Parameter Store. El código no distingue el origen.

---

## 4. Frontend

### 4.1 Estructura

```
src/
├── app/
├── pages/
├── features/
├── entities/
├── components/
├── services/
├── hooks/
├── lib/
├── styles/
└── assets/
```

### 4.2 Responsabilidades

| Carpeta | Responsabilidad |
| --- | --- |
| `app` | Configuración global, router y providers. |
| `pages` | Composición de rutas. Ensamblan, no implementan. |
| `features` | Funcionalidades completas (editor de artículos, buscador, gestor de medios). |
| `entities` | Modelos del dominio y componentes asociados a ellos. |
| `components` | UI compartida sin conocimiento del dominio. |
| `services` | Cliente HTTP y adaptadores hacia la API. |
| `hooks` | Comportamiento reutilizable. |
| `lib` | Utilidades puras, sin estado ni efectos. |
| `styles` | Tokens de diseño y estilos globales. |
| `assets` | Recursos estáticos empaquetados. |

### 4.3 Reglas de dependencia

```
pages → features → entities → components
              ↘        ↘         ↙
                services, hooks, lib
```

- `components` **no** conoce el dominio ni llama a la API.
- `entities` **no** conoce rutas ni páginas.
- Solo `services` habla HTTP; ningún componente hace `fetch` directamente.
- `lib` no importa de ninguna otra carpeta.

### 4.4 Reglas adicionales

- **Sitio público y panel comparten el mismo sistema de diseño**, con rutas y layouts
  distintos.
- El **código del panel no se descarga en las páginas públicas** (separación por carga
  diferida).
- El frontend **no toma decisiones de autorización**: oculta la interfaz por comodidad,
  pero el backend es quien autoriza.
- La URL del API llega por **variable de entorno en tiempo de build**.
- Todo valor presente en el build del frontend es **público**: nunca contiene secretos.
- **No se adopta ninguna biblioteca visual de terceros.** El sistema de diseño se
  construye con **CSS Modules** y **CSS Custom Properties**, sin dependencias nuevas
  (**D-03** — **Resuelta** y **Vigente** desde el 2026-09-04 en `Task/013`; ver
  [open-decisions.md](open-decisions.md)). Los tokens viven en `src/styles/tokens.css` y
  las primitivas compartidas en `src/components/`, cuya superficie pública es
  `src/components/index.ts`.

---

## 5. Comunicación frontend ↔ backend

| Aspecto | Decisión |
| --- | --- |
| Protocolo | HTTP sobre TLS (en producción). |
| Formato | JSON, UTF-8. |
| Estilo | REST orientado a recursos. |
| Base | `/api/v1` (ver [api-contracts.md](api-contracts.md)). |
| Errores | Modelo común de error con `request_id`. |
| Colecciones | Siempre paginadas. |
| Autenticación | Solo en `/api/v1/admin/*`, salvo `login`. **Sesión opaca en cookie `HttpOnly`**, decidida en `Task/011` (§3.8). |
| CORS | Restringido por ambiente. |
| Correlación | Cada petición lleva o recibe un `request_id` propagado a los logs. |

El frontend **no accede jamás** a PostgreSQL, MinIO ni S3 directamente. Toda lectura o
escritura pasa por el backend, salvo la descarga de imágenes mediante URL prefirmada
emitida por el backend.

---

## 6. Compatibilidad con el destino serverless

El backend debe funcionar igual como proceso local y como función Lambda:

| Restricción | Consecuencia de diseño |
| --- | --- |
| Sin estado entre invocaciones | Ningún **estado de negocio** en memoria de proceso: ni sesiones de usuario en RAM, ni datos de contenido cacheados, ni nada cuya pérdida al terminar la invocación cambie el comportamiento observable. |
| Sin procesos residentes | Ninguna tarea de fondo de larga duración ni scheduler interno. |
| Conexiones efímeras a la base de datos | Conexiones cortas y **pooling externo con PgBouncer** delante de PostgreSQL (`Task/029`). El código solo conoce `DATABASE_URL`. |
| Arranque en frío | Artefacto ligero, importaciones perezosas donde ayude. |
| Sistema de archivos efímero | Ningún dato persistente en disco local. |

**El adaptador Lambda es una capa delgada y removible** (`Task/023`). El código de negocio
lo desconoce.

> **Qué no prohíbe la primera fila** *(precisado en `Task/005.6`)*. Una **caché técnica
> recreable** —un `lru_cache` sobre la configuración, el *engine* de SQLAlchemy o el
> `sessionmaker`— **no es estado de negocio**: memoriza el resultado de leer un entorno que
> no cambia durante la vida del proceso, se reconstruye sola en la invocación siguiente y su
> pérdida no altera ninguna respuesta. Es, de hecho, el patrón correcto para el arranque en
> frío. Lo prohibido es lo que **sustituye a la base de datos o a la sesión**: guardar ahí
> contenido, permisos o sesiones de usuario y asumir que seguirán existiendo.

---

## 7. Qué no define este documento

- Esquema físico de base de datos → `Task/008`.
- ~~Mecanismo de autenticación~~ → **cerrado en `Task/011`** (§3.8).
- ~~Forma de la API administrativa~~ → **cerrada en `Task/012`** (§3.10).
- ~~Biblioteca de componentes visuales y diseño~~ → **cerrada en `Task/013`** (§4.4, **D-03**).
- Editor Markdown concreto → `Task/015`.
- Especificación OpenAPI completa → surge de la implementación (`Task/009`, `Task/012`).

Registro completo: [open-decisions.md](open-decisions.md).

---

## 3.10 API administrativa — cerrada en `Task/012` (2026-09-01)

Es la última pieza del backend funcional del MVP. Contrato completo en
[`api-contracts.md`](api-contracts.md) §14.

### Dónde vive cada cosa

| Pieza | Dónde | Qué garantiza |
| --- | --- | --- |
| `app/api/admin.py` | `api` | La **postura común**: `requiere_administrador`, validación de `Origin`, `no-store` y rechazo de parámetros desconocidos. Un router creado con `router_administrativo()` la trae por el hecho de crearse así |
| `<modulo>/domain/publicacion.py` | módulo | Campos mínimos para publicar, uno por tipo. Python plano |
| `<modulo>/application/administracion.py` | módulo | Casos de uso con nombre propio: crear, actualizar, publicar, despublicar, archivar |
| `<modulo>/infrastructure/repositorio.py` | módulo | Persistencia, incluido el `SELECT … FOR UPDATE` de las transiciones |
| `<modulo>/presentation/{router,schemas}_admin.py` | módulo | Endpoints delgados y DTO de entrada y salida |
| `app/shared/slug.py` | `shared` | Formato y derivación del slug |
| `app/shared/reloj.py` | `shared` | Fuente del instante actual, mudada aquí desde `authentication` |
| `audit/domain/puertos.py` | módulo `audit` | `RegistroDeAuditoria` y `ContextoDeAuditoria`, mudados aquí desde `authentication` |
| `audit/infrastructure/queries.py` | módulo `audit` | **`Task/012.1`.** Consulta paginada del historial. **Sin capa `application`**: es solo lectura, mismo criterio **D-009-Q** que ya aplican las consultas públicas y las de medios |
| `audit/presentation/{router_admin,schemas_admin}.py` | módulo `audit` | **`Task/012.1`.** `GET /admin/audit-events` y su DTO de cinco campos. **Sin repositorio**: el repositorio existe donde hay escritura |

**`app/api/admin.py` no sabe nada del modelo de negocio.** Si lo supiera sería el
constructor genérico que **D-009-R** rechazó por concentrar en `app/api` conocimiento que
ADR-004 reparte entre módulos. Sabe de seguridad y de transporte, y nada más.

### Por qué los cuatro tipos publicables repiten su código

Es la misma postura de **D-P** en `data-model.md` —*«una tabla por tipo, columnas
repetidas»*— y de **D-009-R** en las consultas públicas. Una base común entre tipos
tendría que conocer la validación de publicación, las tablas puente y el ciclo de vida de
los cuatro, que son **reglas de negocio**, y alojarlas fuera de su módulo es justo lo que
ADR-004 prohíbe. Los cuatro tipos, además, **no son el mismo**: `Video` no tiene Markdown
ni se despublica, `BookReview` tiene libro y valoración, `Project` tiene un segundo estado.

Lo que **sí** se comparte es lo genuinamente agnóstico: el slug, el reloj, la paginación,
la envoltura de error y la postura de seguridad.

### Dos mudanzas de `Task/011` a su dueño

Las dos son **refactores sin cambio de comportamiento**: `authentication` reexporta ambas
piezas, así que ninguna de sus firmas cambia.

| Pieza | Estaba en | Está en | Por qué |
| --- | --- | --- | --- |
| `RegistroDeAuditoria`, `ContextoDeAuditoria` | `authentication/domain/puertos.py` | `audit/domain/puertos.py` | Pasó de un consumidor a ocho. Que los cuatro tipos de contenido, el perfil, las etiquetas y los medios importaran el módulo de **autenticación** para escribir en el historial sería una dependencia que no describe ninguna relación real |
| `Reloj`, `RelojDelSistema` | `authentication/{domain,infrastructure}` | `app/shared/reloj.py` | Un reloj no conoce ninguna regla de negocio. Lo necesitan además los cuatro tipos, para fijar `published_at` — que **D-H** describe como *«un momento de negocio que fija el caso de uso con su reloj inyectado»* |

### Límite transaccional

**La petición.** `get_session` confirma al salir y revierte ante cualquier excepción, así
que crear un contenido, asociar sus etiquetas, resolver su portada y auditar es atómico
sin ningún mecanismo nuevo.

`Task/011` confirma **dentro** del caso de uso, pero por una razón que aquí no aplica: su
camino de fallo debe persistir estado defensivo. Aquí un fallo debe revertirlo todo.

### Concurrencia

Las transiciones cargan la fila con `SELECT … FOR UPDATE`: publicar es una
lectura-modificación-escritura sobre el estado, y sin cerrojo dos peticiones simultáneas
prosperan las dos. Es el mismo mecanismo que `Task/011` usó para el contador de intentos
fallidos, no uno nuevo.

**La edición no lleva cerrojo optimista**, y es deliberado: exigiría una columna de
versión —cambio de esquema— para un MVP con **un** administrador. Queda registrado como
deuda.

### Dependencia nueva

**`python-multipart==0.0.32`**, la única de la tarea. La exige FastAPI para leer un
archivo subido: sin ella no se puede declarar `UploadFile`. Es Python puro —rueda
`py3-none-any`—, ocupa ~164 KB y no arrastra dependencias transitivas, así que su impacto
en el artefacto de Lambda es despreciable (P-07).
