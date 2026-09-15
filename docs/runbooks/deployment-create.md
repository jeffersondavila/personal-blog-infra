# Runbook — Crear un despliegue

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/026` (2026-09-15) |
| **Entorno ejecutable hoy** | Laboratorio AWS local exclusivamente |
| **Resultado** | Infraestructura creada, inventariada y `GET /health` = 200 |
| **No hace** | AWS real, DB, backend remoto ni publicación de artefactos |

## 1. Condiciones de entrada

- Ejecutar desde el directorio padre que contiene los tres repositorios.
- Infra en `Task/026-Runbooks-de-Despliegue`; backend y frontend limpios.
- Docker Desktop operativo.
- Consola sin variables AWS, perfiles, proxies ni `TF_CLI_ARGS*`. La guarda aborta si
  encuentra una; no la suprimas para continuar: abre una consola limpia.
- Inventario local vacío. `crear` rechaza recursos previos.

Comprueba sólo los **nombres** de variables sensibles, nunca sus valores:

```powershell
$Task026VariablesPeligrosas = Get-ChildItem Env: | Where-Object {
  $_.Name -match '^(AWS_|TF_CLI_ARGS|HTTP_PROXY$|HTTPS_PROXY$|ALL_PROXY$)'
} | Select-Object -ExpandProperty Name
$Task026VariablesPeligrosas
```

Resultado esperado: ninguna línea. Si aparece una, **ABORTAR**.

## 2. Construir y verificar el artefacto canónico

```powershell
$Task026Workspace = (Resolve-Path .).Path
$Task026Infra = Join-Path $Task026Workspace 'personal-blog-infra'
$Task026Backend = Join-Path $Task026Workspace 'personal-blog-backend'
$Task026Paquete = Join-Path $Task026Backend 'lambda_package/task026'
$Task026Zip = Join-Path $Task026Paquete 'personal-blog-backend-lambda.zip'

Push-Location $Task026Backend
python scripts/empaquetar_lambda.py construir --destino lambda_package/task026
python scripts/empaquetar_lambda.py verificar lambda_package/task026
Pop-Location

Get-FileHash -Algorithm SHA256 -LiteralPath $Task026Zip
git -C $Task026Backend status --short
```

Resultado esperado: verificación correcta, SHA-256 visible y ningún cambio rastreado.
El ZIP, `.sha256`, `manifiesto.json` y `construccion.json` permanecen ignorados.

## 3. Arrancar el laboratorio y demostrar el destino

```powershell
Push-Location $Task026Infra
python scripts/laboratorio/laboratorio.py --modo local herramientas
python scripts/laboratorio/laboratorio.py --modo local levantar --lambda-zip $Task026Zip
Pop-Location
```

Antes de cualquier Terraform deben aparecer:

- `modo=local`, región `us-east-1` y ocho endpoints en `127.0.0.1`;
- cuenta `000000000000`;
- `4566/tcp -> 127.0.0.1:4566` como **único** binding;
- red de ejecución sin salida TCP ni metadata link-local;
- runtime de Task/024 fijado por digest.

Ausencia o discrepancia en cualquiera de esas señales significa **ABORTAR**.

## 4. Plan, revisión humana y apply

```powershell
Push-Location $Task026Infra
python scripts/laboratorio/laboratorio.py --modo local crear --lambda-zip $Task026Zip
Pop-Location
```

El comando:

1. demuestra inventario vacío;
2. ejecuta `init`, `fmt`, `validate` y guarda el `plan`;
3. permite sólo acciones `create` sobre la lista cerrada de Task/025;
4. muestra el plan y su SHA-256;
5. se detiene hasta que el operador escriba exactamente
   `APLICAR <sha256-completo>`;
6. vuelve a comprobar artefacto, destino, binding e identidad;
7. aplica, recorre las APIs, ejecuta `/health` y consulta de nuevo con `boto3` tomado
   del propio ZIP.

No hay `--force`. Si el plan contiene `update`, `delete`, reemplazos o tipos ajenos,
**ABORTAR** y conservar la salida para diagnóstico.

## 5. Criterio de salida

Se considera creado sólo si coinciden todas estas evidencias:

- Terraform terminó con código 0.
- S3, los cuatro SSM, IAM, Lambda, API Gateway v2 y Logs aparecen en inventario.
- `boto3/<versión>` encuentra los mismos recursos mediante endpoints loopback.
- El runtime observado coincide con el digest del manifiesto.
- `GET /health` atravesó API Gateway v2 → Lambda y devolvió HTTP 200.

Continúa con [deployment-validate.md](deployment-validate.md). No retires el laboratorio.

## 6. AWS real — preparado, no ejecutable

El mismo grafo se reutilizará, pero **este comando rechaza `--modo production`**. Antes de
habilitarlo harán falta, como mínimo: cuenta autorizada, OIDC/credenciales efímeras,
presupuesto, bootstrap separado del bucket S3 de estado, `tfvars` productivo aprobado y
validación de S3/IAM/KMS/alarms en AWS. Hoy, intentar producción debe abortar.
