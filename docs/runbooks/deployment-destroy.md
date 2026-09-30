# Runbook — Destruir un despliegue

> **Alcance futuro RDS — Task/028.2, aprobada el 2026-09-27.** Este runbook conserva
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

> **Actualizado el 2026-09-29 por `Task/030` (DEF-030-2), aprobada ese mismo día.** Desde la enmienda `H-030-4-root-medios` hay **dos roots**, y `destruir` los
> recorre en orden **inverso** al de creación: primero **aplicación**, que consume el
> bucket, y después **medios**, que lo administra. Cada root tiene su propio plan, su
> propio SHA-256 y su **propia confirmación**.

Para cada root, antes de borrar, el comando ejecuta `terraform plan -destroy`, acepta sólo
`delete` sobre la lista cerrada de tipos y muestra el SHA-256. Revisar el plan y escribir
exactamente `APLICAR <sha256-completo>`:

1. **Aplicación**: función, API, parámetros, logs y rol —13 bajas en el laboratorio—, sin
   ningún `aws_s3_*`. Tras el apply se exigen state y outputs **vacíos**. En ese punto el
   bucket de medios sigue vivo y **es legítimo**: lo administra otro root con su propio
   state. Solo ese nombre exacto se tolera; cualquier otro recurso es residuo.
2. **Medios**: se vacían objetos y versiones del bucket y se revisa su plan —8 bajas, todas
   `aws_s3_*` del módulo `almacenamiento`—. Tras el apply, state y outputs **vacíos** e
   inventario **sin nada**.

Una respuesta abreviada, EOF, `--force`, un tipo nuevo, un reemplazo o un destino
discordante abortan sin aplicar. Se aplica siempre **el plan guardado** de cada root, no
otro plan implícito.

### 2.1. Si `destruir` se interrumpe entre los dos roots

Relanzar `destruir` **no** reanuda: el plan `-destroy` de aplicación sale vacío, la revisión
exige al menos un `delete` y el comando aborta sin llegar a medios. Falla cerrado, pero no
continúa. En ese caso:

- **no** recrear el root de aplicación solo para poder destruirlo;
- comprobar sin mutar que aplicación está a 0 recursos y 0 outputs, que medios conserva
  sus recursos y que el único recurso vivo del proyecto es el bucket de medios;
- decidir **humanamente** cómo completar medios: su plan destructivo guardado solo puede
  usarse si su SHA-256 no cambió, su contenido sigue siendo exactamente los `delete`
  revisados y se revalidaron todas las guardas del destino.

Es una limitación registrada del herramental (§27.9 del
[reporte de Task/030](../task-reports/TASK-030-report.md)).

## 3. Ausencia antes de retirar Floci

Éxito exige simultáneamente:

- `terraform state list` de **los dos roots**: cero direcciones, y cero outputs;
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

El laboratorio deja `terraform-medios` inicializado contra su backend **local**. Antes de
cualquier operación productiva sobre ese root, devolverlo a S3 con el procedimiento del
[runbook del bucket de estado](terraform-state-bootstrap.md), §3: `init -reconfigure` con el
`TF_DATA_DIR` privado, **sin migrar** ningún state.

## 5. AWS real — pendiente

Además de aprobación y guardas de identidad reales, un destroy AWS requerirá política de
retención, backups, revisión de datos y ventana de cambio. Este runbook no autoriza ni
simula esas decisiones; el CLI actual rechaza producción.
