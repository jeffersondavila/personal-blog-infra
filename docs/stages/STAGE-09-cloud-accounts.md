# ETAPA 09 — Cuentas y Seguridad Cloud

| Campo | Valor |
| --- | --- |
| **Número** | 09 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 08](STAGE-08-cloud-ready.md) |
| **Tareas** | 3 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
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

### `Task/027-Configurar-Cuentas-y-Presupuestos` — *Pendiente*

Cuentas AWS y Cloudflare, MFA en todos los accesos, presupuestos y alertas de costo.

**Depende de:** `Task/026`. **Repositorio:** `personal-blog-infra` (documentación).

### `Task/028-GitHub-OIDC-AWS` — *Pendiente*

Confianza OIDC entre GitHub Actions y AWS con roles temporales, **sin credenciales AWS
permanentes** almacenadas en GitHub.

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

- [ ] MFA activo en la cuenta raíz de AWS y en Cloudflare.
- [ ] La cuenta raíz de AWS no se usa para operar; existe un usuario/rol administrativo.
- [ ] Presupuesto mensual definido con alertas por umbral.
- [ ] **GitHub Actions** asume un rol AWS vía OIDC; no hay claves de acceso de larga vida
      **en GitHub**. Esta afirmación se limita a GitHub Actions: **no** describe todavía
      cómo el VPS accederá a AWS (**D-16**).
- [ ] El rol tiene permisos mínimos para el despliegue previsto.
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
