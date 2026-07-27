# ETAPA 09 — Cuentas y Seguridad Cloud

| Campo | Valor |
| --- | --- |
| **Número** | 09 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 08](STAGE-08-cloud-ready.md) |
| **Tareas** | 3 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | Cuentas cloud seguras, con presupuesto y acceso sin credenciales permanentes. |

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

### `Task/029-Seleccionar-PostgreSQL-Administrado` — *Pendiente*

Evaluación de opciones por costo, TLS, backups, pooling de conexiones y compatibilidad
con Lambda. Resultado registrado como ADR.

**Depende de:** `Task/027`.

## Criterios de salida de la etapa

- [ ] MFA activo en la cuenta raíz de AWS y en Cloudflare.
- [ ] La cuenta raíz de AWS no se usa para operar; existe un usuario/rol administrativo.
- [ ] Presupuesto mensual definido con alertas por umbral.
- [ ] GitHub Actions asume un rol AWS vía OIDC; no hay claves de acceso de larga vida.
- [ ] El rol tiene permisos mínimos para el despliegue previsto.
- [ ] Proveedor de PostgreSQL seleccionado, con costo y límites documentados en un ADR.
- [ ] La estrategia de conexión desde Lambda está definida.

## Fuera del alcance de la etapa

- Desplegar recursos de aplicación (Etapa 10).
- Automatizar despliegues (Etapa 11).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Costo inesperado desde el primer día. | Presupuesto y alarmas creados antes que cualquier recurso. |
| Credenciales de larga vida filtradas. | OIDC con roles temporales; ninguna clave estática. |
| Rol OIDC con permisos excesivos. | Permisos mínimos, acotados por repositorio y rama. |
| Agotamiento de conexiones de PostgreSQL desde Lambda. | Pooling o proxy de conexiones evaluado en `Task/029`. |

## Siguiente etapa

[ETAPA 10 — Despliegue Cloud](STAGE-10-cloud-deployment.md)
