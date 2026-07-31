# Reporte — TASK-004 Backups y Recuperación Local

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/004-Backups-y-Recuperacion-Local` |
| **Etapa** | [ETAPA 01 — Infraestructura Local](../stages/STAGE-01-local-infrastructure.md) |
| **Estado final** | **Aprobada** |
| **Fecha de ejecución** | 2026-07-31 |
| **Fecha de aprobación** | 2026-07-31 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Repositorios afectados** | `personal-blog-infra` (únicamente) |
| **Ficha completa** | [TASK-004](../tasks/TASK-004-local-backups-and-recovery.md) |
| **Runbook producido** | [local-backup-and-recovery.md](../runbooks/local-backup-and-recovery.md) |

---

## 1. Estado inicial encontrado

Verificado con Git y Docker antes de tocar nada.

### 1.1 Git

| Repositorio | Rama activa | Árbol | `main` | `dev` | Contenido |
| --- | --- | --- | --- | --- | --- |
| `personal-blog-infra` | `main` | Limpio | `966db01` | `708a71e` | **Idéntico** |
| `personal-blog-frontend` | `main` | Limpio | `144a401` | `8823cc3` | **Idéntico** |
| `personal-blog-backend` | `main` | Limpio | `76c09f5` | `0f94abb` | **Idéntico** |

- `git fetch --prune origin` ejecutado. Avance global **3 de 41**; ETAPA 01 al **50 %**;
  D-05 **Resuelta** con Traefik v3; `Task/004` **Pendiente**.
- `git rev-list --count dev..main` = **0**: no hizo falta normalización previa.

### 1.2 Confirmación del prune de `Task/003`

```
From https://github.com/jeffersondavila/personal-blog-infra
 - [deleted]         (none)     -> origin/Task/003-Crear-Infraestructura-Local
```

`git fetch --prune origin` **retiró la referencia local** de la rama remota que el usuario
eliminó desde GitHub. Tras el prune, las ramas remotas son exactamente `origin/main` y
`origin/dev`. La rama Task local ya no existía desde el cierre de `Task/003`.

### 1.3 Entorno Docker

Docker Desktop 29.1.3, Docker Compose v5.0.1, PowerShell 5.1 en Windows 11.
Los tres servicios en marcha (`postgres` y `minio` **healthy**) y los tres volúmenes
principales presentes.

---

## 2. Rama creada

```
Task/004-Backups-y-Recuperacion-Local
```

Creada **desde `dev`** (`708a71e`) en `personal-blog-infra`, **únicamente**. ROADMAP,
STAGE-01 y STATUS coinciden en que la tarea afecta solo a `infra`. **No se creó en
frontend ni en backend.**

---

## 3. Archivos creados y modificados

**9 creados · 7 modificados · 0 eliminados.** Todos en `personal-blog-infra`.

### Creados

```
scripts/backup/_BackupCommon.ps1                    funciones y guardas compartidas
scripts/backup/New-LocalBackup.ps1                  creacion del conjunto de respaldo
scripts/backup/Test-LocalBackup.ps1                 verificacion de integridad
scripts/backup/Restore-LocalBackupTest.ps1          restauracion aislada y verificacion
scripts/backup/Remove-RecoveryTestResources.ps1     limpieza de recursos temporales
scripts/backup/README.md                            referencia y garantias de seguridad
docs/runbooks/local-backup-and-recovery.md          runbook completo
docs/tasks/TASK-004-local-backups-and-recovery.md   ficha de la tarea
docs/task-reports/TASK-004-report.md                este reporte
```

### Modificados

```
.gitignore                                      local-backups/ y *.tar.gz excluidos
README.md                                       seccion de backup del entorno local
docs/runbooks/README.md                         indice con el nuevo runbook
docs/project-management/STATUS.md               Task/004 en curso; R-08 cerrado; R-11..R-13
docs/project-management/ROADMAP.md              estado de Task/004
docs/stages/STAGE-01-local-infrastructure.md    criterios de salida y riesgos
docs/task-reports/README.md                     indice de reportes
```

**Ningún backup real se versiona.** `local-backups/` está ignorado por Git.

---

## 4. Diseño del sistema de backup

| Servicio | Método | ¿Se detiene? | Por qué |
| --- | --- | --- | --- |
| PostgreSQL | `pg_dump --format=custom --compress=6` | **No** | Trabaja sobre una instantánea transaccional: la copia es coherente en caliente. |
| MinIO — contenido | `mc mirror` + `.zip` | **No** | `mc` lee objetos completos por la API de S3. |
| MinIO — metadatos y tags | `mc stat --json --recursive` y `mc tag list --json` | **No** | `mc mirror` **no los conserva**: se inventarían aparte y se reaplican al restaurar. |
| MinIO — buckets | `mc stat --json` y `mc anonymous get --json` | **No** | Registro informativo, con detección de lo que no se sabe restaurar. |
| Portainer | `tar.gz` del volumen vía contenedor auxiliar | **Sí, solo Portainer** | Escribe su base interna de forma continua; copiarla en caliente puede dar un archivo inconsistente. |

La parada de Portainer está dentro de un bloque `finally`: **se rearranca aunque la copia
falle**. PostgreSQL y MinIO **no se detienen en ningún momento**.

### Alcance en MinIO

| Elemento | ¿Se respalda? | ¿Se restaura? | ¿Se verifica? |
| --- | :---: | :---: | :---: |
| Contenido del objeto | Sí | Sí | SHA-256 del contenido |
| Metadatos (`Content-Type`, `Cache-Control`, `Content-Disposition`, `Content-Encoding`, `Content-Language`, `x-amz-meta-*`) | Sí | Sí, con `mc cp --attr` | Comparación exacta, en ambos sentidos |
| Tags del objeto | Sí | Sí, con `mc tag set` | Comparación exacta, en ambos sentidos |
| Configuración del bucket | Se **registra** | **No** | No |
| Historial de versiones | **No** | **No** | No |

**La restauración no usa `mc mirror`**: subiría el contenido sin metadatos. Cada objeto se
sube con `mc cp --attr` y después se reaplican los tags.

**El script no ignora lo que no sabe copiar.** Si algún bucket usa versionado, Object
Lock, replicación, ciclo de vida, política anónima o cifrado, **aborta** nombrando la
causa; con `-AllowPartial` genera el conjunto marcándolo como `PARCIAL`.

### Aislamiento de la prueba de restauración

Todo lleva el prefijo `personal-blog-recovery`: red propia, volúmenes propios,
contenedores con nombres distintos, **sin puertos publicados** salvo el de Portainer
(`127.0.0.1:9445`) para poder comprobar que responde. La instancia temporal de Portainer
**no monta el socket de Docker**.

### Guarda de seguridad

`Assert-SafeToRemove` exige **dos** condiciones antes de cada borrado: que el nombre **no**
pertenezca al entorno principal y que **sí** lleve el prefijo `personal-blog-recovery`. En
la limpieza se valida el inventario **entero** antes de borrar nada.

Los scripts **no ejecutan** `docker compose down -v`, `docker system prune` ni
`docker volume prune`.

---

## 5. Conjunto generado

Conjunto **`20260731-172039`**, en
`personal-blog-infra/local-backups/20260731-172039/` (ignorado por Git). **Es el único
conjunto conservado**: los anteriores eran pruebas incompletas, sin inventario de
metadatos, y se eliminaron.

| Archivo | Tamaño | SHA-256 |
| --- | ---: | --- |
| `postgres/postgres-20260731-172039.dump` | 3 119 B | `942f0ed1ba60c37860d349df0eab997e1c2fad804f7ce3f6056e611d3562f2c4` |
| `postgres/postgres-20260731-172039.toc.txt` | 841 B | `1e6b667f4d36851d764dccb123500c724b15886ed647202e1fcb537d9de38981` |
| `minio/minio-20260731-172039.zip` | 3 723 B | `56f2968602282ace4d36e372fa2db6b1cf058f99972066062cd5224832fb3ede` |
| `minio/minio-inventory-20260731-172039.json` | 763 B | `f4148f5869f8634f36165879824e63cfbdce226cc03c1532d78aa6e1db342c0f` |
| `minio/minio-objects-20260731-172039.sha256` | 315 B | `b4a2776be09d27dd2f42ef85929b1464f8e9de872edb328adc246174e76ee0a2` |
| **`minio/minio-objects-metadata-20260731-172039.json`** | 3 258 B | `9e82f8f68fadcc2a35aed5a14c7f225f1333a0a4895fc9e52e2d6b3b9dbc22e7` |
| **`minio/minio-buckets-20260731-172039.json`** | 1 014 B | `c8c3b05106fe2c16baef24dab807c1ae05b93a67e399ad117e35944c0e05a37d` |
| `portainer/portainer-20260731-172039.tar.gz` | 2 813 B | `b1c07a5402c737ea4b7c52f6185f26e6e86df196d2721b4175001fe037a18683` |
| `checksums.sha256` | 869 B | *(es el índice)* |
| `manifest.json` | 6 417 B | *(excluido a propósito, ver abajo)* |

**Total de artefactos de datos: 8 archivos, 15 846 B.** Los dos inventarios nuevos —en
negrita— **están incluidos en `checksums.sha256`** y se verifican como el resto.

Contenido de MinIO en este conjunto: **3 objetos**, **2 con metadatos `x-amz-meta-*`**,
**1 con tags**, en **1 bucket**. `completeness: COMPLETO`.

El manifiesto registra: identificador y fecha UTC, proyecto, versiones de Docker y
Compose, imágenes efectivas, detalles por servicio, la lista de artefactos con tamaño y
checksum, el resultado del backup, el **grado de integridad** (`completeness`), el
**resultado de la prueba de restauración** con el desglose de contenido, metadatos y tags,
la limitación explícita sobre el historial de versiones y la advertencia de sensibilidad.
**No contiene ninguna contraseña ni token.**

`manifest.json` no figura en `checksums.sha256` **a propósito**: la prueba de restauración
escribe su resultado en él. Los ocho artefactos de datos sí están todos.

---

## 6. Resultados de cada restauración

Prueba ejecutada sobre el conjunto `20260731-161342`, en entorno temporal aislado.

### PostgreSQL — **CORRECTA**

- Instancia temporal `personal-blog-recovery-postgres`, imagen `postgres:17.10-alpine`,
  volumen propio, **sin puertos publicados**.
- `pg_restore --no-owner --no-privileges` ejecutado; **1 tabla** restaurada fuera de los
  esquemas del sistema.
- **Dato de verificación recuperado y coincidente:**
  `task-004-verificacion-20260731172038`.

### MinIO — **CORRECTA**

- Instancia temporal `personal-blog-recovery-minio`, volumen propio, **sin puertos
  publicados**.
- 1 bucket recreado y **3 objetos restaurados con `mc cp --attr` y `mc tag set`**, no con
  `mc mirror`.

**Contenido — SHA-256:**

| Objeto | Tamaño | Resultado |
| --- | ---: | --- |
| `task004-verificacion/datos/binario.b64` | 4 150 B | **SHA-256 coincide** |
| `task004-verificacion/metadata/ejemplo.json` | 60 B | **SHA-256 coincide** |
| `task004-verificacion/simple.txt` | 17 B | **SHA-256 coincide** |

**Metadatos y tags — comparación exacta:**

| Objeto | Comprobado | Resultado |
| --- | --- | --- |
| `metadata/ejemplo.json` | `Content-Type=application/json`, `Cache-Control=max-age=3600`, **2 metadatos** `x-amz-meta-*`, **2 tags** | **Todos coinciden** |
| `datos/binario.b64` | `Content-Type=application/octet-stream`, **1 metadato** `x-amz-meta-*` | **Todos coinciden** |
| `simple.txt` | `Content-Type=text/plain` | **Coincide** |

Sin objetos, metadatos ni tags ausentes o inesperados. La comparación se hace en ambos
sentidos: un metadato de más también habría hecho fallar la prueba.

### Portainer — **CORRECTA**

- Volumen temporal `personal-blog-recovery_portainer_data` restaurado desde el `tar.gz`.
- Instancia temporal en `127.0.0.1:9445`, **sin el socket de Docker**.
- Responde **HTTP 200** en `/api/status`, versión **2.39.5**.
- **InstanceID coincide** con el del entorno principal:
  `b40b2115-22d9-4bae-a5f7-99f9a6671ee4` — identificador **no sensible** que demuestra que
  el volumen se restauró con su contenido real. **No se comprobaron ni restablecieron
  contraseñas.**

Resultado global registrado en el manifiesto: `"overall": true`.

---

## 7. Recursos temporales creados y eliminados

| Recurso | Creado | Eliminado |
| --- | :---: | :---: |
| `personal-blog-recovery-net` (red) | ✔ | ✔ |
| `personal-blog-recovery-postgres` | ✔ | ✔ |
| `personal-blog-recovery-minio` | ✔ | ✔ |
| `personal-blog-recovery-portainer` | ✔ | ✔ |
| `personal-blog-recovery_postgres_data` | ✔ | ✔ |
| `personal-blog-recovery_minio_data` | ✔ | ✔ |
| `personal-blog-recovery_portainer_data` | ✔ | ✔ |
| `personal-blog-recovery-backup-helper` (auxiliar) | ✔ | ✔ |
| `personal-blog-recovery-restore-helper` (auxiliar) | ✔ | ✔ |

**Todos con el prefijo `personal-blog-recovery`.** La limpieza validó el inventario
completo antes de borrar y, al terminar, confirmó que los tres volúmenes principales
seguían existiendo.

### Datos de prueba creados en el entorno principal y retirados después

| Dato | Dónde | Estado final |
| --- | --- | --- |
| Tabla `backup_verification` con el marcador | PostgreSQL principal | **Eliminada** tras validar (`\dt` → *Did not find any relations*) |
| Bucket `task004-verificacion` con 3 objetos, metadatos y tags | MinIO principal | **Eliminado** tras validar (`mc ls src` → vacío) |

**El backup generado conserva ambos** y sigue disponible para tu revisión: es lo que
permite comprobar por ti mismo que la copia contiene datos reales.

---

## 8. Estado del entorno principal

| Comprobación | Resultado |
| --- | --- |
| `personal-blog-local_postgres_data` | **Presente** |
| `personal-blog-local_minio_data` | **Presente** |
| `personal-blog-local_portainer_data` | **Presente** |
| `postgres` | **Up, healthy** |
| `minio` | **Up, healthy** |
| `portainer` | **Up** (reiniciado tras su copia) |
| `docker compose down -v` | **Nunca ejecutado** |
| `docker volume rm` sobre volúmenes principales | **Nunca ejecutado** |
| `docker system prune` | **Nunca ejecutado** |
| Recursos Docker ajenos al proyecto | **Intactos** |
| `.env` local | **Intacto** y sigue ignorado por Git |

---

## 9. Validaciones ejecutadas — resultados reales

Las 28 comprobaciones se ejecutaron contra Docker Desktop real. **Ninguna se declara sin
haberse ejecutado.** Tabla completa en la [ficha](../tasks/TASK-004-local-backups-and-recovery.md),
sección 10. Resumen:

| Bloque | Resultado |
| --- | --- |
| Estado inicial y volúmenes (1–2) | Los tres servicios operativos, 3 de 3 volúmenes. |
| Sintaxis de los scripts (3) | **5 de 5 sin errores.** |
| Creación del backup (4–6) | Conjunto completo con manifiesto y **8 checksums**. |
| Verificación de integridad (7) | **INTEGRIDAD CORRECTA — 8 archivos**, 0 problemas. |
| Restauración de PostgreSQL (8–9) | **Correcta**, marcador coincidente. |
| Restauración de MinIO — contenido (10–11) | **Correcta**, 3 de 3 objetos con SHA-256 coincidente. |
| **Restauración de MinIO — metadatos y tags (11a–11c)** | **Correcta.** `Content-Type` y `Cache-Control` exactos; **3 metadatos** `x-amz-meta-*` y **2 tags** coincidentes, sin ausentes ni inesperados. |
| Restauración de Portainer (12–13) | **Correcta**, HTTP 200 e InstanceID coincidente. |
| Limpieza y entorno principal (14–18) | Solo recursos temporales eliminados; principal intacto y operativo. |
| Git y secretos (19–21, 24) | `local-backups/` ignorado por `.gitignore:48`; 0 secretos reales; sin errores de espacios. |
| Guarda de seguridad (22) | **Probada explícitamente** — ver abajo. |
| Enlaces y alcance (23, 25–28) | Enlaces verificados sin roturas; backend y frontend intactos; 0 recursos cloud; 0 Terraform; `Task/005` no iniciada. |
| **Inventarios y detección (29–35)** | Inventarios presentes y **en `checksums.sha256`**; **detección de versionado aborta**; `-AllowPartial` marca el conjunto como `PARCIAL`; estructuras JSON de `mc` determinadas empíricamente; datos de prueba eliminados de la fuente; conjuntos incompletos descartados. |

### Prueba explícita de la guarda de seguridad

Se invocó `Assert-SafeToRemove` con nombres reales:

| Nombre | Resultado |
| --- | --- |
| `personal-blog-local_postgres_data` | **BLOQUEADO** |
| `personal-blog-local-minio` | **BLOQUEADO** |
| `personal-blog-local-portainer` | **BLOQUEADO** |
| `personal-blog-local` (prefijo) | **BLOQUEADO** |
| `otro-proyecto-db` | **BLOQUEADO** |
| `farm-tech-infra_farm_db_data` (proyecto ajeno) | **BLOQUEADO** |
| `personal-blog-recovery-postgres` | Permitido |
| `personal-blog-recovery_minio_data` | Permitido |
| `personal-blog-recovery-net` | Permitido |

---

## 10. Pasos exactos para validar

```powershell
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# a) El conjunto existe y esta integro
Get-ChildItem .\local-backups -Recurse -File | Select-Object FullName, Length
cd scripts\backup
.\Test-LocalBackup.ps1

# b) Los backups NO estan versionados (no debe aparecer local-backups)
cd ..\..
git status --porcelain
git check-ignore -v local-backups

# c) Crear un backup nuevo y verificarlo
cd scripts\backup
.\New-LocalBackup.ps1
.\Test-LocalBackup.ps1

# d) Probar la restauracion completa en aislamiento
.\Restore-LocalBackupTest.ps1

# e) Comprobar que la guarda protege el entorno principal
.\Remove-RecoveryTestResources.ps1 -WhatIf

# f) El entorno principal sigue intacto
docker compose ps
docker volume ls --filter name=personal-blog-local

# g) Ayuda de cada script
Get-Help .\New-LocalBackup.ps1 -Full
```

**Qué revisar con atención:** si el contenido del conjunto te parece suficiente, si la
política de retención del runbook §11 te encaja, y si aceptas que el backup sea **manual**
(R-11) y **sin cifrar** (R-12), que son las dos limitaciones conscientes de esta tarea.

---

## 11. Riesgos y limitaciones

**R-08 queda cerrado**: existe copia externa a los volúmenes, con integridad verificada y
restauración demostrada para los tres servicios.

Riesgos nuevos:

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-11 | El backup es **manual**: si nadie lo ejecuta, se pierde todo lo hecho desde la última copia. | Medio | Política de retención que exige backup antes de toda operación destructiva. La automatización queda fuera del alcance declarado. |
| R-12 | Los artefactos son sensibles —incluyen hashes de autenticación de Portainer— y se guardan **sin cifrar**. | Medio | Ignorados por Git y documentados como sensibles en tres lugares. Cifrado a revisar en `Task/018`. |
| R-13 | La copia de Portainer exige detenerlo: una interrupción anómala podría dejarlo parado. | Bajo | El arranque está en un bloque `finally`. Si aun así quedara parado, `docker start` lo resuelve. |

**Limitaciones conscientes:** sin automatización programada, sin copia fuera del equipo,
sin cifrado, sin rotación automática, sin recuperación a un punto en el tiempo, y la
restauración sobre el entorno principal es **manual y documentada**, no automatizada.

En MinIO, además: **el historial de versiones queda fuera del alcance** —solo se respalda
la versión actual de cada objeto— y **la configuración de los buckets se registra pero no
se reaplica**. Ninguna de las dos se pasa por alto: el script las detecta y aborta salvo
que se le pase `-AllowPartial`, en cuyo caso marca el conjunto como `PARCIAL`. Tampoco se
admiten valores de metadato que contengan `;`, porque romperían el formato de
`mc cp --attr`: el backup aborta antes que generar algo que no se sabe restaurar.

---

## 12. Problemas encontrados

Siete, todos resueltos. Detalle en la [ficha](../tasks/TASK-004-local-backups-and-recovery.md),
sección 12. Los tres que más importan:

1. **Los scripts no se analizaban.** En UTF-8 **sin BOM**, PowerShell 5.1 los lee como
   ANSI y el guion largo `—` genera un byte que cierra cadenas antes de tiempo. Todos los
   `.ps1` pasan a **UTF-8 con BOM** y solo ASCII.
2. **La imagen de MinIO no incluye `tar` ni `find`.** El empaquetado y el cálculo de
   hashes se trasladan al host. El fallo de `find` era el más peligroso: generaba un
   archivo de hashes **vacío sin fallar**, lo que habría producido un backup que aparenta
   estar verificado. Se añadió una comprobación de coherencia que **aborta el backup** si
   el inventario y los objetos copiados no cuadran.
3. **La comparación por ETag daba un falso negativo.** Los objetos originales, subidos con
   `mc pipe` (multipart), tenían ETag `7f849e30...-1`; los mismos restaurados con
   `mc mirror` (PUT simple), `2f9a86bf...`. Se comprobó con `sha256sum` que el contenido
   era idéntico. La verificación pasa a comparar **SHA-256 del contenido**.

---

## 12.b Correcciones aplicadas tras la revisión del usuario

Ronda del 2026-07-31, sobre la misma rama y **sin ampliar el alcance declarado**. La tarea
permanece `Lista para validación`. No hubo commit, merge, push ni pull request.

### C-1 — Afirmación incorrecta sobre los metadatos de MinIO

**Lo que declaraba la ficha:** *«backup de los objetos y metadatos de MinIO con `mc`»*,
marcado como cumplido.

**Por qué era falso:** la implementación usaba `mc mirror --preserve` → sistema de
archivos → ZIP, y restauraba con `mc mirror`. Ese camino conserva rutas y contenido pero
**no los metadatos S3 ni los tags**: `--preserve` preserva atributos del **sistema de
archivos** (permisos, fechas), no `Content-Type`, `Cache-Control` ni los `x-amz-meta-*`.
La validación no lo detectaba porque los objetos de prueba **no tenían metadatos
personalizados ni tags**: comparar solo bytes no verificaba el criterio declarado.

**Qué se hizo:**

| Añadido | Detalle |
| --- | --- |
| `minio-objects-metadata-<id>.json` | Por objeto: bucket, clave, tamaño, SHA-256, ETag, `lastModified`, encabezados restaurables, metadatos `x-amz-meta-*` y tags. |
| `minio-buckets-<id>.json` | Por bucket: versionado, Object Lock, replicación, política anónima, ciclo de vida, cifrado, ubicación y características no soportadas. |
| Restauración con metadatos | Ya no se usa `mc mirror`: cada objeto se sube con `mc cp --attr` y los tags se reaplican con `mc tag set`. |
| Comparación exacta | Encabezados, metadatos y tags se comparan **en ambos sentidos**. |
| Detección de lo no soportado | El backup **aborta** ante versionado, Object Lock, replicación, ciclo de vida, política anónima o cifrado, salvo `-AllowPartial`. |
| Inventarios en `checksums.sha256` | Los dos archivos nuevos entran en la verificación de integridad. |

**Estructuras JSON determinadas empíricamente contra la versión instalada de `mc`**, no
supuestas:

```
mc stat --json <objeto>   -> { "metadata": { "Content-Type": ..., "Cache-Control": ...,
                                             "X-Amz-Meta-Task": ..., "X-Amz-Tagging-Count": ... } }
mc tag list --json <obj>  -> { "tagset": { "entorno": "local", "tarea": "task-004" } }
mc stat --json <bucket>   -> { "Versioning": {...}, "ObjectLock": {...}, "Replication": {...},
                               "Policy": {...}, "Encryption": {}, "ilm": {}, "location": ... }
mc anonymous get --json   -> { "permission": "private" }
```

### C-2 — Nueva prueba con metadatos reales

Objetos de validación creados en el bucket temporal:

| Objeto | Contenido | Metadatos | Tags |
| --- | --- | --- | --- |
| `metadata/ejemplo.json` (ruta anidada) | JSON | `Content-Type: application/json`, `Cache-Control: max-age=3600`, **2** `x-amz-meta-*` | **2** |
| `datos/binario.b64` (ruta anidada) | Binario en base64 | `Content-Type: application/octet-stream`, **1** `x-amz-meta-*` | — |
| `simple.txt` | Texto | `Content-Type: text/plain` | — |

Ciclo completo re-ejecutado: **los 3 objetos recuperaron contenido, `Content-Type`,
`Cache-Control`, metadatos y tags de forma exacta**.

### C-3 — Prueba de la detección de configuraciones no soportadas

Se activó el versionado en el bucket de prueba (`mc version enable`) y se relanzó el
backup:

| Modo | Resultado real |
| --- | --- |
| Sin `-AllowPartial` | **ABORTÓ**: `versionado 'Enabled': solo se respalda la version actual de cada objeto` y `El conjunto no se puede considerar completo`. **No generó el conjunto.** |
| Con `-AllowPartial` | Generó el conjunto marcado como `completeness: PARCIAL`, `backupResult.minio: PARCIAL` y `unsupportedFeaturesFound` poblado. |

**Ninguna configuración se ignora en silencio.** Los conjuntos de esta prueba se generaron
**fuera de `local-backups/`** y se eliminaron.

### C-4 — Documentación corregida

Se eliminó toda afirmación de que `mc mirror --preserve` conserva metadatos, y se
distingue explícitamente entre **contenido**, **metadatos**, **tags**, **configuración del
bucket** e **historial de versiones** en `scripts/backup/README.md`,
`docs/runbooks/local-backup-and-recovery.md`, la ficha, este reporte, `STATUS.md` y
`STAGE-01`. El runbook incluye ahora el procedimiento manual de recuperación **con**
metadatos y tags, que antes usaba `mc mirror` y habría perdido ambos.

### C-5 — Problema técnico encontrado durante la corrección

Con `Set-StrictMode`, leer una propiedad ausente aborta el script, y `mc` **omite campos
según el caso**: `tagset` no aparece cuando el objeto no tiene tags. Se añadieron
`Test-HasProperty` y `Get-PropertyOrDefault`, y todo acceso a campos opcionales de `mc`
pasa por ellas.

### C-6 — Conjunto conservado

Se conserva **únicamente `20260731-172039`**, el conjunto final correcto con 8 artefactos
e integridad verificada. Los anteriores eran pruebas incompletas —sin inventario de
metadatos— y se eliminaron para que no se confundan con el válido.

---

## 13. Estado Git final

| Repositorio | Rama activa | Estado del árbol |
| --- | --- | --- |
| `personal-blog-infra` | `Task/004-Backups-y-Recuperacion-Local` | 7 modificados + 4 entradas sin seguimiento (**9 archivos nuevos**), **sin confirmar** |
| `personal-blog-frontend` | `main` | **Limpio** |
| `personal-blog-backend` | `main` | **Limpio** |

Salida real de `git status --porcelain -b`:

```
## Task/004-Backups-y-Recuperacion-Local
 M .gitignore
 M README.md
 M docs/project-management/ROADMAP.md
 M docs/project-management/STATUS.md
 M docs/runbooks/README.md
 M docs/stages/STAGE-01-local-infrastructure.md
 M docs/task-reports/README.md
?? docs/runbooks/local-backup-and-recovery.md
?? docs/task-reports/TASK-004-report.md
?? docs/tasks/TASK-004-local-backups-and-recovery.md
?? scripts/
```

> **4 entradas** sin seguimiento para **9 archivos nuevos**: Git agrupa `scripts/` como
> una sola entrada de directorio, y contiene los 6 archivos de `scripts/backup/`.

`local-backups/` **no aparece** en `git status`: está ignorado por
`.gitignore:48:local-backups/`. El conjunto `20260731-161342` existe en disco y sigue
disponible para tu revisión.

---

## 14. Confirmación de límites respetados **durante la ejecución** (antes de la aprobación)

- **No se hizo ningún commit.** Los cambios quedan sin confirmar.
- **No se hizo merge**, ni hacia `dev` ni hacia `main`.
- **No se hizo push** de ninguna rama.
- **No se creó ningún pull request.**
- **No se modificó `main`.**
- **No se eliminó la rama Task.**
- **No se marcó ninguna tarea como `Aprobada`.** El runbook sigue como `Propuesta`.
- **No se creó ningún ADR.**
- **No se creó ningún recurso cloud** ni cuenta en ningún proveedor.
- **No se creó ningún archivo Terraform.**
- **No se versionó ningún backup real.**
- **No se expuso ni registró ningún secreto**: los scripts no imprimen credenciales y el
  manifiesto no las contiene.
- **No se ejecutó `docker compose down -v`**, ni `docker volume rm` sobre volúmenes
  principales, ni `docker system prune`.
- **No se ejecutó** `git clean -fd`, `git reset --hard`, `push --force` ni `branch -D`.
- **No se modificó `personal-blog-backend` ni `personal-blog-frontend`.**
- **No se tocó ningún recurso Docker ajeno al proyecto.**
- **`Task/005-Fundacion-Backend-FastAPI` NO fue iniciada.**
- El avance global permanece en **3 de 41 (7 %)** y la **ETAPA 01 sigue en 1 de 2 (50 %)**,
  sin marcarse como completada.

---

## 15. Próxima tarea prevista

**`Task/005-Fundacion-Backend-FastAPI`** — base profesional de FastAPI, configuración,
logging, PostgreSQL, Alembic, pruebas y Dockerfile. Primera tarea de la **ETAPA 02** y
primera del repositorio `personal-blog-backend`.

**No ha sido iniciada** y no puede iniciarse hasta que `Task/004` sea aprobada y su cierre
esté completo.

---

## 16. Cierre aprobado (2026-07-31)

El usuario autorizó el cierre con `approved: Task/004-Backups-y-Recuperacion-Local`.
A partir de ese momento se ejecutó el flujo de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §3.

### 16.1 Promociones documentales

| Elemento | De | A |
| --- | --- | --- |
| `Task/004` | Lista para validación | **Aprobada** |
| Runbook `local-backup-and-recovery.md` | Propuesta | **Vigente** |
| **R-08** | Abierto | **Cerrado** |
| Avance global | 3 de 41 (7 %) | **4 de 41 (10 %)** |
| **ETAPA 01** | 1 de 2 (50 %), en curso | **2 de 2 (100 %), COMPLETADA** |
| ETAPA 02 | Pendiente | **Siguiente** |

**No se creó ningún ADR.** Las decisiones de esta tarea son de implementación local y
reversibles. ADR-001 a ADR-005 siguen en **Aceptada**, sin cambios. Las decisiones
diferidas siguen siendo **12**: `Task/004` no resolvió ninguna.

### 16.2 Operaciones de Git ejecutadas

| # | Paso | Resultado |
| --- | --- | --- |
| 1 | Commits en la rama Task | **2 commits** — ver sección 16.3 |
| 2 | `git switch dev` + `pull --ff-only origin dev` | `dev` actualizada, sin cambios remotos nuevos |
| 3 | `git merge --no-ff Task/004-Backups-y-Recuperacion-Local` | Integrada en `dev` |
| 4 | `git push origin dev` | Publicada |
| 5 | `git push -u origin Task/004-Backups-y-Recuperacion-Local` | Rama Task publicada |
| 6 | `gh pr create --base main --head Task/004-Backups-y-Recuperacion-Local` | **PR abierto** |
| 7 | Merge del PR | **NO ejecutado** — corresponde exclusivamente al usuario |
| 8 | `git switch main` + `fetch --prune` + `pull --ff-only` | `main` actualizada, **sin modificar** |
| 9 | `git branch -d Task/004-Backups-y-Recuperacion-Local` | Rama local eliminada (**nunca `-D`**) |
| 10 | Rama Task remota | **Conservada** mientras exista el PR |

### 16.3 Pull request

| Campo | Valor |
| --- | --- |
| **Dirección** | **`Task/004-Backups-y-Recuperacion-Local` → `main`** |
| **Base** | `main` |
| **Head** | `Task/004-Backups-y-Recuperacion-Local` |
| **Estado** | **Abierto, sin fusionar** |

Se respetó la regla crítica del proyecto: **no se creó ningún PR `dev → main`**.

### 16.4 Qué corresponde ahora al usuario

1. Revisar el pull request.
2. Aceptarlo o rechazarlo. **Solo el usuario fusiona hacia `main`.**
3. Decidir si elimina la rama Task remota desde GitHub.

Cuando confirmes la fusión, se ejecutará la normalización `main → dev` descrita en
`PROJECT_INSTRUCTIONS.md` §10. **`Task/005` no puede iniciarse antes de completarla.**

### 16.5 El entorno local tras el cierre

El conjunto de respaldo **`20260731-172039`** sigue en `local-backups/`, ignorado por Git,
disponible para tu revisión. Los tres servicios del entorno principal siguen operativos
con sus volúmenes intactos.
