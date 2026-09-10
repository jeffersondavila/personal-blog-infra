# ETAPA 06 — Integración Continua

| Campo | Valor |
| --- | --- |
| **Número** | 06 |
| **Estado** | En progreso — 2 de 3 aprobadas (67 %) |
| **Dependencias** | [ETAPA 05](STAGE-05-quality-security.md) |
| **Tareas** | 3 |
| **Aprobadas** | 2 |
| **Avance** | 67 % |
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

### `Task/020-CI-Backend` — *Aprobada (2026-09-10)*

Ruff, MyPy, Pytest, verificación de migraciones, build de imagen Docker y escaneo.

**Depende de:** `Task/018`. **Repositorios:** `personal-blog-backend` e infra
(documentación). [Ficha](../tasks/TASK-020-ci-backend.md) ·
[Reporte](../task-reports/TASK-020-report.md).

*Observado el 2026-09-09 (Guatemala):* se completó el preflight y se corrigió,
con autorización expresa, el avance heredado de esta tabla de 0 % a 33 %.
La lectura posterior detectó B-020-1, otra contradicción preexistente en README
backend §3, y se detuvo antes de implementar CI. También se detectó B-020-2
en el Total de ROADMAP. El usuario autorizó ambas correcciones y se aplicaron:
son D preexistentes resueltas durante el preflight. Task020 retomó En progreso.
Al registrar ese desbloqueo no se había obtenido todavía una ejecución real
de Task020 en Actions.

La lectura obligatoria posterior del 2026-09-09 detectó B-020-3 en el reporte
Task019: §H negaba su aprobación y §R conservaba el PR como abierto en presente.
Se detuvo Task020 antes de corregir esos párrafos. El desbloqueo requirió tratamiento
autorizado por el usuario. Después se autorizaron y corrigieron: B-020-3A (D) y B-020-3B (C) resueltas; Task020 retomó En progreso. No se reabren Task019/019.1.

*Implementación del 2026-09-10:* workflow `CI Backend` en cada `push` y
`pull_request`, un job secuencial en `ubuntu-24.04` con Python 3.12.14,
PostgreSQL y MinIO efímeros del propio runner, migraciones sobre el motor real,
la suite completa con `-W error` y escaneo de imagen con política *fail-closed*.
**R-14 queda resuelto** como propuesta: dos *locks* transitivos con hashes,
instalación `--require-hashes` y detección de desfase. El baseline destapó dos
defectos reales y preexistentes —la regresión de `anyio` y tres
vulnerabilidades con corrección en `httpx2`— y ambos se corrigieron, el segundo
con autorización expresa. Ejecuciones reales de Actions y su auditoría paso a
paso en el [reporte](../task-reports/TASK-020-report.md).

*Revisión previa a la aprobación, 2026-09-10:* a petición del usuario se
auditaron dos puntos y los dos resultaron ser contradicciones reales, ya
corregidas. **D-020-1**: la instalación local documentada usaba
`pip install -e ".[dev]"`, que vuelve a resolver transitivas y elude el propio
*lock* que la tarea declara como garantía; el alcance real quedó documentado por
entorno, con la razón técnica por la que los *locks* no son instalables en
Windows. **D-020-2**: una sobreafirmación atribuía SHA o digest a todas las
herramientas externas cuando `pip-audit` solo está fijado por versión exacta.
**D-020-3**: el texto afirmaba que `--require-hashes` implica `--no-deps`, y no
es así; la garantía viene de que el *lock* enumera el cierre transitivo, no de
desactivar la resolución. Las tres son defectos del texto, no de la
implementación, y ninguna reabre etapas anteriores.

*Aprobada el 2026-09-10* mediante `approved: Task/020-CI-Backend`. Avance
**20/41 — 49 %**; esta etapa pasa a **2/3 — 67 %** y **sigue sin completarse**:
falta `Task/021`. **R-14 cerrado**; **S-09 backend** satisfecho y **S-09 global**
abierto. Las decisiones **D-020-A** a **D-020-H** quedan **vigentes**, sin ADR
nuevo.

*Observado el 2026-09-10 UTC, durante y después del cierre aprobado:* el trigger
`pull_request` quedó acreditado por la ejecución **34489982595**, disparada por el
pull request `#15` sobre el head `22af3f1`, con conclusión **`success`**; y la
ejecución **34491446991**, disparada por `push` sobre `dev` con head en el merge
de normalización `5fedcb3`, también concluyó **`success`**. Las dos con sus **21**
pasos en verde, **1855** pruebas y **0** omitidas. Ambos triggers del workflow del
backend tienen, por tanto, ejecución real registrada.

**Criterion 12 de `Task/020` cierra en C = 0 y D = 0**, recalculado el 2026-09-10
por [`Task/020.1`](../tasks/TASK-020.1-correct-post-merge-documentation-drift.md):
la afirmación se escribió durante el cierre, cuando el resultado de la fusión
todavía no existía, y ese mantenimiento convirtió en hechos fechados las
afirmaciones de estado vivo que la fusión volvió falsas.

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
arriba. Task020 siguió el mismo patrón el 2026-09-10, con su propia autorización
de bootstrap y sus dos ejecuciones posteriores al cierre. Publicar una mutación
deliberadamente rota exige un permiso adicional y **sigue sin autorizarse**.
Ninguna de estas observaciones completa por sí sola la etapa: los criterios de
salida exigen los **tres** repositorios, y `Task/021` sigue pendiente.

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
