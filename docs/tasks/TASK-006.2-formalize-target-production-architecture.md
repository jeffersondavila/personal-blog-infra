# TASK-006.2 — Formalizar la arquitectura objetivo de producción

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Nombre** | Formalizar la arquitectura objetivo de producción |
| **Tipo** | **Mantenimiento transversal de arquitectura y planificación** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**6 de 41**) ni la ETAPA 02 (**2 de 3**) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/006.1-Corregir-Drift-Documental-Post-Merge` — **Aprobada** ✔ (2026-08-21) · hotfix manual `d08fe27` del usuario, ya normalizado `main → dev` |
| **Rama** | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | `d08fe27711866eabe091a2d139387e2022c95b70` |
| **Fecha de inicio** | 2026-08-23 |
| **Fecha de aprobación** | 2026-08-23 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Última actualización** | 2026-08-23 — cierre aprobado |
| **Próxima tarea** | `Task/007-Integracion-Local` — **Pendiente, no iniciada** |

---

## 0. Preparación Git

Verificado **antes** de crear la rama, sobre `personal-blog-infra`:

| Comprobación | Resultado |
| --- | --- |
| `main == origin/main` | `d08fe277…` en ambos |
| `dev == origin/dev` | `dbc13fc3…` en ambos |
| `d08fe27` ancestro de `main` | Sí (exit 0) |
| `d08fe27` ancestro de `dev` | Sí (exit 0) |
| `main` ancestro de `dev` | Sí (exit 0) |
| `git rev-list --count dev..main` | `0` |
| `git diff main dev` | **Vacío** |
| Working tree y staging | Limpios |
| Ramas Task locales / remotas | **0 / 0** |

Tras crearla: `git rev-parse HEAD` == `git rev-parse main` == `d08fe277…`, y
`git rev-list --count main..HEAD` == `0`.

> **La normalización `main → dev` del hotfix la ejecutó el usuario**, antes de esta tarea.
> Aquí solo se **verificó**. **Esta tarea no produjo ningún merge ni ningún push.**

## 1. Objetivo

Que la **imagen**, la **documentación arquitectónica**, el **roadmap**, las **tareas
futuras**, las **decisiones** y los **riesgos** describan **la misma arquitectura**.

El usuario actualizó manualmente `images/Infraestructura.png` y la publicó en `main`. La
PNG es una **vista humana**: no sirve para que un agente razone sobre ella. Faltaba su
**contraparte textual**, y varios documentos seguían describiendo la imagen como un
registro histórico desactualizado — afirmación que dejó de ser cierta con el commit
`d08fe27`.

## 2. Contexto

Tres decisiones de producción quedaban sin formalizar en la documentación canónica:

1. **La observabilidad.** [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) movió la
   capa de datos a un VPS externo, y **CloudWatch no observa un host externo**.
   [`production-postgresql-vps.md`](../architecture/production-postgresql-vps.md) §15.3.1
   registraba el hueco de forma explícita: *«No se decide aquí la herramienta»*.
2. **Los secretos del VPS.** SSM sirve a la Lambda; el host necesita los suyos **antes** de
   que exista ninguna invocación. Nadie era propietario del modelo.
3. **El papel de Docker.** La imagen de producción no muestra Docker, y esa ausencia se
   malinterpreta con facilidad como *«Docker no se usa»*.

## 3. Dentro del alcance

- [x] Documento canónico **textual** de la arquitectura objetivo de producción, con las 25
      materias exigidas, en 26 secciones.
- [x] **ADR-008** — observabilidad: CloudWatch mínimo, Grafana Cloud y Alloy. **Aceptada** ✔
      el 2026-08-23.
- [x] Corrección de las notas obsoletas sobre la PNG en `overview.md` y `README.md`.
- [x] Alineación de `local-to-cloud-mapping.md`: observabilidad, secretos del host y papel
      de Docker.
- [x] `security-boundaries.md`: componentes **C-16** y **C-17**, comunicaciones permitidas y
      prohibidas, y **§10** con once reglas.
- [x] `production-postgresql-vps.md`: **§11.1.1** (secretos del host) y **§15.3.1**
      (herramienta de observabilidad ya decidida).
- [x] `non-functional-requirements.md`: **O-09** y **O-10**; **O-06** precisado; totales
      actualizados a **59**.
- [x] `open-decisions.md`: **D-17** a **D-20**, con propietario, información necesaria y
      motivo del diferimiento.
- [x] `ROADMAP.md`: alcance conceptual de `Task/007`, `017`, `029`–`035`, `039`, `040` y
      `041`; mapa de responsabilidades transversales ampliado. **Sin renumerar.**
- [x] `STATUS.md`: mantenimiento en curso, riesgos **R-38** a **R-42**, conteos y notas.
- [x] Fichas de las **ETAPAS 02, 05, 09, 10 y 12**.
- [x] Ficha y reporte de la tarea.
- [x] Auditoría de consistencia terminológica.

## 4. Fuera del alcance

- **Modificar `images/Infraestructura.png`.** No se regenera, edita, comprime ni convierte.
- **Implementar cualquier cosa**: AWS, Cloudflare, Grafana Cloud, VPS, S3, SSM, IAM, Lambda,
  API Gateway, Terraform, Ansible, SOPS, age, Alloy, CI/CD.
- **Iniciar `Task/007`** o cualquier tarea de las ETAPAS 08–12.
- **Tocar `personal-blog-frontend` o `personal-blog-backend`.** Se leyó su estado Git; no se
  modificó nada y no se creó ninguna rama en ellos.
- **Crear tareas oficiales nuevas o renumerar las 41.**
- **Resolver D-17, D-18, D-19 o D-20.** Se abren con propietario; no se deciden.
- **Aprobar por decisión propia.** La aprobación la dio el usuario el 2026-08-23; ADR-008
  quedó **Aceptada** solo entonces.

## 5. Decisiones técnicas

### 5.1 Por qué un ADR nuevo y no una modificación de los existentes

`ADR-003` fijó CloudWatch como respuesta de observabilidad **cuando toda la producción vivía
en AWS**. `ADR-007` rompió ese supuesto pero **no resolvió la consecuencia**: lo dejó
escrito como pendiente. Añadir un plano de observabilidad **con un cuarto proveedor** es una
decisión estructural con costo, seguridad y operación propios — exactamente lo que la
convención del proyecto exige registrar como ADR.

**No se reescribe `ADR-003`.** Se le añade una nota de vigencia y se marca **una sola fila**
—«Logs y métricas»— como modificada, igual que hizo `ADR-007` con «Base de datos». La
decisión original **no desaparece**.

### 5.2 Por qué D-17 y D-18 se abren en lugar de cerrarse

Se cierra el **modelo** —secretos cifrados con clave fuera del repositorio; configuración
del SO separada de Terraform— y se deja abierta **la herramienta**. **SOPS + age** y
**Ansible** son los candidatos probables, pero elegirlos **sin el host provisionado, sin
conocer su distribución y sin saber cuántas veces se reconstruirá** sería inventar la
decisión y convertir una preferencia en un compromiso.

### 5.3 Por qué no se persiste ninguna cifra de Grafana Cloud

Los límites de un tier gratuito **cambian**. Documentarlos como permanentes crearía una
afirmación condenada a envejecer mal — el mismo defecto estructural que
[WORKFLOW §6.1](../project-management/WORKFLOW.md) corrigió para el estado de Git. Por eso
**D-19** existe y `Task/041` verifica **precios del momento**.

### 5.4 Agente en lugar de *stack* autohospedado

Un plano de observabilidad alojado en la máquina que vigila tiene dos fallos, y cada uno
basta: **compite por los recursos de PostgreSQL** (**R-32**, **R-41**) y **desaparece con el
incidente**. Un agente que empuja hacia fuera no tiene ninguno.

## 6. Riesgos

| # | Riesgo | Estado |
| --- | --- | --- |
| R-38 | Dependencia de un tier gratuito de terceros (Grafana Cloud) | **Abierto** |
| R-39 | La telemetría sale del perímetro y puede llevar secretos o PII | **Abierto** |
| R-40 | Secretos del VPS mal gestionados mientras **D-17** siga abierta | **Abierto** |
| R-41 | El agente compite por los recursos de PostgreSQL | **Abierto** |
| R-42 | *Drift* de configuración del VPS, que Terraform no ve | **Abierto** |

Riesgos ya existentes cuya cobertura se **confirmó sin duplicar**: **R-29** (SPOF),
**R-30** (exposición de PgBouncer), **R-31** (backups y restore), **R-32** (disco y
recursos), **R-33** (agotamiento de conexiones), **R-35** (error humano), **R-36**
(redacción de secretos en el log de aplicación), **R-02** (costo cloud imprevisto).

## 7. Deuda técnica pendiente

- **D-17**, **D-18**, **D-19** y **D-20** quedan abiertas, con propietario. Es deliberado.
- La integración `CloudWatch → Grafana Cloud` está **contemplada y no implementada**.
- Ninguna cuenta de Grafana Cloud existe, y **no debe crearse** antes de `Task/027`.

## 8. Validaciones

Tarea **exclusivamente documental**. El **criterio 3** (compilación) y el **criterio 4**
(pruebas) de la [Definition of Done](../project-management/DEFINITION_OF_DONE.md) **no
aplican**: no se modificó código, ni Compose, ni scripts, ni Terraform.

| Validación | Resultado |
| --- | --- |
| `git diff --check` | Sin errores |
| Finales de línea LF en todo Markdown modificado | Verificado |
| Enlaces relativos de los documentos nuevos y modificados | Resuelven |
| `images/Infraestructura.png` existe, se lee y está referenciada | Verificado; **sin modificar** |
| 41 identificadores del roadmap | Intactos, sin renumerar |
| Avance **6 / 41**, ETAPA 02 **2 / 3** | Sin cambios |
| Búsqueda de secretos | Sin hallazgos |
| Auditoría de consistencia terminológica | **0 contradicciones vivas** |

## 9. Pasos de validación para el usuario

1. Comprobar que `images/Infraestructura.png` **no aparece** en
   `git status` ni en `git diff --stat` de esta rama.
2. Leer
   [`docs/architecture/target-production-architecture.md`](../architecture/target-production-architecture.md)
   y contrastarlo con la imagen: deben describir lo mismo.
3. Revisar [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) — quedó
   **Aceptada** el 2026-08-23, y `ADR-003` conserva íntegra su decisión original.
4. Verificar en [`open-decisions.md`](../architecture/open-decisions.md) que **D-17** a
   **D-20** tienen propietario y que **ninguna crea una tarea nueva**.
5. Verificar en [`ROADMAP.md`](../project-management/ROADMAP.md) que siguen existiendo
   **41 tareas**, con los mismos identificadores y en el mismo orden.
6. Confirmar que `Task/007` sigue siendo **integración local** y que su guardrail no la
   convierte en despliegue cloud.
7. Comprobar que el árbol de trabajo está **sin commits**: esta tarea no comitea nada antes
   de la aprobación.

## 10. Aprobación

**Aprobada** por el usuario el 2026-08-23 con la expresión exacta requerida por
[WORKFLOW.md](../project-management/WORKFLOW.md):

```
approved: Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion
```

Con ella, **ADR-008** pasa a **Aceptada**, el documento canónico a **Vigente**, las
decisiones cerradas a **de cumplimiento obligatorio**, **D-17** a **D-20** a **abiertas con
propietario** y **R-38** a **R-42** a **abiertos**.

> **Aprobar no autoriza a implementar.** Contratar Grafana Cloud, provisionar el VPS,
> instalar Alloy o crear cualquier recurso cloud sigue exigiendo su tarea propietaria y una
> autorización explícita del usuario (§4 y
> [target-production-architecture.md](../architecture/target-production-architecture.md)
> §24).
