# Reporte — TASK-027 · Configurar cuentas y presupuestos

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/027-Configurar-Cuentas-y-Presupuestos` |
| **Estado** | **Aprobada** el 2026-09-17 mediante la expresión exacta del flujo |
| **Fase** | D-13 resuelta; presupuesto y cuatro alertas verificados; CAD conservado; cero Budget Actions/access keys; Free Plan activo; sesiones AWS cerradas; validación local superada |
| **Fecha de consulta** | 2026-09-17 (Guatemala) |
| **Repositorio modificado** | `personal-blog-infra` |
| **Repositorios intactos** | `personal-blog-backend`, `personal-blog-frontend` |
| **Ficha** | [TASK-027-cloud-accounts-and-budgets.md](../tasks/TASK-027-cloud-accounts-and-budgets.md) |

> **Reporte aprobado el 2026-09-17.** Cuentas, MFA y cierre de sesión tienen
> evidencia humana saneada; identidad, presupuesto y alertas cuentan además con lecturas
> API/STS agregadas. D-13 quedó resuelta con la aprobación de Task/027.

---

# TASK027 — ANÁLISIS Y PLAN DE IMPLEMENTACIÓN

## A. Alcance canónico

Verificar cuentas AWS y Cloudflare reales; habilitar MFA mediante acción privada del
usuario; sacar a AWS root del flujo operativo; establecer una identidad humana
administrativa separada; resolver D-13; crear y verificar un presupuesto AWS con alertas;
y preparar evidencia para `Task/028`, sin implementar OIDC ni desplegar la aplicación.

## B. Fuentes consultadas

### Proyecto — completas en lo aplicable

- `AGENTS.md` y `docs/claude/PROJECT_INSTRUCTIONS.md` — la ruta solicitada
  `docs/project-management/PROJECT_INSTRUCTIONS.md` no existe; se usó la fuente canónica
  referenciada por `AGENTS.md`.
- `ROADMAP.md`, `STATUS.md`, `WORKFLOW.md`, `DEFINITION_OF_DONE.md`.
- Stages 08, 09 y 10.
- Arquitectura: overview, arquitectura objetivo, límites de seguridad, decisiones abiertas,
  PostgreSQL/VPS y paridad AWS local.
- ADR-001, ADR-003, ADR-006, ADR-007 y ADR-008.
- Fichas y reportes de Task/025, Task/026 y Task/026.1.

### Proveedores — fuentes oficiales consultadas del 2026-09-15 al 2026-09-17

- AWS: [mejores prácticas de IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html),
  [root](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html),
  [MFA de root](https://docs.aws.amazon.com/IAM/latest/UserGuide/enable-mfa-for-root.html),
  [instancias de IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/identity-center-instances.html),
  [límites de una instancia de cuenta](https://docs.aws.amazon.com/singlesignon/latest/userguide/account-instances-identity-center.html),
  [habilitación e impacto de IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/enable-identity-center.html),
  [alta del usuario/grupo/permission set administrativo](https://docs.aws.amazon.com/singlesignon/latest/userguide/quick-start-default-idc.html),
  [MFA de Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/how-to-configure-mfa-device-enforcement.html),
  [credenciales temporales para CLI](https://docs.aws.amazon.com/singlesignon/latest/userguide/howtogetcredentials.html),
  [precio de Identity Center](https://aws.amazon.com/iam/identity-center/faqs/),
  [precio de AWS Organizations](https://docs.aws.amazon.com/organizations/latest/userguide/pricing.html),
  [acceso IAM a Billing](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/control-access-billing.html),
  [permiso para cambiar de rol](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_permissions-to-switch.html),
  [rol para un IAM user con MFA](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user.html),
  [cambio de rol en consola y duración](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-console.html),
  [CloudShell preautenticado](https://docs.aws.amazon.com/IAM/latest/UserGuide/using-aws-with-cloudshell.html),
  [revocación de sesiones del rol](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_revoke-sessions.html),
  [creación de un cost budget](https://docs.aws.amazon.com/cost-management/latest/userguide/create-cost-budget.html),
  [mejores prácticas de Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-best-practices.html),
  [tipos de costo de Budgets](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_budgets_CostTypes.html),
  [Free Tier](https://aws.amazon.com/free/free-tier-faqs/) y
  [precios de AWS Budgets](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/),
  [Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-enable.html) y
  [sus precios](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/pricing/).
- Precios AWS: [S3](https://aws.amazon.com/s3/pricing/),
  [Lambda](https://aws.amazon.com/lambda/pricing/),
  [API Gateway](https://aws.amazon.com/api-gateway/pricing/),
  [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/) y
  [Systems Manager](https://aws.amazon.com/systems-manager/pricing/).
- Cloudflare: [planes](https://www.cloudflare.com/plans/),
  [2FA](https://developers.cloudflare.com/fundamentals/user-profiles/2fa/) y
  [pricing de Pages](https://developers.cloudflare.com/pages/functions/pricing/).
- Verificaciones posteriores de AWS: [ver presupuestos y alertas](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-view.html),
  [describir Budget Actions](https://docs.aws.amazon.com/boto3/latest/reference/services/budgets/client/describe_budget_actions_for_budget.html),
  [configuración automática de CAD](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-enable.html),
  [CAD sin coste y opciones de conservación](https://aws.amazon.com/aws-cost-management/aws-cost-anomaly-detection/faqs/),
  [Free Plan y créditos en Billing Home](https://docs.aws.amazon.com/en_en/awsaccountbilling/latest/aboutv2/free-tier-plans.html),
  [lista de access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-keys-admin-managed.html) y
  [cierre de sesión](https://docs.aws.amazon.com/signin/latest/userguide/how-to-sign-out-in.html).

## C. Preparación Git — evidencia histórica del 2026-09-15

| Repositorio | Resultado |
| --- | --- |
| infra | `main == origin/main == 67c1904944fc624b15c15e466f575f055c5c312d`; `dev == origin/dev == e2d77ee2…`; ancestro/diff correctos; limpio; 0 Task antes del alta |
| backend | `main == origin/main == 4a40364bbd6a444f9469b815d17d2d77a37949ce`; limpio; sin Task |
| frontend | `main == origin/main == 7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce`; limpio; sin Task |

Rama creada solo en infra: `Task/027-Configurar-Cuentas-y-Presupuestos`, con
`HEAD == main` al crearla. En esta preparación no hubo commit, push, merge ni PR.

## D. Estado real descubierto de AWS

| Pregunta | Evidencia | Estado |
| --- | --- | --- |
| ¿Existe cuenta? | Atestación humana saneada posterior al discovery | **Sí; creada por el usuario y acceso confirmado** |
| ¿Qué plan/créditos? | Atestación humana saneada de Billing | **Free Plan; créditos activos** |
| ¿Identidad actual? | STS saneado desde CloudShell devolvió `expected_role=true`, `root=false`, `direct_user=false` | **Rol administrativo temporal verificado** |
| ¿Root vs admin? | Root quedó fuera del flujo; el IAM user inició con MFA, no tiene acceso directo, asumió el rol y al final se cerraron todas las sesiones | **Gate C completado; C.1–C.13 conformes** |
| ¿MFA root? | Atestación humana: TOTP en Duo Mobile y login con MFA | **Sí — evidencia humana saneada** |

No se registró Account ID, correo, QR, seed, TOTP, recovery code ni pago. El agente no creó
la cuenta, claves, perfiles, identidades o recursos; la configuración IAM autorizada la
ejecutó el usuario en su navegador.

## E. Estado real descubierto de Cloudflare

| Pregunta | Evidencia | Estado |
| --- | --- | --- |
| ¿Existe cuenta? | Atestación humana saneada posterior al discovery | **Sí; creada por el usuario y acceso confirmado** |
| ¿Correo verificado? | No comprobado | **Pendiente** |
| ¿Plan aplicable? | Atestación humana saneada | **Free** |
| ¿MFA? | Atestación humana: aplicación TOTP y login con MFA | **Sí — evidencia humana saneada** |

No se registró correo, QR, seed, TOTP ni recovery code. No se generó token ni se creó zona,
Pages, DNS o suscripción.

## F. Dependencias heredadas de Task/026

- Los runbooks y las guardas son vigentes, pero su ejecución real AWS pertenece a Stage 10.
- El modo `production` continúa bloqueado.
- El bucket del backend Terraform no existe.
- Los 21 recursos vistos en Floci no son evidencia AWS real.
- La regla de destino explícito se reutiliza: identidad, cuenta y endpoint se verifican antes
  de cualquier mutación de billing.
- DT-026-1 (rollback cloud no demostrado) no se intenta resolver aquí.

## G. D-13 y datos necesarios

D-13 recibió una propuesta de resolución autorizada por el usuario durante Gate D,
**aceptada con la aprobación final de Task/027**:

1. máximo mensual de todo el proyecto: **USD 20**;
2. sublímite mensual AWS: **USD 5**;
3. alertas: 50 % actual, 80 % forecasted, 80 % actual y 100 % actual;
4. sin budget actions, SNS ni reportes pagos.

### Matriz de costo actual

| Clase | Componentes | Conclusión válida ahora |
| --- | --- | --- |
| Conocido | AWS Budgets de solo monitoreo/notificación | 0 USD por el mecanismo; no se proponen acciones ni reportes |
| Conocido y comprobado humanamente | Cloudflare Free | Cuenta real en Free; 0 USD/mes según plan publicado; sin recursos desplegados |
| Dependiente de uso/región | S3, Lambda, API Gateway, CloudWatch | No hay una cifra mensual honesta sin región, tráfico y retención |
| Potencialmente sin cargo | SSM Standard y ofertas gratuitas AWS | Solo si la configuración/elegibilidad real cumple; no se asume |
| Desconocido hasta otra tarea | VPS | `Task/029` selecciona con precio y RTT vigentes |
| Abierto | Grafana Cloud | D-19 se resuelve en `Task/041`; Task/027 solo reserva contexto |
| Futuro | dominio, snapshots, IPv4, backup/egress | No ocultarlos del techo global |

Gate D quedó completado con esos importes y umbrales. Los USD 20 son el techo global de
voluntad de gasto —AWS, VPS, Cloudflare, Grafana, dominio prorrateado y reserva—, no una
estimación de componentes todavía no seleccionados. AWS Budgets sólo observará USD 5.

## G.1 Gate E — preflight de presupuesto

Esta sección conserva la secuencia histórica de los checkpoints de Gate E, incluida
su redacción previa a la creación. El resultado final verificado consta en los
checkpoints E.8d–E.13 y en §R.

El preflight propone un único cost budget `personal-blog-aws-monthly-cost`, personalizado,
fijo, mensual, recurrente y por USD 5, sobre todos los servicios de la cuenta standalone,
sin filtros de servicio/cuenta/tag. La UI nueva requiere **un filtro de exclusión por tipo
de cargo** con Credit y Refund. Usará unblended costs; excluirá créditos y reembolsos para que no oculten el
consumo, e incluirá los demás tipos de cargo. Tendrá exactamente las cuatro alertas de Gate
D al mismo correo privado, sin registrar la dirección, y cero SNS, Chatbot, actions,
reportes o tags.

AWS documenta que el monitoreo y las notificaciones de Budgets no tienen cargo; los Budget
Reports sí cobran por entrega y quedan excluidos. También documenta una actualización de
datos al menos diaria y unas cinco semanas de historial antes de generar forecasts: el
presupuesto no es un límite duro y la alerta forecasted puede tardar en quedar operativa.

Billing Home, ya visitado en C.12, puede habilitar Cost Explorer automáticamente, pero la
vista previa de E.6 muestra que el acceso no está habilitado actualmente. No se
habilitará Cost Explorer manualmente, ni granularidad horaria, ni se llamará su API de pago.
AWS documenta que el primer presupuesto puede habilitar Cost Explorer y que su proceso de
habilitación configura un monitor y una suscripción de Cost Anomaly Detection. No está
verificado si eso ocurrirá aquí: antes de enviar la creación se resolverá ese efecto
potencial fuera del alcance exacto de las cuatro alertas autorizadas. AWS Budgets no figura entre
los disparadores oficiales de upgrade de Free a Paid; por tanto, que este preflight preserve
Free Plan es una inferencia acotada basada en la lista oficial, no una promesa comercial.
El usuario autorizó explícitamente Gate E el 2026-09-16 para crear exactamente este
presupuesto y las cuatro alertas, con correo privado y sin SNS, actions, reports,
Organizations, Identity Center, access keys ni upgrade. La creación aún no se ha ejecutado;
el agente no operará el navegador. La ejecución manual empieza en E.1 (login IAM con MFA)
y no avanza hasta recibir cada confirmación saneada.

Checkpoint **E.1 completado**: el usuario confirmó login como IAM user de entrada con MFA
solicitado y aceptado; root inactivo, rol todavía no asumido y ningún dato privado
compartido. Presupuesto y alertas siguen inexistentes. E.2 será exclusivamente Switch Role.

Checkpoint **E.2 completado**: el usuario confirmó `PersonalBlogAdministrator` activo,
root e identidad directa del IAM user inactivos, presupuesto todavía inexistente y ningún
dato privado compartido. E.3 verificará STS de forma read-only y saneada antes de cualquier
mutación de Budgets.

Checkpoint **E.3 completado**: STS read-only devolvió
`sts_query_ok/account_match/expected_role/root/direct_user=true/true/true/false/false`.
No se configuraron credenciales manuales ni se mostraron o compartieron IDs/ARN. El
presupuesto sigue sin crearse. E.4 reconfirmará Free Plan/créditos en Billing Home antes de
cualquier mutación.

Checkpoint **E.4 completado**: Billing Home mostró Free Plan activo, días y créditos
restantes positivos y ningún upgrade; el rol seguía activo y no se compartieron datos
privados. E.5 será inventario read-only de Budgets en la Primary billing view para evitar
un duplicado antes de crear.

Checkpoint **E.5 completado**: el usuario verificó la Primary billing view (o ausencia de
selector) y que `personal-blog-aws-monthly-cost` no existe. No pulsó Create budget, el rol
seguía activo y no compartió datos privados. E.6 abrirá el asistente avanzado y elegirá
Cost budget, sin enviar creación.

Checkpoint **E.6 completado con observación**: el usuario seleccionó Customize (advanced)
y Cost budget; Details está abierto y no se creó presupuesto ni se hizo upgrade. La vista
previa mostró `CostExplorer:GetCostAndUsage AccessDeniedException` con el tipo
`User not enabled for cost explorer access`. No se habilitó Cost Explorer. Según la
documentación oficial, la ausencia del gráfico no impide por sí sola configurar Budgets;
esa conclusión sobre el error concreto es una inferencia, no un resultado de creación.
E.7 preparará únicamente los detalles básicos sin avanzar ni enviar el formulario.

Checkpoint **E.7 completado**: el usuario confirmó nombre exacto, período Monthly,
renovación Recurring, método Fixed e importe USD 5. El formulario no se envió, Cost
Explorer no se habilitó manualmente y la edición no está bloqueada. E.8 configurará
únicamente alcance y cálculo, sin avanzar ni enviar.

Checkpoint **E.8 detenido antes de modificar**: el usuario observó que la UI muestra
«Todos los servicios de AWS» y «costes sin combinar», pero indica que Credit/Refund se
configuran mediante «Filtrar dimensiones de costes de AWS específicas» → «tipo de cargo»,
no en Advanced options. No modificó el alcance ni pulsó Siguiente. Se corrige E.8 a
**un único filtro de exclusión Charge type = Credit, Refund**, conservando todos los
servicios y sin filtros de servicio/cuenta/tag. La exclusión debe ser explícita; si la UI
solo permite «Incluir solo» o no admite ambos valores, el usuario se detendrá. Es una
corrección del mecanismo de UI para lograr el criterio de coste ya autorizado, no una
creación ni un cambio de umbral.

Segundo intento **E.8 detenido sin aplicar**: «Tipo de cargos» y operador `Excludes`
están disponibles, pero el selector Valores devuelve `User not enabled for cost explorer
access`; no cargó Credit/Refund. Cero filtros aplicados, cero Siguiente/Create, cero
habilitación manual de Cost Explorer. La ruta de consola queda bloqueada para la
configuración exacta. La API de Budgets conserva `CostTypes` para excluir créditos y
reembolsos sin cargar valores en la UI, pero AWS documenta que crear el primer budget puede
habilitar Cost Explorer, y su habilitación puede configurar Cost Anomaly Detection con
monitor/suscripción. No se ha demostrado una ruta que garantice evitar ese efecto. Gate E
se pausó hasta decisión explícita del usuario; no se crea un presupuesto que incluya
créditos/reembolsos como sustitución silenciosa.
AWS indica además que Cost Explorer no puede deshabilitarse tras su activación: la UI de
consulta es gratuita, mientras sus llamadas API tienen precio por solicitud. Budgets/Cost
Explorer no aparecen entre los disparadores automáticos de upgrade del Free Plan listados
por AWS; esa lectura no reemplaza una reconfirmación posterior del plan y créditos.

**Ampliación explícita de Gate E**: el usuario acepta que la creación del primer Budget
habilite Cost Explorer como efecto necesario y la posible configuración automática de Cost
Anomaly Detection, monitor y suscripción inicial. No autorizó activación manual de Cost
Explorer, granularidad horaria, consultas pagas a su API, upgrade, Organizations, Identity
Center, access keys, SNS, Budget Actions/Reports ni recursos de aplicación adicionales.
Después de crear y verificar el presupuesto se auditarán read-only los recursos de
anomalías (consola y/o historial gratuito de CloudTrail, sin API de Cost Explorer) y se
presentará solo un agregado saneado para decidir expresamente si se
conservan o eliminan; ninguna eliminación anticipada. La ruta UI permanece bloqueada,
por lo que se planificó E.8a como preflight read-only desde CloudShell del rol temporal
para usar la API de AWS Budgets sin invocar Cost Explorer ni crear credenciales.

Checkpoint **E.8a completado**: CloudShell informó solo booleanos saneados
`sts_query_ok/account_match/expected_role/root/direct_user=true/true/true/false/false`
y `budget_absent=true`. La ruta elegida se ajustó a los campos actuales de Budgets:
`FilterExpression.Not` con dimensión `RECORD_TYPE` y valores Credit/Refund, junto con
`Metrics=UnblendedCost`; no se usarán los campos heredados `CostFilters`/`CostTypes`.
E.8b validará localmente la forma de solicitud con un destinatario ficticio, sin correo
real, sin creación y sin API de Cost Explorer.

Checkpoint **E.8b completado**: la salida saneada confirmó `sdk_schema_valid=true`,
`charge_type_excludes_credit_refund=true`, `unblended_monthly_fixed_usd5=true`,
`notifications_count=4`, `real_email_used=false`, `create_budget_called=false` y
`cost_explorer_api_called=false`. E.8c será una única llamada de creación autorizada desde
CloudShell, tras revalidar rol y nombre ausente e introducir el correo privadamente sin
eco. No habrá reintento automático ni difusión de identificadores o destinatario.

Checkpoint **E.8c completado, verificación pendiente**: el usuario informó
`preflight_ok=true`, `recipient_accepted=true`, `create_budget_call=success` y
`verification_pending=true`. AWS aceptó la única solicitud de creación con el
destinatario introducido privadamente. No se repite `CreateBudget`. Todavía no se ha leído
la configuración persistida ni se han verificado por separado las notificaciones, el
Free Plan o los posibles recursos automáticos de Cost Anomaly Detection. E.8d será una
lectura `DescribeBudget` con salida agregada saneada; ninguna API de Cost Explorer.

Checkpoint **E.8d completado**: el usuario confirmó `expected_role=true` y
`describe_budget_ok=true`. Los indicadores saneados `name_exact`, `cost_budget`, `monthly`,
`fixed_usd5`, `unblended_only`, `charge_filter_exact`, `starts_current_utc_month` y
`recurring_long_term` fueron todos `true`. La lectura `DescribeBudget` incluyó la expresión
de filtro y no divulgó gasto, identificadores ni fechas exactas. Quedan pendientes la
verificación separada de las cuatro notificaciones y su destinatario, la ausencia de
Budget Actions, la conservación posterior del Free Plan y la auditoría de posibles
recursos automáticos de Cost Anomaly Detection.

Primer intento **E.8e no concluyente por defecto del verificador**: el usuario informó
`expected_role=true`, `notifications_query_ok=false`, `error_type=KeyError`; no modificó
presupuesto ni alertas y no reintentó. El script asumía que toda notificación devuelve
`ThresholdType`, aunque AWS lo documenta como opcional. El fallo no demuestra ausencia ni
error de configuración de alertas. El siguiente intento omitirá ese campo en la solicitud
de suscriptores cuando falte en la respuesta y distinguirá «tipo de umbral no expuesto»
de «porcentaje verificado»; todas las lecturas siguen sin API de Cost Explorer ni eco del
correo.

Segundo intento **E.8e parcial**: `expected_role=true`, `notifications_query_ok=true`,
`notifications_count=4`, `four_alerts_core_exact=true`, `one_email_each=true` y
`sns_subscribers=0`. AWS omitió `ThresholdType` en las cuatro respuestas
(`threshold_type_explicit_percentage=false`, `threshold_type_omitted_count=4`,
`threshold_type_other_count=0`), por lo que esta lectura no prueba el tipo porcentual.
La comparación estricta contra el correo reintroducido devolvió
`same_private_recipient=false`; no se distingue todavía entre error de entrada,
normalización y destinatario realmente diferente. No se compartieron direcciones ni
se cambió el presupuesto. E.8e sigue abierto: primero se repetirá solo la comparación
privada con doble entrada y resultado agregado; después se resolverá el tipo de umbral.

Tercera lectura **E.8e — destinatario aún sin validar**: `expected_role=true`,
`recipient_check_ok=true`, `notifications_count=4`, entradas privadas no vacías e iguales,
un EMAIL por alerta y un único destinatario almacenado en AWS. Las comparaciones exacta
y normalizada contra el correo reintroducido fueron ambas `false`. No se divulgó ninguna
dirección ni se modificaron alertas. El siguiente checkpoint será inspección visual
read-only en la consola para que el usuario determine privadamente si el destinatario
almacenado es el que realmente quiere; no se actualizará ningún suscriptor sin una
decisión explícita. El tipo porcentual sigue sin demostrarse por la respuesta API.

**Aclaración humana posterior:** el correo reintroducido dos veces en la tercera lectura
es el destinatario que el usuario quiere para las cuatro alertas. Dado que ninguna
comparación coincidió con el único destinatario AWS, la configuración actual difiere de
la intención del usuario. No se modificaron suscriptores ni alertas y el correo no fue
expuesto. Se propone una corrección limitada mediante cuatro llamadas
`budgets:UpdateSubscriber` —una por alerta— con el antiguo suscriptor leído privadamente
de AWS y el nuevo introducido sin eco, sujetas a autorización explícita. No se cambiarán
presupuesto, umbrales, filtros, métricas ni otros recursos. Las cuatro llamadas no son
atómicas; ante fallo se detendrán sin reintento automático y se auditará el estado
parcial antes de decidir recuperación.

**Autorización limitada recibida:** el usuario autorizó exclusivamente sustituir los
cuatro suscriptores EMAIL actuales del presupuesto por su dirección introducida
privadamente, sin mostrar ni registrar ninguna de las dos direcciones. No autorizó
cambiar presupuesto, importe, período, métrica, filtros, umbrales, cantidad de alertas,
SNS, actions, reports ni otros recursos. Se hará preflight read-only y después una
actualización controlada por alerta con verificación individual; al primer fallo se
detendrá sin reintento automático y se auditará read-only el estado parcial. Al final se
verificará un EMAIL por alerta, los cuatro coincidentes con la dirección privada.
`ThresholdType` continúa fuera de esta autorización y se tratará separadamente. No se
ha ejecutado ninguna actualización de suscriptores.

Checkpoint **E.8e-R1 completado, read-only**: el usuario informó `expected_role=true`,
`notifications_count=4`, `four_alerts_core_exact=true`, `one_email_each=true`,
`single_current_recipient=true`, `new_input_confirmed=true`,
`new_differs_from_current=true`, `sns_subscribers=0`, `preflight_ok=true` y
`update_subscriber_called=false`. La dirección nueva se introdujo privadamente y no se
registró. El siguiente checkpoint actualizará solo ACTUAL 50 % mediante una llamada
`UpdateSubscriber` sin reintento automático, seguida de lectura de esa alerta y de las
otras tres. Si la llamada o la lectura falla, se detendrá el flujo para auditoría
read-only del estado parcial; no se supondrá éxito ni fracaso por una excepción.

**Ajuste previo a E.8e-R2 solicitado por el usuario:** antes de cualquier llamada
`UpdateSubscriber`, la dirección nueva introducida dos veces sin eco debe superar
`re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", new_first)`; el resultado se informa solo como
booleano saneado y forma parte de `preflight_ok`. Se conserva el alcance de una única
alerta ACTUAL 50 %, un intento total, lectura inmediata posterior y parada ante
incertidumbre. No se ejecutó R2 ni se mostró/registró ninguna dirección.

Checkpoint **E.8e-R2 completado**: el usuario confirmó `expected_role=true`,
`new_email_syntax_ok=true`, `preflight_ok=true`, `update_call=success`,
`four_alerts_core_unchanged=true`, `one_email_each_after=true`,
`target_new_recipient=true`, `other_three_unchanged=true`,
`sns_subscribers_after=0` y `verification_ok=true`. Una sola alerta —ACTUAL 50 %—
usa ahora la dirección deseada; las otras tres conservan el destinatario anterior.
La salida compartida no incluyó direcciones ni identificadores. E.8e-R3 debe verificar
este estado mixto antes de sustituir solo FORECASTED 80 %, con una llamada y sin
reintento automático. `ThresholdType` permanece sin demostrar y sin modificar.

**Replanificación de E.8e-R3 solicitada por el usuario antes de ejecutarla:** el
mecanismo de R2 quedó demostrado. Se reemplaza la propuesta de tres checkpoints
humanos por **un único bloque controlado** que actualiza en este orden FORECASTED 80 %,
ACTUAL 80 % y ACTUAL 100 %. Debe verificar antes el estado mixto exacto, pedir una
sola doble entrada privada con validación sintáctica, ejecutar cada
`UpdateSubscriber` con un único intento y leer internamente el resultado antes de
continuar. Ante fallo o incertidumbre, no habrá más mutaciones ni repetición del
bloque; se auditará read-only el estado parcial si las consultas funcionan. La
auditoría final comparará la configuración observable del presupuesto y de las
notificaciones con el baseline, exigirá cuatro alertas base, un EMAIL por alerta,
cuatro destinatarios iguales al deseado y cero SNS. Sólo se informarán booleanos y
contadores saneados. `ThresholdType` no se modifica ni se declara verificado por
esta operación. Ninguna de las tres actualizaciones restantes se ha ejecutado.

Checkpoint **E.8e-R3 completado** según la salida saneada del usuario:
`identity_query_ok/expected_role/preflight_read_ok/private_input_confirmed/new_email_syntax_ok/preflight_ok=true`;
`update_calls_attempted=3`, `update_calls_confirmed=3` y
`updates_verified_immediately=3`, sin llamada incierta, fallo de lectura intermedia ni
discordancia de estado. La auditoría final read-only devolvió `final_audit_ok=true`,
`complete=true`, `four_alerts_core_intact=true`, `budget_config_unchanged=true`,
`notification_definitions_unchanged=true`, `one_email_each=true`,
`sns_subscribers=0`, `recipient_counts_known=true`, `desired_recipient_count=4` y
`old_recipient_count=0`. Esto completa la sustitución de destinatarios, sin probar
todavía el tipo porcentual omitido por la API. No se recibieron direcciones, Account ID
ni ARN. Siguiente checkpoint: verificar visualmente, de forma read-only, las cuatro
definiciones porcentuales en la consola de Budgets; si no se muestran, dejarlas como
no verificables, sin modificar alertas.

Checkpoint **E.8f completado, solo lectura**: el usuario informó
`threshold_type_visible=true`, `actual_50_percentage=true`,
`forecasted_80_percentage=true`, `actual_80_percentage=true`,
`actual_100_percentage=true` y `changes_made=none`. La consola confirmó el tipo
porcentual de las cuatro alertas; la omisión previa de `ThresholdType` en la respuesta
API ya no impide esta conclusión visual. No se recibieron capturas ni datos privados.
Siguiente checkpoint: auditoría read-only de los posibles recursos automáticos de Cost
Anomaly Detection; conservarlos o eliminarlos exige decisión humana separada.

Checkpoint **E.9 inventario completado, solo lectura**: el usuario informó
`cad_page_accessible=true`, `cost_monitors_count=1`,
`alert_subscriptions_count=1` y `changes_made=none`. Es un inventario posterior a la
creación del Budget, no una prueba por sí solo de atribución automática. Antes de
presentar una decisión de conservación o eliminación, E.9a caracterizará sin cambios
si el par coincide con el monitor de servicios AWS y la suscripción de resumen diario
que AWS documenta como configuración automática al habilitar Cost Explorer. No se
compartieron nombres, destinatarios, ARN ni identificadores.

Checkpoint **E.9a completado, solo lectura**: el usuario confirmó
`aws_managed_monitor=true`, `aws_services_dimension=true`,
`subscription_linked_to_monitor=true`, `daily_summary=true`, `email_only=true`,
`sns_present=false` y `changes_made=none`. Este par 1/1 coincide con el monitor de
servicios AWS y la suscripción diaria que AWS documenta como configuración automática
al habilitar Cost Explorer. La concordancia no prueba causalidad sin baseline previo
o evento de creación correlacionado; se presenta como inferencia. AWS indica que la
configuración CAD predeterminada no añade coste, pero no sustituye las cuatro alertas
del Budget para el sublímite del proyecto. **Pausa obligatoria**: no conservar ni
eliminar explícitamente monitor o suscripción hasta decisión humana. No se compartieron
nombres, destinatarios, ARN, importes ni fechas.

Checkpoint **E.9b, decisión humana explícita**: conservar tal como están el único
monitor administrado por AWS para servicios AWS y su única suscripción vinculada de
resumen diario EMAIL, sin SNS. Se registran como protección secundaria consciente,
sin sustituir ni modificar las cuatro alertas de Budgets. El usuario no autorizó
cambios, personalizaciones ni recursos CAD adicionales; no se realizó ninguna
mutación para conservarlos. Siguen E.10 (ausencia de Budget Actions) y E.11
(reconfirmación visual de Free Plan/créditos tras la creación).

Checkpoint **E.10 completado, solo lectura**: el usuario informó
`expected_role=true`, `actions_query_ok=true`, `budget_actions_count=0`,
`budget_actions_absent=true` y `changes_made=none` para el presupuesto exacto. La
consulta paginada de AWS Budgets no llamó a Cost Explorer, no creó recursos ni expuso
Account ID/ARN. Siguiente checkpoint E.11: reconfirmación visual de Free Plan activo,
días y créditos restantes positivos en Billing Home, sin registrar importes ni fechas.

Checkpoint **E.11 completado, visual/read-only**: el usuario confirmó
`billing_home_plan_free=true`, `plan_active=true`, `days_remaining_positive=true`,
`credits_remaining_positive=true`, `upgrade_executed=false` y `changes_made=none`.
Billing Home demuestra que el presupuesto y sus alertas no alteraron el Free Plan ni
agotaron los créditos observables. No se recibieron importes, fechas exactas,
identificadores, datos de pago ni capturas. Restan cero access keys posterior, ausencia
de recursos de aplicación atribuibles, cierre de sesión y validaciones locales.

Checkpoint **E.12 completado, visual/read-only**: el usuario informó
`expected_user=true`, `access_keys_count=0` y `changes_made=none` para el IAM user
de entrada. No se recibieron IDs, credenciales ni capturas. El siguiente checkpoint
humano será cerrar CloudShell y la sesión AWS; la ausencia de recursos de aplicación
se formulará acotada a Task/027, no como inventario exhaustivo de toda la cuenta.

Checkpoint **E.13 completado**: el usuario informó `cloudshell_closed=true`,
`aws_console_signed_out=true`, `root_session_active=false`,
`iam_user_session_active=false`, `role_session_active=false`,
`application_resources_created_by_task=0` y
`cloud_resources_changed_during_close=none`. La ausencia de recursos de aplicación
es atestación limitada a Task/027, no inventario universal de AWS. No se recibieron
datos privados. Los Gates A–E están completos por acción humana; restan verificaciones
locales de documentos, Git y secretos antes de `Lista para validación`.

## H. Decisiones ya tomadas que no se reabren

- Arquitectura AWS serverless y frontend Cloudflare Pages.
- PostgreSQL en VPS externo; no RDS ni PostgreSQL en Lambda.
- PgBouncer y TLS como parte de `Task/029`.
- Terraform compartido local/real y D-06 resuelta.
- OIDC de GitHub sin credenciales permanentes pertenece a `Task/028`.
- Grafana Cloud + Alloy; D-19 permanece para `Task/041`.
- D-11, D-12, D-16, D-17, D-18, D-19 y D-20 conservan sus propietarios.

## I. Gate C — estrategia elegida y diseño exacto

El usuario confirmó **Free Plan con créditos activos** y eligió conservarlos. Quedan
expresamente no autorizados: upgrade a Paid, AWS Organizations e IAM Identity Center de
organización. La estrategia seleccionada es:

`IAM user de entrada sin privilegios directos → sts:AssumeRole con MFA → rol administrativo`

Esta elección queda registrada como decisiones **D-027-A a D-027-E**, **Aceptadas y
Vigentes** desde la aprobación final de Task/027. La autorización operativa separada para crear el
diseño exacto sí fue otorgada y ejecutada por el usuario.

Recursos del diseño autorizado, creados y verificados por el usuario:

| Recurso | Diseño |
| --- | --- |
| IAM user | `personal-blog-entry-admin`; consola solamente; MFA TOTP; sin grupos ni access keys |
| Política inline del user | `AssumePersonalBlogAdministratorOnly`: único `Allow` a `sts:AssumeRole` sobre el rol exacto |
| Rol | `PersonalBlogAdministrator`; sesión máxima 3600 s |
| Trust | Principal = ARN exacto del user; `aws:MultiFactorAuthPresent = true`; sin root, comodines ni `ExternalId` |
| Permisos del rol | AWS managed `AdministratorAccess` |
| Billing | Root activa una vez el acceso IAM a Billing; no concede permisos por sí solo |

Las políticas JSON completas, flujo diario, verificación STS, prueba de cero access keys,
evidencia de salida de root y rollback están en la
[ficha §6](../tasks/TASK-027-cloud-accounts-and-budgets.md).

Verificación ejecutada sin credenciales permanentes: el usuario asumió el rol desde la
consola, abrió una sesión nueva de CloudShell y ejecutó `aws sts get-caller-identity`. La
salida no se versionó; se registraron sólo los booleanos saneados que confirman el rol
esperado y descartan root y el IAM user directo.

Rollback: revocar primero las sesiones activas del rol, desadjuntar permisos, eliminar rol,
política/user/MFA/login profile, restaurar el toggle Billing sólo si Task/027 lo cambió y
verificar Free Plan, cero access keys y ausencia de Organization/Identity Center.

El usuario autorizó explícitamente crear exactamente este diseño el 2026-09-15. El primer
intento quedó detenido antes de cualquier mutación porque el entorno no expuso Chrome,
Edge ni navegador integrado y el controlador nativo no estaba conectado. El usuario indicó
después que operará el navegador manualmente y que el agente no debe volver a intentar
Computer Use. D-13 y sus umbrales quedaban entonces para Gate D; posteriormente fueron
decididos, mientras la autorización de Budgets sigue pendiente en Gate E.

El usuario decidió después operar el navegador manualmente. Checkpoint **C.1 completado**:
activó el acceso de usuarios y roles IAM a Billing y confirmó que no compartió datos
privados. Esta opción no concede permisos por sí sola. La identidad IAM sigue inexistente.

Checkpoint **C.2 completado**: creó `personal-blog-entry-admin` con acceso de consola,
sin permisos, grupos, MFA ni access keys, y sin compartir datos privados. El usuario no
puede operar recursos AWS en este estado.

Checkpoint **C.3 completado**: asoció al IAM user una aplicación TOTP distinta del factor
root; confirmó un dispositivo MFA activo, cero access keys y ningún dato privado compartido.
El login del IAM user todavía no se ha verificado.

Checkpoint **C.4 completado**: creó `PersonalBlogAdministrator` con trust exclusivo a
`personal-blog-entry-admin`, sin root ni wildcard y con MFA obligatorio; adjuntó únicamente
la AWS managed policy `AdministratorAccess`, fijó 3600 s, dejó la permissions boundary
vacía y no creó access keys. El IAM user todavía no tiene permiso para asumir el rol.

Checkpoint **C.5 completado**: añadió al IAM user únicamente la política inline
`AssumePersonalBlogAdministratorOnly`, con `sts:AssumeRole` sobre el rol exacto y sin
wildcards; confirmó cero políticas adicionales, grupos, boundary y access keys.

Checkpoint **C.6 completado**: cerró root, inició sesión como `personal-blog-entry-admin`
con MFA solicitado y aceptado, comprobó denegación de acceso directo a IAM Users y confirmó
que todavía no asumió el rol y que siguen existiendo cero access keys.

Checkpoint **C.7 completado**: cambió exitosamente a `PersonalBlogAdministrator`; confirmó
root e identidad directa del IAM user inactivos, contexto MFA aceptado, duración máxima de
3600 s y cero recursos creados o modificados durante la prueba.

Checkpoint **C.8 completado**: desde una CloudShell nueva obtuvo exclusivamente los
booleanos STS `expected_role=true`, `root=false` y `direct_user=false`; no configuró
credenciales, no mostró Account ID/ARN y mantuvo cero access keys y recursos de aplicación.

Checkpoint **C.9 completado**: la auditoría read-only del IAM user confirmó cero access
keys, un MFA, cero grupos, cero políticas administradas, ninguna permissions boundary y
una única inline `AssumePersonalBlogAdministratorOnly`; sus comprobaciones `allow`,
`only_assume_role` y `exact_role` devolvieron `true`.

Checkpoint **C.10 completado**: la auditoría read-only del rol confirmó 3600 s, una sola
AWS managed `AdministratorAccess`, cero políticas inline y ninguna boundary; el trust
devolvió una declaración, user exacto `true`, root/wildcard `false`, `AssumeRole=true` y
condición MFA `true`.

Antes de C.11, el usuario rechazó como insuficiente consultar IAM Identity Center sólo en
`us-east-1`. El checkpoint corregido enumerará por API read-only todas las regiones de la
cuenta con estado `opt-in-not-required` u `opted-in`, ejecutará `sso-admin list-instances`
en cada una y devolverá únicamente totales agregados. Cualquier error regional detiene la
auditoría y se informa sólo con región y clase de error; nunca se convierte en cero.

Checkpoint **C.11 completado**: la verificación corregida devolvió
`organizations_absent=true`, `identity_center_instances_total=0` y
`identity_center_regions_with_instances=0`, con cero consultas regionales fallidas y sin
mostrar o compartir IDs, ARN o datos de identidad. No realizó cambios.

Antes de C.12, el usuario precisó el criterio de evidencia: Billing and Cost Management
Home es la superficie obligatoria para demostrar Free Plan activo, días restantes y
créditos restantes positivos, sin upgrade. La página `Credits` queda como corroboración
opcional; no mostrar información adicional allí no invalida C.12 si Billing Home ya aporta
evidencia inequívoca. Nunca se registran monto, fecha, Account ID, Credit ID, pago o capturas.

Checkpoint **C.12 completado**: Billing Home mostró Free Plan activo, días restantes y
créditos restantes positivos, sin upgrade. `Credits` se consultó opcionalmente. No se
enviaron a Codex ni se documentaron importes, fechas, Account ID, Credit ID o datos de pago.

Checkpoint **C.13 completado**: el usuario cerró CloudShell y terminó completamente la
sesión AWS. Confirmó que no permanecía activa ninguna sesión root, del IAM user o del rol;
se mantuvieron cero access keys y cero recursos de aplicación, sin compartir datos
privados. Con esto, **Gate C queda completado** y el siguiente checkpoint es Gate D.

## J. Operaciones manuales obligatorias

- Alta/login de cuentas y MFA de AWS root/Cloudflare — **completados por el usuario**.
- Plan/créditos y estrategia Gate C — **decididos: Free + IAM standalone**.
- Alta y MFA del IAM user, rol y política — **completadas manualmente por checkpoints**, con secretos bajo control humano.
- Confirmación humana saneada de la configuración que las APIs no expongan.
- Selecciones financieras/de seguridad de Gates C y D.

## K. Operaciones automatizables de forma segura

- STS e inspección selectiva de perfil/endpoint sin mostrar secretos.
- Consultas read-only a IAM/Budgets después de disponer de sesión temporal.
- Creación exacta del presupuesto tras preflight y autorización.
- Lectura posterior del presupuesto y notificaciones por API.
- Validaciones Git, secretos, documentación y ausencia de recursos de aplicación.

## L. Riesgos

Cuenta equivocada, root operativo, Floci/endpoint heredado, secretos expuestos, pérdida de
créditos por AWS Organizations, costos inesperados, confundir presupuesto AWS con global,
precios caducados, evidencia manual tratada como API y despliegue accidental. Las
mitigaciones concretas constan en la ficha §13.

## M. Criterios de aceptación

Son los 16 criterios mínimos de la ficha §10. La evidencia saneada de Gates A–E cubre
cuentas, MFA, root fuera del flujo, identidad administrativa, D-13, presupuesto, cuatro
alertas, CAD conservado, cero Budget Actions/access keys, Free Plan/créditos posteriores,
cero recursos de aplicación atribuibles y cierre de sesiones. Validación local y revisión
de coherencia documental superadas: quedó `Lista para validación` hasta recibir la
aprobación exacta el 2026-09-17.

## N. Plan de ejecución ordenado

1. Fuentes, Git, rama y discovery read-only — **completado**.
2. Documentación inicial — **completada**.
3. Gate A, cuentas — **completado por el usuario**.
4. Gate B, MFA — **completado por el usuario**.
5. Gate C, identidad administrativa — **completado manualmente; C.1–C.13 conformes**.
6. STS y evidencia operativa segura — **completados**.
7. Gate D, D-13/umbrales — **completado**.
8. Preflight de Gate E — **documentado y autorizado; E.1–E.8c completados (ruta UI de E.8 bloqueada)**.
9. Presupuesto y cuatro alertas verificados; CAD 1/1 conservado por decisión humana;
   cero Budget Actions/access keys, Free Plan/créditos posteriores y cierre de sesiones
   verificados — **completado**.
10. Ausencia de recursos de aplicación atribuibles atestada; validación local, DoD y
    cierre técnico documental completados. Aprobación humana recibida el 2026-09-17.

## O. Decisiones técnicas aprobadas

- **D-13, resuelta:** techo de voluntad de gasto USD 20/mes
  global y sublímite AWS USD 5/mes. AWS Budgets observa solo el segundo, no el total.
- **Identidad humana AWS:** IAM user de entrada solo por consola, MFA TOTP y permiso
  exclusivo de `sts:AssumeRole` sobre `PersonalBlogAdministrator`; rol con MFA exigido,
  `AdministratorAccess` y sesión máxima de 3600 s. Cero access keys. No Organizations,
  Identity Center ni upgrade; root fuera del flujo operativo.
- **Costos AWS:** un Cost budget mensual recurrente, fijo USD 5, UnblendedCost, todos
  los servicios y exclusión exacta Credit/Refund; cuatro alertas porcentuales con un
  EMAIL privado compartido entre ellas, cero SNS y Budget Actions/Reports.
- **CAD:** conservar sin cambios el monitor AWS-managed para servicios AWS y la
  suscripción diaria EMAIL vinculada, sin SNS. Protección secundaria, no sustituto
  de los umbrales de Budgets; no autoriza personalización ni recursos adicionales.
- **ADR:** ninguno nuevo. Son decisiones operativas de esta cuenta y esta tarea; D-13
  quedó resuelta por la aprobación exacta de Task/027.

## P. Riesgos y deuda técnica pendiente

- AWS Budgets **no detiene gasto** y su facturación/forecast pueden retrasarse. Las
  cuatro alertas son advertencias, no un límite duro; propietario: operación cloud
  desde Task/027 y validación en despliegues posteriores.
- El Free Plan y los créditos tienen duración/saldo finitos. E.11 prueba el estado
  posterior a Gate E, no garantiza elegibilidad futura; revalidar antes de desplegar
  en tareas posteriores, sin upgrade implícito.
- El par CAD coincide con el patrón automático documentado, pero no se obtuvo baseline
  anterior ni evento de creación correlacionado. Su origen automático es inferencia;
  mantenerlo no eleva sus alertas al nivel del presupuesto del proyecto.
- El correo de Cloudflare no fue comprobado; el plan Free y MFA sí. Verificarlo de
  forma privada antes de usar servicios que dependan de correo, sin documentar la
  dirección.
- El VPS, Grafana Cloud, dominio y demás componentes del techo global aún no tienen
  costo contratado. `Task/029` decide el VPS y D-19 permanece en `Task/041`.

## Q. Validación solicitada y aprobación recibida

1. Revisar la [ficha](../tasks/TASK-027-cloud-accounts-and-budgets.md), este reporte y
   [D-13](../architecture/open-decisions.md) para confirmar que presupuesto, IAM y
   CAD reflejan exactamente las decisiones tomadas.
2. Confirmar que la evidencia de Gates A–E es agregada/saneada: ningún correo,
   Account ID, ARN, factor MFA, clave o importe exacto de créditos está registrado.
3. Antes de la aprobación, verificar que `Task/028` y `Task/029` seguían pendientes,
   D-13 aún era propuesta y no había commit, push, PR ni merge.
4. El usuario aprobó el resultado el 2026-09-17 con la expresión exacta
   `approved: Task/027-Configurar-Cuentas-y-Presupuestos`. D-13 y las decisiones D-027-A
   a D-027-E pasan a vigentes; el flujo Git posterior se registra como cierre separado.

## R. Validación local y Definition of Done

| DoD | Resultado y evidencia |
| --- | --- |
| 1 — alcance | PASS — checklist de la ficha cubierto con Gates A–E y documentación D-13. |
| 2 — sin funcionalidad extra | PASS — sólo documentación infra y mutaciones cloud autorizadas por el usuario; CAD 1/1 conservado sin cambios. |
| 3 — compilación | N/A — no se modificó código ni Terraform. |
| 4 — pruebas de código | N/A — no se modificó código; las validaciones son las lecturas AWS y controles documentales. |
| 5 — documentación | PASS — ficha, reporte, STATUS, ROADMAP, STAGE-09 y D-13 coherentes; enlaces relativos verificados. |
| 6 — secretos | PASS — búsqueda local de patrones sensibles sin correos, Account IDs ni claves; los datos privados nunca se compartieron. |
| 7 — validación para usuario | PASS — pasos reproducibles en §Q sin solicitar datos sensibles. |
| 8 — decisiones | PASS — §O y D-13 aceptadas por aprobación; sin ADR nuevo. |
| 9 — riesgos/deuda | PASS — §P identifica límites de Budgets/CAD, Free Plan finito y costos futuros. |
| 10 — no rompe tareas previas | PASS — sin código ni configuración de aplicación modificados; backend/frontend limpios. |
| 11 — base `main` | PASS — ficha §0 y Git local: `HEAD == main == origin/main` antes de cambios; nunca `dev`. |
| 12 — estado duradero Git/GitHub | PASS — preparación histórica fechada y regla permanente de aprobación; ningún PR o normalización actual se presenta como requisito de Task/028. |

Para la DoD cloud: C-2, C-5 y C-8–C-11 aplican y pasan (destino AWS real, evidencia
distinta de Floci, autorización, recursos IAM/Budget/CAD enumerados, impacto de costo
documentado, sin secretos). C-1, C-3, C-4, C-6 y C-7 son N/A: esta tarea no ejecutó
Terraform, no modificó su grafo/estado ni tocó la matriz de paridad. No se invocaron
tests o builds de backend/frontend porque permanecen intactos.

Validaciones locales al corte 2026-09-17: rama infra correcta, backend/frontend limpios,
`git diff --check` sin errores, enlaces relativos de los seis documentos afectados
resueltos y búsqueda de patrones sensibles con cero coincidencias. Ningún commit,
push, merge o PR se ejecutó en Task/027 antes de la aprobación.

## Estado tras la aprobación

- Proyecto: **27/41 ≈ 66 %**.
- Stage 09: **En progreso; 1/3 aprobadas; ≈ 33 %**.
- Task/027: **Aprobada el 2026-09-17**; Gates A–E completos; E.13 cerró las sesiones AWS y atestó cero recursos de aplicación atribuibles; validación local final superada.
- Task/028 y Task/029: **Pendientes, no iniciadas**.
- D-13: **resuelta** — USD 20/mes global, sublímite AWS USD 5/mes.
- Mutaciones ejecutadas por el agente: **0**. El usuario creó las cuentas, completó
  privadamente MFA y la configuración IAM de Gate C, y ejecutó la única llamada
  autorizada `CreateBudget` de Gate E y las cuatro sustituciones EMAIL autorizadas.
- Recursos de aplicación creados: **0 atribuibles a Task/027**.
- Antes de la aprobación del 2026-09-17 no se ejecutó commit, push, merge ni PR en
  Task/027. El cierre Git posterior no altera la evidencia cloud ni autoriza iniciar Task/028.
