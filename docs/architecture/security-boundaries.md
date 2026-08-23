# Límites de seguridad

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/002-Definir-MVP-y-Arquitectura` (2026-07-26) |
| **Fecha** | 2026-07-26 · §8 añadida y **aprobada** el 2026-08-15 (`Task/005.2`) · §9 añadida y **aprobada** el 2026-08-15 (`Task/005.3`) · §10 añadida y **aprobada** el 2026-08-23 (`Task/006.2`) |

Identifica los **componentes** del sistema, qué comunicaciones entre ellos están
permitidas y cuáles están explícitamente prohibidas.

Relacionados: [non-functional-requirements.md](non-functional-requirements.md) ·
[software-architecture.md](software-architecture.md) ·
[ADR-001 — Local-first](../adr/ADR-001-local-first.md)

---

## 1. Componentes y zonas de confianza

| # | Componente | Zona | Nivel de confianza |
| --- | --- | --- | --- |
| C-01 | **Navegador público** | Internet | **Ninguna.** Toda entrada es hostil hasta validarse. |
| C-02 | **Navegador administrativo** | Internet | **Ninguna por sí mismo.** La confianza proviene de la sesión autenticada, verificada en el servidor. |
| C-03 | **Frontend público** | Cliente | Código público. Nada que contenga es secreto. |
| C-04 | **Panel administrativo** | Cliente | Código público. **No es un límite de seguridad.** |
| C-05 | **API pública** | Servidor | Expuesta a internet. Solo lectura. |
| C-06 | **API administrativa** | Servidor | Expuesta a internet, protegida por autenticación. |
| C-07 | **PostgreSQL** | Datos | Solo accesible desde el backend. |
| C-08 | **MinIO / Amazon S3** | Datos | Privado por defecto. Acceso mediante URL prefirmada. |
| C-09 | **Portainer** | Local, privilegiado | **Solo local.** Acceso al socket de Docker. |
| C-10 | **GitHub Actions** | CI/CD | Ejecuta código; accede a la nube con credenciales temporales. |
| C-11 | **Servicios AWS** | Nube | Lambda, API Gateway, S3, SSM, CloudWatch. |
| C-12 | **Emulador AWS local** (`Task/005.2`) | Local, **privilegiado** | **Solo local.** Acceso al socket de Docker, igual que C-09. **Nunca contiene datos ni credenciales reales.** Ver §8. |
| C-13 | **VPS de producción** (`Task/005.3`) | Internet, **host propio** | **Ninguna por sí mismo.** Host expuesto a Internet, administrado por el proyecto. Su compromiso implica **exposición de todos los datos del blog**. Ver §9. |
| C-14 | **PgBouncer** | Internet, en el VPS | **Único endpoint de la capa de datos alcanzable desde fuera** del VPS. Es el *boundary* de la base de datos. El SSH administrativo del host es un canal **separado**, no forma parte de esta capa. |
| C-15 | **PostgreSQL de producción** | Datos, **privado en el VPS** | **Nunca alcanzable desde Internet.** Solo acepta conexiones internas del VPS. |
| C-16 | **Grafana Alloy** (`Task/006.2`) | En el VPS, **solo salida** | Agente de telemetría. **No abre puertos de entrada.** Lee logs y métricas del host y de sus servicios: **ve datos sensibles por diseño**. Ver §10. |
| C-17 | **Grafana Cloud** (`Task/006.2`) | Internet, **tercero** | Destino externo de telemetría. **Los datos que le llegan salen del perímetro del proyecto.** No tiene acceso a AWS ni al VPS mientras **D-20** siga abierta. Ver §10. |

> **C-03 y C-04 no son límites de seguridad.** Ocultar un botón no protege nada: la
> autorización se decide siempre en C-06.

---

## 2. Comunicaciones permitidas

| Origen | Destino | Permitido | Condición |
| --- | --- | --- | --- |
| C-01 Navegador público | C-03 Frontend público | Sí | HTTPS en producción. |
| C-01 Navegador público | C-05 API pública | Sí | Solo lectura, CORS restringido, solo contenido `published`. |
| C-01 Navegador público | C-06 API administrativa | **Solo `login`** | El resto exige sesión válida. |
| C-02 Navegador admin | C-04 Panel | Sí | Rutas del panel, no indexables. |
| C-02 Navegador admin | C-06 API administrativa | Sí | Con sesión válida verificada en el servidor. |
| C-03 / C-04 Frontend | C-05 / C-06 API | Sí | Único canal de datos del frontend. |
| C-05 / C-06 API | C-07 PostgreSQL | Sí | Credenciales de mínimo privilegio, TLS en producción. |
| C-05 / C-06 API | C-08 Almacenamiento | Sí | A través de la interfaz `ObjectStorage`. |
| C-06 API administrativa | C-08 Almacenamiento | Sí | Genera URLs prefirmadas con expiración. |
| C-01 / C-02 Navegador | C-08 Almacenamiento | Sí, **solo lectura** | Únicamente mediante URL prefirmada emitida por el backend. |
| C-10 GitHub Actions | C-11 Servicios AWS | Sí | Mediante OIDC con rol temporal (`Task/028`). |
| C-11 Lambda | C-11 SSM Parameter Store | Sí | Lectura de configuración, permisos mínimos. |
| C-11 Lambda | C-11 CloudWatch | Sí | Escritura de logs. |
| C-09 Portainer | Docker local | Sí | **Solo en la máquina local.** |
| Terraform local | C-12 Emulador AWS local | Sí | Solo con endpoint local explícito y credenciales ficticias (§8). |
| AWS CLI / SDK local | C-12 Emulador AWS local | Sí | Solo con `--endpoint-url` / `AWS_ENDPOINT_URL` explícito. |
| C-12 Emulador AWS local | Docker local | Sí | **Solo en la máquina local.** Privilegio de nivel host (§8). |
| C-11 Lambda | C-14 PgBouncer | Sí | **TLS obligatorio** con validación del certificado del servidor, y autenticación fuerte (§9). |
| C-14 PgBouncer | C-15 PostgreSQL | Sí | Únicamente por la **red interna del VPS**; nunca por la interfaz pública. |
| Proceso de backup del VPS | C-11 Amazon S3 | Sí | Backup **cifrado**, con credenciales de mínimo privilegio. Destino **fuera del host** (§9). |
| Operador | C-13 VPS | Sí | **SSH solo por llave**, nunca por contraseña. |
| C-16 Grafana Alloy | C-17 Grafana Cloud | Sí | **Solo salida**, cifrada. Sin secretos ni datos personales innecesarios en la telemetría (§10). |
| C-16 Grafana Alloy | C-13 / C-14 / C-15 en el VPS | Sí, **solo lectura** | Lee logs, métricas y estado **dentro del host**. No modifica servicios ni datos. |
| C-17 Grafana Cloud | C-11 CloudWatch | **Todavía no** | Contemplado en la arquitectura, **no implementado**. Exigirá permisos **mínimos y de solo lectura** (**D-20**, `Task/031`). |

---

## 3. Comunicaciones prohibidas

| Origen | Destino | Motivo |
| --- | --- | --- |
| C-01 / C-02 Navegador | C-07 PostgreSQL | La base de datos **nunca** se expone a internet ni al cliente. |
| C-03 / C-04 Frontend | C-07 PostgreSQL | El frontend no tiene credenciales de base de datos. |
| C-03 / C-04 Frontend | C-08 Almacenamiento con credenciales | El frontend **nunca** posee claves de MinIO ni de S3. |
| C-01 Navegador público | C-08 Bucket directo | El bucket es privado; sin acceso público sin URL prefirmada. |
| C-01 Navegador público | Contenido `draft` o `archived` | La API pública jamás lo devuelve, en ningún endpoint. |
| C-01 / C-02 Navegador | C-09 Portainer | **Portainer no se publica.** Solo acceso local. |
| Internet | C-09 Portainer | Nunca expuesto a internet, en ningún entorno. |
| C-09 Portainer | Contenido del blog | Portainer **no administra contenido**. |
| C-10 GitHub Actions | C-11 AWS con claves permanentes | Prohibido: solo credenciales temporales por OIDC. |
| C-10 GitHub Actions | `terraform destroy` sobre **infraestructura real** | Ninguna automatización destruye infraestructura real: AWS, Cloudflare ni VPS (`Task/039`). El `destroy` contra el **emulador AWS efímero** de un job de CI sí está permitido: no hay recurso real que perder y el laboratorio se tira entero al terminar (§8.2). |
| C-11 Lambda | Recursos fuera de su rol | Permisos mínimos, acotados a lo que necesita. |
| Cualquiera | Secretos en Git | Ningún secreto se versiona, en ningún repositorio. |
| Internet o LAN | C-12 Emulador AWS local | **Nunca expuesto.** Ni el puerto 4566 ni sus rangos auxiliares (§8). |
| Credenciales AWS **reales** | C-12 Emulador AWS local | Prohibido: expone una credencial real a un servicio local que no la necesita ni la protege. |
| Secretos **reales** | C-12 SSM emulado | El `SecureString` del emulador **no cifra**. Solo valores ficticios. |
| Herramienta apuntada al laboratorio | C-11 Servicios AWS reales | Prohibido por accidente: exige guardas *fail-closed* antes de `apply` y `destroy` (§8.2). |
| Internet | C-15 PostgreSQL de producción | **La base de datos nunca se publica.** Solo C-14 PgBouncer está expuesto (§9). |
| C-01 / C-02 Navegador | C-14 PgBouncer | El cliente **nunca** habla con la capa de datos; solo lo hace C-11 Lambda. |
| C-11 Lambda | C-14 PgBouncer **sin TLS** | Prohibido en producción: el tramo atraviesa Internet. |
| Credenciales de producción | Git | Ninguna credencial de la base de datos se versiona, en ningún repositorio. |
| Backup | Permanecer **solo** en el VPS | Un backup que solo vive en el host no protege de perder el host (§9). |
| Internet | C-16 Grafana Alloy | El agente **no expone ningún puerto de entrada**. Su tráfico es **saliente**; el firewall sigue *deny-by-default* (§10). |
| Secretos, credenciales o datos personales innecesarios | C-17 Grafana Cloud | La telemetría **sale del perímetro del proyecto**. Regla **O-08** y **O-09**: no viaja lo que no debe salir (§10). |
| C-17 Grafana Cloud | C-13 VPS o C-11 AWS con permisos amplios | Ningún destino de telemetría recibe acceso administrativo. Cuando **D-20** se resuelva, será **solo lectura** y de **permiso mínimo** (§10). |
| **Stack de observabilidad autohospedado** (Grafana, Prometheus, Loki) | C-13 VPS | Prohibido por [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md): compite por los recursos reservados a PostgreSQL y cae con el host que debía vigilar. |

---

## 4. Portainer — reglas explícitas

Portainer CE es la herramienta con **mayor privilegio** del entorno local y merece reglas
propias:

| Regla | Detalle |
| --- | --- |
| **Solo acceso local** | Se accede únicamente desde la máquina de desarrollo. Nunca se expone a internet ni a la red compartida. |
| **No forma parte de `/admin`** | Es una herramienta de infraestructura, ajena al panel administrativo del blog. No comparte autenticación, sesión ni interfaz. |
| **No se publica** | No se despliega en producción, en ninguna forma (ver [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md)). |
| **No administra contenido** | No crea, edita, publica ni elimina contenido del blog. Solo observa contenedores. |
| **Acceso privilegiado al socket de Docker** | Quien controla el socket de Docker controla el equipo: es equivalente a acceso de administrador. Se considera y se trata como tal. |

Consecuencia práctica: Portainer se protege con credenciales propias, no se publica en
ningún puerto accesible desde fuera del equipo, y su compromiso se considera un incidente
de **nivel host**, no de nivel aplicación.

---

## 5. Superficies de ataque y controles

| Superficie | Riesgo principal | Control previsto | Tarea |
| --- | --- | --- | --- |
| Endpoint de login | Fuerza bruta, enumeración de usuarios | Rate limiting, bloqueo temporal, error genérico, auditoría | `Task/011` |
| Endpoints administrativos | Acceso no autorizado | Autenticación obligatoria verificada en servidor | `Task/011`, `Task/012` |
| Subida de imágenes | Archivo malicioso, agotamiento de espacio | Validación de MIME y tamaño, nombre no predecible, bucket privado | `Task/010`, `Task/018` |
| Renderizado de Markdown | XSS almacenado | Sanitización obligatoria en render y vista previa | `Task/014`, `Task/015` |
| Embeds de video | Contenido de terceros no controlado | Lista cerrada de proveedores permitidos | `Task/014` |
| Búsqueda | Inyección | Parámetros tratados como datos, nunca interpolados | `Task/009` |
| Enlaces externos | *Tabnabbing* | `rel="noopener noreferrer"` | `Task/014` |
| CORS | Origen no autorizado | Lista explícita por ambiente, nunca `*` en producción | `Task/018`, `Task/033` |
| Mensajes de error | Filtración de información | Modelo común de error sin trazas internas | `Task/009`, `Task/018` |
| Logs | Filtración de secretos | Lista de campos a redactar | `Task/017` |
| CI/CD | Robo de credenciales | OIDC con roles temporales, secretos enmascarados | `Task/028`, `Task/038` |
| Bucket de objetos | Exposición pública accidental | Bloqueo de acceso público y verificación explícita | `Task/030` |
| **Emulador AWS local** | Control del socket de Docker ⇒ control del host | Solo local, nunca expuesto, versión fijada (§8) | `Task/025`, `Task/018` |
| **Endpoint del emulador (4566)** | Exposición a LAN o a internet | Publicación restringida a `127.0.0.1`; verificación en los runbooks | `Task/025`, `Task/026` |
| **Herramientas de IaC** | Actuar sobre **AWS real** por falta de endpoint | Guardas *fail-closed* antes de `apply` y `destroy` (§8.2) | `Task/025`, `Task/026` |
| **PgBouncer expuesto** | Acceso no autorizado a la capa de datos | TLS obligatorio, autenticación fuerte, firewall *deny-by-default* (§9) | `Task/029`, `Task/018` |
| **SSH del VPS** | Fuerza bruta, credenciales robadas | Solo llave, sin contraseña, servicios mínimos (§9) | `Task/029`, `Task/018` |
| **Host del VPS sin parchear** | Vulnerabilidades acumuladas en SO, PostgreSQL y PgBouncer | Política de actualizaciones y parcheo definida en `Task/029` | `Task/029`, `Task/018` |
| **Backups del VPS** | Fuga de datos si se almacenan sin cifrar; pérdida total si no salen del host | Cifrado y destino externo con credenciales de mínimo privilegio (§9) | `Task/029`, `Task/026` |

---

## 6. Principios transversales

1. **La autorización se decide siempre en el servidor.** El frontend nunca es la barrera.
2. **Mínimo privilegio** en cada credencial, rol y política.
3. **Privado por defecto**: buckets, base de datos y herramientas de infraestructura.
4. **Los secretos nunca entran en Git** ni en el build del frontend ni en los logs.
5. **Toda entrada externa es hostil** hasta validarse en el servidor.
6. **Los errores no enseñan de más**: ni trazas, ni existencia de recursos no visibles.
7. **Todo lo administrativo deja rastro** en auditoría.
8. **Portainer es local y privilegiado**, nunca parte del producto.
9. **Toda herramienta con acceso al socket de Docker es privilegio de nivel host**, se
   llame como se llame. Su compromiso es un incidente de host, no de aplicación.
10. **La base de datos nunca se expone a Internet**, en ningún entorno. Si hay que
    alcanzarla desde fuera, se hace a través de un *boundary* explícito y cifrado
    (`Task/005.3`).

---

## 7. Qué queda para tareas posteriores

| Elemento | Tarea |
| --- | --- |
| Mecanismo de autenticación y estrategia CSRF | `Task/011` |
| Herramienta e implementación de rate limiting | `Task/011`, `Task/018` |
| Cabeceras de seguridad concretas y sus valores | `Task/018` |
| Lista definitiva de tipos MIME y tamaños permitidos | `Task/010`, `Task/018` |
| Proveedores de video permitidos | `Task/014` |
| Política IAM de la Lambda y del rol OIDC | `Task/028`, `Task/032` |
| Política del bucket y expiración de URLs prefirmadas | `Task/030` |
| Campos a redactar en los logs | `Task/017` |
| Guardas *fail-closed* del laboratorio local y su verificación | `Task/025`, `Task/026` |
| Revisión del *networking* de Docker del laboratorio | `Task/025` |
| *Hardening* concreto del VPS, reglas de firewall y política de parcheo | `Task/029`, `Task/018` |
| Configuración de TLS, SCRAM y evaluación de mTLS en PgBouncer | `Task/029` |
| **Ciclo de vida del certificado de PgBouncer**: emisión, CA, *hostname*, renovación, alerta de caducidad y confianza desde Lambda | `Task/029`; validado en `Task/040` |
| Procedimiento de backup, cifrado, retención y prueba de restore | `Task/029`, `Task/026` |
| **Identidad con la que el VPS escribe sus backups en AWS** (**D-16**) | Decide `Task/029` · materializa `Task/030` · valida `Task/040` |
| ***Baseline* de observabilidad del VPS**, incluida la notificación de fallo de backup | `Task/029`; validado en `Task/040`. **No** `Task/017` —local— ni `Task/031` —solo AWS— |
| **Credenciales de CI hacia Cloudflare y el proveedor del VPS**, con *scopes* y rotación | `Task/039`. `Task/028` cubre **solo** GitHub → AWS |
| **Guardas de destino multi-provider** antes de un `apply` real | `Task/039`, sobre las guardas de `Task/025` |
| **Canal de migraciones en producción**: credencial, orden y protección contra ejecución accidental | `Task/038` |

---

## 8. Emulador AWS local (C-12) — reglas explícitas

> **Estado: Vigente** ✔ — aprobado en `Task/005.2` el 2026-08-15. Estrategia completa:
> [aws-local-parity.md](aws-local-parity.md) ·
> [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) — **Aceptada**.

El *AWS Local Parity Lab* introduce un componente con **el mismo nivel de privilegio que
Portainer**, y por la misma razón: **necesita el socket del demonio de Docker** para
ejecutar las funciones Lambda en contenedores reales.

Quien controla el socket de Docker **controla el equipo**: puede crear, modificar y
destruir contenedores, redes y volúmenes de cualquier proyecto de la máquina —incluidos los
volúmenes de PostgreSQL y MinIO del entorno local del blog. Esto **agrava R-09**: pasa a
haber más de un componente con capacidad administrativa sobre el mismo demonio.

### 8.1 Controles obligatorios

| # | Regla | Detalle |
| --- | --- | --- |
| S-01 | **Publicación solo en `127.0.0.1`** | Cuando el host necesite alcanzar el endpoint, se publica únicamente en loopback. |
| S-02 | **Nunca exponer el puerto 4566 a internet** | Sin excepciones, en ningún entorno. |
| S-03 | **Evitar exposición innecesaria a la LAN** | Tampoco los rangos auxiliares (proxies de base de datos, motores de búsqueda). |
| S-04 | **Credenciales ficticias, exclusivamente locales** | Su valor es público por diseño; no protegen nada y no deben aparentar lo contrario. |
| S-05 | **Nunca usar credenciales AWS reales contra el emulador** | Prohibido sin excepción. |
| S-06 | **Ningún secreto se versiona** | Regla ya vigente, sin cambios. |
| S-07 | **Ningún secreto real en el SSM emulado** | Su `SecureString` **no cifra** el valor. Solo datos ficticios. |
| S-08 | **El control de Docker es privilegio de host** | Mismo tratamiento que Portainer (§4). |
| S-09 | **Revisar el *networking* de Docker antes de implementar** | Redes, alias y DNS embebido se revisan en `Task/025`. |
| S-10 | **Versión fijada, nunca `latest` ni `nightly`** | Una etiqueta móvil en infraestructura reproducible es un defecto. |
| S-11 | **Actualizar es un cambio de infraestructura** | Se revisa el CHANGELOG y se revalida la matriz de paridad. |

### 8.2 Protección contra AWS real accidental — *fail-closed*

> **Un comando pensado para el laboratorio no debe poder terminar hablando con AWS real por
> olvidar un endpoint.**

Es el fallo más caro posible: un `apply` —o peor, un `destroy`— que resuelve contra AWS de
verdad. La implementación futura **debe** incluir guardas que **fallen cerrado**:

| # | Guarda |
| --- | --- |
| G-01 | **Entorno explícito** (`local` \| `production`). Sin declaración, no se ejecuta nada. |
| G-02 | **Endpoint explícito.** Para el destino local, su ausencia **aborta**; nunca se continúa con un valor por omisión. |
| G-03 | **Verificación de cuenta**: comprobar que el *account id* observado es el ficticio esperado. |
| G-04 | **Rechazo de credenciales con forma de credencial real** en el flujo local. |
| G-05 | **Validación del destino previa a `apply` y `destroy`**, como paso bloqueante, no como aviso posterior. |

**Ninguna se implementa en `Task/005.2`.** Son requisito para `Task/025` (guardas técnicas)
y `Task/026` (procedimiento escrito que las ejerce), y son coherentes con la prohibición ya
vigente de que **ninguna automatización ejecute `terraform destroy` contra infraestructura
real** (§3). Contra un **emulador AWS efímero** de CI, el `destroy` es legítimo: es el
propio laboratorio el que se destruye, no un recurso real. Precisado en `Task/005.6`.

### 8.3 Qué NO cambia

- El emulador **no forma parte del producto** ni del camino de la petición en producción.
- **No se despliega en la nube**, en ninguna forma.
- **No sustituye** a Portainer, ni a MinIO, ni a PostgreSQL local.
- **No relaja** ninguna regla existente de este documento.

---

## 9. VPS de producción (C-13, C-14, C-15) — reglas explícitas

> **Estado: Vigente** ✔ — aprobado en `Task/005.3` el 2026-08-15. Estrategia completa:
> [production-postgresql-vps.md](production-postgresql-vps.md) ·
> [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) — **Aceptada**.

Situar PostgreSQL de producción en un VPS externo introduce una **superficie de ataque
nueva y permanente**: un host propio, expuesto a Internet, con SSH y un servicio de base de
datos delante. Es el componente cuyo compromiso tendría **el mayor impacto del proyecto**:
implica la exposición de todos los datos del blog.

Hasta ahora ningún dato de producción vivía en infraestructura administrada por el proyecto.
A partir de esta decisión, sí.

### 9.1 Topología obligatoria

```
Aplicación:     Internet ──TLS──► PgBouncer (C-14, único endpoint de la capa de datos)
                                      │
                                      ▼  red interna del VPS
                                  PostgreSQL (C-15, nunca público)

Administración: Operador  ──SSH──► Host del VPS (C-13, canal separado, solo por llave)
```

**Dos canales distintos, no uno.** La aplicación llega a los datos **únicamente** por
PgBouncer. La administración del host usa **SSH**, que es un canal **separado y ajeno a la
capa de datos**, sujeto a sus propias reglas (V-05, V-06, V-07). Decir que PgBouncer es «lo
único alcanzable del VPS» sería inexacto: lo correcto es que es **lo único alcanzable de la
capa de datos**.

| # | Regla |
| --- | --- |
| V-01 | **PostgreSQL no se expone a Internet.** Su puerto no se publica en la interfaz pública; el *binding* y el firewall deben hacerlo cierto por configuración. |
| V-02 | **PgBouncer es el único endpoint de la capa de datos** alcanzable desde fuera del VPS. El SSH administrativo no forma parte de esa capa. |
| V-03 | **El tramo `Lambda → PgBouncer` exige TLS**, con **validación del certificado del servidor**. Un TLS que no valida no protege frente a un intermediario. |
| V-04 | **Autenticación fuerte**, con **SCRAM-SHA-256** como mecanismo preferente cuando la implementación lo permita. |
| V-05 | **Firewall *deny-by-default***: solo se abre lo estrictamente necesario. |
| V-06 | **SSH solo mediante llave.** Sin autenticación por contraseña cuando sea viable. |
| V-07 | **Servicios mínimos** en el host: nada que no sea necesario para la capa de datos. |
| V-08 | **Ningún secreto se versiona.** La cadena de conexión de producción no existe en el repositorio. |
| V-09 | **Actualizaciones y parcheo** del sistema operativo, PostgreSQL y PgBouncer como práctica definida, no como reacción. |
| V-10 | **Docker o el runtime que se use, con el mínimo privilegio razonable.** |
| V-11 | **Monitoreo del espacio en disco** y de los recursos: un disco lleno detiene PostgreSQL y puede impedir el propio backup. |
| V-12 | **Backups cifrados y fuera del host**, con credenciales de mínimo privilegio hacia el destino — **escritura sobre un prefijo concreto**, sin lectura ni borrado del resto. El **mecanismo de identidad** es **D-16**, abierta: el compromiso del VPS **no debe** implicar el compromiso de la cuenta AWS. |
| V-13 | **El compromiso del VPS se trata como exposición de datos**, no como una incidencia de servicio. |

### 9.2 No hay *security through obscurity*

**No** cuentan como control suficiente: cambiar el puerto 5432 · usar solo una contraseña
larga · *rate limiting* en solitario · confiar en que nadie conozca la IP.

Un puerto distinto puede usarse por motivos **operativos**, nunca como frontera principal
de seguridad. La frontera son **firewall, *binding* privado, TLS y autenticación**.

### 9.3 mTLS — evaluable, no obligatorio todavía

TLS mutuo es una mejora razonable de *hardening*, pero **no se declara obligatorio**. Antes
de adoptarlo hay que resolver rotación de certificados, impacto de una caducidad —dejaría el
sitio sin base de datos—, compatibilidad y entrega del certificado a Lambda sin versionarlo.
Se evalúa en `Task/029`.

### 9.4 Qué NO cambia

- **El VPS no aloja la aplicación.** FastAPI sigue en AWS Lambda.
- **El frontend no cambia.** Cloudflare Pages sigue igual.
- **El entorno local no cambia.** PostgreSQL en Docker sigue siendo el destino de desarrollo.
- **No relaja** ninguna regla existente de este documento; añade las suyas.

---

## 10. Observabilidad de producción (C-16, C-17) — reglas explícitas

> **Estado: Vigente** ✔ — aprobado en `Task/006.2` el 2026-08-23. Decisión:
> [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) — **Aceptada**.
> Documento canónico:
> [target-production-architecture.md](target-production-architecture.md) §10–§13.

La observabilidad de producción introduce **una frontera de confianza que las anteriores no
tenían**: un destino **externo al proyecto y a sus dos proveedores**. Hasta ahora, todo dato
del sistema vivía en AWS, en Cloudflare, en el VPS o en la máquina local. **La telemetría
enviada a Grafana Cloud sale de ese perímetro.**

Y el agente que la envía —**Grafana Alloy**, C-16— vive **dentro del VPS**, que es el
componente cuyo compromiso tendría el mayor impacto del proyecto (§9). Un agente que lee
logs del host y de PostgreSQL **ve datos sensibles por diseño**: esa es su función.

### 10.1 Topología

```
VPS (C-13)
  ├── PostgreSQL (C-15) ─┐
  ├── PgBouncer (C-14) ──┤ lectura de logs, metricas y estado
  └── host ──────────────┘
                 │
          Grafana Alloy (C-16)   ← solo salida; NO abre puertos de entrada
                 │
                 ▼  TLS saliente
          Grafana Cloud (C-17)   ← TERCERO. Los datos salen del perimetro

AWS
  CloudWatch minimo (C-11) ····► Grafana Cloud   (D-20, NO implementada)
```

### 10.2 Controles obligatorios

| # | Regla | Detalle |
| --- | --- | --- |
| G-01 | **Alloy no abre puertos de entrada** | Su tráfico es **saliente**. El firewall del VPS sigue *deny-by-default* (regla V-05). |
| G-02 | **La telemetría no lleva secretos** | Ni contraseñas, ni tokens, ni cadenas de conexión, ni claves. Aplicación directa de **O-08**. |
| G-03 | **La telemetría no lleva datos personales innecesarios** | Requisito **O-09**. Enviar a un tercero es exportar: qué se recolecta **es parte del diseño**, no configuración. |
| G-04 | **La credencial de Alloy es un secreto del VPS** | Cifrada, clave fuera del repositorio, permisos mínimos y rotación definida (**D-17**, `Task/029`). |
| G-05 | **Alloy con el mínimo privilegio razonable en el host** | Lee; no administra. No necesita ser raíz para todo lo que hace: lo que exija privilegio se acota. |
| G-06 | **Ningún secreto de Grafana se versiona** | Regla ya vigente (V-08), sin excepción para este componente. |
| G-07 | **Grafana Cloud no recibe acceso a AWS todavía** | **D-20** abierta. Cuando se resuelva será **solo lectura** y de **permiso mínimo**. |
| G-08 | **El compromiso de Grafana Cloud no debe implicar el compromiso de AWS ni del VPS** | Mismo criterio exigido a **D-16**: son principals distintos, con superficies distintas. |
| G-09 | **No se autohospeda un *stack* de observabilidad en el VPS** | Grafana, Prometheus y Loki compiten por los recursos reservados a PostgreSQL y **caen con el host que debían vigilar**. |
| G-10 | **La retención de CloudWatch es corta y explícita** | Nunca infinita (**D-11**, `Task/031`). El costo de observabilidad se contiene por diseño. |
| G-11 | **Ninguna cifra comercial de Grafana se documenta como permanente** | Si se registra, se marca *«verificar en `Task/041` / antes de contratar»*. |

### 10.3 Por qué el agente y no un *stack*

Un plano de observabilidad **alojado en la máquina que vigila** tiene dos fallos, y cada uno
basta para descartarlo en este proyecto:

1. **Compite por los recursos de PostgreSQL** —RAM, CPU, disco—, que es exactamente lo que
   no puede degradarse (**R-32**, **R-41**).
2. **Desaparece con el incidente.** Si el host cae, se pierde la telemetría del momento en
   que más falta hace.

Un **agente** que empuja hacia fuera no tiene ninguno de los dos.

### 10.4 Qué NO cambia

- **El entorno local no cambia.** Alloy y Grafana Cloud son **exclusivamente de
  producción**; en local siguen Docker, Portainer y `Task/017`.
- **El laboratorio AWS local no cambia.** Floci **no emula Grafana Cloud** y no debe
  intentarlo.
- **CloudWatch no desaparece.** Sigue siendo la observabilidad nativa de AWS, en modo
  mínimo.
- **La aplicación no cambia.** Emite logs JSON con correlation ID por `stdout`; quién los
  recoge es decisión de infraestructura.
- **No relaja** ninguna regla existente de este documento; añade las suyas.
