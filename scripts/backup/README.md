# scripts/backup

Scripts de respaldo, verificación y recuperación del entorno local.

Producidos por `Task/004-Backups-y-Recuperacion-Local`. El procedimiento completo, con
sus explicaciones y la recuperación paso a paso, está en
[docs/runbooks/local-backup-and-recovery.md](../../docs/runbooks/local-backup-and-recovery.md).

---

## Scripts

| Script | Qué hace |
| --- | --- |
| [`New-LocalBackup.ps1`](New-LocalBackup.ps1) | Crea un conjunto de respaldo completo con manifiesto y checksums. |
| [`Test-LocalBackup.ps1`](Test-LocalBackup.ps1) | Verifica la integridad de un conjunto mediante SHA-256. |
| [`Restore-LocalBackupTest.ps1`](Restore-LocalBackupTest.ps1) | Restaura en un entorno temporal aislado y comprueba los datos. |
| [`Remove-RecoveryTestResources.ps1`](Remove-RecoveryTestResources.ps1) | Elimina **solo** los recursos temporales de prueba. |
| `_BackupCommon.ps1` | Funciones compartidas. No se ejecuta directamente. |

Todos aceptan `Get-Help`:

```powershell
Get-Help .\New-LocalBackup.ps1 -Full
```

---

## Uso habitual

```powershell
cd scripts\backup

.\New-LocalBackup.ps1              # 1. crear el backup
.\Test-LocalBackup.ps1             # 2. verificar su integridad
.\Restore-LocalBackupTest.ps1      # 3. probar que se puede restaurar
```

El tercer paso crea un entorno temporal, lo verifica y lo elimina automáticamente.

---

## Qué se respalda en MinIO

| Elemento | ¿Se respalda? | ¿Se restaura? | ¿Se verifica? |
| --- | :---: | :---: | :---: |
| Contenido del objeto | Sí | Sí | SHA-256 del contenido |
| Metadatos (`Content-Type`, `Cache-Control`, `Content-Disposition`, `Content-Encoding`, `Content-Language`, `x-amz-meta-*`) | Sí | Sí | Comparación exacta |
| Tags del objeto | Sí | Sí | Comparación exacta |
| Configuración del bucket | Se **registra** | **No** | No |
| Historial de versiones | **No** | **No** | No |

> **`mc mirror` hacia un sistema de archivos copia el contenido, no los metadatos S3.**
> `--preserve` preserva atributos del sistema de archivos, no los metadatos ni los tags.
> Por eso se inventarían aparte con `mc stat --json` y `mc tag list --json`, y se
> reaplican explícitamente al restaurar con `mc cp --attr` y `mc tag set`.

**El script no ignora lo que no sabe copiar.** Si algún bucket usa versionado, Object
Lock, replicación, ciclo de vida, política anónima o cifrado, `New-LocalBackup.ps1`
**aborta** nombrando la causa. Con `-AllowPartial` genera el conjunto marcándolo como
`PARCIAL` en el manifiesto.

---

## Garantías de seguridad

Estos scripts **nunca** tocan el entorno principal salvo para leerlo. En concreto:

- **No ejecutan** `docker compose down -v`, `docker system prune` ni `docker volume prune`.
- **No eliminan** ningún recurso cuyo nombre empiece por `personal-blog-local`.
- Solo eliminan recursos cuyo nombre empiece por `personal-blog-recovery`.
- La guarda `Assert-SafeToRemove` valida **ambas** condiciones antes de cada borrado y
  aborta la operación completa si alguna falla.
- Tras cada operación comprueban que los tres volúmenes principales siguen existiendo.

La única excepción es **Portainer**, que se detiene durante el respaldo de su volumen y se
vuelve a arrancar inmediatamente después, incluso si la copia falla. PostgreSQL y MinIO no
se detienen nunca.

---

## Secretos

- Ningún script contiene credenciales.
- Las credenciales del entorno principal se leen de `.env` y **nunca se imprimen**: se
  pasan a los contenedores como variables de entorno, no por línea de comandos.
- Las credenciales del entorno temporal se **generan al vuelo**, no se imprimen y no se
  guardan.
- El manifiesto **no registra contraseñas ni tokens**.

Los artefactos generados en `local-backups/` **sí son sensibles**: están ignorados por Git
y no deben versionarse ni compartirse. Ver la sección 3.1 del runbook.

---

## Convenciones

- PowerShell, porque el entorno de desarrollo es Windows con Docker Desktop.
- Codificación **UTF-8 con BOM**: sin BOM, PowerShell 5.1 interpreta el archivo como ANSI
  y cualquier carácter no ASCII rompe el análisis sintáctico.
- Solo caracteres ASCII en el código y en los mensajes de consola.
- Fin de línea CRLF y sangría de 4 espacios, según [`.editorconfig`](../../.editorconfig).
- `Set-StrictMode -Version Latest` y `$ErrorActionPreference = 'Stop'` en todos ellos.
