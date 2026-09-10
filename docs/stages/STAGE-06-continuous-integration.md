# ETAPA 06 — Integración Continua

| Campo | Valor |
| --- | --- |
| **Número** | 06 |
| **Estado** | En progreso — 1 de 3 aprobadas (33 %) |
| **Dependencias** | [ETAPA 05](STAGE-05-quality-security.md) |
| **Tareas** | 3 |
| **Aprobadas** | 1 |
| **Avance** | 0 % |
| **Hito que completa** | CI verde en los tres repositorios. |

---

## Objetivo

Automatizar la verificación de calidad en cada cambio de los tres repositorios, de modo
que ningún cambio roto llegue a `dev` ni a `main`.

## Por qué esta etapa existe

Las verificaciones de la Etapa 05 solo tienen valor sostenido si se ejecutan solas.
Aquí se convierten en una barrera automática, no en un ritual manual.

## Tareas

### `Task/019-CI-Frontend` — *Aprobada (2026-09-08)*

Lint, type-check, tests y build en GitHub Actions.

**Depende de:** `Task/018`. **Repositorio:** `personal-blog-frontend`; infra solo
documentación según WORKFLOW. [Ficha](../tasks/TASK-019-ci-frontend.md) ·
[Reporte](../task-reports/TASK-019-report.md).

Añade los gates vigentes de formato y auditoría npm. El build precede a los tests
para ejecutar las guardas SEO/P-05 sobre el artefacto. Un job, Node 22.23.2
coherente con Dockerfile, lockfile reproducible, caché npm, permisos de lectura
y sin secretos ni despliegue. Sus decisiones de implementación quedan
**vigentes** con la aprobación del 2026-09-08. **No hay ADR nuevo.**

*Observado el 2026-09-08 (Guatemala) / 2026-09-09 UTC:* la ejecución
**34305529115**, disparada por `push`, concluyó **`success`** en **79 s** —job de
**76 s**— con los once pasos declarados en verde, **704** pruebas en **75**
archivos y **0** vulnerabilidades. Esa ejecución acreditó el trigger `push`.

*Observado el 2026-09-09 UTC, durante el cierre aprobado:* el trigger
`pull_request` quedó acreditado por la ejecución **34308296565**, disparada por el
pull request `#12`, con conclusión **`success`**; y la ejecución **34308234554**,
disparada por `push` sobre `dev`, también concluyó **`success`**. Ambos triggers
del workflow del frontend tienen, por tanto, ejecución real registrada.

### `Task/020-CI-Backend` — *Pendiente*

Ruff, MyPy, Pytest, verificación de migraciones, build de imagen Docker y escaneo.

**Depende de:** `Task/018`. **Repositorio:** `personal-blog-backend`.

### `Task/021-CI-Infraestructura` — *Pendiente*

`docker compose config`, validación de scripts y escaneo de secretos.

> **Corrección de `Task/005.5`.** Esta tarea pertenece a la ETAPA 06 y **no existe todavía
> ningún archivo Terraform**: el primero lo crea `Task/025`, en la ETAPA 08. Declarar aquí
> `terraform fmt` y `terraform validate` produciría **checks permanentemente en verde por
> no tener nada que validar**, que es peor que no tenerlos: aparentan cobertura.
>
> Regla vigente: `Task/021` configura el CI de infraestructura **para los artefactos que
> existen en ese momento**, y **`Task/025` es responsable de ampliarlo** con `terraform
> fmt -check` y `terraform validate` cuando cree la IaC. Ese *ownership* futuro es
> explícito, no implícito.

**Depende de:** `Task/018`. **Repositorio:** `personal-blog-infra`.

## Criterios de salida de la etapa

**Distribución de responsabilidades reconstruida en Task019:** cada repositorio
implementa sus triggers, gates, medición y revisión de logs en su tarea de CI.
S-09 frontend corresponde a Task019; backend a Task020; infraestructura a Task021.
El escaneo de secretos del historial está asignado explícitamente a Task021 y
se comprueba al cerrar la etapa; Task019 no afirma haber cubierto ese historial.
Task025 incorpora las verificaciones Terraform cuando existan archivos reales.

Los controles negativos locales se distinguen de la ejecución remota. En Task019,
el usuario autorizó el 2026-09-08 el bootstrap por push antes de aprobar; la
ejecución real de `pull_request` y el verde sobre `dev` quedaron comprobados
después, durante el cierre ordinario autorizado, con las ejecuciones citadas
arriba. Publicar una mutación deliberadamente rota exige un permiso adicional y
**sigue sin autorizarse**. Ninguna de estas observaciones completa por sí sola la
etapa: los criterios de salida exigen los **tres** repositorios.

- [ ] Cada repositorio ejecuta su workflow en cada push y pull request.
- [ ] Los tres workflows terminan en verde sobre `dev`.
- [ ] Un cambio deliberadamente roto hace fallar el workflow correspondiente.
- [ ] Ningún secreto aparece en los logs de CI.
- [ ] El tiempo de ejecución de cada workflow está documentado y es razonable.
- [ ] El escaneo de secretos cubre todo el historial disponible.
- [ ] **Ningún check pasa por no tener nada que verificar.** Si una verificación no aplica
      todavía, se declara explícitamente con la tarea que la incorporará.

## Fuera del alcance de la etapa

- Despliegue automático (Etapa 11).
- Credenciales cloud y OIDC (Etapa 09).
- `terraform plan` contra una cuenta real (Etapa 09/10).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Consumo de minutos de GitHub Actions. | Workflows acotados, caché de dependencias, sin matrices innecesarias. |
| CI que falla de forma intermitente y se ignora. | Tests deterministas; cualquier fallo intermitente se trata como defecto. |
| Escaneos que bloquean por falsos positivos. | Lista de excepciones justificada y revisada. |

## Siguiente etapa

[ETAPA 07 — Validación Local](STAGE-07-local-validation.md)
