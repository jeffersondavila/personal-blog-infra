# Runbook — Validar un despliegue

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/026` (2026-09-15) |
| **Entorno ejecutable hoy** | Laboratorio AWS local exclusivamente |
| **Entrada** | Despliegue creado y el mismo ZIP/manifiesto usado al crear |
| **Resultado** | Inventario, configuración, SDK, runtime y camino crítico verificados |

## 1. Preparación

Define las rutas desde el directorio padre de los repositorios:

```powershell
$Task026Workspace = (Resolve-Path .).Path
$Task026Infra = Join-Path $Task026Workspace 'personal-blog-infra'
$Task026Zip = Join-Path $Task026Workspace 'personal-blog-backend/lambda_package/task026/personal-blog-backend-lambda.zip'

Test-Path -LiteralPath $Task026Zip
git -C $Task026Infra branch --show-current
```

Resultado esperado: `True` y `Task/026-Runbooks-de-Despliegue`.

## 2. Validación canónica

```powershell
Push-Location $Task026Infra
python scripts/laboratorio/laboratorio.py --modo local validar --lambda-zip $Task026Zip
Pop-Location
```

El comando revalida el destino antes de `init`, congela el artefacto, fija el runtime y
realiza estas comprobaciones:

| Plano | Evidencia exigida |
| --- | --- |
| Destino | modo local, ocho endpoints loopback, región `us-east-1`, cuenta `000000000000` |
| Perímetro | un solo binding `4566/tcp -> 127.0.0.1:4566` |
| S3 | bucket, versionado/configuración y objeto de prueba; privacidad efectiva queda AWS-only |
| SSM | cuatro parámetros legibles; `SecureString` local no demuestra cifrado |
| IAM | rol y política creados; Floci no demuestra enforcement |
| Lambda | runtime, handler, arquitectura, memoria, timeout y paquete |
| API | `GET /health` HTTP 200 por API Gateway v2 → Lambda |
| Runtime | ID de imagen observado igual al digest del manifiesto Task/024 |
| Logs | grupo presente y eventos recuperados sin secretos evidentes |
| SDK oficial | `boto3` del ZIP encuentra S3, SSM, IAM, Lambda, API y Logs |

## 3. Inspección SDK aislada

Para repetir sólo el inventario oficial sin volver a ejecutar el smoke:

```powershell
Push-Location $Task026Infra
python scripts/laboratorio/laboratorio.py --modo local inspeccionar-sdk --lambda-zip $Task026Zip
Pop-Location
```

No requiere AWS CLI ni `boto3` del host: el SDK se importa del ZIP canónico y recibe
credenciales ficticias/endpoints explícitos. Si el ZIP no contiene un SDK importable o
algún recurso esperado falta, aborta; no recurre silenciosamente al host.

## 4. Cómo interpretar el resultado

Un PASS local significa **hipótesis compatible con AWS**, no paridad completa. En
particular, no cerrar con Floci:

- privacidad/autorización S3;
- mínimo privilegio IAM;
- cifrado de SSM SecureString;
- alarmas CloudWatch;
- endpoint público, cuotas, latencia ni costo.

Esos puntos se vuelven gates AWS-only en Stage 10.

## 5. Si Floci no tiene paridad

1. **ABORTAR** sólo la afirmación afectada; no declarar toda la operación válida.
2. Capturar servicio, llamada, estado, respuesta y versión/digest del emulador.
3. Consultar `docs/architecture/aws-local-parity.md`.
4. Si la diferencia ya está demostrada —por ejemplo H-025-1— usar exclusivamente la
   excepción estrecha existente.
5. Si es nueva, no añadir `ignore_changes`, condicionales ni recursos alternativos al
   Terraform compartido. Registrar el hallazgo y dejar el gate como AWS-only.
6. Si afecta el camino crítico o una destrucción segura, detener el cierre de Task/026.

## 6. Criterio de salida

Validación exitosa = todas las comprobaciones ejecutables terminan en cero y cada
limitación queda nombrada. Continúa con rollback sólo si se activa su criterio; de lo
contrario, conserva el despliegue o usa [deployment-destroy.md](deployment-destroy.md).
