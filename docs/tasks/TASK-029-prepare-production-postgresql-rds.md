# TASK-029 — Preparar-PostgreSQL-Produccion-en-RDS

| Campo | Valor |
| --- | --- |
| Identificador | `Task/029-Preparar-PostgreSQL-Produccion-en-RDS` |
| Tipo / etapa | ETAPA 09 — Cuentas y Seguridad Cloud, tercera de tres tareas. **Cuenta entre las 41** |
| Estado | **Lista para validación** — 2026-09-27. Ejecutada solo en `personal-blog-infra`. **Cero recursos AWS** |
| Definición | Fijada por `Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS`, **aprobada** el 2026-09-27. Sustituye a `Task/029-Preparar-PostgreSQL-Produccion-en-VPS`; conserva el ID |
| Repositorios previstos | `personal-blog-infra`. Backend y frontend solo en lectura, salvo que la inspección al iniciar justifique otra cosa |
| Rama base | `main` actualizado y limpio; **nunca** `dev` |

## 0. Preparación Git

**Ejecutada el 2026-09-27.** Requería `Task/027` y `Task/028` aprobadas —lo estaban— y
`Task/028.2` **aprobada** el 2026-09-27, verificada presente en la ascendencia de `main`.

| Validación | Resultado |
| --- | --- |
| `git fetch --prune origin` | Sin cambios. Ramas remotas: solo `origin/main` y `origin/dev`; la de `Task/028.2` ya estaba eliminada |
| `git switch main` · `git pull --ff-only origin main` | `Already up to date` |
| `git status --porcelain` | **Vacío** en los tres repositorios |
| `git rev-parse main` | `d96d5d569a673d2a0ddfae3cc9b09cfff078b837` |
| `git rev-parse origin/main` | `d96d5d569a673d2a0ddfae3cc9b09cfff078b837` — **coinciden** |
| `git rev-parse dev` | `99e895d44a16e49e38460ce253abe79266c9fb2e` |
| `git diff --stat main dev` | **Vacío**: normalización de `Task/028.2` intacta |
| CI Infra | `main` **SUCCESS**, `dev` **SUCCESS** |
| Otra Task activa que bloquee | **Ninguna**: infra, backend y frontend en `main`, sin `worktree` adicionales |
| `git switch -c Task/029-Preparar-PostgreSQL-Produccion-en-RDS` | Creada **desde `main`**, nunca desde `dev` |
| `git rev-parse HEAD` vs `git rev-parse main` | **Idénticos** (`d96d5d5`) — rama bien creada |

**Rama creada solo en `personal-blog-infra`.** La inspección no encontró ninguna dependencia
que exija modificar `personal-blog-backend` ni `personal-blog-frontend`: el contrato de TLS
viaja en `BLOG_DATABASE_URL` y no requiere cambio de código (ver §15). Ambos repositorios
quedan en `main`, limpios y **sin rama**. Ver
[WORKFLOW](../project-management/WORKFLOW.md) §2.1.

## 1. Objetivo

**Decidir y preparar** un PostgreSQL de producción en **Amazon RDS privado**, ejecutable
dentro de límites aprobados, **sin provisionar nada** y sin exigir evidencia que solo
existirá en tareas posteriores.

## 2. Contexto

[ADR-010](../adr/ADR-010-production-postgresql-on-rds.md) —**Aceptada** el 2026-09-27— sustituye el
modelo VPS de [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) por créditos AWS
disponibles y prioridad de aprendizaje. Esta tarea hereda el principio de `Task/005.5`:
**una tarea no exige como evidencia recursos que crea una tarea posterior**. No añade una
tarea 42. Canónico: [production-postgresql-rds.md](../architecture/production-postgresql-rds.md).

## 3. Dentro del alcance

| Qué | Contenido | Dónde se demuestra |
| --- | --- | --- |
| **Decide** | **D-22**: región, versión, clase, almacenamiento, IOPS, *throughput*, Single-AZ o Multi-AZ, VPC, subnets, DB subnet group, security groups, DNS, rutas y *endpoints*, ventana y *parameter group* · **D-23**: TLS con validación, rotación de CA, KMS, credenciales separadas, SSM frente a Secrets Manager, entrega del secreto a la Lambda, IAM DB auth evaluable · **D-24**: canal privado de administración, restore y migraciones · **D-10**: backups, PITR, snapshots, retención, RPO/RTO, *deletion protection*, snapshot final · si se **evalúa RDS Proxy** | Decisiones fechadas, con alternativas, precios de la fecha y fuentes primarias |
| **Prepara** | Inventario de tráfico de la Lambda (A–E) sobre el código vigente, con el candidato **sin NAT** · presupuesto preliminar de conexiones (**D-12**) · modelo de **costo bruto, crédito elegible, desembolso, vencimiento y escenario poscrédito** frente a **D-13** · contratos de módulos, *state* e identidades separadas · planes de prueba y runbooks para `Task/030`–`Task/040` · revisión de Alembic, extensiones y privilegios frente a RDS · diseño de **R-12**, **R-43** y **R-44** | Documentos y cálculos reproducibles, sin secretos |
| **Puede provisionar** | **Nada.** El primer `apply` de aplicación exige el backend de estado **D-06**, que crea `Task/030`, y **EX-028-C7 no se extiende** a recursos de aplicación | — |
| **Se valida después** | Red y RDS privados; restore sintético y PITR | `Task/031` |
| | Conexión real, secretos, tráfico sin NAT, pool, latencia y límites medidos | `Task/032` |
| | Primeras migraciones por el canal privado, con backup previo | `Task/036` → `Task/038` |
| | Carga, casos negativos, restore reciente, DR y alertas | `Task/040` |
| | Costo real frente a la estimación | `Task/041` |

## 4. Fuera del alcance

Crear RDS, VPC, subnets, security groups, *endpoints*, claves KMS, secretos, buckets o
roles; cualquier `apply`, `import`, `destroy` o migración de *state*; probar
`Lambda ↔ RDS`, medir latencia real o ejecutar un restore en AWS como criterio de salida.
Seleccionar NAT Gateway, EC2 u otro servicio excluido sin una decisión explícita previa.
Cambiar **D-13**, el plan de la cuenta o los presupuestos. Ampliar el rol de validación de
`Task/028`.

## 5. Entregables

Paquete de decisiones D-22, D-23, D-24 y D-10 con alternativas, precios y fecha;
contratos de red, IAM y SQL; diagrama sin valores secretos; costo por escenarios —base,
carga, restore y poscrédito—; presupuesto preliminar de conexiones; planes de prueba con
criterios medibles; runbooks preparados; matriz de propietarios actualizada en el
canónico y el roadmap; ficha y reporte. Todo en infra, salvo que la inspección justifique
otro repositorio al iniciar.

## 6. Criterios de aceptación

1. **D-22**, **D-23**, **D-24** y **D-10** decididas con datos de la fecha y sin valores
   arbitrarios.
2. Inventario de tráfico A–E completo; candidato **sin NAT** viable o, si no lo es,
   necesidad real explicada y decisión explícita pedida al usuario.
3. TLS, KMS, credenciales separadas y rotación definidos, **sin generar ni leer secretos**.
4. Presupuesto preliminar de conexiones y decisión sobre evaluar RDS Proxy, con la
   medición asignada a `Task/032` y `Task/040`.
5. **Costo bruto** por escenarios y condiciones de los créditos verificadas; **D-13**
   respetada, o **decisión explícita** del usuario obtenida antes de cualquier `apply` de
   aplicación.
6. Backend de estado **D-06** y bootstrap separado asignados a `Task/030` **antes** de los
   recursos de `Task/031`; **EX-028-C7 no extendida**.
7. Canal privado **D-24** viable bajo las restricciones, con los límites del ejecutor
   candidato; **ningún acceso público** a la base de datos por conveniencia.
8. Restore sintético y PITR con owner `Task/031`; restore reciente con owner `Task/040`;
   métricas de RPO/RTO definidas. **Ninguna evidencia fingida aquí.**
9. Migraciones (`Task/036`, `Task/038`), seguridad, carga y DR (`Task/040`) y costo
   (`Task/041`) con criterios y owners; **sin ciclos** y **sin criterios que requieran
   recursos futuros**.
10. Documentación, enlaces, contadores y gates locales correctos. Estado de salida:
    **Lista para validación**; nunca autoaprobación.

### Cumplimiento verificado el 2026-09-27

| # | Estado | Evidencia |
| --- | --- | --- |
| 1 | **Cumplido** | D-22, D-23, D-24 y D-10 decididas con precios de la AWS Price List publicada el 2026-09-24 y documentación consultada el 2026-09-27. Ningún valor arbitrario: la versión sigue a la de local, IOPS queda cerrado por el propio servicio y la clase es la mínima de generación actual |
| 2 | **Cumplido** | Inventario A–E completo sobre `d96d5d5`; **clase D vacía**; candidato **sin NAT viable**. No hizo falta pedir decisión de NAT |
| 3 | **Cumplido** | TLS `verify-full`, KMS gestionada por AWS, tres identidades SQL y rotación definidos. **Cero secretos generados o leídos** |
| 4 | **Cumplido** | Presupuesto de conexiones derivado (112 → 89 → 40) y **RDS Proxy descartado** con cuatro condiciones medibles asignadas a `Task/032` y `Task/040` |
| 5 | **Cumplido** | Costo bruto por escenarios entregado y **D-13 no se cumple**, lo que se elevó al usuario sin maquillar el cálculo. **Resuelto el 2026-09-27**: el usuario aceptó el exceso mediante **EX-029-D13**, excepción acotada y fechada que suspende **solo** el sublímite AWS y **conserva íntegro el techo global de USD 20/mes**. Condiciones de los créditos **verificadas por el usuario**: USD 120, límite 2027-03-15 |
| 6 | **Cumplido** | D-06 y el *bootstrap* separado siguen asignados a `Task/030`, **antes** de los recursos de `Task/031`; verificado en el grafo. **EX-028-C7 no se extendió** |
| 7 | **Cumplido** | Canal D-24 viable: **Lambda ejecutora dedicada**, con el límite de **900 s** declarado. **Ningún acceso público** a la base de datos |
| 8 | **Cumplido** | Restore sintético y PITR con owner `Task/031`; restore reciente con owner `Task/040`; **RPO ≤ 15 min** y **RTO ≤ 4 h** definidos. **Ninguna evidencia fingida** |
| 9 | **Cumplido** | Criterios y owners de 030–041 fijados; grafo verificado: **0 ciclos**, **0 dependencias hacia una tarea posterior** |
| 10 | **Cumplido** | Ocho gates ejecutados, **497 enlaces con 0 rotos**, contadores de decisiones y riesgos actualizados. Estado de salida **Lista para validación**; **sin autoaprobación** |

| 8 bis | **Ampliado el 2026-09-27** | El criterio 8 hablaba de *restore*; la decisión **H-4** obligó a añadir una **vía de salida fuera de la cuenta**, porque ningún *backup* administrado sobrevive al cierre de la cuenta. Diseñada aquí; **`Task/040` debe restaurar desde ella** |

**Hallazgo adicional no previsto en los criterios:** el **Free Plan cierra la cuenta y
pierde los datos**. Registrado como **R-47** y elevado como **H-4**.

**Resolución de H-1 a H-4 — 2026-09-27.** El usuario decidió: **us-east-2**; **EX-029-D13**
para el presupuesto, con el techo global intacto; créditos **USD 120** con límite
**2027-03-15**; y **conservar el plan gratuito**, con el Paid Plan **descartado como
prerrequisito de `Task/031`** y la continuidad diferida a una decisión fechada **A** pagar /
**B** desmontar. **No queda ninguna decisión humana pendiente en el alcance de esta tarea.**
Registro íntegro:
[decisiones §11](../architecture/production-postgresql-rds-decisions.md#11-decisiones-del-usuario--h-1-a-h-4-resueltas).

## 7. TDD / Plan test-first

**No aplica en el modo backend.** La tarea decide y prepara: no toca el dominio, los casos
de uso, la API, la persistencia, la autenticación ni la auditoría de
`personal-blog-backend`, así que la
[BACKEND TESTING STRATEGY](../project-management/BACKEND_TESTING_STRATEGY.md) no la
gobierna. Si al iniciar el alcance incluyera código funcional del backend —por ejemplo, un
lector de secretos—, ese trabajo pertenece a `Task/032` y exige allí su propio plan
test-first.

## 8. Plan de validación

Revisión documental, precios y fuentes AWS de la fecha, inspección estática segura del
código, cálculos de capacidad, conexiones y costo, y análisis del grafo de tareas y de
los contratos. Los cálculos **no** se etiquetan como carga ni restore reales. El saldo, la
elegibilidad y el vencimiento de los créditos los verifica **el usuario en privado**; el
agente no lee facturación. Solo consultas AWS de lectura, y solo si el usuario las
autoriza expresamente.

## 9. Comandos de validación

**Ejecutados el 2026-09-27.** Versiones usadas: Git `2.53.0.windows.1`, Python `3.12.10`,
Gitleaks `8.30.1` —la que fija el CI—. **Ningún comando AWS mutante. Ninguna consulta de
facturación.**

| Gate | Comando | Resultado |
| --- | --- | --- |
| Espacios y conflictos | `git diff --check` | **OK**, sin hallazgos |
| UTF-8, LF, controles, BOM | Script sobre los 9 archivos de la tarea | **OK**: 0 CRLF, 0 CR sueltos, 0 controles, 0 BOM |
| Enlaces relativos y anclas | Script que **ignora fences y *code spans*** | **OK**: **526** enlaces, **0 rotos** |
| Encabezados duplicados | *Slugs* repetidos en los documentos de la tarea | **OK**: 0 duplicados, tras corregir una colisión |
| Secretos | `gitleaks dir . --redact=100 --config .gitleaks.toml` sobre el entregable versionado | **OK**: 263 archivos, 5,70 MB, **0 *leaks*** |
| Grafo de tareas | Script que lee las dependencias del ROADMAP | **OK**: **0 ciclos**, **0 dependencias hacia una tarea posterior**; gate de D-06 intacto |
| Terraform | `git status` y `git diff` sobre `terraform/` | **OK**: `terraform/` **sin un solo archivo modificado** |
| Sin recursos Terraform | Ningún `.tf`/`.tfvars`/`.hcl` en el diff · ninguna línea `^+resource "aws_` · los 3 nuevos son Markdown bajo `docs/` · ningún fence `hcl`/`terraform` | **OK** en las cuatro |
| Python / PowerShell | `compileall` / parser | **No aplica**: ningún `.py` ni `.ps1` modificado |

Cinco precisiones de método, detalladas en el
[reporte §9.1](../task-reports/TASK-029-report.md):

1. El gate de enlaces **encontró un defecto real dos veces**: 22 anclas en la primera ronda y
   13 en la segunda habían perdido las tildes que GitHub **conserva** en sus *slugs*. Se
   corrigieron en lectura y escritura **binaria** para no alterar los finales de línea.
2. **El alcance del escaneo de secretos importa:** el directorio completo devuelve 586
   hallazgos sobre 4,58 GB —`tmp/`, `.venv` y directorios no versionados—; **solo el
   entregable** devuelve **0**.
3. **`terraform fmt`/`validate` no se re-ejecutaron** porque no hay binario instalado en la
   estación y `terraform/` **no cambió**, comprobado con `git status` y `git diff`. El CI los
   ejecuta con la versión fijada `1.16.2` al abrirse el PR.
4. **Una colisión de numeración**: quedaron dos §7.7 en el paquete de decisiones y la de
   Grafana pasó a §7.8. Desde entonces el gate comprueba encabezados duplicados.
5. **El gate «sin recursos AWS» se precisó**: buscar nombres de recurso en el diff devolvía
   una coincidencia que era **la propia línea que documenta el gate**. La versión definitiva
   comprueba archivos, declaraciones, tipo de archivo y *fences* por separado.

Los scripts de validación quedaron en el directorio temporal de la sesión: **no se añadió
herramienta nueva al repositorio**.

## 10. Evidencia esperada

Decisiones fechadas; cálculo reproducible sin datos privados; fuentes primarias; matriz de
tráfico A–E; contratos y planes de prueba. **Ningún criterio exige infraestructura que
todavía no existe.**

## 11. Riesgos

**D-13** incompatible, necesidad de un servicio excluido, canal privado inviable, ciclo en
el grafo o *state* sin owner: **detenerse y explicarlo**. Un backup administrado o un
*pool* configurado **no** equivalen a un restore o a una carga probados. Riesgos
relacionados: **R-02**, **R-29** a **R-35**, **R-38** a **R-42**, **R-12**, **R-43** y
**R-44**, según la
[reconciliación de STATUS](../project-management/STATUS.md).

## 12. Decisiones técnicas

Paquete completo:
[production-postgresql-rds-decisions.md](../architecture/production-postgresql-rds-decisions.md)
—**Propuesta pendiente de aprobación**—, con el resumen ejecutivo en §14. Índice vigente en
el [registro de decisiones](../architecture/open-decisions.md) y contexto en el
[canónico RDS §3](../architecture/production-postgresql-rds.md#3-decisiones-que-entrega-task029).
ADR-010 está **Aceptada** desde el 2026-09-27 y **no se reescribe**: esta tarea la instancia.

Resumen de lo decidido: **us-east-2** *(confirmación del usuario)* · PostgreSQL **17.11**,
la misma versión que local y el CI del backend · **db.t4g.micro** · **gp3 20 GiB** con
*autoscaling* a 50 · IOPS y *throughput* **no aprovisionables** bajo 400 GiB · **Single-AZ**
con **R-29** aceptado por escrito · VPC `10.40.0.0/16` con 2 subnets privadas en 2 AZ y
**sin NAT** · 3 security groups por referencia de grupo · *parameter group* propio con
`rds.force_ssl = 1` explícito · **`verify-full`** con bundle de CA dentro del ZIP · clave
KMS **gestionada por AWS** · 3 identidades SQL con `blog_app` **sin DDL** · **SSM
`SecureString`** con entrega en despliegue · **IAM DB auth descartada** por memoria ·
**RDS Proxy descartado** con criterio objetivo · retención **7 días**, PITR, **RPO ≤ 15
min**, **RTO ≤ 4 h** · canal privado por **Lambda ejecutora dedicada** serializada.

## 13. Documentación creada o actualizada

**Nuevos:** `docs/architecture/production-postgresql-rds-decisions.md` (paquete de
decisiones) · `docs/runbooks/rds-private-administration.md` (runbook preparado, **no
ejecutado**) · `docs/task-reports/TASK-029-report.md`.

**Actualizados:** el canónico RDS —enmienda de instancia, estado de entrega en §3, **§6.1
nueva** con el resultado del gate y el hallazgo del plan de la cuenta, y §9 con la
re-verificación de fuentes— · el registro de decisiones —D-22, D-23, D-24 y D-10 con su
Propuesta; D-12 con el presupuesto derivado; D-11 y D-19 con estimación; D-13 con el
resultado del gate— · STATUS · ROADMAP · el índice de runbooks · esta ficha.

**ADR-010 no se modifica.** No apareció contradicción que exija gobierno arquitectónico
nuevo.

## 14. Archivos modificados

Nueve, **todos en `personal-blog-infra` y todos bajo `docs/`**:

| Archivo | Tipo |
| --- | --- |
| `docs/architecture/production-postgresql-rds-decisions.md` | Nuevo |
| `docs/runbooks/rds-private-administration.md` | Nuevo |
| `docs/task-reports/TASK-029-report.md` | Nuevo |
| `docs/architecture/production-postgresql-rds.md` | Modificado |
| `docs/architecture/open-decisions.md` | Modificado |
| `docs/project-management/STATUS.md` | Modificado |
| `docs/project-management/ROADMAP.md` | Modificado |
| `docs/runbooks/README.md` | Modificado |
| `docs/tasks/TASK-029-prepare-production-postgresql-rds.md` | Modificado |

**`terraform/`, `scripts/`, `bootstrap/`, `docker-compose.yml` y los workflows: sin
cambios.** `personal-blog-backend` y `personal-blog-frontend`: **cero archivos, cero ramas**.

## 15. Resultado de pruebas

Los ocho gates de §9 pasaron. No hay pruebas de software que ejecutar: la tarea no modifica
código. **No aplica la BACKEND TEST-FIRST LAW**, porque no se tocó dominio, casos de uso,
API, persistencia, autenticación ni auditoría; la inspección del backend fue de **solo
lectura**.

Verificaciones sustantivas que sí se hicieron sobre el código real:

| Comprobación | Resultado |
| --- | --- |
| Configuración de pool vigente | `pool_size=5`, `max_overflow=5`, `pool_recycle=1800`, `connect_timeout=10`, `pool_pre_ping=True`. **No modificada**: el cambio es de `Task/032` |
| Lectura de SSM en *runtime* | **No existe.** Las coincidencias aparentes son la subcadena `ssm` de `classmethod` |
| Clientes HTTP externos | **Ninguno.** `boto3` es el único SDK AWS; sin `requests`, `httpx`, `aiohttp` ni `smtplib` |
| `sslmode` / `sslrootcert` en el código | **Ausentes.** El TLS viaja en `BLOG_DATABASE_URL`: **el backend no necesita cambios** |
| `CREATE EXTENSION` en migraciones | **Ninguna.** No se necesita `rds_superuser` |
| Versión de PostgreSQL local | **17.11**, en `.env` y en el CI del backend. Paridad exacta con la candidata |

## 16. Problemas encontrados

1. **Las páginas comerciales de precios de AWS no son utilizables:** se renderizan por
   JavaScript y al recuperarlas no contienen cifras. **Resuelto** usando la **AWS Price List
   API**, que es autoritativa y lleva fecha de publicación propia (2026-09-24 para RDS).
2. **22 anclas con tildes eliminadas.** Los *slugs* de GitHub **conservan** los acentos. El
   gate de enlaces lo detectó y se corrigió en modo binario. **Ningún enlace queda roto.**
3. **D-13 no admite RDS.** No es un problema de esta tarea sino un hallazgo suyo: el mínimo
   absoluto es **≈ 15.48 USD/mes** de AWS frente a un sublímite de **5.00**. **No se
   manipuló el cálculo** ni se cambió D-13 por iniciativa del agente: se registró y se elevó
   al usuario (**H-2**). **Resuelto** el 2026-09-27 con **EX-029-D13**.
4. **El Free Plan cierra la cuenta y pierde los datos.** Hallazgo grave y no previsto en el
   canónico. Registrado como **R-47**. El agente propuso el paso a Paid Plan como
   prerrequisito de `Task/031`; el usuario **decidió lo contrario** y se acató. La
   consecuencia que sí quedó, y que el agente añadió: la opción «no continuar» **no era
   ejecutable**, porque los *backups* administrados mueren con la cuenta. De ahí la **vía de
   salida** de **D-10** y el gate fechado del **2027-03-15**.
7. **Colisión de numeración detectada y corregida.** Al insertar las secciones nuevas del
   modelo económico quedaron **dos §7.7** en el paquete de decisiones; la de Grafana pasó a
   **§7.8**. Lo detectó el gate de enlaces al resolver las anclas.
5. **Lambda reclama la Hyperplane ENI tras 14 días de inactividad** y la siguiente
   invocación falla. Relevante en un blog de tráfico bajo; asignado a `Task/032`.
6. **`terraform/providers.tf` le faltan los *endpoints* `ec2` y `rds`** para el laboratorio.
   Es una diferencia legítima de paridad y **corresponde a `Task/031`**: esta tarea no toca
   Terraform.

## 17. Pasos de validación para el usuario

1. Confirmar que la rama es `Task/029-Preparar-PostgreSQL-Produccion-en-RDS`, nace de `main`
   en `d96d5d5` y **solo existe en infra**.
2. Revisar el resumen ejecutivo
   ([§14](../architecture/production-postgresql-rds-decisions.md#14-resumen-ejecutivo--decision-pack))
   y el checkpoint humano
   ([§11](../architecture/production-postgresql-rds-decisions.md#11-decisiones-del-usuario--h-1-a-h-4-resueltas)).
3. Recalcular el gate de D-13: los precios unitarios de §7.1 permiten reproducir cada
   subtotal a mano.
4. Comprobar que la §11 del paquete recoge fielmente las cuatro decisiones del 2026-09-27 y
   que **EX-029-D13** está acotada como se acordó: suspende **solo** el sublímite AWS, **no**
   toca el techo global de USD 20/mes, vence con los créditos o el **2027-03-15** y **no
   autoriza ningún recurso**.
5. Confirmar **cero recursos creados**: el `git diff` no contiene ningún recurso de Terraform
   y `terraform/` está intacto.
6. Comprobar que ningún criterio de salida exige un recurso que su propia tarea no crea.

Aprobar solo si todo lo anterior es correcto.

## 18. Deuda técnica pendiente

`Task/030` *state* y S3 · `Task/031` red, RDS, configuración, CloudWatch, Grafana, acceso
privado y restore · `Task/032` Lambda real · `Task/033` API · `Task/034` Pages ·
`Task/035` DNS · `Task/036` migraciones y operación · `Task/037` CI frontend · `Task/038`
CI backend y migraciones · `Task/039` Terraform en CI · `Task/040` carga, seguridad, DR y
restore integral · `Task/041` costo real.
[Tabla contractual](../architecture/production-postgresql-rds.md#7-propietarios-dependencias-y-evidencia).

## 19. Próxima tarea

`Task/030-Desplegar-Amazon-S3`, cuando esta tarea esté **aprobada**. **No iniciada.**

El gate de **D-13** quedó **resuelto** el 2026-09-27 con **EX-029-D13**, y el **Paid Plan
quedó descartado** como prerrequisito de `Task/031` por decisión del usuario. Por tanto
**`Task/029` no deja ninguna condición previa nueva** más allá de su propia aprobación.

Lo que sí deja son **compromisos con fecha** que ninguna tarea puede olvidar: la vía de salida
de **D-10** debe estar **probada por `Task/040`**, y la decisión de continuidad —**A** pagar o
**B** desmontar— debe tomarse **antes del agotamiento del crédito o del 2027-03-15**, con
`Task/041` como gate (**R-47**). El gate de **D-06** sigue siendo el primero y sigue siendo de
`Task/030`.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| Fecha de aprobación | Pendiente |
| Aprobado por | Pendiente — solo el usuario |
| Expresión requerida | `approved: Task/029-Preparar-PostgreSQL-Produccion-en-RDS` |

**Estado actual: Lista para validación.** Sin commit, sin push, sin PR y sin merge. Todas
las decisiones son **Propuesta — pendiente de aprobación**; **el agente no autoaprueba**.
Reporte: [TASK-029-report.md](../task-reports/TASK-029-report.md).
