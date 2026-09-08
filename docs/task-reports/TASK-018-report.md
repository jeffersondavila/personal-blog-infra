# TASK-018 — Reporte de endurecimiento de seguridad

**Estado: Aprobada el 2026-09-08** mediante
`approved: Task/018-Endurecimiento-de-Seguridad`. Inicio: 2026-09-07. Cierre de
implementación: 2026-09-07.
[Ficha y matriz test-first](../tasks/TASK-018-security-hardening.md).

> **Nota sobre la ejecución.** La implementación la inició un agente que agotó su cuota
> antes de cerrar la tarea, y la continuó otro **sobre el mismo árbol de trabajo**, sin
> descartar nada. La segunda sesión auditó cada cambio heredado, corrigió los defectos que
> encontró —tres de ellos **rompían tareas ya aprobadas**— y completó las validaciones.
> Los hallazgos están en §D.1, señalados como tales.

---

## A. Preflight y saneamiento documental

Las bases históricas de nacimiento están en la ficha §0. El 2026-09-07 se corrigieron
cinco líneas desactualizadas de ROADMAP: encabezado, avance global, fila ETAPA 05,
total y estado de la sección ETAPA 05. Se conservaron las aprobaciones de Task016 y
Task017, otras etapas y los 41 identificadores. Criterio 12 del ajuste: **C = 0**;
solo hechos de aprobación, conteos y fecha de saneamiento, sin estado Git vivo.

## B. Alcance reconstruido

S-01/03/04/05/07/08/10/11, E-06 y R-09/10/12/15/22/36/43/44/46.
S-09 completo sigue en Task019–021. Se conservan D-02/D-09/D-15, ADR-005 y D-08.

## C. Baseline previo al código

Medido el 2026-09-07 (hora local), **antes** de escribir una sola línea.

| Comprobación | Resultado |
| --- | --- |
| Python Windows | 3.12.10 |
| `pip check` | Sin dependencias rotas |
| Ruff lint / formato | Verde; 308 archivos ya formateados |
| MyPy | Verde; 306 archivos |
| Pytest completo con PG/MinIO | **1808 pasadas, 1 omitida**, 409,26 s, `-W error`; omisión: `time.tzset` no existe en Windows |
| Build Docker backend | Exit 0 |
| Node / npm | 24.14.1 / 11.11.0 |
| `npm ci` | Exit 0; 332 paquetes instalados, 333 auditados, cero vulnerabilidades |
| Frontend formato/lint/typecheck | Exit 0 |
| Frontend tests | **687 pasadas, 1 fallida**: `formularios.test.tsx:260`, tiempo agotado a 5000 ms; 95,10 s |
| Frontend build / `npm audit` | Exit 0 / cero vulnerabilidades |
| Docker / Compose | 29.1.3 / 5.0.1 |
| Servicios | Cinco con sonda sana; Portainer en ejecución, sin sonda por diseño |
| HTTP sitio, admin, API, sitemap y assets | **Sin CSP, sin nosniff, sin referrer, sin permissions ni `X-Robots-Tag`** |
| Preflight `POST` de login | **405**, sin cabeceras CORS |
| PostgreSQL runtime | **`rolsuper`, `rolcreatedb` y `rolcreaterole` activos**; `UPDATE`/`DELETE` de `audit_events` **permitidos** |

**Rojo preexistente, registrado antes de implementar.** La prueba del preview agota su
tiempo con el paralelismo por defecto. **R-016-1** ya identifica esa sensibilidad a la
carga. No se cambió el entorno para convertir el baseline en verde, y **no se tocó ningún
tiempo de espera** en toda la tarea.

---

## D. Auditoría de la implementación heredada

### D.1 Defectos encontrados y corregidos

Seis hallazgos. **Tres rompían tareas ya aprobadas** y habrían llegado a la revisión sin
que ninguna suite los detectara, porque ninguna suite ejercita esos procedimientos.

#### 1. Las migraciones dejaron de poder ejecutarse — rompía `Task/008`

Al mover el backend a `blog_runtime`, un rol sin DDL, el procedimiento documentado en el
runbook §6.8 empezó a fallar:

```
docker compose exec backend alembic current
sqlalchemy.exc.ProgrammingError: (psycopg.errors.InsufficientPrivilege)
permission denied for table alembic_version
```

Ni siquiera **leer** el estado de las migraciones era posible. El endurecimiento era
correcto; lo que faltaba era el otro lado: **un sitio donde vivan las operaciones
administrativas**.

**Corrección.** Servicio `migrations` en el Compose, tras `profiles: [admin]`, que reutiliza
la imagen del backend con la identidad administrativa. Queda fuera de `up`, `ps`, `--wait`
y `down`, y solo existe cuando se le invoca:

```
docker compose --profile admin run --rm migrations                 # alembic upgrade head -> exit 0
docker compose --profile admin run --rm migrations alembic current # 0003 (head)
docker compose exec backend alembic current                        # sigue denegado, y debe seguirlo
```

El control negativo forma parte del resultado: que la aplicación **no** pueda migrar es lo
que se buscaba.

#### 2. El respaldo de PostgreSQL y MinIO dejó de funcionar — rompía `Task/004`

```
BACKUP FALLIDO: Error response from daemon:
Could not find the file /tmp/postgres-20260908-033706.dump in container personal-blog-local-postgres
```

Causa medida, no supuesta: `pg_dump` escribía el archivo correctamente —44 933 bytes,
comprobado dentro del contenedor— y era **`docker cp` quien no podía leerlo**, porque
`docker cp` **no atraviesa un montaje `tmpfs`**, y el endurecimiento había puesto `/tmp` en
RAM. Se verificó el contraste con un contenedor desechable: desde un **volumen** `docker cp`
sí funciona.

Afectaba a seis puntos del script, en **los dos** servicios: el volcado de PostgreSQL, su
verificación con `pg_restore --list` y el árbol de objetos que prepara `mc mirror`.

El agente anterior no lo detectó porque su último respaldo (`20260908-024710`) se tomó
**antes** de recrear el entorno endurecido.

**Corrección.** Volumen de paso `/backup` en PostgreSQL y MinIO, y las seis rutas
apuntando ahí. En PostgreSQL el directorio se crea **en la imagen** con propietario
`postgres`: un volumen nombrado nuevo hereda propietario del directorio de la imagen, y
creado sobre la marcha por Docker habría nacido como `root`, ilegible para un proceso que
ya no lo es. Los dos volúmenes quedan **vacíos** entre ejecuciones.

#### 3. La prueba de restauración fallaba al limpiar

```
PRUEBA DE RESTAURACION FALLIDA: rm: can't remove '/tmp/restore.dump': Operation not permitted
```

`docker cp` deposita el archivo como `root`, `/tmp` lleva el bit pegajoso y la imagen de
PostgreSQL arranca ahora como `postgres`. Afectaba a la **limpieza**, no a `pg_restore`,
que leía el archivo sin problema. Corregido ejecutando esa única orden con `-u 0`, con el
motivo escrito al lado.

#### 4. Dos pruebas de seguridad eran tautológicas

Las descubrió el barrido de mutación (§J), no la lectura:

- `test_excepcion_http_no_refleja_detalles_internos` recorría 400, 401, 403, 405, 422 y
  503 — **todos** presentes en la tabla de mensajes genéricos. Al reintroducir el respaldo
  `or str(exc.detail)`, que **es** la fuga, la prueba **seguía pasando**. Se añadió **451**,
  que no está en la tabla y es el único caso que distingue una cosa de la otra.
- El caso `it.each` de `security.config.test.ts` no incluía ningún esquema distinto de
  `http`/`https`, así que anular el filtro de esquema no rompía nada. Se añadió
  `ftp://site.test`, que el resto de la validación aceptaría.

Ambas se **volvieron a mutar** después de reforzarlas, y ambas mutaciones quedaron
detectadas.

#### 5. Finales de línea CRLF

`docker/nginx.conf` tenía una línea con CRLF, contra la política `eol=lf` de
`.gitattributes`. Prettier no cubre los `.conf`, así que pasó desapercibida.

#### 6. La recuperabilidad de las identidades runtime no estaba resuelta

Ver §I.

### D.2 Cambios heredados que se auditaron y se conservan

Se leyó el diff completo de los tres repositorios. Lo que sigue se **conserva** porque se
comprobó su comportamiento, no porque estuviera escrito.

| Cambio | Por qué se conserva |
| --- | --- |
| `AplicacionSegura` envolviendo `build_middleware_stack` | Es lo que garantiza cabeceras y CORS **también en un `500` no controlado**, que Starlette atiende por encima del *stack* de la aplicación. Comprobado con una ruta que lanza a propósito |
| Rechazo de `Origin` duplicado en las escrituras administrativas | Cerrar una vía real de evasión de la comprobación CSRF. Mutación M8: el guarda falla al quitarlo |
| `verify()` de Pillow además de `load()` | `load()` no comprueba todos los CRC de PNG. La prueba trae su **control positivo**: demuestra primero que el decodificador carga los píxeles del archivo corrupto |
| `read(TAMANO_MAXIMO_BYTES + 1)` en el router | Acota la memoria. **No es un control observable**: la cota ASGI ya limita el cuerpo y el dominio rechaza por longitud en cualquier caso. Se declara como lo que es —defensa en profundidad— en vez de inventarle una prueba |
| Mensaje genérico en toda excepción HTTP del framework | Ningún módulo lanza `HTTPException` con texto propio; los errores con mensaje de negocio van por `ApplicationError`, que **sí** conserva mensaje y cabeceras, incluido `Retry-After` del 429 |
| `traefik.yml` descartando campos del log de acceso | La correlación y la ruta segura las registra el backend (O-01/O-02). El borde conserva método, estado y duración |

---

## E. Dependencias

| Auditoría | Fecha | Resultado |
| --- | --- | --- |
| `npm audit` (todo el árbol) | 2026-09-07 | **0 vulnerabilidades** |
| `npm audit --omit=dev` | 2026-09-07 | **0 vulnerabilidades** |
| `pip-audit` sobre `requirements.txt` | 2026-09-07 | **0 vulnerabilidades** en 40 paquetes |
| `pip check` | 2026-09-07 | Sin dependencias rotas |

**Cero dependencias nuevas** en los tres repositorios. Las herramientas de auditoría se
descargaron a un directorio temporal ignorado; no son dependencias del proyecto ni CI.

---

## F. Imágenes Docker

Todas las imágenes quedan fijadas **por etiqueta de parche y por digest**. El escaneo es
del 2026-09-07, con Trivy 0.74.0, sobre las imágenes **finales realmente en ejecución**.

| Imagen | Antes | Después | Digest | CRITICAL | HIGH | Con parche disponible |
| --- | --- | --- | --- | --- | --- | --- |
| Backend | `python:3.12.13-slim` | `python:3.12.14-slim` | `sha256:78387bc3…` | 3 | 51 | **0** |
| Frontend | `node:22.21.1` + `nginx:1.29.3-alpine` | `node:22.23.2` + `nginx:1.30.4-alpine` | `sha256:c610fcdf…` / `sha256:dc5069ad…` | **0** | **0** | — |
| PostgreSQL | `postgres:17.10-alpine` | `postgres:17.11-alpine` + Dockerfile propio | `sha256:18cfe3ef…` | **0** | **0** | — |
| Traefik | `traefik:v3.6.2` | `traefik:v3.7.13` + Dockerfile propio | `sha256:f86a2cab…` | **0** | **0** (1 `UNKNOWN`) | — |
| Portainer | `portainer-ce:2.39.5` | `portainer-ce:2.39.7` | `sha256:0e3c8bc8…` | 1 | 16 | 1 / 14 |
| MinIO | `RELEASE.2025-09-07T16-13-09Z` | **sin cambio**, ahora con digest | `sha256:14cea493…` | **8** | **96** | 6 / 92 |
| Auxiliar de respaldo | `alpine:3.22` | `alpine:3.22.5` | `sha256:14358309…` | **0** | 2 | 2 |

**No se declara «cero vulnerabilidades».** Quedan hallazgos, y este es su reparto real:

- **Backend — 3 CRITICAL y 51 HIGH, ninguno con corrección publicada.** Son paquetes del
  sistema base de Debian 13 (`perl-base`, `util-linux`, `libsqlite3`, `login`…). Trivy
  informa `FixedVersion` vacío en **los 54**: no hay nada que aplicar hoy. Además, la
  imagen final ya no lleva `pip`.
- **Portainer — 1 CRITICAL y 16 HIGH**, frente a **1 y 21** en 2.39.5. Mejora, pero no
  desaparecen: son dependencias Go empaquetadas en el binario, y solo se corrigen con una
  versión que las recompile. **No se sube a 2.45**: sería un salto que migra su base de
  datos, y perseguir un recuento no justifica arriesgar el volumen. La versión elegida se
  probó primero **sobre una copia aislada** del respaldo antes de tocar el entorno real, y
  después se verificó en el real: **HTTP 200**, `ServerVersion 2.39.7`,
  `DatabaseVersion 2.39.7`, mismo volumen `personal-blog-local_portainer_data`.
- **MinIO — 8 CRITICAL y 96 HIGH, y es la única imagen que NO se actualizó.** Es el mayor
  residuo del conjunto y se registra como **R-018-3**. La versión fijada es de hace
  aproximadamente un año, y 98 de esos 104 hallazgos declaran corrección aguas arriba
  (Go `stdlib`, `x/crypto`, `x/net`, `grpc`). Motivo de no subirla dentro de esta tarea:
  es el **servicio de datos** del entorno, subirla cruza un año de *releases* con cambios
  conocidos en IAM y consola, y su exposición real es **solo local, en loopback, y fuera de
  la arquitectura de producción** —donde el destino es Amazon S3 a través de
  `ObjectStorage`—. Es una decisión de riesgo declarada, no un descuido.
- **Auxiliar de respaldo — 2 HIGH** (`libcrypto3`/`libssl3` 3.5.7-r0 → 3.5.8-r0). El
  paquete corregido existe en el repositorio de Alpine —de hecho es el que se aplica en las
  imágenes de PostgreSQL y Traefik— pero todavía no está en ninguna imagen `alpine:3.22.x`
  publicada: se comprobó que 3.22.6 y 3.22.7 **no existen**. En este contenedor no es
  alcanzable: solo empaqueta y calcula *checksums*, sin red ni TLS.

### Endurecimiento de los contenedores

Los seis servicios corren con `read_only: true`, `cap_drop: [ALL]` y
`no-new-privileges:true`, verificado por `docker inspect`. Usuario efectivo:

| Servicio | UID |
| --- | --- |
| Traefik | 65532 |
| Backend | 1001 |
| Frontend (nginx, **incluido el proceso maestro**) | 101 |
| PostgreSQL | 70 |
| **MinIO** | **0** |

**MinIO sigue siendo `root` dentro de su contenedor**, y se dice. Su imagen oficial no
admite un usuario no privilegiado sin reasignar la propiedad del volumen de datos, que es
una operación destructiva sobre datos existentes. Queda acotado por las otras tres
restricciones.

---

## G. Secretos

| Comprobación | Resultado |
| --- | --- |
| Escáner de secretos sobre los archivos **versionables** de los tres repositorios (709 archivos: seguidos por Git más nuevos no ignorados) | **0 hallazgos** |
| `git ls-files` en los tres repositorios | Solo `.env.example`; ni `.env`, ni `secrets/`, ni `local-backups/`, ni `tmp/` |
| `git check-ignore` | `secrets/`, `local-backups/`, `.env` y `tmp/` confirmados como ignorados |
| Valores de ejemplo | Ficticios y marcados como tales |

En ninguna parte de esta tarea se imprimió una contraseña, un JWT ni una clave. El script
de privilegios **no imprime la salida de un proveedor** y convierte cualquier excepción no
prevista en un mensaje genérico, porque una excepción de driver puede transportar la DSN.

**Rotación de credenciales locales.** Las credenciales administrativas de PostgreSQL y
MinIO coincidían con las de ejemplo del `.env.example`. Se sustituyeron por valores
aleatorios en el `.env` **ignorado**, y —esto es lo que importa— se comprobó que la
rotación quedó **coherente con el rol real**: PostgreSQL no cambia la contraseña de un rol
existente porque cambie una variable del Compose sobre un volumen ya inicializado. El
procedimiento ejecuta `ALTER ROLE` dentro de una transacción y solo entonces reemplaza el
`.env`; si el reemplazo falla, deshace el cambio. Verificado a posteriori: el entorno
levanta y autentica con las credenciales nuevas.

**Portainer no se rotó**, conforme a lo acordado. Su credencial ya estaba regularizada.

---

## H. Mínimo privilegio (S-01)

Dos planos de identidad, comprobados **en ejecución** contra los servicios reales, con
control positivo **y** negativo en cada caso.

| Plano | PostgreSQL | MinIO |
| --- | --- | --- |
| Administración | `POSTGRES_USER` (superusuario) | `MINIO_ROOT_USER` |
| Runtime de la aplicación | `blog_runtime` | `blog-runtime` |

Verificado en el entorno levantado:

```
db_user= blog_runtime   host= postgres   db= /personal_blog
blog_runtime | rolsuper=f rolcreatedb=f rolcreaterole=f rolreplication=f rolbypassrls=f
DB: SELECT permitido; UPDATE/DELETE de auditoria y DDL denegados realmente.
MinIO: sonda/PUT/GET/DELETE propios permitidos; listar global/bucket y administrar denegados.
```

### PostgreSQL

Los permisos se contrastaron contra el esquema real —17 tablas— y no contra una lista
escrita de memoria:

- `SELECT`, `INSERT`, `UPDATE`, `DELETE` en las 14 tablas de contenido.
- **`audit_events`: solo `SELECT` e `INSERT`.** La inmutabilidad del historial pasa a
  depender de PostgreSQL, no de que nadie escriba un `UPDATE`. Comprobado con tres
  sentencias prohibidas ejecutadas dentro de transacciones con reversión forzada.
- **`administrators`: solo `SELECT` y `UPDATE`.** La aplicación valida un acceso y anota
  su resultado; **no puede crear ni borrar administradores**.
- **`alembic_version`: sin conceder.** Ni DDL, ni `CREATE`/`TEMPORARY` sobre la base, ni
  `CREATE` sobre el esquema `public` —también retirado de `PUBLIC`—.
- **No hay secuencias** en el esquema: las claves son UUID, así que no falta ningún
  `GRANT USAGE` que rompiera un `INSERT`.

**Las migraciones no dependen del rol limitado.** Se ejecutan por el plano administrativo
(§D.1.1) y se comprobaron los dos lados: `alembic upgrade head` → exit 0;
`docker compose exec backend alembic current` → denegado.

**Las pruebas de integración tampoco.** Usan variables `PERSONAL_BLOG_TEST_*`
independientes del `.env` de la aplicación, con la identidad administrativa: necesitan
crear y borrar *buckets* y ejecutar `alembic downgrade base`.

### MinIO

Política acotada al *bucket* de medios: `GetObject`, `PutObject` y `DeleteObject` sobre su
contenido, y `ListBucket` **restringido al prefijo de la sonda de disponibilidad**.
Comprobado con controles positivos —`PUT`, `GET` y `DELETE` de un objeto propio, recién
creado y con nombre aleatorio— y negativos: `list_buckets` y el listado completo del
*bucket* devuelven **403**, y `mc admin info` devuelve **Access Denied**.

---

## I. Recuperabilidad de las identidades runtime

Este punto quedó sin cerrar en la sesión anterior, y es el que más consecuencias tiene ante
un desastre.

**El problema es real y se midió**, no se dedujo: el volcado de PostgreSQL **sí** lleva las
entradas `ACL` de las 17 tablas —se comprobó en el índice del volcado— pero `pg_dump` de una
base **nunca emite `CREATE ROLE`**. Al restaurar, esos `GRANT` mencionan un rol que puede no
existir. La copia de MinIO, por su parte, contiene objetos y configuración de *buckets*, no
su IAM.

El archivo `secrets/backend-runtime.env` está ignorado por Git y **fuera del respaldo, a
propósito**: un respaldo que llevara dentro sus propias credenciales no protegería nada.

Con lo heredado había un camino sin salida: si se perdía ese archivo pero el rol seguía
existiendo, el script se detenía —correctamente, porque **no rota nada por su cuenta**— y no
ofrecía ninguna alternativa.

**Corrección: `--reissue-runtime-credentials`.** Flag explícito, nunca implícito. Genera
credenciales nuevas sin conocer las anteriores, las aplica en PostgreSQL y en MinIO,
reescribe el archivo de forma atómica y deja que `--apply` reaplique permisos y política.
**No destruye contenido.**

**Probado de extremo a extremo, no solo escrito**, con inventario antes y después:

| Medida | Antes | Después |
| --- | --- | --- |
| Filas: posts / medios / administradores / auditoría | 0 / 0 / 0 / 4 | 0 / 0 / 0 / 4 |
| Buckets y objetos del *bucket* de medios | 3 / 0 | 3 / 0 |
| Verificación de mínimo privilegio | exit 0 | exit 0 |
| Backend tras recrearlo | — | `healthy`; `GET /api/v1/posts` → **200**; `/ready` → `{"status":"ready"}` |

Los dos caminos de recuperación están en el runbook §2.2.

---

## J. Anti-tautología: barrido de mutación

No basta con que las pruebas pasen: hay que demostrar que **fallan** si se quita el control
que dicen proteger. Se mutó el código de producción, se ejecutó el guarda correspondiente y
se restauró el archivo **byte a byte**, comprobando el SHA-256 después de cada caso.

| # | Mutación | Guarda | Resultado |
| --- | --- | --- | --- |
| M1b | `X-Content-Type-Options` cambia de valor | `test_cabeceras_api_tambien_en_errores` | Falla ✔ |
| M2 | `noindex` también en el sitemap | `test_sitemap_no_recibe_noindex` | Falla ✔ |
| M3 | CORS admite cualquier origen | `test_cors_no_concede_lectura_a_origen_ajeno` | Falla ✔ |
| M4 | Se retira la cota ASGI del cuerpo | `test_cuerpo_de_subida_excesivo…` | Falla ✔ |
| M5 | Se retira la redacción de cabeceras | Suite de redacción | Falla ✔ |
| M6 | Se reintroduce `str(exc.detail)` | `test_excepcion_http_no_refleja_detalles_internos` | **NO detectada** → prueba reforzada con 451 |
| M6b | La misma, contra la prueba reforzada | La misma | Falla ✔ |
| M7 | Se retira `verify()` de la imagen | `test_png_con_crc_incorrecto…` | Falla ✔ |
| M8 | Se acepta el primer `Origin` duplicado | `test_origen_duplicado_no_puede_evadir_csrf` | Falla ✔ |
| M9 | Se refleja el mensaje del validador | `test_validacion_no_filtra_el_mensaje…` | Falla ✔ |
| M10 | `read()` sin cota en el router | Suite de archivos | **NO detectada** → ver §D.2: no es un control observable |
| M11 | La cota ASGI cae por debajo del límite del archivo | Prueba de integración nueva | Falla ✔ |
| M12 | El dominio deja de comprobar el tamaño | La misma | Falla ✔ |
| M13 | `GRANT UPDATE` sobre `audit_events` al runtime | `runtime_privileges.py` | Falla ✔, exit 1 |
| M14 | CSP admite `script-src 'unsafe-inline'` | `security.config.test.ts` | Falla ✔ |
| M15 | `frame-src *` | La misma | Falla ✔ |
| M16 | Se anula el filtro de esquema del origen | La misma | **NO detectada** → prueba reforzada con `ftp://` |
| M16b | La misma, contra la prueba reforzada | La misma | Falla ✔ |
| M17 | El `map` de Nginx deja de reconocer `/admin` | Comprobación HTTP | Falla ✔: desaparecen `X-Robots-Tag` y `no-store` |

**Ninguna mutación quedó en el árbol de trabajo.** Cada una se restauró verificando el
hash; la de Nginx se ejecutó en un contenedor **desechable y aislado**, en el puerto 18080,
sin tocar el entorno en marcha, y tanto el contenedor como la configuración mutada se
eliminaron.

Los tres «no detectada» son el resultado valioso del ejercicio: dos destaparon pruebas
tautológicas —corregidas— y el tercero obligó a describir con precisión qué es y qué no es
la cota del router.

---

## K. CORS, Origin y CSRF

**En local no se introduce CORS innecesario.** Sitio y API comparten origen tras Traefik.
La misma lista explícita expresa la política de origen del panel (**D-15**).

| Caso | Comportamiento verificado |
| --- | --- |
| Origen exacto autorizado | `Access-Control-Allow-Origin` con el origen exacto, `Allow-Credentials: true`, `Vary: Origin` |
| Preflight de `POST` de login | **200**, métodos y cabeceras explícitos, **sin `*`**, con correlación |
| Origen ajeno, `null`, sufijo engañoso (`…example.test.ajeno.test`) | **Sin concesión** de CORS |
| Método o cabecera no autorizados (`TRACE`, `x-hostil`) | Preflight **400** |
| Lista vacía | No abre acceso **y** rechaza escrituras de navegador con **403** |
| `*`, URL con credenciales, con ruta, con puerto inválido, con `\`, con espacios | La configuración **no arranca**, y el mensaje **no repite el valor** |
| `Origin` duplicado en una escritura administrativa | **403** |
| Un `500` no controlado desde un origen permitido | Conserva CORS, cabeceras de seguridad y `X-Request-ID` |

`allow_credentials` nunca convive con comodín: es imposible por construcción, porque la
configuración rechaza `*` al arrancar.

Login, logout, `/me`, el CRUD administrativo y la carga de medios siguen funcionando: las
suites de `Task/011`, `Task/012` y `Task/015` pasan sin cambios.

---

## L. Cabeceras por superficie (S-05) y E-06

Comprobado por **HTTP real** contra el entorno levantado, no por lectura de código.
`scripts/security/check_http.py` inspecciona 15 rutas y termina en **`FALLOS=0`**, con
código de salida 0.

| Superficie | CSP | nosniff / frame / referrer / permissions | `X-Robots-Tag` | `Cache-Control` |
| --- | --- | --- | --- | --- |
| `/`, `/articulos`, `/favicon.svg` | `default-src 'self'`; sin `unsafe-*`; `frame-src` solo YouTube *nocookie* y Vimeo | Sí | **Ausente** | `no-cache, must-revalidate` |
| `/assets/…` (bundle real, extraído del HTML) | La misma | Sí | **Ausente** | `public, max-age=31536000, immutable` |
| `/robots.txt` | La misma | Sí | **Ausente** | Revalidado |
| `/admin`, `/admin/login?…`, `/admin/inexistente` | La misma | Sí | **`noindex, nofollow`** | **`no-store`** |
| `/administer` *(control negativo)* | La misma | Sí | **Ausente** | Revalidado |
| `/api/v1/posts`, `/api/v1/inexistente` | `default-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'` | Sí | `noindex, nofollow` | Contrato del recurso |
| `/api/v1/admin/auth/me` (**401**) | La misma | Sí | `noindex, nofollow` | **`no-store`** |
| `/sitemap.xml` | `default-src 'none'` | Sí | **Ausente** | Contrato del sitemap |
| `/health`, `/ready` | `default-src 'none'` | Sí | `noindex, nofollow` | — |

**`noindex` no es global.** El sitio público debe ser indexable; aplicarlo a todo sería un
fallo de producto disfrazado de seguridad. `/administer` es el control negativo: se parece
a `/admin` y **no** recibe la cabecera.

**HSTS ausente y comprobado como ausente.** El entorno sirve HTTP; anunciar HSTS ahí es
incorrecto. La comprobación lo exige explícitamente en las 15 rutas. El borde con TLS real
es `Task/033`–`Task/035`.

**E-06 queda cerrado sin JavaScript.** `Task/016` lo dejó **parcial**: `robots.txt` y
`meta noindex`, que un rastreador solo ve si ejecuta JavaScript. `X-Robots-Tag` viaja en la
respuesta del servidor, generado por un `map` de Nginx sobre `$request_uri` que contempla
mayúsculas y las formas escapadas del segmento. La mutación M17 demuestra que ese `map` es
el control que lo sostiene.

---

## M. Subidas de archivos (S-11)

Se conserva íntegro lo probado en `Task/010` —decodificación real, nada de fiarse de la
extensión ni del `Content-Type`, clave UUID independiente del nombre, *bucket* privado— y se
añaden dos capas:

1. **Cota del cuerpo antes de parsear** el *multipart*, en la capa ASGI: no se fía de
   `Content-Length` —lo valida y rechaza duplicados y valores no numéricos— y también corta
   por acumulación cuando la cabecera **no** viene. Probado en ambos casos.
2. **Verificación de la integridad del contenedor de imagen**, además de la decodificación.
   La prueba trae su **control positivo**: demuestra primero que el decodificador **sí**
   carga los píxeles de un PNG con CRC corrupto, y solo entonces exige que la validación lo
   rechace.

**Las dos cotas componen, y ahora hay una prueba que lo fija.** Un archivo de
`TAMANO_MAXIMO_BYTES + 1` cae justo entre ambas: sin sesión responde **401** —prueba de que
el transporte lo dejó pasar— y con sesión responde **413** con `image_too_large`, que es el
dominio rechazando. Sin la mitad sin sesión, la prueba no distinguiría qué capa contestó:
las dos responden 413. Mutaciones M11 y M12 lo confirman.

**Integración real ejecutada**: 20 pruebas de medios administrativos contra PostgreSQL y
MinIO reales, en verde.

---

## N. Markdown: sanitización y *embeds*

Se auditó el pipeline y **no se cambió**: `react-markdown` sin HTML crudo, `rehype-sanitize`
con esquema de permitidos y protocolos acotados, resultado como árbol React sin `innerHTML`.

Prueba adversaria nueva sobre **las dos superficies** —sitio público y vista previa del
panel— con un mismo documento hostil: `<script>`, `onerror`, `onclick`, `style`, `class`,
`javascript:`, `data:image/svg+xml`, `<iframe>` a un dominio ajeno y HTML crudo. Se exige a
la vez que **el contenido benigno siga siendo legible** —encabezado, `<strong>`, enlace e
imagen válidos— y que no quede ningún elemento, atributo ni protocolo ejecutable.

**Los *embeds* aprobados siguen funcionando bajo la CSP**: `frame-src` autoriza
`https://www.youtube-nocookie.com` y `https://player.vimeo.com`, exactamente los dos hosts
de la lista cerrada de `Task/014`, y `Permissions-Policy` les concede `fullscreen`,
`autoplay` y `picture-in-picture`. `frame-ancestors 'none'` convive con ello: gobierna quién
puede **enmarcar el sitio**, no a quién puede enmarcar el sitio.

**Sin `unsafe-inline` ni `unsafe-eval`.** El HTML construido no tiene un solo `<script>`
inline: se comprobó sobre el artefacto servido. Mutaciones M14 y M15.

---

## O. Errores y redacción (S-07, S-08, O-08, R-36)

**Fuga real encontrada y corregida.** Un validador propio incrusta `str(ValueError)` en el
mensaje de Pydantic, y ese mensaje se reflejaba al cliente. Un señuelo colocado en el valor
recibido **aparecía en la respuesta 422**. Ahora se conserva la **ubicación** del campo
—que es lo accionable— y no su texto. El frontend no consume ese texto: se verificó antes
de decidirlo.

Comprobado que ninguna respuesta 4xx/5xx expone contraseña, `Authorization`, cookie, token,
secreto, DSN, SQL, traza ni ruta del sistema de archivos, con señuelos en 400, 401, 403,
405, 422, **451** y 503, y en un `500` no controlado.

Se conserva lo que hace útil un error: **JSON válido**, `request_id` correlacionado con el
log, código estable y `Retry-After` cuando el contrato lo exige.

Redacción del log, ampliada sobre la arquitectura aprobada en `Task/017` **sin
sustituirla**: cabeceras `Authorization`, `Cookie` y `Set-Cookie` **completas** —una cookie
lleva varios pares y el valor no acaba en el primer token—, contraseña **y usuario** de una
URL autenticada, contraseñas con `/` o `:` dentro, valores entrecomillados con escapes, y
claves escritas con guion además de con guion bajo. Señuelos en **mensaje, contexto y cadena
de excepciones**, en `json` y en `text`, exigiendo a la vez que sobrevivan el diagnóstico,
el `request_id` y el `status_code`. **Idempotencia** comprobada.

**Coste declarado.** Redactar una cabecera sensible consume **el resto de esa línea**. Es
deliberado —`Cookie: a=1; b=2` no tiene dónde parar con seguridad— y es la dirección segura
del error. En formato `json`, que es el del entorno local y el de producción, `request_id`,
`status_code` y el contexto son campos propios y **no viajan dentro del mensaje**, así que
no se pierden.

---

## P. Autenticación

**No se reescribió nada.** `Task/011` está aprobada y sus guardas se auditaron y se
registran como evidencia.

**R-43 — bloqueo del único administrador.** Cubierto por **14** pruebas unitarias y **11**
de integración: umbral de cinco fallos, ventana de quince minutos configurable, **el bloqueo
no se alarga** por seguir fallando durante el bloqueo, el vencimiento libera, dos fallos
simultáneos cuentan dos, y la respuesta es **indistinguible** de unas credenciales
inválidas. El riesgo es una propiedad asumida del diseño; sigue **abierto**, con
recuperación operativa.

**R-44 — crecimiento de tablas.** **No se introdujo ningún proceso residente**, y la
búsqueda dirigida lo confirma: no hay *scheduler*, ni tarea de fondo, ni `cron` en el
backend. Un daemon dentro de FastAPI contradiría el destino Lambda. Sigue **abierto** y
diferido, con `Task/029` como propietario.

**R-46 — confianza en proxies.** El Compose fija `BLOG_TRUSTED_PROXY_HOP_COUNT=0`, el valor
*fail-closed*: no creerse `X-Forwarded-For` sin un proxy declarado. Probado en ambos
sentidos por `Task/011`.

**Cookie de sesión.** `HttpOnly` y `SameSite=Lax` intactos; `Secure=false` **solo** en local,
donde el entorno es HTTP, mediante variable de entorno explícita del Compose. La defensa
CSRF por `Origin` en métodos que cambian estado se conserva y se **refuerza**: un `Origin`
duplicado ya no puede evadirla.

---

## Q. Respaldos

**No se eliminó ningún conjunto.** Los cuatro que existían se conservan, incluido
`20260908-024710`, y se añadió el conjunto canónico posterior al endurecimiento.

| Conjunto | Creado (UTC) | Integridad |
| --- | --- | --- |
| `20260731-172039` | 2026-07-31T17:20:46Z | **Correcta** — 8 archivos |
| `20260907-020539` | 2026-09-07T02:06:13Z | **Correcta** — 8 archivos |
| `20260907-205816` | 2026-09-07T20:58:40Z | **Correcta** — 8 archivos |
| `20260908-024710` | 2026-09-08T02:47:32Z | **Correcta** — 8 archivos |
| **`20260908-034049`** *(posterior al endurecimiento)* | 2026-09-08T03:41:08Z | **Correcta** — 8 archivos, 309,40 KB |

- `Test-PathLiteralRegression.ps1`: **5 correctas, 0 fallidas** (la línea `ERROR` del
  registro es la salida esperada del caso que comprueba el rechazo de comodines).
- `Test-LocalBackup.ps1 -All`: **5 conjuntos verificados, 0 con problemas**.
- **`Restore-LocalBackupTest.ps1` sobre el conjunto nuevo: RESTAURACIÓN VERIFICADA.**
  PostgreSQL **CORRECTA** —17 tablas—, MinIO **CORRECTA** —64 objetos con SHA-256 de
  contenido y `Content-Type` coincidentes— y Portainer **CORRECTA** —HTTP 200, versión
  2.39.7, `InstanceID` coincidente—. Los recursos temporales se eliminaron y el entorno
  principal quedó intacto.

El conjunto nuevo refleja el estado **posterior** a la rotación de credenciales y a la
aplicación de las identidades runtime, e incluye el volumen de Portainer ya en 2.39.7.

**R-12 sigue abierto y no se disimula.** Los respaldos **no están cifrados**. Contienen
información sensible —incluidos los *hashes* de autenticación de Portainer— y su única
protección sigue siendo estar ignorados por Git y no salir de la máquina. No se introdujo
ninguna herramienta de cifrado: es **D-17**, de `Task/029`. Cifrar en el sitio los
existentes habría sido peor: una operación destructiva sobre la única copia.

---

## R. Validaciones finales

Todas ejecutadas **después** de la última corrección, no antes.

| Validación | Resultado |
| --- | --- |
| Backend `pytest -W error` completo, con PostgreSQL y MinIO reales | **1854 pasadas, 1 omitida**, 305,87 s |
| Backend Ruff / `ruff format --check` / MyPy / `pip check` | Verde / 312 archivos / 310 archivos / sin roturas |
| Frontend `format:check` / `lint` / `typecheck` / `build` | Verde |
| Frontend suite **canónica**, ejecución final con la máquina en reposo | **703 pasadas**, 0 fallidas, 41,16 s |
| Frontend suite **canónica**, ejecución intermedia bajo carga | **700 pasadas, 2 fallidas** por tiempo agotado |
| Frontend, los dos archivos afectados **en aislamiento** | **31 pasadas en 4,45 s** |
| Frontend `--maxWorkers=2` | **703 pasadas**, 0 fallidas |
| `npm audit` / `pip-audit` | 0 / 0 |
| `docker compose config --quiet` | Exit 0 |
| `docker compose up -d --wait` | Exit 0; los seis servicios sanos según su contrato |
| `check_http.py` | **`FALLOS=0`**, exit 0 |
| `runtime_privileges.py` sin flags | exit 0 |
| Escáner de secretos sobre archivos versionables | 0 hallazgos |
| Integridad de los cinco conjuntos de respaldo | 0 con problemas |
| Prueba de restauración aislada sobre el conjunto posterior al endurecimiento | **CORRECTA** en PostgreSQL, MinIO y Portainer |

### Sobre la suite canónica del frontend

Se registran **las dos** ejecuciones canónicas, no solo la verde. Una falló dos pruebas por
tiempo agotado a 5000 ms —`formularios.test.tsx:260`, ya conocida, y `routes.test.tsx:54`,
que no estaba en el baseline—; la otra pasó las 703.

**No es una regresión, y la evidencia es cuantitativa**, no una opinión:

| Ejecución | Estado de la máquina | Resultado | Tiempo de `environment` |
| --- | --- | --- | --- |
| Canónica, intermedia | Cargada | 700 pasadas, 2 fallidas | **287,09 s** |
| Canónica, final | En reposo | **703 pasadas** | **158,41 s** |
| `--maxWorkers=2` | — | **703 pasadas** | **69,87 s** |
| Los dos archivos en aislamiento | — | **31 pasadas en 4,45 s** | 1,88 s |

El tiempo de preparación del entorno de pruebas varía en un factor de cuatro entre
ejecuciones idénticas. Es exactamente **R-016-1**. **No se modificó ningún tiempo de espera,
ninguna expectativa y ningún parámetro de paralelismo** para conseguir el verde: la
ejecución en verde es la canónica, sin banderas.

---

## S. Documentación y criterio 12

Documentos tocados: esta ficha y este reporte; ROADMAP; STATUS; STAGE-05;
non-functional-requirements; security-boundaries; el runbook del entorno local; y el índice
de reportes.

**Se corrigió además un drift documental preexistente**, ajeno a esta tarea pero
incompatible con el criterio 5: el índice de reportes omitía `Task/010` a `Task/017`, cuyos
reportes existían desde su aprobación. Queda completo y con la omisión anotada como hecho
fechado.

**Criterio 12 — barrido sobre todo lo modificado.** Clasificación A/B/C:

| Clase | Contenido |
| --- | --- |
| **A — regla permanente** | Los dos planos de identidad; que migrar es del plano administrativo; que `noindex` no es global; que HSTS no se anuncia sobre HTTP; que rotar un secreto exige flag explícito; que los respaldos son sensibles |
| **B — hecho histórico fechado** | Los SHA base del nacimiento de la rama; el baseline del 2026-09-07; los recuentos de escaneo del 2026-09-07; las fechas de aprobación de Task016 y Task017; la nota de saneamiento del ROADMAP y la del índice de reportes |
| **C — estado Git/GitHub vivo** | **0** |

No se persiste ninguna afirmación sobre un pull request abierto, una rama remota, una
fusión pendiente, el árbol de trabajo actual, el área de preparación, ni el estado de
`origin`. Los SHA base se conservan **presentados como hechos fechados del nacimiento de la
rama**, que es lo que el criterio 12 permite explícitamente.

---

## T. Roadmap

Aprobación del usuario recibida el **2026-09-08**:

- Avance global: **18 de 41 — 44 %**.
- ETAPA 05: **Completada, 3 de 3 — 100 %**.
- `Task/018`: **Aprobada**. `Task/019`: **Pendiente, no iniciada**.

Se mantienen los límites aceptados de la etapa: rendering sin JavaScript
(**D-21**, **ADR-009 en Propuesta**) y hallazgos residuales de imágenes (§F).

---

## U. Regla de Git

El estado operativo se consulta en Git, conforme a WORKFLOW §6.1; no se persiste aquí.

---

## V. Bloqueos

**Ninguno que impida validar la tarea.** Los seis defectos de §D.1 se corrigieron dentro de
`Task/018` y su corrección está verificada. Lo que queda son residuos **clasificados, con
propietario y con su motivo**: R-09, R-12, R-018-1, R-018-2, R-018-3, R-018-4, R-44 y R-46.

---

## W. Veredicto

**TASK018 APROBADA POR EL USUARIO EL 2026-09-08.**

Las decisiones de implementación de la ficha §12 quedan **vigentes**. No hay ADR
nuevo ni se promueve ADR-009: la estrategia de rendering sigue abierta.

**Regla permanente:** la aprobación autoriza commit, integración en `dev`, publicación
y pull request `Task/018-Endurecimiento-de-Seguridad → main`.
**El pull request solo lo fusiona el usuario**
([WORKFLOW §3 y §6.1](../project-management/WORKFLOW.md)). El estado vivo de Git y GitHub
se consulta con `git fetch --prune`, `git ls-remote --heads origin "Task/*"` y
`gh pr list`; deliberadamente **no se escribe aquí**.

---

## X. Validaciones del cierre aprobado — 2026-09-08

Aprobación recibida mediante `approved: Task/018-Endurecimiento-de-Seguridad`.
Se revisaron los cambios de los tres repositorios contra el alcance de la ficha.
El cierre actualiza ocho documentos de aprobación y gobierno; **no modifica el
comportamiento funcional aprobado**. También corrige la fila histórica de Task017
que aún figuraba como pendiente en el inventario de STATUS.

| Comprobación repetida para el cierre | Resultado observado |
| --- | --- |
| Backend `pytest -W error -q`, completo con PostgreSQL y MinIO reales | **1854 pasadas, 1 omitida**, **334,56 s**; omisión estructural de `time.tzset` en Windows |
| Backend Ruff, formato, MyPy y `pip check` | Sin errores; 312 archivos formateados y 310 comprobados por MyPy |
| `pip-audit -r requirements.txt`, repetido el 2026-09-08 | **0 vulnerabilidades conocidas** |
| Frontend `npm ci`, formato, lint y typecheck | Código de salida 0; auditoría npm con **0 vulnerabilidades** |
| Frontend `npm run test:run`, sin cambiar paralelismo ni timeouts | **703 pasadas**, 74 archivos, **42,62 s** |
| Frontend build con sitio/API HTTP local y con orígenes HTTPS | Ambos con código de salida 0 |
| Docker Compose: configuración y build de backend, frontend, PostgreSQL y Traefik | Código de salida 0 |
| Servicios locales | Cinco sondas sanas; Portainer en ejecución, sin sonda por diseño |
| `check_http.py --base-url http://localhost:8081` | 15 rutas y preflights; **FALLOS=0** |
| `runtime_privileges.py`, sin flags de provisión o rotación | Controles positivos y negativos de PostgreSQL y MinIO correctos |
| `Test-LocalBackup.ps1 -All` | **5 conjuntos íntegros**, 0 con problemas |
| Sintaxis de los tres scripts PowerShell modificados | **0 errores** |
| Archivos versionables y enlaces relativos de los documentos tocados | **709 archivos**, 0 coincidencias con credenciales locales y 0 enlaces rotos |
| Trivy 0.74.0, escaneo de secretos sobre los 709 archivos versionables | **0 hallazgos** |
| `git diff --check` en los tres repositorios | Sin errores |

**Incidencia del ejecutor, registrada.** El primer intento del frontend se
interrumpió antes de completar Vitest porque PowerShell, con
`ErrorActionPreference=Stop`, interpretó su salida estándar de error como una
excepción. Se corrigió el ejecutor para comprobar el código de salida del proceso.
La repetición canónica pasó sin modificar código, expectativas ni tiempos de espera.

**Advertencia de Vite conservada y documentada.** Los imports sin extensión de
`robots.config` y `security.config` no son compatibles con el futuro cargador
`configLoader: native`; el cargador actual completa tests y builds con código 0.
Su revisión corresponde a **Task019** al definir el entorno de CI. No se silencia
la advertencia ni se cambia la configuración aprobada durante este cierre.

Las restauraciones aisladas, rotaciones y auditorías de imágenes de la implementación
conservan su evidencia fechada en §F, §G, §I y §Q. Este cierre no vuelve a rotar
credenciales ni a restaurar datos. Se mantienen los residuos y propietarios de la
ficha §18. **Criterio 12: C = 0**; aprobación y resultados fechados son duraderos,
el estado operativo de ramas y PR se consulta en Git y GitHub.
