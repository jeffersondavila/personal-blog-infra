# TASK-011 — Autenticación administrativa

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/011-Autenticacion-Administrativa` |
| **Nombre** | Autenticación administrativa |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Estado** | **Aprobada** ✔ el 2026-09-01 |
| **Repositorios involucrados** | `personal-blog-backend` (funcional) · `personal-blog-infra` (gobierno y arquitectura) |
| **Repositorio no modificado** | `personal-blog-frontend` — solo lectura, **sin rama** |
| **Dependencias** | `Task/008-Modelo-de-Datos` (**Aprobada** el 2026-08-25) |
| **Rama** | `Task/011-Autenticacion-Administrativa` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base (backend)** | `c1bc0c8b56f19101f38aec65d1c30066996b9236` |
| **SHA base (infra)** | `90469ecfa5cc0cf798bf11317d3969130ac98cf5` |
| **Fecha de inicio** | 2026-08-30 |
| **Última actualización** | 2026-09-01 |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | backend | infra |
| --- | --- | --- | --- |
| 1 | `main == origin/main` | ✔ `c1bc0c8b…` | ✔ `90469ecf…` |
| 2 | Working tree limpio antes de crear la rama | ✔ vacío | ✔ vacío |
| 3 | Rama creada **desde `main`** | ✔ | ✔ |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | ✔ | ✔ |
| 5 | `git rev-list --count main..HEAD` | ✔ `0` | ✔ `0` |
| 6 | `git merge-base --is-ancestor main dev` (preflight) | ✔ exit 0 | ✔ exit 0 |
| 7 | `git diff main dev` (preflight) | ✔ vacío | ✔ vacío |

Ninguna rama nació de `dev`. El frontend permanece en `main`, limpio y sin rama.

---

## 1. Objetivo

Dotar al backend de **autenticación administrativa verificable en el servidor**: iniciar
sesión, cerrar sesión con invalidación real, consultar la sesión actual, y una protección
reutilizable que `Task/012` aplicará al resto de `/api/v1/admin/*`, con hash seguro de
contraseñas, protección contra fuerza bruta, *rate limiting* y auditoría.

## 2. Contexto

`Task/008` dejó el esquema del `Administrator` —incluidos `last_login_at`,
`failed_login_attempts` y `locked_until`— **sin comportamiento**, y el de `AuditEvent`
sin servicio que lo escriba. `Task/009` y `Task/010` construyeron la API pública y el
almacenamiento. `Task/012` no puede empezar sin una autorización que aplicar.

Esta tarea es además el **primer punto del roadmap donde tres decisiones diferidas dejan
de poder aplazarse**: **D-15** (topología lógica), **D-02** (mecanismo de autenticación) y
**D-09** (*rate limiting*).

---

## DECISION BRIEF PRE-IMPLEMENTACIÓN

> **Sección obligatoria, resuelta ANTES del primer archivo productivo.** Las tres
> decisiones se cierran aquí porque las fuentes canónicas vigentes permiten resolverlas
> **sin contradicción**. Las decisiones de esta sección quedaron **Vigentes** el
> **2026-09-01**, con la aprobación de la tarea por el usuario.

### D-15 — Topología lógica de dominios y política de cookies/CORS

#### Restricciones que la determinan

| Fuente | Restricción |
| --- | --- |
| [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md) · [ROADMAP](../project-management/ROADMAP.md) | El frontend se sirve desde **Cloudflare Pages**; el API vive en **API Gateway HTTP API + Lambda**. Son dos plataformas distintas: **no pueden compartir origen sin interponer un componente nuevo**. |
| [software-architecture.md](../architecture/software-architecture.md) §4.4 | Sitio público y panel son **una sola aplicación** con rutas y layouts distintos y carga diferida del panel. No hay dos despliegues de frontend. |
| [security-boundaries.md](../architecture/security-boundaries.md) §2 | `C-01 → C-06` permitido **solo para `login`**; el resto exige sesión válida verificada en el servidor. |
| [non-functional-requirements.md](../architecture/non-functional-requirements.md) S-04 | CORS con orígenes explícitos por ambiente. **Nunca `*` en producción.** |
| **D-07** (`Task/035`) | El **nombre comercial** del dominio no se decide aquí. |

#### Alternativas evaluadas

| # | Topología | Same-site | Same-origin | Cookie | Veredicto |
| --- | --- | :---: | :---: | --- | --- |
| **T-1** | Sitio y panel en `https://example.com`; API en `https://api.example.com` | **Sí** | No | ***First-party*, host-only, `SameSite=Lax`** | **ELEGIDA** |
| T-2 | Sitio en `https://example.com`; API en `https://api-blog.net` (dominio distinto) | No | No | *Cross-site*: obliga a `SameSite=None; Secure` | **Descartada** |
| T-3 | Todo bajo `https://example.com`, con `/api` proxificado hacia API Gateway | Sí | **Sí** | *First-party*, sin CORS | **Descartada** |
| T-4 | Panel en `https://admin.example.com`, separado del sitio público | Sí | No | *First-party* | **Descartada** |

**Por qué se descarta T-2.** Una cookie *cross-site* es, para el navegador, una cookie de
terceros, y su aceptación depende de **políticas de privacidad y de configuraciones que
varían entre navegadores y entre usuarios**. Apoyar la autenticación del panel en un
mecanismo cuya disponibilidad no controla el proyecto añade una fragilidad que aquí es
**innecesaria**: la topología *same-site* mantiene la cookie como *first-party* y no exige
ningún componente adicional. No hay ninguna ventaja de T-2 que compense esa dependencia.

**Por qué se descarta T-3**, pese a ser la más segura en teoría (elimina CORS y el CSRF
*cross-origin* de un plumazo): exige interponer un proxy —un Worker de Cloudflare o una
regla de reescritura— **delante del API Gateway**. Eso es un componente nuevo en el camino
de cada petición, con su costo, su latencia y su modo de fallo, y **no figura en la
arquitectura objetivo aprobada**. Introducirlo aquí sería tomar una decisión de
infraestructura de refilón, dentro de una tarea de backend. Queda registrada como
alternativa disponible si `Task/035` decide poner un CDN delante del API.

**Por qué se descarta T-4.** Añade un segundo despliegue de frontend y contradice
`software-architecture.md` §4.4, que describe **una** aplicación. No aporta aislamiento
real: el panel seguiría siendo código público (C-04, que **no es un límite de seguridad**).

#### Decisión — T-1

```
https://<sitio>            sitio publico  +  panel administrativo en /admin
https://api.<sitio>        API publica y administrativa
        ^
        mismo dominio registrable  ->  SAME-SITE
        distinto origen            ->  CROSS-ORIGIN
```

| Aspecto | Decisión |
| --- | --- |
| **Relación de sitio** | **Same-site.** Mismo esquema y mismo dominio registrable. |
| **Relación de origen** | **Cross-origin.** Difiere el anfitrión. |
| **Cookies** | ***First-party*, host-only** —emitidas por el anfitrión del API, **sin atributo `Domain`**—. Al ser la petición *same-site*, `SameSite=Lax` **se envía igualmente** en `fetch` desde el sitio, incluidos los `POST`. |
| **CORS** | **Lista explícita** del origen del panel, con `Access-Control-Allow-Credentials: true`. **Prohibido `*`** en cualquier respuesta con credenciales. |
| **Nombres concretos** | **No se eligen.** `example.com` y `api.example.com` son ejemplos. Los nombres reales, el DNS y los certificados son **D-07**, en `Task/035`. |
| **Panel** | Ruta `/admin` del mismo origen que el sitio público, no indexable (E-06, `Task/016`). |

#### Qué implementa `Task/011` y qué no

| Aquí | Más tarde |
| --- | --- |
| La **decisión** de topología y sus consecuencias | — |
| Configuración `BLOG_ADMIN_ALLOWED_ORIGINS`: lista explícita, **nunca `*`**, *fail-fast* | — |
| **Validación de `Origin`** en las peticiones administrativas que cambian estado (defensa CSRF) | — |
| Cookie *first-party*, host-only, `HttpOnly`, `SameSite=Lax`, `Secure` por política | — |
| — | **Middleware CORS efectivo y cabeceras de seguridad** → `Task/018` |
| — | **Nombres de dominio, DNS y certificados** (**D-07**) → `Task/035` |
| — | *Throttling* y CORS del API Gateway → `Task/033` |
| — | Consumo desde el panel React → `Task/015` |

> **Por qué `Task/011` NO añade el middleware CORS.** `Task/018` es su propietario
> declarado (S-04, security-boundaries §7) y el consumidor —el panel— es `Task/015`.
> Añadir cabeceras CORS es la mitad que **concede** acceso; la mitad que **protege** es la
> validación de `Origin`, y esa sí se implementa aquí porque la estrategia CSRF de esta
> misma tarea depende de ella. Entregar la concesión antes que el consumidor sería ampliar
> la superficie sin nadie que la use.

---

### D-02 — Mecanismo concreto de autenticación

#### Requisitos duros que cualquier candidato debe satisfacer

| # | Requisito | Fuente |
| --- | --- | --- |
| RQ-1 | **Cerrar sesión invalida en el servidor**, no solo en el navegador | USER_FLOWS B.12 |
| RQ-2 | Toda petición administrativa salvo `login` se verifica **en el servidor** | S-06, security-boundaries §2 |
| RQ-3 | El backend es ***stateless*** entre invocaciones: nada de sesiones en RAM | P-06, software-architecture §6 |
| RQ-4 | **Un solo administrador**, sin roles ni *claims* complejos | MVP_SCOPE §3 |
| RQ-5 | Ningún secreto en el *build* del frontend ni al alcance de JavaScript | software-architecture §4.4, S-08 |
| RQ-6 | Errores de autenticación **genéricos** | api-contracts §7 |

#### Comparación

| Criterio | **A. Sesión opaca *server-side* + cookie `HttpOnly`** | B. JWT de acceso | C. Access + refresh |
| --- | --- | --- | --- |
| **RQ-1 — invalidación real en logout** | **Nativa**: se marca la fila revocada | **No la cumple** sin lista de revocación | Parcial: exige revocar el *refresh* y esperar a que caduque el *access* |
| **Revocación anticipada** | Inmediata, por sesión | Imposible sin denylist | Solo del *refresh* |
| **RQ-3 — *stateless* del proceso** | ✔ el estado vive en PostgreSQL, no en RAM | ✔ | ✔ |
| **Exposición a XSS** | El token **no es legible por JavaScript** | En `localStorage`, **legible**; en cookie, equivale a A pero sin revocación | Igual, con **dos** secretos que proteger |
| **CSRF** | Existe: se mitiga con `SameSite=Lax` + validación de `Origin` | Con `Authorization: Bearer` no hay CSRF; con cookie, igual que A | Igual |
| **Secreto de firma** | **Ninguno**: no hay nada que firmar | Obligatorio, con rotación e invalidación masiva al rotar | Obligatorio |
| **Complejidad** | Una tabla, una consulta indexada | Baja… **hasta que RQ-1 obliga a la denylist**, que es la misma tabla | Alta: rotación, *replay*, reuso |
| **Coste por petición** | 1 `SELECT` por índice único | 0 … o 1 `SELECT` con denylist | 1 `SELECT` |
| **Encaje con Lambda** | ✔ estado en PostgreSQL, que ya es dependencia | ✔ | ✔ |
| **Encaje con `Task/012`, `015` y `018`** | Una dependencia y una cookie | Manejo de token en el cliente | Manejo de dos tokens y refresco |

#### Decisión — A. Sesión opaca *server-side* con cookie `HttpOnly`

**El argumento decisivo no es la simplicidad: es RQ-1.** El contrato vigente exige que
cerrar sesión invalide **en el servidor**. Un JWT no puede hacerlo por construcción —es
una afirmación autocontenida y válida hasta su expiración—, así que cumplir RQ-1 con JWT
obliga a consultar una lista de revocación en cada petición. En ese momento el JWT ha
**perdido su única ventaja** (no consultar estado compartido) y **conserva todos sus
costes**: un secreto de firma que custodiar y rotar, un formato con historial de
vulnerabilidades de implementación, y *claims* que este proyecto no necesita porque
**hay un solo administrador sin roles**.

Se descarta C por lo mismo, elevado: el par *access/refresh* existe para amortizar la
latencia de una verificación centralizada en sistemas con muchos servicios e identidades.
Aquí hay **un** servicio, **un** usuario y una base de datos que ya está en el camino de
cada petición administrativa. Introduce rotación, detección de *replay* y un segundo
secreto en el cliente a cambio de nada.

> Esta decisión **no** se toma por ser «la más simple», sino porque es la única que
> satisface RQ-1 sin coste añadido. Si el proyecto adoptara varios servicios o identidades
> federadas, la comparación cambiaría y exigiría un ADR que reemplace esta decisión.

#### Forma concreta de la sesión

| Aspecto | Valor | Motivo |
| --- | --- | --- |
| **Token** | `secrets.token_urlsafe(32)` → **256 bits** de CSPRNG | §47: nunca `random`, `uuid1` ni derivados del tiempo |
| **Qué recibe el cliente** | Solo la cookie. **El token no aparece en ningún cuerpo JSON** | Si va al JSON, JavaScript lo lee y `HttpOnly` deja de proteger nada |
| **Qué guarda la base** | `sha256(token)` en hexadecimal (64 caracteres) | Un volcado de la tabla no permite suplantar a nadie |
| **Por qué SHA-256 y no Argon2 para el token** | El token es aleatorio de 256 bits: **no hay diccionario que aplicar**. Un KDF lento protege secretos de baja entropía; aquí solo añadiría latencia | Mismo criterio que se aplica a una clave de API |
| **Comparación** | **No se compara el token en claro**: se busca por índice único sobre el hash | §48: no se escribe comparación criptográfica propia |
| **Duración absoluta** | **12 h** (`BLOG_AUTH_SESSION_TTL_SECONDS`, por defecto 43200) | Jornada de trabajo del propietario. Sin renovación deslizante |
| **Renovación / rotación** | **No** en el MVP | Nadie la ha pedido; añadirla sería comportamiento futuro no solicitado |
| **Idle timeout** | **No** | Ídem. La expiración absoluta ya acota la ventana |
| **Sesiones simultáneas** | **Permitidas** | Un propietario con portátil y móvil no debe expulsarse a sí mismo |
| **Qué invalida una sesión** | Expiración (`expires_at`) y revocación explícita (`revoked_at`, vía *logout*) | Son las dos condiciones probadas |
| **Alcance de `logout`** | Revoca **la sesión actual**, no todas | USER_FLOWS B.12 habla de *la* sesión. «Cerrar todas» no lo pide ninguna fuente |

#### Cookie — atributos fijados

| Atributo | Valor | Motivo |
| --- | --- | --- |
| Nombre | `blog_admin_session` (`BLOG_AUTH_COOKIE_NAME`) | — |
| `HttpOnly` | **Sí, siempre** | Es la razón de elegir cookie sobre `localStorage` |
| `Secure` | **`true` por defecto**; `BLOG_AUTH_COOKIE_SECURE=false` **solo** fuera de producción. Con `BLOG_APP_ENV=production`, el valor `false` **impide arrancar** | §20: no se debilita producción para facilitar `localhost` |
| `SameSite` | **`Lax`** | La petición sitio → API es *same-site* (D-15), así que `Lax` **sí** viaja, incluidos los `POST`. Bloquea el `POST` *cross-site* de un atacante |
| `Path` | El prefijo administrativo (`/api/v1/admin`) | La cookie no se envía a los endpoints públicos. Higiene de exposición, **no** una frontera de seguridad |
| `Domain` | **Ausente** → cookie *host-only* | §20: no se comparte con subdominios que no la necesitan |
| `Max-Age` | La duración de la sesión | Coherente con `expires_at` |

#### Estrategia CSRF

**No se afirma que `SameSite` lo resuelva todo.** Se combinan dos capas independientes:

| Capa | Qué cubre | Qué NO cubre |
| --- | --- | --- |
| **1. `SameSite=Lax`** | El navegador **no envía** la cookie en peticiones *cross-site* salvo navegación de nivel superior por `GET`. Eso descarta el `POST`/`DELETE` forjado desde `evil.com` | Una navegación *cross-site* por `GET`. Irrelevante aquí: los endpoints que cambian estado no son `GET`, y la respuesta de `GET /me` no es legible *cross-origin* sin CORS |
| **2. Validación de `Origin`** | En **todo método que cambia estado** (`POST`, `PUT`, `PATCH`, `DELETE`) bajo `/api/v1/admin/*`: si la petición trae `Origin` y **no** está en la lista explícita, se rechaza con `403` | Un cliente que no sea navegador y no envíe `Origin`: pasa. No es una vía CSRF —el CSRF **necesita** el navegador de la víctima y su cookie ambiente, y todo navegador actual envía `Origin` en esos métodos |

**No se implementa un *token* CSRF sincronizado.** Sería una tercera capa cuyo único caso
adicional —un navegador que envíe cookies *same-site* pero omita `Origin` en un `POST`— no
existe en ningún navegador vigente. `Task/018` puede endurecer si aparece un motivo.

> **Consecuencia operativa, dicha sin adornos:** con `BLOG_ADMIN_ALLOWED_ORIGINS` vacío,
> **cualquier petición administrativa que cambie estado y traiga `Origin` se rechaza**. Es
> deliberadamente *fail-closed*: no existe un origen por defecto seguro. El `.env.example`
> lo documenta y las pruebas lo fijan.

---

### D-09 — Herramienta concreta de *rate limiting*

#### Los dos alcances no se confunden

| | **Bloqueo de cuenta** (*account lockout*) | **Límite de tasa** (*rate limit*) |
| --- | --- | --- |
| Protege | **Una cuenta concreta** frente a la adivinación de su contraseña | **El endpoint** frente a ráfagas desde un origen |
| Partición | El administrador | La IP del cliente |
| Estado | `administrators.failed_login_attempts` / `locked_until` (ya existen) | Contador con ventana |
| Se elude con | Muchas IP distintas | Muchas cuentas distintas —aquí solo hay una— |

**Ninguno sustituye al otro** y el roadmap pide los dos. La existencia de
`failed_login_attempts` y `locked_until` **obliga** a implementar el primero; no exime del
segundo.

#### Alternativas evaluadas para el límite de tasa

| # | Mecanismo | Veredicto |
| --- | --- | --- |
| **RL-1** | Contador **en PostgreSQL**, ventana fija, partición por IP | **ELEGIDA** |
| RL-2 | Biblioteca en memoria del proceso (`slowapi` y equivalentes) | **Descartada por la propia restricción de D-09** |
| RL-3 | Redis / ElastiCache | **Descartada** |
| RL-4 | *Throttling* de API Gateway | **Complemento, no mecanismo** |

**RL-2 se descarta por la restricción escrita en D-09**: *«el backend es stateless;
cualquier contador debe vivir fuera del proceso»*. Un contador en RAM se multiplica por el
número de instancias de Lambda y se pierde en cada arranque en frío: con *N* contenedores
tibios, el límite efectivo es *N × límite*. Llamarlo «rate limiting global» sería falso.

**RL-3 se descarta**: introduce un servicio con estado, con su costo mensual y su
operación, **para un endpoint de un blog con un único usuario** (§44). No hay volumen que
lo justifique, y `Task/029` ya reserva los recursos del VPS para PostgreSQL.

**RL-4 no es una alternativa sino una capa distinta**: el *throttling* de API Gateway es
por etapa o por clave de uso, no conoce la IP del cliente como partición de negocio, no
existe en el entorno local y es propiedad de `Task/033`. Se declara como **refuerzo
futuro**, no como el mecanismo de esta tarea.

#### Decisión — RL-1

| Aspecto | Valor |
| --- | --- |
| **Alcance** | Únicamente `POST /api/v1/admin/auth/login` |
| **Partición** | **IP del cliente**, resuelta por la política explícita de más abajo |
| **Ventana** | Fija, **300 s** (`BLOG_AUTH_RATE_LIMIT_WINDOW_SECONDS`) |
| **Límite** | **10 intentos** por ventana (`BLOG_AUTH_RATE_LIMIT_MAX_ATTEMPTS`) |
| **Se cuentan** | **Todos** los intentos, con éxito o sin él |
| **Respuesta al superarlo** | `429` `too_many_requests` con **`Retry-After`** en segundos hasta el fin de la ventana |
| **Persistencia** | Tabla `login_rate_limits`, una fila por partición, actualizada con un **único `INSERT … ON CONFLICT DO UPDATE`** atómico |
| **Multi-instancia** | **Sí es compartido**: el contador vive en PostgreSQL, que todas las instancias comparten |

#### Límites que se declaran honestamente

1. **Ventana fija, no deslizante.** En el peor caso admite hasta **2 × límite** en el
   entorno de dos ventanas contiguas. Aceptado: la alternativa exige guardar una marca por
   intento para un beneficio que aquí no cambia nada.
2. **No protege frente a un atacante distribuido** que rote direcciones IP. Esa dimensión
   la cubre el **bloqueo de cuenta**, que no depende del origen.
3. **Depende de la fiabilidad de la IP observada**, y por eso la confianza en los proxies
   es explícita y *fail-closed*.
4. **No es un limitador global del API.** Solo protege `login`. El endurecimiento
   transversal es de `Task/018`, y el del borde, de `Task/033`.
5. **Sin purga automática de filas caducadas.** No hay procesos residentes
   (software-architecture §6). Es una fila por IP que haya intentado entrar; se registra
   como deuda con propietario.

#### Política de dirección IP

**No se acepta ciegamente `X-Forwarded-For`**: es una cabecera que cualquier cliente puede
escribir, y confiar en su primer valor permitiría a un atacante falsificar una IP por
intento y anular el límite.

| Configuración | Comportamiento |
| --- | --- |
| `BLOG_TRUSTED_PROXY_HOP_COUNT=0` (**por defecto**) | Se **ignora** `X-Forwarded-For` por completo y se usa la dirección del par TCP (`request.client.host`) |
| `BLOG_TRUSTED_PROXY_HOP_COUNT=n` (`n>0`) | Se toma el valor **n-ésimo desde la derecha** de `X-Forwarded-For`, que es el que añadió el proxy de confianza más externo. Los valores a su izquierda son los que el cliente pudo escribir y **no se usan** |
| IP indeterminable | Partición literal `"unknown"`: todas esas peticiones **comparten un único cubo**, que es la opción *fail-closed* |

El valor correcto de `n` para API Gateway y para Traefik lo fijan `Task/033` y el runbook
del entorno local; el **mecanismo** y su valor seguro por defecto son de esta tarea.

---

### Algoritmo de hash de contraseñas

| Aspecto | Decisión |
| --- | --- |
| **Algoritmo** | **Argon2id** |
| **Biblioteca** | `argon2-cffi` |
| **Parámetros** | `time_cost=2`, `memory_cost=19456` KiB (**19 MiB**), `parallelism=1`, `hash_len=32`, `salt_len=16` |
| **Verificación** | `PasswordHasher.verify()` de la biblioteca. **No se escribe ninguna comparación propia** |
| **Detección de rehash** | `PasswordHasher.check_needs_rehash()`, expuesta por la capa propia |
| **Sal** | La genera la biblioteca en cada hash; dos hashes de la misma contraseña **difieren** |

**Por qué Argon2id.** Es el ganador de la *Password Hashing Competition* y la primera
recomendación vigente de OWASP. Los parámetros elegidos son los **mínimos recomendados por
OWASP** para Argon2id, no los máximos: el destino es **AWS Lambda**, donde 64 MiB por
verificación encarecerían la memoria asignada y el arranque en frío (P-07) sin beneficio
real frente a un atacante que primero tendría que superar el límite de tasa y el bloqueo
de cuenta.

**Alternativas consideradas.** `bcrypt` —maduro, pero trunca a 72 bytes y no es
memory-hard—; `hashlib.scrypt` de la biblioteca estándar —aceptable para OWASP y sin
dependencia nueva, pero obligaría a **inventar la serialización** de sal y parámetros y la
lógica de rehash, que es precisamente lo que §45 desaconseja—; `passlib` —descartada: sin
publicación desde 2020 y con incompatibilidades conocidas frente a `bcrypt` 4.x—.

> **Nota sobre una aparente contradicción con `Task/010`.** Aquella tarea rechazó el SDK
> propio de MinIO **porque arrastraba `argon2-cffi` al artefacto de Lambda «para código que
> allí nunca se ejecuta»**. Aquí la situación es la contraria: `argon2-cffi` es exactamente
> el código que **sí** se ejecuta en cada inicio de sesión. La regla que se aplicó entonces
> —no pagar peso por código muerto— es la misma que justifica añadirlo ahora.

### Enumeración de usuarios y tiempos

| Situación | Respuesta |
| --- | --- |
| Correo inexistente | `401` `invalid_credentials`, mensaje genérico |
| Correo válido, contraseña incorrecta | **La misma**: `401` `invalid_credentials` |
| Cuenta **bloqueada** | **La misma**: `401` `invalid_credentials` |
| No existe ningún administrador | **La misma**: `401` `invalid_credentials` (§50: nunca `500`, nunca «no hay administrador configurado») |

**Por qué el bloqueo no se distingue.** Si una cuenta bloqueada respondiera distinto,
bastaría con enviar el umbral de intentos a un correo para saber si existe: el correo real
cambiaría de respuesta y el inventado no. Eso es exactamente la enumeración que
USER_FLOWS B.1 y api-contracts §7 prohíben.

**Coste aceptado, dicho con claridad:** el propietario que se bloquee a sí mismo verá
«credenciales inválidas» durante el bloqueo, sin explicación en la respuesta. El evento
**sí** queda en auditoría y en el log, que es donde el operador puede verlo.

**Tiempos.** Cuando el correo no existe se ejecuta una **verificación señuelo** contra un
hash Argon2id precalculado, y cuando la cuenta está bloqueada la verificación **también**
se ejecuta. Así el trabajo criptográfico es el mismo en los cuatro casos.

> **No se promete resistencia criptográfica al análisis temporal.** No se ha medido, y
> afirmarlo sin medirlo sería falso. Lo que se afirma y se prueba es que **no existe un
> camino que evite el trabajo criptográfico**, que es la diferencia observable grande —de
> milisegundos— que sí permitiría enumerar.

---

### ¿ADR?

**No se crea ADR en esta tarea.** Evaluado contra los criterios de §62:

| Criterio | ¿Se cumple? |
| --- | --- |
| ¿Es estructural? | **Parcialmente.** D-02 no cambia el estilo arquitectónico, ni el despliegue, ni los límites de módulos: es la elección de un mecanismo **dentro** de la arquitectura ya aceptada por ADR-004 |
| ¿Tiene alternativas reales? | Sí, y quedan registradas arriba con su comparación |
| ¿Afecta a varias tareas futuras? | Sí: `Task/012`, `Task/015`, `Task/018`, `Task/033` y `Task/035` |
| ¿La convención vigente lo exige? | **No.** `open-decisions.md` establece que una decisión resuelta *«se marca aquí y — si es estructural — se registra como ADR»*. Los ocho ADR vigentes deciden estilo, repositorios, destino cloud, formato de contenido, laboratorio local, base de datos de producción y observabilidad: **niveles de decisión distintos del que se toma aquí** |

Las tres decisiones se registran, por tanto, en `open-decisions.md` (marcadas
**Resueltas**), en `software-architecture.md`, en `security-boundaries.md`, en
`api-contracts.md` y en esta ficha. Si `Task/018` o `Task/035` necesitaran **cambiar** la
topología de D-15, ese cambio sí sería estructural y exigiría un ADR que lo registre.

---

## 3. Dentro del alcance

Cada casilla se marca contra la implementación **real**, no contra lo planificado.

- [x] Hash de contraseñas con Argon2id en `app/shared/security/contrasenas.py`.
      `argon2-cffi` 25.1.0, parámetros mínimos de OWASP, rehash silencioso y verificación
      señuelo. **22 pruebas**.
- [x] Modelo de sesión opaca en `app/modules/authentication/domain/sesion.py`:
      `secrets.token_urlsafe(32)` (256 bits), huella SHA-256, expiración exclusiva y
      revocación por marca. **15 pruebas**.
- [x] `administrator_sessions` y `login_rate_limits`, con **migración `0003`**.
      `upgrade` → `downgrade` → `upgrade` y `compare_metadata` verificados contra
      PostgreSQL real. `alembic heads` = `0003`.
- [x] `POST /api/v1/admin/auth/login` — único endpoint administrativo público.
- [x] `POST /api/v1/admin/auth/logout` — **revoca en el servidor**; la misma credencial
      presentada después responde `401`.
- [x] `GET /api/v1/admin/auth/me` — identidad derivada de la sesión, nunca del cliente.
- [x] Protección reutilizable: `AdministradorRequerido` / `requiere_administrador`,
      exportadas desde `app.modules.authentication.presentation`.
- [x] Bloqueo de cuenta sobre `failed_login_attempts` y `locked_until`, con
      `SELECT … FOR UPDATE`. Prueba de **concurrencia real con dos conexiones**.
- [x] Límite de tasa en PostgreSQL: 10 intentos / 300 s por IP, `INSERT … ON CONFLICT`
      atómico y `Retry-After`.
- [x] Auditoría de los **cuatro** eventos, sin ningún secreto y sin el correo intentado.
- [x] Cookie `HttpOnly`, `SameSite=Lax`, `Path` administrativo, **sin `Domain`** y
      `Secure` obligatorio en producción.
- [x] Validación de `Origin` en `POST`/`PUT`/`PATCH`/`DELETE` bajo `/admin`.
- [x] Configuración y `.env.example` documentados, **sin ningún secreto** y sin
      *fallback* ejecutable — la arquitectura elegida no necesita ninguno.
- [x] `Cache-Control: no-store` en las tres respuestas.
- [x] **D-02**, **D-09** y **D-15** resueltas y registradas en `open-decisions.md`.

## 4. Fuera del alcance

| Fuera | Propietario |
| --- | --- |
| CRUD administrativo de contenido, medios por HTTP, transiciones de estado | `Task/012` |
| Panel React y su consumo del contrato | `Task/015` |
| Middleware CORS efectivo, cabeceras de seguridad, CSP, endurecimiento de subida | `Task/018` |
| Correlation ID de extremo a extremo y su cabecera concreta | `Task/017` |
| *Throttling* y CORS del borde | `Task/033` |
| Dominio real, DNS y certificados (**D-07**) | `Task/035` |
| Creación del administrador de **producción** | `Task/036` |
| Semilla local *production-like* | `Task/022` |
| SSM Parameter Store | `Task/032` |
| `forgot-password`, `reset-password`, `register`, `change-password` | **Ninguna fuente canónica los asigna.** No existen |

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Hash de contraseñas y primitivas transversales | backend | `app/shared/security/` |
| Módulo de autenticación completo | backend | `app/modules/authentication/` |
| Servicio de auditoría | backend | `app/modules/audit/application/` |
| Migración `0003` | backend | `alembic/versions/` |
| Configuración de autenticación | backend | `app/shared/configuration/settings.py`, `.env.example` |
| Pruebas | backend | `tests/unit/`, `tests/contract/`, `tests/integration/` |
| Ficha y reporte | infra | `docs/tasks/`, `docs/task-reports/` |
| Decisiones y arquitectura | infra | `open-decisions.md`, `software-architecture.md`, `security-boundaries.md`, `api-contracts.md`, `STAGE-03`, `STATUS`, `ROADMAP` |

## 6. Criterios de aceptación

1. **D-15**, **D-02** y **D-09** resueltas y documentadas, con alternativas comparadas.
2. Argon2id operativo; la contraseña **nunca** se persiste, se registra ni se devuelve.
3. Login correcto crea sesión, actualiza `last_login_at` y reinicia el contador de fallos.
4. Correo inexistente, contraseña incorrecta y cuenta bloqueada son **indistinguibles**.
5. `failed_login_attempts` y `locked_until` se usan de verdad, sin perder actualizaciones
   con dos intentos simultáneos.
6. El límite de tasa es **compartido entre instancias** y responde `429` con `Retry-After`.
7. `logout` revoca en el servidor: **la misma credencial ya no autentica**.
8. `/me` deriva la identidad de la sesión real; ausente, inválida, expirada o revocada → `401`.
9. Existe protección reutilizable para `Task/012`.
10. `login` es el **único** endpoint administrativo público.
11. Auditoría de los cuatro eventos, **sin ningún secreto**, con `request_id` e IP.
12. La API pública **sigue siendo anónima**; `Task/009` y `Task/010` en verde.
13. OpenAPI declara **exactamente** los tres endpoints de autenticación y **ningún** CRUD.
14. Migración `0003` aplica, revierte y reaplica contra PostgreSQL real; `0001` y `0002` intactas.
15. Ciclo test-first demostrado por *slice*, con evidencia RED por la razón esperada.

## 7. TDD / Plan test-first

### 7.1 Comportamientos a construir

Hash verificable y no reversible · sesión opaca con expiración y revocación · inicio de
sesión indistinguible ante fallo · bloqueo de cuenta persistente · límite de tasa
compartido · identidad derivada de la sesión · cierre de sesión con revocación real ·
auditoría sin secretos · transporte por cookie con política explícita · contrato OpenAPI.

### 7.2 Matriz de casos

#### Hash de contraseñas

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| H-01 | Contraseña en claro | — | Devuelve un hash Argon2id (`$argon2id$`), distinto de la entrada | unidad |
| H-02 | Hash + contraseña correcta | H-01 | `True` | unidad |
| H-03 | Hash + contraseña incorrecta | H-01 | `False`, sin excepción | unidad |
| H-04 | Misma contraseña, dos hashes | — | **Distintos** (sal aleatoria), y ambos verifican | unidad |
| H-05 | Hash con parámetros antiguos | — | Se señala necesidad de rehash; con los vigentes, no | unidad |
| H-06 | `repr`, log y mensaje de error | — | La contraseña **no aparece** en ninguno | unidad |
| H-07 | Hash malformado | — | `False`, nunca una excepción hacia arriba | unidad |

#### Sesión

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| S-01 | Generar credencial | — | ≥ 43 caracteres URL-safe; dos generaciones **nunca** coinciden | unidad |
| S-02 | Almacenamiento | Sesión creada | La base guarda `sha256(token)`; **el token en claro no está** | integración |
| S-03 | Expiración | `expires_at` pasado | La sesión no es válida | unidad + integración |
| S-04 | Revocación | `revoked_at` puesto | La sesión no es válida | unidad + integración |
| S-05 | Token desconocido | — | No resuelve administrador | integración |
| S-06 | Token revocado | S-04 | No resuelve administrador | integración |
| S-07 | Token expirado | S-03 | No resuelve administrador | integración |
| S-08 | Dos sesiones del mismo administrador | Política: permitidas | Ambas válidas; revocar una **no** invalida la otra | integración |

#### Login

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| L-01 | Credenciales correctas | Administrador existe | `200`, identidad pública, `Set-Cookie` | integración |
| L-02 | Correo inexistente | — | `401` `invalid_credentials` | integración |
| L-03 | Contraseña incorrecta | Administrador existe | `401` `invalid_credentials` | integración |
| L-04 | L-02 frente a L-03 | — | **Cuerpo, `code` y estado idénticos** | integración |
| L-05 | `last_login_at` | L-01 | Se actualiza | integración |
| L-06 | Contador de fallos | Fallos previos + L-01 | Vuelve a `0` y `locked_until` a `NULL` | integración |
| L-07 | Sesión creada | L-01 | Existe una fila válida cuyo hash corresponde a la cookie | integración |
| L-08 | Cuerpo de la respuesta | L-01 | **Ningún** secreto: ni token, ni hash, ni estado defensivo | contrato + integración |
| L-09 | Sin administrador en la base | Base migrada y vacía | `401`, **nunca** `500` ni creación automática | integración |
| L-10 | Cuerpo inválido o campos faltantes | — | `422` con la envoltura del proyecto, **sin la contraseña** | contrato |

#### Bloqueo de cuenta

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| B-01 | 1 fallo | Contador a 0 | Contador a 1, sin bloqueo | integración |
| B-02 | `umbral − 1` fallos | — | Contador a `umbral − 1`, sin bloqueo | integración |
| B-03 | Fallo número `umbral` | — | `locked_until` en el futuro | integración |
| B-04 | Credenciales **correctas** durante el bloqueo | B-03 | `401` **igual** que un fallo cualquiera | integración |
| B-05 | Tras expirar el bloqueo | `locked_until` pasado | Vuelve a admitirse el intento y el contador se reinicia | integración |
| B-06 | Login correcto posterior | B-05 | Contador a 0 y `locked_until` a `NULL` | integración |
| B-07 | **Dos fallos simultáneos** | Dos conexiones reales | Contador final **2**, no 1 | integración |

#### Límite de tasa

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| R-01 | Intentos por debajo del límite | — | Ninguno se rechaza por tasa | integración |
| R-02 | Intento en el límite exacto | — | Todavía se atiende | integración |
| R-03 | Intento por encima | R-02 | `429` `too_many_requests` | integración |
| R-04 | Cuerpo del `429` | R-03 | Envoltura común del proyecto | integración |
| R-05 | `Retry-After` | R-03 | Presente, entero positivo ≤ ventana | integración |
| R-06 | Partición | Dos IP distintas | El cubo de una **no** afecta a la otra | integración |
| R-07 | `X-Forwarded-For` falsificada | `hops = 0` | **Se ignora**: no permite evadir el límite | integración |
| R-08 | Ventana expirada | Ventana anterior agotada | El contador se reinicia y vuelve a admitirse | integración |

#### Sesión actual (`/me`)

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| M-01 | Cookie válida | Sesión viva | `200` con identidad **derivada de la sesión** | integración |
| M-02 | Sin cookie | — | `401` `unauthenticated` | contrato + integración |
| M-03 | Cookie con token desconocido | — | `401` | integración |
| M-04 | Sesión expirada | — | `401` | integración |
| M-05 | Sesión revocada | — | `401` | integración |
| M-06 | Correo ajeno enviado por el cliente | Sesión válida | Se **ignora**: la identidad viene de la sesión | integración |
| M-07 | Campos devueltos | M-01 | Solo `id`, `email` y `display_name` | contrato + integración |

#### Logout

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| O-01 | Cookie válida | Sesión viva | `204` y `revoked_at` puesto **en la base** | integración |
| O-02 | Reutilizar la **misma** credencial | O-01 | `401` en `/me`: revocación **de servidor** | integración |
| O-03 | Auditoría | O-01 | Evento de cierre registrado | integración |
| O-04 | Limpieza en el cliente | O-01 | `Set-Cookie` de borrado con el **mismo `Path`** | integración |
| O-05 | Sin sesión | — | `401`, no `204` | integración |

#### Auditoría

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| A-01 | Login correcto | — | Evento `authentication.login_succeeded` con `actor_id` | integración |
| A-02 | Login fallido | — | Evento `authentication.login_failed`; `actor_id` **nulo** si el correo no existe | integración |
| A-03 | Logout | — | Evento `authentication.logout` | integración |
| A-04 | Bloqueo activado | Umbral alcanzado | Evento `authentication.account_locked` | integración |
| A-05 | `request_id` | Cualquier evento | Presente y coincidente con la respuesta | integración |
| A-06 | IP | Cualquier evento | Presente, según la política de confianza | integración |
| A-07 | Secretos | Todos los eventos | **Ninguno**: ni contraseña, ni hash, ni token, ni cookie, ni correo | integración |
| A-08 | Inmutabilidad | Evento escrito | Las guardas de `Task/008` siguen rechazando `UPDATE` y `DELETE` | integración |
| A-09 | Fallo no revertido | Login fallido por la ruta real | El evento y el contador **persisten** pese al `401` | integración |

#### Cookie y transporte

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| C-01 | `HttpOnly` | L-01 | Presente | contrato |
| C-02 | `Secure` | Según configuración | Presente con `true`; ausente con `false` | contrato |
| C-03 | `SameSite` | L-01 | `Lax` | contrato |
| C-04 | `Path` y `Domain` | L-01 | `Path` = prefijo admin; **sin `Domain`** | contrato |
| C-05 | Secreto en el cuerpo | L-01 | El valor de la cookie **no** aparece en el JSON | contrato |
| C-06 | Borrado en logout | O-01 | Cookie vaciada con el mismo `Path` | contrato |
| C-07 | `Origin` no permitido en `POST` | Lista explícita | `403`, sin tocar credenciales | contrato |
| C-08 | `Origin` permitido | Lista explícita | Se atiende con normalidad | contrato |
| C-09 | Sin `Origin` | — | Se atiende (cliente no navegador) | contrato |
| C-10 | `GET /me` con `Origin` ajeno | — | **No** se rechaza: no cambia estado | contrato |
| C-11 | `Cache-Control` | Las tres respuestas | `no-store` | contrato |
| C-12 | `Secure=false` con `production` | Configuración | **El proceso no arranca** | unidad |

#### OpenAPI

| Caso | Resultado esperado | Capa |
| --- | --- | --- |
| P-01 | `login` **sin** requisito de seguridad | contrato |
| P-02 | `logout` **con** el esquema de seguridad | contrato |
| P-03 | `me` **con** el esquema de seguridad | contrato |
| P-04 | **Cero** rutas de CRUD administrativo | contrato |
| P-05 | Esquema declarado de tipo `apiKey` en `cookie`, con el nombre real | contrato |
| P-06 | Las diez rutas públicas y `/health`, **intactas** | contrato |

#### Configuración

| Caso | Resultado esperado | Capa |
| --- | --- | --- |
| F-01 | Configuración válida construye | unidad |
| F-02 | `BLOG_ADMIN_ALLOWED_ORIGINS` con `*` → **no arranca** | unidad |
| F-03 | Origen malformado → **no arranca** | unidad |
| F-04 | Ningún valor de autenticación sensible en `repr` ni en el mensaje de error | unidad |
| F-05 | **No existe ningún secreto de firma**: la arquitectura elegida no lo necesita | unidad |

### 7.3 Tests RED esperados

Se registran *slice* a *slice* en el reporte, con el comando exacto y el motivo del fallo.
Un test que pase al escribirse **se clasifica como regresión**, no como evidencia RED.

### 7.4 Integración necesaria

**PostgreSQL real** (`personal_blog_test`, con la guarda *fail-closed* vigente) para todo
lo que dependa del motor: el `SELECT … FOR UPDATE` del bloqueo, el `INSERT … ON CONFLICT`
del límite de tasa, la unicidad del hash de sesión, la migración `0003` y el ciclo de vida
completo de la petición. **SQLite queda prohibido** como sustituto. MinIO no interviene.

### 7.5 Casos negativos y de seguridad

No autenticado, sesión inválida, expirada y revocada, credenciales incorrectas, correo
inexistente, cuenta bloqueada, base sin administrador, `Origin` no permitido, cabecera
`X-Forwarded-For` falsificada, exceso de tasa, cuerpo inválido y ausencia de filtraciones
en la respuesta, en la auditoría y en el log.

### 7.6 Regresiones relevantes

Las **792 pruebas** vigentes siguen en verde. En particular: los **diez** endpoints
públicos siguen siendo **anónimos**, el `access_url` de `Task/010` sigue funcionando, las
guardas de inmutabilidad de `AuditEvent` siguen activas, el harness sigue siendo hermético
y `0001` y `0002` no se tocan.

## 8. Plan de validación

Cada criterio de aceptación se comprueba con las pruebas de su fila en la matriz, más los
*quality gates* completos al final y el ciclo real de migraciones contra PostgreSQL.

## 9. Comandos de validación

```bash
ruff check . && ruff format --check . && mypy .
pytest tests/unit -q
pytest tests/contract -q
pytest -m integration -q
pytest -q -W error
pytest --cov -q
pip check
git diff --check
alembic heads
```

## 10. Evidencia esperada

Salida de RED y GREEN por *slice*, resultado de la suite completa, cobertura, ciclo
`upgrade` / `downgrade` / `upgrade` de la migración `0003` y el contenido real de la
especificación OpenAPI. Se registra en el reporte de la tarea.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | El bloqueo de cuenta puede dejar fuera al **único** administrador | Alto | Bloqueo **temporal**, nunca permanente; duración configurable; el operador ve el evento en auditoría |
| 2 | Confiar en `X-Forwarded-For` permitiría evadir el límite de tasa | Alto | *Fail-closed*: se ignora salvo confianza declarada explícitamente |
| 3 | La ventana fija admite hasta 2 × límite en su frontera | Bajo | Declarado; el bloqueo de cuenta cubre la dimensión que importa |
| 4 | `argon2-cffi` es una dependencia binaria en el artefacto de Lambda | Medio | Rueda `manylinux` disponible; **debe verificarse al empaquetar** en `Task/024` y `Task/032` |
| 5 | Las tablas de estado de autenticación no se purgan: `login_rate_limits` y `administrator_sessions` | Bajo | Una fila por IP observada y una por inicio de sesión con éxito; `login_rate_limits` es la fuente mayor. La purga se registra como deuda con propietario (**R-44**) |
| 6 | Una autenticación pensada por simplicidad puede ser insegura | Alto | Riesgo ya previsto por la ETAPA 03; `Task/018` revisa el endurecimiento |

## 12. Decisiones técnicas

| Id | Decisión | Alternativas | Justificación | ¿ADR? |
| --- | --- | --- | --- | --- |
| D-011-A | **Topología T-1**: sitio y panel en el dominio raíz, API en subdominio | Dominios separados; mismo origen con proxy; panel en subdominio | *Same-site* sin componentes nuevos; cookies *first-party*, sin depender de la aceptación de cookies de terceros | No |
| D-011-B | **Sesión opaca *server-side* con cookie `HttpOnly`** | JWT; access + refresh | Única opción que cumple la invalidación en el servidor sin coste añadido | No |
| D-011-C | Token `secrets.token_urlsafe(32)`, almacenado como `sha256` | Guardar el token; usar un KDF lento sobre él | 256 bits de entropía no admiten diccionario; un volcado de la tabla no permite suplantar | No |
| D-011-D | Duración **absoluta** de 12 h, sin renovación ni *idle timeout* | Deslizante; refresh | Nadie lo pide; añadirlo sería comportamiento futuro no solicitado | No |
| D-011-E | **Sesiones simultáneas permitidas**; `logout` revoca solo la actual | Sesión única; «cerrar todas» | USER_FLOWS B.12 habla de *la* sesión | No |
| D-011-F | **Argon2id** con los parámetros mínimos de OWASP | bcrypt; `hashlib.scrypt`; passlib | Recomendación vigente, con rehash y verificación de la biblioteca; parámetros aptos para Lambda | No |
| D-011-G | Bloqueo tras **5** fallos durante **15 min**, con reinicio al expirar | Retardo exponencial; bloqueo permanente | Acota la adivinación sin dejar al propietario fuera de forma permanente | No |
| D-011-H | Concurrencia del bloqueo con **`SELECT … FOR UPDATE`** | `UPDATE` atómico con `CASE`; sin protección | Serializa los intentos de la misma cuenta y mantiene la lógica legible y probable | No |
| D-011-I | **Límite de tasa en PostgreSQL**, ventana fija de 300 s y 10 intentos por IP | Memoria del proceso; Redis; solo API Gateway | Único mecanismo compartido entre instancias sin infraestructura nueva | No |
| D-011-J | IP con **confianza en proxies explícita** y `hops = 0` por defecto | Primer valor de `X-Forwarded-For`; siempre el par TCP | *Fail-closed*: una cabecera falsificable no decide la partición | No |
| D-011-K | CSRF con **`SameSite=Lax` + validación de `Origin`**, sin *token* sincronizado | Solo `SameSite`; *token* CSRF | Dos capas independientes; la tercera no cubriría ningún caso vigente | No |
| D-011-L | La cuenta bloqueada responde **igual** que unas credenciales inválidas | Responder `423` o `429` distintivo | Distinguir permitiría enumerar el correo real | No |
| D-011-M | **Verificación señuelo** cuando el correo no existe, y también con la cuenta bloqueada | Salir antes | Elimina el atajo que evita el trabajo criptográfico | No |
| D-011-N | El caso de uso **confirma su transacción** antes de devolver el fallo | Dejar que el `401` la revierta | Sin esto, el contador de fallos, el límite de tasa y la auditoría se perderían con el error | No |
| D-011-O | `require_administrator` vive en el **módulo** `authentication`, no en `shared/security` | Colocarlo en `shared`, como sugiere la tabla de §3.4 | `shared` no puede depender de un módulo de negocio; `shared/security` conserva las primitivas transversales | No |
| D-011-P | **Sin middleware CORS** en esta tarea | Añadirlo aquí | `Task/018` es su propietario y `Task/015` su consumidor; la mitad protectora —`Origin`— sí se entrega | No |
| D-011-Q | **Ningún secreto de firma** en la configuración | Reservar `JWT_SECRET` «por si acaso» | §37: la arquitectura elegida no lo necesita, y un secreto sin uso solo es superficie | No |
| D-011-R | **Sin ADR** | Crear ADR-009 | La decisión no es estructural en el sentido de los ocho ADR vigentes; queda registrada en las fuentes canónicas | No |

## 13. Documentación creada o actualizada

| Documento | Qué cambió |
| --- | --- |
| `docs/tasks/TASK-011-administrative-authentication.md` | **Creado** — esta ficha, con el *Decision Brief* y la matriz |
| `docs/task-reports/TASK-011-report.md` | **Creado** — reporte de ejecución |
| `docs/project-management/STATUS.md` | Tarea en curso, estado y riesgos |
| `docs/project-management/ROADMAP.md` | Estado de `Task/011` |
| `docs/stages/STAGE-03-domain-and-backend.md` | Estado y criterios de salida |
| `docs/architecture/open-decisions.md` | **D-02, D-09 y D-15 → Resueltas** |
| `docs/architecture/software-architecture.md` | Mecanismo de autenticación; precisión sobre `shared/security` |
| `docs/architecture/security-boundaries.md` | CSRF, *rate limiting* y política de IP |
| `docs/architecture/api-contracts.md` | Contrato de los tres endpoints |
| `docs/architecture/data-model.md` | Tablas nuevas y migración `0003` |
| `personal-blog-backend/.env.example` | Sección de autenticación, solo placeholders |

## 14. Archivos modificados

### `personal-blog-backend` — modificados

`app/main.py` · `app/modules/authentication/infrastructure/models.py` ·
`app/shared/configuration/settings.py` · `app/shared/errors/exceptions.py` ·
`app/shared/errors/handlers.py` · `pyproject.toml` · `requirements.txt` ·
`.env.example` · `tests/contract/test_openapi_publica.py` ·
`tests/integration/conftest.py` · `tests/test_openapi.py`

### `personal-blog-backend` — creados

`alembic/versions/20260831_0003_sesiones_administrativas_y_limite_de_acceso.py` ·
`app/shared/security/` (`contrasenas.py`, `peticiones.py`, `origen.py`) ·
`app/modules/authentication/{domain,application,presentation}/` ·
`app/modules/authentication/infrastructure/{repositorios,limitador,reloj}.py` ·
`app/modules/audit/domain/acciones.py` ·
`app/modules/audit/infrastructure/registro.py` · **13 módulos de prueba nuevos**

### `personal-blog-infra`

Ficha, reporte y los ocho documentos de la tabla anterior.

### `personal-blog-frontend`

**Ninguno.** Sin rama y sin cambios.

## 15. Resultado de pruebas

| Prueba | Comando | Resultado |
| --- | --- | --- |
| Lint | `ruff check .` | **All checks passed!** |
| Formato | `ruff format --check .` | **220 files already formatted** |
| Tipado | `mypy .` | **Success: no issues found in 218 source files** |
| Suite completa + cobertura | `pytest --cov -q -W error -rs` | **1046 pasan · 1 omitida · 0 fallos · 0 errores · 0 advertencias** · 97,93 s |
| Cobertura | idem | **100 %** — 0 sentencias y 0 ramas sin cubrir |
| Dependencias | `pip check` | **No broken requirements found** |
| Migraciones | `alembic heads` | `0003 (head)` |
| Espacios | `git diff --check` | Sin problemas |

**Única omisión:** `test_la_variable_tz_no_altera_el_timestamp` — `time.tzset` no existe
en Windows. **Preexistente de `Task/005`**; `Task/011` no añade ninguna.

## 16. Problemas encontrados

Ocho, todos registrados con su causa y su corrección en el
[reporte §T](../task-reports/TASK-011-report.md). Los dos que más enseñan:

1. **Contaminación entre pruebas por `ON DELETE RESTRICT`.** La primera suite completa
   dio **48 fallos que no aparecían al ejecutar los módulos por separado**: la limpieza
   borraba el administrador antes que sus eventos de auditoría, la clave foránea lo
   rechazaba dentro de un `finally`, y la fila superviviente bloqueaba —por el `UNIQUE`
   del *singleton*— a todas las pruebas posteriores. Se resolvió con
   `limpiar_autenticacion`, que borra en orden de dependencias. **Es un defecto del
   andamiaje, no del código productivo**, y lo que demuestra es que el `RESTRICT` de
   `Task/008` funciona.
2. **Un nombre de cookie configurable habría hecho mentir a OpenAPI**, porque FastAPI
   construye el esquema de seguridad al definir las rutas. La variable se **retiró**.

## 17. Pasos de validación para el usuario

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-backend

# 1. Estado de la rama: sin commits, sin staging.
git branch --show-current
git rev-list --count main..HEAD      # 0

# 2. Gates estaticos.
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m mypy .
.venv\Scripts\python -m pip check

# 3. Suite completa contra PostgreSQL real, con cobertura y sin advertencias.
#    Exporta SOLO estas variables: cargar el .env de infra entero introduce TZ=UTC
#    y hace que una prueba de zona horaria se auto-omita.
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog_test"
$env:PERSONAL_BLOG_TEST_STORAGE_ENDPOINT_URL = "http://127.0.0.1:9000"
$env:PERSONAL_BLOG_TEST_STORAGE_ACCESS_KEY = "<MINIO_ROOT_USER>"
$env:PERSONAL_BLOG_TEST_STORAGE_SECRET_KEY = "<MINIO_ROOT_PASSWORD>"
.venv\Scripts\python -m pytest --cov -q -W error -rs

# 4. Migraciones.
$env:BLOG_DATABASE_URL = $env:PERSONAL_BLOG_TEST_DATABASE_URL
.venv\Scripts\python -m alembic heads        # 0003 (head)
.venv\Scripts\python -m alembic history

# 5. Los tres endpoints en la especificacion, y ningun CRUD administrativo.
.venv\Scripts\python -c "import json;from app.main import create_app;from fastapi.testclient import TestClient;d=TestClient(create_app()).get('/openapi.json').json();print(sorted(r for r in d['paths'] if 'admin' in r))"
```

**Comprobación pendiente que requiere Docker** —deliberadamente no ejecutada, porque el
alcance de la sesión excluía tocarlo—: reconstruir la imagen del backend para confirmar
que `argon2-cffi` se instala en Linux. La rueda `manylinux_2_17_x86_64` **existe y se
verificó descargándola** para `--python-version 3.12`; falta la construcción real.

## 18. Deuda técnica pendiente

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | **Las tablas de estado de autenticación no se purgan** (**R-44**). `login_rate_limits` crece por **dirección IP observada** y es la fuente de crecimiento potencialmente mayor; `administrator_sessions` crece por **inicio de sesión con éxito**, y las filas caducadas o revocadas permanecen. No hay procesos residentes que las limpien; el volumen es despreciable con un único administrador, pero el crecimiento es monótono | `Task/018` o `Task/029` |
| 2 | **La imagen Docker no se reconstruyó** tras añadir una dependencia binaria | Comprobación del usuario · `Task/024`/`Task/032` |
| 3 | **El inicio de sesión desde navegador en local exige DOS variables, todavía no cableadas en el Compose local.** (A) **`BLOG_ADMIN_ALLOWED_ORIGINS`** con el origen real del panel: es *fail-closed*, y sin él la validación de `Origin` rechaza los `POST` del navegador. (B) **`BLOG_AUTH_COOKIE_SECURE=false`**, porque el entorno local actual sirve por **HTTP** y una cookie `Secure` no se conserva ni se reenvía sobre HTTP. **Hacen falta las dos**: con una sola, el inicio de sesión desde navegador sigue sin funcionar. No se añaden aquí porque el consumidor real del contrato todavía no existe | `Task/015` |
| 4 | **La resistencia al análisis temporal no está medida.** Se garantiza que no queda ningún camino que evite el trabajo criptográfico; nada más | `Task/018`, si se mide |
| 5 | **Los saltos de proxy de confianza no están fijados** para Traefik ni API Gateway. El mecanismo existe con el valor seguro por defecto | Runbook local · `Task/033` |

## 19. Próxima tarea

`Task/012-API-Administrativa` — CRUD de contenido, borradores, publicación, archivado y
gestión de imágenes, protegido con la dependencia que entrega esta tarea.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-01** |
| **Aprobado por** | **jeffersondavila** (usuario) |
| **Expresión de aprobación** | `approved: Task/011-Autenticacion-Administrativa` |
| **Efecto en el avance** | Avance global **11 de 41 (27 %)**; ETAPA 03 en **4 de 5 (80 %)** |
| **Decisiones promovidas** | **D-15**, **D-02** y **D-09** pasan de *propuesta* a **Vigentes**; **D-011-A** a **D-011-R**, **Vigentes** |

> Esta sección solo se completa cuando el usuario autoriza explícitamente la aprobación.
> Claude nunca la completa por iniciativa propia. La autorización se recibió con la
> expresión exacta `approved: Task/011-Autenticacion-Administrativa`.
