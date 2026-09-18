# TASK-027 — Configurar cuentas y presupuestos

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/027-Configurar-Cuentas-y-Presupuestos` |
| **Nombre** | Configurar cuentas y presupuestos |
| **Etapa** | ETAPA 09 — Cuentas y Seguridad Cloud |
| **Estado** | **Aprobada** el 2026-09-17 — Gates A–E completos |
| **Repositorio modificado** | `personal-blog-infra` |
| **Repositorios en solo lectura** | `personal-blog-backend`, `personal-blog-frontend` |
| **Dependencias** | `Task/026` ✔ · `Task/026.1` ✔ (mantenimiento, no cuenta en las 41) |
| **Rama** | `Task/027-Configurar-Cuentas-y-Presupuestos` |
| **Rama base** | `main` — nunca `dev` |
| **SHA base** | `67c1904944fc624b15c15e466f575f055c5c312d` |
| **Fecha de inicio** | 2026-09-15 |
| **Última actualización** | 2026-09-17 |
| **Reporte** | [TASK-027-report.md](../task-reports/TASK-027-report.md) |

> Esta es la primera tarea que interactúa con proveedores cloud reales. En el checkpoint
> inicial el agente hizo sólo lectura e investigación. Después, el usuario completó
> privadamente Gates A y B: creó ambas cuentas y habilitó/verificó sus MFA. **El agente no
> vio ni registró identificadores, credenciales o material MFA y no ejecutó ninguna
> mutación externa.** La identidad administrativa fue creada y verificada después por el
> usuario mediante los checkpoints autorizados de Gate C. En Gate E el usuario creó y
> verificó el presupuesto y cuatro alertas; no creó recursos de aplicación atribuibles a
> Task/027. El agente no operó AWS ni vio datos privados.

---

## 0. Preparación Git demostrada

Se ejecutaron `fetch --prune`, cambio a `main` y `pull --ff-only` antes de la primera
mutación local. El estado físico comprobado fue:

| Repositorio | `main == origin/main` | Estado adicional | Árbol antes de la rama |
| --- | --- | --- | --- |
| `personal-blog-infra` | `67c1904944fc624b15c15e466f575f055c5c312d` | `dev == origin/dev == e2d77ee2…`; `main` ancestro de `dev`; `dev..main = 0`; diff vacío; 0 ramas Task | limpio |
| `personal-blog-backend` | `4a40364bbd6a444f9469b815d17d2d77a37949ce` | en `main`; 0 ramas Task | limpio |
| `personal-blog-frontend` | `7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce` | en `main`; 0 ramas Task | limpio |

La rama se creó exclusivamente en infra desde `main`. Inmediatamente después:
`HEAD == main == origin/main == 67c19049…`, `main..HEAD = 0` y árbol limpio.

## 1. Objetivo

Establecer y demostrar cuentas AWS y Cloudflare reales con MFA, una identidad humana
administrativa de AWS separada de root, un presupuesto mensual decidido por el usuario y
alertas de costo verificadas, sin desplegar infraestructura de aplicación y dejando una
base segura para que `Task/028` configure OIDC posteriormente.

## 2. Contexto y dependencias heredadas

`Task/026` dejó cinco runbooks vigentes y el modo `production` bloqueado. El Terraform
portable contiene un grafo de aplicación de 21 recursos, pero **no se ejecuta en esta
tarea**. La evidencia de Floci sigue siendo hipótesis local: no demuestra IAM, cifrado,
cuotas, costos ni comportamiento de AWS real.

Se heredan sin reabrir:

- ADR-001: local-first y primera interacción cloud controlada en la ETAPA 09.
- ADR-003: arquitectura serverless AWS de bajo costo.
- D-06: estado Terraform real en S3 con `use_lockfile`, sin DynamoDB; el bucket aún no
  existe y no pertenece a esta tarea.
- ADR-007: PostgreSQL en VPS externo detrás de PgBouncer; la selección es `Task/029`.
- ADR-008: Grafana Cloud + Alloy; D-19 permanece abierta hasta `Task/041`.
- D-11 y D-12 permanecen abiertas para `Task/031` y `Task/032`.

## 3. Dentro del alcance

- [x] Demostrar mediante atestación humana saneada la existencia y acceso a una cuenta AWS
      real; Free Plan/créditos e identidad técnica quedaron verificados sin identificadores.
- [x] Demostrar mediante atestación humana saneada la existencia y acceso a una cuenta
      Cloudflare real en plan Free; el correo verificado sigue sin comprobarse.
- [x] Registrar únicamente evidencia saneada de MFA de AWS root y Cloudflare.
- [x] Establecer una identidad humana administrativa AWS separada de root, con MFA y sin
      claves de acceso permanentes innecesarias.
- [x] Resolver D-13 mediante decisión explícita del usuario, aceptada con la
      aprobación de Task/027.
- [x] Configurar y verificar un presupuesto AWS y notificaciones con monto, moneda,
      período y umbrales explícitos autorizados.
- [x] Documentar el contexto de costo de Cloudflare, VPS y Grafana sin resolver D-19 ni
      anticipar la selección de `Task/029`.
- [x] Dejar evidencia no secreta suficiente para que `Task/028` pueda preparar OIDC.
- [x] Comprobar mediante atestación humana que esta tarea no creó recursos de aplicación;
      no se afirma un inventario exhaustivo de la cuenta.

## 4. Fuera del alcance

- Terraform `apply` contra AWS real o cambios al grafo de aplicación.
- S3, SSM, Lambda, API Gateway o log groups de aplicación.
- Cloudflare Pages, zonas, DNS, WAF, dominios o API tokens.
- VPS, PostgreSQL, PgBouncer, TLS del VPS, backup o Grafana Cloud.
- OIDC de GitHub Actions (`Task/028`) e identidad del VPS hacia AWS (`Task/029`, D-16).
- Claves de acceso para root, GitHub o el operador humano.
- Credenciales reales contra Floci.

## 5. Descubrimiento cloud inicial — solo lectura

### AWS

- AWS CLI: **no instalada o no disponible en `PATH`**.
- Indicadores AWS consultados mediante una lista cerrada: ninguno presente.
- `~/.aws/config` y `~/.aws/credentials`: **no existen**; no se leyó contenido secreto.
- `aws sts get-caller-identity`: **no ejecutable**, porque no existe CLI ni sesión segura.
- Cuenta, plan, identidad actual y MFA: **no verificables desde este entorno**.

### Cloudflare

- `wrangler`, `cloudflared` y CLI `cloudflare`: no disponibles.
- Indicadores cerrados de token/cuenta en el entorno: ninguno presente.
- Superficies de navegador controlables: ninguna disponible durante el descubrimiento.
- Cuenta, plan y MFA: **no verificables desde este entorno**.
- No se creó ni solicitó ningún token.

Ese fue el resultado del discovery inicial. Gates A y B posteriores añadieron evidencia
humana real sin convertirla en evidencia API.

### 5.1 Evidencia humana saneada — Gates A y B

| Proveedor | Cuenta | MFA | Lo que sigue sin comprobarse |
| --- | --- | --- | --- |
| AWS | Creada por el usuario; acceso confirmado; **Free Plan con créditos activos** | Root MFA con aplicación TOTP (Duo Mobile); inicio de sesión con MFA confirmado | Ninguno para Gates A–C; STS operativo ya verificado en C.8 |
| Cloudflare | Creada por el usuario; acceso confirmado; **plan Free** | MFA con aplicación TOTP; inicio de sesión con MFA confirmado | Correo verificado |

No se registraron correos, Account IDs, QR, seeds, TOTP, recovery codes, datos de pago ni
capturas. **Gates A, B, C y D quedan completados; Gate E es el checkpoint actual.**

## 6. Gate C — identidad exacta creada y verificada

El usuario eligió el 2026-09-15 la alternativa compatible con AWS Free standalone y fijó
estas prohibiciones: **sin upgrade a Paid, sin AWS Organizations y sin IAM Identity Center
de organización**. El diseño aprobado conceptualmente es usuario de entrada sin privilegios
directos → rol administrativo temporal con MFA. El usuario autorizó exactamente esta
creación el 2026-09-15, sin Organizations, Identity Center, access keys ni upgrade. El
primer intento de ejecución no pudo abrir una superficie de navegador: Chrome, Edge y el
navegador integrado no estaban disponibles, y el controlador nativo tampoco estaba
conectado. No hubo mutaciones en ese intento. Después, el usuario operó su navegador
privadamente y completó C.1–C.13 sin exponer material de autenticación. El agente no operó
el navegador ni ejecutó mutaciones externas.

### 6.1 Checkpoints de ejecución manual

| Checkpoint | Evidencia saneada | Estado |
| --- | --- | --- |
| C.1 — acceso IAM a Billing | El usuario confirmó que activó `IAM User and Role Access to Billing Information`; no compartió datos privados | **Completado** |
| C.2 — IAM user de entrada | El usuario confirmó `personal-blog-entry-admin`: consola habilitada; cero permisos, grupos y access keys; MFA todavía ausente; no compartió datos privados | **Completado** |
| C.3 — MFA del IAM user | El usuario confirmó una aplicación TOTP activa, distinta del factor root; un dispositivo MFA, cero access keys y ningún dato privado compartido; login todavía no verificado | **Completado** |
| C.4 — rol administrativo | El usuario confirmó `PersonalBlogAdministrator`: trust sólo a `personal-blog-entry-admin`, sin root/wildcards, MFA obligatorio, sólo `AdministratorAccess`, 3600 s, sin boundary ni access keys | **Completado** |
| C.5 — permiso de entrada | El usuario confirmó una única política inline: sólo `sts:AssumeRole` sobre `PersonalBlogAdministrator`, sin wildcard; cero políticas adicionales, grupos, boundary y access keys | **Completado** |
| C.6 — login del IAM user | El usuario confirmó root cerrado; login del IAM user exitoso con MFA; acceso directo a IAM Users denegado; rol aún no asumido; cero access keys | **Completado** |
| C.7 — cambio de rol | El usuario confirmó Switch Role exitoso, `PersonalBlogAdministrator` activo, sin root ni identidad directa del user, contexto MFA aceptado, 3600 s y cero mutaciones de recursos | **Completado** |
| C.8 — identidad STS | El usuario confirmó `expected_role=true`, `root=false`, `direct_user=false`, sin credenciales manuales, Account ID/ARN, access keys ni recursos de aplicación | **Completado** |
| C.9 — auditoría del IAM user | La consulta read-only confirmó 0 keys, 1 MFA, 0 grupos/policies administradas/boundary, única inline esperada y sus tres comprobaciones en `true` | **Completado** |
| C.10 — auditoría del rol | La consulta confirmó 3600 s, una sola AWS managed `AdministratorAccess`, cero inline/boundary y trust exacto en todos sus booleanos | **Completado** |
| C.11 — exclusiones de cuenta | El usuario confirmó `organizations_absent=true`, total/regiones con Identity Center `0/0`, cero fallos regionales y cero IDs/ARN/datos expuestos | **Completado** |
| C.12 — conservación del plan | Billing Home confirmó Free Plan activo, días y créditos restantes positivos y cero upgrade; `Credits` se consultó sólo como evidencia opcional; no se registraron valores ni identificadores | **Completado** |
| C.13 — cierre de sesión | El usuario confirmó CloudShell cerrada y sesión AWS terminada por completo: root, IAM user y rol inactivos; cero access keys, cero recursos de aplicación y ningún dato privado compartido | **Completado** |

| ID | Decisión de Task/027 | Estado |
| --- | --- | --- |
| D-027-A | Conservar AWS Free Plan/créditos; no crear Organization ni Identity Center de organización | **Aceptada y Vigente** |
| D-027-B | El humano entra con un IAM user sin privilegios directos y opera asumiendo un rol temporal | **Aceptada y Vigente** |
| D-027-C | El rol confía sólo en el user exacto, exige MFA y dura como máximo 3600 s | **Aceptada y Vigente** |
| D-027-D | Cero access keys; verificación STS mediante credenciales temporales de la consola/CloudShell | **Aceptada y Vigente** |
| D-027-E | Root hace sólo bootstrap, Billing y recuperación; después queda fuera del flujo normal | **Aceptada y Vigente** |

### 6.2 Recursos IAM exactos

| Recurso / ajuste | Nombre canónico | Configuración |
| --- | --- | --- |
| IAM user de entrada | `personal-blog-entry-admin` | Acceso sólo a consola; contraseña privada elegida por el usuario; sin cambio forzado inicial; sin grupos; sin access keys, SSH keys, certificados ni credenciales de servicio |
| MFA del IAM user | Asociación privada al usuario | Aplicación TOTP; dispositivo distinto del token root; QR, seed y códigos nunca salen del proveedor/dispositivo |
| Política inline del IAM user | `AssumePersonalBlogAdministratorOnly` | Un único `Allow`: `sts:AssumeRole` sobre el ARN exacto del rol administrativo |
| IAM role administrativo | `PersonalBlogAdministrator` | `MaxSessionDuration = 3600` segundos; trust exclusivo al ARN exacto del IAM user y MFA obligatorio |
| Política de permisos del rol | AWS managed `AdministratorAccess` | Privilegios administrativos durante la sesión asumida; no se adjunta al IAM user |
| Billing bootstrap | `Activate IAM Access` | Root lo habilita una vez para la consola Billing/Budgets; no concede permisos por sí solo |

El Account ID se sustituye privadamente al crear los recursos y **no se versiona**. No se
crea group, customer-managed policy, access key, Organization, Identity Center ni recurso
de aplicación.

### 6.3 Política inline exacta del usuario

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AssumePersonalBlogAdministratorRoleOnly",
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::<ACCOUNT_ID>:role/PersonalBlogAdministrator"
    }
  ]
}
```

No se añade un `Deny` redundante: todo lo no permitido queda en *implicit deny*. No se
concede `iam:ChangePassword`, autoservicio MFA, CloudShell ni acceso a servicios al usuario
base. La contraseña final se establece privadamente durante el bootstrap para no requerir
permisos adicionales de cambio.

### 6.4 Trust policy exacta del rol

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TrustEntryUserWithMFAOnly",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<ACCOUNT_ID>:user/personal-blog-entry-admin"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
```

El principal no es el root de la cuenta ni un comodín: es el usuario exacto. Si ese usuario
se elimina y recrea, AWS no restaura silenciosamente la confianza; la trust debe revisarse.
No se usa `ExternalId`, porque impediría el cambio de rol normal desde la consola.

### 6.5 Flujo diario

1. Abrir privadamente la URL de inicio de sesión IAM de la cuenta.
2. Iniciar sesión como `personal-blog-entry-admin` con contraseña y MFA.
3. Elegir **Switch role** hacia `PersonalBlogAdministrator`.
4. Operar sólo mientras la consola muestre el rol asumido.
5. La sesión dura como máximo una hora; al terminar, salir de la cuenta.

El usuario base no puede administrar AWS directamente. Al asumir el rol, sus permisos base
se sustituyen por los del rol; no se acumulan. Root queda reservado para recuperación o
tareas que AWS marque expresamente como root-only.

### 6.6 Verificación ejecutada, sin access keys

Después de asumir el rol se abrió una sesión nueva de AWS CloudShell, que heredó las
credenciales temporales de la consola, y se ejecutó:

```bash
aws sts get-caller-identity
```

La salida se inspeccionó localmente y no se copió al repositorio. Demostró:

- cuenta privada esperada;
- ARN de tipo `assumed-role/PersonalBlogAdministrator/...`;
- identidad distinta de `root`, distinta del IAM user directo y de una cuenta
  ficticia de prueba;
- ningún endpoint local o override.

La evidencia versionada es únicamente booleana/saneada. Además se comprobaron:

- `MaxSessionDuration = 3600`;
- sólo `AdministratorAccess` adjunta al rol;
- política inline única del usuario;
- exactamente un MFA activo para el usuario;
- `list-access-keys` devuelve longitud `0`;
- acciones distintas de `sts:AssumeRole` quedan en *implicit deny* para el usuario base;
- trust policy contiene el principal exacto y `aws:MultiFactorAuthPresent = true`.

### 6.7 Evidencia de que root queda fuera del flujo

- Root ejecuta sólo el bootstrap inicial y `Activate IAM Access` con su MFA.
- Se cierra la sesión root antes de probar la identidad operativa.
- El primer `sts get-caller-identity` operativo debe mostrar el rol asumido.
- Toda operación posterior de Task/027 se realiza como el rol; un evento root posterior
  aborta el cierre salvo que sea una acción root-only documentada.
- Root conserva MFA y **cero access keys**.

### 6.8 Rollback

1. Entrar como root con MFA únicamente para recuperación.
2. Revocar primero todas las sesiones activas de `PersonalBlogAdministrator`.
3. Desadjuntar `AdministratorAccess` y eliminar el rol.
4. Eliminar la política inline del usuario.
5. Desactivar/eliminar su MFA, eliminar el login profile y eliminar el usuario.
6. Restaurar `Activate IAM Access` a su valor previo sólo si Task/027 lo cambió y ninguna
   otra identidad depende de él.
7. Verificar ausencia de rol/usuario, cero access keys, ausencia de Organization/Identity
   Center y plan AWS aún Free.

La revocación añade temporalmente `AWSRevokeOlderSessions` para invalidar las credenciales
emitidas antes del corte; no se confía sólo en esperar la expiración de una hora.

### 6.9 Impacto sobre Free Plan

IAM, roles y STS no tienen cargo adicional. Este diseño no contiene ninguna operación de
upgrade, Organizations o Identity Center; por tanto, no incluye el disparador que AWS
documenta como conversión automática a Paid y caducidad de créditos. El plan Free y los
créditos se comprobaron de nuevo después del bootstrap en C.12 y seguían activos.

## 7. D-13 — decisión autorizada en Gate D

D-13 es el **límite mensual de todo el proyecto**, mientras que AWS Budgets solo observa
cargos AWS. El usuario decidió explícitamente:

1. techo mensual total del proyecto: **USD 20**;
2. sublímite mensual AWS: **USD 5**.

Desglose consultado el 2026-09-15:

| Componente | Estado de costo | Tratamiento en D-13 |
| --- | --- | --- |
| AWS Budgets | Monitoreo y notificaciones sin acciones: sin cargo. Las acciones y reportes tienen tarifación propia | Proponer presupuesto solo de notificación; sin acciones ni reportes |
| S3 | Almacenamiento, solicitudes y salida dependen de región y uso; entrada y ciertos tránsitos son gratuitos | Estimación pendiente de región/uso; no crear bucket aquí |
| SSM Parameter Store | Parámetros Standard sin cargo adicional; Advanced e interacciones avanzadas sí pueden cobrar | El diseño prevé Standard, pero se verificará al desplegar |
| Lambda | Pago por solicitudes y duración; existe oferta gratuita sujeta a condiciones vigentes | No asumir elegibilidad del Free Tier |
| API Gateway HTTP API | Pago por llamadas y transferencia; sin mínimo contractual | Estimación pendiente de tráfico/región |
| CloudWatch | Métricas, logs y alarmas dependen de volumen y región; existen límites gratuitos condicionados | D-11 aún abierta; no fijar retención aquí |
| Cloudflare | La cuenta real está en Free; el plan publicado es 0 USD/mes y Pages estático publica solicitudes de assets gratuitas e ilimitadas | Plan real confirmado; sin Pages, zona, DNS ni contratación adicional |
| VPS/PostgreSQL | Proveedor, región, IPv4, snapshots y tráfico aún no seleccionados | Importe desconocido hasta `Task/029` |
| Grafana Cloud | D-19 abierta; tier y límites deben verificarse al decidir | Reserva pendiente; resolución definitiva en `Task/041` |
| Dominio y otros futuros | No contratados ni cotizados en esta tarea | No ocultarlos: mantener reserva o tratarlos fuera del presupuesto operativo, según decida el usuario |

Fórmula de decisión:

`D-13 total = sublímite AWS + VPS + Cloudflare + Grafana + dominio prorrateado + reserva`

Gate D autorizó el 2026-09-15:

- mensual, USD;
- 50 % de gasto real;
- 80 % de gasto previsto;
- 80 % de gasto real;
- 100 % de gasto real;
- destinatario introducido directamente por el usuario o tratado sin persistirlo;
- sin acciones automáticas, SNS ni reportes pagos.

La resolución de D-13 quedó **Aceptada y Vigente** el 2026-09-17. Los
USD 20 son un techo de voluntad de gasto que incluye AWS, VPS, Cloudflare, Grafana, dominio
prorrateado y reserva; no afirman que esos componentes ya tengan precio seleccionado. El
sublímite AWS de USD 5 es la única parte que observará AWS Budgets.

### 7.1 Gate E — preflight y ejecución verificados

El diseño aprobado consistía en crear exactamente **un** presupuesto de AWS Budgets.

El usuario autorizó este diseño exacto el 2026-09-16, con el correo introducido
privadamente y sin SNS, actions, reports, Organizations, Identity Center, access keys ni
upgrade. La ejecución posterior fue manual, un checkpoint a la vez, sin Computer Use del
agente; el resultado persistido se verificó por API y consola.

| Checkpoint | Evidencia saneada | Estado |
| --- | --- | --- |
| E.1 — login de entrada | El usuario inició sesión como `personal-blog-entry-admin`; MFA solicitado y aceptado; root inactivo, rol todavía no asumido y ningún dato privado compartido | **Completado** |
| E.2 — asumir rol | El usuario confirmó `PersonalBlogAdministrator` activo; root e identidad directa del IAM user inactivos; presupuesto aún inexistente y ningún dato privado compartido | **Completado** |
| E.3 — STS previo a mutación | El usuario confirmó `sts_query_ok/account_match/expected_role/root/direct_user=true/true/true/false/false`; sin credenciales manuales, IDs/ARN mostrados o compartidos, ni presupuesto creado | **Completado** |
| E.4 — Free Plan previo a mutación | Billing Home mostró Free activo, días y créditos restantes positivos, sin upgrade; rol activo y ningún dato privado compartido | **Completado** |
| E.5 — inventario de Budgets | El usuario verificó Primary billing view (o sin selector) y ausencia del nombre exacto `personal-blog-aws-monthly-cost`; no pulsó Create budget, mantuvo el rol activo y no compartió datos privados | **Completado** |
| E.6 — tipo de presupuesto | El usuario seleccionó Customize (advanced) y Cost budget; formulario Details abierto, sin creación ni upgrade. La vista previa devolvió `CostExplorer:GetCostAndUsage AccessDeniedException` (`User not enabled for cost explorer access`); no se habilitó Cost Explorer | **Completado con observación** |
| E.7 — detalles básicos | El usuario confirmó nombre exacto, Monthly, Recurring, Fixed y USD 5; formulario sin enviar, Cost Explorer no habilitado manualmente y edición no bloqueada | **Completado** |
| E.8 — alcance y cálculo | La UI nueva requiere un filtro de exclusión Charge type/Tipo de cargos para Credit/Refund. El usuario observó dimensión y operador `Excludes`, pero al abrir Valores recibió `User not enabled for cost explorer access`: no pudo cargar ni seleccionar Credit/Refund. No aplicó filtro, no pulsó Siguiente/Create y no habilitó Cost Explorer manualmente | **Detenido — sin mutación** |
| E.8a — preflight de ruta alternativa | CloudShell del rol temporal confirmó `sts_query_ok/account_match/expected_role/root/direct_user=true/true/true/false/false` y `budget_absent=true`; ninguna llamada a Cost Explorer ni creación | **Completado** |
| E.8b — validación local de definición | El usuario confirmó `sdk_schema_valid=true`, exclusión Credit/Refund, UnblendedCost/MONTHLY/fijo USD 5, cuatro notificaciones, destinatario ficticio, sin `CreateBudget` ni API de Cost Explorer | **Completado** |
| E.8c — creación única | El usuario confirmó `preflight_ok=true`, `recipient_accepted=true`, `create_budget_call=success`, `verification_pending=true` en ese momento; una sola solicitud `budgets:CreateBudget`, sin exponer el correo. E.8d–E.8f hicieron las verificaciones posteriores. | **Completado** |
| E.8d — lectura del presupuesto | El usuario confirmó `expected_role/describe_budget_ok/name_exact/cost_budget/monthly/fixed_usd5/unblended_only/charge_filter_exact/starts_current_utc_month/recurring_long_term=true`; sin gasto, identificadores ni fechas exactas | **Completado** |
| E.8e — notificaciones y destinatario | El verificador corregido encontró cuatro alertas base exactas, un EMAIL por alerta y cero SNS; AWS omitió `ThresholdType` en las cuatro respuestas. La lectura privada detectó un destinatario distinto del deseado, por lo que el usuario autorizó corregir únicamente los cuatro suscriptores EMAIL. R1–R3 completaron esa corrección y la auditoría final confirmó cuatro destinatarios deseados. El tipo porcentual se comprobó aparte en E.8f. | **Completado** |
| E.8e-R1 — preflight de corrección | El usuario confirmó `expected_role=true`, cuatro alertas base exactas, un EMAIL por alerta, único destinatario actual, dirección nueva confirmada y distinta, cero SNS, `preflight_ok=true`, `update_subscriber_called=false` | **Completado — read-only** |
| E.8e-R2 — actualizar ACTUAL 50 % | El usuario confirmó rol, sintaxis local, preflight y única llamada exitosos; lectura posterior: cuatro alertas base inalteradas, un EMAIL por alerta, ACTUAL 50 % con la dirección nueva, otras tres sin cambios, cero SNS y `verification_ok=true`. No se mostró ni registró ningún correo | **Completado** |
| E.8e-R3 — bloque de tres suscriptores restantes | El usuario confirmó preflight de identidad/estado mixto, doble entrada privada y sintaxis válida; tres llamadas `UpdateSubscriber` intentadas, confirmadas y verificadas inmediatamente, sin fallo ni incertidumbre. La auditoría final read-only confirmó cuatro alertas base intactas, presupuesto y definiciones de notificaciones sin cambios observables, un EMAIL por alerta, cuatro destinatarios deseados, cero antiguos y cero SNS. No se mostró ni registró ninguna dirección ni identificador; `ThresholdType` no se tocó. | **Completado** |
| E.8f — tipo porcentual de las alertas | El usuario confirmó por inspección visual read-only `threshold_type_visible=true` y tipo porcentaje `true` para ACTUAL 50 %, FORECASTED 80 %, ACTUAL 80 % y ACTUAL 100 %; `changes_made=none`. No se registraron capturas ni datos privados. | **Completado** |
| E.9 — inventario Cost Anomaly Detection | El usuario informó `cad_page_accessible=true`, `cost_monitors_count=1`, `alert_subscriptions_count=1` y `changes_made=none` tras revisar ambas pestañas de la consola. El inventario por sí solo no prueba el origen automático de esos recursos. | **Completado — solo lectura** |
| E.9a — caracterización saneada | El usuario confirmó `aws_managed_monitor/aws_services_dimension/subscription_linked_to_monitor/daily_summary/email_only=true`, `sns_present=false` y `changes_made=none`. El par 1/1 coincide con la configuración automática que AWS documenta al habilitar Cost Explorer; sin baseline previo ni evento de creación correlacionado, la atribución causal es inferida, no demostrada. No se registraron nombres, destinatarios, ARN, umbrales ni fechas. | **Completado — read-only** |
| E.9b — decisión sobre CAD | El usuario decidió conservar el monitor administrado por AWS y la suscripción diaria EMAIL tal como están, como protección secundaria consciente y sin coste adicional según la documentación oficial. No autorizó cambios, personalizaciones ni recursos CAD adicionales. No sustituye las cuatro alertas de Budgets. | **Completado — conservar sin mutación** |
| E.10 — ausencia de Budget Actions | El usuario confirmó `expected_role=true`, `actions_query_ok=true`, `budget_actions_count=0`, `budget_actions_absent=true` y `changes_made=none` mediante `DescribeBudgetActionsForBudget` paginado; ningún Account ID/ARN mostrado ni API de Cost Explorer llamada. | **Completado — read-only** |
| E.11 — Free Plan y créditos posteriores | El usuario confirmó en Billing Home `billing_home_plan_free/plan_active/days_remaining_positive/credits_remaining_positive=true`, `upgrade_executed=false` y `changes_made=none`. No se compartieron importes, fechas exactas, identificadores, pago ni capturas. | **Completado — visual/read-only** |
| E.12 — access keys posteriores | El usuario confirmó `expected_user=true`, `access_keys_count=0` y `changes_made=none` en IAM → Users → Security credentials. No se compartieron IDs, credenciales ni capturas. | **Completado — visual/read-only** |
| E.13 — cierre de sesión AWS | El usuario confirmó `cloudshell_closed/aws_console_signed_out=true`, `root_session_active/iam_user_session_active/role_session_active=false`, `application_resources_created_by_task=0` y `cloud_resources_changed_during_close=none`. Es una atestación acotada a Task/027, no un inventario exhaustivo. | **Completado — sesión cerrada** |

| Campo | Valor exacto |
| --- | --- |
| Nombre | `personal-blog-aws-monthly-cost` |
| Tipo | Cost budget |
| Configuración | Customize (advanced) |
| Período | Monthly |
| Renovación | Recurring budget; sin fecha de fin |
| Inicio | Período mensual UTC vigente al crearlo |
| Método | Fixed |
| Importe | USD 5 por mes |
| Alcance | Todos los servicios de la cuenta standalone en Primary; sin filtro de servicio, cuenta o etiqueta. **Un solo filtro por tipo de cargo: excluir Credit y Refund**; sin billing view personalizada |
| Agregación | Unblended costs, apropiado para una cuenta individual |
| Créditos | Excluidos mediante el filtro de tipo de cargo para que los créditos Free Tier no oculten consumo bruto |
| Reembolsos | Excluidos mediante el mismo filtro para que no reduzcan artificialmente el consumo observado |
| Resto de tipos de cargo | No excluidos: descuentos, impuestos, soporte, suscripciones y cargos upfront/recurrentes, incluidos los tipos futuros distintos de Credit/Refund |
| Tags | Ninguno |

Notificaciones exactas, todas con comparación `GREATER_THAN` y umbral porcentual:

| # | Tipo | Umbral | Equivalencia sobre USD 5 | Destino |
| --- | --- | --- | --- | --- |
| 1 | Actual | 50 % | USD 2.50 | Un correo introducido privadamente por el usuario |
| 2 | Forecasted | 80 % | USD 4.00 | El mismo correo privado |
| 3 | Actual | 80 % | USD 4.00 | El mismo correo privado |
| 4 | Actual | 100 % | USD 5.00 | El mismo correo privado |

Quedan deshabilitados o vacíos: Amazon SNS, AWS Chatbot, budget actions, aprobación manual
de acciones, IAM/SCP actions, acciones sobre EC2/RDS y AWS Budgets Reports. No se crea
Organization, Identity Center, access key, recurso de aplicación ni upgrade de plan.

AWS documenta que monitorear y recibir notificaciones de Budgets no tiene cargo; los
reportes entregados sí se cobran y por eso quedan excluidos. El presupuesto **no es un
límite duro**: sin actions no detiene recursos ni gasto, y los datos se actualizan al menos
una vez al día. La alerta forecasted puede configurarse desde el inicio, pero AWS necesita
aproximadamente cinco semanas de historial para generarla.

El siguiente bloque conserva la justificación histórica del preflight previo a E.8c; la
tabla anterior contiene el resultado final de cada checkpoint.

La vista previa de E.6 devolvió un error de acceso a Cost Explorer. En E.8, el mismo
estado impidió cargar los valores de Tipo de cargos; por tanto, **esta ruta de consola no
permite preparar la exclusión exacta ahora**. AWS documenta que el gráfico puede estar
vacío y que se puede crear un presupuesto sin habilitar Cost Explorer manualmente, pero
también indica que Budgets puede habilitarlo al crear el primer presupuesto. La guía de
habilitación de Cost Explorer dice que ese proceso configura automáticamente un monitor y
una suscripción de alertas de Cost Anomaly Detection. No está demostrado si esa
automatización ocurrirá en esta cuenta al crear el presupuesto. No se pulsará ninguna
opción de habilitación manual, no se habilitará granularidad horaria ni se consultará la API
de Cost Explorer. La API de Budgets ofrece campos `CostTypes.IncludeCredit=false` y
`IncludeRefund=false` sin selector UI, pero ese método alternativo tampoco demostraría que
crear el primer presupuesto no habilite Cost Explorer. **Gate E se pausó antes de
crear** para confirmar el alcance de estos efectos automáticos. Según AWS, Cost
Explorer no se puede deshabilitar después y su interfaz es gratuita, pero sus llamadas
API tienen precio por solicitud. La documentación de Free Plan no enumera Cost Explorer/Budgets
entre sus disparadores automáticos de upgrade; esto es una inferencia sobre esa lista,
no una garantía de estado futuro. No se cambiará la definición a un presupuesto que incluya créditos/reembolsos
sin autorización. La conservación del Free Plan se reconfirmará después de cualquier creación
autorizada; no se promete por inferencia que un servicio mantenga condiciones comerciales.

El usuario **amplió expresamente Gate E** para aceptar que crear el primer AWS Budget
habilite Cost Explorer como efecto necesario y la posible creación automática por AWS de
Cost Anomaly Detection (monitor y suscripción inicial). **No autorizó habilitar Cost
Explorer manualmente**, granularidad horaria ni consultas pagas a su API. Tampoco amplió
la autorización a upgrade, Organizations, Identity Center, access keys, SNS, Budget
Actions/Reports u otros recursos de aplicación. Como el selector UI sigue bloqueado, se
preparará una ruta manual desde CloudShell con la API de **AWS Budgets**, usando las
credenciales temporales del rol. La ruta elegida usa los campos actuales
`FilterExpression.Not.Dimensions` con clave `RECORD_TYPE`, valores `Credit` y `Refund`,
y `Metrics=UnblendedCost`, sin invocar Cost Explorer ni usar los campos heredados
`CostFilters`/`CostTypes`. E.8a ya reconfirmó el rol y que el nombre exacto no existe;
E.8b validó localmente el esquema con destinatario ficticio y sin llamadas de creación.
El usuario seguirá ejecutando cada paso en
su navegador, uno por uno. Después de crear y verificar el presupuesto, se auditará
read-only qué recursos de Cost Anomaly Detection aparecieron, usando la consola y/o el
historial gratuito de eventos de administración de CloudTrail, sin consultar la API de
Cost Explorer; **antes de conservar o
eliminar cualquiera de ellos se presentará evidencia saneada y se pedirá decisión
explícita**. La presencia de recursos posteriores no se atribuirá automáticamente a esta
operación sin una línea base verificable.

Tras la creación se verificará de forma read-only y saneada únicamente: existencia/nombre,
tipo COST, USD 5, período MONTHLY, método fijo, exclusión `RECORD_TYPE` de Credit/Refund
en `FilterExpression.Not` (o su representación equivalente), ningún filtro de
servicio/cuenta/tag, créditos/reembolsos excluidos,
cuatro notificaciones exactas, destinatario email presente sin mostrarlo, cero SNS y cero
actions. Después se reconfirmarán Billing Home (Free activo, días/créditos positivos, sin
upgrade), cero access keys, cero recursos de aplicación y cierre total de sesión.

## 8. Gates humanos obligatorios

| Gate | Acción humana | Motivo | Estado |
| --- | --- | --- | --- |
| A | Acceder o crear AWS y Cloudflare; introducir privadamente identidad, pago, verificación y términos | El entorno no puede demostrar si existen | **Completado — atestación humana saneada** |
| B | Configurar personalmente MFA en AWS root y Cloudflare; custodiar factores y recuperación | El agente no debe ver QR, seed, TOTP ni códigos | **Completado — ambos inicios de sesión verificados por el usuario** |
| C | Diseñar, autorizar, crear y verificar la identidad administrativa AWS | Separar root y obtener sesión administrativa temporal sin perder Free Plan | **Completado — C.1–C.13 ejecutados manualmente; el agente no operó el navegador** |
| D | Decidir techo total D-13, sublímite AWS y umbrales | Decisión financiera del usuario | **Completado — USD 20 total, USD 5 AWS y cuatro alertas autorizadas** |
| E | Autorizar el preflight exacto y la creación del presupuesto/notificaciones | Mutación real de billing | **Completado por el usuario:** presupuesto y cuatro alertas verificados; CAD 1/1 conservado por decisión humana; cero Budget Actions y access keys; Free Plan/créditos posteriores positivos; CloudShell/consola cerradas y cero recursos de aplicación atribuibles atestados. |

## 9. Operaciones automatizables de forma segura

Después de los gates y solo con sesión temporal/autorizada:

- comprobar CLI y perfil sin volcar secretos;
- ejecutar `aws sts get-caller-identity` antes de cada mutación;
- abortar si la identidad es root, la cuenta es ficticia/de prueba, hay endpoint local,
  credenciales `test/test`, un override o una cuenta distinta de la aprobada;
- consultar por API/CLI MFA administrativo, identidad y presupuesto cuando la API lo
  permita, enmascarando identificadores;
- crear exclusivamente el presupuesto/notificaciones autorizados;
- leer de nuevo la configuración para verificar monto, período, moneda y umbrales;
- auditar Git, secretos y ausencia de recursos atribuibles a esta tarea.

El MFA de root y Cloudflare requiere comprobación humana saneada; no se intentará extraer
el material secreto ni generar tokens solo para automatizar la evidencia.

## 10. Criterios de aceptación

- [x] AWS real correctamente identificada, con evidencia saneada y STS agregado.
- [x] Cloudflare real correctamente identificada por atestación humana saneada; el correo
      sigue sin comprobarse y no se registra.
- [x] MFA root AWS habilitado — evidencia humana saneada; TOTP y login verificado.
- [x] MFA Cloudflare habilitado — evidencia humana saneada; TOTP y login verificado.
- [x] Root AWS fuera del flujo operativo normal.
- [x] Identidad administrativa separada establecida y verificada.
- [x] D-13 decidida explícitamente por el usuario — USD 20 total y USD 5 AWS.
- [x] Presupuesto mensual AWS configurado de acuerdo con D-13.
- [x] Alertas de costo configuradas y verificadas.
- [x] Ningún secreto mostrado o versionado en el checkpoint inicial.
- [x] Ningún recurso de aplicación desplegado en el checkpoint inicial.
- [x] Backend y frontend intactos y sin rama Task.
- [x] `Task/028` no iniciada.
- [x] `Task/029` no iniciada.
- [x] Documentación final coherente: ficha, reporte, STATUS, ROADMAP, Stage 09 y D-13.
- [x] Definition of Done completa sin FAIL; N/A justificados en el reporte §R.

## 11. TDD / plan test-first

No aplica: no hay comportamiento funcional de backend. La validación es de identidad,
configuración cloud, costo, seguridad, ausencia de secretos y gobierno documental.

## 12. Plan de validación

1. Evidencia humana saneada de existencia/acceso a cuentas y plan aplicable.
2. Evidencia humana saneada de MFA, sin capturas que expongan secretos.
3. Identidad administrativa: login operativo y `sts get-caller-identity` sin root.
4. Presupuesto: lectura posterior por API/CLI de límite, unidad, período y notificaciones.
5. Costos: contrastar precios oficiales vigentes y separar hechos, estimaciones, tiers y
   desconocidos.
6. Ausencia: inventario de recursos limitado y no destructivo; preexistencias se registran,
   nunca se borran para fabricar un cero.
7. Git: cambios solo en infra; backend/frontend limpios; ningún secreto.
8. DoD: cada criterio se marcará PASS, N/A justificado o FAIL.

## 13. Riesgos

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Actuar en cuenta/identidad equivocada o contra Floci | Crítico | STS, cuenta enmascarada aprobada, no-root, lista cerrada de variables y sin endpoint override antes de mutar |
| Exposición de credenciales, MFA, pago o recuperación | Crítico | El usuario introduce/custodia; jamás copiar, capturar ni versionar |
| Perder créditos al habilitar AWS Organizations | Alto | Conocer primero el plan; elección explícita en Gate C |
| Factura inesperada | Alto | D-13 antes del primer recurso; alertas reales; sin acciones de pago |
| Presupuesto AWS confundido con costo total | Alto | D-13 total y sublímite AWS separados |
| Tiers/precios caducan | Medio | Fuente oficial fechada y revalidación en `Task/029`/`Task/041` |
| Crear infraestructura “para probar” | Alto | Prohibición y comprobación de ausencia; cero Terraform apply |
| Evidencia manual exagerada | Alto | Declarar qué es atestación humana y qué se verificó por API |

## 14. Plan de ejecución ordenado

1. ✔ Leer fuentes canónicas y oficiales aplicables.
2. ✔ Revalidar Git y crear la rama únicamente en infra desde `main`.
3. ✔ Ejecutar discovery cloud read-only sin secretos.
4. ✔ Crear ficha/reporte y actualizar documentos vivos a `En progreso` sin contadores.
5. ✔ Gate A: usuario creó/accedió a ambas cuentas y devolvió sólo estado saneado.
6. ✔ Gate B: usuario configuró y verificó ambos MFA sin compartir material secreto.
7. ✔ Gate C: estrategia B creada y verificada manualmente mediante C.1–C.13; sesión
   privilegiada cerrada. El agente no vuelve a intentar Computer Use.
8. ✔ Demostrar la sesión temporal con STS sin registrar Account ID ni ARN completo.
9. ✔ Gate D: D-13 = USD 20 total; sublímite AWS = USD 5; cuatro alertas, sin actions/SNS/reportes.
10. ✔ Gate E: presupuesto y cuatro alertas verificados; CAD 1/1 auditado y conservado
    por decisión humana; cero Budget Actions/access keys, Free Plan/créditos posteriores
    y cierre de sesión verificados.
11. ✔ Verificar presupuesto/alertas, auditar CAD y decidir expresamente conservarlo.
12. ✔ Verificar localmente secretos y cambios externos de repositorio; ausencia de recursos
    de aplicación atribuibles atestada por el usuario.
13. ✔ Completar DoD, ficha, reporte y documentos vivos; aprobación recibida el 2026-09-17.

## 15. Resultado del checkpoint actual

| Comprobación | Resultado |
| --- | --- |
| Git/branch | PASS — rama creada desde `main` limpio el 2026-09-15; la publicación pertenece al cierre posterior a la aprobación |
| Cuenta AWS | PASS — creada/accesible; Free Plan y créditos activos; rol temporal verificado por STS saneado |
| Cuenta Cloudflare | PASS humano saneado — creada/accesible, plan Free y MFA verificado; correo no comprobado |
| MFA | PASS humano saneado — AWS root, IAM user y Cloudflare con TOTP; inicios de sesión verificados |
| Secretos | PASS — no volcados ni persistidos |
| Mutaciones ejecutadas por el agente | PASS — cero; cuentas, MFA, IAM, la llamada `CreateBudget` y las cuatro sustituciones EMAIL fueron acciones privadas del usuario |
| Recursos de aplicación creados | PASS — cero atribuibles a Task/027 |
| Gate actual | E completado por el usuario; cero access keys y recursos de aplicación atribuibles, sesiones cerradas; validación local final superada |

## 16. Documentación creada o actualizada

- `docs/tasks/TASK-027-cloud-accounts-and-budgets.md` — ficha de la tarea.
- `docs/task-reports/TASK-027-report.md` — análisis A–N y evidencia incremental.
- `docs/project-management/STATUS.md` — Task/027 aprobada; Stage 09 en progreso, 1/3.
- `docs/project-management/ROADMAP.md` — fila y actualización viva de Task/027.
- `docs/stages/STAGE-09-cloud-accounts.md` — Stage 09 en progreso, 1/3 aprobadas.
- `docs/architecture/open-decisions.md` — resolución D-13 aceptada.

## 17. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | 2026-09-17 |
| **Aprobado por** | Usuario |
| **Expresión de aprobación** | `approved: Task/027-Configurar-Cuentas-y-Presupuestos` |

La expresión exacta fue recibida el 2026-09-17 y autorizó el cierre Git descrito en
[WORKFLOW.md](../project-management/WORKFLOW.md). El PR `Task → main` queda para revisión
y fusión manual del usuario.
