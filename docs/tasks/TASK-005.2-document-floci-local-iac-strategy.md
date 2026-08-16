# TASK-005.2 — Documentar la estrategia de IaC local con Floci

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Nombre** | Documentar la estrategia de IaC local (AWS Local Parity) |
| **Tipo** | **Mantenimiento de arquitectura y gobierno documental** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**5 de 41**) ni la ETAPA 02 (**1 de 3**) |
| **Etapa de referencia** | Afecta al alcance futuro de la [ETAPA 08](../stages/STAGE-08-cloud-ready.md), con reflejo en las [ETAPA 10](../stages/STAGE-10-cloud-deployment.md) y [ETAPA 11](../stages/STAGE-11-deployment-automation.md) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/005.1-Formalizar-TDD-Backend` — **Aprobada** ✔ (2026-08-13), PR `#7` **fusionado** y normalización `main → dev` **completada** el 2026-08-15 |
| **Rama** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local`, creada desde `dev` normalizado (`4e6bfaa`). **Publicada en el cierre** |
| **Fecha de inicio** | 2026-08-15 |
| **Fecha de aprobación** | 2026-08-15 |
| **Última actualización** | 2026-08-15 — cierre aprobado |
| **Próxima tarea** | `Task/006-Fundacion-Frontend-React` — **Pendiente, no iniciada** |

---

## 1. Objetivo

Formalizar, por escrito y de forma versionada, esta meta:

> **La infraestructura AWS del proyecto debe poder desarrollarse, aprenderse,
> provisionarse y destruirse localmente con la mayor fidelidad razonable antes de gastar
> en AWS real.**

Y hacerlo **antes** de que `Task/025` escriba el primer archivo `.tf`, porque la decisión
condiciona cómo se escribe Terraform desde la primera línea.

El resultado es un documento canónico —
[`docs/architecture/aws-local-parity.md`](../architecture/aws-local-parity.md) — más un ADR
en estado **Propuesta** y las referencias necesarias en roadmap, estado, fichas de etapa,
documentos de arquitectura, límites de seguridad e instrucciones de Claude.

## 2. Contexto

La ETAPA 08 compromete hoy a `Task/025-Terraform-Cloud` únicamente a `terraform fmt -check`
y `terraform validate`. Eso comprueba **sintaxis, no comportamiento**: no crea nada, no
ejercita permisos y no demuestra que `apply` o `destroy` funcionen.

Consecuencia: el **primer `apply` real ocurriría en producción**, con cuenta AWS creada y
costo corriendo, sobre una IaC que nunca se ejecutó. El propio riesgo ya estaba escrito en
la ficha de la etapa —*«Terraform validado en seco que falla en el primer `apply` real»`*—
sin más mitigación que un runbook.

Además, el proyecto es también un ejercicio de **formación** en AWS y Terraform.
Equivocarse forma parte del método; equivocarse sobre recursos facturables, no.

Existe una vía intermedia: ejecutar la misma IaC contra un emulador AWS local. Este
mantenimiento decide si el proyecto la adopta, con qué límites y qué **no** promete.

## 3. Dentro del alcance

- [x] Verificar el estado real de Floci en **fuentes oficiales exclusivamente** (2026-08-15).
- [x] Crear el documento canónico `docs/architecture/aws-local-parity.md`.
- [x] Formalizar el **principio de portabilidad**: una sola definición de Terraform, dos
      destinos, sin duplicar el grafo de recursos.
- [x] Declarar explícitamente que **no se promete «cero cambios»** y acotar en una tabla
      cerrada qué diferencias local/AWS son legítimas.
- [x] Documentar los **dos modos locales** (desarrollo de aplicación · laboratorio de
      paridad) y que **MinIO ≠ Floci**: ninguno sustituye al otro.
- [x] Crear la **matriz de paridad** canónica, entera en estado `No evaluada`.
- [x] Documentar capacidades y **límites de fidelidad** por servicio, sin afirmar en ningún
      punto que algo sea «idéntico a AWS».
- [x] Fijar la **regla de versión**: se elegirá una release estable en `Task/025`; nunca
      `latest`.
- [x] Ampliar los límites de seguridad con el componente **C-12** y sus reglas.
- [x] Registrar el requisito de **guardas *fail-closed*** contra AWS real accidental.
- [x] Definir el **Infrastructure Learning Loop** de 12 preguntas.
- [x] Reformular el objetivo y el alcance futuro de la **ETAPA 08** sin añadir ni renumerar
      tareas.
- [x] Dejar escrito que la **ETAPA 10 reutiliza** los módulos de `Task/025`.
- [x] Aclarar el encaje futuro de la validación local en `Task/039`.
- [x] Crear **ADR-006** en estado `Propuesta`, con alternativas y criterio de abandono.
- [x] Añadir **D-14** a las decisiones diferidas, con respuesta propuesta.
- [x] Registrar los riesgos **R-19** a **R-28**.
- [x] Añadir la sección compacta **AWS LOCAL PARITY LAW** a `PROJECT_INSTRUCTIONS.md`.
- [x] Registrar en `STATUS.md` la normalización posterior a `Task/005.1` y esta tarea.
- [x] Crear ficha y reporte, y actualizar el índice de reportes.

## 4. Fuera del alcance

| Elemento | Motivo o tarea |
| --- | --- |
| Instalar Floci, descargar su imagen o levantar contenedores | Tarea **exclusivamente documental**. La implementación es de `Task/025`. |
| Crear cualquier archivo `.tf`, `.tfvars`, `.hcl` o estado de Terraform | `Task/025`. Los ejemplos del documento canónico son **ilustrativos**. |
| Ejecutar `terraform init`, `plan`, `apply` o `destroy` | `Task/025`. |
| Ejecutar AWS CLI contra AWS real | Prohibido. No hay cuenta y no se creará aquí. |
| Modificar `docker-compose.yml` | El entorno local del **Modo A** no se toca. |
| Modificar `personal-blog-backend` o `personal-blog-frontend` | La tarea no los afecta; no se creó rama en ellos. |
| Fijar una versión concreta de Floci | Deliberado: Floci publica cada pocos días. La versión se fija en `Task/025`. |
| Resolver **D-01** — proveedor de PostgreSQL administrado | `Task/029`. Que Floci soporte RDS **no es criterio de arquitectura de datos**. |
| Resolver **D-06** — backend de estado de Terraform | `Task/025`. Se documenta la tensión, no la solución. |
| Crear cuentas AWS o Cloudflare | ETAPA 09. |
| Crear workflows de CI | `Task/039`. Solo se documenta la intención. |
| Añadir, eliminar o renumerar tareas del roadmap | Las 41 se conservan intactas. |
| Modificar, regenerar o mover `images/Infraestructura.png` | Es un asset del usuario. Se referencia como *arquitectura objetivo AWS / producción*. |
| Generar un PNG nuevo de arquitectura | No solicitado. Los diagramas nuevos son Mermaid dentro de Markdown. |
| Iniciar `Task/006` | No se inicia la tarea siguiente sin cerrar la actual. |

## 5. Entregables

| Entregable | Ruta | Acción |
| --- | --- | --- |
| **Documento canónico** de la estrategia | `docs/architecture/aws-local-parity.md` | **Creado** |
| **ADR-006** — Paridad AWS local con Floci (**Propuesta**) | `docs/adr/ADR-006-local-aws-parity-with-floci.md` | **Creado** |
| Ficha de esta tarea | `docs/tasks/TASK-005.2-document-floci-local-iac-strategy.md` | **Creado** |
| Reporte de esta tarea | `docs/task-reports/TASK-005.2-report.md` | **Creado** |
| Ficha de la ETAPA 08 | `docs/stages/STAGE-08-cloud-ready.md` | Modificado |
| Ficha de la ETAPA 10 | `docs/stages/STAGE-10-cloud-deployment.md` | Modificado |
| Ficha de la ETAPA 11 | `docs/stages/STAGE-11-deployment-automation.md` | Modificado |
| Visión general de arquitectura | `docs/architecture/overview.md` | Modificado |
| Correspondencia local → nube | `docs/architecture/local-to-cloud-mapping.md` | Modificado |
| Límites de seguridad | `docs/architecture/security-boundaries.md` | Modificado |
| Decisiones diferidas (**D-14**) | `docs/architecture/open-decisions.md` | Modificado |
| Roadmap | `docs/project-management/ROADMAP.md` | Modificado |
| Estado del proyecto | `docs/project-management/STATUS.md` | Modificado |
| Ley compacta para las sesiones de Claude | `docs/claude/PROJECT_INSTRUCTIONS.md` | Modificado |
| Índice de reportes | `docs/task-reports/README.md` | Modificado |
| README del repositorio | `README.md` | Modificado |

**4 creados · 12 modificados · 0 eliminados — 16 archivos afectados.** Todos en
`personal-blog-infra`.
**0 archivos** en `personal-blog-backend` y **0** en `personal-blog-frontend`.
**0 archivos Terraform. 0 cambios en `docker-compose.yml`. 0 cambios en `images/`.**

## 6. Criterios de aceptación

| # | Criterio | Estado |
| --- | --- | --- |
| 1 | PR `#7` verificado como **fusionado**, con su merge commit real. | Cumplido — validación 1 |
| 2 | `main` y `dev` de infra normalizadas, con el merge del PR contenido en `dev`. | Cumplido — validación 2 |
| 3 | Rama remota `Task/005.1` **ausente**, sin ejecutar ningún borrado. | Cumplido — validación 3 |
| 4 | Backend y frontend verificados y **sin modificar**. | Cumplido — validación 4 |
| 5 | `Task/005.2` creada desde `dev` normalizado, sin sobrescribir nada. | Cumplido — validación 5 |
| 6 | Existe un único documento canónico con la estrategia completa. | Cumplido — validación 6 |
| 7 | Floci verificado **solo con fuentes oficiales**, con fecha registrada. | Cumplido — validación 7 |
| 8 | Ninguna afirmación declara paridad «idéntica a AWS». | Cumplido — validación 8 |
| 9 | El principio de portabilidad y la tabla de diferencias legítimas están escritos. | Cumplido — validación 9 |
| 10 | No se promete «cero cambios»; la meta correcta está formulada. | Cumplido — validación 9 |
| 11 | La matriz de paridad existe y está **entera en `No evaluada`**. | Cumplido — validación 10 |
| 12 | No se fija ninguna versión de Floci; la regla «nunca `latest`» está escrita. | Cumplido — validación 11 |
| 13 | Los dos modos locales están documentados y MinIO se conserva. | Cumplido — validación 12 |
| 14 | **D-01** y **D-06** siguen abiertas y explícitamente no resueltas. | Cumplido — validación 13 |
| 15 | **ADR-006** existe con alternativas A–D y criterio de abandono. Estado `Propuesta` durante la ejecución; **`Aceptada`** al aprobarse la tarea. | Cumplido — validación 14 |
| 16 | **D-14** registrada; respuesta propuesta durante la ejecución y **Resuelta** al aprobarse la tarea. | Cumplido — validación 13 |
| 17 | Seguridad: C-12, controles S-01 a S-11 y guardas G-01 a G-05. | Cumplido — validación 15 |
| 18 | El *learning loop* de 12 preguntas está definido. | Cumplido — validación 6 |
| 19 | La ETAPA 08 incorpora AWS Local Parity conservando `Task/023`–`Task/026`. | Cumplido — validación 16 |
| 20 | La ETAPA 10 declara que **reutiliza** los módulos de `Task/025`. | Cumplido — validación 16 |
| 21 | `Task/039` aclara el encaje del laboratorio sin duplicar responsabilidades. | Cumplido — validación 16 |
| 22 | Riesgos **R-19** a **R-28** registrados con impacto, mitigación y tarea. `Propuesto` durante la ejecución; **`Abierto`** tras la aprobación. Ninguno cerrado. | Cumplido — validación 17 |
| 23 | Exactamente **41 tareas**, ninguna renumerada. | Cumplido — validación 18 |
| 24 | Avance global **5 de 41**; ETAPA 02 **1 de 3**; `Task/006` **Pendiente**. | Cumplido — validación 18 |
| 25 | `PROJECT_INSTRUCTIONS.md` enlaza al canónico sin duplicarlo. | Cumplido — validación 19 |
| 26 | Todos los enlaces relativos resuelven. | Cumplido — validación 20 |
| 27 | `images/Infraestructura.png` **intacta**. | Cumplido — validación 21 |
| 28 | Cero secretos, cero `.tf`, cero cambios en Compose, backend y frontend. | Cumplido — validaciones 22 a 24 |
| 29 | Floci **no instalado**: sin imagen, sin contenedor, sin comandos ejecutados. | Cumplido — validación 25 |
| 30 | Sin commit, sin push, sin merge y sin PR **mientras la tarea no estuvo aprobada**; quedó `Lista para validación`. El commit, la integración en `dev` y el PR se ejecutaron **solo tras la aprobación explícita del usuario**. | Cumplido — validación 26 |

## 7. TDD / Plan test-first

**No aplica.** Esta tarea no introduce comportamiento funcional del backend: es
documentación de arquitectura y gobierno. La regla test-first
([BACKEND_TESTING_STRATEGY](../project-management/BACKEND_TESTING_STRATEGY.md)) sigue
íntegra y **no se modifica**.

Su verificación equivalente es la **consistencia documental y el estado real de Git**,
comprobados en la sección 10.

## 8. Plan de validación

Cada criterio se comprueba por: verificación del estado real de Git y de GitHub; búsqueda de
términos en los documentos afectados; verificación de enlaces relativos; recuento de las
tareas del roadmap; y comprobación de ausencia —de archivos Terraform, de secretos, de
contenedores y de cambios en repositorios ajenos.

## 9. Comandos de validación

```powershell
$env:PATH = "$env:PATH;C:\Program Files\GitHub CLI"
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# 1. PR #7 y ramas remotas
gh pr view 7 --repo jeffersondavila/personal-blog-infra --json number,state,mergeCommit,baseRefName,headRefName
git ls-remote --heads origin "Task/*"

# 2. Normalizacion main / dev
git log --oneline dev..main
git diff --stat main dev

# 3. Rama activa
git branch --show-current
git status --porcelain -b

# 4. Recuento del roadmap: deben seguir siendo 41
$bt = [char]96
(Select-String -Path docs\project-management\ROADMAP.md -Pattern ('^\| ' + $bt + 'Task/0')).Count

# 5. Ausencias
Get-ChildItem -Recurse -Include *.tf,*.tfvars,*.tfstate .. | Measure-Object
git status --porcelain -- docker-compose.yml images/
docker ps -a --filter "name=floci"

# 6. Repositorios no implicados
git -C ..\personal-blog-backend  status --porcelain -b
git -C ..\personal-blog-frontend status --porcelain -b

# 7. Higiene
git diff --check
```

## 10. Resultado de las validaciones

Ejecutadas el 2026-08-15. **Ninguna se declara sin haberse ejecutado.** Resultados completos
en el [reporte](../task-reports/TASK-005.2-report.md) §7.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-19 | **Nuevo.** El comportamiento del emulador difiere del de AWS real. | Medio | Matriz en `No evaluada`; AWS real es la autoridad final. |
| R-20 | **Nuevo.** Falsa sensación de paridad. | **Alto** | «Paridad completa» prohibida; vocabulario obligatorio; pregunta 12 del *learning loop*. |
| R-21 | **Nuevo.** Una actualización del emulador rompe la compatibilidad validada. | Medio | Versión fijada, nunca `latest`; actualizar exige revalidar la matriz. |
| R-22 | **Nuevo.** Acceso al socket de Docker: privilegio de nivel host. **Agrava R-09.** | **Alto** | Componente C-12; mismo tratamiento que Portainer; revisión de *networking* en `Task/025`. |
| R-23 | **Nuevo.** Endpoint local expuesto a LAN o internet. | **Alto** | Controles S-01 a S-03; verificación en los runbooks de `Task/026`. |
| R-24 | **Nuevo.** Actuar sobre AWS real por accidente, o usar credenciales reales contra el emulador. | **Alto** | Guardas *fail-closed* G-01 a G-05, obligatorias antes del primer `apply`. |
| R-25 | **Nuevo.** El camino crítico Terraform + API Gateway v2 + Lambda + Logs no está cubierto por la suite oficial de compatibilidad. | **Alto** | Objetivo explícito de `Task/025`; si falla, esos recursos pasan a `AWS-only`. |
| R-26 | **Nuevo.** Acabar con dos IaC distintas por acumulación de condicionales. | Medio | Tabla cerrada de diferencias legítimas; lo demás es defecto de diseño. |
| R-27 | **Nuevo.** Dependencia excesiva del emulador. | Medio | El laboratorio es una puerta, no un destino; la ETAPA 10 sigue siendo obligatoria. |
| R-28 | **Nuevo.** IAM no aplica políticas por omisión: un rol puede validarse en local y ser incorrecto en AWS. | **Alto** | El laboratorio valida creación, nunca autorización; mínimo privilegio es **AWS-only**. |
| R-14 | Dependencias transitivas del backend sin bloquear. | Medio | Sin cambios. `Task/020`. |
| R-16 | El `.env` local conserva las contraseñas de ejemplo. | Bajo | Sin cambios. Decisión del usuario. |

## 12. Decisiones técnicas

| # | Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- | --- |
| 1 | **Sí crear ADR**, a diferencia de `Task/005.1`. | No crearlo, por ser mantenimiento. | `Task/005.1` era una **práctica de trabajo**; esta decide **cómo se construye y se valida la infraestructura**, condiciona cuatro tareas futuras y añade un componente a los límites de seguridad. Es estructural. | **Sí — ADR-006** |
| 2 | **ADR-006 en estado `Propuesta`.** | Dejarlo `Aceptada` directamente. | Ninguna decisión de una tarea no aprobada puede marcarse como aceptada (WORKFLOW §6). | — |
| 3 | **Documento canónico en `docs/architecture/`.** | `docs/project-management/`, junto a la estrategia de pruebas. | Es una decisión sobre **la estructura del sistema y su infraestructura**, no sobre el proceso de trabajo. Convive con `local-to-cloud-mapping.md` y `security-boundaries.md`. | No |
| 4 | **Referenciar, no duplicar.** | Repetir la estrategia en cada documento afectado. | Once copias divergen en cuanto una cambia. Cada documento enuncia lo mínimo operativo y enlaza a la fuente única. Mismo criterio que `Task/005.1`. | No |
| 5 | **No fijar versión de Floci.** | Fijar hoy la 1.6.0. | El proyecto publica cada 3–4 días: una versión escrita hoy estaría obsoleta antes de llegar a `Task/025`, y fijarla ahora no aporta reproducibilidad porque no hay nada que reproducir todavía. | No |
| 6 | **No añadir tareas al roadmap.** | Crear `Task/025.1` para el laboratorio. | El laboratorio **es** la forma de hacer `Task/025`, no una tarea aparte. Añadir tareas rompería el conteo de 41 y la numeración. | No |
| 7 | **Ampliar el alcance de la ETAPA 08 en lugar de crear una etapa nueva.** | Insertar una ETAPA 08.1. | Renumerar 13 etapas por un cambio de alcance destruiría todas las referencias cruzadas del proyecto a cambio de nada. | No |
| 8 | **Matriz de paridad entera en `No evaluada`.** | Rellenarla con lo que la documentación oficial declara soportar. | Documentación no es evidencia. Rellenarla con expectativas es exactamente **R-20**: crearía la falsa paridad que la matriz existe para evitar. | No |
| 9 | **Registrar el hueco de la suite oficial de compatibilidad Terraform** (**R-25**). | Omitirlo: los servicios están documentados individualmente. | Es el hallazgo más relevante de la investigación y afecta al camino crítico exacto del proyecto. Ocultarlo haría la estrategia optimista y poco fiable. | No |
| 10 | **Diagramas en Mermaid, no en PNG.** | Generar un PNG nuevo. | El usuario no lo pidió; Mermaid se versiona, se diferencia en Git y se edita. El PNG existente es del usuario y no se toca. | No |
| 11 | **No resolver D-01 ni D-06.** | Aprovechar el impulso y cerrarlas. | Serían decisiones tomadas por disponibilidad de un emulador, no por los criterios que las gobiernan. Es justo lo que `open-decisions.md` existe para impedir. | No |

## 13. Documentación creada o actualizada

Ver sección 5. **16 archivos** (4 creados + 12 modificados), todos en `personal-blog-infra`.

## 14. Resultado de pruebas

**No aplica en el sentido habitual:** la tarea no ejecuta código de aplicación ni de
infraestructura. Su equivalente son las **26 validaciones** de consistencia documental y de
estado de Git del [reporte](../task-reports/TASK-005.2-report.md) §7, todas ejecutadas.

La suite del backend **no se reejecutó**: esta tarea no toca `personal-blog-backend`, cuyo
árbol permanece limpio en `main`.

## 15. Pasos de validación para el usuario

```powershell
$env:PATH = "$env:PATH;C:\Program Files\GitHub CLI"
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# 1. Rama y estado
git branch --show-current     # Task/005.2-Documentar-Estrategia-Floci-IaC-Local
git status --porcelain -b     # cambios sin confirmar, sin commit

# 2. El PR #7 esta fusionado y su rama remota ya no existe
gh pr view 7 --repo jeffersondavila/personal-blog-infra --json state,mergeCommit
git ls-remote --heads origin "Task/*"    # sin resultados

# 3. main y dev con el mismo contenido
git diff --stat main dev      # vacio

# 4. Lee la estrategia completa y la decision
code docs\architecture\aws-local-parity.md
code docs\adr\ADR-006-local-aws-parity-with-floci.md

# 5. El ADR NO esta aceptado
Select-String -Path docs\adr\ADR-006-local-aws-parity-with-floci.md -Pattern "Propuesta"

# 6. El roadmap sigue en 41 tareas y 5 aprobadas
Select-String -Path docs\project-management\ROADMAP.md -Pattern "5 de 41"
$bt = [char]96
(Select-String -Path docs\project-management\ROADMAP.md -Pattern ('^\| ' + $bt + 'Task/0')).Count   # 41

# 7. Cero Terraform y cero Floci
Get-ChildItem -Recurse -Include *.tf,*.tfvars,*.tfstate .. | Measure-Object
docker ps -a --filter "name=floci"

# 8. La imagen no se toco
git status --porcelain -- images/

# 9. Los otros repositorios no se tocaron
git -C ..\personal-blog-backend  status --porcelain -b
git -C ..\personal-blog-frontend status --porcelain -b
```

Ningún comando es destructivo.

## 16. Deuda documental pendiente tras la aprobación

- **La matriz de paridad está vacía de evidencia.** Es correcto —nada se ha probado— pero
  significa que la estrategia todavía no está respaldada por hechos. Se llena en `Task/025`.
- **La versión de Floci no está fijada.** Es deliberado, pero deja una decisión abierta que
  `Task/025` debe cerrar antes del primer `apply`.
- **Las guardas *fail-closed* están descritas conceptualmente, no implementadas.** Hasta que
  `Task/025` las implemente, **R-24** sigue sin mitigación técnica.
- **No hay diagrama PNG del laboratorio.** Los diagramas nuevos son Mermaid. Si el usuario
  quiere una versión gráfica equivalente a `Infraestructura.png`, debe pedirla.

## 17. Próxima tarea

`Task/006-Fundacion-Frontend-React` — **Pendiente, no iniciada**. No comienza hasta que el
usuario fusione el PR de `Task/005.2` y se complete la normalización `main → dev`.

## 18. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Efecto en el avance** | **Ninguno.** Es mantenimiento: no cuenta dentro de las 41 tareas. Avance global **5 de 41 (12 %)**; ETAPA 02 **1 de 3**; `Task/006` **Pendiente** |

Promociones ejecutadas en el cierre:

| Elemento | Antes | Después |
| --- | --- | --- |
| [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) | `Propuesta` | **`Aceptada`** ✔ |
| [aws-local-parity.md](../architecture/aws-local-parity.md) | `Propuesta` | **`Vigente`** ✔ |
| **D-14** — emulador AWS local para la IaC | `Respuesta propuesta` | **`Resuelta`** — **Floci** ✔ |
| Riesgos **R-19** a **R-28** | `Propuesto` | **`Abierto`** — ninguno cerrado |
| `security-boundaries.md` §8 y componente **C-12** | `Propuesta` | **`Vigente`** ✔ |
| `PROJECT_INSTRUCTIONS.md` §15 — *AWS Local Parity Law* | `Propuesta` | **Vigente y de cumplimiento obligatorio** ✔ |
| **D-01** y **D-06** | Abiertas | **Abiertas** — sin cambios, por diseño |

> El usuario autorizó explícitamente el cierre con la expresión exacta requerida por
> [WORKFLOW.md](../project-management/WORKFLOW.md) §3, y autorizó el flujo completo:
> commit, integración en `dev`, publicación de la rama y creación del pull request
> `Task/005.2 → main`. **La fusión del PR sigue siendo responsabilidad exclusiva del
> usuario.**
