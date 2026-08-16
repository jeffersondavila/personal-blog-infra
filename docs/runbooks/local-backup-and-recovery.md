# Runbook — Backup y recuperación local

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/004-Backups-y-Recuperacion-Local` (2026-07-31) |
| **Fecha** | 2026-07-31 |
| **Tarea** | `Task/004-Backups-y-Recuperacion-Local` |
| **Alcance** | Respaldo, verificación y restauración de PostgreSQL, MinIO y Portainer en local |

Procedimiento para crear copias de seguridad del entorno local, verificar su integridad,
probar que se pueden restaurar y recuperar el entorno tras una pérdida.

Complementa a [local-environment.md](local-environment.md), que cubre el arranque, la
parada y el diagnóstico del entorno.

> **Un backup que nunca se ha restaurado no cuenta como backup.** Por eso este runbook
> incluye una prueba de restauración real, en un entorno aislado, y por eso conviene
> ejecutarla de vez en cuando y no solo el día que hace falta.

---

## 1. Qué cubre y qué no

| Cubre | No cubre |
| --- | --- |
| Copia de PostgreSQL con `pg_dump`, en caliente. | Automatización programada (tarea del sistema, cron). |
| **Contenido** de los objetos de MinIO. | Subida de las copias a la nube o a otro equipo. |
| **Metadatos y tags** de los objetos de MinIO. | Cifrado de los artefactos. |
| Copia del volumen de datos de Portainer. | Retención automática o rotación programada. |
| Checksums SHA-256 y manifiesto por ejecución. | Restauración *en caliente* sobre el entorno principal. |
| Prueba de restauración en un entorno temporal aislado. | Recuperación de datos que nunca llegaron a respaldarse. |
| Recuperación tras pérdida total de contenedores y volúmenes. | **Historial de versiones de MinIO.** |
| Registro de la configuración de cada bucket. | **Reaplicación** de esa configuración al restaurar. |

**Todo es local.** Ningún recurso cloud interviene en este procedimiento.

### 1.1 Qué se respalda exactamente en MinIO

Conviene distinguir cuatro cosas que suelen confundirse:

| Elemento | ¿Se respalda? | ¿Se restaura? | ¿Se verifica? |
| --- | :---: | :---: | :---: |
| **Contenido del objeto** | Sí | Sí | Sí — SHA-256 del contenido |
| **Metadatos del objeto** (`Content-Type`, `Cache-Control`, `Content-Disposition`, `Content-Encoding`, `Content-Language`, `x-amz-meta-*`) | Sí | Sí | Sí — comparación exacta |
| **Tags del objeto** | Sí | Sí | Sí — comparación exacta |
| **Configuración del bucket** (versionado, Object Lock, replicación, ciclo de vida, política anónima, cifrado) | Se **registra** | **No** | No |
| **Historial de versiones** | **No** | **No** | No |

> **`mc mirror` hacia un sistema de archivos copia el contenido, no los metadatos.**
> La opción `--preserve` preserva atributos del sistema de archivos (permisos, fechas),
> **no** los metadatos S3 ni los tags. Por eso el procedimiento los inventaría aparte con
> `mc stat --json` y `mc tag list --json`, y los **reaplica explícitamente** al restaurar
> con `mc cp --attr` y `mc tag set`.

**Alcance temporal: la versión ACTUAL de cada objeto.** Si un bucket tiene versionado
activo, las versiones anteriores **no se respaldan**. El script lo detecta y no lo pasa
por alto — ver sección 4.2.

**Lo que no se reaplica al restaurar:** el `ETag` y la fecha de última modificación son
derivados y los recalcula MinIO; `X-Amz-Tagging-Count` se deriva del número de tags, que
sí se verifica.

---

## 2. Requisitos

| Requisito | Detalle |
| --- | --- |
| Docker Desktop | En ejecución. Los scripts fallan de forma explícita si el daemon no responde. |
| PowerShell | 5.1 o superior. Los scripts se prueban en PowerShell 5.1 de Windows. |
| Entorno local levantado | Los tres servicios en marcha (`docker compose up -d`). |
| Archivo `.env` | En la raíz del repositorio. Los scripts lo leen; nunca imprimen sus valores. |
| Imagen `alpine:3.22` | Se descarga automáticamente la primera vez. |
| Espacio en disco | Proporcional al contenido: la base de datos vacía y sin objetos ocupa unos 12 KB. |

---

## 3. Dónde viven las copias

```
personal-blog-infra/
└── local-backups/              <- IGNORADO POR GIT
    └── YYYYMMDD-HHMMSS/        <- un conjunto por ejecución, en UTC
        ├── manifest.json
        ├── checksums.sha256
        ├── postgres/
        │   ├── postgres-<id>.dump                 volcado custom (pg_restore)
        │   └── postgres-<id>.toc.txt              índice legible del volcado
        ├── minio/
        │   ├── minio-<id>.zip                     CONTENIDO de los objetos
        │   ├── minio-inventory-<id>.json          inventario con tamaños y ETags
        │   ├── minio-objects-<id>.sha256          SHA-256 del contenido
        │   ├── minio-objects-metadata-<id>.json   METADATOS y TAGS por objeto
        │   └── minio-buckets-<id>.json            configuración de cada bucket
        └── portainer/
            └── portainer-<id>.tar.gz              volumen de datos completo
```

### 3.1 Sensibilidad de los artefactos

> **Trata el contenido de `local-backups/` como información sensible.**

| Artefacto | Qué contiene |
| --- | --- |
| Volcado de PostgreSQL | Todos los datos del blog. Cuando exista contenido real, incluirá el hash de la contraseña del administrador y el registro de auditoría. |
| Copia de MinIO | Todos los archivos e imágenes subidos. |
| Copia de Portainer | Configuración interna, usuarios, **hashes de autenticación**, endpoints y claves internas de la instalación. |

Reglas:

- **`local-backups/` está ignorado por Git** y no debe aparecer nunca en `git status`.
- **Nunca** se versiona un backup, ni se adjunta a un pull request, ni se comparte.
- Los scripts **no imprimen contraseñas** y el manifiesto **no registra ningún secreto**.
- El archivo `.env` **no se incluye** en los conjuntos de respaldo: es configuración, se
  reconstruye desde `.env.example`, y meterlo en la copia sería duplicar secretos sin
  necesidad.

---

## 4. Crear un backup

Desde `scripts/backup/`:

```powershell
.\New-LocalBackup.ps1
```

Qué hace, en orden:

1. Comprueba dependencias y que los tres volúmenes principales existen.
2. **PostgreSQL**: `pg_dump --format=custom` dentro del contenedor, **sin detenerlo**.
   Genera además el índice del volcado con `pg_restore --list`.
3. **MinIO**, **sin detenerlo**:
   - Inspecciona la configuración de cada bucket y **aborta** si encuentra algo que no
     sabe restaurar (sección 4.2).
   - `mc mirror` a un directorio temporal para el **contenido**.
   - `mc stat --json --recursive` y `mc tag list --json` para los **metadatos y tags**.
   - Calcula el SHA-256 de cada objeto y empaqueta el árbol en un `.zip`.
4. **Portainer**: **detiene el contenedor**, empaqueta su volumen con un contenedor
   auxiliar y **lo vuelve a arrancar**.
5. Calcula los checksums SHA-256 de todos los artefactos, inventarios incluidos.
6. Escribe el manifiesto.

Opciones:

```powershell
.\New-LocalBackup.ps1 -SkipPortainer          # omite Portainer y su parada
.\New-LocalBackup.ps1 -BackupRoot D:\copias   # otro destino
.\New-LocalBackup.ps1 -AllowPartial           # permite un conjunto PARCIAL
Get-Help .\New-LocalBackup.ps1 -Full          # ayuda completa
```

### 4.2 Configuraciones que el script no sabe restaurar

Antes de copiar nada, el script inspecciona cada bucket y busca:

| Configuración | Consecuencia |
| --- | --- |
| Versionado `Enabled` o `Suspended` | Solo se respaldaría la versión actual de cada objeto. |
| Object Lock activo | No se respaldan retenciones ni modos de bloqueo. |
| Replicación configurada | No se respalda su configuración. |
| Reglas de ciclo de vida | No se respaldan. |
| Política anónima distinta de `private` | Se registra, pero no se reaplica al restaurar. |
| Cifrado en reposo configurado | No se respalda su configuración. |

Si encuentra alguna, **aborta** con un mensaje que la nombra. Un backup que ignora en
silencio lo que no sabe copiar es peor que no tener backup: da una confianza que no
corresponde.

Para generar el conjunto de todos modos:

```powershell
.\New-LocalBackup.ps1 -AllowPartial
```

El conjunto queda marcado como **`PARCIAL`** en `manifest.json` (`completeness`) y en
`minio-buckets-<id>.json`, con la lista exacta de lo que no cubre.

### 4.1 Por qué solo se detiene Portainer

PostgreSQL y MinIO ofrecen copias coherentes **en caliente**: `pg_dump` trabaja sobre una
instantánea transaccional y `mc mirror` lee objetos completos a través de la API de S3.

Portainer no ofrece nada equivalente: escribe su base interna de forma continua y copiar
sus archivos mientras escribe puede producir un archivo inconsistente. Por eso **se
detiene durante el tiempo mínimo necesario** y se arranca inmediatamente después, incluso
si la copia falla.

**PostgreSQL y MinIO no se detienen en ningún momento.**

---

## 5. Verificar la integridad

```powershell
.\Test-LocalBackup.ps1                        # el conjunto más reciente
.\Test-LocalBackup.ps1 -BackupSet 20260731-161342
.\Test-LocalBackup.ps1 -All                   # todos los conjuntos
```

Comprueba que cada archivo existe, que su SHA-256 coincide con el registrado y que no hay
archivos en el conjunto que falten en `checksums.sha256`. No toca Docker y no restaura
nada.

> `manifest.json` no figura en `checksums.sha256` **a propósito**: la prueba de
> restauración escribe su resultado en él. Los artefactos de datos sí están todos.

---

## 6. Probar la restauración en un entorno aislado

```powershell
.\Restore-LocalBackupTest.ps1
```

Con verificación del dato de prueba de PostgreSQL:

```powershell
.\Restore-LocalBackupTest.ps1 -ExpectedPostgresMarker 'mi-marcador'
```

Para conservar el entorno temporal e inspeccionarlo:

```powershell
.\Restore-LocalBackupTest.ps1 -KeepResources
```

### 6.1 Qué crea, y por qué es seguro

Todo lleva el prefijo `personal-blog-recovery`:

| Recurso temporal | Aislamiento |
| --- | --- |
| Red `personal-blog-recovery-net` | Independiente de las redes del entorno principal. |
| `personal-blog-recovery-postgres` | Volumen propio, **sin puertos publicados**. |
| `personal-blog-recovery-minio` | Volumen propio, **sin puertos publicados**. |
| `personal-blog-recovery-portainer` | Volumen propio, en `127.0.0.1:9445`, **sin el socket de Docker**. |

Las credenciales del entorno temporal **se generan al vuelo**, no se imprimen y no se
guardan: las instancias se destruyen al terminar.

**El entorno principal no se detiene, no se modifica y no se elimina.** Una guarda de
seguridad aborta cualquier operación de borrado sobre un recurso cuyo nombre empiece por
`personal-blog-local`.

### 6.2 Qué comprueba

| Componente | Comprobación |
| --- | --- |
| PostgreSQL | `pg_restore` termina; se cuentan las tablas restauradas; si se indicó un marcador, debe existir y coincidir. |
| MinIO — contenido | Se compara el **SHA-256 del contenido** de cada objeto, y se detectan objetos ausentes o inesperados. |
| MinIO — metadatos | Se consulta cada objeto restaurado con `mc stat --json` y se comparan **exactamente** los encabezados restaurables y los `x-amz-meta-*`, en ambos sentidos: falta un metadato o aparece uno de más y la prueba falla. |
| MinIO — tags | Se consultan con `mc tag list --json` y se comparan **exactamente**, también en ambos sentidos. |
| Portainer | La instancia temporal arranca, responde `HTTP 200` en `/api/status` y su **InstanceID** coincide con el del entorno principal. |

La restauración de MinIO **no usa `mc mirror`**: subiría el contenido sin los metadatos.
Cada objeto se restaura con `mc cp --attr`, que los aplica en la propia subida, y después
se reaplican los tags con `mc tag set`.

> **Por qué SHA-256 y no ETag.** MinIO calcula el ETag de forma distinta según cómo se
> subiera el objeto: uno subido en multipart lleva sufijo `-N` y el mismo contenido
> restaurado con un PUT simple recibe otro valor. Comparar ETags daría falsos negativos.
> El SHA-256 del contenido no depende del modo de subida.

> **Qué queda fuera de la comparación.** El `ETag` y `lastModified` son derivados y los
> recalcula MinIO. `X-Amz-Tagging-Count` se deriva del número de tags, que sí se verifica
> por separado. La **configuración de los buckets no se reaplica**, así que tampoco se
> compara: el script la muestra al empezar para que quede a la vista.

> **Por qué el InstanceID.** Es un identificador **no sensible** que Portainer deriva de
> su base de datos. Si el de la instancia restaurada coincide con el del entorno
> principal, el volumen se restauró con su contenido real. **No se comprueban ni se
> restablecen contraseñas.**

---

## 7. Limpiar los recursos temporales

```powershell
.\Remove-RecoveryTestResources.ps1 -WhatIf    # ver qué se eliminaría
.\Remove-RecoveryTestResources.ps1 -Force     # eliminar sin confirmación
```

Antes de borrar nada valida **todo** el inventario: si un solo recurso no supera la
comprobación, no se elimina ninguno. Nunca elimina recursos del entorno principal, y al
terminar confirma que los tres volúmenes principales siguen existiendo.

Este script **no** ejecuta `docker compose down -v`, `docker system prune` ni
`docker volume prune`.

---

## 8. `docker compose down` frente a `down -v`

| Comando | Contenedores | Redes | **Volúmenes** | Datos |
| --- | --- | --- | --- | --- |
| `docker compose stop` | Detenidos | Se conservan | **Se conservan** | Intactos |
| `docker compose down` | Eliminados | Eliminadas | **Se conservan** | **Intactos** |
| `docker compose down -v` | Eliminados | Eliminadas | **ELIMINADOS** | **DESTRUIDOS** |

`docker compose down` es seguro: recrea los contenedores desde cero pero vuelve a montar
los mismos volúmenes.

**`docker compose down -v` destruye la base de datos, los objetos de MinIO y la
configuración de Portainer.** No hay deshacer. Antes de ejecutarlo:

```powershell
.\New-LocalBackup.ps1
.\Test-LocalBackup.ps1
```

---

## 9. Recuperación

> Los procedimientos de esta sección **sobrescriben datos del entorno principal**. Haz un
> backup antes, aunque el entorno parezca perdido: un backup del estado roto puede ser
> útil para diagnosticar.

### 9.1 Recuperar PostgreSQL

```powershell
# 1. Copiar el volcado al contenedor
docker cp .\local-backups\<id>\postgres\postgres-<id>.dump personal-blog-local-postgres:/tmp/restore.dump

# 2. Restaurar. --clean elimina los objetos existentes antes de recrearlos
docker exec personal-blog-local-postgres pg_restore -U blog_local -d personal_blog `
    --clean --if-exists --no-owner --no-privileges /tmp/restore.dump

# 3. Limpiar
docker exec personal-blog-local-postgres rm -f /tmp/restore.dump

# 4. Comprobar
docker exec personal-blog-local-postgres psql -U blog_local -d personal_blog -c "\dt"
```

`pg_restore` puede devolver un código distinto de cero por avisos no fatales. Lo que
decide es si los datos están: compruébalo con `\dt` y consultando las tablas.

### 9.2 Recuperar MinIO

> **`mc mirror` restauraría el contenido pero dejaría los objetos sin sus metadatos ni
> sus tags.** Para recuperarlos hay que subir cada objeto con `mc cp --attr` y reaplicar
> los tags, tal como hace `Restore-LocalBackupTest.ps1`.

**Opción recomendada:** reutilizar la lógica ya probada del script, que lee el inventario
de metadatos y lo reaplica objeto a objeto. Consúltalo en
[`Restore-LocalBackupTest.ps1`](../../scripts/backup/Restore-LocalBackupTest.ps1), sección
de MinIO.

**Procedimiento manual**, si prefieres hacerlo paso a paso:

```powershell
# 1. Expandir el archivo de objetos y copiarlo al contenedor
Expand-Archive .\local-backups\<id>\minio\minio-<id>.zip -DestinationPath $env:TEMP\minio-restore
docker cp $env:TEMP\minio-restore personal-blog-local-minio:/tmp/minio-restore

# 2. Configurar el cliente
docker exec personal-blog-local-minio sh -c 'mc alias set local http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"'

# 3. Recrear los buckets que declara el inventario
docker exec personal-blog-local-minio sh -c 'for b in $(ls /tmp/minio-restore); do mc mb --ignore-existing local/$b; done'

# 4. Subir cada objeto CON sus metadatos. Los valores salen de
#    minio-objects-metadata-<id>.json, campos `headers` y `userMetadata`:
docker exec personal-blog-local-minio mc cp `
    --attr "Content-Type=application/json;Cache-Control=max-age=3600;x-amz-meta-task=task-004" `
    /tmp/minio-restore/<bucket>/<clave> local/<bucket>/<clave>

# 5. Reaplicar los tags. Los valores salen del campo `tags` del mismo archivo:
docker exec personal-blog-local-minio mc tag set local/<bucket>/<clave> "entorno=local&tarea=task-004"

# 6. Limpiar y comprobar
docker exec personal-blog-local-minio sh -c 'rm -rf /tmp/minio-restore'
docker exec personal-blog-local-minio mc ls --recursive local
docker exec personal-blog-local-minio mc stat --json local/<bucket>/<clave>
Remove-Item $env:TEMP\minio-restore -Recurse -Force
```

En PowerShell, usa comillas **simples** para el argumento de `sh -c`: con comillas dobles,
PowerShell expande `$MINIO_ROOT_USER` antes de enviarlo y el comando falla con
`Invalid access key`.

**La configuración de los buckets no se restaura**: si el bucket original tenía
versionado, política anónima o reglas de ciclo de vida, hay que reaplicarlas a mano
consultando `minio-buckets-<id>.json`.

### 9.3 Recuperar Portainer

```powershell
# 1. Detener Portainer
docker stop personal-blog-local-portainer

# 2. Contenedor auxiliar que escribe en el volumen
docker create --name portainer-restore -v personal-blog-local_portainer_data:/data `
    alpine:3.22 sh -c "rm -rf /data/* && tar xzf /portainer.tar.gz -C /data"
docker cp .\local-backups\<id>\portainer\portainer-<id>.tar.gz portainer-restore:/portainer.tar.gz
docker start -a portainer-restore
docker rm -f portainer-restore

# 3. Arrancar y comprobar
docker start personal-blog-local-portainer
Start-Process "https://127.0.0.1:9444"
```

Tras restaurar, Portainer vuelve al estado del backup: **el usuario administrador y su
contraseña son los que existían entonces**.

### 9.4 Recuperación completa tras pérdida total

Cuando ya no existen ni contenedores ni volúmenes — por ejemplo tras un
`docker compose down -v`:

```powershell
# 1. Recrear el entorno vacío
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra
Copy-Item .env.example .env      # si tampoco existe .env; revisa los valores
docker compose up -d
docker compose ps                # esperar a que postgres y minio estén healthy

# 2. Verificar el backup antes de usarlo
cd scripts\backup
.\Test-LocalBackup.ps1

# 3. Restaurar los tres componentes: secciones 9.1, 9.2 y 9.3

# 4. Comprobar el resultado
docker compose ps
docker exec personal-blog-local-postgres psql -U blog_local -d personal_blog -c "\dt"
docker exec personal-blog-local-minio mc ls --recursive local
```

**Qué no se recupera:** todo lo ocurrido **después** del último backup. Ese es el motivo
de la política de retención de la sección 11.

---

## 10. Resolución de problemas

| Síntoma | Causa habitual | Qué hacer |
| --- | --- | --- |
| `El daemon de Docker no responde` | Docker Desktop parado. | Arráncalo y repite. |
| `No existe el archivo .env` | Falta la configuración local. | `Copy-Item .env.example .env`. |
| `FALTAN VOLUMENES DEL ENTORNO PRINCIPAL` | Los volúmenes no existen. | **Detente.** Alguien ejecutó `down -v` o los borró. Ve a la sección 9.4. |
| `Incoherencia en la copia de MinIO` | El inventario y los objetos copiados no cuadran. | No se genera el backup. Repite; si persiste, revisa el estado de MinIO. |
| `El conjunto no se puede considerar completo` | Algún bucket usa versionado, Object Lock, replicación, ciclo de vida, política anónima o cifrado. | Revisa la lista que muestra. Si aceptas la limitación, repite con `-AllowPartial`: el conjunto quedará marcado como PARCIAL. |
| `tiene un metadato con ';'` | Un valor de metadato contiene `;`, que rompe el formato de `mc cp --attr`. | El backup se aborta antes que generar algo que no se sabe restaurar. Cambia ese metadato o amplía el script. |
| `El conjunto no incluye el inventario de metadatos` | El conjunto lo generó una versión anterior del script. | Genera un conjunto nuevo con `New-LocalBackup.ps1`. |
| `OPERACION BLOQUEADA` en la limpieza | Se intentó borrar algo del entorno principal. | Es la guarda haciendo su trabajo. Revisa qué nombre se pasó. |
| `checksum distinto` al verificar | El archivo se corrompió o se modificó. | **No restaures ese conjunto.** Usa otro y genera uno nuevo. |
| `Invalid access key` con `mc` | Comillas dobles en `sh -c`: PowerShell expandió la variable. | Usa comillas simples. |
| La prueba de restauración deja recursos en pie | Falló a mitad. | `.\Remove-RecoveryTestResources.ps1 -Force`. |
| Portainer temporal no responde | Arranque lento o puerto 9445 ocupado. | Comprueba el puerto; repite. |

---

## 11. Retención

Política **manual y mínima**, acorde al alcance de un entorno local:

| Regla | Detalle |
| --- | --- |
| **Antes de cualquier operación destructiva** | Backup obligatorio: `down -v`, cambio de versión mayor de PostgreSQL, reconstrucción del entorno. |
| **Conservar** | Los **3 conjuntos** más recientes, y el último que superó una prueba de restauración. |
| **Eliminar** | El resto, borrando el directorio del conjunto completo. |
| **Verificar** | Ejecutar `Test-LocalBackup.ps1 -All` de vez en cuando; un conjunto corrupto se descarta. |
| **Probar la restauración** | Al menos una vez por etapa del roadmap, y siempre antes de una operación destructiva planificada. |

Eliminar un conjunto es borrar su carpeta:

```powershell
Remove-Item .\local-backups\<id> -Recurse -Force
```

No hay rotación automática **a propósito**: en un entorno local, borrar copias sin que
nadie lo decida es más peligroso que acumular unos megabytes.

---

## 12. Qué no cubre `Task/004`

| Elemento | Dónde corresponde |
| --- | --- |
| Automatización programada del backup | Fuera del alcance actual. Requeriría una tarea del sistema. |
| Copia fuera del equipo o en la nube | Etapas 09 y 10; para producción, D-10 en [open-decisions.md](../architecture/open-decisions.md). |
| Cifrado de los artefactos | No contemplado. Los conjuntos se protegen manteniéndolos locales y sin versionar. |
| **Historial de versiones de MinIO** | Solo se respalda la versión **actual** de cada objeto. Restaurar versiones anteriores exigiría recorrer `mc ls --versions` y reconstruir el orden de versiones, con su propio modelo de integridad. |
| **Reaplicación de la configuración de los buckets** | Versionado, Object Lock, replicación, ciclo de vida, política anónima y cifrado se **registran** pero no se restauran. Reaplicarlos sin poder verificarlos sería dar una garantía falsa. |
| Backups del backend y del frontend | No existen todavía (`Task/005`, `Task/006`). |
| Backup del esquema de la aplicación | No hay esquema hasta `Task/008`; el procedimiento ya lo cubrirá automáticamente. |
| Restauración a un punto en el tiempo | Requeriría WAL archiving; desproporcionado para un entorno local. |
| Backups de PostgreSQL de producción en el VPS, **fuera del host** y con restore probado | `Task/029`, decisión D-10. Ver [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) §15. |

Nada de esto se ignora en silencio: el script **detecta** las configuraciones que no sabe
restaurar y **aborta** salvo que se le pase `-AllowPartial`, en cuyo caso marca el
conjunto como `PARCIAL`.

---

## 13. Documentos relacionados

- [local-environment.md](local-environment.md) — arranque, parada y diagnóstico.
- [ADR-001 — Estrategia local-first](../adr/ADR-001-local-first.md)
- [security-boundaries.md](../architecture/security-boundaries.md) — reglas de Portainer.
- [ETAPA 01 — Infraestructura Local](../stages/STAGE-01-local-infrastructure.md)
- [TASK-004](../tasks/TASK-004-local-backups-and-recovery.md) — ficha de la tarea.
- [scripts/backup/README.md](../../scripts/backup/README.md) — referencia de los scripts.
