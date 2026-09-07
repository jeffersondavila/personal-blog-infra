<#
.SYNOPSIS
    Verifica la integridad de un conjunto de respaldo mediante checksums SHA-256.

.DESCRIPTION
    Comprueba, sin restaurar nada y sin tocar Docker:

      - Que el conjunto existe y contiene manifest.json y checksums.sha256.
      - Que cada archivo listado existe.
      - Que su SHA-256 coincide con el registrado.
      - Que no hay archivos en el conjunto que falten en checksums.sha256.

    Un backup cuya integridad no se ha comprobado no cuenta como backup.

.PARAMETER BackupSet
    Identificador del conjunto (por ejemplo `20260731-143000`) o ruta completa.
    Si se omite, se verifica el conjunto mas reciente.

.PARAMETER BackupRoot
    Directorio raiz de los backups. Por defecto `local-backups/`.

.PARAMETER All
    Verifica todos los conjuntos existentes.

.EXAMPLE
    .\Test-LocalBackup.ps1

.EXAMPLE
    .\Test-LocalBackup.ps1 -BackupSet 20260731-143000

.EXAMPLE
    .\Test-LocalBackup.ps1 -All

.NOTES
    Task/004-Backups-y-Recuperacion-Local
#>
[CmdletBinding()]
param(
    [string]$BackupSet,
    [string]$BackupRoot,
    [switch]$All
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '_BackupCommon.ps1')

function Test-OneBackupSet {
    param([Parameter(Mandatory)][string]$Path)

    Write-Step "Verificando $(Split-Path $Path -Leaf)"

    $manifestPath = Join-Path $Path 'manifest.json'
    $checksumPath = Join-Path $Path 'checksums.sha256'

    if (-not (Test-Path -LiteralPath $manifestPath)) {
        Write-Host "    FALLO  falta manifest.json" -ForegroundColor Red
        return $false
    }
    Write-Ok 'manifest.json presente'

    if (-not (Test-Path -LiteralPath $checksumPath)) {
        Write-Host "    FALLO  falta checksums.sha256" -ForegroundColor Red
        return $false
    }
    Write-Ok 'checksums.sha256 presente'

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    Write-Info "Creado (UTC): $($manifest.createdAtUtc)"
    Write-Info "Docker $($manifest.dockerVersion) / Compose $($manifest.composeVersion)"

    $ok = $true
    $checked = @()

    foreach ($line in (Get-Content -LiteralPath $checksumPath)) {
        $trimmed = $line.Trim()
        if ($trimmed.Length -eq 0) { continue }

        $parts = $trimmed -split '\s+', 2
        if ($parts.Count -ne 2) {
            Write-Host "    FALLO  linea mal formada: $trimmed" -ForegroundColor Red
            $ok = $false
            continue
        }

        $expected = $parts[0].ToLower()
        $relative = $parts[1].Trim()
        $checked += $relative
        $filePath = Join-Path $Path ($relative -replace '/', '\')

        if (-not (Test-Path -LiteralPath $filePath)) {
            Write-Host "    FALLO  no existe: $relative" -ForegroundColor Red
            $ok = $false
            continue
        }

        $actual = Get-Sha256 -Path $filePath
        $size = Format-Size (Get-FileSizeBytes -Path $filePath)

        if ($actual -eq $expected) {
            Write-Ok "$relative ($size)"
        }
        else {
            Write-Host "    FALLO  checksum distinto en $relative" -ForegroundColor Red
            Write-Host "           esperado: $expected" -ForegroundColor DarkGray
            Write-Host "           obtenido: $actual" -ForegroundColor DarkGray
            $ok = $false
        }
    }

    # Archivos presentes en el conjunto que nadie declaro: senal de que el
    # conjunto se manipulo despues de crearse.
    $known = @('manifest.json', 'checksums.sha256')
    # `@()` es obligatorio: con Set-StrictMode, un Where-Object sin resultados
    # devuelve $null y consultar .Count sobre $null aborta el script.
    $present = @(Get-ChildItem -LiteralPath $Path -Recurse -File | ForEach-Object {
        $_.FullName.Substring($Path.Length).TrimStart('\') -replace '\\', '/'
    })
    $unlisted = @($present | Where-Object { $known -notcontains $_ -and $checked -notcontains $_ })
    if ($unlisted.Count -gt 0) {
        foreach ($u in $unlisted) {
            Write-Warn "archivo no declarado en checksums.sha256: $u"
        }
        $ok = $false
    }

    if ($ok) {
        Write-Host "    INTEGRIDAD CORRECTA - $($checked.Count) archivos" -ForegroundColor Green
    }
    else {
        Write-Host "    INTEGRIDAD COMPROMETIDA" -ForegroundColor Red
    }
    return $ok
}

try {
    Write-Host '=== Verificacion de integridad de backups - Task/004 ===' -ForegroundColor White

    $root = Get-BackupRoot -Root $BackupRoot
    Write-Info "Raiz de backups: $root"

    $sets = @()

    if ($All) {
        $sets = @(Get-ChildItem -LiteralPath $root -Directory | Sort-Object Name)
        if ($sets.Count -eq 0) { Stop-WithError "No hay ningun conjunto de respaldo en $root." }
    }
    elseif ($BackupSet) {
        $candidate = if (Test-Path -LiteralPath $BackupSet) { $BackupSet } else { Join-Path $root $BackupSet }
        if (-not (Test-Path -LiteralPath $candidate)) { Stop-WithError "No existe el conjunto '$BackupSet'." }
        $sets = @(Get-Item -LiteralPath $candidate)
    }
    else {
        $latest = Get-ChildItem -LiteralPath $root -Directory | Sort-Object Name -Descending | Select-Object -First 1
        if ($null -eq $latest) { Stop-WithError "No hay ningun conjunto de respaldo en $root. Ejecuta New-LocalBackup.ps1 primero." }
        $sets = @($latest)
        Write-Info "Conjunto mas reciente: $($latest.Name)"
    }

    $failed = 0
    foreach ($set in $sets) {
        if (-not (Test-OneBackupSet -Path $set.FullName)) { $failed++ }
    }

    Write-Step 'Resumen'
    Write-Host "    Conjuntos verificados : $($sets.Count)"
    Write-Host "    Con problemas         : $failed"

    if ($failed -gt 0) { exit 1 }
    Write-Host ''
    Write-Host '    Todos los conjuntos verificados son integros.' -ForegroundColor Green
}
catch {
    Write-Host ''
    Write-Host "VERIFICACION FALLIDA: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
