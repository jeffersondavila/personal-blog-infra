# Límites de seguridad

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/002-Definir-MVP-y-Arquitectura` (2026-07-26) |
| **Fecha** | 2026-07-26 · §8 añadida y **aprobada** el 2026-08-15 (`Task/005.2`) |

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
| C-10 GitHub Actions | `terraform destroy` | Ninguna automatización destruye infraestructura (`Task/039`). |
| C-11 Lambda | Recursos fuera de su rol | Permisos mínimos, acotados a lo que necesita. |
| Cualquiera | Secretos en Git | Ningún secreto se versiona, en ningún repositorio. |
| Internet o LAN | C-12 Emulador AWS local | **Nunca expuesto.** Ni el puerto 4566 ni sus rangos auxiliares (§8). |
| Credenciales AWS **reales** | C-12 Emulador AWS local | Prohibido: expone una credencial real a un servicio local que no la necesita ni la protege. |
| Secretos **reales** | C-12 SSM emulado | El `SecureString` del emulador **no cifra**. Solo valores ficticios. |
| Herramienta apuntada al laboratorio | C-11 Servicios AWS reales | Prohibido por accidente: exige guardas *fail-closed* antes de `apply` y `destroy` (§8.2). |

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
vigente de que **ninguna automatización ejecute `terraform destroy`** (§3).

### 8.3 Qué NO cambia

- El emulador **no forma parte del producto** ni del camino de la petición en producción.
- **No se despliega en la nube**, en ninguna forma.
- **No sustituye** a Portainer, ni a MinIO, ni a PostgreSQL local.
- **No relaja** ninguna regla existente de este documento.
