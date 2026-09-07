<#
.SYNOPSIS
    Regresion: las rutas ya resueltas se consumen como LITERALES.

.DESCRIPTION
    Task/004.1-Corregir-Backup-Rutas-Literales.

    `New-LocalBackup.ps1` fallo con un backup real:

        BACKUP FALLIDO: No se encuentra la propiedad 'Hash' en este objeto.

    La causa NO era MinIO ni Get-FileHash: era pasar una ruta CONCRETA del
    filesystem a un parametro que interpreta comodines. En PowerShell, `-Path`
    trata `[` y `]` como una clase de caracteres. Una clave de objeto como

        pruebas/test_algo[minio]/archivo.bin

    deja de casar consigo misma, el cmdlet devuelve $null y, bajo
    `Set-StrictMode -Version Latest`, `$null.Hash` es un error terminante.

    Estas pruebas recorren las funciones REALES que usa el respaldo, no
    envoltorios creados para la ocasion.

    El andamiaje (crear y borrar el arbol de prueba, calcular el SHA-256
    esperado) usa APIs de .NET a proposito: si usara los mismos cmdlets que
    esta verificando, un fallo podria enmascararse o inventarse.

.EXAMPLE
    .\Test-PathLiteralRegression.ps1
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '_BackupCommon.ps1')

$script:Passed = 0
$script:Failed = 0

# Clave realista: reproduce el nombre que generan los tests parametrizados de
# pytest en el backend y que dejo el escenario que rompio el respaldo.
$script:BracketKey = 'pruebas/test_algo[minio]/archivo.bin'
$script:Payload = [byte[]](0..255)

function Get-ExpectedSha256 {
    param([Parameter(Mandatory)][byte[]]$Bytes)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($Bytes)) -replace '-', '').ToLower()
    } finally {
        $sha.Dispose()
    }
}

function New-Fixture {
    <# Crea un arbol de prueba con .NET y devuelve su raiz. #>
    param([Parameter(Mandatory)][string]$RootName)
    $root = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), $RootName)
    if ([System.IO.Directory]::Exists($root)) { [System.IO.Directory]::Delete($root, $true) }
    $file = [System.IO.Path]::Combine($root, ($script:BracketKey -replace '/', '\'))
    [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($file)) | Out-Null
    [System.IO.File]::WriteAllBytes($file, $script:Payload)
    return [pscustomobject]@{ Root = $root; File = $file }
}

function Remove-Fixture {
    param([Parameter(Mandatory)][string]$Root)
    if ([System.IO.Directory]::Exists($Root)) { [System.IO.Directory]::Delete($Root, $true) }
}

function Invoke-Case {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][scriptblock]$Body
    )
    try {
        & $Body
        $script:Passed++
        Write-Ok $Name
    } catch {
        $script:Failed++
        Write-Host "    FAIL $Name" -ForegroundColor Red
        Write-Host "         $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Assert-Equal {
    param($Expected, $Actual, [Parameter(Mandatory)][string]$What)
    if ($Expected -ne $Actual) {
        throw "$What -- esperado '$Expected', obtenido '$Actual'"
    }
}

Write-Step 'Regresion de rutas literales (Task/004.1)'

$expectedHash = Get-ExpectedSha256 -Bytes $script:Payload
$expectedSize = $script:Payload.Length

# --- 1. Get-Sha256 sobre una ruta con corchetes ----------------------------
# Es la funcion que firma cada artefacto del conjunto de respaldo.
Invoke-Case 'Get-Sha256 trata la ruta con corchetes como literal' {
    $fx = New-Fixture -RootName 'blog-t0041-sha'
    try {
        Assert-Equal -Expected $expectedHash -Actual (Get-Sha256 -Path $fx.File) -What 'SHA-256'
    } finally { Remove-Fixture -Root $fx.Root }
}

# --- 2. Get-FileSizeBytes sobre una ruta con corchetes ---------------------
# Alimenta el tamano declarado en el manifiesto.
Invoke-Case 'Get-FileSizeBytes trata la ruta con corchetes como literal' {
    $fx = New-Fixture -RootName 'blog-t0041-size'
    try {
        Assert-Equal -Expected $expectedSize -Actual (Get-FileSizeBytes -Path $fx.File) -What 'Tamano'
    } finally { Remove-Fixture -Root $fx.Root }
}

# --- 3. Get-FileHashMap: el bucle que fallo en produccion ------------------
# Es el codigo extraido de New-LocalBackup.ps1 (mapa clave -> SHA-256 del
# arbol de objetos de MinIO) y reutilizado por Restore-LocalBackupTest.ps1.
Invoke-Case 'Get-FileHashMap indexa un objeto cuya CLAVE lleva corchetes' {
    $fx = New-Fixture -RootName 'blog-t0041-map'
    try {
        $map = Get-FileHashMap -Root $fx.Root
        Assert-Equal -Expected 1 -Actual $map.Count -What 'Numero de objetos'
        if (-not $map.ContainsKey($script:BracketKey)) {
            throw "La clave '$($script:BracketKey)' no esta en el mapa. Claves: $($map.Keys -join ', ')"
        }
        Assert-Equal -Expected $expectedHash -Actual $map[$script:BracketKey] -What 'SHA-256 del objeto'
    } finally { Remove-Fixture -Root $fx.Root }
}

# --- 4. La RAIZ del arbol lleva corchetes ----------------------------------
# Cubre el caso en que es -BackupRoot, y no la clave, quien los contiene.
Invoke-Case 'Get-FileHashMap acepta una raiz que lleva corchetes' {
    $fx = New-Fixture -RootName 'blog-t0041-[raiz]'
    try {
        $map = Get-FileHashMap -Root $fx.Root
        Assert-Equal -Expected 1 -Actual $map.Count -What 'Numero de objetos'
        Assert-Equal -Expected $expectedHash -Actual $map[$script:BracketKey] -What 'SHA-256 del objeto'
    } finally { Remove-Fixture -Root $fx.Root }
}

# --- 5. Guarda fail-closed sobre la raiz de backups ------------------------
# `Compress-Archive` de Windows PowerShell 5.1 esta roto para rutas con
# metacaracteres: falla igual con -Path que con -LiteralPath. No podemos
# arreglarlo desde aqui, asi que el respaldo debe RECHAZAR esa raiz en vez de
# producir un conjunto que aparenta estar bien.
Invoke-Case 'Assert-NoWildcardInPath rechaza una raiz con metacaracteres' {
    $rejected = $false
    try {
        Assert-NoWildcardInPath -Path 'C:\tmp\local-backups[1]' -What 'La raiz de backups'
    } catch {
        $rejected = $true
    }
    if (-not $rejected) { throw 'La guarda acepto una raiz con corchetes' }

    # Y no debe estorbar en el caso normal.
    Assert-NoWildcardInPath -Path 'C:\Users\quien\Blog_Personal\local-backups' -What 'La raiz de backups'
}

Write-Host ''
if ($script:Failed -gt 0) {
    Write-Host "RESULTADO: $($script:Passed) correcta(s), $($script:Failed) fallida(s)" -ForegroundColor Red
    exit 1
}
Write-Host "RESULTADO: $($script:Passed) correcta(s), 0 fallidas" -ForegroundColor Green
exit 0
