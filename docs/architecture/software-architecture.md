# Arquitectura de software

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/002-Definir-MVP-y-Arquitectura` (2026-07-26) |
| **Fecha** | 2026-07-26 |

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
    └── configuration/
```

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
| `audit` | Registro inmutable de acciones administrativas. |

### 3.4 Responsabilidad de `shared`

| Paquete | Responsabilidad |
| --- | --- |
| `database` | Sesión, unidad de trabajo, base de los modelos ORM. |
| `storage` | Interfaz `ObjectStorage` y sus implementaciones. |
| `security` | Hash de contraseñas, dependencias de autorización, cabeceras de seguridad. |
| `logging` | Logs JSON y propagación del correlation ID. |
| `pagination` | Parámetros y envoltura de colección paginada. |
| `errors` | Jerarquía de errores de dominio y su traducción a HTTP. |
| `configuration` | Carga y validación de configuración desde variables de entorno. |

`shared` contiene **capacidades técnicas transversales**, nunca reglas de negocio.

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
- **Validación futura de MIME y tamaño** en cada carga (`Task/010`, endurecida en
  `Task/018`).
- **Nombres de objeto no predecibles**, para que conocer una URL no permita adivinar
  otras.
- **URLs prefirmadas previstas para producción**, con expiración.
- **Bucket privado por defecto**; sin acceso público directo.

Cambiar de MinIO a S3 debe requerir cambiar **configuración**, no código de dominio.

### 3.8 Configuración

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
- **Todavía no se selecciona una biblioteca visual concreta** (ver
  [open-decisions.md](open-decisions.md)).

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
| Autenticación | Solo en `/api/v1/admin/*`. Mecanismo concreto pendiente (`Task/011`). |
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
| Sin estado entre invocaciones | Nada de cachés en memoria de proceso ni sesiones en RAM. |
| Sin procesos residentes | Ninguna tarea de fondo de larga duración ni scheduler interno. |
| Conexiones efímeras a la base de datos | Uso de conexiones cortas o pooling externo (`Task/029`). |
| Arranque en frío | Artefacto ligero, importaciones perezosas donde ayude. |
| Sistema de archivos efímero | Ningún dato persistente en disco local. |

**El adaptador Lambda es una capa delgada y removible** (`Task/023`). El código de negocio
lo desconoce.

---

## 7. Qué no define este documento

- Esquema físico de base de datos → `Task/008`.
- Mecanismo de autenticación → `Task/011`.
- Biblioteca de componentes visuales y diseño → `Task/013`.
- Editor Markdown concreto → `Task/015`.
- Especificación OpenAPI completa → surge de la implementación (`Task/009`, `Task/012`).

Registro completo: [open-decisions.md](open-decisions.md).
