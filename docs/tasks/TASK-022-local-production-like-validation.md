# TASK-022 — Validación Local Production-Like

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/022-Validacion-Local-Production-Like` |
| **Nombre** | Validación Local Production-Like |
| **Etapa** | ETAPA 07 — Validación Local |
| **Estado** | **Aprobada** el 2026-09-12 |
| **Repositorios involucrados** | personal-blog-backend · personal-blog-infra · **personal-blog-frontend en SOLO LECTURA** |
| **Dependencias** | `Task/019`, `Task/020`, `Task/021` — las tres **Aprobadas** |
| **Rama** | `Task/022-Validacion-Local-Production-Like` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base backend** | `4a36bb532ed33851142785859c97ed7302efb31c` |
| **SHA base infra** | `184c833541bfd99a60df6a56c68b3dfa63e28a4d` |
| **Fecha de inicio** | 2026-09-12 |
| **Última actualización** | 2026-09-12 |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | backend | infra |
| --- | --- | --- | --- |
| 1 | `main == origin/main` | ✔ `4a36bb5…` en ambos lados | ✔ `184c833…` en ambos lados |
| 2 | Working tree limpio antes de crear la rama | ✔ `status --porcelain` vacío; staging 0; untracked 0 | ✔ ídem |
| 3 | Rama creada **desde `main`** | ✔ `git switch -c` desde `main` | ✔ ídem |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | ✔ `4a36bb532ed3…` | ✔ `184c833541bf…` |
| 5 | `dev` **no** es ancestro de `HEAD` | ✔ verificado con `merge-base --is-ancestor` | ✔ ídem |

**El frontend no tiene rama Task.** Permanece en `main` limpio y en solo lectura por
decisión explícita del usuario del 2026-09-12. Si el recorrido real descubre un defecto de
frontend que deba corregirse, la ejecución **se detiene y se reporta** antes de crear
ninguna rama allí.

---

## 1. Objetivo

Demostrar que el blog completo funciona, **se reconstruye desde cero** y **conserva sus
datos**, en condiciones equivalentes a producción, antes de crear ninguna cuenta cloud.

---

## 2. Contexto

Es la **puerta de control de [ADR-001](../adr/ADR-001-local-first.md)**: su punto 1 sitúa la
primera interacción con AWS o Cloudflare en la ETAPA 09, *«después de que la Etapa 07
(`Task/022`) haya demostrado el sistema completo funcionando en local»*.

Resuelve además una laguna acumulada y con propietario asignado: **la base local nunca ha
tenido administrador ni perfil**. `Task/012` decidió por diseño (**D-012-U**) que el perfil
no se crea por API — `PUT /admin/profile` sobre base vacía responde `404` y no deja fila.
En consecuencia, `Task/014`, `Task/015` y `Task/016` entregaron sus superficies **sin poder
validarlas nunca en un navegador con contenido real**. Cinco entradas de deuda documentadas
apuntan a esta tarea como dueña:

| Origen | Deuda | Referencia |
| --- | --- | --- |
| `Task/016` | **B-016-4** — evidencia con contenido real | STATUS §Bloqueos de Task/016 |
| `Task/014` | Deuda 12 — validación visual con contenido | [TASK-014](TASK-014-public-site.md) §deuda |
| `Task/015` | Deuda 8 y riesgo **R-A** — recorrido funcional con administrador real | [TASK-015](TASK-015-admin-panel.md) §976, §1083 |
| `Task/012` | Deuda 1 — perfil `404` sin semilla | [TASK-012](TASK-012-administrative-api.md) §495 |
| `Task/006` | Sin pruebas de extremo a extremo | [TASK-006](TASK-006-react-frontend-foundation.md) §377 |

La propiedad de la semilla no se infiere del nombre de la tarea: está escrita en
[`data-model.md`](../architecture/data-model.md) §5 —*«Datos semilla en el entorno local →
`Task/022-Validacion-Local-Production-Like`»*— y repetida en los propios modelos ORM de
`Administrator` y `Profile`.

---

## 3. Dentro del alcance

Los ocho elementos son los que enumera
[STAGE-07](../stages/STAGE-07-local-validation.md), sin añadir ni quitar:

- [x] Reconstrucción completa del entorno desde cero.
- [x] Aplicación de migraciones sobre base vacía.
- [x] **Carga de datos semilla** (`Administrator` + `Profile`) — único entregable de código.
- [x] Recorrido completo del flujo administrativo.
- [x] Publicación de contenido real de prueba.
- [x] Verificación de persistencia tras reinicio.
- [x] Ejecución y **restauración** de un backup.
- [x] Revisión del estado de todos los servicios en Portainer.

Y, como consecuencia obligatoria del octavo: **evidencia registrada de cada punto**.

---

## 4. Fuera del alcance

Lo que declara STAGE-07 §Fuera del alcance:

- Cualquier acción en proveedores cloud.
- Adaptación a Lambda (ETAPA 08, `Task/023`).
- Terraform (ETAPA 08, `Task/025`).

Y, por decisión explícita registrada en el preflight del 2026-09-12:

| No se hace | Motivo |
| --- | --- |
| Cerrar **D-21** / promover **ADR-009** | No le está asignada. `Task/022` **aporta evidencia** con contenido real, que es lo que [`open-decisions.md`](../architecture/open-decisions.md) §6.4 pide; no elige estrategia de *rendering* |
| Cerrar **R-018-3** (residual MinIO) | Sigue **ABIERTO**. No se toca el baseline ni la política S-09 |
| Cerrar **R-021-1** (residual Portainer) | Sigue **ABIERTO** |
| Cerrar **R-018-4** (buckets residuales de prueba) | Sigue **ABIERTO**; borrarlos es destructivo y no está autorizado por separado |
| Modificar el frontend | Solo lectura, salvo defecto demostrado y decisión previa del usuario |
| Contenido de demostración extenso | La semilla crea el **mínimo** estado requerido para validar |
| Crear cuentas, DNS, dominio público | ADR-001 lo sitúa en la ETAPA 09 |
| Reabrir ETAPA 06 o arrastrar `Task/020.3` | Cerradas y normalizadas |

---

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Semilla local | backend | `scripts/seed_local.py` |
| Suite test-first de la semilla | backend | `tests/integration/test_seed_local.py` |
| Ficha de la tarea | infra | `docs/tasks/TASK-022-local-production-like-validation.md` |
| Reporte de la tarea | infra | `docs/task-reports/TASK-022-report.md` |
| Runbook actualizado | infra | `docs/runbooks/local-environment.md` |
| Estado y planificación | infra | `docs/project-management/STATUS.md`, `ROADMAP.md`, `docs/stages/STAGE-07-local-validation.md` |
| Cierre de **T-07** | infra | `docs/architecture/non-functional-requirements.md` |

---

## 6. Criterios de aceptación

Los ocho criterios de salida de STAGE-07, literales:

1. El entorno se reconstruye desde cero **sin intervención manual no documentada**.
2. Todas las migraciones aplican sobre base vacía.
3. Es posible **crear, editar, publicar y archivar** cada tipo de contenido
   (`Post`, `BookReview`, `Video`, `Project`).
4. Las imágenes subidas **se sirven correctamente en el sitio público**.
5. Los datos y archivos **sobreviven a un reinicio completo**.
6. **Un backup se restaura con éxito y los datos coinciden.**
7. Todos los servicios aparecen **sanos en Portainer**.
8. **Se registra evidencia de cada punto anterior.**

**NFR que esta tarea puede cerrar: `T-07`** —*«el entorno local se reconstruye desde cero
siguiendo un runbook escrito»*—, cuyos propietarios son `Task/004` y `Task/022`.
Ningún otro NFR se declara cerrado aquí.

---

## 7. TDD / Plan test-first

**Obligatoria.** La semilla crea `Administrator` y `Profile`: es **comportamiento funcional
nuevo** de persistencia y autenticación. No cae en las excepciones de
[`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md) §4 —no es
*wiring* trivial ni «script trivial»—: tiene idempotencia definida, respeta invariantes
*singleton* de PostgreSQL y escribe una credencial. Se aplican **B-1 a B-12**.

### 7.1 Comportamientos a construir

1. Sobre una base **migrada y vacía**, la semilla deja **exactamente un** `Administrator` y
   **exactamente un** `Profile`.
2. La contraseña se almacena como **hash Argon2id con los parámetros vigentes de
   `Task/011`**, y el hash resultante **verifica** con la misma primitiva que usa el login.
3. La semilla es **idempotente**, con esta definición explícita: *ejecutarla N veces deja el
   mismo estado observable que ejecutarla una vez; no duplica filas, no rota la contraseña
   ya establecida y no sobrescribe campos editados después por el panel.*
4. Las credenciales y los datos personales llegan **por variables de entorno**; no hay
   ningún valor por defecto para la contraseña ni para el correo.
5. La semilla **nunca** emite la contraseña por salida estándar, error ni log (**S-08**), y
   **nada sensible se versiona** (**S-10**).
6. Ante una precondición incumplida —base sin migrar, entrada inválida, administrador ajeno
   ya presente— **falla de forma explícita y no deja estado parcial**.

### 7.2 Matriz de casos

Construida **antes** de escribir implementación (B-1).

| # | Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- | --- |
| C1 | Happy path | Correo, contraseña, nombre válidos | Base migrada y vacía | 1 `Administrator` + 1 `Profile`; código de salida 0 | integración |
| C2 | Hash compatible con el login | ídem C1 | Tras C1 | `contrasena_valida(hash, contrasena)` es `True` y `necesita_rehash(hash)` es `False` | integración |
| C3 | Idempotencia — sin duplicar | Misma entrada | Semilla ya ejecutada | Siguen siendo 1 y 1; ninguna excepción | integración |
| C4 | Idempotencia — no rota la credencial | Misma entrada | Semilla ya ejecutada | `password_hash` **idéntico** al de la primera ejecución | integración |
| C5 | Idempotencia — no pisa ediciones del panel | Misma entrada | `full_name`/`headline` editados tras sembrar | Los valores editados **se conservan** | integración |
| C6 | Falta la contraseña | Variable de contraseña ausente | Base migrada y vacía | Error explícito, salida ≠ 0, **0 filas creadas** | integración |
| C7 | Falta el correo | Variable de correo ausente | Base migrada y vacía | Error explícito, salida ≠ 0, **0 filas creadas** | integración |
| C8 | Correo malformado | `no-es-un-correo` | Base migrada y vacía | Rechazo explícito, **0 filas creadas** | integración |
| C9 | Contraseña demasiado corta | Cadena por debajo del mínimo | Base migrada y vacía | Rechazo explícito, **0 filas creadas** | integración |
| C10 | Administrador ajeno ya presente | Correo distinto del sembrado | Un `Administrator` con otro correo | **No** crea un segundo; mensaje claro; el cerrojo `administrador_unico` no se viola | integración |
| C11 | Base sin migrar | Entrada válida | Esquema ausente | Falla explícita; no crea tablas ni filas | integración |
| C12 | Sin secretos en la salida | Entrada válida | — | La contraseña **no aparece** en stdout, stderr ni en los registros emitidos | integración |

### 7.3 Tests RED esperados

Todos en `tests/integration/test_seed_local.py`, marcados `@pytest.mark.integration`.

| Test | Caso | Motivo de fallo esperado en RED |
| --- | --- | --- |
| `test_siembra_administrador_y_perfil_en_base_vacia` | C1 | `ModuleNotFoundError`: `scripts.seed_local` no existe |
| `test_el_hash_sembrado_verifica_con_la_primitiva_del_login` | C2 | ídem |
| `test_segunda_ejecucion_no_duplica_filas` | C3 | ídem |
| `test_segunda_ejecucion_conserva_el_hash` | C4 | ídem |
| `test_no_sobrescribe_campos_editados` | C5 | ídem |
| `test_falla_sin_contrasena` | C6 | ídem |
| `test_falla_sin_correo` | C7 | ídem |
| `test_rechaza_correo_malformado` | C8 | ídem |
| `test_rechaza_contrasena_corta` | C9 | ídem |
| `test_no_crea_segundo_administrador` | C10 | ídem |
| `test_falla_sobre_base_sin_migrar` | C11 | ídem |
| `test_no_emite_la_contrasena` | C12 | ídem |

En RED el motivo es la **ausencia del módulo**, que es la razón esperada para código que
todavía no existe. La evidencia literal se conserva en el reporte (B-2).

### 7.4 Integración necesaria

**PostgreSQL real, nunca SQLite** (B-6). Los comportamientos dependen de garantías que solo
da el motor: los cerrojos `UNIQUE (is_singleton)` con `CHECK (is_singleton IS TRUE)` de
`administrators` y `profiles`, y el único sobre `email`. Se usa el harness oficial de
integración —`PERSONAL_BLOG_TEST_DATABASE_URL` sobre `personal_blog_test`, con su marca
`personal-blog:test-database`—, cuyas fixtures derivan todas de la guarda *fail-closed*
`destino_de_integracion_verificado`.

MinIO **no** es necesario para la semilla: no crea `MediaAsset`.

### 7.5 Casos negativos y de seguridad

C6 a C12 de la matriz. En particular:

- **S-08 / S-10** — C12 comprueba con un valor señuelo que la contraseña no se filtra a
  ninguna salida. Ningún valor real se versiona: los tests usan dominios reservados
  (RFC 2606) y cadenas de prueba, igual que `tests/integration/datos_de_autenticacion.py`.
- **Invariante *singleton*** — C10 comprueba que la semilla no intenta violar el cerrojo.
- **Sin estado parcial** — C6 a C9 y C11 exigen 0 filas tras el fallo.

### 7.6 Regresiones relevantes

- Suite completa del backend: **1855** pruebas es el baseline vigente tras `Task/020.3`.
- `tests/unit/test_hash_de_contrasenas.py` — los parámetros de Argon2id no se relajan.
- `tests/test_grafo_de_fixtures_de_integracion.py` — toda fixture nueva debe seguir
  derivando de la guarda verificada.
- `tests/integration/test_singletons.py` — los cerrojos siguen intactos.
- `tests/integration/test_api_admin_perfil.py` — el perfil **sigue sin crearse por API**
  (D-012-U). La semilla **no** cambia esa decisión.

---

## 8. Plan de validación

| Criterio | Cómo se comprueba |
| --- | --- |
| 1 | Reconstrucción siguiendo **únicamente** el runbook escrito; toda desviación se registra como hallazgo antes de corregir el runbook |
| 2 | `alembic current`/`history` sobre base recién creada; volúmenes nuevos demostrados |
| 3 | Recorrido en navegador de los flujos B.1–B.12 de [`USER_FLOWS.md`](../product/USER_FLOWS.md) para los cuatro tipos publicables |
| 4 | Imagen subida por el panel y verificada en el sitio público servido por Traefik |
| 5 | Reinicio **sin** eliminar volúmenes; recuento de filas y objetos antes/después |
| 6 | Backup nuevo del entorno ya poblado, verificación e **restauración real** con comparación objetiva |
| 7 | **Requiere intervención del usuario en la interfaz de Portainer**; `docker ps` no basta |
| 8 | Reporte con la evidencia de cada punto |

---

## 9. Comandos de validación

```bash
# Gates del backend (no destructivos)
ruff format --check .
ruff check .
mypy .
pytest -W error --durations=15

# Integración con PostgreSQL real (requiere la variable del runbook §9.4)
pytest tests/integration/test_seed_local.py -W error -v

# Infra (no destructivo)
docker compose config
docker compose ps
```

---

## 10. Evidencia esperada

- Salida literal de RED y GREEN de la semilla.
- Recuento de filas y objetos antes y después de cada operación crítica.
- Identificador, ruta y resultado de integridad de cada backup.
- Inventario exacto de volúmenes destruidos y recreados.
- Registro de cada paso manual no documentado que aparezca durante la reconstrucción.
- Confirmación del usuario sobre el estado de los servicios en Portainer.

---

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | `docker compose down -v` destruye los datos locales, incluidos el rol `blog_runtime` y la identidad de MinIO | Alto | Backup verificado **fuera** de los volúmenes destruibles; guarda documentada antes de destruir |
| 2 | La semilla maneja una credencial y datos personales | Alto | Entrada por variables de entorno; nada versionado (**S-10**); C12 comprueba que no se filtra |
| 3 | La reconstrucción destapa pasos manuales no documentados | Medio | Es el hallazgo que la tarea busca: se registra primero y se corrige el runbook después |
| 4 | La restauración falla o los datos no coinciden | Medio | Criterio 6 obligatorio; comparación objetiva, no «exit 0» |
| 5 | El recorrido real destapa defectos de producto | Medio | Se detiene, se clasifica y se pide decisión de alcance antes de ampliar |
| 6 | **R-018-4**: dos *buckets* residuales de prueba entran en cada respaldo | Bajo | Ya documentado; no se borran aquí |

---

## 12. Decisiones técnicas

| Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- |
| **D-022-A** — La semilla vive en `personal-blog-backend`, en `scripts/seed_local.py` | Ubicarla en `personal-blog-infra` junto a `runtime_privileges.py` | La semilla necesita Argon2id, los modelos ORM y las invariantes del dominio. PROJECT_INSTRUCTIONS §13 asigna dominio, persistencia y autenticación al backend, y excluye de infra la «lógica de negocio de la aplicación». El precedente de `runtime_privileges.py` es infraestructura —roles y políticas—, no dominio | No |
| **D-022-B** — Idempotencia definida como *«no duplica, no rota la credencial, no pisa ediciones»* | Idempotencia como «recrear siempre desde cero» | Recrear rotaría la contraseña en cada ejecución y borraría lo editado por el panel, que es justo lo que el criterio 5 debe conservar | No |
| **D-022-C** — Credenciales por variable de entorno, sin valor por defecto | Valores por defecto para comodidad | Un valor por defecto es una credencial conocida; fallar es la conducta correcta (**S-10**) | No |
| **D-022-D** — La semilla crea el mínimo: `Administrator` + `Profile` | Sembrar también contenido de ejemplo | El contenido de prueba lo crea el **recorrido administrativo real**, que es lo que los criterios 3 y 4 deben demostrar. Sembrarlo lo sustituiría por un atajo | No |

> Todas estas decisiones quedaron **Vigentes** con la aprobación del **2026-09-12**.
> Hasta entonces estuvieron como *Propuesta — pendiente de aprobación*.

---

## 12.1 Hallazgos de la reconstrucción — registrados antes de corregir nada

> La reconstrucción se ejecutó siguiendo **únicamente** el runbook escrito, que es lo que
> exige el criterio 1. Cada paso que hizo falta y **no** estaba en el procedimiento se
> registra aquí como hallazgo, con su evidencia, **antes** de tocar la documentación. Son
> exactamente el riesgo que [STAGE-07](../stages/STAGE-07-local-validation.md) nombra:
> *«pasos manuales no documentados que impiden reproducir el entorno»*.

| # | Hallazgo | Evidencia | Estado |
| --- | --- | --- | --- |
| **H-1** | **El runbook §8 no construye las imágenes.** Usa `docker compose pull` sin acotar, que falla para las **cuatro** imágenes que el proyecto construye, y **omite `docker compose build`**. El §4 (Arranque) sí lo tiene: acota el `pull` a los terceros y construye en su paso 4. | `pull access denied` para `personal-blog-backend`, `-frontend`, `-traefik` y `-postgres`, más el aviso del propio Compose: *«Some service image(s) must be built from source»* | Corregir §8 |
| **H-2** | **El runbook §8 no crea el bucket de medios.** `down -v` lo destruye con el volumen, y §8 no lo recrea, de modo que el paso 6 —`runtime_privileges.py --apply`— **termina en exit 1**. El procedimiento existe, pero vive en §10.2 y §8 no lo enlaza. | `Verificacion interrumpida (NoSuchBucket)` y **exit 1**. Tras crear el bucket con §10.2, el mismo comando da **exit 0**: causa y efecto demostrados | Corregir §8 |
| **H-3** | **Defecto del propio entregable.** `python scripts/seed_local.py` —la forma documentada en su docstring— fallaba: al invocar por ruta, Python coloca `scripts/` en `sys.path` y no la raíz, así que `app` no se resolvía. Ninguna prueba lo detectaba porque todas **importaban** el módulo. | `ModuleNotFoundError: No module named 'app'` | **Resuelto**, con regresión permanente en `tests/test_seed_local_invocacion.py` |
| **H-4** | **El runbook §8 no menciona la base de pruebas.** `down -v` destruye también `personal_blog_test`, y sin ella la suite de integración se omite entera. El procedimiento está en §9.2–9.3, pero §8 no lo enlaza. | Tras `down -v`, `SELECT … WHERE datname='personal_blog_test'` no devuelve nada | Corregir §8 |
| **H-5** | **La recuperación total no restaura las identidades runtime.** El runbook de backup **no menciona `blog_runtime` ni `runtime_privileges.py` en ninguna parte**, y su §9.4 pasa de `docker compose up -d` a restaurar los tres componentes. Pero el volcado lleva los `GRANT` al rol runtime **y no el rol**: `pg_dump` de una base no incluye roles globales. Siguiendo §9.4 al pie de la letra tras una pérdida total se recuperan los datos y **la aplicación queda sin permisos**. §12 «Qué no cubre `Task/004`» tampoco lo declara. | Con privilegios: `errors ignored on restore: 17`, todos `role "blog_runtime" does not exist`. **Con `--no-privileges`, que es lo que manda §9.1: ningún aviso y código 0** — el fallo es **silencioso** | **Resuelto y revalidado** (§12.2) |
| **H-6** | **La lista de «imágenes de terceros» de §4 es incorrecta**, e hizo que la primera corrección de H-1 heredara el error: incluía `postgres` y `traefik`, que el proyecto **construye** con Dockerfile propio. | `docker compose config`: solo `minio` y `portainer` declaran imagen sin `build`; las construidas son cuatro | **Resuelto** |
| **H-7** | **La recuperación manual copiaba a `/tmp` del contenedor**, imposible desde el endurecimiento de `Task/018` (`read_only: true`). Afecta a §9.1 y §9.2 del runbook de backup. El destino correcto es el área de paso `/backup`, que el propio Compose declara para esto. Además, **la imagen de MinIO no trae `find` ni `awk`**, así que el bucle que propone §9.2 tampoco funciona dentro del contenedor. | `Error response from daemon: container rootfs is marked read-only` y `find: command not found` | **Resuelto** |

**Causa común de H-1, H-2, H-4, H-5, H-6 y H-7:** el runbook §8 y el de backup son de
`Task/003` y `Task/004`; **`Task/010` introdujo el bucket de medios y `Task/018` el
endurecimiento y los dos planos de identidad**, y ninguno actualizó los procedimientos de
reconstrucción y recuperación. No son descuidos de redacción: son procedimientos que
quedaron atrás respecto del entorno que describen, y solo una reconstrucción real podía
demostrarlo.

---

## 12.2 H-5 — revalidación del procedimiento corregido

**No se declara resuelto porque cambiara el Markdown.** Corregido el runbook, se ejecutó
una **recuperación total real**: `down -v` completo y recuperación desde el conjunto
`20260913-000448`, verificado antes de usarlo. Se dejó `secrets/backend-runtime.env` en el
host **a propósito**, con credenciales ya muertas: es lo que ocurre en una pérdida real.

Un entorno Compose paralelo no servía: `runtime_privileges.py` fija MinIO en
`127.0.0.1:9000` y el archivo runtime en una ruta única, y los puntos E, F y G exigen ese
archivo y el contenedor `backend` reales.

| # | Comprobación | Resultado |
| --- | --- | --- |
| **A** | Restore de PostgreSQL | **17 tablas**, datos completos, código 0 |
| **B** | Restore de MinIO | **6 objetos** con su `Content-Type` |
| **C** | Identidades reprovisionadas por el procedimiento documentado | `--reissue-runtime-credentials --apply`, **exit 0** |
| **D** | `blog_runtime` existe | `super=false createdb=false createrole=false login=true`; identidad MinIO **enabled** con política `blog-runtime-media` |
| **E** | El archivo runtime corresponde a las nuevas credenciales | `4b028076…` → **`8c107c85…`** |
| **F** | El backend arranca con el plano runtime | `healthy`, DSN `postgresql://blog_runtime:***@postgres:5432/personal_blog` |
| **G** | `/ready` responde | **200**, `{"status":"ready"}` |
| **H** | `runtime_privileges.py` sin flags | **exit 0** |
| **I** | Mínimo privilegio vigente | DDL y `UPDATE`/`DELETE` de auditoría denegados **realmente**; en MinIO, listar global y administrar denegados |
| **J** | Sin errores de restore por rol inexistente | **0** errores de rol y **0** *errors ignored*, restaurando con privilegios en una base de comprobación. Antes: **17** |

**El entorno quedó operativo**, no solo restaurado: datos idénticos, **login `200`** e
imagen servida con los **mismos 4836 bytes**. **No se creó ningún rol a mano** y no se
inventó una segunda forma de provisionar: `--reissue-runtime-credentials` ya existía desde
`Task/018`, descrito en su propia ayuda como *«el camino de recuperación tras restaurar un
respaldo»*.

---

## 13. Documentación creada o actualizada

- `docs/tasks/TASK-022-local-production-like-validation.md` — ficha (nueva).
- `docs/project-management/STATUS.md` — etapa y tarea en curso.
- `docs/project-management/ROADMAP.md` — ETAPA 07 En progreso.
- `docs/stages/STAGE-07-local-validation.md` — estado de la etapa.
- *Pendientes de la fase de cierre:* `docs/runbooks/local-environment.md` (H-1, H-2, H-4),
  `docs/runbooks/local-backup-and-recovery.md` (H-5),
  `docs/architecture/non-functional-requirements.md` (**T-07**),
  `docs/task-reports/TASK-022-report.md`.

---

## 14. Archivos modificados

| Repositorio | Archivo | Acción |
| --- | --- | --- |
| backend | `scripts/seed_local.py` | creado |
| backend | `scripts/__init__.py` | creado |
| backend | `tests/integration/test_seed_local.py` | creado |
| backend | `tests/test_seed_local_invocacion.py` | creado (regresión de H-3) |
| backend | `pyproject.toml` | modificado — `scripts` declarado *first-party* para isort |
| infra | `docs/tasks/TASK-022-local-production-like-validation.md` | creado |
| infra | `docs/project-management/STATUS.md` | modificado |
| infra | `docs/project-management/ROADMAP.md` | modificado |
| infra | `docs/stages/STAGE-07-local-validation.md` | modificado |
| frontend | — | **sin rama y sin cambios** |

---

## 15. Resultado de pruebas

| Prueba | Comando | Resultado |
| --- | --- | --- |
| RED de la semilla | `pytest tests/integration/test_seed_local.py -W error` | **Falla**: `ModuleNotFoundError: No module named 'scripts.seed_local'` — la razón esperada (B-2) |
| GREEN de la semilla | ídem, tras implementar | **17 passed** (12 casos, 17 con parametrizaciones) |
| RED de H-3 | `pytest tests/test_seed_local_invocacion.py -W error` | **1 failed**: `ModuleNotFoundError: No module named 'app'` |
| GREEN de H-3 | ídem, tras la corrección | **3 passed** |
| Formato | `ruff format --check .` | **315 files already formatted** |
| Lint | `ruff check .` | **All checks passed!** |
| Tipos | `mypy .` | **Success: no issues found in 313 source files** |
| Regresión completa | `pytest -W error` con PostgreSQL y MinIO reales | **1871 passed, 1 skipped** en 310 s. El *skip* es estructural de Windows (`time.tzset`), ya documentado. 1871 + 1 = **1855 del baseline + 17 nuevas** |
| Recorrido administrativo | HTTP real por Traefik | **37 comprobaciones OK, 0 fallos** |
| Restauración | `Restore-LocalBackupTest.ps1` | **RESTAURACION VERIFICADA CORRECTAMENTE** |

---

## 16. Problemas encontrados

1. **H-1 a H-5**, en §12.1.
2. **Dos intentos fallidos del recorrido, ambos por error del guion de validación, no del
   producto.** El primero omitía `summary`, que la validación de publicación de `Task/012`
   exige (`409 cannot_publish_incomplete_draft`); el segundo reutilizaba un título ya
   usado (`409 slug_already_exists`). **Las dos respuestas del API fueron correctas**: el
   producto rechazó lo que debía rechazar. Como efecto colateral quedan **2 borradores
   huérfanos** de esos intentos, invisibles en el sitio público.
3. **Primer intento de la prueba de invocación mal construido:** un entorno sin
   `SystemRoot` hacía morir al subproceso en Windows con `WinError 10106` antes de ejecutar
   una línea del script. Se corrigió partiendo del entorno real y restando las variables,
   y la razón quedó escrita en el propio módulo de prueba.
4. **Tres contenedores residuales de `Task/020`** (`task020-runner`, `-minio`,
   `-postgres`), en marcha desde hacía dos días. Inspeccionados y eliminados con
   autorización: `Mounts=0` en los tres, sin volúmenes propios ni compartidos, sin
   pertenencia a ningún proyecto Compose y con puertos distintos de los del entorno local.
5. **Observación sobre R-018-4, que NO se cierra.** Los dos *buckets* residuales
   `personal-blog-test-*` desaparecieron con `down -v`, y el respaldo posterior inspecciona
   **1** bucket en lugar de 3. El riesgo **sigue abierto**: su causa —la limpieza del
   *harness* no sobrevive a un `SIGKILL`— no ha cambiado, y volverán a aparecer.

---

## 17. Pasos de validación para el usuario

**Portainer y el recorrido visual ya los confirmaste el 2026-09-12** (reporte §7). Lo que
sigue permite reproducir el resto sin operaciones destructivas.

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# 1. Los seis servicios en marcha y sanos
docker compose ps

# 2. El sitio y el API responden por Traefik
curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8081/
curl.exe -s http://localhost:8081/api/v1/profile        # 200: antes era 404 sin semilla

# 3. Contenido real publicado, y ningun archivado visible
curl.exe -s http://localhost:8081/api/v1/posts
curl.exe -s http://localhost:8081/sitemap.xml

# 4. Minimo privilegio del plano runtime: sin flags SOLO comprueba, debe dar 0
..\personal-blog-backend\.venv\Scripts\python.exe .\scripts\security\runtime_privileges.py
$LASTEXITCODE

# 5. Integridad de los dos conjuntos de respaldo
cd scripts\backup ; .\Test-LocalBackup.ps1 -All
```

Para entrar al panel: **http://localhost:8081/admin** con
`propietario@personal-blog.invalid`. La contraseña **no está en ningún documento**
(requisito S-10); vive en `secrets/seed-admin.env`, ignorado por Git:

```powershell
Get-Content .\secrets\seed-admin.env | Select-String PASSWORD
```

---

## 18. Deuda técnica pendiente

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | `runtime_privileges.py` fija MinIO en `127.0.0.1:9000` y el archivo runtime en una ruta única: impide validar la recuperación en un entorno Compose paralelo sin tocar el script | sin propietario asignado |
| 2 | La recuperación de MinIO de §9.2 sigue siendo **manual, objeto a objeto**. La lógica automatizada existe dentro de `Restore-LocalBackupTest.ps1`, pero solo para el entorno temporal | sin propietario asignado |
| 3 | Intermitencia de la suite de integración bajo contención de recursos | ya abierta desde `Task/005.7` |
| 4 | Dos borradores huérfanos en la base local, invisibles en el sitio público | ninguno: son datos de prueba de esta ejecución |

---

## 19. Próxima tarea

`Task/023-Compatibilidad-FastAPI-Lambda` — adaptador de FastAPI para API Gateway HTTP API y
Lambda. **No se inicia** hasta que `Task/022` esté aprobada y normalizada.

---

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-12** |
| **Aprobado por** | **El usuario** |
| **Expresión de aprobación** | `approved: Task/022-Validacion-Local-Production-Like` |

Con esta aprobación la tarea **cuenta en las 41**: el avance pasa a **22/41 ≈ 54 %** y la
**ETAPA 07 queda Completada** (1/1, 100 %). **T-07** pasa a **Satisfecho y Vigente**.

**No cambia:** **D-21** sigue Abierta y **ADR-009** en Propuesta; **R-018-3**, **R-021-1**
y **R-018-4** siguen Abiertos. `Task/023` queda **Pendiente, no iniciada**.
