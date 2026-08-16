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
controlada, sin credenciales permanentes y sin destrucción automática de recursos.

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

**Depende de:** `Task/036`. **Repositorio:** `personal-blog-backend`.

### `Task/039-Automatizar-Terraform` — *Pendiente*

`terraform plan` revisable en cada PR, `apply` protegido por aprobación manual y
**sin destrucción automática**.

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
- [ ] Ningún workflow usa credenciales cloud permanentes.
- [ ] El `plan` de Terraform es visible y revisable antes del `apply`.
- [ ] El `apply` requiere aprobación manual.
- [ ] Ningún workflow puede ejecutar `terraform destroy`.
- [ ] Existe un procedimiento de rollback probado para frontend y backend.

## Fuera del alcance de la etapa

- Validación final de producción (Etapa 12).
- Protección de costos permanente (Etapa 12).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Un despliegue automático rompe producción. | Rollback probado y despliegue solo desde ramas aprobadas. |
| Destrucción accidental de recursos vía CI. | `destroy` prohibido en los workflows; `apply` con aprobación manual. |
| Divergencia entre el estado de Terraform y lo desplegado. | `plan` en cada PR; deriva tratada como defecto. |
| Secretos expuestos en logs de CI. | Uso de secretos enmascarados y revisión de salidas. |

## Siguiente etapa

[ETAPA 12 — Lanzamiento y Operación](STAGE-12-launch-and-operations.md)
