# TASK-004.1 — Corregir el tratamiento de rutas en el sistema de respaldo local

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/004.1-Corregir-Backup-Rutas-Literales` |
| **Nombre** | Corregir el tratamiento de rutas en el sistema de respaldo local |
| **Tipo** | **Mantenimiento correctivo de `Task/004`** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**17 de 41**, 41 %) ni la ETAPA 05 (**2 de 3**, 67 %) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/017-Observabilidad-Local` — **Aprobada** ✔, PR `#30` fusionado y normalización `main → dev` completada |
| **Rama** | `Task/004.1-Corregir-Backup-Rutas-Literales`. **Publicada en el cierre** |
| **Rama base** | **`main`** |
| **SHA base** | **`0ec1231ae4aef116c85d1288a97d3f128eec64b5`** (`= main = origin/main` al crearla) |
| **Fecha de inicio** | 2026-09-06 |
| **Fecha de aprobación** | **2026-09-06** |
| **Expresión de aprobación** | `approved: Task/004.1-Corregir-Backup-Rutas-Literales` |
| **Próxima tarea** | Ninguna del roadmap. Queda desbloqueado el trabajo operativo en espera: reset del administrador de Portainer |
| **Ficha origen** | [TASK-004](TASK-004-local-backups-and-recovery.md) |
| **Reporte** | [TASK-004.1-report.md](../task-reports/TASK-004.1-report.md) |
| **Pull request** | [`#31`](https://github.com/jeffersondavila/personal-blog-infra/pull/31) `Task/004.1 → main`, creado durante el cierre aprobado y **fusionado manualmente por el usuario el 2026-09-07**, merge commit `a90cc55` |

---

## 0. Preparación Git

| # | Comprobación | Resultado real |
| --- | --- | --- |
| 1 | `main == origin/main` | **Sí** — ambos `0ec1231` |
| 2 | Working tree limpio antes de crear la rama | **Sí** — `git status --porcelain` vacío |
| 3 | Rama activa antes de crear = `main` | **Sí** |
| 4 | Rama creada **desde `main`** | **Sí** |
| 5 | `git rev-parse HEAD` == `git rev-parse main` tras crearla | **Sí** — ambos `0ec1231` |
| 6 | Commits propios frente a `main` al crearla | **0** |

```powershell
git switch main
git fetch --prune origin
git pull --ff-only origin main
git status --short                              # vacio
git rev-parse main; git rev-parse origin/main   # 0ec1231 / 0ec1231

git switch -c Task/004.1-Corregir-Backup-Rutas-Literales

git rev-parse HEAD; git rev-parse main          # 0ec1231 / 0ec1231
git rev-list --count main..HEAD                 # 0
```

---

## 1. Objetivo

Corregir un defecto **demostrado en ejecución real** del sistema de respaldo y
recuperación local entregado por `Task/004`:

> Una ruta del sistema de archivos **ya resuelta** se estaba pasando a parámetros de
> PowerShell que **interpretan comodines**. Cuando la ruta contiene `[` o `]`, el cmdlet
> deja de encontrar el archivo, devuelve `$null` y, bajo `Set-StrictMode -Version Latest`,
> el acceso a una propiedad de `$null` aborta el respaldo.

El objetivo no es solo que el respaldo vuelva a terminar, sino que **la verificación y la
prueba de restauración** sigan significando lo que prometen.

## 2. Contexto — cómo apareció

`Task/017` quedó cerrada y normalizada. Como trabajo operativo separado se iba a
regularizar el acceso local a Portainer, y el procedimiento exigía un respaldo previo.
Ese respaldo **falló**:

```
BACKUP FALLIDO: No se encuentra la propiedad 'Hash' en este objeto.
```

El respaldo anterior correcto es del **2026-07-31**. Entre esa fecha y hoy, los tests de
integración del backend dejaron en MinIO objetos cuyas claves contienen `[minio]` y
`[s3]` — los identificadores que genera `pytest` al parametrizar. Esos objetos son el
**detonante**, no la causa.

## 3. Causa raíz

`Get-FileHash -Path`, `Get-Item`, `Test-Path`, `Get-Content`, `Remove-Item`,
`Get-ChildItem`, `Resolve-Path`, `Expand-Archive` y `Out-File -FilePath` tratan su
argumento como **patrón**, no como ruta literal. En PowerShell, `[...]` es una clase de
caracteres.

Comprobación directa sobre el archivo real que rompió el respaldo:

| Llamada | Resultado |
| --- | --- |
| `Test-Path -LiteralPath` | `True` — el archivo existe |
| `Get-FileHash -Path` | **`$null`** |
| `Get-FileHash -LiteralPath` | funciona |

`Set-StrictMode -Version Latest` convierte el `$null.Hash` resultante en un error
terminante. Sin StrictMode el fallo habría sido **silencioso**, que es peor.

## 4. Alcance

Auditar los cinco scripts de `scripts/backup/` y consumir como **literal** toda ruta ya
resuelta. **No** se tocan los comodines deliberados.

- `scripts/backup/_BackupCommon.ps1`
- `scripts/backup/New-LocalBackup.ps1`
- `scripts/backup/Test-LocalBackup.ps1`
- `scripts/backup/Restore-LocalBackupTest.ps1`
- `scripts/backup/Remove-RecoveryTestResources.ps1`

### Fuera de alcance

- **No** se eliminan los buckets `personal-blog-test-*`. Son un hallazgo separado de
  higiene de los tests de integración y, además, el escenario real de regresión de esta
  corrección.
- **No** se resetea Portainer. Es el trabajo operativo que quedó en espera.
- **No** se modifica el roadmap ni el avance.

## 5. Criterio de éxito

| # | Criterio |
| --- | --- |
| 1 | Prueba RED que reproduce el defecto de comodines |
| 2 | Corrección con semántica literal donde corresponde |
| 3 | Pruebas dirigidas en verde |
| 4 | `New-LocalBackup.ps1` completa un respaldo real **con los buckets actuales intactos** |
| 5 | El conjunto nuevo contiene manifiesto, checksums y Portainer |
| 6 | `Test-LocalBackup.ps1` pasa |
| 7 | `Restore-LocalBackupTest.ps1` pasa en entorno temporal aislado |
| 8 | Los volúmenes principales permanecen intactos |
| 9 | El conjunto fallido `20260907-014623` queda eliminado **después** de lo anterior |
| 10 | Git no contiene secretos |
| 11 | Sin commit, push ni PR **mientras la tarea estuviera pendiente de aprobación** |

## 6. Límites

- No se ejecuta `docker compose down`, `down -v`, `volume rm` ni `system prune`.
- La prueba de restauración usa exclusivamente los recursos `personal-blog-recovery-*`.
- Ningún cambio se promueve a Aceptada o Vigente por decisión propia.
