# Runbook — Destruir un despliegue

> **Alcance futuro RDS — Task/028.2, propuesta del 2026-09-27, pendiente de aprobación.** Este runbook conserva
> el alcance probado de Task/026; su inventario actual no cubre red/RDS nuevos.
> Task/031 debe ampliar guardas/inventario, permisos, creación/borrado protegido,
> snapshots/restore/PITR, KMS, SG, endpoint y rollback antes de operar esos recursos.
> Task/036/038 añade migraciones privadas y Task/040 verifica DR/restore integral.
> [Contrato RDS](../architecture/production-postgresql-rds.md). No autoriza AWS ni
> extiende EX-028-C7; D-06 en Task/030 precede al primer apply de aplicación.


| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/026` (2026-09-15) |
| **Peligro** | **DESTRUCTIVO**: elimina todos los recursos administrados del destino |
| **Entorno ejecutable hoy** | Laboratorio AWS local exclusivamente |
| **Resultado** | Estado vacío, APIs sin recursos y Docker sin residuos al retirar el lab |

## 1. Precondiciones y abortos

- Tener el ZIP/manifiesto usados por la configuración actual.
- Confirmar que el objetivo es el laboratorio. `production` debe abortar.
- No continuar si la identidad no es `000000000000` o existe más de un binding.
- No borrar el estado para “arreglar” un destroy: estado vacío no prueba ausencia.
- No detener Floci antes de consultar ausencia; hacerlo elimina al testigo.

```powershell
$Task026Workspace = (Resolve-Path .).Path
$Task026Infra = Join-Path $Task026Workspace 'personal-blog-infra'
$Task026Zip = Join-Path $Task026Workspace 'personal-blog-backend/lambda_package/task026/personal-blog-backend-lambda.zip'
Test-Path -LiteralPath $Task026Zip
```

Si devuelve `False`, **ABORTAR** y reconstruir la misma fuente aprobada.

## 2. Plan destructivo y aprobación humana

```powershell
Push-Location $Task026Infra
python scripts/laboratorio/laboratorio.py --modo local destruir --lambda-zip $Task026Zip
Pop-Location
```

Antes de borrar, el comando ejecuta `terraform plan -destroy`, acepta sólo `delete` sobre
los tipos cerrados de Task/025 y muestra el SHA-256. Revisar que el plan corresponda al
laboratorio completo y escribir exactamente `APLICAR <sha256-completo>`.

Una respuesta abreviada, EOF, `--force`, un tipo nuevo, un reemplazo o un destino
discordante abortan sin aplicar. Después de confirmar, se eliminan objetos/versiones del
bucket local y se aplica **el plan guardado**, no otro plan implícito.

## 3. Ausencia antes de retirar Floci

Éxito exige simultáneamente:

- `terraform state list`: cero direcciones;
- ListBuckets: ningún bucket `blog-lab*`;
- Lambda: ninguna función `blog-lab*`;
- API Gateway v2: ninguna API `blog-lab*`;
- Logs: ningún grupo `/aws/lambda/blog-lab*`;
- SSM: ningún parámetro `/blog-lab*`.

Si el estado queda vacío pero una API conserva recursos, el destroy **falló**. Mantén
Floci activo, captura el inventario y entra al runbook de recuperación.

## 4. Retirar el laboratorio y verificar residuos

Sólo después de la ausencia por APIs:

```powershell
Push-Location $Task026Infra
python scripts/laboratorio/laboratorio.py --modo local bajar
Pop-Location

docker ps -a --filter 'name=personal-blog-lab' --format '{{.Names}}'
docker ps -a --filter 'label=floci=true' --format '{{.Names}}'
docker network ls --filter 'name=personal-blog-lab' --format '{{.Name}}'
docker volume ls --filter 'name=personal-blog-lab' --format '{{.Name}}'
docker volume ls --filter 'label=floci=true' --format '{{.Name}}'
```

Resultado esperado: el comando `bajar` declara cero residuos y las cinco consultas no
imprimen nada.

## 5. AWS real — pendiente

Además de aprobación y guardas de identidad reales, un destroy AWS requerirá política de
retención, backups, revisión de datos y ventana de cambio. Este runbook no autoriza ni
simula esas decisiones; el CLI actual rechaza producción.
