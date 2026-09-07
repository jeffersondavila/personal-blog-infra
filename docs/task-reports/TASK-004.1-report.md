# Reporte — TASK-004.1 · Corregir el tratamiento de rutas en el sistema de respaldo local

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/004.1-Corregir-Backup-Rutas-Literales` |
| **Tipo** | **Mantenimiento correctivo de `Task/004`** |
| **Cuenta en el roadmap** | **No.** Avance global (**17 de 41**) y ETAPA 05 (**2 de 3**) **sin cambios** |
| **Estado final** | **Aprobada** ✔ — cerrada el 2026-09-06 |
| **Expresión de aprobación** | `approved: Task/004.1-Corregir-Backup-Rutas-Literales` |
| **Repositorio** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/004.1-Corregir-Backup-Rutas-Literales`. **Publicada en el cierre** |
| **Rama base** | **`main`** |
| **SHA base** | **`0ec1231ae4aef116c85d1288a97d3f128eec64b5`** |
| **Fecha** | 2026-09-06 (los identificadores de conjunto llevan marca UTC) |
| **Ficha** | [TASK-004.1](../tasks/TASK-004.1-fix-backup-literal-paths.md) |
| **Commits** | **1**, creado **después** de la aprobación explícita del usuario |
| **Pull request** | `Task/004.1 → main` — **abierto, sin fusionar** |

---

## 1. El defecto

`New-LocalBackup.ps1` abortó durante un respaldo real:

```
BACKUP FALLIDO: No se encuentra la propiedad 'Hash' en este objeto.
```

El fallo ocurrió en la fase de MinIO. **Ningún contenedor llegó a detenerse** y ningún
volumen fue modificado, pero quedó un conjunto incompleto en disco.

## 2. Causa raíz

`scripts/backup/New-LocalBackup.ps1`, línea 297 del código original:

```powershell
$hash = (Get-FileHash -Path $file.FullName -Algorithm SHA256).Hash.ToLower()
```

`-Path` interpreta su argumento como **patrón**, no como ruta. En PowerShell `[...]` es
una clase de caracteres, así que una clave como

```
pruebas/test_el_tipo_de_contenido_y_el_tamano_se_preservan[minio]/02b7fbc8/tipada.png
```

deja de casar consigo misma. `Get-FileHash` devuelve `$null` y, bajo
`Set-StrictMode -Version Latest`, `$null.Hash` es un error terminante.

**El defecto no es de MinIO ni de `Get-FileHash`.** Es usar una ruta del sistema de
archivos ya resuelta como si fuera un patrón.

Comprobación directa sobre el archivo real:

| Llamada | Resultado |
| --- | --- |
| `Test-Path -LiteralPath` | `True` |
| `Get-FileHash -Path` | **`$null`** |
| `Get-FileHash -LiteralPath` | correcto |

Sin `Set-StrictMode` el fallo habría sido **silencioso**, que es peor: un respaldo sin
los hashes de sus objetos.

## 3. Por qué apareció ahora

El defecto existe desde `Task/004`. Se volvió **alcanzable** cuando aparecieron objetos
con corchetes en la clave:

| Bucket | Creado | Origen |
| --- | --- | --- |
| `personal-blog-media` | 2026-08-28 | bucket real del blog, **vacío** |
| `personal-blog-test-97fa6fde117d` | 2026-08-31 | residuo de tests de integración |
| `personal-blog-test-f25797004393` | 2026-09-02 | residuo de tests de integración |

De los 64 objetos presentes, **44 llevan corchetes** en la clave: son los identificadores
que genera `pytest` al parametrizar (`[minio]`, `[s3]`).

El último respaldo correcto es del **2026-07-31**, anterior a esos buckets. Por eso
`Task/004` se validó en su día sin detectar nada.

## 4. Prueba RED

Se creó `scripts/backup/Test-PathLiteralRegression.ps1` **antes** de corregir. Contra el
código de `main`:

```
    FAIL Get-Sha256 trata la ruta con corchetes como literal
         No se encuentra la propiedad 'Hash' en este objeto. Compruebe que existe.
    FAIL Get-FileSizeBytes trata la ruta con corchetes como literal
         No se encuentra la propiedad 'Length' en este objeto. Compruebe que existe.
    FAIL Get-FileHashMap indexa un objeto cuya CLAVE lleva corchetes
         El termino 'Get-FileHashMap' no se reconoce...
    FAIL Get-FileHashMap acepta una raiz que lleva corchetes
         El termino 'Get-FileHashMap' no se reconoce...

RESULTADO: 1 correcta(s), 4 fallida(s)
```

El primer fallo reproduce **literalmente** el mensaje del respaldo real. Los dos fallos de
`Get-FileHashMap` son RED de la extracción pendiente, no del defecto de comodines: se
declara así de forma explícita en lugar de presentarlos como si fueran lo mismo.

**Nota de honestidad.** Un quinto caso inicial comprobaba que un directorio con corchetes
se enumera y se borra. Pasaba desde el principio porque llamaba a los cmdlets con
`-LiteralPath` directamente, sin recorrer código del proyecto: era **tautológico**. Se
eliminó y se sustituyó por el caso que ejercita la guarda descrita en §5.3.

## 5. Corrección

### 5.1 Semántica literal

Toda ruta ya resuelta se consume con `-LiteralPath`.

| Archivo | Conversiones |
| --- | --- |
| `_BackupCommon.ps1` | 7 |
| `New-LocalBackup.ps1` | 12 |
| `Test-LocalBackup.ps1` | 11 |
| `Restore-LocalBackupTest.ps1` | 13 |
| `Remove-RecoveryTestResources.ps1` | 0 — no contenía ninguna |

Cada caso se revisó de forma individual para distinguir una ruta concreta de un comodín
deliberado. No se hizo ningún reemplazo masivo a ciegas.

### 5.2 `Get-FileHashMap` — se elimina el bucle duplicado

El bucle que falló estaba **duplicado**: en `New-LocalBackup.ps1` (indexar el árbol
copiado) y en `Restore-LocalBackupTest.ps1` (indexar el árbol restaurado). El mismo
defecto en dos sitios a la vez.

Ahora vive una sola vez en `_BackupCommon.ps1`. Comparar el original con lo restaurado
solo significa algo si ambos lados lo calculan con el mismo código.

Las claves se ordenan con `Sort-Object`: el orden de una hashtable de PowerShell no está
definido, y sin ordenar el archivo `.sha256` saldría en un orden distinto en cada
ejecución. Esto **evita una regresión** que habría introducido el propio refactor.

### 5.3 `Assert-NoWildcardInPath` — guarda fail-closed

Hallazgo adicional, comprobado en ejecución:

> **`Compress-Archive` de Windows PowerShell 5.1 falla con `[` en su ruta de origen
> INCLUSO con `-LiteralPath`.** Resuelve la ruta como patrón por dentro y no hay ningún
> parámetro que lo evite.

No se puede corregir desde el script. Por eso `Get-BackupRoot` —punto único por el que
pasan los tres scripts— rechaza ahora una raíz que contenga `[`, `]`, `*` o `?`, en lugar
de producir un conjunto que aparente estar completo.

Esto afecta **solo a la ruta del conjunto de respaldo**. Las **claves** de los objetos sí
pueden llevar corchetes: es justo lo que corrige el resto de la tarea.

### 5.4 Comodín deliberado que se conserva

```powershell
Compress-Archive -Path (Join-Path $stagingPath '*') -DestinationPath $hostMinioArchive -Force
```

El `*` es intencionado: archiva el **contenido** de `_staging`, no la carpeta. Solo expande
los hijos inmediatos, que son nombres de bucket, y S3 no admite corchetes en ellos; las
claves con corchetes viven más abajo y `Compress-Archive` las recorre sin volver a
interpretarlas. Queda documentado en el propio código para que no parezca un descuido en
la próxima revisión.

## 6. Respaldo real

Ejecutado **con los buckets `personal-blog-test-*` intactos**, que es el escenario que
reproduce el defecto.

| Dato | Valor |
| --- | --- |
| **Conjunto** | **`20260907-020539`** |
| Creado (UTC) | `2026-09-07T02:06:13Z` |
| Artefactos | 8 |
| Tamaño | 244.39 KB |
| PostgreSQL | `postgres-20260907-020539.dump` (39.89 KB) |
| MinIO | `minio-20260907-020539.zip` (44.12 KB) — **64 objetos** con SHA-256 |
| Portainer | `portainer-20260907-020539.tar.gz` (66.60 KB) |
| Manifiesto | presente |
| Checksums | presentes, 8 entradas |

Portainer se detuvo el tiempo mínimo y volvió a arrancar. PostgreSQL y MinIO no se
detuvieron en ningún momento.

## 7. Verificación

`Test-LocalBackup.ps1` sobre `20260907-020539`:

```
    INTEGRIDAD CORRECTA - 8 archivos
    Conjuntos verificados : 1
    Con problemas         : 0
```

## 8. Prueba de restauración — la sospecha era correcta

`Restore-LocalBackupTest.ps1` sobre el conjunto nuevo, en entorno temporal aislado:

```
    PostgreSQL : CORRECTA
    MinIO      : CORRECTA
    Portainer  : CORRECTA
    RESTAURACION VERIFICADA CORRECTAMENTE
```

| Comprobación | Resultado |
| --- | --- |
| Tablas restauradas | 17 |
| Objetos restaurados con metadatos y tags | 64 |
| Objetos con SHA-256 coincidente | 64, **44 de ellos con corchetes en la clave** |
| `Content-Type` comparados | 64 |
| Portainer temporal | HTTP 200, `InstanceID` coincide con el del entorno principal |

**Respuesta experimental a la pregunta abierta: sí, la restauración también estaba rota.**
`Restore-LocalBackupTest.ps1` contenía el defecto idéntico al indexar el árbol restaurado.
Con el código de `main` habría abortado con el mismo error. Es la **primera vez** que esa
prueba se ejecuta contra un conjunto con claves entre corchetes: la validación de
`Task/004` del 2026-07-31 no tenía ninguna.

No apareció ningún otro fallo por interpretación de comodines.

## 9. Integridad del entorno principal

| Comprobación | Resultado |
| --- | --- |
| `personal-blog-local_postgres_data` | presente |
| `personal-blog-local_minio_data` | presente |
| `personal-blog-local_portainer_data` | presente |
| Contenedores principales en marcha | **6 de 6** |
| Recursos temporales `personal-blog-recovery-*` | creados y eliminados por el propio procedimiento |
| `docker compose down` / `down -v` / `volume rm` / `prune` | **no ejecutados** |

## 10. Limpieza del conjunto fallido

`local-backups/20260907-014623/` eliminado **después** de cumplirse las tres condiciones:

| # | Condición | Resultado |
| --- | --- | --- |
| 1 | Existe un conjunto nuevo completo | **Sí** — `20260907-020539` |
| 2 | Verificado correctamente | **Sí** — integridad y restauración |
| 3 | El conjunto fallido es inequívocamente incompleto | **Sí** — sin `manifest.json`, sin `checksums.sha256`, `portainer/` **vacío** (0 archivos) y 64 archivos de `_staging` sin empaquetar |

`local-backups/20260731-172039/` **no se tocó**.

## 11. Hallazgo separado — buckets de test persistentes

**No se corrige en esta tarea.** No lo produce el sistema de respaldo.

Los tests de integración del backend dejan buckets `personal-blog-test-*` en el MinIO
local después de ejecutarse. Hay dos, del 2026-08-31 y del 2026-09-02, con 64 objetos.

Pendiente de investigar: **por qué el teardown no los elimina**. No se borran todavía:
son el escenario real de regresión de esta corrección.

## 12. Observación adicional — bucket vacío no restaurado

Detectada al leer la salida de la restauración. **Fuera del alcance de esta tarea y no
corregida.**

El conjunto declara 3 buckets, pero la restauración recreó **2**. `personal-blog-media`
no se recrea porque no tiene objetos y los buckets se reconstruyen a partir de ellos. En
una restauración real, un bucket vacío se perdería.

Es un hueco **preexistente** de `Task/004`, sin relación con el defecto de rutas. Se deja
registrado para decidirlo aparte.

## 13. Archivos

### Creados

| Archivo | Contenido |
| --- | --- |
| `scripts/backup/Test-PathLiteralRegression.ps1` | Regresión de rutas literales, 5 casos |
| `docs/tasks/TASK-004.1-fix-backup-literal-paths.md` | Ficha |
| `docs/task-reports/TASK-004.1-report.md` | Este reporte |

### Modificados

| Archivo | Cambio |
| --- | --- |
| `scripts/backup/_BackupCommon.ps1` | 7 conversiones + `Get-FileHashMap` + `Assert-NoWildcardInPath` |
| `scripts/backup/New-LocalBackup.ps1` | 12 conversiones + uso de `Get-FileHashMap` + comentario del comodín deliberado |
| `scripts/backup/Test-LocalBackup.ps1` | 11 conversiones |
| `scripts/backup/Restore-LocalBackupTest.ps1` | 13 conversiones + uso de `Get-FileHashMap` |
| `docs/task-reports/README.md` | Fila en el índice de reportes |

### No modificados

`docker-compose.yml`, `.env`, `.gitignore`, runbooks, `STATUS.md`, `ROADMAP.md`.

## 14. Validaciones ejecutadas

| Validación | Resultado |
| --- | --- |
| Sintaxis de los 6 scripts (`Parser::ParseFile`) | **0 errores** |
| Regresión dirigida — RED previo | **4 de 5 fallando**, por la razón esperada |
| Regresión dirigida — GREEN | **5 de 5 correctas** |
| Respaldo real completo | **Correcto** — `20260907-020539` |
| Verificación de integridad | **Correcta** — 8 archivos |
| Prueba de restauración aislada | **Correcta** — PostgreSQL, MinIO y Portainer |
| Finales de línea | LF en todos los archivos, según `.gitattributes` |
| Búsqueda de secretos | Ninguno. No se creó `secrets/`, no hay credenciales en el diff |

## 15. Refactor

Ejecutado: extracción de `Get-FileHashMap` para eliminar el bucle duplicado. No cambia el
comportamiento observable salvo el **orden determinista** del archivo `.sha256`, que es
una corrección necesaria del propio refactor y queda justificada en §5.2.

## 16. Límites respetados

| Límite | Cumplido |
| --- | --- |
| No iniciar `Task/018` | **Sí** |
| No resetear Portainer | **Sí** |
| No borrar buckets `personal-blog-test-*` | **Sí** |
| No parchear `main` | **Sí** — rama Task creada desde `main` |
| Sin commit, push ni PR **antes** de la aprobación | **Sí** — el árbol se dejó sin commit para validación |
| Commit, push y PR **solo tras** `approved:` | **Sí** — 1 commit, rama publicada, PR `Task/004.1 → main` abierto |
| PR **no** fusionado por el agente | **Sí** — la fusión es responsabilidad del usuario |
| No tocar volúmenes principales | **Sí** |
| No cambiar el avance del roadmap | **Sí** — 17/41 y ETAPA 05 2/3 intactos |

## 17. Estado final

**Aprobada** ✔ el 2026-09-06 mediante
`approved: Task/004.1-Corregir-Backup-Rutas-Literales`.

Integrada en `dev` mediante merge `--no-ff` y publicada. El pull request
`Task/004.1 → main` queda **abierto y sin fusionar**: aceptarlo es responsabilidad
exclusiva del usuario.

Queda desbloqueado el trabajo operativo en espera: el reset del administrador de
Portainer, que ya cuenta con un respaldo válido y verificado (`20260907-020539`).
