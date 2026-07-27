# Límites de seguridad

| Campo | Valor |
| --- | --- |
| **Estado** | Propuesta de `Task/002-Definir-MVP-y-Arquitectura` — Lista para validación |
| **Fecha** | 2026-07-26 |

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
