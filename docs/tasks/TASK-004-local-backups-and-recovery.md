# TASK-004 — Backups y Recuperación Local

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/004-Backups-y-Recuperacion-Local` |
| **Nombre** | Backups y Recuperación Local |
| **Etapa** | [ETAPA 01 — Infraestructura Local](../stages/STAGE-01-local-infrastructure.md) |
| **Estado** | **Aprobada** |
| **Repositorios involucrados** | `personal-blog-infra` (únicamente) |
| **Dependencias** | `Task/003-Crear-Infraestructura-Local` — **Aprobada** ✔ (2026-07-29) |
| **Rama** | `Task/004-Backups-y-Recuperacion-Local`, creada desde `dev` en `personal-blog-infra` |
| **Fecha de inicio** | 2026-07-31 |
| **Fecha de aprobación** | 2026-07-31 |
| **Aprobado por** | jeffersondavila |
| **Última actualización** | 2026-07-31 |

---

## 1. Objetivo

Disponer de un procedimiento local, reproducible y **verificado** para respaldar
PostgreSQL, MinIO y Portainer a archivos **externos a los volúmenes de Docker**, comprobar
su integridad y **demostrar que esas copias se pueden restaurar**.

No basta con que los volúmenes persistan: `Task/003` ya lo demostró. `Task/004` debe
demostrar que existe una copia **fuera** de los volúmenes y que esa copia se restaura
correctamente.

## 2. Contexto

`Task/003` dejó el entorno local en marcha, pero con un riesgo abierto de impacto **alto**:

> **R-08** — El entorno local no tiene copia de seguridad: `docker compose down -v`
> destruye la base de datos y los objetos de MinIO sin recuperación posible.

Esta tarea cierra ese riesgo. Es también la última de la ETAPA 01: al aprobarse,
la etapa quedará completa y podrá empezar la ETAPA 02 con el backend y el frontend.

Sin respaldo verificado, todo lo que se construya a partir de `Task/005` estaría sobre un
entorno que no se puede recuperar.

## 3. Dentro del alcance

- [x] Crear la rama `Task/004` desde `dev`, **solo** en `personal-blog-infra`.
- [x] Backup de PostgreSQL con `pg_dump` en formato custom, **sin detener el servicio**.
- [x] Backup del **contenido** de los objetos de MinIO, **sin detener el servicio**.
- [x] Backup de los **metadatos y tags** de cada objeto, inventariados con
      `mc stat --json` y `mc tag list --json`, y **reaplicados al restaurar**.
- [x] Registro de la **configuración de cada bucket**, con detección de las
      características que el procedimiento no sabe restaurar.
- [x] Backup del volumen de datos y configuración de Portainer.
- [x] Conjunto de respaldo identificable por fecha y hora UTC.
- [x] Manifiesto por ejecución con versiones, artefactos, tamaños y resultados.
- [x] Checksums SHA-256 de todos los artefactos.
- [x] Verificación de integridad sin restaurar.
- [x] Restauración de los tres componentes en recursos temporales **aislados**.
- [x] Validación de que los datos restaurados son correctos.
- [x] Limpieza que elimina **únicamente** recursos temporales.
- [x] Guardas que rechazan cualquier operación sobre el entorno principal.
- [x] Directorio `local-backups/` ignorado por Git.
- [x] Runbook de recuperación y reconstrucción del entorno.
- [x] Política manual mínima de retención.
- [x] Actualizar la documentación de gestión afectada.

## 4. Fuera del alcance

| Elemento | Motivo o tarea |
| --- | --- |
| Automatización programada del backup | Requeriría una tarea del sistema. Fuera del alcance declarado. |
| Subida de copias a la nube o a otro equipo | Etapas 09 y 10; para producción, decisión D-10. |
| Cifrado de los artefactos | No contemplado. Se protegen manteniéndolos locales y sin versionar. |
| Restauración en caliente sobre el entorno principal | Sólo se documenta el procedimiento manual; la prueba automatizada usa recursos temporales. |
| Recuperación a un punto en el tiempo (WAL archiving) | Desproporcionado para un entorno local. |
| Backups de backend y frontend | No existen todavía (`Task/005`, `Task/006`). |
| Backup del esquema de la aplicación | No hay esquema hasta `Task/008`; el procedimiento ya lo cubrirá. |
| Política de retención empresarial | Fuera del alcance: se define una política **manual y mínima**. |
| Estrategia de backups en la nube | `Task/029`, decisión D-10. |

**Prohibiciones explícitas de esta tarea, todas respetadas:**

- **No crear ningún recurso cloud** ni cuenta en ningún proveedor.
- **No versionar ninguna copia de seguridad real.**
- **No exponer ni registrar secretos** en scripts, manifiestos, documentación o consola.
- **No ejecutar operaciones destructivas** sobre el entorno principal.

## 5. Entregables

| Entregable | Ruta | Acción |
| --- | --- | --- |
| Funciones compartidas | `scripts/backup/_BackupCommon.ps1` | Creado |
| Creación de backups | `scripts/backup/New-LocalBackup.ps1` | Creado |
| Verificación de integridad | `scripts/backup/Test-LocalBackup.ps1` | Creado |
| Prueba de restauración aislada | `scripts/backup/Restore-LocalBackupTest.ps1` | Creado |
| Limpieza de recursos temporales | `scripts/backup/Remove-RecoveryTestResources.ps1` | Creado |
| Referencia de los scripts | `scripts/backup/README.md` | Creado |
| Runbook de backup y recuperación | `docs/runbooks/local-backup-and-recovery.md` | Creado |
| Ficha de esta tarea | `docs/tasks/TASK-004-local-backups-and-recovery.md` | Creado |
| Reporte de esta tarea | `docs/task-reports/TASK-004-report.md` | Creado |
| Exclusión de los backups | `.gitignore` | Modificado |
| Índice de runbooks | `docs/runbooks/README.md` | Modificado |
| Estado del proyecto | `docs/project-management/STATUS.md` | Modificado |
| Roadmap | `docs/project-management/ROADMAP.md` | Modificado |
| Ficha de la Etapa 01 | `docs/stages/STAGE-01-local-infrastructure.md` | Modificado |
| Índice de reportes | `docs/task-reports/README.md` | Modificado |
| README del repositorio | `README.md` | Modificado |

**9 creados · 7 modificados · 0 eliminados.**

## 6. Diseño del sistema de respaldo

### 6.1 Método por servicio

| Servicio | Método | ¿Se detiene? | Justificación |
| --- | --- | --- | --- |
| PostgreSQL | `pg_dump --format=custom --compress=6` | **No** | `pg_dump` trabaja sobre una instantánea transaccional: la copia es coherente en caliente. |
| MinIO — contenido | `mc mirror` + `.zip` | **No** | `mc` lee objetos completos por la API de S3: cada objeto es coherente. |
| MinIO — metadatos y tags | `mc stat --json --recursive` y `mc tag list --json` | **No** | Se inventarían aparte porque `mc mirror` **no los conserva** — ver §6.1. |
| MinIO — buckets | `mc stat --json` y `mc anonymous get --json` por bucket | **No** | Registro informativo, con detección de lo que no se sabe restaurar. |
| Portainer | `tar.gz` del volumen mediante contenedor auxiliar | **Sí, solo Portainer** | Escribe su base interna de forma continua; copiarla en caliente puede producir un archivo inconsistente. |

La parada de Portainer dura lo mínimo y está dentro de un bloque `finally`: **el
contenedor se vuelve a arrancar incluso si la copia falla**. PostgreSQL y MinIO **no se
detienen en ningún momento**.

### 6.1 Alcance en MinIO: contenido, metadatos, tags y configuración

`mc mirror` hacia un **sistema de archivos** copia el contenido de los objetos, no sus
metadatos S3. La opción `--preserve` preserva atributos del sistema de archivos —permisos
y fechas—, **no** `Content-Type`, ni los `x-amz-meta-*`, ni los tags. Respaldar solo con
`mirror` y afirmar que conserva metadatos sería falso.

Por eso el procedimiento separa cuatro cosas:

| Elemento | ¿Se respalda? | ¿Se restaura? | ¿Se verifica? |
| --- | :---: | :---: | :---: |
| **Contenido del objeto** | Sí | Sí | SHA-256 del contenido |
| **Metadatos del objeto** (`Content-Type`, `Cache-Control`, `Content-Disposition`, `Content-Encoding`, `Content-Language`, `x-amz-meta-*`) | Sí | Sí, con `mc cp --attr` | Comparación exacta, en ambos sentidos |
| **Tags del objeto** | Sí | Sí, con `mc tag set` | Comparación exacta, en ambos sentidos |
| **Configuración del bucket** (versionado, Object Lock, replicación, ciclo de vida, política anónima, cifrado) | Se **registra** | **No** | No |
| **Historial de versiones** | **No** | **No** | No |

**Alcance temporal: la versión ACTUAL de cada objeto.**

**No se restaura con `mc mirror`:** cada objeto se sube individualmente con
`mc cp --attr`, que aplica los metadatos en la propia subida, y después se reaplican los
tags. `mirror` habría dejado los objetos sin metadatos.

**Metadatos derivados, excluidos de la comparación:** `ETag` y `lastModified` los recalcula
MinIO; `X-Amz-Tagging-Count` se deriva del número de tags, que sí se verifica aparte.

### 6.2 Detección de configuraciones no soportadas

Antes de copiar nada, el script inspecciona cada bucket y **aborta** si encuentra
versionado (`Enabled` o `Suspended`), Object Lock, replicación, reglas de ciclo de vida,
política anónima distinta de `private` o cifrado en reposo.

Un backup que ignora en silencio lo que no sabe copiar da una confianza que no
corresponde. Con `-AllowPartial` el conjunto se genera igualmente, pero queda marcado como
**`PARCIAL`** en `manifest.json` y en `minio-buckets-<id>.json`, con la lista exacta de lo
que no cubre.

**Verificado en ejecución real** — validaciones 30 y 31 de la sección 10.

### 6.2 Estructura de un conjunto

```
local-backups/YYYYMMDD-HHMMSS/
├── manifest.json
├── checksums.sha256
├── postgres/
│   ├── postgres-<id>.dump                 volcado custom
│   └── postgres-<id>.toc.txt              índice legible (pg_restore --list)
├── minio/
│   ├── minio-<id>.zip                     CONTENIDO de los objetos
│   ├── minio-inventory-<id>.json          inventario con tamaños y ETags
│   ├── minio-objects-<id>.sha256          SHA-256 del contenido
│   ├── minio-objects-metadata-<id>.json   METADATOS y TAGS por objeto
│   └── minio-buckets-<id>.json            configuración de cada bucket
└── portainer/
    └── portainer-<id>.tar.gz              volumen completo
```

Los dos inventarios nuevos **están incluidos en `checksums.sha256`**.

`manifest.json` **no** figura en `checksums.sha256`, porque la prueba de restauración
escribe su resultado en él. Todos los artefactos de datos sí están.

### 6.3 Aislamiento de la prueba de restauración

| Recurso temporal | Aislamiento |
| --- | --- |
| `personal-blog-recovery-net` | Red propia. |
| `personal-blog-recovery-postgres` | Volumen propio, **sin puertos publicados**. |
| `personal-blog-recovery-minio` | Volumen propio, **sin puertos publicados**. |
| `personal-blog-recovery-portainer` | Volumen propio, `127.0.0.1:9445`, **sin el socket de Docker**. |

Las credenciales del entorno temporal se generan al vuelo, no se imprimen y no se guardan.
La instancia temporal de Portainer **no monta el socket de Docker**: no lo necesita para
arrancar, y así no se le concede acceso privilegiado al host.

### 6.4 Guardas de seguridad

`Assert-SafeToRemove` se invoca antes de **cualquier** eliminación y exige **dos**
condiciones:

1. Que el nombre **no** pertenezca al entorno principal (`personal-blog-local*`).
2. Que el nombre **sí** lleve el prefijo `personal-blog-recovery`.

Si alguna falla, la operación se aborta por completo. En la limpieza se valida el
inventario **entero** antes de borrar nada: si un solo recurso no pasa, no se elimina
ninguno.

Los scripts **no ejecutan** `docker compose down -v`, `docker system prune` ni
`docker volume prune`. Tras cada operación comprueban que los tres volúmenes principales
siguen existiendo.

## 7. Criterios de aceptación

| # | Criterio | Estado |
| --- | --- | --- |
| 1 | Los scripts tienen sintaxis válida. | Cumplido — validación 3 |
| 2 | Se crea un conjunto de respaldo completo. | Cumplido — validación 4 |
| 3 | El conjunto incluye manifiesto. | Cumplido — validación 5 |
| 4 | El conjunto incluye checksums SHA-256. | Cumplido — validación 6 |
| 5 | La verificación de checksums pasa. | Cumplido — validación 7 |
| 6 | El backup de PostgreSQL se crea sin detener el servicio. | Cumplido — validación 4 |
| 7 | El backup de MinIO se crea sin detener el servicio. | Cumplido — validación 4 |
| 8 | Portainer se detiene lo mínimo y vuelve a arrancar. | Cumplido — validación 4 |
| 9 | PostgreSQL se restaura en un entorno temporal aislado. | Cumplido — validación 8 |
| 10 | El dato de prueba de PostgreSQL restaurado coincide. | Cumplido — validación 9 |
| 11 | MinIO se restaura en un entorno temporal aislado. | Cumplido — validación 10 |
| 12 | Los checksums de los objetos restaurados coinciden. | Cumplido — validación 11 |
| 12a | El conjunto incluye el inventario de metadatos y está en `checksums.sha256`. | Cumplido — validaciones 6 y 29 |
| 12b | El `Content-Type` restaurado coincide exactamente. | Cumplido — validación 11a |
| 12c | Los metadatos `x-amz-meta-*` restaurados coinciden exactamente. | Cumplido — validación 11b |
| 12d | Los tags restaurados coinciden exactamente. | Cumplido — validación 11c |
| 12e | Se detecta el estado de versionado de los buckets. | Cumplido — validaciones 29 y 30 |
| 12f | Ninguna configuración de bucket se ignora en silencio. | Cumplido — validaciones 30 y 31 |
| 13 | Portainer se restaura en un volumen temporal. | Cumplido — validación 12 |
| 14 | El Portainer temporal arranca y responde. | Cumplido — validación 13 |
| 15 | Solo se eliminan recursos temporales. | Cumplido — validaciones 14 y 22 |
| 16 | Los volúmenes principales permanecen intactos. | Cumplido — validación 15 |
| 17 | Los servicios principales siguen operativos. | Cumplido — validaciones 16 a 18 |
| 18 | `local-backups/` está ignorado por Git. | Cumplido — validación 19 |
| 19 | Ningún backup real aparece en `git status`. | Cumplido — validación 20 |
| 20 | No hay secretos en los archivos versionados. | Cumplido — validación 21 |
| 21 | Los enlaces relativos resuelven. | Cumplido — validación 23 |
| 22 | Backend y frontend intactos. | Cumplido — validación 25 |
| 23 | No se creó ningún recurso cloud ni archivo Terraform. | Cumplido — validaciones 26 y 27 |
| 24 | La tarea queda `Lista para validación`, nunca `Aprobada` por decisión propia. | Cumplido — aprobada después por el usuario el 2026-07-31 |
| 25 | No se inició `Task/005`. | Cumplido — validación 28 |

## 8. Plan de validación

Cada criterio se comprueba ejecutando el ciclo completo contra Docker Desktop real:
crear datos de prueba identificables, respaldar, verificar, restaurar en aislamiento,
comparar y limpiar. Resultados reales en la sección 10.

## 9. Comandos de validación

```powershell
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra\scripts\backup

# Sintaxis
Get-ChildItem *.ps1 | ForEach-Object {
    $e = $null
    [System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$null, [ref]$e) | Out-Null
    "$($_.Name): $($e.Count) errores"
}

# Ciclo completo
.\New-LocalBackup.ps1
.\Test-LocalBackup.ps1
.\Restore-LocalBackupTest.ps1 -ExpectedPostgresMarker '<marcador>'
.\Remove-RecoveryTestResources.ps1 -WhatIf
.\Remove-RecoveryTestResources.ps1 -Force

# Entorno principal intacto
docker compose ps
docker volume ls --filter name=personal-blog-local

# Git
git status --porcelain -b
git check-ignore -v local-backups
```

## 10. Resultado de las validaciones

Ejecutadas el 2026-07-31 sobre Docker Desktop 29.1.3, Docker Compose v5.0.1 y
PowerShell 5.1 en Windows 11. **Ninguna validación se declara sin haberse ejecutado.**

| # | Validación | Resultado real |
| --- | --- | --- |
| 1 | Estado inicial de los servicios | `postgres` y `minio` **healthy**, `portainer` up. |
| 2 | Volúmenes principales presentes | **3 de 3**. |
| 3 | Sintaxis de los scripts | **5 de 5 sin errores** con `[Parser]::ParseFile`. |
| 4 | Creación de un backup completo | **OK.** Conjunto `20260731-172039`, 8 archivos, **15.47 KB**. PostgreSQL y MinIO respaldados sin detenerse; Portainer detenido y reiniciado. |
| 5 | Manifiesto | `manifest.json` presente, con versiones, imágenes, artefactos, `completeness: COMPLETO` y resultados. |
| 6 | Checksums | `checksums.sha256` con **8 entradas**, incluidos los dos inventarios nuevos. |
| 7 | Verificación de integridad | **INTEGRIDAD CORRECTA — 8 archivos**, 0 problemas. |
| 8 | Restauración de PostgreSQL en entorno temporal | **OK.** `pg_restore` ejecutado; **1 tabla** restaurada fuera de los esquemas del sistema. |
| 9 | Comparación del dato de PostgreSQL | **COINCIDE.** Marcador `task-004-verificacion-20260731172038` recuperado íntegro. |
| 10 | Restauración de MinIO en entorno temporal | **OK.** 1 bucket recreado y **3 objetos** restaurados con `mc cp --attr` y `mc tag set`, en instancia temporal sin puertos publicados. |
| 11 | Comparación de checksums de objetos | **COINCIDEN los 3.** `datos/binario.b64` (4 150 B), `metadata/ejemplo.json` (60 B) y `simple.txt` (17 B). |
| 11a | Comparación de `Content-Type` | **COINCIDEN los 3.** `application/octet-stream`, `application/json` y `text/plain`. Además `Cache-Control=max-age=3600` en `ejemplo.json`. |
| 11b | Comparación de metadatos `x-amz-meta-*` | **COINCIDEN.** 2 metadatos en `ejemplo.json` (`X-Amz-Meta-Task`, `X-Amz-Meta-Origen`) y 1 en `binario.b64`. Sin metadatos ausentes ni inesperados. |
| 11c | Comparación de tags | **COINCIDEN los 2** de `ejemplo.json`: `entorno=local` y `tarea=task-004`. Sin tags ausentes ni inesperados. |
| 12 | Restauración de Portainer en volumen temporal | **OK.** Volumen `personal-blog-recovery_portainer_data` restaurado. |
| 13 | Inicio y respuesta de Portainer temporal | **HTTP 200** en `/api/status`, versión 2.39.5. **InstanceID coincide** con el del entorno principal: `b40b2115-22d9-4bae-a5f7-99f9a6671ee4`. |
| 14 | Eliminación solo de recursos temporales | **OK.** 3 contenedores, 3 volúmenes y 1 red eliminados, todos con prefijo `personal-blog-recovery`. |
| 15 | Volúmenes principales tras la limpieza | **3 de 3 presentes**, verificado por el propio script. |
| 16 | Servicios principales operativos | Los tres en marcha tras el ciclo completo. |
| 17 | Salud de PostgreSQL y MinIO | **healthy** ambos. |
| 18 | Portainer `/api/status` | **HTTP 200**. |
| 19 | `local-backups/` ignorado por Git | `git check-ignore -v` → `.gitignore:48:local-backups/`. |
| 20 | Backups reales en `git status` | **Ninguno.** El directorio no aparece. |
| 21 | Búsqueda de secretos | **0 credenciales reales** en archivos versionados. Las únicas coincidencias son los marcadores ficticios `change-me-*` de `.env.example`, ya presentes desde `Task/003`. |
| 22 | Guarda de seguridad | **Probada explícitamente**: bloquea los 3 volúmenes principales, los contenedores principales, el prefijo del proyecto y recursos ajenos; permite solo los `personal-blog-recovery*`. |
| 23 | Enlaces Markdown relativos | **326 verificados, 0 rotos**. |
| 24 | `git diff --check` | Sin errores de espacios en blanco. |
| 25 | Backend y frontend intactos | Ambos en `main`, **árboles limpios**, sin rama `Task/004`. |
| 26 | Ausencia de recursos cloud | **Ninguno.** Sin cuentas, sin llamadas a AWS ni Cloudflare. |
| 27 | Archivos Terraform nuevos | **Ninguno.** Sin `*.tf` en el workspace. |
| 28 | `Task/005` | **No iniciada.** Ninguna rama la referencia. |

### Validaciones añadidas en la ronda de corrección (2026-07-31)

| # | Validación | Resultado real |
| --- | --- | --- |
| 29 | Inventarios de metadatos y buckets presentes y con checksum | `minio-objects-metadata-20260731-172039.json` (3.18 KB) y `minio-buckets-20260731-172039.json` (1014 B), **ambos en `checksums.sha256`** y verificados. |
| 30 | **Detección de versionado — aborta** | Se activó el versionado en el bucket de prueba y se relanzó el backup: **abortó** con `versionado 'Enabled': solo se respalda la version actual de cada objeto` y `El conjunto no se puede considerar completo`. **No generó el conjunto.** |
| 31 | **Modo `-AllowPartial`** | Con el parámetro, el conjunto se generó y quedó marcado como **`completeness: PARCIAL`**, `backupResult.minio: PARCIAL` y con `unsupportedFeaturesFound` poblado. **Ninguna configuración se ignoró en silencio.** |
| 32 | Estructuras JSON reales de `mc` | Determinadas empíricamente, no supuestas: `mc stat --json` devuelve `metadata` con `Content-Type`, `Cache-Control` y `X-Amz-Meta-*`; `mc tag list --json` devuelve `tagset`; `mc stat --json <bucket>` devuelve `Versioning`, `ObjectLock`, `Replication`, `Policy`, `Encryption`, `ilm` y `location`. |
| 33 | Objeto de validación con metadatos completos | Creado `task004-verificacion/metadata/ejemplo.json`: contenido JSON, `Content-Type: application/json`, `Cache-Control`, 2 metadatos personalizados, **2 tags** y **ruta anidada**. |
| 34 | Datos de prueba eliminados de la fuente | Tabla eliminada (`\dt` → *Did not find any relations*) y bucket eliminado (`mc ls src` → vacío). |
| 35 | Conjuntos de prueba incompletos | Eliminados. **Se conserva únicamente `20260731-172039`**, el conjunto final correcto. Los conjuntos de la prueba de detección se generaron fuera de `local-backups/` y se borraron. |

## 11. Decisiones técnicas

| # | Decisión | Alternativas | Justificación | ¿ADR? |
| --- | --- | --- | --- | --- |
| 1 | PowerShell para los scripts. | Bash, Make. | El entorno principal es Windows con Docker Desktop, tal como fija `Task/003`. | No |
| 2 | `pg_dump` en formato custom. | SQL plano; copia del volumen. | Permite `pg_restore` selectivo, comprime y es independiente de la disposición del volumen. Una copia del volumen exige detener PostgreSQL y ata la copia a la versión exacta del motor. | No |
| 3 | Copia de MinIO a nivel de **objetos**. | `tar` del volumen `minio_data`. | Es portable a Amazon S3, que es el destino en producción según [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md). Una copia del volumen sería inservible fuera de MinIO. | No |
| 3a | **Inventario de metadatos y tags aparte del contenido.** | Confiar en `mc mirror --preserve`. | **Verificado**: `mirror` hacia un sistema de archivos copia el contenido, y `--preserve` preserva atributos del sistema de archivos, **no** los metadatos S3 ni los tags. Confiar en él habría producido restauraciones sin `Content-Type` ni `x-amz-meta-*`. Se inventarían con `mc stat --json` y `mc tag list --json`. | No |
| 3b | **Restaurar objeto a objeto con `mc cp --attr`,** no con `mc mirror`. | `mc mirror` en la restauración. | `mirror` subiría el contenido sin metadatos. `mc cp --attr` los aplica en la propia subida; los tags se reaplican después con `mc tag set`. | No |
| 3c | **Abortar ante configuraciones de bucket no soportadas.** | Registrarlas y continuar; ignorarlas. | Un backup que ignora en silencio lo que no sabe copiar da una confianza que no corresponde. Se aborta por defecto y `-AllowPartial` permite continuar marcando el conjunto como `PARCIAL`. | No |
| 3d | **Historial de versiones fuera del alcance,** declarado explícitamente. | Implementarlo. | Restaurar versiones anteriores exige recorrer `mc ls --versions` y reconstruir su orden, con un modelo de integridad propio. Se declara fuera de alcance **y se detecta**: si un bucket tiene versionado, el backup aborta salvo `-AllowPartial`. | No |
| 4 | Empaquetado de MinIO en `.zip`, no `.tar.gz`. | `tar` dentro del contenedor. | **La imagen de MinIO no incluye `tar` ni `find`** (verificado). `Compress-Archive` forma parte de PowerShell y no añade dependencias. | No |
| 5 | SHA-256 del contenido para verificar objetos, **no el ETag**. | Comparar ETags. | **Verificado empíricamente**: MinIO calcula el ETag según el modo de subida. El mismo contenido dio `7f849e30...-1` (multipart) y `2f9a86bf...` (PUT simple). Comparar ETags produce falsos negativos. | No |
| 6 | Cálculo de hashes en el host, no en el contenedor. | `sha256sum` dentro de MinIO. | La imagen no tiene `find` para recorrer el árbol. `Get-FileHash` en el host es uniforme para backup y restauración. | No |
| 7 | Detener **solo** Portainer durante su copia. | No detener nada; detener los tres. | Portainer escribe su base de forma continua. PostgreSQL y MinIO ofrecen copias coherentes en caliente y detenerlos sería una interrupción innecesaria. | No |
| 8 | Comparar el **InstanceID** de Portainer. | Comparar hashes de usuarios; iniciar sesión. | El InstanceID es un identificador **no sensible** derivado de la base de datos: demuestra que el volumen se restauró con su contenido real, sin tocar credenciales. | No |
| 9 | Instancia temporal de Portainer **sin** el socket de Docker. | Montarlo como en el entorno principal. | No lo necesita para arrancar, y así la prueba no concede acceso privilegiado al host a un contenedor efímero. Coherente con R-09. | No |
| 10 | Doble condición en la guarda de borrado. | Comprobar solo la lista de volúmenes principales. | Una lista negra falla ante nombres nuevos. Exigir además el prefijo `personal-blog-recovery` convierte la omisión en un bloqueo, no en un borrado. | No |
| 11 | Retención **manual**, sin rotación automática. | Rotación por número de conjuntos o por antigüedad. | En un entorno local, borrar copias sin que nadie lo decida es más peligroso que acumular unos megabytes. El alcance pide una política mínima. | No |
| 12 | Scripts en UTF-8 **con BOM**. | UTF-8 sin BOM. | **Verificado**: sin BOM, PowerShell 5.1 interpreta el archivo como ANSI y un solo carácter no ASCII rompe el análisis sintáctico. Ver sección 12, problema 1. | No |
| 13 | No incluir `.env` en los conjuntos. | Respaldarlo con el resto. | Es configuración reconstruible desde `.env.example`. Incluirlo duplicaría secretos en un artefacto ya sensible sin aportar nada. | No |

**No se creó ningún ADR.** Ninguna de estas decisiones altera la arquitectura acordada:
todas son de implementación local y reversibles.

## 12. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | **Los scripts no se analizaban.** Escritos en UTF-8 **sin BOM**, PowerShell 5.1 los leía como ANSI; el guion largo `—` se convertía en tres bytes, uno de los cuales (`0x94`) es una comilla tipográfica que cerraba cadenas antes de tiempo. | Todos los `.ps1` pasan a **UTF-8 con BOM** y a **solo ASCII**. Registrado como convención en `scripts/backup/README.md`. |
| 2 | **`&&` no es válido en PowerShell 5.1.** Aparecía dentro de una cadena con comillas dobles que PowerShell intentaba analizar. | Reemplazado por una cadena literal construida aparte, que ejecuta `sh` dentro del contenedor. |
| 3 | **`docker rm -f` sobre un contenedor inexistente abortaba el script.** Con `$ErrorActionPreference = 'Stop'`, el stderr de un ejecutable nativo se convierte en excepción, incluso cuando la ausencia es el resultado esperado. | Añadidas `Test-ContainerExists`, `Test-VolumeExists`, `Test-NetworkExists` y `Remove-ContainerIfExists`, que consultan con `--filter` en lugar de `inspect`. Eliminadas todas las redirecciones `2>$null` sobre `docker`. |
| 4 | **La imagen de MinIO no incluye `tar`.** El empaquetado falló con `tar: command not found`. | El árbol se extrae con `docker cp` y se comprime en el host con `Compress-Archive`. |
| 5 | **La imagen de MinIO tampoco incluye `find`.** El cálculo de hashes generó un archivo vacío **sin fallar**, que es peor: habría producido un backup que aparenta estar verificado. | Los hashes se calculan en el host con `Get-FileHash`. Además se añadió una comprobación de coherencia: si el inventario declara N objetos y se copian M distintos, **el backup se aborta**. |
| 6 | **La comparación por ETag daba falso negativo.** Los objetos originales, subidos con `mc pipe` (multipart), tenían ETag con sufijo `-1`; los restaurados con `mc mirror` (PUT simple), otro valor. El contenido era idéntico. | Verificado con `sha256sum` que el contenido coincidía. La verificación pasa a comparar **SHA-256 del contenido**. Documentado en el runbook para que no se reinterprete como un fallo. |
| 7 | **`.Count` sobre `$null` abortaba la verificación** con `Set-StrictMode`, cuando `Where-Object` no devolvía resultados. | Las colecciones se envuelven en `@()` antes de consultar `.Count`. |
| 8 | **Afirmación incorrecta sobre `mc mirror --preserve`,** detectada por el usuario en la revisión: se declaraba que respaldaba «objetos y metadatos» cuando solo copiaba el contenido. La validación con SHA-256 no lo detectaba porque los objetos de prueba no tenían metadatos personalizados ni tags. | Añadidos el inventario de metadatos y el de configuración de buckets, la restauración con `mc cp --attr` y `mc tag set`, y la comparación exacta de encabezados, metadatos y tags. Corregida toda la documentación. Detalle en la sección 18. |
| 9 | **Leer propiedades ausentes abortaba el script** con `Set-StrictMode`: `mc` omite `tagset` cuando el objeto no tiene tags, y campos de configuración cuando no están definidos. | Añadidas `Test-HasProperty` y `Get-PropertyOrDefault`; todo acceso a campos opcionales de `mc` pasa por ellas. |

## 13. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-08 | El entorno local no tiene copia de seguridad. | Alto | **Cerrado por esta tarea.** Existe un procedimiento de backup con integridad verificada y restauración demostrada. Queda como riesgo residual **R-11**. |
| R-11 | **Nuevo.** El backup es **manual**: si nadie lo ejecuta, se pierde todo lo hecho desde la última copia. | Medio | Política de retención (runbook §11) que exige backup antes de toda operación destructiva. La automatización queda fuera del alcance declarado. |
| R-12 | **Nuevo.** Los artefactos de respaldo son sensibles —incluyen hashes de autenticación de Portainer— y viven sin cifrar en el equipo. | Medio | `local-backups/` ignorado por Git y documentado como sensible en tres lugares. El cifrado queda fuera del alcance; se revisará en `Task/018`. |
| R-13 | **Nuevo.** La copia de Portainer exige detener su contenedor: si el proceso se interrumpe de forma anómala, podría quedar parado. | Bajo | El arranque está en un bloque `finally`: se ejecuta aunque la copia falle. Si aun así queda parado, `docker start` lo resuelve. |
| R-09 | Portainer conserva capacidad administrativa sobre el daemon de Docker. | Medio | Sin cambios respecto a `Task/003`. La instancia temporal de esta tarea **no** monta el socket. |
| R-10 | Las etiquetas de imagen fijadas envejecen. | Medio | Sin cambios. `Task/018` y `Task/021`. |
| R-02 a R-07 | Riesgos vigentes de tareas anteriores. | — | Sin cambios. |

## 14. Documentación creada o actualizada

- `scripts/backup/*.ps1` — **creados**: 5 scripts.
- `scripts/backup/README.md` — **creado**: referencia y garantías de seguridad.
- `docs/runbooks/local-backup-and-recovery.md` — **creado**: procedimiento completo.
- `docs/tasks/TASK-004-local-backups-and-recovery.md` — **creado**: esta ficha.
- `docs/task-reports/TASK-004-report.md` — **creado**: reporte de ejecución.
- `.gitignore` — `local-backups/` y `*.tar.gz` excluidos.
- `docs/runbooks/README.md` — índice con el nuevo runbook.
- `docs/project-management/STATUS.md` — `Task/004` en curso; R-08 cerrado; R-11 a R-13.
- `docs/project-management/ROADMAP.md` — estado de `Task/004`.
- `docs/stages/STAGE-01-local-infrastructure.md` — criterios de salida y riesgos.
- `docs/task-reports/README.md` — índice de reportes.
- `README.md` — sección de backup del entorno local.

## 15. Pasos de validación para el usuario

Ver [reporte de la tarea](../task-reports/TASK-004-report.md), sección 10.

## 16. Deuda técnica pendiente

- **Backup manual.** Sin automatización programada (R-11).
- **Sin cifrado** de los artefactos (R-12). A revisar en `Task/018`.
- **Sin copia fuera del equipo.** Un fallo de disco se lleva entorno y backups.
- **Sin rotación automática.** La retención es manual y depende de que alguien la aplique.
- **Sin validación de los scripts en CI.** Se añade en `Task/021`.
- **La restauración sobre el entorno principal es manual.** Documentada paso a paso, pero
  no automatizada: automatizar una operación destructiva sobre datos reales exigiría más
  garantías de las que esta tarea contempla.
- **Historial de versiones de MinIO fuera del alcance** (§6.1). Detectado y declarado, no
  ignorado: si un bucket tiene versionado, el backup aborta salvo `-AllowPartial`.
- **La configuración de los buckets se registra pero no se reaplica.** Tras una
  recuperación real habría que reponerla a mano desde `minio-buckets-<id>.json`.
- **Valores de metadato con `;` no soportados.** Rompen el formato de `mc cp --attr`; el
  backup aborta antes que generar algo que no se sabe restaurar.

## 17. Próxima tarea

`Task/005-Fundacion-Backend-FastAPI` — base profesional de FastAPI, configuración,
logging, PostgreSQL, Alembic, pruebas y Dockerfile. Primera tarea de la **ETAPA 02** y
primera del repositorio `personal-blog-backend`.

**No se inicia hasta que `Task/004` sea aprobada** y se complete su cierre.

## 18. Correcciones aplicadas tras la revisión del usuario

Ronda del 2026-07-31, sobre la misma rama y **sin ampliar el alcance declarado**. La tarea
permanece `Lista para validación`. No hubo commit, merge, push ni pull request.

### 18.1 Afirmación incorrecta sobre los metadatos de MinIO

**Error detectado por el usuario.** La ficha declaraba cumplido *«backup de los objetos y
metadatos de MinIO con `mc`»*, pero la implementación usaba
`mc mirror --preserve` → sistema de archivos → ZIP, y restauraba con `mc mirror`.

Ese camino conserva rutas y contenido, pero **no los metadatos S3 ni los tags**:
`--preserve` preserva atributos del **sistema de archivos** (permisos, fechas), no
`Content-Type`, `Cache-Control` ni los `x-amz-meta-*`. La validación no lo detectaba
porque los objetos de prueba **no tenían metadatos personalizados ni tags**: comparar solo
bytes no verificaba el criterio declarado.

**Corrección aplicada.** Se conserva la copia del contenido y se añade lo que faltaba:

| Añadido | Detalle |
| --- | --- |
| `minio-objects-metadata-<id>.json` | Por objeto: bucket, clave, tamaño, SHA-256, ETag, `lastModified`, encabezados restaurables, metadatos `x-amz-meta-*` y tags. |
| `minio-buckets-<id>.json` | Por bucket: versionado, Object Lock, replicación, política anónima, ciclo de vida, cifrado, ubicación y lista de características no soportadas. |
| Restauración con metadatos | Ya no se usa `mc mirror`: cada objeto se sube con `mc cp --attr` y los tags se reaplican con `mc tag set`. |
| Comparación exacta | Encabezados, metadatos `x-amz-meta-*` y tags se comparan **en ambos sentidos**: falta uno o aparece de más y la prueba falla. |
| Detección de lo no soportado | El backup **aborta** ante versionado, Object Lock, replicación, ciclo de vida, política anónima o cifrado, salvo `-AllowPartial`. |
| Inventarios en `checksums.sha256` | Los dos archivos nuevos entran en la verificación de integridad. |

**Estructuras JSON determinadas empíricamente**, no supuestas: `mc stat --json` devuelve
`metadata` con claves normalizadas (`Content-Type`, `X-Amz-Meta-Task`); `mc tag list
--json` devuelve `tagset`; `mc stat --json <bucket>` devuelve `Versioning`, `ObjectLock`,
`Replication`, `Policy`, `Encryption`, `ilm` y `location`.

### 18.2 Nueva prueba con metadatos reales

Se creó `task004-verificacion/metadata/ejemplo.json` con contenido JSON,
`Content-Type: application/json`, `Cache-Control: max-age=3600`, **2 metadatos
personalizados**, **2 tags** y **ruta anidada**; más `datos/binario.b64` (1 metadato) y
`simple.txt` (sin metadatos personalizados, para contraste).

El ciclo completo se ejecutó de nuevo: **los 3 objetos** recuperaron contenido,
`Content-Type`, `Cache-Control`, metadatos y tags de forma exacta.

### 18.3 Prueba de la detección de configuraciones no soportadas

Se activó el versionado en el bucket de prueba y se relanzó el backup:

- **Sin `-AllowPartial`: abortó**, nombrando el bucket y la causa. No generó el conjunto.
- **Con `-AllowPartial`:** lo generó marcado como `completeness: PARCIAL`,
  `backupResult.minio: PARCIAL` y con `unsupportedFeaturesFound` poblado.

Los conjuntos de esta prueba se generaron **fuera de `local-backups/`** y se eliminaron.

### 18.4 Documentación corregida

Se eliminó toda afirmación de que `mc mirror --preserve` conserva metadatos, y se
distingue explícitamente entre **contenido**, **metadatos**, **tags**, **configuración del
bucket** e **historial de versiones** en: `scripts/backup/README.md`,
`docs/runbooks/local-backup-and-recovery.md`, esta ficha, el reporte, `STATUS.md` y
`STAGE-01`.

### 18.5 Conjunto conservado

Se conserva **únicamente `20260731-172039`**, el conjunto final correcto, con 8 artefactos
e integridad verificada. Los conjuntos anteriores eran pruebas incompletas —sin inventario
de metadatos— y se eliminaron para que no se confundan con el válido.

---

## 19. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** |
| **Fecha de aprobación** | 2026-07-31 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/004-Backups-y-Recuperacion-Local` |

Con esta aprobación:

- El runbook [local-backup-and-recovery.md](../runbooks/local-backup-and-recovery.md) pasa
  de *Propuesta* a **Vigente**.
- **R-08 queda cerrado definitivamente.** El entorno local tiene copia externa a los
  volúmenes, con integridad verificada y restauración demostrada.
- El avance global pasa a **4 de 41 (10 %)**.
- **La ETAPA 01 queda COMPLETADA** (2 de 2 tareas aprobadas). La ETAPA 02 pasa a ser la
  siguiente.
- No se creó ningún ADR: las decisiones de esta tarea son de implementación local y
  reversibles.

Quedan abiertos los riesgos residuales **R-11** (el backup es manual), **R-12** (los
artefactos son sensibles y sin cifrar) y **R-13** (la copia de Portainer exige detenerlo).

### Flujo de cierre ejecutado

| # | Paso | Resultado |
| --- | --- | --- |
| 1 | Aprobación registrada documentalmente. | Hecho |
| 2 | Runbook promovido de *Propuesta* a **Vigente**. | Hecho |
| 3 | STATUS, ROADMAP y ficha de etapa actualizados; avance a 4 de 41; ETAPA 01 completada. | Hecho |
| 4 | Validaciones finales re-ejecutadas. | Hecho |
| 5 | Commits creados en la rama Task. | Hecho |
| 6 | `Task/004` integrada en `dev` con merge `--no-ff`. | Hecho |
| 7 | Push de `dev`. | Hecho |
| 8 | Publicación de la rama `Task/004`. | Hecho |
| 9 | Pull request **`Task/004-Backups-y-Recuperacion-Local → main`**, sin fusionar. | Hecho — abierto para revisión del usuario |
| 10 | Merge del pull request hacia `main`. | **No ejecutado** — corresponde exclusivamente al usuario |
| 11 | Vuelta a `main`, `fetch --prune` y `pull --ff-only`. | Hecho |
| 12 | Rama Task local eliminada con `git branch -d`. | Hecho |
| 13 | Rama Task remota conservada. | Hecho |
| 14 | `Task/005` iniciada. | **No** — requiere que el usuario fusione el PR y se complete la normalización `main → dev` |

Detalle completo: [reporte de la tarea](../task-reports/TASK-004-report.md).
