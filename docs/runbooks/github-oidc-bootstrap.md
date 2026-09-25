# Bootstrap GitHub OIDC → AWS

**Borrador operativo, no ejecutado.** Diseño de trabajo aceptado para Task/028;
checkpoint local del **2026-09-22**, tarea **En progreso**. Los pasos AWS/GitHub
requieren autorizaciones posteriores concretas. Este documento no las concede.
No abrir CloudShell, ejecutar AWS CLI autenticada ni publicar durante el checkpoint.

## 1. Alcance y requisitos previos

Solo el root [bootstrap/github-oidc](../../bootstrap/github-oidc/main.tf), separado
del grafo de aplicación Task/025. Recursos previstos: un rol
`PersonalBlogGitHubOidcValidation` y, únicamente en caso A, un proveedor IAM OIDC.
Sin buckets, application IAM, permisos Terraform, DynamoDB ni otras políticas.

El usuario opera en AWS Console con MFA y asume `PersonalBlogAdministrator`.
No usar root ni crear access keys. Confirmar privadamente cuenta y región previstas;
el agente no solicita ni ve password, TOTP, recovery codes, PAT, access keys,
JWT ni credenciales STS. GetCallerIdentity comprueba identidad, **no demuestra MFA**:
el login humano es una evidencia separada.

Antes de cualquier futura operación: autorización de su alcance, código revisado
identificado por digest, Terraform **1.16.2** y provider **6.64.0** con lock del repo,
Python 3.12+, AWS CLI v2 y GnuPG disponibles. Verificar procedencia/checksums de
herramientas. No habilitar debug, `set -x`, `TF_LOG`, endpoints alternativos, perfiles
ajenos, plugins/CLI args Terraform inyectados ni segundo escritor.

El paquete revisado puede transferirse manualmente a CloudShell sin publicar Git.
Debe contener fuentes/lock/scripts y ningún archivo privado, estado, plan o token.
La preparación/transferencia de ese paquete pertenece a la operación futura
autorizada; **no se prepara en el checkpoint**. Trabajar desde su raíz de infra.

## 2. EX-028-C7: custodia temporal

**Excepción aceptada como diseño de trabajo**, no aprobación de tarea ni permiso
de crear recursos. D-06 permanece Resuelta y Vigente desde Task/025.

| Propiedad | Contrato |
| --- | --- |
| Alcance | Solo `bootstrap/github-oidc/`; no aplicación ni backend de CI |
| Estado | `$HOME/.local/state/personal-blog/bootstrap/github-oidc/terraform.tfstate` |
| Configuración, planes y TF_DATA_DIR | Fuera de todo checkout Git, incluso de rutas ignoradas |
| Protección | umask 077; directorios 0700; archivos 0600; propietario humano |
| Concurrencia | Un escritor, workspace default, lock local activado; no force-unlock sin diagnóstico |
| Copias | Antes/después de mutaciones y tras fallo parcial; cifradas y fuera de CloudShell |
| Revisión | A los 30 días de la primera creación cloud, fecha registrada en evidencia privada |
| Extinción | Task/030, antes del primer apply de infraestructura de aplicación |
| C-7 | **No PASS literal**: excepción acotada hasta migración comprobada a S3 |

CloudShell cifra el almacenamiento persistente, pero retiene HOME solo hasta
120 días desde el último uso: no sustituye un backup externo.
[Cifrado](https://docs.aws.amazon.com/cloudshell/latest/userguide/data-encryption.html)
y [retención](https://docs.aws.amazon.com/general/latest/gr/cloudshell.html).

**Comandos futuros, solo después de autorización:**

```bash
set -euo pipefail
umask 077
export OIDC_PRIVATE="$HOME/.local/state/personal-blog/bootstrap/github-oidc"
export TF_DATA_DIR="$OIDC_PRIVATE/terraform-data"
export TF_WORKSPACE=default
install -d -m 0700 "$OIDC_PRIVATE" "$TF_DATA_DIR" "$OIDC_PRIVATE/snapshots"
export OIDC_STATE="$OIDC_PRIVATE/terraform.tfstate"
export OIDC_CONFIG="$OIDC_PRIVATE/config.private.json"
export OIDC_INVENTORY="$OIDC_PRIVATE/inventory.private.json"
export OIDC_PLAN="$OIDC_PRIVATE/reviewed.tfplan"
```

Crear privadamente `config.private.json` con exactamente estas claves; sustituir
marcadores en el editor humano. No son credenciales. La caducidad se elige como
**literal UTC futuro, máximo dos horas**, sin timestamp automático ni renovación.

```json
{
  "expected_account_id": "<CUENTA_CONFIRMADA_PRIVADAMENTE>",
  "aws_region": "<REGION_CONFIRMADA>",
  "trust_phase": "task",
  "task_expires_at": "<LITERAL_UTC_YYYY-MM-DDTHH:MM:SSZ>"
}
```

```bash
chmod 0600 "$OIDC_CONFIG"
python3 - <<'PY'
import json, os
from pathlib import Path
p = Path(os.environ["OIDC_PRIVATE"]) / "local.tfbackend"
p.write_text("path = " + json.dumps(os.environ["OIDC_STATE"]) + "\n")
p.chmod(0o600)
PY
```

No poner credenciales en variables Terraform ni en backend. Nunca usar
`terraform init` sin este backend-config para operaciones reales: el backend
local vacío por defecto apuntaría al checkout. Las guardas rechazan rutas en Git;
el plan-check además vincula el backend inicializado al estado externo esperado.

## 2.1 Entornos de operación soportados

Dos, ambos explícitos; cualquier otro se rechaza con `UNSUPPORTED_PLATFORM`.

| Entorno | Credenciales | Invocación |
| --- | --- | --- |
| **CloudShell (Linux)** | sesión ambiental del contenedor | sin `--aws-profile`; un perfil nombrado se rechaza (`CLOUDSHELL_PROFILE_FORBIDDEN`) |
| **Estación Windows** | perfil nombrado renovado por `aws login` | `--aws-profile personal-blog` obligatorio (`LOCAL_PROFILE_REQUIRED`) |

El perfil viaja como **argumento explícito** hacia cada llamada `aws`, nunca como
entorno heredado: `AWS_PROFILE` y `AWS_DEFAULT_PROFILE` presentes se rechazan
(`IMPLICIT_PROFILE`), porque decidirían el destino sin aparecer en el comando
revisado. Las claves de larga vida siguen prohibidas: si hay `AWS_ACCESS_KEY_ID`
debe ser de sesión (`ASIA…`) y traer su `AWS_SESSION_TOKEN`.

**Límite declarado.** El código **no** prueba que el perfil `personal-blog` obtenga
sus credenciales de `aws login`: averiguarlo exigiría leer `~/.aws/credentials` o la
caché de sesión, prohibido por diseño. Lo que sí queda probado es más útil: la
identidad efectiva debe ser una **sesión STS asumida** de `PersonalBlogAdministrator`.
Una clave de usuario IAM de larga vida produce un ARN `iam::…:user/…` y la guarda de
identidad la rechaza. El mecanismo concreto del perfil es responsabilidad del
operador; la naturaleza temporal de la credencial efectiva sí se verifica.

En Windows no existe el modo POSIX, así que la guarda de rutas privadas exige que
el archivo viva bajo `%LOCALAPPDATA%` y rechaza *reparse points* —junctions y
symlinks que podrían redirigir una ruta ya comprobada—. Es una guarda de **ámbito**,
no una auditoría de ACL: la ACL sigue siendo responsabilidad del operador.

Ninguna otra guarda cambia: destino de cuenta, identidad humana, rechazo de root,
estado, trust, proveedor, políticas y la prohibición de destroy/import/target son
idénticas en los dos entornos.

**El estado de Terraform es único y vive donde se creó.** Operar desde el otro
entorno no lo duplica: una segunda copia activa está prohibida (§4).

## 3. Inventario y lifecycle A/B/C

Ejecutar el inventario de solo lectura **después de su autorización**, desde la
raíz del código revisado:

```bash
python3 -B -m scripts.oidc.bootstrap inventory --aws-real --config "$OIDC_CONFIG" --state "$OIDC_STATE" --inventory "$OIDC_INVENTORY"
```

La herramienta comprueba cuenta/principal humano, rutas privadas, estado,
`GetOpenIDConnectProvider`, `GetRole`, `ListAttachedRolePolicies` y
`ListRolePolicies`; captura las respuestas sin imprimir cuerpos ni errores crudos.
Guarda inventario y tfvars privados. Solo imprime caso/ownership o un STOP genérico.
Ante STOP, investigar **privadamente**, sin compartir salidas crudas.

| Caso observado realmente | Acción permitida |
| --- | --- |
| A: GetOpenIDConnectProvider devuelve exactamente NoSuchEntity | Terraform puede crear el proveedor; registrar A |
| B: existe con URL GitHub exacta y lista de clientes exactamente `["sts.amazonaws.com"]` | Data source; sin import, ownership ni eliminación por este root |
| C: URL/audiencia discrepan, respuesta incompleta o lectura no concluyente | STOP; no modificar, importar ni arreglar |
| Continuación de A: proveedor existe y ARN/dirección pertenecen al estado custodiado | Conservar ownership A; nunca reclasificar como compartido B |

La API IAM normaliza URL sin prefijo https; ambas representaciones equivalentes
se comparan con el hostname exacto, sin comodines ni URLs alternativas.
NoSuchEntity es la única prueba de ausencia: AccessDenied, red o JSON vacío no lo son.
Un rol preexistente sin estado correspondiente también detiene la operación.
No cambiar `provider_mode` manualmente para eludir la guarda.

Para GitHub, AWS utiliza su cadena de CAs de confianza: no se inventa thumbprint
ni se modifica el existente. Se registra lo observado. Las condiciones aud/sub
son de la trust del rol, no atributos del proveedor.
[Contrato del provider fijado](https://github.com/hashicorp/terraform-provider-aws/blob/v6.64.0/website/docs/r/iam_openid_connect_provider.html.markdown).

Antes de operar, reconfirmar por lectura la configuración OIDC del repositorio:
`use_default=true`, `use_immutable_subject=true` y prefijo
`repo:jeffersondavila@60154716/personal-blog-infra@1313255836`.
Si cambió, detener y revisar; no reconfigurar automáticamente GitHub.
[Subjects inmutables](https://docs.github.com/en/actions/reference/security/oidc).

## 4. Snapshots, cifrado y recuperación

Con un único escritor detenido, copiar estado/config/inventario y lock a un
directorio fechado privado. Antes de primera creación, registrar **estado ausente**
en lugar de inventarlo. Después de un fallo, conservar también cualquier estado
parcial y `.backup`, sin restaurar encima ni repetir apply automáticamente.

```bash
snapshot_dir="$OIDC_PRIVATE/snapshots/$(date -u +%Y%m%dT%H%M%SZ)"
install -d -m 0700 "$snapshot_dir"
for file in "$OIDC_CONFIG" "$OIDC_INVENTORY" "$OIDC_STATE" "$OIDC_STATE.backup"; do
  if test -f "$file"; then cp -p -- "$file" "$snapshot_dir/"; fi
done
cp -- bootstrap/github-oidc/.terraform.lock.hcl "$snapshot_dir/provider.lock.hcl"
if ! test -f "$OIDC_STATE"; then printf 'state absent before creation\n' > "$snapshot_dir/state-absent.txt"; fi
find "$snapshot_dir" -type f -exec chmod 0600 {} +
(cd "$snapshot_dir" && sha256sum -- * > SHA256SUMS)
tar -C "$snapshot_dir" -cf "$snapshot_dir.tar" .
gpg --symmetric --cipher-algo AES256 --no-symkey-cache --output "$snapshot_dir.tar.gpg" "$snapshot_dir.tar"
chmod 0600 "$snapshot_dir.tar.gpg"
```

GnuPG solicita la frase **solo en su interfaz privada**; jamás argumento, variable,
archivo versionado ni chat. Descargar manualmente el `.gpg` a
`%LOCALAPPDATA%\PersonalBlog\bootstrap-backups\github-oidc\`, protegido por ACL del
usuario, y a un medio externo protegido independiente del equipo. Separar la
custodia del secreto de cifrado. Verificar digest del cifrado en ambos destinos.
No cargar copias a artifacts GitHub ni usar el bucket de medios/backups.

**Prueba de recuperación obligatoria antes de confiar en la copia:** descifrar una
copia descargada, en directorio privado distinto y sin inicializar otro backend:

```bash
recovery_dir="$OIDC_PRIVATE/recovery-check"
install -d -m 0700 "$recovery_dir"
gpg --no-symkey-cache --output "$recovery_dir/snapshot.tar" --decrypt "$snapshot_dir.tar.gpg"
tar -xf "$recovery_dir/snapshot.tar" -C "$recovery_dir"
(cd "$recovery_dir" && sha256sum -c SHA256SUMS)
python3 - "$snapshot_dir" "$recovery_dir" <<'PY'
import json, sys
from pathlib import Path
left, right = (Path(p) / "terraform.tfstate" for p in sys.argv[1:])
if left.exists():
    a, b = (json.loads(p.read_text()) for p in (left, right))
    assert (a["lineage"], a["serial"], a["resources"]) == (b["lineage"], b["serial"], b["resources"])
else:
    assert not right.exists()
print("RECOVERY_CONTENT_OK; no second writer started")
PY
```

El checksum cubre contenido; comparar además lineage, serial y direcciones de
recursos privadamente. Registrar resultado/fecha sin estado crudo. Tras verificar,
el usuario retira plaintext de snapshots/tar/recuperación conforme a su retención
privada; conserva estado operativo y copias cifradas. No usar borrados recursivos
automáticos ni asegurar borrado físico en almacenamiento gestionado.

Para desastre: detener todos los escritores, recuperar la última copia conocida,
comparar inventario real y estado antes de refresh/plan. Si falta estado, no
importar ni adoptar automáticamente recursos existentes; STOP y plan de recuperación
revisado. Nunca una segunda copia de estado activa.

## 5. Plan humano y apply limitado

Tras inventario A/B, copia previa verificada y autorización concreta del plan:

```bash
terraform -chdir=bootstrap/github-oidc init -input=false -lockfile=readonly -backend-config="$OIDC_PRIVATE/local.tfbackend" > "$OIDC_PRIVATE/init.log" 2>&1
terraform -chdir=bootstrap/github-oidc plan -input=false -lock=true -lock-timeout=30s -var-file="$OIDC_PRIVATE/bootstrap.auto.tfvars.json" -out="$OIDC_PLAN" > "$OIDC_PRIVATE/plan.log" 2>&1
terraform -chdir=bootstrap/github-oidc show -json "$OIDC_PLAN" > "$OIDC_PRIVATE/plan.private.json"
python3 -B -m scripts.oidc.bootstrap plan-check --config "$OIDC_CONFIG" --state "$OIDC_STATE" --inventory "$OIDC_INVENTORY" --plan "$OIDC_PRIVATE/plan.private.json"
sha256sum "$OIDC_PLAN" > "$OIDC_PRIVATE/reviewed-plan.sha256"
```

Inventario máximo 10 minutos; si vence, repetir inventario/plan/revisión. El revisor
humano examina el plan en privado y aprueba **su digest**. No publicar plan binario,
JSON, tfvars, backend metadata ni logs. La guarda exige solo rol/proveedor previsto,
variables/destino exactos, sin imports, drift, módulos, políticas, destroy,
reemplazos ni cambios de provider. Un plan con cualquier otra cosa se rechaza.

Creación: A máximo dos recursos; B un rol y referencia data. Transición: únicamente
cambiar assume_role_policy Task → main; no renovación ni ampliación automática.
Validar otra vez identidad/inventario y que no cambió código, configuración ni estado
antes de consumir exactamente el plan aprobado.

**Solo después de autorización de apply**, no en este checkpoint:

```bash
sha256sum -c "$OIDC_PRIVATE/reviewed-plan.sha256"
terraform -chdir=bootstrap/github-oidc apply -input=false -lock=true -lock-timeout=30s "$OIDC_PLAN" > "$OIDC_PRIVATE/apply.log" 2>&1
python3 -B -m scripts.oidc.bootstrap inventory --aws-real --verify-target --config "$OIDC_CONFIG" --state "$OIDC_STATE" --inventory "$OIDC_INVENTORY"
```

No `-auto-approve`, `-target`, `-replace`, `-refresh=false` ni `-lock=false`.
Aplicar un plan guardado no pide aprobación interactiva: **la autorización humana
del digest anterior es indispensable**. Después, snapshot/cifrado/copia externa y
recuperación; nuevo plan sin cambios y readback IAM exacto. Si apply falla,
snapshot parcial, STOP e inventario; no reintentar a ciegas.

El **plan posterior sin cambios** se acredita con el propio Terraform:
`-detailed-exitcode` en 0 y `resource_drift` vacío. **No** se reejecuta `plan-check`
sobre él: esa guarda es la puerta previa al apply y revalida la ventana de caducidad,
de modo que rechaza con `EXPIRY_WINDOW` cualquier plan de fase task una vez vencido
el literal, aunque no cambie nada. Es deliberado: un literal vencido no debe poder
aplicarse.

## 6. Trust y sesiones

Principal único: `arn:aws:iam::<CUENTA>:oidc-provider/token.actions.githubusercontent.com`.
Action única `sts:AssumeRoleWithWebIdentity`; aud exacta `sts.amazonaws.com`.

| Fase | StringEquals sub | Condición adicional |
| --- | --- | --- |
| Temporal explícita | `repo:jeffersondavila@60154716/personal-blog-infra@1313255836:ref:refs/heads/Task/028-GitHub-OIDC-AWS` | DateLessThan aws:CurrentTime = literal UTC suministrado |
| Final por defecto | `repo:jeffersondavila@60154716/personal-blog-infra@1313255836:ref:refs/heads/main` | Sin caducidad y sin admitir Task |

Un Statement, sin wildcard, repositorio genérico ni environment. El literal temporal
no se recalcula; si expira antes de probar, STOP y nueva revisión/autorización.
Para transición, editar privadamente solo `trust_phase="main"` y
`task_expires_at=null`; repetir inventario/backup/plan/revisión/apply/readback.
Sustituir la trust completa, no añadir main a la temporal.

MaxSessionDuration del rol = 3600; workflow solicita 900 segundos. No se adjuntan
managed ni inline policies, ni AdministratorAccess/ReadOnlyAccess/permisos aplicación.
`GetCallerIdentity` no necesita un permiso IAM concedido al rol.
[API STS](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html).

## 7. GitHub y pruebas futuras

Cambios futuros sujetos a autorización: publicar workflow/código, configurar solo
variables no secretas `AWS_OIDC_ROLE_ARN`, `AWS_EXPECTED_ACCOUNT_ID` y `AWS_REGION`.
Sin secretos AWS, cambios de subject OIDC, environments ni branch protection aquí.
El repositorio es público y las **variables de Actions no se enmascaran** en los
logs, a diferencia de los secrets: GitHub vuelca el bloque `env:` del job, de modo
que el Account ID y el ARN del rol **sí quedan visibles** en la ejecución. Observado
el 2026-09-24 y **aceptado**: son identificadores, no credenciales (D-028-A). Lo que
nunca debe aparecer en un log es material de autenticación —JWT, access keys, secret
access keys, session tokens—; el verificador no los imprime. Revisar saneamiento
antes de compartir evidencia sigue siendo obligatorio.

El workflow usa acciones fijadas por SHA y permisos de job `contents: read` +
`id-token: write`; otro job sin id-token demuestra solo la limitación del lado
GitHub. Solo push de la Task exacta y dispatch de main, con ID de repositorio/owner
verificados. Nada de dev, tags, PR, pull_request_target ni artifacts.

**Secuencia futura, no preparada ni autorizada en este checkpoint:**

1. Primera publicación premerge, commit + push exclusivamente Task, autorizados
   expresamente: configuración versionada `task_expectation=SUCCESS`, trust temporal
   vigente; JWT genuino → STS → GetCallerIdentity; `iam:ListRoles` debe devolver
   exactamente AccessDenied; audience incorrecta debe devolver InvalidIdentityToken.
2. Humano instala trust final main con procedimiento §5, backup/readback y plan
   sin cambios. Destruir ni ampliar permisos no forma parte de esta transición.
3. Segunda publicación premerge autorizada por separado: cambiar expectativa
   versionada a `DENIED`; JWT **nuevo**, legítimo, de Task debe obtener
   **AccessDenied** de STS. InvalidIdentityToken, timeout, variables ausentes,
   token vencido o error de red **no cuentan**.
4. Cierre Git/PR/merge según autorizaciones posteriores. Después del merge,
   workflow_dispatch desde main espera SUCCESS y repite pruebas. Por ser posterior
   al merge, **no condiciona la aprobación**: es validación **postmerge obligatoria**
   antes de dar por integrada Task/028 y de avanzar a la tarea siguiente. Si falla,
   el avance se detiene y Task/028 se corrige. No inferirlo de pruebas premerge.

El dispatch requiere que el archivo exista en la rama predeterminada; no sirve
para la primera prueba premerge.
[Regla de workflow_dispatch](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch).

Tokens solo en memoria; credenciales STS solo en memoria/entorno del proceso hijo
AWS CLI, nunca argumentos, archivos, outputs, GITHUB_ENV o artifacts. Los errores
imprimen códigos/mensajes fijos. STS verifica la firma; decodificar claims en Python
solo permite una comprobación anticipada de audiencia/subject.

## 8. Evidencia y límites de seguridad

Obligatoria y saneada: caso A/B/C realmente observado, ownership, recursos realmente
creados, **cero managed policies**, **cero inline policies**, trust exacta,
GetCallerIdentity correcto y operaciones negativas específicas con AccessDenied.
Audiencia incorrecta valida la cadena provider/trust, no aísla solo StringEquals aud.
El job sin id-token valida GitHub, no una denegación AWS.

**No se afirma ausencia universal de capacidades en toda AWS.** Una denegación IAM
ListRoles no caracteriza S3, KMS, queues u otros recursos. Una resource-based policy
puede otorgar capacidades sin una policy de identidad adjunta. El inventario actual
del script para resource policies es **vacío**; cualquier inspección humana adicional
debe enumerar exactamente los recursos/policies comprobados y su fecha.
Otras ramas, forks, PR y tags tienen cobertura estática, no pruebas AWS reales,
salvo que existan ejecuciones genuinas posteriormente autorizadas.

## 9. Rollback, revocación y destrucción

Ante cualquier discrepancia: detener publicaciones y operaciones; conservar
evidencia privada/cifrada; no importar/adoptar ni modificar provider compartido.
Cerrar nuevas asunciones mediante trust revisada por el humano, con autorización
de contingencia; restaurar una trust antigua de Task no es rollback automático.
Una caducidad expirada tampoco se renueva automáticamente.

Cambiar trust o eliminar permiso de asumir **no invalida sesiones ya emitidas**:
esperar su expiración (workflow 900 s, límite del rol 3600 s). Si hace falta
revocación inmediata, el humano puede usar la operación IAM de revocar sesiones,
que introduce `AWSRevokeOlderSessions`: es una política temporal, rompe el
invariante cero inline y debe registrarse/reconciliarse antes de repetir evidencias.
GetCallerIdentity puede funcionar aun con denegaciones: no prueba revocación.
[Revocación IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_revoke-sessions.html).

**Prohibido destroy automático.** Terraform tiene prevent_destroy en recursos
propios; el proveedor B solo es data y nunca se elimina desde este estado.
Una limpieza excepcional de recursos A/rol exige inventario de dependencias,
sesiones agotadas, backups y autorización humana específica; no hay comando de
destroy en este runbook ni herramienta de apply/destroy automático.

## 10. Task/030: extinción de la excepción

Task/030 reutiliza los módulos Task/025 de aplicación y tiene excepción explícita
ETAPA 10 para crear el bootstrap D-06: S3 dedicado solo al estado, privado,
versionado, cifrado, public access block, sin DynamoDB y separado de medios/backups.
El backend debe preexistir al grafo dependiente: no duplica el grafo de aplicación.

Su ficha deberá incluir diseño del bootstrap del bucket, custodia de **su propio
estado**, permisos mínimos de backend, costos y recuperación. No implementarlo en
Task/028. Una vez creado/protegido/verificado el bucket, con ambos escritores
detenidos y backups recuperables:

1. Preparar backend S3 en cambio revisado del root OIDC; key
   `bootstrap/github-oidc/terraform.tfstate`, `encrypt=true`,
   `use_lockfile=true`, cuenta/región/bucket verificados, sin credenciales.
2. Ejecutar humanamente `terraform init -migrate-state` con configuración privada;
   nunca sustituir por `-reconfigure` para omitir la migración ni usar force-copy.
3. Comparar lineage, serial, direcciones y contenido; verificar versión S3,
   bloqueo y recuperación; plan sin cambios, un solo backend activo.
4. Migrar o custodiar explícitamente el estado del bootstrap del bucket; resolver
   esa dependencia antes de cerrar la excepción.
5. Archivar cifrado el estado local, retirar su uso como backend y registrar
   extinción EX-028-C7 **antes del primer apply de aplicación**.

## 11. Costos y operaciones pendientes

Estimación del alcance IAM/STS: **USD 0 de cargo adicional** por esos servicios,
consultado el 2026-09-22; no se crean servicios de aplicación. CloudShell mantiene
sus cuotas y GitHub Actions su facturación propia; no se promete costo global cero.
El bucket/migración de Task/030 necesita estimación propia de storage/requests.
[Precios IAM](https://aws.amazon.com/iam/faqs/).

Quedan pendientes todas las operaciones reales, backups/recuperación reales,
observación A/B/C, publicaciones y reconfirmación main. Los mocks locales no
son evidencia cloud. Permisos backend: Task/038; Terraform: Task/039; validación
integral: Task/040. Protección efectiva de main antes de esos roles de despliegue;
el rol de validación nunca se promueve a rol de despliegue.
