# TASK-005.6 — Cerrar fundaciones tras la mega auditoría

| Campo | Valor |
| --- | --- |
| **Rama** | `Task/005.6-Cerrar-Fundaciones-Tras-Mega-Auditoria` |
| **Tipo** | **Mantenimiento transversal de fundaciones** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-16 |
| **Fecha de aprobación** | 2026-08-16 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.6-Cerrar-Fundaciones-Tras-Mega-Auditoria` |
| **Etapa** | Ninguna. Es mantenimiento previo a `Task/006` |
| **Cuenta en las 41 tareas** | **No** |
| **Repositorios** | `personal-blog-infra`, `personal-blog-backend`, `personal-blog-frontend` |
| **Rama base** | **`main`** en los tres |
| **SHA base** | infra `bd0aaf5` · backend `72c8adc` · frontend `4132a65`. `HEAD == main` verificado inmediatamente después de crear cada rama |
| **Depende de** | `Task/005.5` (aprobada, fusionada y normalizada) |
| **Habilita** | `Task/006-Fundacion-Frontend-React` |

---

## 1. Contexto

Dos auditorías independientes —una de **Claude** y otra de **Codex**— revisaron el proyecto
completo antes de iniciar `Task/006`. Coinciden en lo esencial:

> **No existe un defecto arquitectónico que obligue a reconstruir el proyecto.** La
> arquitectura, Git, el roadmap, PostgreSQL, FastAPI, Docker, Alembic y las *boundaries* son
> reutilizables.

Pero encontraron problemas concretos en **reproducibilidad**, **aislamiento de las pruebas**,
**seguridad del harness de PostgreSQL**, **semántica de los tests transaccionales** y
**estado documental posterior a `Task/005.5`**.

Esta tarea los cierra. Su objetivo no es rediseñar nada: es dejar los cimientos en un estado
que `Task/008` y siguientes puedan dar por bueno sin volver a auditarlo.

### 1.1 Principio de trabajo aplicado

Ningún hallazgo se aceptó como autoridad. El ciclo seguido para cada uno fue:

```
HALLAZGO → REPRODUCIR → ENTENDER CAUSA → CONTRASTAR CON FUENTE CANÓNICA
        → DECIDIR → CORREGIR → CREAR REGRESIÓN → REVALIDAR
```

Los identificadores llevan **prefijo de origen** (`CLAUDE-` / `CODEX-`) a propósito: las dos
auditorías reutilizaron numeración `MEGA-AUD` con significados distintos.

---

## 2. Dentro del alcance

| # | Materia | Repositorio |
| --- | --- | --- |
| 1 | Política de finales de línea (`.gitattributes`) | los tres |
| 2 | Aislamiento de la suite frente al `.env` del desarrollador | backend |
| 3 | Base de datos de pruebas dedicada y guarda *fail-closed* | backend, infra (runbook) |
| 4 | Distinción `skip` / `fail` de la integración | backend, infra (estrategia) |
| 5 | Verificación semántica de `commit` y `rollback` | backend |
| 6 | Test de migraciones con contrato durable | backend |
| 7 | Cobertura de una configuración `production` **válida** | backend |
| 8 | Estado documental posterior a `Task/005.5` | infra |
| 9 | Regla de gobierno: estado duradero frente a transitorio | infra |
| 10 | Contradicciones documentales puntuales | infra, backend |

## 3. Fuera del alcance

Se dejan **con propietario ya asignado**, no sin resolver:

| Materia | Propietario |
| --- | --- |
| Redacción automática de secretos en el log (**R-36**) | `Task/017`, `Task/018` |
| *Lock* transitivo con hashes (**R-14**) | `Task/020` |
| Actualización de dependencias | Ninguna tarea lo pide ahora |
| Endurecimiento productivo | `Task/018` |
| Terraform, Floci, AWS, VPS, PgBouncer, Cloudflare | ETAPAS 08–11 |
| Modelo de datos y funcionalidad del blog | `Task/008` y siguientes |
| Código del frontend | `Task/006` |

> **Regla aplicada:** un hallazgo cuya tarea propietaria futura es correcta **se queda
> allí**. No se mueve trabajo a `Task/005.6` solo porque una auditoría lo mencionara.

---

## 4. Hallazgos y veredictos

Matriz completa con evidencia en el
[reporte](../task-reports/TASK-005.6-report.md) §3.

| Veredicto | Cantidad |
| --- | --- |
| **CORREGIR EN 005.6** | 13 |
| **DIFERIR CON OWNER YA DEFINIDO** | 2 |
| **FALSO POSITIVO / YA CORREGIDO** | 1 |

---

## 5. Decisiones tomadas

### D-005.6-A — La política EOL se resuelve con `.gitattributes`, no con `core.autocrlf`

**Causa raíz:** Git para Windows instala `core.autocrlf=true` a nivel *system*
(`C:/Program Files/Git/etc/gitconfig`). El **índice ya guardaba LF**; era el *checkout* el
que producía CRLF en el árbol de trabajo, y `ruff format --check .` —configurado con
`line-ending = "lf"`— fallaba en los 31 archivos Python.

**Decisión:** `.gitattributes` con `* text=auto eol=lf` en los **tres** repositorios. No se
toca la configuración global de la máquina: los atributos del repositorio tienen prioridad
sobre `core.autocrlf`, de modo que un clon nuevo obtiene LF sin configurar nada.

**Consecuencia verificada:** **0 líneas de diff de contenido.** La corrección no reescribió
ningún archivo en el índice.

### D-005.6-B — Base de datos de pruebas dedicada, con marca dentro de la propia base

**Problema:** las pruebas de integración ejecutan `alembic downgrade base`. El README
indicaba apuntar `PERSONAL_BLOG_TEST_DATABASE_URL` a `personal_blog`, la base cotidiana de
desarrollo. Antes de `Task/008` eso solo borraba `alembic_version`; **desde `Task/008`
destruiría el contenido del blog**.

**Decisión:** base dedicada `personal_blog_test` y guarda *fail-closed* de **dos barreras**:

1. el nombre debe terminar en `_test`;
2. la base debe llevar la marca `personal-blog:test-database` en su **comentario de
   PostgreSQL**.

**Por qué la segunda barrera:** una guarda que solo lee la URL depende de que alguien la
escriba bien. La marca **vive dentro de la base**: escribir bien una URL no la fabrica, y
apuntar por error a `personal_blog` no la encuentra.

**Alternativas descartadas:** un segundo servicio en `docker-compose.yml` (innecesario: una
base adicional en el contenedor existente resuelve lo mismo y no toca el stack); *schema*
aislado (no protege de `downgrade base`, que actúa sobre el esquema); base efímera por
ejecución (más frágil y más lenta, sin ganancia de seguridad).

### D-005.6-C — Un fallo de PostgreSQL nunca se degrada a `skip`

El *fixture* capturaba cualquier excepción y llamaba a `pytest.skip`. Con credenciales
incorrectas o una regresión del motor, la suite quedaba **verde**. Regla nueva: sin variable
de entorno → `SKIP`; con variable y cualquier fallo → **`FAIL`**.

### D-005.6-D — Los tests transaccionales demuestran efecto, no llamadas

`commit` y `rollback` se verifican leyendo desde **otra sesión**. Validado por **mutación**:
con `session_scope` roto, ambos tests se ponen rojos. Los anteriores pasaban con el código
roto.

### D-005.6-E — El test de migraciones no puede fijar el estado del esquema

`assert tablas <= {"alembic_version"}` afirmaba que el proyecto no tiene tablas de negocio:
cierto solo antes de `Task/008`. Se sustituye por el contrato durable de **M-04** — el
esquema tras `upgrade` + `downgrade` debe ser idéntico al de antes—, que además detecta el
defecto real: una migración que crea un objeto y olvida soltarlo.

### D-005.6-F — Los documentos versionados no registran estado transitorio de GitHub

Ver [WORKFLOW §6.1](../project-management/WORKFLOW.md). Corrige la causa **estructural** del
drift: un documento escrito antes de la fusión y fusionado por ese mismo PR está condenado a
afirmar «el PR sigue abierto» para siempre.

---

## 6. Tests agregados y modificados

| Archivo | Test | Cambio |
| --- | --- | --- |
| `tests/test_configuration.py` | `test_la_configuracion_de_prueba_ignora_el_dotenv_del_desarrollador` | **Nuevo** — regresión del aislamiento |
| `tests/test_configuration.py` | `test_el_dotenv_intruso_del_caso_anterior_si_es_legible` | **Nuevo** — guarda anti-tautología del anterior |
| `tests/test_configuration.py` | `test_una_configuracion_de_produccion_valida_se_construye` | **Nuevo** — rama de cobertura que faltaba |
| `tests/integration/test_database_connection.py` | `test_session_scope_confirma_y_el_dato_persiste` | **Nuevo**, sustituye a una comprobación sin efecto observable |
| `tests/integration/test_database_connection.py` | `test_session_scope_revierte_y_el_dato_no_persiste` | **Nuevo**, sustituye a `test_session_scope_revierte_si_falla` |
| `tests/integration/test_migrations.py` | `test_el_downgrade_revierte_todo_lo_que_el_upgrade_creo` | **Nuevo**, sustituye a `test_la_migracion_fundacional_no_crea_tablas_de_negocio` |
| `tests/integration/test_migrations.py` | `test_upgrade_downgrade_y_reaplicacion` | **Modificado** — `head` se lee del directorio de scripts, ya no se fija `"0001"` |
| `tests/integration/conftest.py` | `tabla_de_pruebas` | **Fixture nueva** — tabla real y descartable, `DROP` en `finally` |

> **Justificación de las sustituciones**, exigida por
> [BACKEND_TESTING_STRATEGY §9](../project-management/BACKEND_TESTING_STRATEGY.md): ninguna
> se hizo para acomodar código incorrecto. Dos casos (`commit`/`rollback`) **contenían un
> error demostrado** —pasaban con la implementación rota, comprobado por mutación—, y el
> tercero (`tablas <= {"alembic_version"}`) codificaba un **requisito con caducidad
> conocida** que `Task/008` invalidará legítimamente.

---

## 7. Criterios de aceptación

### EOL

- [x] `.gitattributes` en los tres repositorios.
- [x] No depende de cambiar `core.autocrlf` global.
- [x] `ruff format --check .` **PASS**.
- [x] TS/TSX futuro protegido antes de que exista.
- [x] **0 diff semántico** por renormalización.

### Aislamiento de pruebas

- [x] Los tests unitarios no leen el `.env` del desarrollador.
- [x] Existe regresión que lo demuestra, con RED registrado.
- [x] Sin variable → `SKIP` explícito.
- [x] Variable definida e inválida → **FAIL**.
- [x] Base de pruebas aislada de `personal_blog`.
- [x] `downgrade` solo sobre entorno verificado.

### Transacciones

- [x] `commit`: el dato persiste y otra sesión lo ve.
- [x] `rollback`: el dato no persiste y otra sesión lo comprueba.
- [x] Sin mocks. Verificado por mutación.

### Migraciones

- [x] `upgrade` → `downgrade` → `upgrade` contra la base de pruebas.
- [x] El test no asume «0 tablas de negocio» para siempre.

### Configuración

- [x] `production` insegura rechazada.
- [x] `production` válida aceptada.

### Documentación y gobierno

- [x] `Task/005.5` registrada como fusionada y normalizada.
- [x] `Task/006` es la siguiente tarea oficial, **Pendiente**.
- [x] `STATUS.md` sin contradicciones vigentes.
- [x] Workflow sin necesidad estructural de una tarea de mantenimiento por cada PR.
- [x] Invariante `main → Task` intacto. **0 reglas** `dev → Task`.
- [x] Avance **5 / 41**; ETAPA 02 **1 / 3**.

---

## 8. Validaciones

Resultados completos en el [reporte](../task-reports/TASK-005.6-report.md) §5.

| Validación | Resultado |
| --- | --- |
| `pytest -W error` | **73 passed, 1 skipped, 0 warnings** |
| Cobertura | **100 %** — 249 sentencias, 22 ramas, 0 sin cubrir |
| Integración PostgreSQL real | **10 passed** |
| Guardas *fail-closed* | 4 rutas verificadas |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 32 files already formatted |
| `mypy` (strict) | Success, 30 source files |
| `pip check` | No broken requirements found |
| `docker build` + smoke | Imagen construida; contenedor `healthy`, no-root, `/health` 200, `/openapi.json` 200, contraseña enmascarada |
| `docker compose config --quiet` | Sin errores |
| `git diff --check` | Sin problemas |
| Secret scan | Sin credenciales reales |

---

## 9. Documentos relacionados

- [Reporte de la tarea](../task-reports/TASK-005.6-report.md)
- [WORKFLOW §6.1](../project-management/WORKFLOW.md) — estado duradero frente a transitorio
- [BACKEND_TESTING_STRATEGY §8.3](../project-management/BACKEND_TESTING_STRATEGY.md)
- [Runbook del entorno local §9](../runbooks/local-environment.md) — base de pruebas
- [STATUS.md](../project-management/STATUS.md)
