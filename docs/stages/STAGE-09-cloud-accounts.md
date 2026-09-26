# ETAPA 09 — Cuentas y Seguridad Cloud

| Campo | Valor |
| --- | --- |
| **Número** | 09 |
| **Estado** | **En progreso** — `Task/027` Aprobada, 1/3 tareas aprobadas |
| **Dependencias** | [ETAPA 08](STAGE-08-cloud-ready.md) |
| **Tareas** | 3 |
| **Aprobadas** | 1 |
| **Avance** | ≈ 33 % |
| **Hito que completa** | Cuentas cloud seguras, con presupuesto y **acceso de GitHub Actions a AWS sin credenciales permanentes** (OIDC, `Task/028`). El modelo de identidad del **VPS hacia AWS** se decide en `Task/029` (**D-16**, abierta) y **Cloudflare y el proveedor del VPS pueden exigir otro mecanismo** (`Task/039`). *(Acotado en `Task/005.6`: el hito afirmaba «acceso sin credenciales permanentes» sin restringir el sujeto, lo que prejuzgaba decisiones todavía abiertas.)* |

---

## Objetivo

Crear las cuentas cloud con controles de costo y de acceso **antes** de desplegar
cualquier recurso.

> Esta es la **primera etapa que interactúa con proveedores cloud**. Cada tarea requiere
> autorización explícita del usuario antes de ejecutarse.

## Por qué esta etapa existe

El mayor riesgo de un proyecto personal en la nube no es técnico: es una factura
inesperada. Presupuestos, alarmas y MFA van **antes** que el primer recurso.

## Tareas

### `Task/027-Configurar-Cuentas-y-Presupuestos` — *Aprobada el 2026-09-17*

Cuentas AWS y Cloudflare, MFA en todos los accesos, presupuestos y alertas de costo.

**Depende de:** `Task/026`. **Repositorio:** `personal-blog-infra` (documentación).

Iniciada el 2026-09-15 desde `main` limpio (`67c19049…`). Gates A/B completos con evidencia
saneada. AWS está en Free Plan con créditos activos y Cloudflare en Free. Gate C conserva
ese estado mediante un IAM user de entrada sin permisos directos que sólo puede asumir con
MFA un rol administrativo de una hora. Organizations/Identity Center y access keys quedan
excluidos. El usuario ejecutó y verificó manualmente C.1–C.13, incluida la identidad STS,
las auditorías de configuración, la conservación del Free Plan y el cierre total de las
sesiones. Gate D fijó D-13, resuelta con la aprobación de Task/027: USD 20/mes global y
USD 5/mes AWS, con cuatro alertas y sin funciones pagas/automáticas. Gate E fue
autorizado el 2026-09-16; E.1–E.4
reconfirmaron login IAM/MFA, rol/STS y Free Plan. E.5 descartó el nombre duplicado en
Budgets. E.6 abrió el asistente avanzado de Cost budget, sin crear. La vista previa mostró
acceso denegado a Cost Explorer; no se habilitó manualmente. E.7 completó los detalles
básicos sin enviar; E.8 se detuvo sin cambios: el selector de Credit/Refund devolvió
`User not enabled for cost explorer access`, sin filtro aplicado. Un posible efecto
automático de Cost Explorer/Anomaly Detection fue autorizado acotadamente por el usuario;
tras crear se auditó read-only y se decidió por separado conservar el par 1/1. E.8a
CloudShell confirmó el rol y la ausencia del budget; E.8b validó localmente el esquema
con un destinatario ficticio. El usuario confirmó que E.8c pasó preflight y que la única
llamada `CreateBudget` fue exitosa con destinatario introducido privadamente.
No se repetirá la creación.
En E.8d, `DescribeBudget` confirmó con booleanos saneados el nombre, tipo Cost, período
mensual recurrente, límite fijo USD 5, métrica UnblendedCost y filtro exacto que excluye
solo Credit/Refund. E.8e-R3 confirmó cuatro alertas base intactas, un destinatario EMAIL
deseado por alerta, cero SNS y configuración del presupuesto sin cambios observables tras
cuatro sustituciones autorizadas. El tipo porcentual no fue expuesto por la API, pero E.8f
lo confirmó para las cuatro alertas mediante inspección visual read-only, sin cambios.
E.9 observó read-only un monitor y una suscripción de Cost Anomaly Detection, sin cambios.
E.9a confirmó monitor administrado por AWS para servicios AWS y suscripción vinculada de
resumen diario solo por EMAIL, sin SNS. El par coincide con la configuración automática
documentada por AWS, aunque su origen causal no está probado. En E.9b el usuario decidió
conservarlo sin cambios como protección secundaria; no autorizó personalizaciones.
E.10 confirmó read-only cero Budget Actions para el presupuesto exacto. E.11 reconfirmó
visualmente Free Plan activo con días y créditos restantes positivos, sin upgrade ni
cambios. E.12 reconfirmó cero access keys del IAM user de entrada. E.13 cerró CloudShell
y todas las sesiones AWS; el usuario atestó cero recursos de aplicación creados por
Task/027, sin pretender un inventario exhaustivo de la cuenta. La validación local de
Git, enlaces y patrones de secretos pasó; el usuario aprobó Task/027 el 2026-09-17.
**0 mutaciones ejecutadas por el agente;
1 tarea aprobada en esta etapa.**

[Ficha](../tasks/TASK-027-cloud-accounts-and-budgets.md) ·
[Reporte](../task-reports/TASK-027-report.md)

### `Task/028-GitHub-OIDC-AWS` — *Lista para validación · bloqueo externo H-028-1*

Federación OIDC real GitHub Actions → AWS, **sin access keys permanentes**.
Rol exclusivo `PersonalBlogGitHubOidcValidation`, cero managed/inline policies:
no acredita despliegue. Root separado, provider A/B/C fail-closed, EX-028-C7,
trust Task exacta/caducable → main exclusiva y reconfirmación postmerge.
Checkpoint del 2026-09-22: implementación/pruebas locales ejecutadas, autorizadas el 2026-09-21;
federación real pendiente. Checkpoint del 2026-09-24: bajo autorización acotada a solo lectura
y plan se observó el caso real **A** con ownership **A** y se revisó un plan de **dos**
creaciones administradas, con **cero mutaciones AWS** y **sin apply**. La federación real,
las publicaciones y la reconfirmación postmerge siguen pendientes de autorización.
Checkpoint del 2026-09-24: **federación real demostrada** —dos recursos creados, trust
exacta, cero políticas, `AccessDenied` e `InvalidIdentityToken` exactos en la primera
ejecución premerge—. Los criterios de salida de abajo **no se marcan**: por convención
de esta etapa, una casilla se marca cuando la respalda una tarea **aprobada**.
[Ficha](../tasks/TASK-028-github-oidc-aws.md) · [Reporte §12](../task-reports/TASK-028-report.md).

Task/038 define permisos mínimos backend; Task/039 los de Terraform; Task/040
valida integralmente. Branch protection queda fuera de Task/028, pero debe existir
antes de habilitar roles de despliegue efectivos. No promover el rol de validación.

**Depende de:** `Task/027`.

### `Task/029-Preparar-PostgreSQL-Produccion-en-VPS` — *Pendiente*

> **Alcance redefinido el 2026-08-15** por `Task/005.3` (mantenimiento). El **identificador
> `029` no cambia**; cambian el nombre y el alcance. Antes se llamaba
> `Task/029-Seleccionar-PostgreSQL-Administrado` y daba por supuesto un servicio
> administrado. Estrategia:
> [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) ·
> [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) — **Aceptada**.

Selección y preparación del **VPS externo** que alojará el PostgreSQL de producción, con
**PgBouncer** delante, **PostgreSQL privado** y conexión **TLS** desde la Lambda, que
permanece en AWS.

Debe cubrir, como mínimo:

| Bloque | Contenido |
| --- | --- |
| **Selección** | Comparar proveedores con **precios actuales** · seleccionar VPS, región y tamaño · CPU, RAM, almacenamiento · IPv4/IPv6 · tráfico y *egress* · snapshots · **RTT medido** hacia la región AWS · costo total |
| **Base de datos** | Distribución del host · versión de PostgreSQL · persistencia · *filesystem* y volumen · `max_connections` |
| **Conexiones** | PgBouncer · `pool_mode` · tamaños de pool · *tuning* · relación con la concurrencia reservada de Lambda |
| **Seguridad** | TLS · **ciclo de vida del certificado de PgBouncer**: emisión, CA, *hostname*, instalación, renovación y confianza desde el cliente · SCRAM-SHA-256 · evaluación de mTLS · firewall *deny-by-default* · SSH por llave · usuarios · *hardening* |
| **Secretos del host** (`Task/006.2`) | **D-17** — herramienta de gestión de **secretos cifrados**, con la clave **fuera del repositorio** y descifrado local seguro. **SOPS + age es candidato, no decisión.** Custodia y **rotación** de la clave. **SSM sirve a la Lambda, no al VPS** |
| **Configuración del SO** (`Task/006.2`) | **D-18** — mecanismo de configuración interna del host: **Ansible**, **cloud-init** o **scripts idempotentes**. **Terraform no configura Linux.** Cómo se ejecuta y cómo se detecta el *drift* (**R-42**) |
| **Observabilidad** (`Task/006.2`) | **Grafana Alloy** instalado y configurado en el VPS, enviando el *baseline* a **Grafana Cloud**. **No se autohospedan Grafana, Prometheus ni Loki.** Su credencial es un secreto del host (**D-17**) |
| **Operación** | Backups **fuera del host** · restore **probado** · almacenamiento externo · retención · RPO · RTO · **baseline de observabilidad del VPS** · espacio en disco · actualizaciones y parcheo · rollback · recuperación |
| **Identidad** | **D-16** — con qué mecanismo escribirá el VPS sus backups en AWS, y bajo qué restricciones de seguridad |
| **IaC** | Soporte de Terraform del proveedor · documentación operacional |

Resultado registrado como ADR o como actualización del ADR vigente.

**Depende de:** `Task/027`. **Repositorio:** `personal-blog-infra`.

#### Qué `Task/029` **define y prepara**, y qué **no puede validar todavía**

> Corregido en `Task/005.5`. La versión anterior exigía como criterio de salida evidencia
> que **solo puede existir después** de `Task/030` (S3) y `Task/032` (Lambda). Una tarea no
> puede depender de recursos que se crean más tarde.

| Materia | `Task/029` entrega | Se valida de verdad en |
| --- | --- | --- |
| **Backup off-host** | Mecanismo completo —dump, cifrado, retención— y **restore demostrado** contra un destino externo **disponible en ese momento** | `Task/030` fija S3 como destino definitivo · `Task/040` valida la cadena completa |
| **Identidad hacia AWS** | **Decisión D-16** y sus restricciones de seguridad. **No** se crea el principal | `Task/030` lo materializa |
| **RTT `Lambda ↔ VPS`** | RTT **medido** hacia la región AWS objetivo, con método reproducible y registrado — criterio de selección, no estimación | `Task/032` y `Task/040`, con la Lambda real |
| **Concurrencia y pool** | Números **derivados y justificados**: `max_connections`, pool de PgBouncer y la *Reserved Concurrency* que se pedirá | `Task/032` la aplica · `Task/040` la valida bajo carga real |
| **Observabilidad del VPS** | *Baseline* configurado: uptime, CPU, RAM, disco, PostgreSQL, PgBouncer, fallo de backup y caducidad de certificado | `Task/040` verifica que opera de verdad |
| **Certificado TLS** | Emitido, instalado, con renovación definida y confianza verificada desde un cliente | `Task/040` lo valida **desde la Lambda real** |

**No se decide aquí** el mecanismo concreto de identidad —clave de larga vida, IAM Roles
Anywhere u otro—: **D-16** sigue **abierta** hasta `Task/029`. Y **`Task/028` no la
resuelve**: OIDC de GitHub Actions hacia AWS **no** entrega credenciales a un host externo.

## Criterios de salida de la etapa

- [x] MFA activo en la cuenta raíz de AWS y en Cloudflare — evidencia humana saneada de
      login con TOTP; Task/027 aprobada.
- [x] La cuenta raíz de AWS no se usa para operar; existe un usuario/rol administrativo —
      verificado en Gate C; Task/027 aprobada.
- [x] Presupuesto mensual definido con alertas por umbral — configuración y cuatro
      destinatarios verificados en Gate E; Task/027 aprobada.
- [ ] **GitHub Actions** asume un rol AWS vía OIDC; no hay claves de acceso de larga vida
      **en GitHub**. Esta afirmación se limita a GitHub Actions: **no** describe todavía
      cómo el VPS accederá a AWS (**D-16**).
- [ ] El rol de validación tiene **cero managed policies y cero inline policies**,
      trust exacta y GetCallerIdentity correcto, con evidencia real saneada.
- [ ] Las operaciones negativas elegidas devuelven **AccessDenied**; no se deduce
      ausencia universal de permisos por resource-based policies de toda la cuenta.
- [ ] La trust final acepta exclusivamente main; el rechazo desde Task con token
      nuevo y la reconfirmación postmerge main quedan demostrados.

Permisos de despliegue: fuera de este criterio, propietarios Task/038 y Task/039,
validación integral Task/040. Inspección de resource policies: limitada al inventario
efectivamente comprobado.

- [ ] **Proveedor de VPS seleccionado**, con costo, región y límites documentados, usando
      **precios verificados en el momento de la selección**.
- [ ] El **RTT hacia la región AWS objetivo** está **medido**, no estimado, con método
      reproducible registrado. El RTT definitivo `Lambda → PgBouncer` se mide en `Task/032`.
- [ ] La estrategia de conexión desde Lambda está definida: **PgBouncer**, tamaños de pool y
      `max_connections` coherentes entre sí, y la *Reserved Concurrency* que se solicitará
      a `Task/032`.
- [ ] **PostgreSQL no es alcanzable desde Internet**; solo PgBouncer está expuesto.
- [ ] La conexión `Lambda → PgBouncer` usa **TLS con validación de certificado**, y el
      **ciclo de vida del certificado** —emisión, CA, *hostname*, renovación, caducidad—
      está definido y operativo.
- [ ] Existe una estrategia de **backup fuera del host** y un **restore demostrado** contra
      un destino disponible en ese momento. El destino **definitivo en S3** lo materializa
      `Task/030`.
- [ ] **D-16 resuelta**: está decidido con qué mecanismo el VPS escribirá en AWS y bajo qué
      restricciones. Su **materialización** es de `Task/030`.
- [ ] Existe un ***baseline* de observabilidad del VPS** configurado —uptime, CPU, RAM,
      disco, PostgreSQL, PgBouncer, fallo de backup, caducidad de certificado—, **enviado
      fuera del host mediante Grafana Alloy hacia Grafana Cloud** (**O-10**). `Task/017` es
      local y `Task/031` es solo AWS: **ninguna de las dos cubre esto**.
- [ ] **D-17 resuelta**: está decidida la herramienta de secretos cifrados del VPS, con
      custodia y rotación de la clave definidas. **Ningún secreto del host versionado en
      claro.**
- [ ] **D-18 resuelta**: está decidido el mecanismo de configuración interna del sistema
      operativo, y **no es Terraform**.
- [ ] La telemetría que sale hacia Grafana Cloud **no contiene secretos ni datos personales
      innecesarios** (**O-09**).
- [ ] Ninguna credencial de producción está versionada.

## Fuera del alcance de la etapa

- **Crear el bucket S3 de backups, su política y el principal de acceso del VPS**: es de
  `Task/030`. Aquí solo se **decide** el mecanismo (**D-16**).
- **Medir el RTT desde la Lambda real** y fijar la *Reserved Concurrency*: `Task/032`.
- **Validar la cadena backup → S3 → restore de extremo a extremo**: `Task/040`.
- Desplegar recursos de aplicación (Etapa 10).
- Automatizar despliegues (Etapa 11).
- Conectar la Lambda a una VPC o introducir NAT Gateway por esta decisión: excluido por
  [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) salvo requisito real y decisión
  separada.
- Alta disponibilidad, réplicas o *failover* automático: el SPOF de un solo VPS se acepta
  conscientemente en la primera versión.

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Costo inesperado desde el primer día. | Presupuesto y alarmas creados antes que cualquier recurso. |
| Credenciales de larga vida filtradas. | OIDC con roles temporales; ninguna clave estática. |
| Rol OIDC con permisos excesivos. | Permisos mínimos, acotados por repositorio y rama. |
| Agotamiento de conexiones de PostgreSQL desde Lambda (**R-03**, **R-33**). | **PgBouncer** con pool limitado más *Reserved Concurrency* de Lambda; los números salen de pruebas, no de intuición. |
| **El VPS añade superficie de ataque** expuesta a Internet (**R-30**). | Firewall *deny-by-default*, SSH por llave, PostgreSQL privado, TLS obligatorio, parcheo. |
| **Backup no restaurable** (**R-31**). | Un backup no está validado hasta haberse restaurado; la prueba es criterio de salida. |
| **Elegir un VPS lejano por ahorrar poco** y pagar latencia en cada consulta (**R-34**). | RTT **medido** como criterio de selección, no el precio en solitario. |
| **Los secretos del host acaban en claro o sin rotación** (**R-40**). | Cifrado obligatorio, clave fuera del repositorio, permisos mínimos y rotación definida (**D-17**). |
| **El agente de observabilidad compite con PostgreSQL** por RAM, CPU y disco (**R-41**). | **Agente, no *stack***: Alloy en lugar de Grafana + Prometheus + Loki autohospedados. El dimensionamiento lo contempla. |
| ***Drift* de configuración del host**, que Terraform no ve (**R-42**). | Mecanismo idempotente y reproducible (**D-18**), runbooks (`Task/026`) y verificación en `Task/040`. |

## Siguiente etapa

[ETAPA 10 — Despliegue Cloud](STAGE-10-cloud-deployment.md)
