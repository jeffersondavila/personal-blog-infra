# TASK-005.7 — Cerrar hallazgos finales de certificación

| Campo | Valor |
| --- | --- |
| **Rama** | `Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` |
| **Tipo** | **Mantenimiento transversal**: hermeticidad del harness y *fail-closed* real de la integración |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-16 |
| **Fecha de aprobación** | 2026-08-16 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` |
| **Etapa** | Ninguna. Es mantenimiento previo a `Task/006` |
| **Cuenta en las 41 tareas** | **No** |
| **Repositorios** | `personal-blog-backend`, `personal-blog-infra`, `personal-blog-frontend` |
| **Rama base** | **`main`** en los tres |
| **SHA base** | infra `7c98f5910e3948561fb4ec2d1c80094520f31afa` · backend `c36cd44b5f5adb0a92568f1c30c2109ec97e7460` · frontend `5d2bef1b49e34a8cf9ada60aff613dbd5e00a3b8`. `HEAD == main` verificado inmediatamente después de crear cada rama |
| **Depende de** | `Task/005.6` (aprobada, fusionada y normalizada) |
| **Habilita** | `Task/006-Fundacion-Frontend-React` |

---

## 1. Contexto

Después de `Task/005.6` se ejecutó una **mega auditoría final independiente** con dos
agentes, **Claude** y **Codex**. Ambos reprodujeron **los mismos dos problemas técnicos
reales** en la fundación de testing.

Discreparon en la severidad, y la discrepancia es el dato interesante:

| Agente | Severidad asignada | Recomendación |
| --- | --- | --- |
| **Claude** | **MEDIO** | Diferir: `Task/006` es frontend y no depende técnicamente del backend |
| **Codex** | **ALTO** | No diferir: la baseline **no está certificada** mientras existan |

**Decisión adoptada en esta tarea: el criterio más estricto.** No se difieren; se corrigen
ahora.

**El motivo no es que `Task/006` dependa del backend** — no depende. El motivo es poder
declarar `Task/001` – `Task/005.7` como una **baseline cerrada**, sin arrastrar garantías
documentadas en `Task/005.6` que resultan ser **falsas**. Una garantía escrita que no se
cumple es peor que no haberla escrito: quien la lee deja de comprobar lo que promete.

`005.7` resuelve el **hecho**, no la discusión sobre la severidad. Ambos agentes reprodujeron
lo mismo; eso basta.

### 1.1 Principio de trabajo aplicado

Ningún hallazgo se aceptó como autoridad. El ciclo seguido para cada uno:

```
HALLAZGO → REPRODUCIR → ENTENDER CAUSA → CONTRASTAR CON FUENTE CANÓNICA
        → DECIDIR → CORREGIR (RED → GREEN) → CREAR REGRESIÓN → REVALIDAR
```

**Ningún hallazgo que no pudiera demostrarse se corrigió.**

---

## 2. Los dos defectos obligatorios

### 2.1 `CERT-AUD-001` — el harness no es hermético frente al `.env`

La suite podía consumir el `.env` del desarrollador. Dos manifestaciones, ambas
reproducidas:

**A — ruta de integración.** `configured_process` deja el proceso apuntando a la base real
fijando **solo** `BLOG_DATABASE_URL`. Las funciones que resuelven la configuración por sí
mismas —`session_scope`, `get_session`, `alembic/env.py`— llaman a `get_settings()`, que
construye `Settings` sin *overrides* y, por tanto, con `env_file=".env"`.

**B — durante la *collection*.** La cadena es:

```
tests/conftest.py  →  from app.main import create_app
app/main.py        →  app = create_app()      (nivel de módulo)
create_app()       →  get_settings()
get_settings()     →  Settings()              (env_file=".env", relativo al cwd)
```

Ese import ocurre **antes** de que ninguna *fixture* pueda intervenir: las *fixtures* se
ejecutan después de la *collection*, así que un `autouse=True` **llega tarde por
definición**.

**Efecto demostrado:** un `.env` intruso en el directorio de trabajo alteraba `app_name`,
`log_level` y `app_debug` del proceso de pruebas.

### 2.2 `CERT-AUD-002` — la protección de la base de integración no es estructural

`Task/005.6` puso la guarda *fail-closed* en `database_engine`. Pero dejó **pública** la
*fixture* `database_settings`, que entregaba la configuración **sin verificar nada**. La ruta

```
database_settings  →  Settings  →  create_database_engine(...)  →  DDL
```

permitía obtener una conexión al destino de integración sin pasar por las dos barreras
(sufijo `_test` y marca `personal-blog:test-database`).

La suite **actual** usaba correctamente `database_engine`. El problema es que el **harness
exponía** un camino que una prueba futura puede tomar por error.

Eso contradice la garantía que `Task/005.6` dejó documentada:

> «ninguna prueba de integración recibe configuración/engine sin que la guarda haya pasado»

**Reproducido:** con una base descartable terminada en `_test` **sin marca**, esa ruta abrió
conexión y ejecutó `CREATE TABLE`.

### 2.3 Alcance exacto de la garantía que se implementa

Definirlo con precisión es parte del trabajo, porque `Task/005.6` sobreafirmó.

**NO significa:** «ningún código Python imaginable puede crear un *engine* manualmente». Eso
sería imposible de garantizar y falso escribirlo.

**SÍ significa:**

> **Ninguna *fixture* pública u oficial del harness de integración entrega `Settings`,
> `Engine`, `Session`, conexión o `Config` de Alembic para el destino de integración antes
> de validar que ese destino es seguro.**

---

## 3. Hallazgos documentales bajos incluidos

Todos verificados antes de corregir. Los siete se reprodujeron.

| # | Hallazgo | Archivo |
| --- | --- | --- |
| 1 | «Backup y restauración → No existen → `Task/004`», con `Task/004` **aprobada** | `docs/runbooks/local-environment.md` |
| 2 | STAGE-11 afirma «sin credenciales permanentes» como absoluto y luego se desdice | `docs/stages/STAGE-11-deployment-automation.md` |
| 3 | `.editorconfig` y `.gitattributes` se contradicen para `*.ps1`/`*.psm1` y para `*.bat`/`*.cmd` | los tres repositorios |
| 4 | Dos secciones tituladas «Último mantenimiento aprobado» | `docs/project-management/STATUS.md` |
| 5 | Regla antigua «el estado real de las ramas se registra en STATUS.md» frente a §6.1 | `docs/project-management/WORKFLOW.md` |
| 6 | Comando histórico con `PERSONAL_BLOG_TEST_DATABASE_URL=.../personal_blog` | ficha y reporte de `Task/005` |
| 7 | «sin servicios de costo fijo mensual» pese a ADR-007 | `docs/architecture/overview.md` |

**El registro histórico no se reescribe.** El hallazgo 6 se marca con una advertencia
visible; el comando se conserva tal y como se escribió.

---

## 4. Hallazgo deliberadamente diferido

### `CERT-AUD-009` — concurrencia de la suite de integración

La suite **no es segura para ejecución concurrente** sobre la misma base: tabla auxiliar con
nombre fijo, `downgrade base` sobre esquema compartido y mutación de entorno y cachés de
proceso.

**No se implementa paralelismo ahora.** `pytest-xdist` no está instalado, no existe ejecución
paralela oficial y hay un único flujo de integración esperado: el riesgo **no es explotable
en el estado actual**, y resolverlo sería sobrediseñar sin un consumidor real.

Queda registrado como riesgo **R-37** en [STATUS.md](../project-management/STATUS.md), con
**propietario `Task/020-CI-Backend`** — la tarea canónica de CI del backend, que es quien
decidiría habilitar paralelismo. Debe revisarse **antes** de habilitarlo.

---

## 5. Dentro del alcance

| # | Materia | Repositorio |
| --- | --- | --- |
| 1 | Arranque hermético del harness de pruebas (`CERT-AUD-001`) | backend |
| 2 | Resolutor único verificado del destino de integración (`CERT-AUD-002`) | backend |
| 3 | Regresiones permanentes de ambos, con subproceso limpio | backend |
| 4 | Comprobación estructural del grafo de *fixtures*, sobre módulos **descubiertos** del directorio del harness | backend |
| 5 | Reconciliación `.editorconfig` / `.gitattributes` | los tres |
| 6 | Los siete hallazgos documentales de §3 | infra |
| 7 | Registro de `CERT-AUD-009` como **R-37** con propietario | infra |
| 8 | Actualización de `BACKEND_TESTING_STRATEGY` §8.3.5 – §8.3.7 | infra |

## 6. Fuera del alcance

**No se implementa nada de esto**, y su ausencia es deliberada:

React · Vite · frontend funcional · cualquier funcionalidad de negocio del backend ·
`Article` · `Review` · `Video` · `Project` · autenticación · S3 · adaptador MinIO de
aplicación · Lambda · Terraform · Floci · AWS · VPS · PgBouncer · Cloudflare · CI/CD ·
redacción global de secretos en el log · *lock* de dependencias completo · paralelismo de la
suite.

**No se toca la arquitectura productiva.** `app/` no cambia.

Se dejan **con propietario ya asignado**, no sin resolver:

| Materia | Propietario |
| --- | --- |
| Concurrencia de la integración (**R-37**, `CERT-AUD-009`) | `Task/020` |
| Redacción automática de secretos en el log (**R-36**) | `Task/017`, `Task/018` |
| *Lock* transitivo con hashes (**R-14**) | `Task/020` |
| Proveedor, tamaño y *pooling* del VPS PostgreSQL | `Task/029` |
| **D-16** — identidad del VPS hacia AWS | `Task/029` |

---

## 7. Criterios de aceptación

### 7.1 `CERT-AUD-001` — solo se considera cerrado si

- [x] La *collection* no consume un dotenv no controlado.
- [x] La ruta de integración no consume un dotenv no controlado.
- [x] Existe una **regresión permanente**.
- [x] Un **subproceso limpio** demuestra el aislamiento.
- [x] Un *cwd* distinto del repositorio no cambia el resultado.
- [x] Existe guarda **anti-tautología**: el `.env` intruso **sí** es legible sin aislamiento.
- [x] La suite completa queda verde.

### 7.2 `CERT-AUD-002` — solo se considera cerrado si

- [x] Ninguna *fixture* pública entrega el destino sin verificar.
- [x] El *engine* oficial está siempre verificado.
- [x] El `Config` de Alembic oficial está siempre verificado.
- [x] Una base sin la marca **falla**.
- [x] Una base sin el sufijo `_test` **falla**.
- [x] `personal_blog` **falla**.
- [x] El fallo ocurre **antes** de cualquier DDL.
- [x] Existe una **regresión permanente**.
- [x] `personal_blog` queda **intacta**.
- [x] La comprobación estructural **descubre** los módulos del harness en lugar de
      enumerarlos: añadir un módulo de integración nuevo **no** exige recordar registrarlo
      para conservar la protección. *(Añadido tras la revisión del usuario del 2026-08-16.)*
- [x] El descubrimiento tiene guarda anti-tautología: no puede quedarse verde por dejar de
      encontrar archivos.

### 7.3 Documentales — solo se consideran cerrados si

- [x] El backup local no figura como inexistente.
- [x] STAGE-11 no usa el absoluto incorrecto.
- [x] Las políticas EOL no se contradicen.
- [x] STATUS no tiene títulos engañosos.
- [x] WORKFLOW tiene una sola fuente viva.
- [x] Los comandos históricos de `Task/005` están marcados **NO EJECUTAR**.
- [x] El principio de costo reconoce el VPS como excepción consciente.

### 7.4 De gobierno

- [x] Ninguna afirmación promete más protección de la que existe.
- [x] `CERT-AUD-009` tiene propietario futuro explícito.
- [x] Avance: **5 / 41**. ETAPA 02: **1 / 3**. `Task/006`: **Pendiente**.
- [x] `005.7` **no cuenta** en las 41 tareas.

---

## 8. Validaciones exigidas

| Validación | Exigencia |
| --- | --- |
| RED/GREEN de ambos defectos | Evidencia registrada en el reporte, con el RED tomado **antes** del fix |
| `pytest -W error` | 0 *warnings*, sin filtros |
| Cobertura | Con `--cov-report=term-missing` |
| `ruff check` · `ruff format --check` · `mypy` | Sin errores, sin *autofix* de lint |
| `pip check` | Sin dependencias rotas |
| Suite **sin** `PERSONAL_BLOG_TEST_DATABASE_URL` | Unitarias verdes; solo se omite lo que exige PostgreSQL |
| *Mutation test* de `commit` y `rollback` | Ambos se ponen rojos; el archivo se restaura con el mismo hash |
| `personal_blog` antes/después | **Idéntica**: tablas, revisión de Alembic y comentario |
| Docker | `build` y *smoke* de `/health` y `/openapi.json`, sin secretos en el log |
| *Secret scan* | Ninguna credencial real en los cambios |

---

## 9. Estado

**Aprobada** el 2026-08-16 con la expresión
`approved: Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion`.

Quedan **vigentes** a partir de esta aprobación:

- El **arranque hermético** del harness de pruebas: la suite no consume el `.env` del
  desarrollador, tampoco durante la *collection*.
- La garantía ***fail-closed*** del harness de integración: un **único resolutor verificado**
  alimenta todas las *fixtures*, con el alcance definido en §2.3 —el harness oficial, no
  Python arbitrario—.
- El **descubrimiento automático** de los módulos del harness en la comprobación estructural:
  añadir un módulo de integración no exige recordar registrarlo.
- La política EOL coherente entre `.gitattributes` y `.editorconfig` en los tres repositorios.
- Las secciones §8.3.5 – §8.3.7 de
  [BACKEND_TESTING_STRATEGY](../project-management/BACKEND_TESTING_STRATEGY.md).
- El riesgo **R-37** con propietario `Task/020`.

`Task/006-Fundacion-Frontend-React` sigue **Pendiente y no iniciada**.

---

## 10. Documentos relacionados

- [Reporte de `Task/005.7`](../task-reports/TASK-005.7-report.md)
- [BACKEND_TESTING_STRATEGY](../project-management/BACKEND_TESTING_STRATEGY.md) §8.3.5 – §8.3.7
- [STATUS](../project-management/STATUS.md) — R-37
- [WORKFLOW](../project-management/WORKFLOW.md) §4, §6.1
- [TASK-005.6](TASK-005.6-close-foundations-after-mega-audit.md) — tarea anterior
- [Runbook del entorno local](../runbooks/local-environment.md) §9
