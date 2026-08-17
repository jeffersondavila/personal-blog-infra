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

GitHub Actions hacia AWS Lambda usando OIDC.

**Además — canal de migraciones en producción** (*ownership* asignado en `Task/005.5`).
`Task/036` ejecuta la **primera** migración a mano; el canal **repetible** es de esta
tarea, y debe dejar definido:

- quién ejecuta `alembic upgrade` y **desde qué entorno**;
- con **qué credencial**, y por qué no es una credencial de larga vida versionada;
- el **orden respecto al despliegue** de la Lambda;
- qué ocurre **si la migración falla** a mitad, y cómo se revierte;
- qué **impide una ejecución accidental** contra producción.

**Depende de:** `Task/036`. **Repositorio:** `personal-blog-backend`.

### `Task/039-Automatizar-Terraform` — *Pendiente*

`terraform plan` revisable en cada PR, `apply` protegido por aprobación manual y
**sin destrucción automática**.

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

> **No se afirma «sin credenciales permanentes» como absoluto global** mientras el diseño
> no haya demostrado cómo Cloudflare y el VPS se autentican sin ellas. La afirmación
> vigente y verificada se limita a **GitHub Actions → AWS**.

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

## Siguiente etapa

[ETAPA 12 — Lanzamiento y Operación](STAGE-12-launch-and-operations.md)
