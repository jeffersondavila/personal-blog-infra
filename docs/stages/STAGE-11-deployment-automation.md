# ETAPA 11 — Automatización de Despliegues

| Campo | Valor |
| --- | --- |
| **Número** | 11 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 10](STAGE-10-cloud-deployment.md) |
| **Tareas** | 3 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | Entrega continua operativa, sin acciones destructivas automáticas. |

---

## Objetivo

Que cada cambio aprobado llegue a la nube de forma automática, reproducible y
controlada, **sin credenciales permanentes en el canal GitHub Actions → AWS** (OIDC,
`Task/028`) y sin destrucción automática de recursos.

> *(Acotado en `Task/005.7`: aquí se leía «sin credenciales permanentes» sin sujeto, lo
> que contradecía la aclaración de la propia etapa más abajo. El mecanismo de Cloudflare
> y del proveedor del VPS es de `Task/039` y **D-16 sigue abierta**: pueden no admitir
> OIDC.)*

## Por qué esta etapa existe

El despliegue manual es la principal fuente de errores de operación y de deriva entre lo
que dice el código y lo que hay desplegado. Se automatiza **después** de que el
despliegue manual está probado.

## Tareas

### `Task/037-Deploy-Automatico-Frontend` — *Pendiente*

GitHub Actions hacia Cloudflare Pages.

**Depende de:** `Task/036`. **Repositorio:** `personal-blog-frontend`.

### `Task/038-Deploy-Automatico-Backend` — *Pendiente*

GitHub Actions hacia AWS Lambda usando OIDC. **Task/038 es propietaria de los
permisos mínimos de despliegue backend**, acotados a operaciones y recursos reales.
No reutilizar ni ampliar el rol de validación Task/028. Protección efectiva de main
obligatoria antes de habilitar este rol; Task/040 valida integralmente.

**Además — canal de migraciones en producción** (*ownership* asignado en `Task/005.5`).
`Task/036` ejecuta la **primera** migración a mano; el canal **repetible** es de esta
tarea, y debe dejar definido:

- quién ejecuta `alembic upgrade` y **desde qué entorno**;
- con **qué credencial**, y por qué no es una credencial de larga vida versionada;
- el **orden respecto al despliegue** de la Lambda;
- qué ocurre **si la migración falla** a mitad, y cómo se revierte;
- qué **impide una ejecución accidental** contra producción.

> **Enmienda de `Task/028.2`, aprobada el 2026-09-27.** Con RDS
> privado, un *runner* público de GitHub **no alcanza la base de datos** solo por tener
> identidad OIDC: **OIDC acredita identidad, no conectividad SQL**. El canal repetible se
> construye sobre el **canal privado D-24** que decide `Task/029`, habilita `Task/031` y
> estrena `Task/036`. Añade al checklist anterior: **ejecuciones serializadas**,
> **identidad SQL de migración** distinta de la de la aplicación, **backup previo** y
> **nunca** migraciones como efecto lateral del arranque de la Lambda.

**Depende de:** `Task/036`. **Repositorio:** `personal-blog-backend`.

### `Task/039-Automatizar-Terraform` — *Pendiente*

`terraform plan` revisable en cada PR, `apply` protegido por aprobación manual y
**sin destrucción automática**. **Task/039 es propietaria de los permisos mínimos
Terraform**, incluidos backend/lock según D-06 y recursos gestionados. Rol separado
del validador Task/028; protección efectiva de main antes de habilitarlo.
Task/040 valida la cadena completa.

#### Automatización multi-provider

Desde [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md), Terraform es
conceptualmente **multi-provider**: AWS, Cloudflare y el proveedor del VPS. **`Task/028`
solo resuelve GitHub OIDC → AWS.** Esta tarea es propietaria de lo demás:

| Materia | Alcance |
| --- | --- |
| **Credenciales** | Mecanismo por proveedor. Cloudflare y el VPS **pueden no admitir OIDC**; si exigen un token, se documenta por qué y cómo se acota |
| **Rotación y *scopes*** | Caducidad, permisos mínimos y procedimiento de rotación escrito |
| **Entornos protegidos** | Aprobación manual obligatoria antes de cualquier `apply` real |
| **Guardas de destino** | Extensión *fail-closed* de `Task/025`: cuenta AWS esperada, **proyecto Cloudflare esperado** y **proyecto/región del VPS esperados**. Sin coincidencia, no se ejecuta |

> **Terraform no configura el sistema operativo del VPS** (precisado en `Task/006.2`,
> **aprobada** el 2026-08-23). Puede **crear** el VPS si el proveedor elegido en `Task/029` tiene un
> provider mantenido, pero **no sustituye a Ansible, cloud-init ni a los scripts
> idempotentes** en usuarios, firewall, TLS, PostgreSQL, PgBouncer, Grafana Alloy, secretos
> ni backups. El mecanismo es **D-18**, y es de `Task/029`. Riesgo asociado: **R-42**.

> **No se afirma «sin credenciales permanentes» como absoluto global** mientras el diseño
> no haya demostrado cómo Cloudflare y el VPS se autentican sin ellas. La afirmación
> vigente y verificada se limita a **GitHub Actions → AWS**.

> **Enmienda de `Task/028.2`, aprobada el 2026-09-27.** Sin VPS,
> los providers son **dos**: **AWS y Cloudflare**. Pierden objeto la fila de credenciales
> y la guarda del proveedor del VPS, y la nota sobre su sistema operativo (**D-18**, con
> cierre por no aplicabilidad (2026-09-27)). Se añade: **red y RDS** entran en los
> inventarios, en las guardas de cuenta, región y entorno, y en la **protección contra
> borrado** —*deletion protection*, snapshot final, ningún `destroy` real automático—. La
> afirmación «sin credenciales permanentes» sigue limitada a GitHub Actions → AWS mientras
> Cloudflare no demuestre otro mecanismo.

**Depende de:** `Task/037`, `Task/038`. **Repositorio:** `personal-blog-infra`.

#### Dónde encaja la validación local en CI

Intención futura registrada en `Task/005.2`. **No modifica** las responsabilidades ya
asignadas a `Task/020-CI-Backend`, `Task/021-CI-Infraestructura`, `Task/037` ni `Task/038`:
solo aclara qué aporta el laboratorio de paridad dentro de esta tarea.

Sobre un **emulador efímero levantado por el propio job**, un pull request de
infraestructura puede ejecutar el ciclo completo sin credenciales cloud:

```
Pull Request
   └─► GitHub Actions
         └─► emulador AWS efímero
               ├─ terraform validate
               ├─ terraform plan   (local)
               ├─ terraform apply  (local)
               ├─ pruebas de infraestructura
               └─ terraform destroy (local)
```

Y, por separado, el camino hacia AWS real, que **no cambia**:

```
GitHub Actions ─► OIDC ─► AWS real ─► plan revisable ─► apply protegido
```

Reglas que se mantienen intactas:

- El `destroy` automático **solo** es admisible contra el emulador efímero del job, que se
  destruye entero al terminar.
- **Ningún workflow ejecuta `terraform destroy` contra AWS real.** Sin excepciones.
- El `apply` contra AWS real sigue exigiendo **aprobación manual**.
- Ningún workflow usa credenciales cloud permanentes; el job local no usa credencial real
  alguna.

Estrategia completa: [aws-local-parity.md](../architecture/aws-local-parity.md) §11.3.

## Criterios de salida de la etapa

- [ ] Un cambio aprobado en el frontend llega a Cloudflare Pages sin intervención manual.
- [ ] Un cambio aprobado en el backend actualiza la Lambda mediante OIDC.
- [ ] **El acceso a AWS no usa credenciales permanentes.** Para **Cloudflare y el VPS**, el
      mecanismo está documentado, acotado y con rotación definida — o se justifica
      explícitamente por qué no puede evitarse un token de larga vida.
- [ ] El `plan` de Terraform es visible y revisable antes del `apply`.
- [ ] El `apply` requiere aprobación manual **y verifica el destino esperado de cada
      provider** antes de ejecutarse.
- [ ] **Ningún workflow puede ejecutar `terraform destroy` contra AWS real, Cloudflare o el
      VPS.** Sin excepciones. El `destroy` **sí** es admisible —y necesario— contra el
      emulador AWS **efímero** levantado por el propio job, que se destruye entero al
      terminar y no contiene ningún recurso real. La distinción es la del punto anterior de
      esta misma etapa; ver también
      [aws-local-parity.md](../architecture/aws-local-parity.md) §11.3.
      *(Precisado en `Task/005.6`: este criterio decía «Ningún workflow puede ejecutar
      `terraform destroy`» en absoluto, contradiciendo el bloque de reglas de esta misma
      etapa.)*
- [ ] Existe un procedimiento de rollback probado para frontend y backend.
- [ ] El **canal de migraciones en producción** está definido, con credencial acotada,
      orden respecto al despliegue, comportamiento ante fallo y protección contra
      ejecución accidental.

*(Enmienda de `Task/028.2`: en los criterios anteriores, «el VPS» deja de ser un
provider; quedan **AWS y Cloudflare**. Se añaden desde la aprobación del 2026-09-27:)*

- [ ] El canal de migraciones usa el **canal privado D-24**, serializa las ejecuciones, usa
      una identidad SQL de migración distinta de la de la aplicación y exige backup previo.
- [ ] Red y RDS están en los inventarios y en las guardas de destino; ningún workflow puede
      borrar RDS, sus snapshots ni su clave KMS.
- [ ] Los roles de despliegue backend y de Terraform son **distintos** entre sí y del rol de
      validación de `Task/028`, que sigue sin políticas.

## Fuera del alcance de la etapa

- Validación final de producción (Etapa 12).
- Protección de costos permanente (Etapa 12).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Un despliegue automático rompe producción. | Rollback probado y despliegue solo desde ramas aprobadas. |
| Destrucción accidental de recursos vía CI. | `destroy` **prohibido contra cualquier destino real** (AWS, Cloudflare, VPS); permitido solo contra el emulador efímero del job. `apply` real con aprobación manual y verificación previa del destino. |
| Divergencia entre el estado de Terraform y lo desplegado. | `plan` en cada PR; deriva tratada como defecto. |
| Secretos expuestos en logs de CI. | Uso de secretos enmascarados y revisión de salidas. |
| *(`Task/028.2`)* **Migración contra RDS lanzada por accidente o dos a la vez** (**R-35**). | Canal privado **D-24**, ejecuciones serializadas, entorno protegido y backup previo. |
| *(`Task/028.2`)* **Plan o *state* con credenciales de la base de datos** publicados en CI. | Custodia del *state* definida antes del `apply` y salidas revisadas; `sensitive` no elimina el valor del *state*. |

## Siguiente etapa

[ETAPA 12 — Lanzamiento y Operación](STAGE-12-launch-and-operations.md)
