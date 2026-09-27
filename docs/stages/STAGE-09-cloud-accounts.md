# ETAPA 09 — Cuentas y Seguridad Cloud

| Campo | Valor |
| --- | --- |
| **Número** | 09 |
| **Estado** | **En progreso** — `Task/027` y `Task/028` Aprobadas, 2/3 tareas aprobadas. *(Corregido en `Task/028.2`: decía «`Task/027` Aprobada, 1/3».)* |
| **Dependencias** | [ETAPA 08](STAGE-08-cloud-ready.md) |
| **Tareas** | 3 |
| **Aprobadas** | 2 |
| **Avance** | ≈ 67 % |
| **Hito que completa** | Cuentas cloud seguras, con presupuesto y **acceso de GitHub Actions a AWS sin credenciales permanentes** (OIDC, `Task/028`). El modelo de identidad del **VPS hacia AWS** se decide en `Task/029` (**D-16**, abierta) y **Cloudflare y el proveedor del VPS pueden exigir otro mecanismo** (`Task/039`). *(Acotado en `Task/005.6`: el hito afirmaba «acceso sin credenciales permanentes» sin restringir el sujeto, lo que prejuzgaba decisiones todavía abiertas.)* *(Enmienda propuesta por `Task/028.2`: el hito incluye además el **diseño RDS preparado** por `Task/029`, **sin provisión**; D-16 tiene cierre por no aplicabilidad propuesto, y Cloudflare sigue pudiendo exigir otro mecanismo en `Task/039`.)* |

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

### `Task/028-GitHub-OIDC-AWS` — *Aprobada el 2026-09-26*

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
ejecución premerge—. Cierre del 2026-09-26: transición a trust `main`, segunda publicación
con el `AccessDenied` esperado, custodia EX-028-C7 cerrada con recuperación verificada, y
**H-028-1 y H-028-2 resueltas dentro de esta misma tarea** —espejo privado que preserva el
digest, y `CVE-2026-84445` **corregido** en Portainer, `minio` y `mc`, con el residual
aceptado de MinIO de **99 a 10** y **cero identidades nuevas**—. El 2026-09-26, bajo
autorización acotada, el derivado corregido queda **publicado** en el GHCR privado con etiqueta
nueva —digest preservado por construcción, verificado releyéndolo del registro, identidad de
Task/027.1 intacta— y **consumido** por el entorno local, que ya no ejecuta la identidad
vulnerable. Ese mismo día se corrigió el **runtime** de Portainer, que seguía ejecutando 2.39.7
aunque la configuración ya fijara 2.45.1 —respaldo restaurado y verificado antes de migrar—, con
lo que H-028-2 cierra de verdad. **Aprobada** el 2026-09-26 mediante
`approved: Task/028-GitHub-OIDC-AWS`: sus decisiones pasan a **Aceptadas y Vigentes** sin ADR
nuevo, **EX-028-C7** queda **cerrada** y el runbook pasa a **Vigente**. Con ella se marcan tres
de los cuatro criterios de salida que le corresponden; el cuarto sigue abierto porque **la
reconfirmación postmerge requiere el merge humano** y nunca fue prerrequisito de la aprobación.
*(Actualizado en `Task/028.2`: el cuarto criterio quedó demostrado el 2026-09-26 —`Verify
AWS OIDC` **success** sobre `main` en `e0fa95b`— y lo registró `Task/028.1`; ver los
criterios de salida. Este párrafo había quedado sin actualizar.)*
[Ficha](../tasks/TASK-028-github-oidc-aws.md) ·
[Reporte §12-§26](../task-reports/TASK-028-report.md).

Task/038 define permisos mínimos backend; Task/039 los de Terraform; Task/040
valida integralmente. Branch protection queda fuera de Task/028, pero debe existir
antes de habilitar roles de despliegue efectivos. No promover el rol de validación.

**Depende de:** `Task/027`.

### `Task/029-Preparar-PostgreSQL-Produccion-en-RDS` — *Pendiente*

> **Alcance redefinido de nuevo el 2026-09-27** por `Task/028.2` (mantenimiento):
> **propuesta pendiente de aprobación**. El **identificador `029` no cambia**; cambian el
> nombre y el alcance. Antes se llamaba `Task/029-Preparar-PostgreSQL-Produccion-en-VPS`,
> y antes aún `Task/029-Seleccionar-PostgreSQL-Administrado`. Estrategia propuesta:
> [production-postgresql-rds.md](../architecture/production-postgresql-rds.md) ·
> [ADR-010](../adr/ADR-010-production-postgresql-on-rds.md) — **Propuesta**. Ficha:
> [TASK-029](../tasks/TASK-029-prepare-production-postgresql-rds.md).

**Decide y prepara el PostgreSQL de producción en Amazon RDS privado. No provisiona
nada.** Se conserva el principio de `Task/005.5`: *una tarea no exige como evidencia
recursos que crea una tarea posterior*.

| Qué | Contenido | Dónde se demuestra |
| --- | --- | --- |
| **Decide** | **D-22** (región, versión, clase, almacenamiento, disponibilidad, VPC, subnets, security groups, rutas y *endpoints*) · **D-23** (TLS, KMS, credenciales, SSM frente a Secrets Manager, IAM DB auth evaluable) · **D-24** (canal privado de administración y migraciones) · **D-10** (backups, PITR, snapshots, RPO/RTO, *deletion protection*) · si se evalúa RDS Proxy | Decisiones fechadas, con alternativas, precios y fuentes |
| **Prepara** | Inventario de tráfico de la Lambda sobre el código vigente, con el candidato **sin NAT** · presupuesto preliminar de conexiones (**D-12**) · modelo de **costo bruto, créditos, desembolso, vencimiento y poscrédito** frente a **D-13** · contratos de módulos, *state* e identidades · planes de prueba y runbooks de `Task/030`–`Task/040` · diseño de **R-12**, **R-43** y **R-44** | Documentos y cálculos reproducibles, sin secretos |
| **Puede provisionar** | **Nada.** El primer `apply` de aplicación exige el backend de estado **D-06**, que crea `Task/030`, y **EX-028-C7 no se extiende** a recursos de aplicación | — |
| **Se valida después** | Red y RDS privados, restore sintético y PITR | `Task/031` |
| | Conexión real, secretos, tráfico sin NAT, pool y latencia medidos | `Task/032` |
| | Primeras migraciones por el canal privado, con backup previo | `Task/036` · `Task/038` |
| | Carga, casos negativos, restore reciente, DR y alertas | `Task/040` |
| | Costo real frente a la estimación | `Task/041` |

**Gate económico:** si el costo bruto no cabe en **D-13** (USD 5 AWS / USD 20 global), la
tarea **se detiene** y pide una decisión explícita al usuario. No se sube el presupuesto
ni se cuenta con los créditos como costo cero.

**Depende de:** `Task/027`, `Task/028` y del cierre de `Task/028.2`.
**Repositorio:** `personal-blog-infra`.

<details>
<summary>Historia — definición de Task/029 para el modelo VPS, vigente del 2026-08-15 hasta la propuesta de Task/028.2</summary>

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

</details>

## Criterios de salida de la etapa

- [x] MFA activo en la cuenta raíz de AWS y en Cloudflare — evidencia humana saneada de
      login con TOTP; Task/027 aprobada.
- [x] La cuenta raíz de AWS no se usa para operar; existe un usuario/rol administrativo —
      verificado en Gate C; Task/027 aprobada.
- [x] Presupuesto mensual definido con alertas por umbral — configuración y cuatro
      destinatarios verificados en Gate E; Task/027 aprobada.
- [x] **GitHub Actions** asume un rol AWS vía OIDC; no hay claves de acceso de larga vida
      **en GitHub** — federación real demostrada, cero access keys permanentes; Task/028
      aprobada. Esta afirmación se limita a GitHub Actions: **no** describe todavía
      cómo el VPS accederá a AWS (**D-16**). *(D-16 tiene cierre por no aplicabilidad
      propuesto por `Task/028.2`. La afirmación sigue sin acreditar permisos de despliegue
      ni conectividad SQL privada.)*
- [x] El rol de validación tiene **cero managed policies y cero inline policies**,
      trust exacta y GetCallerIdentity correcto, con evidencia real saneada — verificado
      contra IAM tras el apply y en la convergencia posterior; Task/028 aprobada.
- [x] Las operaciones negativas elegidas devuelven **AccessDenied**; no se deduce
      ausencia universal de permisos por resource-based policies de toda la cuenta —
      `AccessDenied` e `InvalidIdentityToken` exactos; Task/028 aprobada.
- [x] La trust final acepta exclusivamente main; el rechazo desde Task con token
      nuevo y la reconfirmación postmerge main quedan demostrados — trust main-only aplicada
      y verificada contra IAM, rechazo desde la rama Task con un JWT nuevo el 2026-09-25, y
      **reconfirmación postmerge el 2026-09-26**: `Verify AWS OIDC` **success** por
      `workflow_dispatch` sobre `main` en `e0fa95b`. Task/028 aprobada; evidencia registrada
      por `Task/028.1`.

Permisos de despliegue: fuera de este criterio, propietarios Task/038 y Task/039,
validación integral Task/040. Inspección de resource policies: limitada al inventario
efectivamente comprobado.

Criterios de `Task/029` **propuestos por `Task/028.2`**, pendientes de aprobación. Todos se
satisfacen con decisiones y documentos, **sin recursos AWS**:

- [ ] **D-22**, **D-23**, **D-24** y **D-10** decididas con precios y fuentes de la fecha
      de ejecución, sin valores arbitrarios.
- [ ] Inventario de tráfico de la Lambda repetido sobre el código vigente; candidato **sin
      NAT** viable o, si no lo es, necesidad real explicada y decisión explícita pedida.
- [ ] TLS con validación de CA y *hostname*, KMS, credenciales separadas y rotación
      definidos, **sin generar ni leer secretos**.
- [ ] Presupuesto preliminar de conexiones (**D-12**) y decisión sobre evaluar RDS Proxy,
      con la medición asignada a `Task/032` y `Task/040`.
- [ ] **Costo bruto** por escenarios, créditos, desembolso, vencimiento y escenario
      poscrédito frente a **D-13**; si no cabe, **decisión explícita** antes de cualquier
      `apply` de aplicación.
- [ ] Contratos de *state* (**D-06** en `Task/030`, **EX-028-C7 no extendida**), módulos e
      identidades separadas.
- [ ] Planes de restore, carga, seguridad y DR con owner y criterio medible posterior.
- [ ] Ninguna credencial de producción versionada.

<details>
<summary>Historia — criterios de Task/029 para el modelo VPS, vigentes hasta la propuesta de Task/028.2</summary>

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

</details>

## Fuera del alcance de la etapa

*(Enmienda propuesta por `Task/028.2`: **crear red, RDS, *endpoints*, claves KMS, secretos o
roles** es de `Task/031`/`Task/032`; **medir la latencia y los límites desde la Lambda
real**, de `Task/032`; **demostrar restore**, de `Task/031` y `Task/040`. Conectar la Lambda
a la VPC es parte de la propuesta; **introducir NAT Gateway** sigue excluido sin decisión
explícita. La disponibilidad Single-AZ o Multi-AZ la decide **D-22**. Las viñetas siguientes
son las del modelo VPS y se conservan como historia.)*


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

*(Enmienda propuesta por `Task/028.2`. Las filas de R-30, R-34, R-40, R-41 y R-42 describen
el host y pierden objeto literal. Su reformulación está en la
[reconciliación de riesgos de STATUS](../project-management/STATUS.md). Siguen vigentes:
**conexiones** (R-03/R-33, ahora con pool derivado y RDS Proxy evaluable), **backup no
restaurable** (R-31) y **costo** (R-02, con créditos que caducan).)*

## Siguiente etapa

[ETAPA 10 — Despliegue Cloud](STAGE-10-cloud-deployment.md)
