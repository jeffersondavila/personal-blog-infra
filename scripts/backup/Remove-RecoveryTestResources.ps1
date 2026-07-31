<#
.SYNOPSIS
    Elimina UNICAMENTE los recursos temporales de las pruebas de restauracion.

.DESCRIPTION
    Busca contenedores, volumenes y redes cuyo nombre empiece por
    `personal-blog-recovery` y los elimina.

    Antes de eliminar cada recurso, comprueba dos condiciones:

      1. Que NO pertenece al entorno principal (`personal-blog-local*`).
      2. Que SI lleva el prefijo de los recursos temporales.

    Si alguna falla, la operacion se aborta. Un error de tipeo no puede acabar
    borrando la base de datos real.

    Al terminar verifica que los tres volumenes principales siguen existiendo.

.PARAMETER Force
    No pide confirmacion.

.PARAMETER WhatIf
    Muestra que se eliminaria, sin eliminar nada.

.EXAMPLE
    .\Remove-RecoveryTestResources.ps1 -WhatIf

.EXAMPLE
    .\Remove-RecoveryTestResources.ps1 -Force

.NOTES
    Task/004-Backups-y-Recuperacion-Local

    Este script NUNCA elimina:
      - personal-blog-local_postgres_data
      - personal-blog-local_minio_data
      - personal-blog-local_portainer_data
      - Ningun contenedor del entorno principal.

    Tampoco ejecuta `docker compose down -v`, `docker system prune` ni
    `docker volume prune`.
#>
[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$WhatIf
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '_BackupCommon.ps1')

try {
    Write-Host '=== Limpieza de recursos temporales de prueba - Task/004 ===' -ForegroundColor White

    Assert-Dependencies | Out-Null

    $prefix = $script:RecoveryPrefix

    # --- Inventario ---------------------------------------------------------
    Write-Step "Buscando recursos con prefijo '$prefix'"

    $containers = @(docker ps -a --filter "name=$prefix" --format '{{.Names}}' | Where-Object { $_ })
    $volumes    = @(docker volume ls --filter "name=$prefix" --format '{{.Name}}' | Where-Object { $_ })
    $networks   = @(docker network ls --filter "name=$prefix" --format '{{.Name}}' | Where-Object { $_ })

    Write-Info "Contenedores: $($containers.Count)"
    foreach ($c in $containers) { Write-Info "  - $c" }
    Write-Info "Volumenes: $($volumes.Count)"
    foreach ($v in $volumes) { Write-Info "  - $v" }
    Write-Info "Redes: $($networks.Count)"
    foreach ($n in $networks) { Write-Info "  - $n" }

    if ($containers.Count -eq 0 -and $volumes.Count -eq 0 -and $networks.Count -eq 0) {
        Write-Ok 'No hay recursos temporales que eliminar'
        return
    }

    # --- Guarda previa sobre TODO el inventario -----------------------------
    # Se valida el conjunto completo antes de borrar nada: si un solo recurso
    # no supera la comprobacion, no se elimina ninguno.
    Write-Step 'Comprobando que ningun recurso pertenece al entorno principal'
    foreach ($name in ($containers + $volumes + $networks)) {
        Assert-SafeToRemove -Name $name
    }
    Write-Ok 'Todos los recursos son temporales y se pueden eliminar'

    if ($WhatIf) {
        Write-Step 'WhatIf: no se elimino nada'
        return
    }

    if (-not $Force) {
        $answer = Read-Host "Eliminar $($containers.Count) contenedores, $($volumes.Count) volumenes y $($networks.Count) redes temporales? (s/N)"
        if ($answer -ne 's' -and $answer -ne 'S') {
            Write-Warn 'Cancelado por el usuario'
            return
        }
    }

    # --- Eliminacion --------------------------------------------------------
    Write-Step 'Eliminando recursos temporales'

    foreach ($c in $containers) {
        Assert-SafeToRemove -Name $c
        docker rm -f $c | Out-Null
        Write-Ok "contenedor $c"
    }

    foreach ($v in $volumes) {
        Assert-SafeToRemove -Name $v
        docker volume rm $v | Out-Null
        if ($LASTEXITCODE -eq 0) { Write-Ok "volumen $v" }
        else { Write-Warn "no se pudo eliminar el volumen $v (puede estar en uso)" }
    }

    foreach ($n in $networks) {
        Assert-SafeToRemove -Name $n
        docker network rm $n | Out-Null
        if ($LASTEXITCODE -eq 0) { Write-Ok "red $n" }
        else { Write-Warn "no se pudo eliminar la red $n (puede estar en uso)" }
    }

    # --- Verificacion final -------------------------------------------------
    Write-Step 'Comprobando que el entorno principal sigue intacto'
    Assert-MainEnvironmentIntact | Out-Null
    foreach ($v in $script:MainVolumes) { Write-Ok "volumen principal presente: $v" }

    $mainRunning = @(docker ps --filter "name=$($script:MainProjectPrefix)" --format '{{.Names}}' | Where-Object { $_ })
    Write-Info "Contenedores principales en marcha: $($mainRunning.Count)"
    foreach ($c in $mainRunning) { Write-Info "  - $c" }

    Write-Host ''
    Write-Host '    Limpieza completada. El entorno principal no fue tocado.' -ForegroundColor Green
}
catch {
    Write-Host ''
    Write-Host "LIMPIEZA FALLIDA: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
