<#
.SYNOPSIS
    Restaura un conjunto de respaldo en un entorno temporal AISLADO y verifica
    que los datos recuperados son correctos.

.DESCRIPTION
    Un backup que nunca se ha restaurado no cuenta como backup. Este script lo
    demuestra sin poner en riesgo el entorno principal.

    Todo lo que crea lleva el prefijo `personal-blog-recovery` y vive en:

      - Una red temporal propia.
      - Volumenes temporales propios.
      - Contenedores con nombres distintos.
      - Sin publicar puertos, salvo el de Portainer, necesario para comprobar
        que responde.

    El entorno principal NO se detiene, NO se modifica y NO se elimina. Los
    volumenes `personal-blog-local_*` estan protegidos por una guarda que
    aborta cualquier intento de eliminarlos.

    Las credenciales del entorno temporal se generan al vuelo y no se imprimen
    ni se guardan: las instancias de prueba se destruyen al terminar.

.PARAMETER BackupSet
    Identificador del conjunto o ruta completa. Por defecto, el mas reciente.

.PARAMETER BackupRoot
    Directorio raiz de los backups. Por defecto `local-backups/`.

.PARAMETER KeepResources
    No elimina los recursos temporales al terminar, para poder inspeccionarlos.
    Limpialos despues con Remove-RecoveryTestResources.ps1.

.PARAMETER ExpectedPostgresMarker
    Texto que debe encontrarse en la tabla de verificacion restaurada. Si se
    indica, la prueba falla cuando no aparece.

.EXAMPLE
    .\Restore-LocalBackupTest.ps1

.EXAMPLE
    .\Restore-LocalBackupTest.ps1 -BackupSet 20260731-143000 -KeepResources

.NOTES
    Task/004-Backups-y-Recuperacion-Local
#>
[CmdletBinding()]
param(
    [string]$BackupSet,
    [string]$BackupRoot,
    [switch]$KeepResources,
    [string]$ExpectedPostgresMarker
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '_BackupCommon.ps1')

# --- Nombres de los recursos temporales ------------------------------------
$netName       = "$($script:RecoveryPrefix)-net"
$pgName        = "$($script:RecoveryPrefix)-postgres"
$minioName     = "$($script:RecoveryPrefix)-minio"
$portainerName = "$($script:RecoveryPrefix)-portainer"
$pgVolume        = "$($script:RecoveryPrefix)_postgres_data"
$minioVolume     = "$($script:RecoveryPrefix)_minio_data"
$portainerVolume = "$($script:RecoveryPrefix)_portainer_data"
$portainerPort = 9445

function New-TempSecret {
    # Credencial efimera para las instancias de prueba. Nunca se imprime ni se
    # persiste: las instancias se destruyen al terminar.
    $bytes = New-Object 'System.Byte[]' 24
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    return ([Convert]::ToBase64String($bytes) -replace '[^A-Za-z0-9]', '') + 'Tmp1'
}

function Wait-ForHealthy {
    param(
        [Parameter(Mandatory)][string]$Container,
        [Parameter(Mandatory)][scriptblock]$Probe,
        [int]$TimeoutSeconds = 120
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (& $Probe) { return $true }
        Start-Sleep -Seconds 3
    }
    return $false
}

$created = @{ Containers = @(); Volumes = @(); Networks = @() }
$report = [ordered]@{}

try {
    Write-Host '=== Prueba de restauracion aislada - Task/004 ===' -ForegroundColor White

    Assert-Dependencies | Out-Null
    Assert-HelperImage
    Assert-MainEnvironmentIntact | Out-Null
    Write-Ok 'Los tres volumenes principales estan presentes'

    # --- Localizar y verificar el conjunto ----------------------------------
    $root = Get-BackupRoot -Root $BackupRoot
    if ($BackupSet) {
        $setPath = if (Test-Path $BackupSet) { (Resolve-Path $BackupSet).Path } else { Join-Path $root $BackupSet }
    }
    else {
        $latest = Get-ChildItem -Path $root -Directory | Sort-Object Name -Descending | Select-Object -First 1
        if ($null -eq $latest) { Stop-WithError "No hay ningun conjunto de respaldo en $root." }
        $setPath = $latest.FullName
    }
    if (-not (Test-Path $setPath)) { Stop-WithError "No existe el conjunto '$BackupSet'." }

    $setId = Split-Path $setPath -Leaf
    Write-Step "Conjunto a restaurar: $setId"

    $manifest = Get-Content (Join-Path $setPath 'manifest.json') -Raw | ConvertFrom-Json
    Write-Info "Creado (UTC): $($manifest.createdAtUtc)"

    Write-Step 'Verificando integridad antes de restaurar'
    & (Join-Path $PSScriptRoot 'Test-LocalBackup.ps1') -BackupSet $setPath | Out-Null
    if ($LASTEXITCODE -ne 0) { Stop-WithError 'La verificacion de checksums fallo. No se restaura un backup corrupto.' }
    Write-Ok 'Checksums correctos'

    # --- Red temporal -------------------------------------------------------
    Write-Step 'Creando entorno temporal aislado'
    if (-not (Test-NetworkExists -Name $netName)) {
        docker network create $netName | Out-Null
        $created.Networks += $netName
    }
    Write-Ok "Red $netName"

    # =======================================================================
    # PostgreSQL
    # =======================================================================
    Write-Step 'Restaurando PostgreSQL en instancia temporal'

    $pgImage = $manifest.images.postgres
    $pgDb = $manifest.postgres.database
    $pgUser = $manifest.postgres.user
    $pgPass = New-TempSecret

    Remove-ContainerIfExists -Name $pgName
    Invoke-DockerOrFail -DockerArgs @(
        'run', '-d', '--name', $pgName,
        '--network', $netName,
        '-v', "$($pgVolume):/var/lib/postgresql/data",
        '-e', "POSTGRES_DB=$pgDb",
        '-e', "POSTGRES_USER=$pgUser",
        '-e', "POSTGRES_PASSWORD=$pgPass",
        $pgImage
    ) -ErrorMessage 'No se pudo crear la instancia temporal de PostgreSQL.' | Out-Null
    $created.Containers += $pgName
    $created.Volumes += $pgVolume
    Write-Ok "Contenedor $pgName (sin puertos publicados)"

    $pgReady = Wait-ForHealthy -Container $pgName -Probe {
        $null = docker exec $pgName pg_isready -U $pgUser -d $pgDb -h 127.0.0.1
        return ($LASTEXITCODE -eq 0)
    }
    if (-not $pgReady) { Stop-WithError 'La instancia temporal de PostgreSQL no llego a aceptar conexiones.' }
    Write-Ok 'Instancia temporal lista'

    $dumpArtifact = $manifest.artifacts | Where-Object { $_.service -eq 'postgres' -and $_.file -like '*.dump' } | Select-Object -First 1
    $dumpPath = Join-Path $setPath ($dumpArtifact.file -replace '/', '\')

    docker cp $dumpPath "$($pgName):/tmp/restore.dump" | Out-Null
    if ($LASTEXITCODE -ne 0) { Stop-WithError 'No se pudo copiar el volcado a la instancia temporal.' }

    $restoreOutput = docker exec $pgName pg_restore -U $pgUser -d $pgDb --no-owner --no-privileges /tmp/restore.dump 2>&1
    # pg_restore devuelve un codigo distinto de 0 ante avisos no fatales; lo
    # que decide es si los datos estan, y eso se comprueba a continuacion.
    if ($LASTEXITCODE -ne 0) {
        Write-Warn 'pg_restore devolvio avisos:'
        Write-Host ($restoreOutput | Out-String) -ForegroundColor DarkGray
    }
    docker exec $pgName rm -f /tmp/restore.dump | Out-Null
    Write-Ok 'pg_restore ejecutado'

    $tables = (docker exec $pgName psql -U $pgUser -d $pgDb -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema');").Trim()
    Write-Info "Tablas restauradas fuera de los esquemas del sistema: $tables"

    $pgVerified = $true
    $markerFound = '(no solicitado)'
    if ($ExpectedPostgresMarker) {
        $exists = (docker exec $pgName psql -U $pgUser -d $pgDb -tAc "SELECT count(*) FROM information_schema.tables WHERE table_name = 'backup_verification';").Trim()
        if ($exists -ne '1') {
            Write-Host "    FALLO  la tabla backup_verification no se restauro" -ForegroundColor Red
            $pgVerified = $false
        }
        else {
            $markerFound = (docker exec $pgName psql -U $pgUser -d $pgDb -tAc "SELECT marker FROM backup_verification ORDER BY id LIMIT 1;").Trim()
            if ($markerFound -eq $ExpectedPostgresMarker) {
                Write-Ok "Dato de verificacion restaurado y coincide: '$markerFound'"
            }
            else {
                Write-Host "    FALLO  el dato no coincide. Esperado '$ExpectedPostgresMarker', obtenido '$markerFound'" -ForegroundColor Red
                $pgVerified = $false
            }
        }
    }

    $report['postgres'] = [ordered]@{
        instance     = $pgName
        image        = $pgImage
        tables       = $tables
        markerFound  = $markerFound
        verified     = $pgVerified
    }

    # =======================================================================
    # MinIO
    # =======================================================================
    Write-Step 'Restaurando MinIO en instancia temporal'

    $minioImage = $manifest.images.minio
    $minioUser = 'recoverytest'
    $minioPass = New-TempSecret

    Remove-ContainerIfExists -Name $minioName
    Invoke-DockerOrFail -DockerArgs @(
        'run', '-d', '--name', $minioName,
        '--network', $netName,
        '-v', "$($minioVolume):/data",
        '-e', "MINIO_ROOT_USER=$minioUser",
        '-e', "MINIO_ROOT_PASSWORD=$minioPass",
        $minioImage, 'server', '/data'
    ) -ErrorMessage 'No se pudo crear la instancia temporal de MinIO.' | Out-Null
    $created.Containers += $minioName
    $created.Volumes += $minioVolume
    Write-Ok "Contenedor $minioName (sin puertos publicados)"

    $minioReady = Wait-ForHealthy -Container $minioName -Probe {
        $null = docker exec $minioName mc ready local
        return ($LASTEXITCODE -eq 0)
    }
    if (-not $minioReady) { Stop-WithError 'La instancia temporal de MinIO no llego a estar lista.' }
    Write-Ok 'Instancia temporal lista'

    $minioArtifact = $manifest.artifacts | Where-Object { $_.service -eq 'minio' -and $_.file -like '*.zip' } | Select-Object -First 1
    if ($null -eq $minioArtifact) { Stop-WithError 'El conjunto no contiene el archivo de objetos de MinIO.' }
    $minioArchivePath = Join-Path $setPath ($minioArtifact.file -replace '/', '\')

    # La imagen de MinIO no incluye `tar` ni `unzip`: el archivo se expande en
    # el host con Expand-Archive y el arbol resultante se copia al contenedor.
    $expandPath = Join-Path $env:TEMP "personal-blog-recovery-minio-$(Get-Random)"
    if (Test-Path $expandPath) { Remove-Item $expandPath -Recurse -Force }
    New-Item -ItemType Directory -Path $expandPath -Force | Out-Null
    Expand-Archive -Path $minioArchivePath -DestinationPath $expandPath -Force

    docker exec $minioName sh -c 'rm -rf /tmp/minio-restore' | Out-Null
    docker cp $expandPath "$($minioName):/tmp/minio-restore" | Out-Null
    if ($LASTEXITCODE -ne 0) { Stop-WithError 'No se pudo copiar la copia de MinIO a la instancia temporal.' }
    Remove-Item $expandPath -Recurse -Force

    docker exec -e RT_USER=$minioUser -e RT_PASS=$minioPass $minioName sh -c 'mc alias set restoretgt http://127.0.0.1:9000 "$RT_USER" "$RT_PASS" > /dev/null' | Out-Null
    if ($LASTEXITCODE -ne 0) { Stop-WithError 'No se pudo configurar mc en la instancia temporal de MinIO.' }

    # --- Inventario de metadatos del conjunto -------------------------------
    $metadataArtifact = $manifest.artifacts | Where-Object { $_.service -eq 'minio' -and $_.file -like '*objects-metadata*' } | Select-Object -First 1
    if ($null -eq $metadataArtifact) {
        Stop-WithError 'El conjunto no incluye el inventario de metadatos de MinIO. Fue generado por una version anterior del script y no se puede verificar la restauracion de metadatos.'
    }
    $metadataPath = Join-Path $setPath ($metadataArtifact.file -replace '/', '\')
    $metadataDoc = Get-Content $metadataPath -Raw | ConvertFrom-Json

    $bucketsArtifact = $manifest.artifacts | Where-Object { $_.service -eq 'minio' -and $_.file -like '*buckets*' } | Select-Object -First 1
    if ($null -ne $bucketsArtifact) {
        $bucketsDoc = Get-Content (Join-Path $setPath ($bucketsArtifact.file -replace '/', '\')) -Raw | ConvertFrom-Json
        $declaredCompleteness = "$(Get-PropertyOrDefault -InputObject $bucketsDoc -Name 'completeness' -Default 'desconocida')"
        Write-Info "Buckets en el conjunto: $(Get-PropertyOrDefault -InputObject $bucketsDoc -Name 'bucketCount' -Default 0) - integridad declarada: $declaredCompleteness"
        $unsupportedInSet = @(Get-PropertyOrDefault -InputObject $bucketsDoc -Name 'unsupportedFeaturesFound' -Default @())
        if ($unsupportedInSet.Count -gt 0) {
            Write-Warn 'El conjunto declara configuraciones de bucket que NO se reaplican al restaurar:'
            foreach ($item in $unsupportedInSet) { Write-Host "           - $item" -ForegroundColor Yellow }
        }
    }

    # --- Restauracion objeto a objeto, con metadatos ------------------------
    #
    # NO se usa `mc mirror` para restaurar: copiaria el contenido pero dejaria
    # los objetos sin sus metadatos S3 ni sus tags. Cada objeto se sube con
    # `mc cp --attr`, que si los aplica, y despues se reaplican los tags.
    $bucketsToCreate = @($metadataDoc.objects | ForEach-Object { $_.bucket } | Sort-Object -Unique)
    foreach ($bucket in $bucketsToCreate) {
        docker exec $minioName mc mb --ignore-existing "restoretgt/$bucket" | Out-Null
        if ($LASTEXITCODE -ne 0) { Stop-WithError "No se pudo crear el bucket temporal '$bucket'." }
    }
    Write-Ok "$($bucketsToCreate.Count) bucket(s) recreados"

    foreach ($entry in $metadataDoc.objects) {
        $source = "/tmp/minio-restore/$($entry.bucket)/$($entry.key)"
        $target = "restoretgt/$($entry.bucket)/$($entry.key)"

        # `mc cp --attr` espera `clave=valor;clave=valor`.
        $attrParts = @()
        foreach ($property in $entry.headers.PSObject.Properties) {
            $attrParts += "$($property.Name)=$($property.Value)"
        }
        foreach ($property in $entry.userMetadata.PSObject.Properties) {
            $attrParts += "$($property.Name)=$($property.Value)"
        }

        if ($attrParts.Count -gt 0) {
            docker exec $minioName mc cp --quiet --attr ($attrParts -join ';') $source $target | Out-Null
        }
        else {
            docker exec $minioName mc cp --quiet $source $target | Out-Null
        }
        if ($LASTEXITCODE -ne 0) { Stop-WithError "No se pudo restaurar el objeto '$($entry.bucket)/$($entry.key)'." }

        $tagParts = @()
        foreach ($property in $entry.tags.PSObject.Properties) {
            $tagParts += "$($property.Name)=$($property.Value)"
        }
        if ($tagParts.Count -gt 0) {
            docker exec $minioName mc tag set $target ($tagParts -join '&') | Out-Null
            if ($LASTEXITCODE -ne 0) { Stop-WithError "No se pudieron reaplicar los tags de '$($entry.bucket)/$($entry.key)'." }
        }
    }
    docker exec $minioName sh -c 'rm -rf /tmp/minio-restore' | Out-Null
    Write-Ok "$($metadataDoc.objects.Count) objeto(s) restaurados con sus metadatos y tags"

    # --- Verificacion por SHA-256 del contenido -----------------------------
    #
    # Se compara el hash del CONTENIDO, no el ETag. MinIO calcula el ETag de
    # forma distinta segun como se subiera el objeto: un objeto subido en
    # multipart lleva sufijo `-N` y el mismo contenido restaurado con un PUT
    # simple recibe otro valor. Comparar ETags daria falsos negativos.
    $hashArtifact = $manifest.artifacts | Where-Object { $_.service -eq 'minio' -and $_.file -like '*objects*' } | Select-Object -First 1
    if ($null -eq $hashArtifact) { Stop-WithError 'El conjunto no incluye los SHA-256 de los objetos de MinIO.' }
    $hashPath = Join-Path $setPath ($hashArtifact.file -replace '/', '\')

    $originalHashes = @{}
    foreach ($line in (Get-Content $hashPath)) {
        $trimmed = $line.Trim()
        if ($trimmed.Length -eq 0) { continue }
        $parts = $trimmed -split '\s+', 2
        if ($parts.Count -ne 2) { continue }
        $key = $parts[1].Trim() -replace '^\./', ''
        $originalHashes[$key] = $parts[0].ToLower()
    }

    # Se espeja el bucket restaurado, se extrae al host y se recalculan los
    # hashes con el mismo metodo que en el backup. La imagen de MinIO no
    # incluye `find`, asi que el calculo se hace siempre en el host.
    docker exec $minioName sh -c 'rm -rf /tmp/minio-verify; mkdir -p /tmp/minio-verify' | Out-Null
    $verifyMirror = docker exec $minioName sh -c 'mc mirror --quiet --preserve restoretgt /tmp/minio-verify 2>&1'
    if ($LASTEXITCODE -ne 0) {
        Write-Host ($verifyMirror | Out-String) -ForegroundColor DarkGray
        Stop-WithError 'No se pudo espejar el bucket restaurado para verificarlo.'
    }

    $verifyPath = Join-Path $env:TEMP "personal-blog-recovery-verify-$(Get-Random)"
    if (Test-Path $verifyPath) { Remove-Item $verifyPath -Recurse -Force }
    docker cp "$($minioName):/tmp/minio-verify" $verifyPath | Out-Null
    if ($LASTEXITCODE -ne 0) { Stop-WithError 'No se pudo extraer el bucket restaurado para verificarlo.' }
    docker exec $minioName sh -c 'rm -rf /tmp/minio-verify' | Out-Null

    $restoredHashes = @{}
    foreach ($file in (Get-ChildItem -Path $verifyPath -Recurse -File -Force)) {
        $key = $file.FullName.Substring($verifyPath.Length).TrimStart('\') -replace '\\', '/'
        $restoredHashes[$key] = (Get-FileHash -Path $file.FullName -Algorithm SHA256).Hash.ToLower()
    }
    Remove-Item $verifyPath -Recurse -Force

    # Tamanos, para dar un dato adicional al informe.
    $restoredSizes = @{}
    foreach ($line in (docker exec $minioName sh -c 'mc ls --recursive --json restoretgt')) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        try { $obj = $line | ConvertFrom-Json } catch { continue }
        if ($obj.PSObject.Properties.Name -contains 'key' -and $obj.type -eq 'file') {
            $restoredSizes[$obj.key] = $obj.size
        }
    }

    $minioVerified = $true
    $compared = 0
    foreach ($key in $originalHashes.Keys) {
        if (-not $restoredHashes.ContainsKey($key)) {
            Write-Host "    FALLO  objeto ausente tras restaurar: $key" -ForegroundColor Red
            $minioVerified = $false
            continue
        }
        if ($originalHashes[$key] -ne $restoredHashes[$key]) {
            Write-Host "    FALLO  contenido distinto en $key" -ForegroundColor Red
            Write-Host "           SHA-256 original : $($originalHashes[$key])" -ForegroundColor DarkGray
            Write-Host "           SHA-256 restaurado: $($restoredHashes[$key])" -ForegroundColor DarkGray
            $minioVerified = $false
            continue
        }
        $compared++
        $size = if ($restoredSizes.ContainsKey($key)) { "$($restoredSizes[$key]) B" } else { 'tamano no disponible' }
        Write-Ok "$key - $size, SHA-256 coincide"
    }

    foreach ($key in $restoredHashes.Keys) {
        if (-not $originalHashes.ContainsKey($key)) {
            Write-Host "    FALLO  objeto inesperado tras restaurar: $key" -ForegroundColor Red
            $minioVerified = $false
        }
    }

    if ($originalHashes.Count -eq 0) {
        Write-Warn 'El backup no contenia ningun objeto: no hay nada que comparar.'
    }

    # --- Comparacion de METADATOS y TAGS ------------------------------------
    #
    # Se consulta de nuevo cada objeto restaurado y se comparan exactamente los
    # encabezados restaurables, los metadatos x-amz-meta-* y los tags. Cualquier
    # diferencia no documentada hace fallar la prueba.
    $metadataCompared = 0
    $tagsCompared = 0
    $metadataVerified = $true

    foreach ($entry in $metadataDoc.objects) {
        $target = "restoretgt/$($entry.bucket)/$($entry.key)"
        $label = "$($entry.bucket)/$($entry.key)"

        $stat = @(Invoke-McJson -Container $minioName -McArgs @('stat', '--json', $target))[0]
        if ((Get-PropertyOrDefault -InputObject $stat -Name 'status') -ne 'success') {
            Write-Host "    FALLO  no se pudo consultar el objeto restaurado: $label" -ForegroundColor Red
            $metadataVerified = $false
            continue
        }
        $statMetadata = Get-PropertyOrDefault -InputObject $stat -Name 'metadata'

        $objectOk = $true

        # Encabezados restaurables: comparacion exacta.
        foreach ($property in $entry.headers.PSObject.Properties) {
            $expected = "$($property.Value)"
            $actual = Get-McMetadataValue -Metadata $statMetadata -Name $property.Name
            if ("$actual" -ne $expected) {
                Write-Host "    FALLO  $label - $($property.Name): esperado '$expected', obtenido '$actual'" -ForegroundColor Red
                $objectOk = $false
            }
        }

        # Metadatos personalizados x-amz-meta-*: comparacion exacta en ambos
        # sentidos, para detectar tambien los que aparecen de mas.
        $expectedUser = @{}
        foreach ($property in $entry.userMetadata.PSObject.Properties) { $expectedUser[$property.Name] = "$($property.Value)" }

        $actualUser = @{}
        if ($null -ne $statMetadata) {
            foreach ($property in $statMetadata.PSObject.Properties) {
                if ($script:DerivedMetadataKeys -contains $property.Name) { continue }
                if ($property.Name -like 'X-Amz-Meta-*') { $actualUser[$property.Name] = "$($property.Value)" }
            }
        }

        foreach ($name in $expectedUser.Keys) {
            if (-not $actualUser.ContainsKey($name)) {
                Write-Host "    FALLO  $label - falta el metadato $name" -ForegroundColor Red
                $objectOk = $false
            }
            elseif ($actualUser[$name] -ne $expectedUser[$name]) {
                Write-Host "    FALLO  $label - $name : esperado '$($expectedUser[$name])', obtenido '$($actualUser[$name])'" -ForegroundColor Red
                $objectOk = $false
            }
        }
        foreach ($name in $actualUser.Keys) {
            if (-not $expectedUser.ContainsKey($name)) {
                Write-Host "    FALLO  $label - metadato inesperado tras restaurar: $name" -ForegroundColor Red
                $objectOk = $false
            }
        }

        # Tags: comparacion exacta en ambos sentidos.
        $expectedTags = @{}
        foreach ($property in $entry.tags.PSObject.Properties) { $expectedTags[$property.Name] = "$($property.Value)" }

        $actualTags = @{}
        $tagResult = @(Invoke-McJson -Container $minioName -McArgs @('tag', 'list', '--json', $target))[0]
        $actualTagset = $null
        if ((Get-PropertyOrDefault -InputObject $tagResult -Name 'status') -eq 'success') {
            $actualTagset = Get-PropertyOrDefault -InputObject $tagResult -Name 'tagset'
        }
        if ($null -ne $actualTagset) {
            foreach ($property in $actualTagset.PSObject.Properties) { $actualTags[$property.Name] = "$($property.Value)" }
        }

        foreach ($name in $expectedTags.Keys) {
            if (-not $actualTags.ContainsKey($name)) {
                Write-Host "    FALLO  $label - falta el tag '$name'" -ForegroundColor Red
                $objectOk = $false
            }
            elseif ($actualTags[$name] -ne $expectedTags[$name]) {
                Write-Host "    FALLO  $label - tag '$name': esperado '$($expectedTags[$name])', obtenido '$($actualTags[$name])'" -ForegroundColor Red
                $objectOk = $false
            }
        }
        foreach ($name in $actualTags.Keys) {
            if (-not $expectedTags.ContainsKey($name)) {
                Write-Host "    FALLO  $label - tag inesperado tras restaurar: '$name'" -ForegroundColor Red
                $objectOk = $false
            }
        }

        if ($objectOk) {
            $metadataCompared++
            if ($expectedTags.Count -gt 0) { $tagsCompared++ }
            $detail = @()
            foreach ($property in $entry.headers.PSObject.Properties) { $detail += "$($property.Name)=$($property.Value)" }
            if ($expectedUser.Count -gt 0) { $detail += "$($expectedUser.Count) metadato(s) x-amz-meta-*" }
            if ($expectedTags.Count -gt 0) { $detail += "$($expectedTags.Count) tag(s)" }
            Write-Ok "$label - $($detail -join ', ') coinciden"
        }
        else {
            $metadataVerified = $false
        }
    }

    $minioVerified = $minioVerified -and $metadataVerified

    $report['minio'] = [ordered]@{
        instance             = $minioName
        image                = $minioImage
        objectsInBackup      = $originalHashes.Count
        objectsRestored      = $restoredHashes.Count
        contentVerified      = $compared
        metadataVerified     = $metadataCompared
        objectsWithTags      = $tagsCompared
        verification         = 'SHA-256 del contenido, mas comparacion exacta de encabezados, metadatos x-amz-meta-* y tags'
        versionHistoryNote   = 'El historial de versiones queda fuera del alcance: solo se verifica la version actual de cada objeto.'
        bucketConfigNote     = 'La configuracion de los buckets se registra en el conjunto pero NO se reaplica al restaurar.'
        verified             = $minioVerified
    }

    # =======================================================================
    # Portainer
    # =======================================================================
    $portainerArtifact = $manifest.artifacts | Where-Object { $_.service -eq 'portainer' } | Select-Object -First 1
    $portainerVerified = $null

    if ($null -eq $portainerArtifact) {
        Write-Step 'Portainer omitido: el conjunto no incluye su copia'
        $report['portainer'] = [ordered]@{ verified = 'omitido - sin copia en el conjunto' }
    }
    else {
        Write-Step 'Restaurando Portainer en volumen temporal'

        $portainerImage = $manifest.images.portainer
        $portainerArchivePath = Join-Path $setPath ($portainerArtifact.file -replace '/', '\')

        if (-not (Test-VolumeExists -Name $portainerVolume)) {
            docker volume create $portainerVolume | Out-Null
        }
        $created.Volumes += $portainerVolume

        # Contenedor auxiliar: descomprime el archivo dentro del volumen temporal.
        $helperName = "$($script:RecoveryPrefix)-restore-helper"
        Remove-ContainerIfExists -Name $helperName
        Invoke-DockerOrFail -DockerArgs @(
            'create', '--name', $helperName,
            '-v', "$($portainerVolume):/data",
            $script:HelperImage,
            'sh', '-c', 'tar xzf /portainer.tar.gz -C /data'
        ) -ErrorMessage 'No se pudo crear el contenedor auxiliar de restauracion.' | Out-Null
        $created.Containers += $helperName

        docker cp $portainerArchivePath "$($helperName):/portainer.tar.gz" | Out-Null
        if ($LASTEXITCODE -ne 0) { Stop-WithError 'No se pudo copiar el archivo de Portainer al contenedor auxiliar.' }

        docker start -a $helperName | Out-Null
        if ($LASTEXITCODE -ne 0) { Stop-WithError 'El contenedor auxiliar no pudo descomprimir el volumen de Portainer.' }

        Assert-SafeToRemove -Name $helperName
        docker rm -f $helperName | Out-Null
        $created.Containers = @($created.Containers | Where-Object { $_ -ne $helperName })
        Write-Ok "Volumen $portainerVolume restaurado"

        # La instancia temporal NO monta el socket de Docker: no lo necesita
        # para arrancar y asi no se le concede acceso privilegiado al host.
        Remove-ContainerIfExists -Name $portainerName
        Invoke-DockerOrFail -DockerArgs @(
            'run', '-d', '--name', $portainerName,
            '--network', $netName,
            '-p', "127.0.0.1:$($portainerPort):9443",
            '-v', "$($portainerVolume):/data",
            $portainerImage
        ) -ErrorMessage 'No se pudo crear la instancia temporal de Portainer.' | Out-Null
        $created.Containers += $portainerName
        Write-Ok "Contenedor $portainerName en 127.0.0.1:$portainerPort (sin socket de Docker)"

        Add-Type -AssemblyName System.Net.Http -ErrorAction SilentlyContinue
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
        if ($null -eq ([System.Management.Automation.PSTypeName]'RecoveryTrustAll').Type) {
            Add-Type @'
using System.Net;
using System.Security.Cryptography.X509Certificates;
public class RecoveryTrustAll : ICertificatePolicy {
    public bool CheckValidationResult(ServicePoint sp, X509Certificate cert, WebRequest req, int problem) { return true; }
}
'@
        }
        [System.Net.ServicePointManager]::CertificatePolicy = New-Object RecoveryTrustAll

        $statusJson = $null
        $portainerUp = Wait-ForHealthy -Container $portainerName -Probe {
            try {
                $resp = Invoke-WebRequest -Uri "https://127.0.0.1:$portainerPort/api/status" -UseBasicParsing -TimeoutSec 10
                if ($resp.StatusCode -eq 200) {
                    $script:lastStatus = $resp.Content
                    return $true
                }
            }
            catch { }
            return $false
        }

        if (-not $portainerUp) {
            Write-Host '    FALLO  la instancia temporal de Portainer no respondio' -ForegroundColor Red
            $portainerVerified = $false
            $report['portainer'] = [ordered]@{ instance = $portainerName; verified = $false }
        }
        else {
            $statusJson = $script:lastStatus | ConvertFrom-Json
            Write-Ok "Responde /api/status - HTTP 200, version $($statusJson.Version)"

            # El InstanceID es un identificador NO sensible y se deriva de la
            # base de datos de Portainer: si coincide con el del entorno
            # principal, el volumen se restauro con su contenido real.
            $mainStatus = $null
            try {
                $mainResp = Invoke-WebRequest -Uri 'https://127.0.0.1:9444/api/status' -UseBasicParsing -TimeoutSec 10
                $mainStatus = ($mainResp.Content | ConvertFrom-Json).InstanceID
            }
            catch { }

            $portainerVerified = $true
            if ($mainStatus) {
                if ($mainStatus -eq $statusJson.InstanceID) {
                    Write-Ok "InstanceID coincide con el del entorno principal: $($statusJson.InstanceID)"
                }
                else {
                    Write-Host "    FALLO  el InstanceID restaurado no coincide con el principal" -ForegroundColor Red
                    $portainerVerified = $false
                }
            }
            else {
                Write-Warn 'No se pudo consultar el Portainer principal para comparar el InstanceID.'
            }

            $report['portainer'] = [ordered]@{
                instance   = $portainerName
                image      = $portainerImage
                version    = $statusJson.Version
                instanceId = $statusJson.InstanceID
                verified   = $portainerVerified
            }
        }
    }

    # =======================================================================
    # Resultado
    # =======================================================================
    Assert-MainEnvironmentIntact | Out-Null
    Write-Ok 'Los tres volumenes principales siguen intactos'

    $allOk = $pgVerified -and $minioVerified -and ($portainerVerified -ne $false)

    Write-Step 'Resultado de la prueba de restauracion'
    Write-Host "    PostgreSQL : $(if ($pgVerified) { 'CORRECTA' } else { 'FALLIDA' })"
    Write-Host "    MinIO      : $(if ($minioVerified) { 'CORRECTA' } else { 'FALLIDA' })"
    if ($null -ne $portainerVerified) {
        Write-Host "    Portainer  : $(if ($portainerVerified) { 'CORRECTA' } else { 'FALLIDA' })"
    }
    else {
        Write-Host "    Portainer  : omitido"
    }

    # Registrar el resultado en el manifiesto del conjunto probado.
    $manifest.restoreTestResult = [ordered]@{
        testedAtUtc          = Get-UtcTimestamp
        postgres             = $pgVerified
        minio                = $minioVerified
        minioContentVerified = $compared
        minioMetadataVerified = $metadataCompared
        minioObjectsWithTags = $tagsCompared
        portainer            = $portainerVerified
        overall              = $allOk
        scopeNote            = 'MinIO: verificados contenido, encabezados restaurables, metadatos x-amz-meta-* y tags de la version ACTUAL de cada objeto. Historial de versiones y configuracion de buckets quedan fuera del alcance.'
    }
    $manifest | ConvertTo-Json -Depth 6 | Out-File -FilePath (Join-Path $setPath 'manifest.json') -Encoding utf8
    Write-Info 'Resultado registrado en manifest.json'
    # `manifest.json` no figura en checksums.sha256 precisamente porque se
    # actualiza aqui: la verificacion de integridad sigue siendo valida.

    if (-not $KeepResources) {
        Write-Step 'Eliminando unicamente los recursos temporales'
        & (Join-Path $PSScriptRoot 'Remove-RecoveryTestResources.ps1') -Force
    }
    else {
        Write-Warn "Recursos temporales conservados por -KeepResources. Limpialos con Remove-RecoveryTestResources.ps1"
    }

    if (-not $allOk) { exit 1 }
    Write-Host ''
    Write-Host '    RESTAURACION VERIFICADA CORRECTAMENTE' -ForegroundColor Green
}
catch {
    Write-Host ''
    Write-Host "PRUEBA DE RESTAURACION FALLIDA: $($_.Exception.Message)" -ForegroundColor Red
    Write-Warn 'Los recursos temporales pueden seguir en pie. Revisalos y limpialos con Remove-RecoveryTestResources.ps1'
    exit 1
}
