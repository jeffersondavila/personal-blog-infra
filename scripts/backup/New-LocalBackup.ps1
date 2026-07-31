<#
.SYNOPSIS
    Crea un conjunto de respaldo completo del entorno local del blog.

.DESCRIPTION
    Respalda los tres servicios del entorno local a archivos EXTERNOS a los
    volumenes de Docker:

      - PostgreSQL : volcado logico con pg_dump en formato custom, en caliente.
      - MinIO      : copia a nivel de objetos con `mc mirror`, mas el inventario.
      - Portainer  : archivo tar.gz del volumen de datos.

    Genera un manifiesto y un archivo de checksums SHA-256 por ejecucion.

    El backup de Portainer exige coherencia: su base interna se escribe de
    forma continua. Por eso el contenedor de Portainer se DETIENE durante el
    tiempo minimo necesario y se vuelve a arrancar. PostgreSQL y MinIO NO se
    detienen en ningun momento.

    Este script NO elimina nada y NO modifica los volumenes principales.

.PARAMETER BackupRoot
    Directorio raiz de los backups. Por defecto `local-backups/` en la raiz
    del repositorio, que esta ignorado por Git.

.PARAMETER SkipPortainer
    Omite el respaldo de Portainer y, con el, su parada momentanea.

.PARAMETER AllowPartial
    Permite generar el conjunto aunque MinIO use caracteristicas que este
    procedimiento no sabe restaurar (versionado, Object Lock, replicacion,
    ciclo de vida, politicas anonimas, cifrado). Sin este parametro, el script
    ABORTA en lugar de producir un backup que aparenta estar completo.
    Con el, el conjunto queda marcado como PARCIAL en el manifiesto.

.EXAMPLE
    .\New-LocalBackup.ps1

.EXAMPLE
    .\New-LocalBackup.ps1 -SkipPortainer

.EXAMPLE
    .\New-LocalBackup.ps1 -AllowPartial

.NOTES
    Task/004-Backups-y-Recuperacion-Local

    Los artefactos generados son SENSIBLES: contienen los datos del blog y la
    configuracion de Portainer, incluidos hashes de autenticacion. Nunca se
    versionan ni se comparten.

    ALCANCE EN MINIO: se respalda la version ACTUAL de cada objeto, con su
    contenido, sus metadatos (Content-Type, Cache-Control, Content-Disposition,
    Content-Encoding, Content-Language y x-amz-meta-*) y sus tags. El historial
    de versiones queda FUERA del alcance.
#>
[CmdletBinding()]
param(
    [string]$BackupRoot,
    [switch]$SkipPortainer,
    [switch]$AllowPartial
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '_BackupCommon.ps1')

$mainPostgres  = 'personal-blog-local-postgres'
$mainMinio     = 'personal-blog-local-minio'
$mainPortainer = 'personal-blog-local-portainer'
$portainerVolume = 'personal-blog-local_portainer_data'

try {
    Write-Host '=== Backup del entorno local - Task/004 ===' -ForegroundColor White

    $versions = Assert-Dependencies
    Assert-HelperImage
    Assert-MainEnvironmentIntact | Out-Null
    Write-Ok 'Los tres volumenes principales estan presentes'

    $config = Read-DotEnv

    # --- Preparar el conjunto de respaldo -----------------------------------
    $setId = Get-BackupSetId
    $root = Get-BackupRoot -Root $BackupRoot
    $setPath = Join-Path $root $setId

    Write-Step "Creando conjunto de respaldo $setId"
    foreach ($sub in @('', 'postgres', 'minio', 'portainer')) {
        $target = if ($sub -eq '') { $setPath } else { Join-Path $setPath $sub }
        New-Item -ItemType Directory -Path $target -Force | Out-Null
    }
    Write-Ok "Destino: $setPath"

    $artifacts = @()
    $results = @{}

    # --- PostgreSQL ---------------------------------------------------------
    Write-Step 'Respaldando PostgreSQL (sin detener el servicio)'

    $pgVersion = (docker exec $mainPostgres psql -U $config['POSTGRES_USER'] -d $config['POSTGRES_DB'] -tAc 'SHOW server_version;').Trim()
    Write-Info "Servidor PostgreSQL $pgVersion"
    Write-Info "Base '$($config['POSTGRES_DB'])', usuario '$($config['POSTGRES_USER'])'"

    $dumpName = "postgres-$setId.dump"
    $containerDump = "/tmp/$dumpName"

    # `pg_dump` se ejecuta dentro del contenedor y escribe a /tmp; despues se
    # extrae con `docker cp`. Escribir a stdout y canalizarlo por PowerShell
    # corromperia el archivo binario.
    Invoke-DockerOrFail -DockerArgs @(
        'exec', $mainPostgres,
        'pg_dump', '-U', $config['POSTGRES_USER'], '-d', $config['POSTGRES_DB'],
        '--format=custom', '--compress=6', '--file', $containerDump
    ) -ErrorMessage 'pg_dump fallo. Revisa que PostgreSQL este healthy.' | Out-Null

    $hostDump = Join-Path $setPath "postgres\$dumpName"
    Invoke-DockerOrFail -DockerArgs @('cp', "$($mainPostgres):$containerDump", $hostDump) `
        -ErrorMessage 'No se pudo extraer el volcado de PostgreSQL del contenedor.' | Out-Null
    docker exec $mainPostgres rm -f $containerDump | Out-Null

    $pgSize = Get-FileSizeBytes -Path $hostDump
    $artifacts += [pscustomobject]@{
        Service      = 'postgres'
        RelativePath = "postgres/$dumpName"
        FullPath     = $hostDump
        Bytes        = $pgSize
        Sha256       = Get-Sha256 -Path $hostDump
    }
    $results['postgres'] = 'OK'
    Write-Ok "$dumpName ($(Format-Size $pgSize))"

    # Inventario legible del contenido respaldado, util para verificar sin
    # restaurar. No contiene datos, solo la lista de objetos del volcado.
    $tocName = "postgres-$setId.toc.txt"
    $hostToc = Join-Path $setPath "postgres\$tocName"
    docker cp $hostDump "$($mainPostgres):/tmp/verify.dump" | Out-Null
    docker exec $mainPostgres pg_restore --list /tmp/verify.dump | Out-File -FilePath $hostToc -Encoding utf8
    docker exec $mainPostgres rm -f /tmp/verify.dump | Out-Null
    $tocSize = Get-FileSizeBytes -Path $hostToc
    $artifacts += [pscustomobject]@{
        Service      = 'postgres'
        RelativePath = "postgres/$tocName"
        FullPath     = $hostToc
        Bytes        = $tocSize
        Sha256       = Get-Sha256 -Path $hostToc
    }
    Write-Ok "$tocName ($(Format-Size $tocSize)) - indice del volcado"

    # --- MinIO --------------------------------------------------------------
    Write-Step 'Respaldando MinIO (sin detener el servicio)'

    $minioVersion = (docker inspect $mainMinio --format '{{index .Config.Image}}').Trim()
    Write-Info "Imagen $minioVersion"

    # El alias de `mc` vive fuera del volumen de datos, asi que se reestablece
    # en cada ejecucion. Las credenciales se leen de las variables de entorno
    # del propio contenedor: nunca viajan por la linea de comandos.
    docker exec $mainMinio sh -c 'mc alias set backupsrc http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" > /dev/null' | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Stop-WithError 'No se pudo configurar el cliente mc dentro del contenedor de MinIO.'
    }

    # --- Configuracion de los buckets ---------------------------------------
    #
    # Se registra ANTES de copiar nada, para poder abortar si el entorno usa
    # caracteristicas que este procedimiento no sabe restaurar.
    $bucketEntries = @()
    $unsupported = @()

    $bucketList = Invoke-McJson -Container $mainMinio -McArgs @('ls', '--json', 'backupsrc')
    $bucketNames = @($bucketList | Where-Object { $_.type -eq 'folder' } | ForEach-Object { $_.key.TrimEnd('/') })

    foreach ($bucket in $bucketNames) {
        $stat = @(Invoke-McJson -Container $mainMinio -McArgs @('stat', '--json', "backupsrc/$bucket"))[0]
        $anon = @(Invoke-McJson -Container $mainMinio -McArgs @('anonymous', 'get', '--json', "backupsrc/$bucket"))[0]
        $ilm = @(Invoke-McJson -Container $mainMinio -McArgs @('ilm', 'rule', 'list', '--json', "backupsrc/$bucket"))

        # `mc` omite campos segun el caso, y con Set-StrictMode leer una
        # propiedad ausente aborta el script: todo acceso pasa por
        # Get-PropertyOrDefault.
        $statVersioning = Get-PropertyOrDefault -InputObject $stat -Name 'Versioning'
        $versioning = "$(Get-PropertyOrDefault -InputObject $statVersioning -Name 'status' -Default '')"

        $statLock = Get-PropertyOrDefault -InputObject $stat -Name 'ObjectLock'
        $lockEnabled = "$(Get-PropertyOrDefault -InputObject $statLock -Name 'enabled' -Default '')"

        $statReplication = Get-PropertyOrDefault -InputObject $stat -Name 'Replication'
        $replication = [bool](Get-PropertyOrDefault -InputObject $statReplication -Name 'enabled' -Default $false)

        $statPolicy = Get-PropertyOrDefault -InputObject $stat -Name 'Policy'
        $policyType = "$(Get-PropertyOrDefault -InputObject $statPolicy -Name 'type' -Default 'none')"

        $anonPermission = 'private'
        if ((Get-PropertyOrDefault -InputObject $anon -Name 'status') -eq 'success') {
            $anonPermission = "$(Get-PropertyOrDefault -InputObject $anon -Name 'permission' -Default 'private')"
        }

        $hasLifecycle = @($ilm | Where-Object { (Get-PropertyOrDefault -InputObject $_ -Name 'status') -eq 'success' }).Count -gt 0

        $statEncryption = Get-PropertyOrDefault -InputObject $stat -Name 'Encryption'
        $encryptionSet = $false
        if ($null -ne $statEncryption) {
            $encryptionSet = @($statEncryption.PSObject.Properties).Count -gt 0
        }

        # Caracteristicas que este procedimiento NO sabe restaurar. Registrarlas
        # y seguir en silencio seria ofrecer una garantia que no existe.
        $bucketUnsupported = @()
        if ($versioning -eq 'Enabled' -or $versioning -eq 'Suspended') {
            $bucketUnsupported += "versionado '$versioning': solo se respalda la version actual de cada objeto"
        }
        if (-not [string]::IsNullOrWhiteSpace($lockEnabled)) {
            $bucketUnsupported += 'Object Lock activo: no se respaldan retenciones ni modos de bloqueo'
        }
        if ($replication) {
            $bucketUnsupported += 'replicacion configurada: no se respalda su configuracion'
        }
        if ($hasLifecycle) {
            $bucketUnsupported += 'reglas de ciclo de vida configuradas: no se respaldan'
        }
        if ($anonPermission -ne 'private' -or ($policyType -ne 'none' -and $policyType -ne 'private')) {
            $bucketUnsupported += "politica anonima '$anonPermission': se registra pero no se reaplica al restaurar"
        }
        if ($encryptionSet) {
            $bucketUnsupported += 'cifrado en reposo configurado: no se respalda su configuracion'
        }

        foreach ($item in $bucketUnsupported) { $unsupported += "$bucket - $item" }

        $bucketEntries += [ordered]@{
            name                = $bucket
            versioning          = $versioning
            objectLockEnabled   = $lockEnabled
            replicationEnabled  = $replication
            anonymousPolicy     = $anonPermission
            policyType          = $policyType
            lifecycleConfigured = $hasLifecycle
            encryptionConfigured = $encryptionSet
            location            = "$(Get-PropertyOrDefault -InputObject $stat -Name 'location' -Default '')"
            unsupportedFeatures = $bucketUnsupported
        }
    }

    Write-Ok "$($bucketNames.Count) bucket(s) inspeccionados"

    if ($unsupported.Count -gt 0) {
        Write-Warn 'Se detectaron configuraciones que este procedimiento NO sabe restaurar:'
        foreach ($item in $unsupported) { Write-Host "           - $item" -ForegroundColor Yellow }
        if (-not $AllowPartial) {
            Stop-WithError 'El conjunto no se puede considerar completo. Revisa las configuraciones anteriores y, si aun asi quieres generarlo, vuelve a ejecutar con -AllowPartial: el conjunto quedara marcado como PARCIAL.'
        }
        Write-Warn 'Continuando por -AllowPartial: el conjunto se marcara como PARCIAL.'
    }

    docker exec $mainMinio sh -c 'rm -rf /tmp/minio-backup; mkdir -p /tmp/minio-backup' | Out-Null
    $mirrorOutput = docker exec $mainMinio sh -c 'mc mirror --quiet backupsrc /tmp/minio-backup 2>&1'
    if ($LASTEXITCODE -ne 0) {
        Write-Host ($mirrorOutput | Out-String) -ForegroundColor DarkGray
        Stop-WithError 'mc mirror fallo.'
    }

    # Inventario de objetos con tamano y ETag: registro informativo del estado
    # del bucket en el momento del backup.
    $inventoryName = "minio-inventory-$setId.json"
    $hostInventory = Join-Path $setPath "minio\$inventoryName"
    docker exec $mainMinio sh -c 'mc ls --recursive --json backupsrc' | Out-File -FilePath $hostInventory -Encoding utf8
    $inventorySize = Get-FileSizeBytes -Path $hostInventory

    # Empaquetado del arbol de objetos en un unico archivo verificable.
    #
    # La imagen de MinIO NO incluye `tar` ni `find`, asi que el arbol se extrae
    # con `docker cp` y todo el procesado se hace en el host con cmdlets de
    # PowerShell. No se anade ninguna dependencia externa.
    $minioArchive = "minio-$setId.zip"
    $hostMinioArchive = Join-Path $setPath "minio\$minioArchive"
    $stagingPath = Join-Path $setPath 'minio\_staging'

    if (Test-Path $stagingPath) { Remove-Item $stagingPath -Recurse -Force }
    Invoke-DockerOrFail -DockerArgs @('cp', "$($mainMinio):/tmp/minio-backup", $stagingPath) `
        -ErrorMessage 'No se pudo extraer el arbol de objetos de MinIO del contenedor.' | Out-Null
    docker exec $mainMinio sh -c 'rm -rf /tmp/minio-backup' | Out-Null

    # SHA-256 del CONTENIDO de cada objeto. Es lo que se compara al restaurar.
    #
    # El ETag no sirve para esto: MinIO lo calcula de forma distinta segun como
    # se subiera el objeto. Un objeto subido en multipart (`mc pipe`) recibe un
    # ETag con sufijo `-N`, y el mismo contenido restaurado con un PUT simple
    # recibe otro. Comparar ETags daria falsos negativos.
    $objectHashName = "minio-objects-$setId.sha256"
    $hostObjectHashes = Join-Path $setPath "minio\$objectHashName"
    $objectFiles = @(Get-ChildItem -Path $stagingPath -Recurse -File -Force)
    $hashByKey = @{}
    $hashLines = foreach ($file in $objectFiles) {
        $relative = $file.FullName.Substring($stagingPath.Length).TrimStart('\') -replace '\\', '/'
        $hash = (Get-FileHash -Path $file.FullName -Algorithm SHA256).Hash.ToLower()
        $hashByKey[$relative] = $hash
        "$hash  $relative"
    }
    @($hashLines) | Out-File -FilePath $hostObjectHashes -Encoding ascii
    $objectHashSize = Get-FileSizeBytes -Path $hostObjectHashes
    $objectCount = $objectFiles.Count

    # Coherencia entre lo que declara el inventario y lo que se ha copiado.
    # Un backup que dice tener objetos pero no los tiene es peor que ninguno.
    $inventoryObjects = @(Get-Content $hostInventory | Where-Object {
        if ([string]::IsNullOrWhiteSpace($_)) { return $false }
        try { return (($_ | ConvertFrom-Json).type -eq 'file') } catch { return $false }
    }).Count
    if ($inventoryObjects -ne $objectCount) {
        Stop-WithError "Incoherencia en la copia de MinIO: el inventario declara $inventoryObjects objetos y se copiaron $objectCount. No se genera un backup incompleto."
    }

    if ($objectFiles.Count -eq 0) {
        # MinIO sin ningun objeto: se genera un marcador para que el archivo
        # exista y la restauracion no tenga casos especiales.
        New-Item -ItemType Directory -Path (Join-Path $stagingPath '.empty') -Force | Out-Null
        Write-Warn 'MinIO no contiene ningun objeto: la copia esta vacia.'
    }
    Compress-Archive -Path (Join-Path $stagingPath '*') -DestinationPath $hostMinioArchive -Force
    if (-not (Test-Path $hostMinioArchive)) {
        Stop-WithError 'No se pudo empaquetar la copia de MinIO.'
    }
    Remove-Item $stagingPath -Recurse -Force

    # --- Inventario de METADATOS y TAGS -------------------------------------
    #
    # `mc mirror` hacia un sistema de archivos copia el CONTENIDO, no los
    # metadatos S3: Content-Type, Cache-Control, los x-amz-meta-* y los tags se
    # perderian. Se inventarian aparte, con `mc stat` y `mc tag list`, y se
    # reaplican explicitamente al restaurar.
    $metadataName = "minio-objects-metadata-$setId.json"
    $hostMetadata = Join-Path $setPath "minio\$metadataName"

    $objectEntries = @()
    $withUserMetadata = 0
    $withTags = 0

    foreach ($bucket in $bucketNames) {
        $stats = Invoke-McJson -Container $mainMinio -McArgs @('stat', '--json', '--recursive', "backupsrc/$bucket")
        foreach ($stat in $stats) {
            if ((Get-PropertyOrDefault -InputObject $stat -Name 'status') -ne 'success') { continue }
            if ((Get-PropertyOrDefault -InputObject $stat -Name 'type') -ne 'file') { continue }

            # `name` viene como `<bucket>/<key>` en modo recursivo.
            $fullName = "$(Get-PropertyOrDefault -InputObject $stat -Name 'name' -Default '')"
            $key = $fullName
            if ($key.StartsWith("$bucket/")) { $key = $key.Substring($bucket.Length + 1) }

            $headers = [ordered]@{}
            foreach ($header in $script:RestorableHeaders) {
                $value = Get-McMetadataValue -Metadata (Get-PropertyOrDefault -InputObject $stat -Name 'metadata') -Name $header
                if (-not [string]::IsNullOrWhiteSpace($value)) { $headers[$header] = $value }
            }

            $statMetadata = Get-PropertyOrDefault -InputObject $stat -Name 'metadata'
            $userMetadata = [ordered]@{}
            if ($null -ne $statMetadata) {
                foreach ($property in $statMetadata.PSObject.Properties) {
                    if ($script:DerivedMetadataKeys -contains $property.Name) { continue }
                    if ($property.Name -like 'X-Amz-Meta-*') {
                        $userMetadata[$property.Name] = $property.Value
                    }
                }
            }
            if ($userMetadata.Count -gt 0) { $withUserMetadata++ }

            # `tagset` no aparece en la respuesta cuando el objeto no tiene
            # tags: hay que comprobarlo antes de leerlo.
            $tags = [ordered]@{}
            $tagResult = @(Invoke-McJson -Container $mainMinio -McArgs @('tag', 'list', '--json', "backupsrc/$bucket/$key"))[0]
            $tagset = $null
            if ((Get-PropertyOrDefault -InputObject $tagResult -Name 'status') -eq 'success') {
                $tagset = Get-PropertyOrDefault -InputObject $tagResult -Name 'tagset'
            }
            if ($null -ne $tagset) {
                foreach ($property in $tagset.PSObject.Properties) {
                    $tags[$property.Name] = $property.Value
                }
            }
            if ($tags.Count -gt 0) { $withTags++ }

            # Un valor con `;` rompe el formato `clave=valor;clave=valor` que
            # exige `mc cp --attr`. Antes que restaurar mal, se aborta.
            foreach ($value in (@($headers.Values) + @($userMetadata.Values))) {
                if ("$value".Contains(';')) {
                    Stop-WithError "El objeto '$bucket/$key' tiene un metadato con ';', que no se puede reaplicar con 'mc cp --attr'. No se genera un backup que no se sabe restaurar."
                }
            }

            $objectEntries += [ordered]@{
                bucket       = $bucket
                key          = $key
                size         = (Get-PropertyOrDefault -InputObject $stat -Name 'size' -Default 0)
                sha256       = $(if ($hashByKey.ContainsKey("$bucket/$key")) { $hashByKey["$bucket/$key"] } else { $null })
                etag         = "$(Get-PropertyOrDefault -InputObject $stat -Name 'etag' -Default '')"
                lastModified = "$(Get-PropertyOrDefault -InputObject $stat -Name 'lastModified' -Default '')"
                headers      = $headers
                userMetadata = $userMetadata
                tags         = $tags
            }
        }
    }

    if ($objectEntries.Count -ne $objectCount) {
        Stop-WithError "Incoherencia: se inventariaron $($objectEntries.Count) objetos con metadatos y se copiaron $objectCount contenidos. No se genera un backup incompleto."
    }
    foreach ($entry in $objectEntries) {
        if ([string]::IsNullOrWhiteSpace($entry.sha256)) {
            Stop-WithError "El objeto '$($entry.bucket)/$($entry.key)' no tiene contenido copiado. No se genera un backup incompleto."
        }
    }

    $metadataDocument = [ordered]@{
        generatedAtUtc = Get-UtcTimestamp
        scope          = 'Version ACTUAL de cada objeto. El historial de versiones queda FUERA del alcance de Task/004.'
        restorable     = 'Content-Type, Cache-Control, Content-Disposition, Content-Encoding, Content-Language, metadatos x-amz-meta-* y tags.'
        notRestorable  = 'ETag y lastModified son derivados y los recalcula MinIO. X-Amz-Tagging-Count se deriva de los tags.'
        objectCount    = $objectEntries.Count
        withUserMetadata = $withUserMetadata
        withTags       = $withTags
        objects        = $objectEntries
    }
    $metadataDocument | ConvertTo-Json -Depth 8 | Out-File -FilePath $hostMetadata -Encoding utf8
    $metadataSize = Get-FileSizeBytes -Path $hostMetadata

    # --- Inventario de configuracion de BUCKETS -----------------------------
    $bucketsName = "minio-buckets-$setId.json"
    $hostBuckets = Join-Path $setPath "minio\$bucketsName"
    $bucketsDocument = [ordered]@{
        generatedAtUtc           = Get-UtcTimestamp
        scope                    = 'Registro informativo de la configuracion de cada bucket. Al restaurar solo se recrea el bucket; las configuraciones listadas NO se reaplican.'
        bucketCount              = $bucketEntries.Count
        buckets                  = $bucketEntries
        unsupportedFeaturesFound = $unsupported
        completeness             = $(if ($unsupported.Count -gt 0) { 'PARCIAL' } else { 'COMPLETO' })
    }
    $bucketsDocument | ConvertTo-Json -Depth 8 | Out-File -FilePath $hostBuckets -Encoding utf8
    $bucketsSize = Get-FileSizeBytes -Path $hostBuckets

    $minioSize = Get-FileSizeBytes -Path $hostMinioArchive
    $artifacts += [pscustomobject]@{
        Service      = 'minio'
        RelativePath = "minio/$minioArchive"
        FullPath     = $hostMinioArchive
        Bytes        = $minioSize
        Sha256       = Get-Sha256 -Path $hostMinioArchive
    }
    $artifacts += [pscustomobject]@{
        Service      = 'minio'
        RelativePath = "minio/$inventoryName"
        FullPath     = $hostInventory
        Bytes        = $inventorySize
        Sha256       = Get-Sha256 -Path $hostInventory
    }
    $artifacts += [pscustomobject]@{
        Service      = 'minio'
        RelativePath = "minio/$objectHashName"
        FullPath     = $hostObjectHashes
        Bytes        = $objectHashSize
        Sha256       = Get-Sha256 -Path $hostObjectHashes
    }
    $artifacts += [pscustomobject]@{
        Service      = 'minio'
        RelativePath = "minio/$metadataName"
        FullPath     = $hostMetadata
        Bytes        = $metadataSize
        Sha256       = Get-Sha256 -Path $hostMetadata
    }
    $artifacts += [pscustomobject]@{
        Service      = 'minio'
        RelativePath = "minio/$bucketsName"
        FullPath     = $hostBuckets
        Bytes        = $bucketsSize
        Sha256       = Get-Sha256 -Path $hostBuckets
    }
    $results['minio'] = $(if ($unsupported.Count -gt 0) { 'PARCIAL' } else { 'OK' })
    Write-Ok "$minioArchive ($(Format-Size $minioSize))"
    Write-Ok "$inventoryName ($(Format-Size $inventorySize)) - inventario de objetos"
    Write-Ok "$objectHashName ($(Format-Size $objectHashSize)) - SHA-256 de $objectCount objetos"
    Write-Ok "$metadataName ($(Format-Size $metadataSize)) - metadatos y tags: $withUserMetadata objeto(s) con x-amz-meta-*, $withTags con tags"
    Write-Ok "$bucketsName ($(Format-Size $bucketsSize)) - configuracion de $($bucketEntries.Count) bucket(s)"

    # --- Portainer ----------------------------------------------------------
    if ($SkipPortainer) {
        $results['portainer'] = 'OMITIDO (-SkipPortainer)'
        Write-Step 'Portainer omitido por parametro'
    }
    else {
        Write-Step 'Respaldando Portainer (parada momentanea del contenedor)'
        Write-Info 'Portainer escribe su base interna de forma continua: se detiene para obtener una copia coherente.'
        Write-Info 'PostgreSQL y MinIO NO se detienen.'

        $portainerWasRunning = (docker inspect $mainPortainer --format '{{.State.Running}}').Trim() -eq 'true'

        try {
            if ($portainerWasRunning) {
                docker stop $mainPortainer | Out-Null
                if ($LASTEXITCODE -ne 0) { Stop-WithError 'No se pudo detener Portainer.' }
                Write-Ok 'Portainer detenido'
            }

            # Contenedor auxiliar: monta el volumen en SOLO LECTURA y escribe
            # el archivo en un volumen temporal propio, del que se extrae con
            # `docker cp`. Evita depender de bind mounts de Windows.
            $portainerArchive = "portainer-$setId.tar.gz"
            $helperName = "$($script:RecoveryPrefix)-backup-helper"

            Remove-ContainerIfExists -Name $helperName
            Invoke-DockerOrFail -DockerArgs @(
                'run', '--name', $helperName,
                '-v', "$($portainerVolume):/data:ro",
                $script:HelperImage,
                'sh', '-c', "tar czf /$portainerArchive -C /data ."
            ) -ErrorMessage 'El contenedor auxiliar no pudo empaquetar el volumen de Portainer.' | Out-Null

            $hostPortainerArchive = Join-Path $setPath "portainer\$portainerArchive"
            Invoke-DockerOrFail -DockerArgs @('cp', "$($helperName):/$portainerArchive", $hostPortainerArchive) `
                -ErrorMessage 'No se pudo extraer el archivo de Portainer del contenedor auxiliar.' | Out-Null

            Remove-ContainerIfExists -Name $helperName

            $portainerSize = Get-FileSizeBytes -Path $hostPortainerArchive
            $artifacts += [pscustomobject]@{
                Service      = 'portainer'
                RelativePath = "portainer/$portainerArchive"
                FullPath     = $hostPortainerArchive
                Bytes        = $portainerSize
                Sha256       = Get-Sha256 -Path $hostPortainerArchive
            }
            $results['portainer'] = 'OK'
            Write-Ok "$portainerArchive ($(Format-Size $portainerSize))"
        }
        finally {
            # Portainer vuelve a arrancar pase lo que pase.
            if ($portainerWasRunning) {
                docker start $mainPortainer | Out-Null
                Write-Ok 'Portainer reiniciado'
            }
        }
    }

    # --- Checksums ----------------------------------------------------------
    Write-Step 'Generando checksums SHA-256'
    $checksumPath = Join-Path $setPath 'checksums.sha256'
    $lines = foreach ($a in $artifacts) { "$($a.Sha256)  $($a.RelativePath)" }
    $lines | Out-File -FilePath $checksumPath -Encoding ascii
    Write-Ok "checksums.sha256 con $($artifacts.Count) entradas"

    # --- Manifiesto ---------------------------------------------------------
    Write-Step 'Generando manifiesto'

    $images = @{}
    foreach ($pair in @(@($mainPostgres, 'postgres'), @($mainMinio, 'minio'), @($mainPortainer, 'portainer'))) {
        if (Test-ContainerExists -Name $pair[0]) {
            $img = docker inspect $pair[0] --format '{{.Config.Image}}'
            $images[$pair[1]] = $img.Trim()
        }
    }

    $manifest = [ordered]@{
        backupSetId       = $setId
        createdAtUtc      = Get-UtcTimestamp
        project           = 'personal-blog-local'
        task              = 'Task/004-Backups-y-Recuperacion-Local'
        dockerVersion     = $versions.Docker
        composeVersion    = $versions.Compose
        images            = $images
        postgres          = [ordered]@{
            database      = $config['POSTGRES_DB']
            user          = $config['POSTGRES_USER']
            serverVersion = $pgVersion
            format        = 'custom (pg_dump -Fc), restaurable con pg_restore'
            hotBackup     = $true
        }
        minio             = [ordered]@{
            contentMethod    = 'mc mirror a sistema de archivos, empaquetado en zip (la imagen de MinIO no incluye tar)'
            metadataMethod   = 'mc stat --json y mc tag list --json por objeto, inventariados aparte'
            metadataNote     = 'mc mirror hacia un sistema de archivos NO conserva los metadatos S3 ni los tags: por eso se inventarian y se reaplican explicitamente al restaurar.'
            hotBackup        = $true
            objectCount      = $objectCount
            withUserMetadata = $withUserMetadata
            withTags         = $withTags
            bucketCount      = $bucketEntries.Count
            verification     = 'SHA-256 del contenido, mas comparacion exacta de encabezados restaurables, metadatos x-amz-meta-* y tags. El ETag no se usa: MinIO lo calcula distinto segun el modo de subida.'
            versionHistory   = 'FUERA DE ALCANCE. Se respalda unicamente la version actual de cada objeto.'
            bucketConfig     = 'Registrada de forma informativa. Al restaurar solo se recrea el bucket; versionado, Object Lock, replicacion, ciclo de vida, politicas y cifrado NO se reaplican.'
            unsupportedFeaturesFound = $unsupported
        }
        portainer         = [ordered]@{
            volume            = $portainerVolume
            method            = 'tar.gz del volumen mediante contenedor auxiliar'
            containerStopped  = (-not $SkipPortainer)
        }
        artifacts         = @($artifacts | ForEach-Object {
            [ordered]@{
                service = $_.Service
                file    = $_.RelativePath
                bytes   = $_.Bytes
                sha256  = $_.Sha256
            }
        })
        backupResult      = $results
        completeness      = $(if ($unsupported.Count -gt 0) { 'PARCIAL' } else { 'COMPLETO' })
        completenessNote  = $(if ($unsupported.Count -gt 0) {
            'PARCIAL: MinIO usa caracteristicas que este procedimiento no sabe restaurar. Ver minio.unsupportedFeaturesFound.'
        } else {
            'COMPLETO para el alcance declarado: contenido, metadatos y tags de la version actual de cada objeto. El historial de versiones queda fuera del alcance.'
        })
        restoreTestResult = 'no ejecutada - usa Restore-LocalBackupTest.ps1'
        sensitivity       = 'ALTA. Contiene los datos del blog y la configuracion de Portainer, incluidos hashes de autenticacion. No versionar, no compartir, no subir a la nube.'
        secretsIncluded   = 'ninguno: este manifiesto no registra contrasenas ni tokens'
    }

    $manifestPath = Join-Path $setPath 'manifest.json'
    $manifest | ConvertTo-Json -Depth 6 | Out-File -FilePath $manifestPath -Encoding utf8
    Write-Ok 'manifest.json'

    # --- Resumen ------------------------------------------------------------
    Assert-MainEnvironmentIntact | Out-Null

    $totalBytes = ($artifacts | Measure-Object -Property Bytes -Sum).Sum
    Write-Step 'Backup completado'
    Write-Host "    Conjunto : $setId"
    Write-Host "    Ruta     : $setPath"
    Write-Host "    Archivos : $($artifacts.Count)"
    Write-Host "    Tamano   : $(Format-Size $totalBytes)"
    Write-Host ''
    Write-Warn 'Los artefactos son SENSIBLES. No los versiones ni los compartas.'
    Write-Info 'Verifica la integridad con:  .\Test-LocalBackup.ps1'
    Write-Info 'Prueba la restauracion con:  .\Restore-LocalBackupTest.ps1'

    return $setPath
}
catch {
    Write-Host ''
    Write-Host "BACKUP FALLIDO: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
