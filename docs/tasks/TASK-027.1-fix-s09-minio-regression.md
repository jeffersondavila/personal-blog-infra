# TASK-027.1 — Corregir la regresión S-09 de MinIO

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/027.1-Corregir-Regresion-S09-MinIO` |
| **Nombre** | Corregir la regresión S-09 de MinIO |
| **Tipo** | **Mantenimiento correctivo de seguridad (S-09)** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas y no altera el avance global |
| **Estado** | **Aprobada** — addendum Floci aprobado el **2026-09-21**; aprobación del alcance MinIO del 2026-09-20 conservada como historia |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/027.1-Corregir-Regresion-S09-MinIO` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | **`67c1904`** (`= main = origin/main` al crearla el 2026-09-17) |
| **Fecha de inicio** | 2026-09-17 (Guatemala) |
| **Última actualización** | 2026-09-21: segunda aprobación y publicación del addendum, §22 |
| **Fecha de aprobación del alcance original** | **2026-09-20**; no autoriza publicar el addendum |
| **Expresión de la primera aprobación (2026-09-20)** | `approved: Task/027.1-Corregir-Regresion-S09-MinIO` |
| **Reporte** | [TASK-027.1-report.md](../task-reports/TASK-027.1-report.md) |
| **Publicación de la imagen** | **Publicada** en GHCR el 2026-09-19, bajo autorización humana acotada que **no** equivale a aprobar la tarea. RepoDigest remoto verificado: `sha256:84c67632…059129`. Paquete **PRIVADO**; visibilidad **no modificada** |

---

## 0. Preparación Git — historia del 2026-09-17 a la primera aprobación

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | Resultado real |
| --- | --- | --- |
| 1 | Rama activa | `Task/027.1-Corregir-Regresion-S09-MinIO` |
| 2 | Rama creada **desde `main`** | Sí |
| 3 | `git rev-parse HEAD` == `git rev-parse main` | **coinciden** (`67c1904`) |
| 4 | `git rev-list --count main..HEAD` | **0** — la rama no tiene commits propios |
| 5 | Commits de esta tarea | **ninguno.** Los cambios permanecen sin *commit*, según las instrucciones del proyecto §6 |
| 6 | `personal-blog-backend` / `personal-blog-frontend` | en `main`, limpios, **sin rama Task** |

En la preparación del 2026-09-17, `main` no contenía el entregable de Task/027.
Esta tabla es histórica: después se publicaron `7e7d56e`, `6890ded` y `df3ba33`.
La observación Git del addendum y la estrategia posterior están en §21.

---

## 1. Objetivo

Eliminar la única vulnerabilidad **accionable y corregible** que quedaba en la imagen de
MinIO del entorno local —`CVE-2026-79921` en `github.com/rabbitmq/amqp091-go v1.10.0`—
sin abandonar el release Community aceptado, sin relajar la política S-09 y sin
generalizar la excepción `accepted-baseline` a las imágenes que construye el proyecto.

## 2. Contexto — por qué existe esta tarea

`Task/021` dejó el residual de MinIO bajo **R-018-3** con **100** hallazgos accionables
aceptados por identidad exacta y ligados al digest. Ese conjunto se aceptó porque la imagen
fijada ya era la última publicada del release y **no existía actualización que eliminara el
residual**.

Una de esas 100 identidades sí tenía corrección disponible **aguas arriba del binario, no
de la imagen**: `amqp091-go` publicó `v1.13.0`. Mantenerla aceptada equivalía a tratar como
irremediable algo que sí se podía corregir reconstruyendo el binario desde el commit exacto
del release ya aceptado.

Esta tarea **no reabre `Task/021`** ni reinterpreta su aprobación: corrige el residual que
dejó de ser irremediable.

## 3. Dentro del alcance

- [x] Reconstruir `/usr/bin/minio` desde el **commit exacto** del release
      `RELEASE.2025-09-07T16-13-09Z` con un único cambio de dependencia.
- [x] Conservar **byte a byte** el resto del runtime oficial: sistema operativo, `mc`,
      *entrypoint*, configuración, permisos y los 9 *layers* heredados.
- [x] Demostrar que la construcción es **reproducible**: manifest, config, *layers*,
      *diff IDs* y binario idénticos en construcciones independientes.
- [x] Producir **SBOM canónico** y **procedencia** deterministas.
- [x] Atar el baseline al manifiesto de construcción con un **atestado nominal**, no con
      una política nueva ni con una capacidad genérica.
- [x] Extender `CI Infra` para construir, verificar, escanear y atestar el derivado.
- [x] Dejar el residual en **99** identidades, sin ninguna nueva.

## 4. Fuera del alcance

- **Hacer público el paquete de GHCR.** La imagen **ya está publicada** —el 2026-09-19, con
  autorización acotada— pero el paquete sigue **PRIVADO** y su visibilidad no se toca.
  El cierre del 2026-09-20 publicó el código correspondiente esencial; SBOM y
  procedencia junto a la imagen siguen pendientes (DT-027.1-1).
  *(Hasta el 2026-09-18 esta línea decía que publicar era lo único pendiente para que la
  referencia del Compose fuera resoluble: cierto entonces, resuelto ya.)*
- Cambiar el release de MinIO, su configuración, sus credenciales o su topología.
- Tocar el stack `personal-blog-local` en ejecución.
- Relajar la tolerancia cero de `postgres` y `traefik`, o extender `accepted-baseline` a
  cualquier imagen propia.
- Resolver `R-018-3`: sigue **ABIERTO** con 99 identidades.
- `Task/027` y `Task/028`: intactas.

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Receta de construcción del derivado | infra | `docker/minio/Dockerfile` |
| Parche de dependencia (`go.mod`, `go.sum`) | infra | `docker/minio/minio-amqp091-go-1.13.0.patch` |
| Manifiesto de construcción con todas las identidades | infra | `docker/minio/build-manifest.json` |
| Nota de gobernanza y licencia | infra | `docker/minio/README.md` |
| Verificador, atestador, SBOM canónico, procedencia y comparador | infra | `scripts/minio/artifact.py` |
| Gobernanza fail-closed del derivado | infra | `tests/security/test_minio_derivative.py` |
| Contrato del builder OCI del workflow | infra | `tests/security/test_workflow_build_drivers.py` |
| Atestado nominal en el comparador S-09 | infra | `scripts/security/vulnerability_gate.py` |
| Baseline con 99 identidades y atestado | infra | `security/vulnerability-baseline.json` |
| Gates de construcción, escaneo, SBOM y procedencia | infra | `.github/workflows/ci-infra.yml` |
| Referencia de la imagen | infra | `.env.example`, `docker-compose.yml` |

## 6. Criterios de aceptación

1. El binario del derivado enlaza `amqp091-go v1.13.0` y presenta **0** hallazgos
   accionables de ese paquete. **Cumplido.**
2. Solo cambia `/usr/bin/minio`: el resto del runtime es idéntico al de la base fijada.
   **Cumplido y exigido por el verificador.**
3. Dos construcciones independientes producen la **misma** identidad OCI. **Cumplido.**
4. El gate S-09 compara **99** identidades exactas y **0** nuevas. **Cumplido.**
5. `postgres` y `traefik` conservan **tolerancia cero**. **Cumplido.**
6. El atestado **no** es una política nueva ni aplicable a otra clave del baseline.
   **Cumplido, con control negativo.**
7. Los gates locales aplicables de `CI Infra` pasan sobre el estado final. **Cumplido.**
8. Los recursos temporales de la tarea quedan eliminados y el stack principal intacto.
   **Cumplido.**
9. La identidad de publicación queda descrita **sin afirmar de más**. **Cumplido**, y desde
   el 2026-09-19 **verificada contra el registro**: el RepoDigest remoto coincide
   exactamente con el manifiesto OCI esperado, comprobado además recalculando el `sha256`
   del manifiesto crudo descargado de GHCR.
10. La referencia de `.env.example` **resuelve** contra el registro. **Cumplido**, con un
   *pull* aislado que devolvió el mismo digest y que después se eliminó.

## 7. TDD / Plan test-first

**No aplica en el modo backend.** Esta tarea no toca `personal-blog-backend` ni su dominio,
casos de uso, API, persistencia, autenticación o auditoría, de modo que la
[BACKEND TESTING STRATEGY](../project-management/BACKEND_TESTING_STRATEGY.md) no la
gobierna.

Sí se aplicó su principio equivalente en la capa que sí toca: la gobernanza del derivado se
escribió como pruebas **antes** de aceptar el resultado, e incluye **controles negativos**
que demuestran que el gate falla cuando debe fallar.

| Control negativo | Qué demuestra |
| --- | --- |
| `test_attestation_is_not_a_generic_baseline_option` | El atestado aplicado a otra clave del baseline es **rojo** |
| `test_repository_coherence_rejects_a_changed_manifest_hash` | Manipular el `sha256` del manifiesto es **rojo** |
| `test_only_previously_accepted_99_risks_remain` | El conjunto es 99 y `CVE-2026-79921` ya no está |
| `test_project_images_still_have_zero_tolerance` | `postgres` y `traefik` siguen en tolerancia cero |
| `test_baseline_is_bound_to_exact_build_manifest` | Baseline, referencia y digest coinciden con el manifiesto |

## 8. Plan de validación

Cada criterio se comprueba con el mecanismo que el propio proyecto fija, no con
herramientas ad hoc: el lanzador del laboratorio para Terraform, el verificador OCI para la
identidad de la imagen y el comparador S-09 para el residual.

## 9. Comandos de validación

```bash
# Terraform — mecanismo fijado por el proyecto, sin instalación global
python scripts/laboratorio/laboratorio.py --modo local herramientas
terraform version
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform validate

# Suites y coherencia
python -B -m unittest discover -s tests/security -p 'test_*.py'
python -B -m unittest discover -s tests/laboratorio -p 'test_*.py'
python scripts/security/vulnerability_gate.py --baseline security/vulnerability-baseline.json --comprobar-coherencia .

# Compose
docker compose --env-file .env.example --profile admin config --quiet
docker compose --file laboratorio/docker-compose.laboratorio.yml --env-file laboratorio/.env.laboratorio.example config --quiet

# Identidad del derivado y gate S-09
python scripts/minio/artifact.py --manifest docker/minio/build-manifest.json --root . verify --oci <ruta>/minio.oci.tar
python scripts/security/vulnerability_gate.py --baseline security/vulnerability-baseline.json --reports <directorio-de-informes>
```

## 10. Evidencia esperada

Identidad OCI reproducida, informe Trivy atestado, SBOM canónico, procedencia y el
resultado completo del gate S-09. Todo ello consta en el
[reporte](../task-reports/TASK-027.1-report.md) §3 a §7.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | ~~La referencia del Compose apunta a una imagen todavía no publicada~~ — **materializado y resuelto** el 2026-09-19 | Era alto para un `up` limpio | **Cerrado.** La imagen se publicó y la referencia resuelve; se comprobó con `manifest inspect` y un *pull* aislado. El stack en ejecución **no** se tocó y sigue con la imagen original |
| 2 | Tratar el derivado como precedente para aceptar residuales en imágenes propias | Alto para S-09 | El atestado es **nominal**: solo la clave `minio`. Hay control negativo que lo demuestra |
| 3 | Distribuir la imagen sin el código correspondiente | Legal (AGPL-3.0) | `docker/minio/README.md` exige commit, parche, Dockerfile, manifiesto, SBOM y procedencia junto a la distribución |
| 4 | Confundir reproducibilidad con hermeticidad | Medio | Declarado sin adornos: la construcción **usa red**; lo demostrado es la **identidad verificada** de todo lo que descarga (D-027.1-E) |
| 5 | ~~Divergencia entre el manifiesto OCI local y el RepoDigest que asigne GHCR~~ — **descartado por medición** | Era medio | **No se produjo.** GHCR conservó `mediaType` OCI, config y los 10 layers; el digest remoto es idéntico al esperado (reporte §9) |

## 12. Decisiones técnicas

| Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- |
| **D-027.1-A** Reconstruir solo el binario sobre la base oficial | Cambiar de release; construir la imagen entera desde cero | Conserva el release ya aceptado y los 9 *layers* oficiales; reduce la superficie del cambio a un archivo | No |
| **D-027.1-B** Atestado **nominal** ligado a la clave `minio` | Cuarta política de baseline; campo genérico | Una política genérica habría creado la puerta que S-09 evita; el atestado no es configurable para otra imagen | No |
| **D-027.1-C** Baseline atado al `sha256` del manifiesto de construcción | Confiar solo en el digest de la imagen | Ata baseline → manifiesto → Dockerfile → parche, y cualquier edición rompe la cadena | No |
| **D-027.1-D** SBOM y procedencia **canonizados** antes de comparar | Comparar la salida cruda de Trivy | La salida cruda lleva `serialNumber`, marcas de tiempo y `bom-ref` aleatorios: sin canonizar, dos SBOM equivalentes nunca coincidirían | No |
| **D-027.1-E** Describir el resultado como **reproducible con identidades fijadas**, no como *hermético* ni *offline* | Llamarlo build hermético | La construcción **descarga** fuente y módulos por red; lo demostrado es que cada identidad está fijada y verificada, no que no haya red | No |
| **D-027.1-F** No publicar en GHCR dentro de esta tarea | Publicar y cerrar | Publicar es una acción externa e irreversible; la sección 9 de las instrucciones del proyecto la reserva al usuario | No |

Todas pasan a **Aceptadas y Vigentes** con la aprobación del 2026-09-20, **sin ADR nuevo**:
ninguna altera una decisión arquitectónica aceptada. `D-027.1-F` se conserva con su matiz —
publicar exigió autorización humana explícita, que se concedió de forma acotada el
2026-09-19, separada de la aprobación de la tarea.

## 13. Documentación creada o actualizada

- `docs/tasks/TASK-027.1-fix-s09-minio-regression.md` — esta ficha (**creada**).
- `docs/task-reports/TASK-027.1-report.md` — reporte de la tarea (**creado**).
- `docs/project-management/STATUS.md` — mantenimiento en curso y **R-018-3** actualizado.
- `docs/project-management/ROADMAP.md` — registro del mantenimiento fuera de las 41.
- `docker/minio/README.md` — gobernanza y licencia del derivado (**creado**).

## 14. Archivos modificados

| Repositorio | Archivo | Acción |
| --- | --- | --- |
| infra | `.env.example` | modificado |
| infra | `docker-compose.yml` | modificado |
| infra | `.github/workflows/ci-infra.yml` | modificado |
| infra | `scripts/security/vulnerability_gate.py` | modificado |
| infra | `security/vulnerability-baseline.json` | modificado |
| infra | `tests/security/test_pinned_artifact_policy.py` | modificado |
| infra | `tests/security/test_vulnerability_gate.py` | modificado |
| infra | `docker/minio/Dockerfile` | creado |
| infra | `docker/minio/README.md` | creado |
| infra | `docker/minio/build-manifest.json` | creado |
| infra | `docker/minio/minio-amqp091-go-1.13.0.patch` | creado |
| infra | `scripts/minio/artifact.py` | creado |
| infra | `tests/security/test_minio_derivative.py` | creado |
| infra | `docs/tasks/TASK-027.1-fix-s09-minio-regression.md` | creado |
| infra | `docs/task-reports/TASK-027.1-report.md` | creado |
| infra | `docs/project-management/STATUS.md` | modificado |
| infra | `docs/project-management/ROADMAP.md` | modificado |

## 15. Resultado de pruebas

El detalle por gate, con cifras exactas, está en el
[reporte](../task-reports/TASK-027.1-report.md) §3. Resumen: **todos los gates locales
aplicables en verde**, sin ninguno parcial presentado como completo.

## 16. Problemas encontrados

1. **Terraform no estaba en `PATH`.** Se resolvió con el **lanzador fijado del proyecto**
   (`scripts/laboratorio/laboratorio.py --modo local herramientas`), que verifica identidad
   y versión contra las constantes del repositorio. **No se instaló ninguna versión global
   ad hoc.**
2. **Trivy en Windows no inventaría un ELF sin bit de ejecución.** El escaneo del binario de
   Terraform se replicó **dentro de un contenedor Linux**, que es el entorno del CI, con el
   artefacto `linux_amd64` verificado por su `sha256` fijado. Detalle en el reporte §3.
3. **La referencia apuntaba a un GHCR vacío — resuelto el 2026-09-19.** Durante la fase de
   implementación, `.env.example` apuntaba a una imagen que no existía, así que un
   `docker compose up` limpio no habría podido resolverla. Con la publicación autorizada,
   la referencia **resuelve**: se comprobó con `docker manifest inspect` y con un *pull*
   aislado que devolvió el mismo digest y que después se eliminó. El stack en ejecución
   **no se tocó ni se recreó** y sigue sirviendo con la imagen original.
5. **Un primer intento de publicación fue rechazado.** El 2026-09-19, antes de que existiera
   credencial de registro en este perfil, el `push` devolvió `denied`. No publicó nada; la
   imagen cargada para intentarlo se eliminó. Se resolvió cuando el usuario registró la
   credencial, y entonces el `push` se completó.
6. **`Task/027` y esta tarea tocan los mismos documentos de gestión.** La instrucción
   del usuario del 2026-09-21 fija el cierre por fases de §21: después de aprobar y publicar
   027.1, otra autorización permitirá integrarla completa en 027 mediante `merge --no-ff`.
   Los conflictos se resolverán semánticamente, conservando ambos alcances, sin `ours`
   o `theirs` global. Reconocer la aprobación de Task/027 no adelanta esa integración.

## 16b. Addendum — 2026-09-20: portabilidad del CI

Hecho histórico del **2026-09-20**, posterior a la primera aprobación, publicado en
`df3ba33`. El PR #48 fue cerrado después sin merge; su cierre se fecha en §21.
**No reescribe la evidencia anterior.**

`CI Infra` quedó rojo al integrar la tarea en `dev`: `docker buildx build --output type=oci`
cayó en el builder `default` del runner, cuyo **driver `docker` no implementa exportadores**
(«OCI exporter is not supported for the docker driver»). Postgres y Traefik construyeron
bien; falla solo el paso del derivado.

Localmente no se detectó porque allí se usaron builders `docker-container` explícitos y el
*image store* de containerd: dos motivos para funcionar que el runner no tiene.

**Corrección mínima:** un builder aislado `minio-oci`, driver `docker-container`, con la
imagen de BuildKit fijada por **digest del índice multi-arquitectura**
(`moby/buildkit@sha256:28a898…41d8`, **v0.32.2**, la misma que produjo la identidad
verificada), **sin `--use`**, retirado con un `trap` que conserva el código de salida real.
Los `docker build` de Postgres y Traefik **no se tocan**.

**No cambia nada de la identidad:** una cuarta construcción sin caché y con `--pull` devolvió
el mismo `manifest_digest`, `config_digest`, binario, y el mismo número y orden de layers;
`artifact.py compare` da `"reproducible": true`. `build-manifest.json`, el baseline, el
Dockerfile, el parche y la imagen publicada en GHCR quedan **intactos**.

**Regresión añadida:** `tests/security/test_workflow_build_drivers.py`, 14 pruebas con cinco
controles negativos demostrados. Detalle en el
[reporte §12b](../task-reports/TASK-027.1-report.md).

## 17. Pasos históricos de validación — antes de la primera aprobación

Estos comandos y expectativas son historia del 2026-09-18/20. Para validar el addendum
sobre los commits ya publicados, usar §21; no se espera `main..HEAD == 0`.

```powershell
# 1. La rama es la correcta y no tiene commits propios
git -C personal-blog-infra rev-parse --abbrev-ref HEAD
git -C personal-blog-infra rev-list --count main..HEAD     # 0

# 2. El stack principal sigue healthy y con la imagen original
docker ps --format "{{.Names}} {{.Image}} {{.Status}}"
docker inspect personal-blog-local-minio --format "{{.Config.Image}}"

# 3. No quedan recursos temporales de la tarea
docker ps -a --format "{{.Names}}" | Select-String task0271
docker volume ls --format "{{.Name}}" | Select-String task0271
docker images --format "{{.Repository}}:{{.Tag}}" | Select-String task0271
docker buildx ls | Select-String task0271

# 4. El residual es 99 y la tolerancia cero sigue intacta
python -B -m unittest discover -s tests/security -p "test_*.py"
python scripts/security/vulnerability_gate.py --baseline security/vulnerability-baseline.json --comprobar-coherencia .
```

## 18. Deuda técnica pendiente

| # | Deuda | Propietario |
| --- | --- | --- |
| **DT-027.1-1** | ~~Publicar el derivado en GHCR~~ — **HECHO** el 2026-09-19 y verificado. ~~Material AGPL solo en local~~ — **resuelto por este cierre**: el commit del 2026-09-20 versiona `Dockerfile`, parche, `build-manifest.json`, `README.md` y `artifact.py`, y el *push* los publica en `jeffersondavila/personal-blog-infra`, que es un repositorio **público**. **Lo que queda:** SBOM y procedencia se **generan** en CI pero **no se publican como artefactos junto a la imagen**; conviene resolverlo antes de hacer público el paquete | Usuario |
| **DT-027.1-2** | **R-018-3 sigue ABIERTO** con 99 identidades. El derivado no lo cierra | `Task/039` y revisiones de S-09 |
| **DT-027.1-3** | La construcción obtiene fuente y módulos **por red**. Un mirror o caché verificada acercaría la hermeticidad real | Sin tarea asignada |

## 19. Próxima tarea

**Ninguna se inicia.** `Task/027` permanece **Aprobada**; avance **27/41 ≈ 66 %**,
ETAPA 09 **1/3 ≈ 33 %**. `Task/028` permanece **Pendiente, no iniciada**. Esta tarea
no suma avance ni autoriza avanzar.

## 20. Primera aprobación — historia del alcance MinIO (2026-09-20)

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-20** |
| **Aprobado por** | **el usuario** (`jeffersondavila`) |
| **Expresión de la primera aprobación (2026-09-20)** | `approved: Task/027.1-Corregir-Regresion-S09-MinIO` |

Con aquella primera aprobación (no cubre el addendum posterior):

- las decisiones **D-027.1-A** a **D-027.1-F** pasan a **Aceptadas y Vigentes**, sin ADR nuevo;
- **el avance NO cambia**, porque el mantenimiento no cuenta entre las 41 tareas; la cifra
  vigente la fija la última tarea canónica aprobada;
- **`R-018-3` sigue ABIERTO** con 99 identidades;
- **`Task/027` conserva su aprobación** del 2026-09-17;
- **`Task/028` sigue no iniciada**;
- **la visibilidad del paquete de GHCR NO cambia**: sigue **privado**.

## 21. Addendum Floci / regresión S-09 descubierta durante el cierre de Task/027.1

**Implementado el 2026-09-20 (Guatemala); reconciliado y APROBADO el 2026-09-21.**
El usuario amplió expresamente este mantenimiento, siguiendo el precedente de
`Task/020.3`: un gate de cierre reveló un defecto independiente. No se crea `Task/025.1`,
otra maintenance ni una tarea canónica nueva. La aprobación de §20 pertenece al alcance
original y **no autorizaba** commit/push del addendum; la segunda aprobación, registrada
en §22, sí lo autoriza —y solo eso—.

### Alcance entregado

- [x] Floci **2.0.1 → 2.1.0**, digest del índice OCI verificado remotamente y
      plataforma `linux/amd64` explícita.
- [x] Healthcheck sin curl ni paquetes nuevos: Bash `/dev/tcp`, HTTP 200 y seis
      servicios `running`; controles negativos por estado HTTP, servicio ausente,
      servicio detenido y servicio inexistente.
- [x] Baseline **70 → 2** por intersección exacta con las identidades históricas:
      **68 retiradas, 0 añadidas**. Las siete regresiones de 2.0.1 desaparecen.
- [x] H-025-1 cerrada técnicamente: `PutParameter` conserva Tags; segundo plan **exit 0**.
      Se retira del lanzador la tolerancia a `tags_all`; una regresión vuelve a fallar.
- [x] Parser API Gateway aislado y compatible con camelCase/PascalCase. JSON/HTTP
      inválidos abortan; un API existente hace fallar la prueba de ausencia.
- [x] S-11: plan/apply de 21 recursos, readback, Lambda cold real y segunda invocación,
      API → Lambda, Logs, aislamiento, destroy y ausencia incluyendo API Gateway.
- [x] Hallazgo adicional de S-11: el DNS de Floci reenviaba consultas externas desde
      Lambda. Compose confina los resolutores a loopback IPv6 y desactiva fallback
      público. Se comprueba **desde el contenedor Lambda real**, no solo con una sonda
      genérica de la red. El gate CI de puertos usa el modelo JSON de Compose para no
      confundir la dirección DNS `::1` con un puerto publicado.
- [x] S-09 completo y gates locales aplicables. MinIO **99/99**, misma identidad GHCR,
      sin reconstrucción, modificación de receta/parche/manifiesto ni publicación.
- [x] Documentación y limpieza de recursos temporales; stack principal intacto.

### Decisiones del addendum — Aceptadas y Vigentes desde el 2026-09-21

Consumir el release estable 2.1.0 por digest; reducir exclusivamente el riesgo histórico;
exigir convergencia literal de SSM; usar Bash disponible en la imagen; cerrar el reenvío
DNS del laboratorio; interpretar el inventario API sin falsos negativos. Ninguna cambia
la arquitectura: **Floci solo se ejecuta en local, nunca se despliega a AWS; producción
usa AWS real**. No se declara paridad completa.

Con la aprobación del **2026-09-21** pasan de **Propuesta** a **Aceptadas y Vigentes**,
**sin ADR nuevo**: ninguna altera una decisión arquitectónica aceptada (§22).

El [reporte §14](../task-reports/TASK-027.1-report.md#14-addendum-floci--regresión-s-09-descubierta-durante-el-cierre-de-task0271)
contiene digests, mediciones, fallos intermedios, gates, limpieza y límites.

### Validación y punto de detención

```powershell
git branch --show-current  # Task/027.1-Corregir-Regresion-S09-MinIO
git rev-parse HEAD         # df3ba33777058f6cbad1747e3d695c09e7a74fee
git diff --cached --stat   # vacío
git diff --check
python -B -m unittest discover -s tests/security -p "test_*.py"
python -B -m unittest discover -s tests/laboratorio -p "test_*.py"
python scripts/security/vulnerability_gate.py --baseline security/vulnerability-baseline.json --comprobar-coherencia .
docker compose -f laboratorio/docker-compose.laboratorio.yml --env-file laboratorio/.env.laboratorio.example config --quiet
```

Los comandos históricos de §17 describen la fase original anterior a sus commits.
**Observado el 2026-09-21:** HEAD `df3ba33`, tres commits anteriores publicados;
addendum local sin commit y staging vacío. La comprobación de HEAD anterior es una
observación de esta fase, no una constante para cierres futuros.

**Observado el 2026-09-21:** el usuario cerró sin merge los
[PR #47](https://github.com/jeffersondavila/personal-blog-infra/pull/47) y
[PR #48](https://github.com/jeffersondavila/personal-blog-infra/pull/48), con `closedAt`
`2026-09-21T02:38:32Z` y `2026-09-21T02:38:38Z`, respectivamente, y `mergedAt=null`
en ambos. El cierre ocurrió el 2026-09-20 en Guatemala. Es un hecho histórico;
Git/GitHub son la fuente viva de ramas, PR y checks.

**Punto de detención 1 — cumplido y superado.** Aquella fase terminó sin commit, push,
merge, cambio a Task/027 ni PR, con la tarea **Lista para validación**. La aprobación del
**2026-09-21** (§22) la cierra y habilita el **punto de detención 2**. Task/027 conserva su
aprobación: **27/41 ≈ 66 %**, ETAPA 09 **1/3 ≈ 33 %**. Task/028 no se inicia. Los gates
locales **no** equivalen a una ejecución remota del addendum.

Por instrucción expresa del usuario, la [estrategia de cierre por fases](../task-reports/TASK-027.1-report.md#15-reconciliación-documental-y-estrategia-de-cierre--2026-09-21)
prevalece para este cierre: tras `approved: Task/027.1-Corregir-Regresion-S09-MinIO`,
commit y push de 027.1, verificar remoto y **detenerse sin PR ni integración en dev**.
Solo otra autorización permitirá consolidar todo su historial en 027 mediante
`merge --no-ff`, conservar todo el alcance cloud aprobado y validar el árbol combinado.
La entrega final será un único PR nuevo `Task/027 → main`; no reabrir #47/#48 ni crear
otro PR de 027.1. Solo el usuario fusiona hacia main.

---

## 22. Segunda aprobación — addendum Floci (2026-09-21)

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-21** (Guatemala) |
| **Aprobado por** | **el usuario** (`jeffersondavila`) |
| **Expresión de la aprobación** | `approved: Task/027.1-Corregir-Regresion-S09-MinIO` |
| **Alcance que cubre** | El **addendum Floci** de §21. La aprobación del 2026-09-20 cubre el alcance MinIO de §20 y se conserva como historia |

Con esta aprobación:

- Las **decisiones del addendum** pasan de **Propuesta** a **Aceptadas y Vigentes**,
  **sin ADR nuevo**: ninguna altera una decisión arquitectónica aceptada.
- **El avance NO cambia.** `Task/027.1` es mantenimiento y **no cuenta entre las 41**:
  sigue **27/41 ≈ 66 %** y **ETAPA 09 1/3 ≈ 33 %**, cifras que fija `Task/027`.
- **H-025-1** queda **cerrada técnicamente**; **H-025-6** sigue **ABIERTA** con dos
  identidades exactas; **H-025-7** conserva sus nueve; **R-018-3** sigue **ABIERTO** con
  99 identidades.
- `Task/027` conserva su aprobación del 2026-09-17 y `Task/028` **no se inicia**.
- **La visibilidad del paquete de GHCR NO cambia:** sigue **privado**, sin reconstruir ni
  republicar la imagen.
- **Floci sigue siendo laboratorio local** y lo observado en él sigue siendo **hipótesis**
  hasta la ETAPA 10 (ADR-006). **No se declara paridad completa.**

### Punto de detención 2 — lo único autorizado por esta aprobación

Por instrucción expresa del usuario, esta aprobación **sustituye el cierre ordinario de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) para esta entrega** y autoriza
**únicamente**:

1. Registrar documentalmente la aprobación y promover las decisiones del addendum.
2. Ejecutar las validaciones finales.
3. Crear los commits del addendum sobre `Task/027.1-Corregir-Regresion-S09-MinIO`.
4. Publicar esa rama en `origin` y **verificar su SHA remoto**.

**No autoriza:** crear un pull request, reabrir #47/#48, integrar en `dev`, cambiar a
`Task/027`, consolidar mediante `merge --no-ff`, tocar `main` ni iniciar `Task/028`.
Esa consolidación exige **otra autorización**, descrita en el
[reporte §15](../task-reports/TASK-027.1-report.md#15-reconciliación-documental-y-estrategia-de-cierre--2026-09-21).
**Solo el usuario fusiona hacia `main`.**

Esta excepción **no** cambia cómo nacen las ramas Task: toda Task sigue naciendo de `main`
actualizado y limpio ([WORKFLOW §2.1](../project-management/WORKFLOW.md)).

La evidencia de ejecución de esta fase está en el
[reporte §16](../task-reports/TASK-027.1-report.md#16-segunda-aprobación-y-publicación-del-addendum--2026-09-21).
