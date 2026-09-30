# Runbook — Recuperar o reconstruir un despliegue

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
| **Entorno ejecutable hoy** | Laboratorio AWS local exclusivamente |
| **Recupera** | Ausencia total o `apply` parcial con estado conservado |
| **No recupera** | Estado perdido, DB, secretos reales ni datos no respaldados |

## 1. Clasificar antes de actuar

| Situación observada | Acción |
| --- | --- |
| APIs vacías y estado existente/vacío | Reconstrucción con `recuperar` |
| `apply` interrumpido, estado conservado | Reconciliación con `recuperar` |
| Drift local controlado del SSM de ensayo | Reconciliación estrecha; el ciclo canónico la demuestra |
| Estado ausente pero APIs con recursos | **ABORTAR**; no aplicar ni destruir a ciegas |
| Artefacto/manifiesto sin procedencia | **ABORTAR** y reconstruir desde un `ref` aprobado |
| Incidente de datos o DB | Fuera de alcance; escalar al mecanismo de backup aprobado |

## 2. Preparar laboratorio y artefacto

Desde el directorio padre de los repositorios:

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

Push-Location $Task026Infra
python scripts/laboratorio/laboratorio.py --modo local levantar --lambda-zip $Task026Zip
Pop-Location
```

## 3. Recuperar con estado conservado

```powershell
Push-Location $Task026Infra
python scripts/laboratorio/laboratorio.py --modo local recuperar --lambda-zip $Task026Zip
Pop-Location
```

El plan puede contener únicamente `create` y `update`; cualquier `delete`, reemplazo o
tipo ajeno aborta. El operador revisa y confirma con `APLICAR <sha256-completo>`. Después
se exige inventario, inspección `boto3`, runtime correcto y `/health` = 200.

Si el plan no se puede explicar por la ausencia o el `apply` parcial observado,
**ABORTAR**, incluso si la lista cerrada lo permitiría.

> **Actualizado el 2026-09-29 por `Task/030` (DEF-030-2), pendiente de su aprobación
> final.** `recuperar` reconcilia primero **medios** y después **aplicación**. Si el bucket
> falta, su root se crea —con su propio plan y su propia confirmación— **antes** de tocar
> aplicación; si está sano, su plan sale sin cambios y se conserva **sin apply ni
> confirmación**; un **reemplazo** de medios se rechaza antes del apply; un fallo en medios
> impide continuar. El contrato nombre/ARN se obtiene antes del root de aplicación.
> Evidencia: **pruebas controladas** de integración; no se provocó un incidente real
> (§27.4 del [reporte de Task/030](../task-reports/TASK-030-report.md)).

## 4. Ensayo canónico completo

Para certificación local —no para una operación humana de producción— existe un ciclo
autocontenido:

```powershell
Push-Location $Task026Infra
python scripts/laboratorio/laboratorio.py --modo local ciclo --lambda-zip $Task026Zip
python scripts/laboratorio/laboratorio.py --modo local bajar
Pop-Location
```

El ciclo ejecuta CREATE → VALIDATE → inspección con `boto3` → segundo plan → drift
controlado → reconciliación → DESTROY → ausencia → RECONSTRUCCIÓN → smoke → segundo
DESTROY → ausencia. El drift permitido es exactamente
`/blog-lab/local/storage_region`; el plan debe recrear su dirección Terraform y, fuera
de ella, sólo puede aparecer H-025-1 (`aws_ssm_parameter.tags_all`).

## 5. Estado perdido o incoherente

En Windows, el estado local vive normalmente bajo
`$env:LOCALAPPDATA/personal-blog-infra/estado/local/`; si se definió
`PERSONAL_BLOG_CACHE`, deriva de su directorio padre. Nunca está en Git ni dentro de
Floci.

> **Actualizado el 2026-09-28** por la enmienda `Task/030 H-030-4-root-medios`. Ahora hay
> **dos estados, uno por root**, cada uno en su subdirectorio:
>
> - `estado/local/aplicacion/terraform.tfstate` — función, API, parámetros, logs y rol;
> - `estado/local/medios/terraform.tfstate` — bucket de medios.
>
> Antes había un único `estado/local/terraform.tfstate`. Si encuentras esa ruta, es de una
> ejecución anterior a la enmienda: **consérvala como evidencia y no la reutilices**. El
> orden de recuperación es el de creación —medios primero, porque el grafo de aplicación
> recibe su nombre y su ARN como entradas— y el de destrucción es el inverso.

Si falta y las APIs aún muestran recursos:

1. no ejecutes `apply`, `destroy`, `state rm` ni importaciones improvisadas;
2. conserva Floci y el almacenamiento actual;
3. registra inventario, rutas de estado y último artefacto conocido;
4. restaura una copia válida del estado si existe;
5. si no existe, abre una decisión humana para importar o retirar recursos uno a uno.

El laboratorio no usa backend S3: sus states son locales por diseño. *(Hasta `Task/030`
esta frase decía que el bucket de state no existía; desde el 2026-09-28 existe, pero solo
guarda states productivos, nunca los del laboratorio.)*

## 6. Cuando Floci no alcance paridad

- Si la API no existe o diverge sin afectar seguridad, registrar el caso en la matriz y
  dejar la comprobación AWS-only.
- Si la divergencia afecta IAM, privacidad S3, cifrado, alarmas o endpoint público, no
  declarar recuperación productiva: Floci no es autoridad.
- Si impide identificar destino, revisar plan, destruir o verificar ausencia, detener la
  operación. No sustituir evidencia por “el contenedor se apagó”.
- No añadir `ignore_changes`, recursos alternativos ni condicionales locales al grafo.

## 7. Transición futura a AWS real

Antes del primer intento real se requieren: bootstrap del estado, identidad efímera,
presupuesto, `tfvars` aprobado, locks, backups, observabilidad y ventana de cambio. Se
ejecutará primero `init`/`plan` sin mutación, se verificará la cuenta real autorizada y se
repetirán los gates AWS-only. Hasta entonces `--modo production` debe fallar cerrado.
