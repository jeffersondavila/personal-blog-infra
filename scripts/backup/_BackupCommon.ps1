# ---------------------------------------------------------------------------
# _BackupCommon.ps1 - Funciones compartidas de respaldo y recuperacion local
#
# Task/004-Backups-y-Recuperacion-Local
#
# Este archivo NO se ejecuta directamente: lo cargan los demas scripts con
# dot-sourcing. No contiene ningun secreto.
# ---------------------------------------------------------------------------

Set-StrictMode -Version Latest

# --- Constantes del entorno principal --------------------------------------
# Todo recurso cuyo nombre empiece por este prefijo pertenece al entorno
# principal y esta PROTEGIDO frente a cualquier operacion de eliminacion.
$script:MainProjectPrefix = 'personal-blog-local'

$script:MainVolumes = @(
    'personal-blog-local_postgres_data',
    'personal-blog-local_minio_data',
    'personal-blog-local_portainer_data'
)

$script:MainContainers = @(
    'personal-blog-local-postgres',
    'personal-blog-local-minio',
    'personal-blog-local-portainer'
)

# Prefijo de los recursos temporales de prueba de restauracion.
$script:RecoveryPrefix = 'personal-blog-recovery'

# Imagen auxiliar para operaciones sobre volumenes (tar, checksums).
$script:HelperImage = 'alpine:3.22'

# --- Salida ----------------------------------------------------------------

function Write-Step {
    param([Parameter(Mandatory)][string]$Message)
    Write-Host ''
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([Parameter(Mandatory)][string]$Message)
    Write-Host "    OK   $Message" -ForegroundColor Green
}

function Write-Info {
    param([Parameter(Mandatory)][string]$Message)
    Write-Host "         $Message" -ForegroundColor Gray
}

function Write-Warn {
    param([Parameter(Mandatory)][string]$Message)
    Write-Host "    AVISO $Message" -ForegroundColor Yellow
}

function Stop-WithError {
    param([Parameter(Mandatory)][string]$Message)
    Write-Host "    ERROR $Message" -ForegroundColor Red
    throw $Message
}

# --- Dependencias ----------------------------------------------------------

function Assert-Dependencies {
    <#
        Falla de forma segura y explicita si falta alguna dependencia, antes
        de tocar nada. Preferimos no empezar a que quede un backup a medias.
    #>
    Write-Step 'Comprobando dependencias'

    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if ($null -eq $docker) {
        Stop-WithError 'No se encontro el comando `docker`. Instala Docker Desktop y vuelve a intentarlo.'
    }

    # Se captura con try/catch en lugar de redirigir stderr: en PowerShell 5.1
    # con $ErrorActionPreference = 'Stop', el stderr de un ejecutable nativo se
    # convierte en excepcion y ocultaria este mensaje de diagnostico.
    $serverVersion = $null
    try { $serverVersion = docker version --format '{{.Server.Version}}' } catch { }
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($serverVersion)) {
        Stop-WithError 'El daemon de Docker no responde. Arranca Docker Desktop y vuelve a intentarlo.'
    }
    Write-Ok "Docker $serverVersion"

    $composeVersion = $null
    try { $composeVersion = docker compose version --short } catch { }
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($composeVersion)) {
        Stop-WithError 'No se encontro `docker compose` v2. Actualiza Docker Desktop.'
    }
    Write-Ok "Docker Compose $composeVersion"

    return [pscustomobject]@{
        Docker  = $serverVersion
        Compose = $composeVersion
    }
}

function Assert-HelperImage {
    <# Descarga la imagen auxiliar solo si no esta presente. #>
    $existing = docker images --quiet $script:HelperImage
    if ([string]::IsNullOrWhiteSpace($existing)) {
        Write-Info "Descargando imagen auxiliar $($script:HelperImage)..."
        docker pull $script:HelperImage | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Stop-WithError "No se pudo descargar la imagen auxiliar $($script:HelperImage)."
        }
    }
    Write-Ok "Imagen auxiliar $($script:HelperImage) disponible"
}

# --- Rutas y configuracion -------------------------------------------------

function Get-RepositoryRoot {
    <# Raiz del repositorio: dos niveles por encima de scripts/backup/. #>
    return (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

function Get-BackupRoot {
    param([string]$Root)
    if ([string]::IsNullOrWhiteSpace($Root)) {
        $Root = Join-Path (Get-RepositoryRoot) 'local-backups'
    }
    if (-not (Test-Path $Root)) {
        New-Item -ItemType Directory -Path $Root -Force | Out-Null
    }
    return (Resolve-Path $Root).Path
}

function Read-DotEnv {
    <#
        Lee el archivo .env del repositorio y devuelve un hashtable.
        Los valores NUNCA se imprimen: quien los use debe pasarlos a Docker
        por variable de entorno, no por linea de comandos ni por consola.
    #>
    $envPath = Join-Path (Get-RepositoryRoot) '.env'
    if (-not (Test-Path $envPath)) {
        Stop-WithError "No existe el archivo .env en la raiz del repositorio. Copialo de .env.example."
    }

    $values = @{}
    foreach ($line in (Get-Content $envPath)) {
        $trimmed = $line.Trim()
        if ($trimmed.Length -eq 0 -or $trimmed.StartsWith('#')) { continue }
        $index = $trimmed.IndexOf('=')
        if ($index -lt 1) { continue }
        $key = $trimmed.Substring(0, $index).Trim()
        $value = $trimmed.Substring($index + 1).Trim()
        $values[$key] = $value
    }

    foreach ($required in @('POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'MINIO_ROOT_USER', 'MINIO_ROOT_PASSWORD')) {
        if (-not $values.ContainsKey($required) -or [string]::IsNullOrWhiteSpace($values[$required])) {
            Stop-WithError "Falta la variable $required en .env."
        }
    }

    return $values
}

# --- Guardas de seguridad --------------------------------------------------

function Test-IsMainResource {
    <# Devuelve $true si el nombre pertenece al entorno principal. #>
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Name)

    if ([string]::IsNullOrWhiteSpace($Name)) { return $false }
    if ($script:MainVolumes -contains $Name) { return $true }
    if ($script:MainContainers -contains $Name) { return $true }
    return $Name.StartsWith($script:MainProjectPrefix)
}

function Assert-SafeToRemove {
    <#
        GUARDA CRITICA. Se invoca antes de CUALQUIER eliminacion.

        Rechaza todo recurso que pertenezca al entorno principal y exige que
        el nombre lleve el prefijo de los recursos temporales de prueba. Un
        error de tipeo no puede acabar borrando la base de datos real.
    #>
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Name)

    if (Test-IsMainResource -Name $Name) {
        Stop-WithError "OPERACION BLOQUEADA: '$Name' pertenece al entorno principal y no se elimina nunca desde estos scripts."
    }

    if (-not $Name.StartsWith($script:RecoveryPrefix)) {
        Stop-WithError "OPERACION BLOQUEADA: '$Name' no lleva el prefijo '$($script:RecoveryPrefix)' de los recursos temporales. Solo se eliminan recursos de prueba."
    }
}

function Assert-MainEnvironmentIntact {
    <# Comprueba que los tres volumenes principales siguen existiendo. #>
    $missing = @()
    foreach ($volume in $script:MainVolumes) {
        if (-not (Test-VolumeExists -Name $volume)) { $missing += $volume }
    }
    if ($missing.Count -gt 0) {
        Stop-WithError "FALTAN VOLUMENES DEL ENTORNO PRINCIPAL: $($missing -join ', '). Detente y revisa antes de continuar."
    }
    return $true
}

# --- Existencia de recursos ------------------------------------------------
#
# Se consulta con `--filter`, no con `inspect`: `inspect` escribe en stderr
# cuando el recurso no existe y, con $ErrorActionPreference = 'Stop', eso
# aborta el script aunque la ausencia sea el resultado esperado.

function Test-ContainerExists {
    param([Parameter(Mandatory)][string]$Name)
    $found = docker ps -a --filter "name=^$([regex]::Escape($Name))$" --format '{{.Names}}'
    return (@($found | Where-Object { $_ -eq $Name }).Count -gt 0)
}

function Test-VolumeExists {
    param([Parameter(Mandatory)][string]$Name)
    $found = docker volume ls --filter "name=^$([regex]::Escape($Name))$" --format '{{.Name}}'
    return (@($found | Where-Object { $_ -eq $Name }).Count -gt 0)
}

function Test-NetworkExists {
    param([Parameter(Mandatory)][string]$Name)
    $found = docker network ls --filter "name=^$([regex]::Escape($Name))$" --format '{{.Name}}'
    return (@($found | Where-Object { $_ -eq $Name }).Count -gt 0)
}

function Remove-ContainerIfExists {
    <#
        Elimina un contenedor solo si existe, tras pasar la guarda de
        seguridad. Nunca toca contenedores del entorno principal.
    #>
    param([Parameter(Mandatory)][string]$Name)
    if (Test-ContainerExists -Name $Name) {
        Assert-SafeToRemove -Name $Name
        docker rm -f $Name | Out-Null
    }
}

# --- MinIO -----------------------------------------------------------------

function Invoke-McJson {
    <#
        Ejecuta `mc` dentro de un contenedor y devuelve los objetos JSON de su
        salida, una entrada por linea. `mc` emite JSON Lines, no un array.

        Devuelve una coleccion vacia si el comando falla: varias consultas de
        configuracion (ciclo de vida, retencion) responden con error cuando la
        configuracion simplemente no existe, y eso no es un fallo.
    #>
    param(
        [Parameter(Mandatory)][string]$Container,
        [Parameter(Mandatory)][string[]]$McArgs
    )

    $raw = docker exec $Container mc @McArgs
    $parsed = @()
    foreach ($line in @($raw)) {
        $text = "$line".Trim()
        if ($text.Length -eq 0) { continue }
        try { $parsed += ($text | ConvertFrom-Json) } catch { continue }
    }
    return $parsed
}

function Test-HasProperty {
    <#
        Con Set-StrictMode, leer una propiedad ausente aborta el script. Las
        respuestas de `mc` omiten campos segun el caso (`tagset` no aparece si
        el objeto no tiene tags), asi que hay que comprobar antes de leer.
    #>
    param(
        [Parameter(Mandatory)][AllowNull()]$InputObject,
        [Parameter(Mandatory)][string]$Name
    )
    if ($null -eq $InputObject) { return $false }
    return (@($InputObject.PSObject.Properties.Name) -contains $Name)
}

function Get-PropertyOrDefault {
    <# Lee una propiedad si existe; si no, devuelve el valor por defecto. #>
    param(
        [Parameter(Mandatory)][AllowNull()]$InputObject,
        [Parameter(Mandatory)][string]$Name,
        $Default = $null
    )
    if (Test-HasProperty -InputObject $InputObject -Name $Name) {
        return $InputObject.$Name
    }
    return $Default
}

function Get-McMetadataValue {
    <#
        Lee una clave del bloque `metadata` de `mc stat --json`, sin distinguir
        mayusculas: MinIO devuelve los encabezados normalizados en formato
        `Content-Type` o `X-Amz-Meta-Task` segun el caso.
    #>
    param(
        [Parameter(Mandatory)][AllowNull()]$Metadata,
        [Parameter(Mandatory)][string]$Name
    )
    if ($null -eq $Metadata) { return $null }
    foreach ($property in $Metadata.PSObject.Properties) {
        if ($property.Name -ieq $Name) { return $property.Value }
    }
    return $null
}

# Encabezados que `mc cp --attr` puede reaplicar al restaurar.
$script:RestorableHeaders = @(
    'Content-Type',
    'Cache-Control',
    'Content-Disposition',
    'Content-Encoding',
    'Content-Language'
)

# Metadatos DERIVADOS: MinIO los calcula solo y no se reaplican ni se comparan.
# `X-Amz-Tagging-Count` refleja el numero de tags, que se verifica aparte.
$script:DerivedMetadataKeys = @(
    'X-Amz-Tagging-Count'
)

# --- Utilidades ------------------------------------------------------------

function Get-Sha256 {
    param([Parameter(Mandatory)][string]$Path)
    return (Get-FileHash -Path $Path -Algorithm SHA256).Hash.ToLower()
}

function Get-FileSizeBytes {
    param([Parameter(Mandatory)][string]$Path)
    return (Get-Item $Path).Length
}

function Format-Size {
    param([Parameter(Mandatory)][long]$Bytes)
    if ($Bytes -ge 1MB) { return ('{0:N2} MB' -f ($Bytes / 1MB)) }
    if ($Bytes -ge 1KB) { return ('{0:N2} KB' -f ($Bytes / 1KB)) }
    return "$Bytes B"
}

function Get-UtcTimestamp {
    return (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
}

function Get-BackupSetId {
    return (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
}

function Invoke-DockerOrFail {
    <# Ejecuta docker y falla con un mensaje claro si el codigo no es 0. #>
    param(
        [Parameter(Mandatory)][string[]]$DockerArgs,
        [Parameter(Mandatory)][string]$ErrorMessage
    )
    $output = & docker @DockerArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host ($output | Out-String) -ForegroundColor DarkGray
        Stop-WithError $ErrorMessage
    }
    return $output
}
