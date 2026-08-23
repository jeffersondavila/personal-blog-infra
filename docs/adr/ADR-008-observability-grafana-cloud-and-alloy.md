# ADR-008 — Observabilidad: CloudWatch mínimo y Grafana Cloud con Alloy

| Campo | Valor |
| --- | --- |
| **Estado** | **Aceptada** ✔ |
| **Fecha** | 2026-08-23 |
| **Fecha de aceptación** | 2026-08-23 |
| **Aceptada por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Tarea** | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` (mantenimiento; **no cuenta** en las 41 tareas) |
| **Reemplaza a** | — |
| **Reemplazada por** | — |
| **Modifica parcialmente** | [ADR-003](ADR-003-serverless-low-cost-cloud.md) — **solo la fila «Logs y métricas»**. El resto de ADR-003 sigue íntegro y vigente |
| **Complementa a** | [ADR-007](ADR-007-production-postgresql-on-vps.md) — cierra la herramienta del *baseline* de observabilidad del VPS que aquel documento dejó explícitamente sin decidir |
| **Documento canónico** | [target-production-architecture.md](../architecture/target-production-architecture.md) §10–§13 — **Vigente** |
| **Decisiones diferidas que abre** | **D-19** (plan y costo de Grafana Cloud, `Task/041`) · **D-20** (integración `CloudWatch → Grafana Cloud`, `Task/031`) |

> **Aceptada** el 2026-08-23, al aprobar el usuario `Task/006.2` con la expresión exacta
> requerida por [WORKFLOW.md](../project-management/WORKFLOW.md). Sus reglas son **vigentes
> y de cumplimiento obligatorio** desde esta fecha.
>
> **Aceptar esta decisión no autoriza a implementarla.** Contratar Grafana Cloud, instalar
> Alloy o crear recursos AWS sigue exigiendo su tarea propietaria y la autorización explícita
> del usuario.

---

## Contexto

Hasta ahora el proyecto tenía **una sola respuesta** a la observabilidad de producción:
**CloudWatch**, elegido en [ADR-003](ADR-003-serverless-low-cost-cloud.md) por ser el
servicio nativo de Lambda y por su costo cercano a cero con retención corta. Esa respuesta
era suficiente **mientras toda la producción vivía en AWS**.

[ADR-007](ADR-007-production-postgresql-on-vps.md) rompió ese supuesto. La capa de datos de
producción —el componente cuyo fallo deja el blog sin contenido— pasó a vivir en un **VPS
externo a AWS**. Y **CloudWatch no observa un host externo por defecto**.

El propio ADR-007 y su documento canónico registraron el hueco con precisión:

> «**`Task/029` define y configura el *baseline*** de observabilidad del VPS […] **No se
> decide aquí la herramienta.** En particular, **no se adopta CloudWatch Agent por
> omisión**.»
> — [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) §15.3.1

Quedaban por tanto tres problemas abiertos y sin herramienta:

1. **Qué observa el VPS**, y con qué agente.
2. **Dónde se miran juntas** las dos mitades de producción —AWS y VPS— sin abrir dos
   consolas y correlacionar a mano.
3. **Qué pasa con CloudWatch**: si sigue, si se sustituye, y con qué alcance.

El perfil del proyecto no cambia: un blog personal, un operador, tráfico bajo y el **costo
como restricción principal de diseño**. Cualquier respuesta que implique un costo fijo
apreciable, o que consuma los recursos del VPS reservados a PostgreSQL, está descartada de
partida.

## Decisión

> **La observabilidad de producción tiene dos planos: CloudWatch en modo mínimo dentro de
> AWS, y Grafana Cloud como plano central de visualización, consulta y alertas, alimentado
> desde el VPS por Grafana Alloy.**

Cuatro puntos, que forman la decisión completa:

### 1. CloudWatch se mantiene, en modo mínimo

**No desaparece.** Sigue siendo la observabilidad **nativa** de AWS: logs y métricas de
Lambda y API Gateway, errores y diagnóstico operativo de primera línea.

«Mínimo» significa: **retención corta y explícita** —nunca infinita—, alarmas
**imprescindibles**, sin *dashboards* elaborados, sin funcionalidades avanzadas no
justificadas y **sin duplicar** dentro de CloudWatch lo que se verá en Grafana Cloud. La
retención exacta sigue siendo **D-11**, en `Task/031`.

### 2. Grafana Cloud es el plano central

Es donde se **mira**, se **consulta** y se **alerta**. Recibe la telemetría del VPS y, en
el futuro, lo que llegue desde CloudWatch (punto 4).

**El tier gratuito es una preferencia presupuestaria, no una dependencia arquitectónica
rígida.** Si deja de ser suficiente o cambia de condiciones, se decide pagar, reducir el
volumen de telemetría o cambiar de destino: **la arquitectura no se rompe**. Por eso **no
se persiste aquí ningún límite, cuota ni precio**: son datos comerciales de terceros con
fecha de caducidad, y `Task/041` los verifica con precios vigentes.

### 3. Grafana Alloy es el agente del VPS

Alloy recolecta **logs, métricas y telemetría** del host y de sus servicios y los envía a
Grafana Cloud. Cubre el *baseline* que `Task/029` ya tenía asignado: `uptime`, CPU, RAM,
**espacio en disco** (**R-32**), estado de **PostgreSQL**, estado de **PgBouncer**, **fallo
del backup** y **caducidad del certificado** de PgBouncer.

> **No se autohospedan Grafana, Prometheus ni Loki en el VPS** como *stack* completo.

Dos razones, y ambas son suficientes por separado: la RAM, la CPU y el disco del VPS se
reservan **principalmente para PostgreSQL**; y un plano de observabilidad alojado en la
misma máquina que vigila **se cae exactamente cuando más falta hace**.

### 4. La integración `CloudWatch → Grafana Cloud` se contempla, no se implementa

La arquitectura prevé que Grafana Cloud consulte o reciba lo que hay en CloudWatch mediante
**el mecanismo seguro/IAM que corresponda**. **Qué mecanismo** es **D-20**, abierta, con
propietario **`Task/031`** y validación en `Task/040`. **Nada de esto se implementa ahora.**

## Qué NO decide este ADR

- **No decide el plan comercial de Grafana Cloud**, ni sus límites, ni su costo: **D-19**,
  `Task/041`.
- **No decide el mecanismo de integración con CloudWatch**: **D-20**, `Task/031`.
- **No decide la retención de CloudWatch**: **D-11**, `Task/031`, sin cambios.
- **No decide la observabilidad de la aplicación.** Logs JSON, correlation ID y redacción
  siguen siendo de `Task/017` (local) y `Task/018` (endurecimiento). Lo que sí fija es que
  esa telemetría debe ser **portable**: el dominio no se acopla a CloudWatch, Grafana, Loki
  ni Prometheus; los destinos los absorbe la infraestructura.
- **No decide la herramienta de secretos del VPS** —**D-17**— ni la de configuración del
  sistema operativo —**D-18**—, aunque Alloy dependa de ambas para instalarse y autenticarse.
- **No autoriza contratar, registrar ni configurar nada.**

## Alternativas consideradas

| Alternativa | Por qué se descartó |
| --- | --- |
| **Solo CloudWatch, con CloudWatch Agent en el VPS** | Instalar un agente de AWS en un host externo tiene costo de ingesta, superficie de ataque y **credenciales AWS permanentes en el VPS** — el mismo problema que **D-16** aún no resuelve. Además, CloudWatch es un mal plano de consulta unificado para métricas de host. |
| **Stack autohospedado en el VPS** (Grafana + Prometheus + Loki) | Compite por RAM, CPU y disco con PostgreSQL, que es justo lo que no puede degradarse (**R-32**). Y **se cae con el host que debía vigilar**: la telemetría del incidente desaparece con el incidente. |
| **Solo Grafana Cloud, eliminando CloudWatch** | Perder la observabilidad **nativa** de Lambda y API Gateway a cambio de nada: los logs de Lambda nacen en CloudWatch de todos modos, y desactivarlos deja el diagnóstico de AWS sin primera línea. |
| **Otro SaaS de observabilidad** | Ninguno aporta una ventaja demostrada aquí, y Alloy es el agente natural del destino elegido. La decisión es reversible: la telemetría es portable por diseño. |
| **Sin observabilidad del VPS hasta el lanzamiento** | Inaceptable. Un disco lleno detiene PostgreSQL y **puede impedir el propio backup** (**R-32**); un certificado caducado deja el blog sin base de datos. Son fallos silenciosos hasta que son catastróficos. |

## Consecuencias

### Positivas

- **Se cierra un hueco real:** el componente de mayor impacto del proyecto —el VPS— deja de
  estar sin observabilidad asignada.
- **Un solo lugar donde mirar** las dos mitades de producción, sin correlacionar a mano
  entre dos consolas.
- **CloudWatch deja de crecer** como respuesta por defecto: se acota a lo nativo y barato.
- **Los recursos del VPS siguen siendo de PostgreSQL.** Un agente pesa mucho menos que un
  *stack*.
- **Alertas reales** sobre disco, certificado y fallo de backup, que son los tres fallos
  silenciosos más caros de esta arquitectura.

### Negativas

- **Un proveedor más.** Ya eran dos —AWS y Cloudflare— más el VPS; ahora hay una cuarta
  superficie de configuración y facturación.
  *Mitigación:* alcance acotado a observabilidad; sustituible sin tocar la aplicación.
- **Dependencia de un tier gratuito de terceros** (**R-38**), cuyos límites pueden cambiar.
  *Mitigación:* declarado explícitamente como preferencia presupuestaria, no como
  dependencia; verificación en `Task/041`.
- **La telemetría sale del proyecto hacia un tercero** (**R-39**). Logs de host y de
  PostgreSQL pueden contener datos que no deberían salir.
  *Mitigación:* la regla **O-08** se aplica también aquí; **qué se recolecta es parte del
  diseño**, no un detalle de configuración.
- **Una credencial más en el VPS**, la de Alloy hacia Grafana Cloud (**R-40**).
  *Mitigación:* entra en el mecanismo de secretos cifrados del VPS (**D-17**), con permisos
  mínimos y rotación definida en `Task/029`.
- **Alloy consume recursos del VPS** (**R-41**), por pocos que sean.
  *Mitigación:* agente, no *stack*; el dimensionamiento de `Task/029` lo contempla.
- **Observabilidad repartida en dos planos** mientras **D-20** siga abierta: hasta que exista
  la integración, AWS se mira en CloudWatch y el VPS en Grafana Cloud.
  *Mitigación:* es un estado transitorio con propietario asignado (`Task/031`).

### Neutras

- **La aplicación no cambia.** Sigue emitiendo logs JSON con correlation ID por `stdout`;
  quién los recoge es una decisión de infraestructura.
- **El entorno local no cambia.** Docker, Portainer y `Task/017` siguen igual: **Alloy y
  Grafana Cloud son exclusivamente de producción**.
- **El laboratorio AWS local no cambia.** Floci no emula Grafana Cloud y no debe intentarlo.

## Costo

No se registra ninguna cifra, por decisión: los precios y los límites de los planes
gratuitos **cambian**, y persistirlos aquí crearía una afirmación condenada a envejecer mal.

| Componente | Intención | Quién lo verifica |
| --- | --- | --- |
| **CloudWatch** | Costo mínimo por retención corta y alarmas imprescindibles | `Task/031` (**D-11**), `Task/041` |
| **Grafana Cloud** | Tier gratuito **si sigue siendo suficiente** | `Task/041` (**D-19**), con aporte de `Task/027` |
| **Grafana Alloy** | Software libre; su costo es el consumo de recursos del VPS | `Task/029` |
| **Transferencia de telemetría desde el VPS** | Marginal frente al tráfico incluido del VPS — **supuesto, no verificado** | `Task/041` |

**Regla vigente:** `Task/041` usa **precios reales del momento**, nunca cifras heredadas de
este ADR.

## Seguridad

| Regla |
| --- |
| **La telemetría que sale hacia Grafana Cloud no contiene contraseñas, tokens, cadenas de conexión ni datos personales innecesarios** (**O-08**, **O-09**) |
| **La credencial de Alloy hacia Grafana Cloud es un secreto del VPS**: cifrada, con la clave fuera del repositorio, con permisos mínimos y rotación definida (**D-17**) |
| **Grafana Cloud no recibe acceso a AWS** hasta que **D-20** decida el mecanismo, que será de **solo lectura** y de **permiso mínimo** |
| **Ninguna credencial de larga vida versionada**, en ningún repositorio |
| **El compromiso de Grafana Cloud no debe implicar el compromiso de AWS ni del VPS**: mismo criterio que se exige a **D-16** |
| **Alloy no abre puertos de entrada en el VPS.** Su tráfico es saliente; el firewall sigue *deny-by-default* |

Componentes formalizados en [security-boundaries.md](../architecture/security-boundaries.md):
**C-16** (Grafana Alloy en el VPS) y **C-17** (Grafana Cloud, destino externo), con sus
reglas en §10.

## Operación

- **`Task/029`** instala y configura Alloy en el VPS, y deja cubierto el *baseline*.
- **`Task/031`** mantiene CloudWatch en modo mínimo y prepara la base de la integración
  (**D-20**).
- **`Task/040`** verifica que la observabilidad **opera de verdad** —no que está
  configurada—, incluidas las alertas de disco, certificado y fallo de backup.
- **`Task/041`** revisa costo y vigencia de los tiers.
- **`Task/026`** documenta en runbooks qué se mira, dónde y qué hacer ante cada alerta.

## Cumplimiento

- Ninguna tarea puede **autohospedar Grafana, Prometheus o Loki en el VPS** sin un ADR que
  reemplace a este.
- Ninguna tarea puede **eliminar CloudWatch** ni ampliarlo más allá de «mínimo» sin un ADR
  que reemplace a este.
- Ninguna tarea puede **acoplar el dominio de la aplicación** a un destino concreto de
  telemetría.
- **Ninguna cifra comercial** de Grafana Cloud se documenta como permanente; si se
  documenta, se marca *«verificar en `Task/041` / antes de contratar»*.
- **Nada de esto se implementa** antes de la tarea propietaria, y ninguna cuenta se contrata
  sin autorización explícita del usuario.

## Referencias

- [Arquitectura objetivo de producción](../architecture/target-production-architecture.md) §10–§13
- [ADR-003 — Nube serverless de bajo costo](ADR-003-serverless-low-cost-cloud.md)
- [ADR-007 — PostgreSQL de producción en VPS externo](ADR-007-production-postgresql-on-vps.md)
- [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) §15.3.1
- [security-boundaries.md](../architecture/security-boundaries.md) §10
- [open-decisions.md](../architecture/open-decisions.md) — **D-17**, **D-18**, **D-19**, **D-20**
- [non-functional-requirements.md](../architecture/non-functional-requirements.md) §5
