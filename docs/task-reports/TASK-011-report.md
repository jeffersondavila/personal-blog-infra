# TASK-011 — Reporte de ejecución

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/011-Autenticacion-Administrativa` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Estado** | **Aprobada** ✔ el 2026-09-01 |
| **Aprobado por** | **jeffersondavila** (usuario) |
| **Expresión de aprobación** | `approved: Task/011-Autenticacion-Administrativa` |
| **Fecha** | 2026-09-01 |
| **Ficha** | [TASK-011](../tasks/TASK-011-administrative-authentication.md) |
| **Repositorios modificados** | `personal-blog-backend` · `personal-blog-infra` |
| **Repositorio no modificado** | `personal-blog-frontend` — **sin rama y sin cambios** |

---

## A. Preflight y ramas

| Comprobación | backend | infra | frontend |
| --- | --- | --- | --- |
| `main == origin/main` antes de crear | ✔ `c1bc0c8b…` | ✔ `90469ecf…` | ✔ `fd62f221…` |
| Working tree limpio antes de crear | ✔ vacío | ✔ vacío | ✔ vacío |
| `git merge-base --is-ancestor main dev` | ✔ exit 0 | ✔ exit 0 | *no aplica* |
| `git rev-list --count dev..main` | ✔ `0` | ✔ `0` | *no aplica* |
| `git diff main dev` | ✔ vacío | ✔ vacío | *no aplica* |
| Rama creada **desde `main`** | ✔ | ✔ | **sin rama** |
| `HEAD == main` justo tras crearla | ✔ | ✔ | — |
| `git rev-list --count main..HEAD` | ✔ `0` | ✔ `0` | — |

**¿Alguna rama nació de `dev`?** **NO.** El frontend permanece en `main`, limpio y
sin rama: la tarea no lo modifica.

---

## B. D-15 — Topología lógica de dominios · **RESUELTA**

### Alternativas evaluadas

| # | Topología | Veredicto |
| --- | --- | --- |
| **T-1** | Sitio y panel en el dominio raíz; API en `api.<dominio>` | **ELEGIDA** |
| T-2 | Dominios registrables distintos | Descartada: la cookie sería *cross-site*, es decir, **de terceros**, y la autenticación quedaría sujeta a políticas de privacidad y a configuraciones que **varían entre navegadores y entre usuarios**. Esa dependencia es evitable: la topología *same-site* conserva la cookie como *first-party* y elimina la fragilidad **sin añadir ningún componente** |
| T-3 | Mismo origen, con `/api` proxificado hacia API Gateway | Descartada **pese a ser la más segura en teoría**: elimina CORS y el CSRF *cross-origin*, pero exige interponer un componente nuevo —un Worker o una regla de reescritura— en el camino de cada petición, con su costo, su latencia y su modo de fallo, y **no figura en la arquitectura objetivo aprobada**. Queda registrada como alternativa si `Task/035` pone un CDN delante del API |
| T-4 | Panel en `admin.<dominio>`, separado del sitio | Descartada: exige un segundo despliegue de frontend y contradice `software-architecture.md` §4.4, que describe **una** aplicación. No aporta aislamiento real —C-04 no es un límite de seguridad— |

### Decisión

```
https://<sitio>            sitio publico  +  panel administrativo en /admin
https://api.<sitio>        API publica y administrativa
```

| Aspecto | Valor |
| --- | --- |
| **Same-site** | **Sí.** Mismo esquema y mismo dominio registrable |
| **Same-origin** | **No.** Difiere el anfitrión |
| **Implicación para la cookie** | ***First-party*, host-only** (sin atributo `Domain`). Al ser la petición *same-site*, **`SameSite=Lax` viaja igualmente**, también en `POST` |
| **CORS conceptual** | Lista **explícita** del origen del panel con `Access-Control-Allow-Credentials: true`. **`*` prohibido**: la configuración **no arranca si se declara `*` como origen permitido**. Declarar uno o varios orígenes concretos es el uso previsto y arranca con normalidad |
| **Nombres reales** | **No se eligen.** `example.com` es un ejemplo |

### Reparto

| Aquí (`Task/011`) | Más tarde |
| --- | --- |
| La decisión y sus consecuencias | — |
| `BLOG_ADMIN_ALLOWED_ORIGINS`, con validación *fail-fast* y `*` prohibido | — |
| **Validación de `Origin`** en métodos que cambian estado | — |
| Cookie *first-party*, `HttpOnly`, `SameSite=Lax`, `Secure` por política | — |
| — | **Middleware CORS efectivo y cabeceras de seguridad** → **`Task/018`** |
| — | **Dominio concreto, DNS y certificados** (**D-07**) → **`Task/035`** |
| — | *Throttling* y CORS del borde → `Task/033` |
| — | Consumo desde el panel React → `Task/015` |

> **Por qué `Task/011` no instala el middleware CORS.** Añadir cabeceras CORS es la
> mitad que **concede** acceso, y su propietario declarado es `Task/018` (S-04,
> security-boundaries §7); su consumidor, `Task/015`. La mitad que **protege** —la
> validación de `Origin`— sí se entrega aquí, porque la estrategia CSRF de esta misma
> tarea depende de ella.

---

## C. D-02 — Mecanismo de autenticación · **RESUELTA**

### Comparación

| Criterio | **A. Sesión opaca + cookie `HttpOnly`** | B. JWT | C. Access + refresh |
| --- | --- | --- | --- |
| Logout invalida en el servidor | **Nativo** | **No lo cumple** sin denylist | Parcial |
| Revocación anticipada | Inmediata | Imposible sin denylist | Solo del *refresh* |
| Secreto de firma | **Ninguno** | Obligatorio | Obligatorio |
| Legible por JavaScript | **No** | Sí en `localStorage` | Sí |
| Coste por petición | 1 `SELECT` indexado | 0 … o 1 con denylist | 1 |
| Complejidad | Una tabla | Baja **hasta** que la denylist la iguala | Rotación y *replay* |

### Decisión — A, y el argumento no es la simplicidad

**Es RQ-1.** USER_FLOWS.md B.12 exige que cerrar sesión **invalide en el servidor**.
Un JWT no puede hacerlo por construcción —es una afirmación autocontenida, válida
hasta su expiración—, así que cumplir ese contrato con JWT obliga a consultar una
lista de revocación en cada petición. En ese momento el JWT **ha perdido su única
ventaja** —no consultar estado compartido— y **conserva todos sus costes**: un
secreto de firma que custodiar y rotar, y *claims* que este proyecto no necesita
porque hay **un solo administrador sin roles**.

C se descarta por lo mismo, elevado: el par *access/refresh* amortiza la latencia de
una verificación centralizada en sistemas con muchos servicios e identidades. Aquí
hay **un** servicio, **un** usuario y una base de datos que ya está en el camino de
cada petición administrativa.

| Aspecto | Valor |
| --- | --- |
| **Logout server-side** | `administrator_sessions.revoked_at`. Probado presentando **la misma credencial** después del cierre: `401` |
| **Duración** | **12 h absolutas**. Sin renovación deslizante, sin *idle timeout* |
| **Almacenamiento en cliente** | **Solo la cookie `HttpOnly`.** La credencial **no aparece en ningún cuerpo JSON**, y hay prueba que lo fija |
| **CSRF** | `SameSite=Lax` **+** validación de `Origin` (sección L) |
| **Sesiones simultáneas** | Permitidas. `logout` revoca **la actual**, no todas |

---

## D. D-09 — *Rate limiting* · **RESUELTA**

### Los dos alcances no se confunden

| | Bloqueo de cuenta | Límite de tasa |
| --- | --- | --- |
| Protege | **Una cuenta** frente a la adivinación de su contraseña | **El endpoint** frente a ráfagas |
| Partición | El administrador | La IP del cliente |
| Se elude con | Muchas IP | Muchas cuentas —aquí solo hay una— |

**Ninguno sustituye al otro, y el roadmap pide los dos.**

### Alternativas

| # | Mecanismo | Veredicto |
| --- | --- | --- |
| **RL-1** | Contador en **PostgreSQL**, ventana fija, partición por IP | **ELEGIDA** |
| RL-2 | Memoria del proceso (`slowapi` y similares) | **Descartada por la restricción escrita en la propia D-09**: *«el backend es stateless; cualquier contador debe vivir fuera del proceso»*. Con `N` instancias tibias el límite efectivo sería `N × límite`, y llamarlo «límite global» sería falso |
| RL-3 | Redis / ElastiCache | Descartada: un servicio con estado, su costo y su operación **para un endpoint de un blog con un usuario** |
| RL-4 | *Throttling* de API Gateway | **No es alternativa sino otra capa**: es por etapa o clave de uso, no conoce la IP como partición, no existe en local y es de `Task/033`. Queda como **refuerzo futuro** |

### Configuración y garantías

| Aspecto | Valor |
| --- | --- |
| Alcance | Solo `POST /api/v1/admin/auth/login` |
| Partición | IP del cliente, según la política de confianza en proxies |
| Ventana / límite | **300 s / 10 intentos** |
| Se cuentan | **Todos** los intentos, acertados o no |
| Respuesta | `429` `too_many_requests` con **`Retry-After`** (entero ≥ 1, ≤ ventana) |
| **Atomicidad** | Un **único** `INSERT … ON CONFLICT DO UPDATE` con `CASE` y `RETURNING`. El motor toma el cerrojo de fila y resuelve lectura, decisión y escritura sin hueco. La alternativa —leer, sumar en Python, escribir— pierde actualizaciones justo cuando el límite tiene algo que hacer |
| **Multi-instancia** | **Sí es compartido**: el contador vive en PostgreSQL |

### Limitaciones declaradas, no disimuladas

1. **Ventana fija.** En la frontera entre dos ventanas admite hasta **2 × límite**.
2. **No protege frente a un atacante distribuido** que rote IP. Esa dimensión la cubre
   el bloqueo de cuenta.
3. **Depende de la fiabilidad de la IP observada**; de ahí la política *fail-closed*.
4. **No es un limitador global del API.** Solo `login`. Lo transversal es de `Task/018`.
5. **Sin purga automática** de filas caducadas: no hay procesos residentes. Deuda
   registrada con propietario.

---

## E. Hash de contraseñas — Argon2id

| Aspecto | Valor |
| --- | --- |
| **Algoritmo** | Argon2id |
| **Biblioteca** | `argon2-cffi` **25.1.0** (con `argon2-cffi-bindings`) |
| **Parámetros** | `time_cost=2`, `memory_cost=19456` KiB (**19 MiB**), `parallelism=1`, `hash_len=32`, `salt_len=16` |
| **Origen de los parámetros** | Los **mínimos recomendados por OWASP** para Argon2id. No los máximos: el destino es Lambda, donde la variante de 64 MiB encarecería memoria y arranque en frío (P-07) sin beneficio proporcional frente a un atacante que primero tendría que atravesar el límite de tasa y el bloqueo |
| **Verificación** | `PasswordHasher.verify()` de la biblioteca. **Ninguna comparación propia** |
| **Rehash** | `check_needs_rehash()`, expuesto como `necesita_rehash`. Se aplica **en el acceso correcto**, que es el único momento en que la contraseña en claro existe para recalcular. El propietario no se entera |
| **Verificación señuelo** | Hash Argon2id calculado sobre un valor **aleatorio de 256 bits generado en cada arranque**. Se ejecuta cuando el correo no existe **y también cuando la cuenta está bloqueada** |
| **Longitud del hash** | ≤ 255, fijado por prueba contra `LONGITUD_DE_HASH` del esquema |

**Alternativas consideradas:** `bcrypt` —trunca a 72 bytes, no es *memory-hard*—;
`hashlib.scrypt` —aceptable para OWASP y sin dependencia nueva, pero obligaría a
**inventar la serialización** de sal y parámetros y la lógica de rehash, que es
precisamente lo que el proyecto no quiere escribir a mano—; `passlib` —sin
publicación desde 2020, con incompatibilidades conocidas frente a `bcrypt` 4.x—.

**Nota sobre una aparente contradicción con `Task/010`.** Aquella tarea rechazó el SDK
de MinIO **porque arrastraba `argon2-cffi` «para código que allí nunca se ejecuta»**.
Aquí es exactamente el código que **sí** se ejecuta en cada inicio de sesión: la regla
—no pagar peso por código muerto— es la misma y ahora justifica añadirlo.

---

## F. Modelo de sesión

| Aspecto | Valor |
| --- | --- |
| **Token** | `secrets.token_urlsafe(32)` |
| **Entropía** | **256 bits**, fijada por prueba (`entropia_minima_en_bits() >= 256`) |
| **Qué recibe el cliente** | Solo la cookie |
| **Qué guarda la base** | `sha256(token)` en hexadecimal, 64 caracteres, con **índice único** |
| **Por qué SHA-256 y no Argon2** | El token es aleatorio de 256 bits: **no hay diccionario que aplicar**. Un KDF lento protege secretos de baja entropía; aquí solo añadiría latencia a cada petición administrativa. Mismo criterio que se aplica a una clave de API |
| **Comparación** | **No se compara el token en claro**: se busca por índice único sobre la huella. No existe ninguna comparación criptográfica propia que pueda escribirse mal |
| **Lo que NO se promete** | Que el motor resuelva esa búsqueda en tiempo constante. No se ha medido y no se afirma |
| **Expiración** | `expires_at`, **exclusivo**: en el instante exacto ya no vale |
| **Revocación** | `revoked_at`; basta con que tenga valor, no se compara con el reloj —así un desfase no resucita una sesión cerrada— |
| **Sesiones simultáneas** | Permitidas y aisladas: revocar una no afecta a la otra |

---

## G. Migración `0003`

| Comprobación | Resultado |
| --- | --- |
| **Revisión** | `0003`, `down_revision = '0002'` |
| **`alembic heads`** | `0003 (head)` |
| **Tablas creadas** | `administrator_sessions`, `login_rate_limits` |
| **`0001` y `0002`** | **Intactas.** Fijado por prueba: exactamente tres archivos de revisión y los dos anteriores presentes por nombre |
| **`upgrade` → `downgrade` → `upgrade`** | ✔ `tests/integration/test_migrations.py`, contra PostgreSQL real. Compara el esquema antes y después |
| **`compare_metadata`** | ✔ `test_el_esquema_aplicado_coincide_con_el_modelo`: sin *drift* entre `Base.metadata` y la base |
| **Motor** | `personal_blog_test`. **SQLite no se usó** |

**Sin datos.** Sigue sin haber `INSERT` en ninguna migración: crear un administrador
exige correo y hash reales, que no se versionan (S-10). Es de `Task/022` y `Task/036`.

**Sin índices sobre `administrator_id` ni `expires_at`**: ninguna consulta del alcance
vigente los recorre —la sesión se resuelve **siempre** por la huella, que ya tiene
índice único— y un índice sin consulta es coste de escritura a cambio de nada (M-06).

---

## H. Inicio de sesión

| Caso | Resultado |
| --- | --- |
| Credenciales correctas | `200`, identidad pública, `Set-Cookie` |
| Correo inexistente | `401` `invalid_credentials` |
| Contraseña incorrecta | `401` `invalid_credentials` |
| **Indistinguibilidad** | **Cuerpo, código y estado idénticos**, retirando solo `request_id`, que es correlación y no información sobre la cuenta |
| Correo con mayúsculas | Se acepta: se normaliza antes de consultar |
| `last_login_at` | Se actualiza |
| Contador de fallos | Vuelve a `0` y `locked_until` a `NULL` |
| Sesión creada | Una fila cuya huella corresponde a la cookie entregada |
| Cuerpo de la respuesta | Exactamente `{id, email, display_name}`. Ni token, ni hash, ni estado defensivo |
| **Base sin administrador** | `401`, **nunca `500`**, y **no se crea ningún administrador**. El mensaje no menciona la configuración del sistema |

---

## I. Bloqueo de cuenta

| Aspecto | Valor |
| --- | --- |
| Umbral / duración | **5 fallos / 15 min**, configurables |
| `failed_login_attempts` | Se usa de verdad: incrementa, se reinicia en éxito |
| `locked_until` | Se usa de verdad: se fija al alcanzar el umbral y se limpia en éxito |
| **Durante el bloqueo** | **Ni las credenciales correctas entran**, y la respuesta es **idéntica** a la de credenciales inválidas |
| **El bloqueo no se alarga** | Un fallo durante el bloqueo **no desplaza** `locked_until`. Si lo hiciera, cualquiera podría dejar al **único** administrador fuera de su panel indefinidamente: sería cambiar un problema por otro peor |
| **Al vencer** | El contador **empieza de nuevo**. Sin ese reinicio quedaría en el umbral y el primer fallo posterior volvería a bloquear al instante: un bloqueo anunciado como temporal sería permanente en la práctica |
| **Concurrencia** | `SELECT … FOR UPDATE` sobre la fila del administrador |

### El coste de D-011-L, dicho sin adornos

La cuenta bloqueada responde **igual** que unas credenciales inválidas. **El
propietario que se bloquee a sí mismo verá «credenciales inválidas»** durante quince
minutos, sin explicación en la respuesta.

Se acepta porque la alternativa es peor: si el bloqueo respondiera distinto, averiguar
el correo real sería trivial —se envían cinco intentos a un correo cualquiera y se
mira si la respuesta cambia; con uno inventado nunca cambiaría—. El motivo real queda
en la **auditoría** (`authentication.account_locked`), que es donde el operador puede
consultarlo.

### Prueba de concurrencia (B-07)

Dos peticiones simultáneas, **dos conexiones reales**, sincronizadas con una barrera.
Se exige el resultado correcto —contador final **2**—, no se observa quién gana. Con la
implementación ingenua el resultado sería 1: un umbral de cinco se convertiría, ante un
atacante que pida en paralelo, en uno de diez o más.

---

## J. Límite de tasa — evidencia

| Caso | Resultado |
| --- | --- |
| Por debajo del límite | Ninguno se rechaza por tasa |
| En el límite exacto | Todavía se atiende |
| Por encima | `429` con la envoltura de error del proyecto |
| `Retry-After` | Presente, entero positivo ≤ ventana |
| Ni con credenciales correctas | `429`, y **sin `Set-Cookie`** |
| **Partición** | El cubo de una IP no afecta a otra: el atacante **no** puede dejar al propietario sin acceso |
| **`X-Forwarded-For` falsificada** | **Se ignora** con `hops = 0`: once cabeceras distintas producen **un** solo cubo, el de la IP real |
| Control positivo | Con `hops = 1` la cabecera **sí** se atiende — sin él, una implementación que la ignorara siempre pasaría la prueba anterior sin política alguna |
| Ventana vencida | El contador se reinicia y vuelve a admitirse |
| Sin identidades | La tabla no guarda correo, administrador ni contraseña |

---

## K. Política de la cookie

| Atributo | Valor | Comprobado |
| --- | --- | --- |
| Nombre | `blog_admin_session` | **Constante, no configuración** (ver §T.4) |
| `HttpOnly` | **Siempre** | ✔ |
| `Secure` | `true` por defecto; `false` **solo** fuera de producción, donde con `BLOG_APP_ENV=production` el proceso **no arranca** | ✔ en ambos sentidos |
| `SameSite` | **`Lax`** | ✔, y se comprueba que no es `None` ni `Strict` |
| `Path` | `/api/v1/admin` — no viaja a los diez endpoints públicos | ✔ |
| `Domain` | **Ausente** → *host-only* | ✔ |
| `Max-Age` | `43200`, coherente con `expires_at` | ✔ |
| Secreto en el cuerpo | **No aparece** | ✔ |
| Borrado en `logout` | Repite `Path` y `HttpOnly` — el navegador solo sustituye una cookie si `Name`, `Domain` y `Path` coinciden | ✔ |
| `Cache-Control` | `no-store` en las **tres** respuestas | ✔ |

`Path` es **higiene de exposición, no una frontera de seguridad**: quien lo aplica es
el navegador.

---

## L. CSRF y `Origin`

Dos capas independientes. **No se afirma que `SameSite` lo resuelva todo.**

| Capa | Cubre | No cubre |
| --- | --- | --- |
| **`SameSite=Lax`** | El navegador **no envía** la cookie en peticiones *cross-site* que cambian estado: descarta el `POST` forjado desde un sitio de terceros | La navegación *cross-site* por `GET` — irrelevante: los endpoints que cambian estado no son `GET`, y la respuesta de `GET /me` no es legible *cross-origin* sin CORS |
| **Validación de `Origin`** | `POST`/`PUT`/`PATCH`/`DELETE` bajo `/admin`: si trae `Origin` y no está en la lista explícita → `403`. **No depende de que el navegador se comporte** | Un cliente que no es navegador y no envía `Origin`: pasa |

**Por qué pasar sin `Origin` no es un agujero.** Un CSRF **necesita** el navegador de
la víctima y su cookie ambiente, y todo navegador actual envía `Origin` en esos
métodos. Quien no es un navegador tendría que **poseer** la credencial para llegar a
algo, y entonces el CSRF ya no es el problema. Rechazarlas rompería cualquier
automatización legítima sin cerrar nada.

**Sin *token* CSRF sincronizado:** sería una tercera capa cuyo único caso adicional
—un navegador que envíe cookies *same-site* pero omita `Origin` en un `POST`— no
existe en ningún navegador vigente. `Task/018` puede endurecer si aparece un motivo.

**Comparación exacta**, no por prefijo: `https://example.com.evil.invalid` contiene el
origen permitido como subcadena y una comprobación con `in` o `startswith` lo
aceptaría. Probado, junto con `Origin: null`, subdominios y puertos distintos.

> **Consecuencia operativa.** Con `BLOG_ADMIN_ALLOWED_ORIGINS` vacío —el valor por
> defecto— **ningún navegador puede iniciar ni cerrar sesión**. Es *fail-closed*
> deliberado: no existe un origen por defecto seguro. Está documentado en
> `.env.example` y fijado por prueba.

**`Task/012` hereda la guarda automáticamente** si monta sus routers bajo el mismo
prefijo con la misma dependencia; la política vive en `app/shared/security/origen.py`,
no en el router.

---

## M. `GET /admin/auth/me`

| Caso | Resultado |
| --- | --- |
| Sesión válida | `200` con la identidad **derivada de la sesión** |
| **Cabeceras del cliente afirmando otra identidad** | **Se ignoran**: la identidad sale de la sesión |
| Sin cookie · desconocida · caducada · revocada | `401` `unauthenticated`, y **los cuatro cuerpos son idénticos** |
| Credencial basura (vacía, 5000 caracteres) | `401`, sin estallar |
| Dos sesiones vivas | Cada credencial resuelve la suya |
| Campos | Exactamente `{id, email, display_name}` |
| Control positivo | Una sesión vigente **creada a mano** sí autentica — sin él, una implementación que rechazara toda credencial no emitida por `login` pasaría la prueba de caducidad sin comprobar nada |

---

## N. Cierre de sesión

| Aspecto | Resultado |
| --- | --- |
| Respuesta | `204`, sin cuerpo |
| **Revocación en servidor** | `revoked_at` escrito **en la base** |
| **Reutilización de la misma credencial** | Se guarda **antes** de cerrar sesión y se vuelve a presentar **saltándose el borrado de la cookie**: `401`. **Es la comprobación que un JWT no podría pasar** |
| Limpieza en el cliente | `Set-Cookie` de borrado con los mismos atributos |
| Sin sesión | `401`, no `204` |
| Aislamiento | Cierra **una** sesión: la otra sigue viva y solo **una fila** queda revocada |
| Auditoría | `authentication.logout` |

**«Logout borra el token del navegador» no cuenta como invalidación**, y esta tarea no
lo acepta: una credencial copiada antes del borrado seguiría autenticando.

---

## O. Protección reutilizable para `Task/012`

| Aspecto | Valor |
| --- | --- |
| **Ubicación** | `app/modules/authentication/presentation/dependencias.py` |
| **API pública** | `from app.modules.authentication.presentation import AdministradorRequerido, requiere_administrador` |
| **Uso en `Task/012`** | `def endpoint(administrador: AdministradorRequerido) -> …` y nada más |
| **Qué hace** | Extrae la credencial, valida la sesión, resuelve el administrador y rechaza si algo falla |
| **Qué no hace** | Ninguna regla de CRUD; no depende de ningún router concreto |
| **Variante para `logout`** | `SesionEnCursoRequerida`, que añade la credencial. Un endpoint de contenido **no** necesita ver el secreto de sesión, así que no lo recibe |

**Por qué no vive en `app/shared/security` (D-011-O).** `software-architecture.md`
§3.4 asigna las *dependencias de autorización* a `shared/security`. Resolverlas exige
consultar **sesiones y administradores**, que son del módulo `authentication`, así que
colocarlas en `shared` obligaría a que `shared` importara un módulo de negocio — justo
lo que la regla de dependencias prohíbe. `shared/security` conserva las **primitivas
transversales** (hash de contraseñas, dirección del cliente, política de `Origin`); la
autorización vive con quien es dueño de los datos que consulta. Queda anotado en
`software-architecture.md`.

---

## P. Auditoría

**Cuatro acciones, y cada una tiene un productor real:**
`authentication.login_succeeded` · `authentication.login_failed` ·
`authentication.logout` · `authentication.account_locked`.

| Aspecto | Resultado |
| --- | --- |
| `actor_id` nulo | Cuando el correo no corresponde a ningún administrador. **Que sea nulo es, en sí mismo, la información de que el correo probado no existe** — sin guardar el correo |
| `request_id` | Presente y **coincidente con el del cuerpo de error** de esa misma petición. Dos peticiones producen identificadores distintos |
| `ip_address` | Presente, según la política de confianza. Con un par que no es una IP se registra `unknown` en lugar de texto arbitrario |
| **Secretos** | **Ninguno.** Se recorre la **fila entera** de cada evento buscando contraseña, hash, credencial y huella |
| **Correo intentado** | **No se guarda.** Convertiría la auditoría en un almacén de datos personales de terceros alimentado por cualquiera (O-09) |
| Bloqueo | Se audita la **transición**, no el estado: los intentos posteriores durante el mismo bloqueo no vuelven a emitirlo |
| Inmutabilidad | Las guardas de `Task/008` siguen rechazando `UPDATE`. `Task/011` solo **crea** |
| Límite de tasa | **No genera evento**, y es deliberado: es un hecho operativo del endpoint que cualquiera puede provocar desde fuera, y auditarlo permitiría llenar el historial de ruido justo antes de hacer algo que sí conviene esconder |

---

## Q. Contrato HTTP y OpenAPI

| Endpoint | Método | Éxito | Seguridad | Caché |
| --- | --- | --- | --- | --- |
| `/api/v1/admin/auth/login` | `POST` | `200` | **Ninguna** — único administrativo público | `no-store` |
| `/api/v1/admin/auth/logout` | `POST` | `204` | `sesionAdministrativa` | `no-store` |
| `/api/v1/admin/auth/me` | `GET` | `200` | `sesionAdministrativa` | `no-store` |

| Código | Cuándo |
| --- | --- |
| `401` `invalid_credentials` | Correo inexistente, contraseña incorrecta o cuenta bloqueada |
| `401` `unauthenticated` | Sesión ausente, desconocida, caducada o revocada |
| `403` `forbidden` | `Origin` no permitido en un método que cambia estado |
| `422` `validation_error` | Cuerpo inválido, con la **envoltura del proyecto** |
| `429` `too_many_requests` | Límite de tasa, con `Retry-After` |

| Comprobación OpenAPI | Resultado |
| --- | --- |
| Rutas administrativas declaradas | **Exactamente las tres** de autenticación |
| CRUD administrativo | **Cero** — es de `Task/012` |
| Esquema de seguridad | `apiKey` en `cookie`, con el **nombre real** de la cookie |
| Rutas públicas | Las **diez** más `/health`, **intactas y sin ningún requisito de seguridad** |
| `HTTPValidationError` de FastAPI | **No aparece**: el router declara la envoltura real del proyecto |

**Ningún middleware de autenticación global.** Proteger `/api/v1` entero habría
convertido en privados los diez endpoints públicos de `Task/009`. La protección se
aplica **endpoint a endpoint** mediante una dependencia, y hay una prueba que recorre
la especificación entera exigiendo que ninguna ruta pública declare seguridad.

---

## R. PostgreSQL real

| Aspecto | Valor |
| --- | --- |
| Base | `personal_blog_test` |
| Guarda *fail-closed* | Activa: sufijo `_test` **y** marca `personal-blog:test-database` dentro de la base |
| `personal_blog` | **NO se usó** |
| SQLite | **NO se usó** |
| Grafo de fixtures | Las **siete** fixtures nuevas derivan del resolutor verificado; `test_grafo_de_fixtures_de_integracion.py` sigue en verde |
| Docker | **No se recreó nada.** Ni `down`, ni `up --build`, ni `prune`. PostgreSQL y MinIO son los que ya estaban en marcha |

---

## S. TDD por *slice*

Doce *slices*. Cada uno registra el comando, el RED y su motivo. **Un test que pasó al
escribirse se clasifica como regresión, nunca como evidencia RED.**

| # | *Slice* | RED (motivo exacto) | GREEN | Refactor |
| --- | --- | --- | --- | --- |
| **0** | Decision Gate D-15 / D-02 / D-09 | *No aplica*: sin código productivo | — | — |
| **1** | Hash de contraseñas | `ModuleNotFoundError: app.shared.security` — el módulo no existía | 17 ✔ | Parámetros **derivados del propio hasher** para que la constante publicada y los reales no puedan separarse; señuelo desde CSPRNG |
| **2** | Dominio de sesión | `ModuleNotFoundError: …domain.sesion` | 15 ✔ | No necesario: el diseño resultante ya es el mínimo |
| **3a** | Esquema + migración `0003` | **11 fallos**: las tablas no existían y solo había dos revisiones | 24 ✔ (incluye ciclo de migraciones y `compare_metadata`) | — |
| **3b** | Repositorios | `ModuleNotFoundError: …infrastructure.repositorios` | 18 ✔ | Se adoptó la convención de `Task/010` —los métodos de escritura hacen `flush`—; dos pruebas pasaron a esperar el `IntegrityError` en el punto que lo provoca (§T.1) |
| **3c** | Configuración | **18 fallos**: los campos no existían | 26 ✔ | — |
| **4** | Login | **15 fallos**: `404`, el endpoint no existía | 17 ✔ | — |
| **5** | Bloqueo de cuenta | `ModuleNotFoundError: …domain.bloqueo` + **9 fallos** de integración: el contador nunca se incrementaba | 47 ✔ | — |
| **6a** | Dirección del cliente | `ImportError: DIRECCION_DESCONOCIDA` | 16 ✔ | — |
| **6b** | Límite de tasa | **10 fallos**: el limitador no existía | 13 ✔ | — |
| **7** | `/me` + `require_administrator` | **12 fallos**: `404` | 48 ✔ | El nombre de la cookie pasó de configuración a **constante** (§T.4); se añadió `cliente_administrativo` al harness (§T.3) |
| **8** | Logout | **11 fallos**: `404` | 11 ✔ | `SesionEnCurso` unifica identidad y credencial, para que `logout` no tenga que releer la cookie por su cuenta |
| **9** | Auditoría | `ModuleNotFoundError: …audit.domain` | 16 ✔ | Identificador de petición **memorizado en `request.state`** y reutilizado por los manejadores de error |
| **10** | `Origin` / CSRF | `ImportError: METODOS_QUE_CAMBIAN_ESTADO`, y **3 fallos** de contrato: no se rechazaba ningún origen | 32 ✔ | — |
| **11** | OpenAPI y regresión | **4 fallos** en pruebas de `Task/009` y `Task/005` | Suite completa ✔ | — |

### Tests que **pasaron al escribirse** — clasificados como regresión, no como RED

Se registran uno a uno porque la honestidad del ciclo depende de ello:

| Prueba | Por qué pasó al escribirse |
| --- | --- |
| `test_ningun_rechazo_entrega_cookie_de_sesion` · `test_el_correo_inexistente_y_la_contrasena_incorrecta_son_indistinguibles` (*slice* 4) | Con el endpoint inexistente, dos `404` también son indistinguibles y tampoco traen cookie. Pasaban **por el motivo equivocado**; solo miden algo desde que el endpoint existe |
| `test_el_rechazo_por_tasa_usa_la_envoltura_de_error_del_proyecto` (*slice* 6b) | El `401` previo ya usaba la misma envoltura |
| `test_el_rechazo_por_origen_usa_la_envoltura…` · `test_el_rechazo_por_origen_no_entrega_ninguna_cookie` (*slice* 10) | El `500` previo también respetaba la envoltura y tampoco traía cookie |
| Las **6** comprobaciones de OpenAPI del *slice* 10 | El esquema de seguridad ya lo había producido el *slice* 7 |
| Las **9** de `test_politica_de_la_cookie.py` | La política de cookie se implementó en los *slices* 4 y 8; este módulo la **fija**, no la introdujo |
| `test_un_acceso_correcto_por_la_ruta_real_persiste_su_sesion` | Control positivo del camino de éxito, escrito junto a las dos pruebas que sí tuvieron RED |
| `test_un_hash_ilegible_no_se_marca_para_rehash` | Cierra un hueco de cobertura detectado al final (§W); el comportamiento ya existía |

**No se usó mutation testing en ninguna forma**, ni como evidencia ni como sustituto.

---

## T. Defectos encontrados durante la integración

Ninguno se corrigió en silencio.

### T.1 · La sesión sin `flush` no era visible en su propia unidad de trabajo

**Síntoma:** cuatro pruebas del *slice* 3b fallaban al buscar una sesión recién creada.
**Causa:** el harness usa `autoflush=False`, así que el `INSERT` no se había emitido.
**Corrección:** se adoptó la convención ya vigente en el repositorio de medios de
`Task/010` —los métodos de escritura hacen `flush`, con el motivo documentado—. Dos
pruebas pasaron a esperar el `IntegrityError` **en la llamada que lo provoca** en lugar
de en un `flush` posterior: la garantía se refuerza, no se relaja.

### T.2 · Contaminación entre pruebas por `AuditEvent.actor_id ON DELETE RESTRICT`

**Síntoma:** la primera suite completa dio **48 fallos** que **no aparecían al ejecutar
los módulos por separado**.
**Causa:** las dos pruebas que confirman de verdad limpiaban borrando el administrador
**antes** que sus eventos de auditoría. La clave foránea `RESTRICT` —la que `Task/008`
puso para que el historial no se pierda con quien lo generó— rechazaba ese borrado, el
fallo ocurría dentro de un `finally`, y la fila quedaba. Como `administrators.is_singleton`
es `UNIQUE`, **una sola fila olvidada impedía que cualquier prueba posterior creara su
administrador**.
**Corrección:** helper `limpiar_autenticacion`, que borra en orden de dependencias
—`AuditEvent` → `AdministratorSession` → `LoginRateLimit` → `Administrator`— y se aplica
**antes y después**: después porque lo escrito sobrevive; antes porque una ejecución
interrumpida puede haber dejado la suya. El razonamiento está en el docstring del helper.

> Es un defecto **del andamiaje de pruebas**, no del código productivo, y se registra
> como tal. Lo que demuestra es que el `RESTRICT` de `Task/008` funciona.

### T.3 · La cookie `Secure` no sobrevivía al cliente de pruebas

**Síntoma:** las pruebas de `/me` con sesión válida recibían `401`.
**Causa:** `TestClient` habla **HTTP**, y un cliente que respeta la norma —httpx la
respeta— **no guarda ni reenvía una cookie `Secure` recibida por HTTP**. Cada petición
posterior llegaba sin cookie.
**Corrección:** fixture `cliente_administrativo`, que construye la aplicación con
`auth_cookie_secure=False` — **exactamente la configuración del entorno local**, que
sirve por HTTP. No se debilitó nada para que pasaran las pruebas: que `Secure` sea
obligatorio **en producción** lo comprueban la configuración —el proceso no arranca sin
él— y las pruebas de contrato de la cookie, en ambos sentidos.

### T.4 · Un nombre de cookie configurable habría hecho mentir a OpenAPI

**Hallazgo:** FastAPI construye el esquema de seguridad **al definir las rutas**. Con el
nombre en una variable de entorno, un despliegue que la cambiara publicaría una
especificación que **declara una cookie distinta de la que el servidor usa**.
**Corrección:** el nombre pasó a ser constante y `BLOG_AUTH_COOKIE_NAME` se retiró.
Nada pedía poder renombrarla (§36: no se añade configuración que la arquitectura no
necesita). La prueba que fijaba el valor por defecto se sustituyó por otra que fija la
constante **y** exige que no exista tal campo de configuración.

### T.5 · Una prueba de partición mezclaba los dos alcances de protección

**Síntoma:** `test_el_cubo_de_una_direccion_no_afecta_a_otra` fallaba.
**Causa:** el «atacante» gastaba sus once intentos contra el **correo real**, así que
activaba el **bloqueo de cuenta** —que no depende del origen— y el propietario tampoco
entraba. **La prueba no medía lo que decía medir.**
**Corrección:** el atacante usa un correo inexistente. Aísla la partición del límite de
tasa; el bloqueo tiene sus propias pruebas.

### T.6 · Dos aserciones afirmaban cosas que el almacenamiento no garantiza

1. **Orden de dos eventos de la misma petición.** `occurred_at` lo pone `now()` de
   PostgreSQL, que devuelve el instante de **inicio de la transacción**: el fallo y el
   bloqueo comparten marca. Afirmar cuál va antes habría fallado un día sin motivo. Se
   comprueban presencia y recuento.
2. **`ip_address == "testclient"`.** El cliente de pruebas se presenta con un nombre que
   **no es una dirección IP**, y la política *fail-closed* lo convierte en `unknown` —que
   es lo correcto—. Se sustituyó por dos pruebas: una con dirección real y otra que fija
   ese comportamiento *fail-closed*.

### T.7 · Expectativas de OpenAPI anteriores a `Task/011`

Cuatro pruebas de `Task/009` y `Task/005` exigían **cero** rutas administrativas, y sus
propios docstrings anotaban que llegarían en `Task/011` y `Task/012`. Es el primero de
los supuestos que `BACKEND_TESTING_STRATEGY.md` §9 admite para modificar un test: **el
requisito cambió**. Lo que protegen **no** cambió —que no se documente una superficie no
implementada—: la expectativa se **estrechó** al CRUD de `Task/012`, en lugar de
desaparecer. Además, `test_la_api_publica_es_de_solo_lectura` se restringió a las rutas
públicas en vez de relajarse.

### T.8 · El aviso de cookies por petición habría roto `-W error`

`TestClient.get(..., cookies=…)` está deprecado en httpx. Las cookies se fijan **en el
cliente**, con limpieza en un `finally`.

---

## U. Quality gates

| Gate | Comando | Resultado |
| --- | --- | --- |
| Lint | `ruff check .` | **All checks passed!** |
| Formato | `ruff format --check .` | **220 files already formatted** |
| Tipos | `mypy .` | **Success: no issues found in 218 source files** |
| Suite completa | `pytest --cov -q -W error -rs` | **1046 pasan · 1 omitida · 0 fallos · 0 errores · 0 advertencias** · 97,93 s |
| Cobertura | idem | **100 %** de `app/` — 2333 sentencias, **0** sin cubrir; 210 ramas, **0** parciales |
| Dependencias | `pip check` | **No broken requirements found** |
| Espacios | `git diff --check` | Sin problemas |
| Migraciones | `alembic heads` | `0003 (head)` |
| Ciclo de migración | integración | `upgrade` → `downgrade` → `upgrade` ✔ · `compare_metadata` ✔ |

Las suites por capa (`unit`, `contract`, `-m integration`) se ejecutaron *slice* a
*slice* durante el desarrollo y quedan cubiertas por la ejecución completa final, que
las incluye todas con `-W error`.

### Lo que **no** se ejecutó, y por qué

**No se construyó la imagen Docker.** El alcance de la sesión excluye tocar Docker, y
ningún `Dockerfile` cambió. Lo que sí cambió es `requirements.txt`, que ahora incluye
una dependencia **binaria**, así que se verificó lo que de verdad importaba sin tocar el
entorno: **existe rueda `manylinux_2_17_x86_64` para el destino Linux/Lambda** —
`argon2_cffi_bindings-…-cp36-abi3-manylinux_2_17_x86_64.whl` (86 KB) más
`argon2_cffi-25.1.0-py3-none-any.whl`—, descargadas explícitamente con
`--platform manylinux_2_17_x86_64 --python-version 3.12`. Es `abi3`, así que no depende
de la versión concreta de CPython. **Reconstruir la imagen queda como comprobación para
el usuario**, y los pasos están en la ficha.

---

## V. Pruebas omitidas — identificadas, no supuestas

**1 omitida.** Se identificó sin volver a ejecutar la suite completa: primero por
inspección (`grep` de `pytest.skip` / `skipif` en `tests/`) y después confirmando con una
ejecución de **un solo archivo** de 0,03 s.

| Archivo | Prueba | Condición | Motivo | ¿Nueva de `Task/011`? |
| --- | --- | --- | --- | --- |
| `tests/test_logging_utc.py:133` | `test_la_variable_tz_no_altera_el_timestamp` | `@pytest.mark.skipif(_tzset is None)` | `time.tzset` **solo existe en Unix**. La prueba manipula `TZ` para comprobar que no desplaza el *timestamp*, y sin `tzset` el cambio no surte efecto | **No.** Preexistente de `Task/005`, ya registrada en `STATUS.md` como la única omisión conocida |

**Ninguna omisión oculta un defecto**, y **`Task/011` no añade ninguna**.

### Un hallazgo sobre el ejecutor, no sobre el proyecto

Una ejecución intermedia dio **2 omisiones**. La segunda era
`test_el_timestamp_no_coincide_con_la_hora_local_del_host`, que se auto-omite cuando el
anfitrión ya opera en UTC. **La causaba el script auxiliar con el que se lanzaba la
suite**: cargaba el `.env` completo de infra, que define `TZ=UTC` para los contenedores,
y en Windows el *runtime* de C honra esa variable, de modo que `time.localtime()`
devolvía UTC.

Se corrigió el script para que exporte **solo** las variables `PERSONAL_BLOG_TEST_*`. La
prueba vuelve a ejecutarse y la suite recupera la única omisión documentada. **No se
tocó ningún archivo del proyecto**: el defecto estaba en el ejecutor. Se registra porque
explica la diferencia entre dos ejecuciones y porque el propio proyecto insiste en que
el resultado no debe depender de dónde se ejecute.

---

## W. Cobertura

**100 % de `app/`** — 2333 sentencias, **0** sin cubrir; 210 ramas, **0** parciales.

Se alcanzó **cerrando dos huecos reales**, sin tocar ninguna exclusión ni ningún
*assert*:

1. **`necesita_rehash` con un hash ilegible** (2 sentencias). Era un hueco de la matriz:
   el caso hermano estaba cubierto para `contrasena_valida` (H-07) y no para esta. Se
   añadió la prueba; el comportamiento —devolver `False` en vez de estallar— ya existía,
   así que **se clasifica como regresión, no como RED**.
2. **Tres ramas parciales en `puertos.py`.** Eran tres *stubs* de `Protocol` escritos en
   una sola línea (`def f(...) -> None: ...`), forma que la exclusión ya vigente del
   proyecto —`...` en línea propia— no alcanza. Se les dio el **docstring que les
   faltaba**, que es la convención del resto del archivo y que además documenta el
   contrato del puerto. No se tocó la configuración de cobertura.

**La cobertura es señal, no especificación:** ningún test se modificó para conservar el
porcentaje.

---

## X. Búsqueda de secretos

| Comprobación | Resultado |
| --- | --- |
| Patrones sensibles (`PRIVATE KEY`, `aws_secret_access_key`, `jwt_secret`, `signing_key`, `api_key=…`) sobre **todos** los archivos nuevos y modificados | **Ninguna coincidencia real.** Las cuatro coincidencias textuales son **documentación que explica que ese secreto no existe** |
| Literales `password/secret/token/credencial = "…"` | **Ninguno** fuera de valores explícitamente ficticios |
| Credenciales de prueba | `administrador@example.invalid` (TLD reservado por RFC 2606) y `contrasena-de-prueba-suficientemente-larga`. Viven **solo** en `tests/`, no abren nada y la base de pruebas se recrea |
| `.env.example` | Sin ningún valor real. La sección nueva **no contiene ni un solo secreto**, y lo dice explícitamente |
| `.env` real | Ignorado por `.gitignore` y **ausente** del conjunto de cambios |
| `DATABASE_URL` con contraseña en archivos nuevos | Ninguna |
| Auditoría | Prueba que recorre la **fila entera** de cada evento buscando contraseña, hash, credencial y huella |
| Logs | El módulo de hash no registra nada; prueba con `caplog` a nivel `DEBUG` que ninguna rama emite la contraseña |

**La arquitectura elegida no introduce ningún secreto nuevo**, y esa es una consecuencia
concreta de D-011-B: no hay nada que firmar.

---

## Y. Documentación

| Documento | Cambio |
| --- | --- |
| `docs/tasks/TASK-011-administrative-authentication.md` | **Creado.** Incluye el *Decision Brief* completo y la matriz de comportamiento |
| `docs/task-reports/TASK-011-report.md` | **Creado.** Este documento |
| `docs/project-management/STATUS.md` | Tarea en curso, estado, avance y riesgos |
| `docs/project-management/ROADMAP.md` | Estado de `Task/011` |
| `docs/stages/STAGE-03-domain-and-backend.md` | Estado de la tarea y criterios de salida |
| `docs/architecture/open-decisions.md` | **D-02, D-09 y D-15 → Resueltas** |
| `docs/architecture/software-architecture.md` | Mecanismo de autenticación; precisión sobre `shared/security` |
| `docs/architecture/security-boundaries.md` | CSRF, *rate limiting* y política de IP |
| `docs/architecture/api-contracts.md` | Contrato de los tres endpoints y códigos |
| `docs/architecture/data-model.md` | Las dos tablas nuevas y la migración `0003` |
| `personal-blog-backend/.env.example` | Sección de autenticación, con placeholders |

**ADR:** **no se crea.** La decisión no es estructural en el sentido de los ocho ADR
vigentes —que deciden estilo, repositorios, destino cloud, formato de contenido,
laboratorio local, base de datos de producción y observabilidad—: es la elección de un
mecanismo **dentro** de la arquitectura ya aceptada por ADR-004. Queda registrada en
`open-decisions.md` y en los documentos de arquitectura. Cambiar la topología de D-15
más adelante **sí** sería estructural y exigiría un ADR.

---

## Z. Criterio 12 — estado transitorio

Barrido dirigido sobre los documentos tocados, buscando *«PR abierto»*, *«pendiente de
fusionar»*, *«hasta que el usuario fusione»*, *«hasta completar normalización»*, *«rama
remota pendiente»*, *«Task012 no inicia hasta»* y *«y normalizada»*.

| Clase | Recuento |
| --- | --- |
| **A** — historia o evidencia fechada | Las tablas de este reporte y las notas de la ficha |
| **B** — regla permanente | *«toda Task nace de `main` actualizado»* |
| **C** — estado vivo o transitorio | **0** |

`Task/012` queda **Pendiente, no iniciada**, sin condicionarla a ningún PR, rama remota,
fusión ni normalización.

---

## AA. Gobierno

| Campo | Valor |
| --- | --- |
| **`Task/011`** | **Aprobada** ✔ el 2026-09-01 por jeffersondavila |
| **Avance global** | **11 / 41 — 27 %** *(la aprobación del usuario lo movió desde 10 / 41 — 24 %)* |
| **ETAPA 03** | **4 / 5 — 80 %** *(desde 3 / 5 — 60 %)* |
| **`Task/012`** | **Pendiente, no iniciada.** Aprobar `Task/011` **no** autoriza iniciarla |
| **D-02 / D-09 / D-15** | **Resueltas** y **Vigentes** desde el 2026-09-01 |
| **D-011-A a D-011-R** | **Vigentes** desde el 2026-09-01 |
| **D-07 / D-08** | **Abiertas**, con sus propietarios intactos |

---

## AB. Estado de Git al cerrar

| | backend | infra | frontend |
| --- | --- | --- | --- |
| Rama | `Task/011-Autenticacion-Administrativa` | `Task/011-Autenticacion-Administrativa` | `main` |
| Staging | **0** | **0** | **0** |
| Commits sobre `main` | **0** | **0** | **0** |
| Push | **0** | **0** | **0** |
| Merge | **0** | **0** | **0** |
| Pull request | **0** | **0** | **0** |

---

## AC. Deuda registrada

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | **Las tablas de estado de autenticación no se purgan** (**R-44**). `login_rate_limits` crece por **dirección IP observada** y es la fuente de crecimiento potencialmente mayor; `administrator_sessions` crece por **inicio de sesión con éxito**, y las filas caducadas o revocadas permanecen. No hay procesos residentes que las limpien; el volumen es despreciable con un único administrador, pero el crecimiento es monótono | `Task/018` (endurecimiento) o `Task/029` (operación) |
| 2 | **La imagen Docker no se reconstruyó** tras añadir una dependencia binaria. La rueda `manylinux` existe y está verificada; falta la construcción real | Comprobación del usuario · `Task/024`/`Task/032` al empaquetar |
| 3 | **El inicio de sesión desde navegador en local exige DOS variables, todavía no cableadas en el Compose local.** (A) **`BLOG_ADMIN_ALLOWED_ORIGINS`** con el origen real del panel: es *fail-closed*, y sin él la validación de `Origin` rechaza los `POST` del navegador. (B) **`BLOG_AUTH_COOKIE_SECURE=false`**, porque el entorno local actual sirve por **HTTP** y una cookie `Secure` no se conserva ni se reenvía sobre HTTP. **Hacen falta las dos**: con una sola, el inicio de sesión desde navegador sigue sin funcionar. No se añaden aquí porque el consumidor real del contrato todavía no existe | `Task/015` |
| 4 | **La resistencia al análisis temporal no está medida.** Se garantiza que **no queda ningún camino que evite el trabajo criptográfico**; no se afirma nada más | `Task/018` si algún día se mide |
| 5 | **El número de saltos de proxy de confianza no está fijado** para Traefik ni para API Gateway. El mecanismo existe con el valor seguro por defecto | Runbook local · `Task/033` |

---

## AD. Veredicto

| Pregunta | Respuesta |
| --- | --- |
| ¿D-15 resuelta? | **SÍ** |
| ¿D-02 resuelta? | **SÍ** |
| ¿D-09 resuelta? | **SÍ** |
| ¿Argon2id correcto? | **SÍ** |
| ¿Sesión opaca *server-side*? | **SÍ** |
| ¿El token no se persiste en claro? | **SÍ** |
| ¿`logout` invalida realmente en el servidor? | **SÍ** |
| ¿`/me` valida sesión real? | **SÍ** |
| ¿*Lockout* persistente y seguro ante concurrencia? | **SÍ** |
| ¿Límite de tasa compartido entre instancias? | **SÍ** |
| ¿Auditoría sin secretos? | **SÍ** |
| ¿CSRF/`Origin` coherente con D-15? | **SÍ** |
| ¿OpenAPI correcto? | **SÍ** |
| ¿PostgreSQL real? | **SÍ** |
| ¿`0003` reversible? | **SÍ** |
| ¿`0001` y `0002` intactas? | **SÍ** |
| ¿TDD real documentado? | **SÍ** |
| ¿Suite completa verde? | **SÍ** — 1046 pasan, 1 omitida |
| ¿0 fallos? | **SÍ** |
| ¿0 errores? | **SÍ** |
| ¿Cobertura final correcta? | **SÍ** — 100 % |
| ¿`pip check` limpio? | **SÍ** |
| ¿Criterio 12 con C = 0? | **SÍ** |
| ¿Frontend intacto? | **SÍ** |
| ¿0 commits, push, merge o PR? | **SÍ** |
| ¿`Task/011` lista para validación? | **SÍ** — y **Aprobada** por el usuario el 2026-09-01 |
