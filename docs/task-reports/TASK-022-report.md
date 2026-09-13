# TASK-022 — Reporte — Validación Local Production-Like

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/022-Validacion-Local-Production-Like` |
| **Etapa** | ETAPA 07 — Validación Local |
| **Estado** | **Aprobada** el 2026-09-12 por el usuario mediante `approved: Task/022-Validacion-Local-Production-Like` |
| **Repositorios** | `personal-blog-backend`, `personal-blog-infra`. **`personal-blog-frontend`: sin rama y sin cambios** |
| **Rama base** | `main` en los dos repositorios con rama |
| **SHA base backend** | `4a36bb532ed33851142785859c97ed7302efb31c` |
| **SHA base infra** | `184c833541bfd99a60df6a56c68b3dfa63e28a4d` |
| **Fecha** | 2026-09-12 (zona local del proyecto, Guatemala) |
| **Ficha** | [TASK-022](../tasks/TASK-022-local-production-like-validation.md) |

---

## 1. Qué demuestra esta tarea

Que el blog completo **funciona, se reconstruye desde cero y conserva sus datos** en
condiciones equivalentes a producción. Es la puerta de control de
[ADR-001](../adr/ADR-001-local-first.md), cuyo punto 1 sitúa la primera interacción con
AWS o Cloudflare **después** de que la ETAPA 07 lo haya demostrado.

Los **ocho criterios de salida** de [STAGE-07](../stages/STAGE-07-local-validation.md)
quedaron satisfechos. **T-07** —*«el entorno local se reconstruye desde cero siguiendo un
runbook escrito»*— es el único requisito no funcional que esta tarea cierra, y **solo
pudo cerrarse después de corregir el runbook**: la primera reconstrucción real demostró
que el procedimiento escrito no reproducía el entorno.

---

## 2. Los ocho criterios

| # | Criterio | Resultado | Evidencia |
| --- | --- | --- | --- |
| 1 | Reconstrucción desde cero sin intervención manual no documentada | **Satisfecho tras corregir el runbook** | §4 y §5: siete hallazgos, todos corregidos y revalidados |
| 2 | Migraciones sobre base vacía | **Satisfecho** | 0 tablas y sin `alembic_version` antes; **`0003` y 17 tablas** después |
| 3 | Crear, editar, publicar y archivar cada tipo | **Satisfecho** | `Post`, `BookReview`, `Video`, `Project`: los cuatro verbos por HTTP real |
| 4 | Imágenes servidas en el sitio público | **Satisfecho** | Enlace firmado `200`, **4836 bytes idénticos** a los subidos, con `alt_text` |
| 5 | Datos y archivos sobreviven a un reinicio | **Satisfecho** | Estado idéntico antes y después de `down` + `up` sin tocar volúmenes |
| 6 | Backup restaurado con datos coincidentes | **Satisfecho** | Restauración verificada; conteos iguales y **huella `md5` idéntica fila a fila** |
| 7 | Servicios sanos en Portainer | **Satisfecho** | **Confirmación humana del usuario**, 2026-09-12 (§7) |
| 8 | Evidencia registrada de todo lo anterior | **Satisfecho** | Este reporte |

---

## 3. Lo que existía antes y lo que existe ahora

La base local **nunca había tenido administrador ni perfil**. `Task/012` decidió por
diseño (**D-012-U**) que el perfil no se crea por API, así que `Task/014`, `Task/015` y
`Task/016` entregaron sus superficies sin poder validarlas nunca con contenido real.

*Medido al empezar, 2026-09-12:* `administrators=0 profiles=0 posts=0 book_reviews=0
videos=0 projects=0 media_assets=0`, y `GET /api/v1/profile` respondía **404**.

*Medido al terminar:* `administrators=1 profiles=1 posts=4 book_reviews=2 videos=2
projects=2 media_assets=3`, y `GET /api/v1/profile` responde **200**.

Con eso quedan desbloqueadas cinco deudas que apuntaban a esta tarea: **B-016-4**, la
deuda 12 de `Task/014`, la deuda 8 y el riesgo **R-A** de `Task/015`, la deuda 1 de
`Task/012` y la ausencia de pruebas de extremo a extremo de `Task/006`.

---

## 4. La semilla — `scripts/seed_local.py`

Único entregable de código. Crea el **mínimo** estado necesario: un `Administrator` y un
`Profile`. **No siembra contenido de ejemplo** (decisión D-022-D): los artículos, reviews,
vídeos, proyectos e imágenes los creó el **recorrido administrativo real**, que es lo que
los criterios 3 y 4 debían demostrar; sembrarlos habría sustituido la demostración por un
atajo.

### 4.1 Ciclo TDD (B-1 a B-12)

| Paso | Evidencia |
| --- | --- |
| **B-1 matriz** | 12 casos (C1–C12) escritos en la ficha **antes** de implementar |
| **B-2 RED** | `ModuleNotFoundError: No module named 'scripts.seed_local'` — la razón esperada para código que aún no existe |
| **B-3 GREEN** | **17 passed** (12 casos, 17 con parametrizaciones) |
| **B-4 refactor** | `ErrorDeSemilla` → `SemillaInvalidaError`, por la convención de sufijo `Error` del proyecto (N818). Sin cambio de comportamiento observable |
| **B-5 / B-7** | Suite del área y **suite entera** en verde (§8) |
| **B-6 integración** | **PostgreSQL real, nunca SQLite**: lo que se afirma depende de los cerrojos del motor |
| **B-8/9/10** | C6–C12: variable ausente, correo malformado, contraseña corta, administrador ajeno, base sin migrar, y la prueba de señuelo de S-08 |
| **B-11** | H-3 dejó su regresión permanente en `tests/test_seed_local_invocacion.py` |
| **B-12** | Ninguna expectativa se modificó para acomodar la implementación |

### 4.2 Decisiones

- **D-022-A** — vive en el backend. Necesita Argon2id, los modelos ORM y las invariantes
  del dominio; PROJECT_INSTRUCTIONS §13 excluye de infra la lógica de negocio.
- **D-022-B** — idempotencia definida como *«no duplica, no rota la credencial, no pisa
  ediciones»*. Verificado en el entorno real: dos ejecuciones seguidas dejaron
  `administrators=1 profiles=1` y **la misma huella del hash**.
- **D-022-C** — credenciales por variable de entorno, **sin valores por defecto**. Un
  valor por defecto para la contraseña sería una credencial conocida (**S-10**).
- **D-022-D** — la semilla no crea contenido de demostración.
- **D-022-E** — mínimo de 12 caracteres para la contraseña sembrada. El login no impone
  mínimo —no le corresponde juzgar una credencial ya establecida—, pero **crearla** sí es
  la oportunidad de no fabricar una débil.

### 4.3 Con qué identidad se ejecuta, y por qué importa

Con el **plano de administración**, el mismo de las migraciones. No es una preferencia:
desde `Task/018`, `blog_runtime` tiene **solo `SELECT` y `UPDATE`** sobre `administrators`
y **no puede crear administradores** (**S-01**). Sembrar es provisión, no operación de la
aplicación.

### 4.4 Que el hash sirve, demostrado de dos formas

La prueba C2 comprueba que `contrasena_valida` acepta el hash y que `necesita_rehash` es
`False`. Y en el entorno real, el **login administrativo respondió `200` con cookie de
sesión**, con `401` en el control negativo sin cookie. La cadena semilla → Argon2id →
login de `Task/011` quedó cerrada de extremo a extremo.

---

## 5. Los siete hallazgos de la reconstrucción

> La reconstrucción se ejecutó siguiendo **únicamente** el runbook escrito. Cada paso que
> hizo falta y no estaba se registró **antes** de tocar la documentación. Son el riesgo que
> STAGE-07 nombra: *«pasos manuales no documentados que impiden reproducir el entorno»*.

| # | Hallazgo | Evidencia | Estado |
| --- | --- | --- | --- |
| **H-1** | §8 hacía `docker compose pull` sin acotar —falla para las cuatro imágenes propias— y **omitía `docker compose build`** | `pull access denied` ×4 y el aviso del propio Compose | **Corregido** |
| **H-2** | §8 **y §4** no creaban el bucket de medios, y `runtime_privileges.py --apply` **termina en exit 1** sin él | `NoSuchBucket` → crear bucket → **exit 0** | **Corregido** |
| **H-3** | *Defecto del propio entregable:* `python scripts/seed_local.py` no funcionaba | `ModuleNotFoundError: No module named 'app'` | **Corregido**, con regresión permanente |
| **H-4** | §8 no advertía de que `down -v` destruye `personal_blog_test`, sin la cual la suite **se omite entera** en vez de fallar | La base no existía tras la destrucción | **Corregido** |
| **H-5** | La recuperación total **no restauraba las identidades runtime** | §6 completa | **Corregido y revalidado** |
| **H-6** | La lista de «imágenes de terceros» de §4 incluía `postgres` y `traefik`, que **el proyecto construye** | `docker compose config`: solo `minio` y `portainer` declaran imagen sin `build` | **Corregido** |
| **H-7** | §9.1 y §9.2 copiaban a `/tmp` del contenedor, imposible desde `Task/018` | `Error response from daemon: container rootfs is marked read-only` | **Corregido** |

**Causa común de H-1, H-2, H-4, H-5, H-6 y H-7:** los runbooks son de `Task/003` y
`Task/004`; **`Task/010` añadió el bucket de medios y `Task/018` el endurecimiento y los
dos planos de identidad**, y ninguno actualizó los procedimientos de reconstrucción y
recuperación. No son descuidos de redacción: son procedimientos que quedaron atrás
respecto del entorno que describen, y **solo una reconstrucción real podía demostrarlo**.

H-6 y H-7 aparecieron **mientras se corregían** los anteriores: H-6 porque el primer
intento de corrección heredó la lista equivocada de §4, y H-7 al ejecutar por primera vez
la recuperación manual documentada.

---

## 6. H-5 — el hallazgo más serio, y su revalidación

### 6.1 El problema

`pg_dump` de una base **no exporta los roles**: son objetos *globales* del clúster. El
volcado sí exporta los `GRANT` que mencionan a `blog_runtime`. La copia de MinIO no
incluye su IAM, y `secrets/backend-runtime.env` está fuera del respaldo a propósito.

El runbook de backup **no mencionaba `blog_runtime` ni `runtime_privileges.py` en ninguna
parte**, y su §9.4 pasaba de «recrear el entorno» a «restaurar los tres componentes».
Siguiéndolo al pie de la letra se recuperan **todas las filas** y la aplicación **queda sin
poder leerlas**.

**El caso peor es el silencioso**, y así quedó documentado:

| Restauración | Qué se ve | Qué ocurre |
| --- | --- | --- |
| Con `--no-privileges`, que es lo que mandaba §9.1 | **Nada**, código 0 | Los `GRANT` ni se intentan; nada señala que el rol no existe |
| Sin `--no-privileges` | `role "blog_runtime" does not exist` ×17 y `errors ignored on restore: 17`, código 0 | Fallan uno a uno, contados como *ignorados* |

**El mecanismo ya existía**: `--reissue-runtime-credentials` está en el script desde
`Task/018`, descrito en su propia ayuda como *«el camino de recuperación tras restaurar un
respaldo»*. Lo que faltaba era que el runbook lo usara. **No se inventó una segunda forma
de provisionar**, y **no se creó ningún rol a mano**.

### 6.2 La revalidación — recuperación total real, A a J

Un entorno Compose paralelo no servía: `runtime_privileges.py` fija MinIO en
`127.0.0.1:9000` y el archivo runtime en `secrets/backend-runtime.env`, y los puntos E, F y
G exigen ese archivo y el contenedor `backend` reales. La validación fiel fue **ejecutar
§9.4 corregida sobre el entorno principal**, que es su escenario declarado: `down -v`
completo y recuperación desde el conjunto `20260913-000448`, verificado antes de usarlo.

Se dejó `secrets/backend-runtime.env` **a propósito** en el host, con sus credenciales ya
muertas: es exactamente lo que ocurre en una pérdida real, y es el caso que
`--reissue-runtime-credentials` debe resolver.

| # | Comprobación | Resultado |
| --- | --- | --- |
| **A** | Restore de PostgreSQL conforme | **17 tablas**, datos completos, código 0 |
| **B** | Restore de MinIO conforme | **6 objetos** con su `Content-Type` |
| **C** | Identidades reprovisionadas **por el procedimiento documentado** | `--reissue-runtime-credentials --apply`, **exit 0** |
| **D** | `blog_runtime` existe | `super=false createdb=false createrole=false login=true`; identidad MinIO `blog-runtime` **enabled**, política `blog-runtime-media` |
| **E** | El archivo runtime corresponde a las **nuevas** credenciales | Huella `4b028076…` → **`8c107c85…`** |
| **F** | El backend arranca con el plano runtime | `healthy`; DSN efectivo `postgresql://blog_runtime:***@postgres:5432/personal_blog` |
| **G** | `/ready` responde | **HTTP 200**, `{"status":"ready"}` — y `/ready` comprueba PostgreSQL **y** almacenamiento |
| **H** | `runtime_privileges.py` sin flags | **exit 0** |
| **I** | Mínimo privilegio vigente | *«SELECT permitido; UPDATE/DELETE de auditoría y DDL denegados realmente»* y *«listar global/bucket y administrar denegados»* |
| **J** | Sin errores de restore por rol inexistente | Restaurando **con** privilegios en una base de comprobación: **0** errores de rol, **0** *errors ignored*. Antes eran **17** |

**Y el entorno quedó operativo, no solo restaurado:** datos idénticos a los previos a la
pérdida, **login administrativo `200`** e imagen servida por enlace firmado con **4836
bytes**, los mismos de siempre.

*(La base de comprobación de J y el contenedor temporal se eliminaron; el área de paso
`/backup` quedó vacía.)*

---

## 7. Criterio 7 — Portainer

**Confirmado por el usuario el 2026-09-12.** No se aporta captura porque no se tomó
ninguna: se registra la confirmación tal cual.

- Los **6 contenedores** runtime aparecen *running*.
- **postgres, minio, backend, frontend y traefik**: *healthy*.
- **portainer**: *running* sin healthcheck, como se esperaba.
- Los **5 volúmenes** `personal-blog-local_*` están presentes.
- Los logs del backend se consultan desde Portainer → **O-07 verificado también en la
  interfaz**, que es lo que `Task/017` había dejado a la aprobación del usuario.

> **Precisión del usuario, incorporada:** `migrations` **no** cuenta como contenedor
> runtime persistente. Es el servicio del perfil `admin`, que se ejecuta con
> `run --rm` y desaparece al terminar. Los servicios persistentes son **seis**.

**Recorrido visual, también confirmado por el usuario:** tarjetas, imágenes, Markdown y
*embed* de vídeo correctos, y comportamiento conforme a **320, 390, 768 y 1280 px**. **No
observó ningún defecto de frontend** que justificara crear rama allí.

---

## 8. Validaciones ejecutadas

### 8.1 Backend

| Gate | Resultado |
| --- | --- |
| `ruff format --check .` | **316 files already formatted** |
| `ruff check .` | **All checks passed!** |
| `mypy .` | **Success: no issues found in 314 source files** |
| Suite completa `pytest -W error` | *(ver §8.4)* |
| Migraciones aplican | **`0003`, 17 tablas** sobre base vacía, dos veces |
| Migraciones revierten | Cubierto por `tests/integration/test_migrations.py`, dentro de la suite |
| Imagen Docker construye | `personal-blog-backend:local Built`, dos veces |

### 8.2 Frontend — sin modificaciones, gates ejecutados igual

| Gate | Resultado |
| --- | --- |
| `format:check` | **All matched files use Prettier code style!** |
| `lint` | Sin hallazgos |
| `typecheck` | Sin errores |
| `test:run` | **704 passed (75 archivos)** |
| `build` | **Correcto**, con las mismas variables que usa CI |

> **Un matiz que conviene registrar:** `npm run build` **falla sin
> `VITE_API_BASE_URL`**, con `«debe ser un origen HTTP(S) canonico sin credenciales»`. **No
> es una regresión**: es la validación de `Task/018`, y tanto CI como el `Dockerfile` la
> proporcionan. Al ejecutarla suelta en el host hay que darla, igual que hace CI.

> **Dos pruebas de frontend fallaron en un primer intento y pasaron al repetirlo**, sin
> cambio de código entre las dos ejecuciones. El primer intento corrió mientras la suite
> del backend se ejecutaba en paralelo, y el informe de Vitest registró
> `environment 314.95s`. Es un **comportamiento consistente con contención de recursos
> durante la ejecución paralela**; no se afirma como causa demostrada, porque no se aisló
> la variable.

### 8.3 Infraestructura

| Gate | Resultado |
| --- | --- |
| `docker compose config --quiet` | **Válido**, 6 servicios |
| Scripts PowerShell | **6 archivos, 0 fallos de parseo** |
| Scripts Python | **3 archivos compilan** |

### 8.4 Suite del backend — y una intermitencia que no se oculta

**Resultado final: `1874 passed, 1 skipped` en 419 s, código de salida 0**, con
`-W error` y contra **PostgreSQL y MinIO reales**. Las cuentas cuadran:
**1874 + 1 = 1875 = 1855 del baseline + 20 nuevas** (17 de la semilla, 3 de la
invocación). El *skip* es el estructural de Windows —`time.tzset` no existe—, ya
documentado desde `Task/017`.

**En una ejecución anterior falló una prueba, y se registra tal cual:**

```
FAILED tests/integration/test_concurrencia_del_texto_alternativo.py::
       test_dos_primeros_usos_con_el_mismo_texto_son_coherentes[perfil]
1 failed, 1873 passed, 1 skipped
```

Qué se comprobó antes de calificarla:

1. **Aislada pasa**: `5 passed` al ejecutar solo ese archivo.
2. **No hay residuos**: `profiles=0 administrators=0 media_assets=0 posts=0
   audit_events=0` en `personal_blog_test`, y `_preparar` además llama a `_limpiar`
   antes de empezar.
3. **No la puede causar la semilla**: los recolectores de pytest ordenan
   `test_concurrencia_del_texto_alternativo.py` **antes** que `test_seed_local.py`, y las
   pruebas de la semilla trabajan dentro de la transacción que la fixture revierte.
4. **Repetida, pasa**: la ejecución siguiente dio `1874 passed`, sin cambio de código.

La prueba lanza **dos conexiones reales** que compiten por un cerrojo de fila y exige que
**ambos** veredictos sean `ok`; cualquier error del cerrojo la incumple. El fallo se
produjo mientras esta sesión ejecutaba en paralelo la suite del frontend.

**Qué se afirma y qué no.** Lo demostrado es lo enumerado arriba: un fallo en una
ejecución, el caso aislado en verde, la suite completa posterior en verde, sin cambio de
código, y un riesgo de intermitencia ya conocido. Es un **comportamiento consistente con
contención de recursos durante la ejecución paralela** —igual que los dos *flakes* de
frontend de §8.2—, pero **no se declara esa causalidad como demostrada**: habría hecho
falta aislar la variable y reproducir el fallo a voluntad, y no se hizo.

**El riesgo de concurrencia de la suite de integración, abierto desde `Task/005.7`, sigue
abierto y no se declara resuelto.** Tampoco se toca la prueba: su expectativa fuerte es
deliberada, y relajarla para que no moleste sería exactamente lo que
[`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md) §9
prohíbe.

---

## 9. Datos que quedaron en el entorno

`administrators=1 profiles=1 posts=4 book_reviews=2 videos=2 projects=2 media_assets=3`,
6 objetos en `personal-blog-media`.

De los 4 artículos, **2 son borradores huérfanos** de dos intentos fallidos del guion de
validación —no del producto—: el primero omitía `summary`, que la validación de
publicación de `Task/012` exige (`409 cannot_publish_incomplete_draft`), y el segundo
repetía un título ya usado (`409 slug_already_exists`). **Las dos respuestas del API fueron
correctas.** Los borradores **no son visibles en el sitio público** ni en el sitemap, y no
se borran: no estorban a ninguna prueba y borrar por pulcritud sería una operación
destructiva sin necesidad.

---

## 10. Riesgos y decisiones que esta tarea NO cierra

| Elemento | Estado | Nota |
| --- | --- | --- |
| **D-21** / [ADR-009](../adr/ADR-009-rendering-strategy-for-crawlers.md) | **Abierta** · ADR en **Propuesta** | `Task/022` **aporta la evidencia con contenido real** que [`open-decisions.md`](../architecture/open-decisions.md) §6.4 pedía. **No elige** estrategia de *rendering* |
| **R-018-3** — residual de MinIO | **Abierto** | No se tocó el baseline ni la política S-09 |
| **R-021-1** — residual de Portainer | **Abierto** | Ídem |
| **R-018-4** — *buckets* residuales de prueba | **Abierto** | *Observado el 2026-09-12:* desaparecieron con `down -v`, y el respaldo posterior inspecciona **1** bucket en vez de 3. **El riesgo sigue abierto**: su causa —la limpieza del *harness* no sobrevive a un `SIGKILL`— no ha cambiado |

---

## 11. Deuda técnica pendiente

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | `runtime_privileges.py` fija MinIO en `127.0.0.1:9000` y el archivo runtime en una ruta única. Impide validar la recuperación en un entorno Compose paralelo sin tocar el script | sin propietario asignado |
| 2 | La recuperación de MinIO de §9.2 sigue siendo **manual objeto a objeto**. La lógica automatizada existe dentro de `Restore-LocalBackupTest.ps1`, pero solo para el entorno temporal | sin propietario asignado |
| 3 | Intermitencia de la suite de integración bajo contención | riesgo ya abierto desde `Task/005.7` |
| 4 | El `.gitignore` de `personal-blog-infra` **no cubre `__pycache__/`**, así que compilar los scripts Python —lo que hace el gate de `CI Infra`— ensucia `git status` en local. Observado y limpiado durante esta tarea; **no se corrige aquí** por estar fuera del alcance | sin propietario asignado |

---

## 12. Criterion 12 — estado duradero frente a transitorio

Barrido dirigido sobre los ocho documentos tocados, más los de estado, buscando
afirmaciones condenadas a volverse falsas.

| Clase | Resultado |
| --- | --- |
| **C** — estado transitorio escrito como vigente | **0**. Ninguna mención a un PR, a una rama remota o a una normalización como situación actual. Todo lo observado va **fechado**: *«Observado el 2026-09-12»* |
| **D** — contradicciones en el estado vigente | **0**. Avance **21/41 ≈ 51 %** coherente en STATUS y ROADMAP; ETAPA 07 descrita igual en los tres sitios; `Task/022` como **Lista para validación** en STATUS, ROADMAP, STAGE-07 y la ficha |

Comprobado además que **no queda vigente** ninguna frase que la ejecución ya resolvió:

- *«pendiente de comprobación en Portainer»* — sustituida por la confirmación del usuario,
  fechada.
- *«pendiente de recorrido visual»* — ídem.
- *«H-5 abierto»* — H-5 figura **Resuelto y revalidado**, con su evidencia A–J.

**Los fallos se conservan como hechos históricos fechados**, no se borran: los siete
hallazgos con su síntoma literal, los 17 errores de `pg_restore`, el RED de la semilla, el
`ModuleNotFoundError` de H-3, los dos `409` del guion de validación y la prueba
intermitente de concurrencia. Un reporte del que desaparecen los tropiezos deja de servir
para entender por qué el procedimiento es como es.

---

## 13. Estado de la tarea

**Aprobada** el **2026-09-12** por el usuario mediante
`approved: Task/022-Validacion-Local-Production-Like`.

Con esa aprobación:

- **Cuenta en las 41 tareas**: el avance pasa de **21/41 ≈ 51 %** a **22/41 ≈ 54 %**.
- **ETAPA 07 — Validación Local queda Completada**, con **1 de 1 tarea aprobada (100 %)**
  y su hito alcanzado: *Blog validado íntegramente en local. Puerta de entrada a la nube.*
- **T-07 queda Satisfecho** y **Vigente**.
- Las decisiones **D-022-A** a **D-022-E** pasan de *Propuesta* a **Vigentes**.

Lo que la aprobación **no** cambia: **D-21** sigue **Abierta** y **ADR-009** en
**Propuesta**; **R-018-3**, **R-021-1** y **R-018-4** siguen **Abiertos**. Que la ETAPA 07
esté completada **no autoriza acciones cloud**: la primera es de la ETAPA 09, y
`Task/023-Compatibilidad-FastAPI-Lambda` queda **Pendiente, no iniciada**.
