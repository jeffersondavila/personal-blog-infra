# Runbook — Rollback de una versión

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/026` (2026-09-15) |
| **Entorno ejecutable hoy** | Laboratorio AWS local; AWS real pendiente |
| **Mecanismo** | `ref` aprobado anterior → reconstruir → plan `update` → validar |
| **No cubre** | Rollback de base de datos ni restauración de estado Terraform perdido |

## 1. Criterio de decisión

Hacer rollback sólo cuando una versión recién desplegada causa una regresión atribuible
al artefacto y existe un `ref` anterior **aprobado y compatible**. Ejemplos: `/health`
deja de responder, el handler falla al arrancar o aumenta de forma sostenida el error del
camino crítico.

No hacer rollback cuando el incidente es pérdida de estado, indisponibilidad de Floci,
credenciales/destino dudosos, corrupción de datos o una migración incompatible. En esos
casos, **ABORTAR** y usar [deployment-recovery.md](deployment-recovery.md) o escalar. Este
proyecto no tiene un mecanismo aprobado de rollback de DB.

## 2. Identificar una fuente anterior aprobada

El operador debe aportar el `ref`; el runbook no lo elige automáticamente:

```powershell
$Task026Workspace = (Resolve-Path .).Path
$Task026Infra = Join-Path $Task026Workspace 'personal-blog-infra'
$Task026Backend = Join-Path $Task026Workspace 'personal-blog-backend'
$Task026PreviousRef = '<REF_APROBADO_ANTERIOR>'

git -C $Task026Backend rev-parse --verify "$Task026PreviousRef^{commit}"
git -C $Task026Backend show --no-patch --format='%H %cI %s' $Task026PreviousRef
```

Si el commit no existe o su aprobación/procedencia no puede demostrarse, **ABORTAR**.

## 3. Reconstruir en un worktree aislado

```powershell
$Task026RollbackTree = Join-Path $Task026Workspace '.task026-rollback-backend'
if (Test-Path -LiteralPath $Task026RollbackTree) { throw 'La ruta aislada ya existe; revisar y abortar.' }

git -C $Task026Backend worktree add --detach $Task026RollbackTree $Task026PreviousRef
Push-Location $Task026RollbackTree
python scripts/empaquetar_lambda.py construir --destino lambda_package/rollback
python scripts/empaquetar_lambda.py verificar lambda_package/rollback
$Task026RollbackZip = Join-Path $Task026RollbackTree 'lambda_package/rollback/personal-blog-backend-lambda.zip'
Get-FileHash -Algorithm SHA256 -LiteralPath $Task026RollbackZip
Pop-Location
```

Nunca use como entrada el SHA histórico de Task/024 sin reconstruir: aquel hash es
evidencia de una ejecución, no un registro de artefactos.

## 4. Plan y apply del rollback

```powershell
Push-Location $Task026Infra
python scripts/laboratorio/laboratorio.py --modo local rollback --lambda-zip $Task026RollbackZip
Pop-Location
```

El gate exige:

- sólo acciones `update`;
- al menos una actualización de `aws_lambda_function`;
- ningún `create`, `delete` ni reemplazo;
- únicamente H-025-1 como divergencia local adicional;
- confirmación exacta `APLICAR <sha256-completo-del-plan>`;
- `/health` = 200 e inventario con `boto3` tras aplicar.

Si el ZIP anterior produce el mismo código y el plan no actualiza Lambda, el comando
aborta: no se declarará un rollback inexistente.

## 5. Limpieza del worktree

Sólo después de validar y comprobar que el worktree no tiene cambios rastreados:

```powershell
git -C $Task026RollbackTree status --short
git -C $Task026Backend worktree remove $Task026RollbackTree
```

`worktree remove` sin `--force` debe negarse si hay material no recuperable. No uses
fuerza para convertir una limpieza fallida en éxito.

## 6. AWS real

El criterio será el mismo, pero requerirá además versiones/alias de Lambda, métricas y
ventana de observación aprobadas. Nada de eso se simula con Floci y el modo producción
permanece bloqueado.
