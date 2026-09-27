# TASK-029 — Preparar-PostgreSQL-Produccion-en-RDS

| Campo | Valor |
| --- | --- |
| Identificador | `Task/029-Preparar-PostgreSQL-Produccion-en-RDS` |
| Tipo / etapa | ETAPA 09 — Cuentas y Seguridad Cloud, tercera de tres tareas. **Cuenta entre las 41** |
| Estado | **Pendiente** — no iniciada |
| Definición | **Propuesta** por `Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS` (2026-09-27), pendiente de aprobación. Sustituye a `Task/029-Preparar-PostgreSQL-Produccion-en-VPS`; conserva el ID |
| Repositorios previstos | `personal-blog-infra`. Backend y frontend solo en lectura, salvo que la inspección al iniciar justifique otra cosa |
| Rama base | `main` actualizado y limpio; **nunca** `dev` |

## 0. Preparación Git

**No iniciada: no hay rama ni SHA base.** Requiere `Task/027` y `Task/028` aprobadas —lo
están— y el mantenimiento `Task/028.2` **aprobado**. Como toda Task, nace de `main`
actualizado tras la normalización. Al abrirla: `fetch --prune`, `switch main`,
`pull --ff-only`, árbol limpio, `main == origin/main`; crear la rama y comprobar
`HEAD == main`. Ver [WORKFLOW](../project-management/WORKFLOW.md) §2.1.

## 1. Objetivo

**Decidir y preparar** un PostgreSQL de producción en **Amazon RDS privado**, ejecutable
dentro de límites aprobados, **sin provisionar nada** y sin exigir evidencia que solo
existirá en tareas posteriores.

## 2. Contexto

[ADR-010](../adr/ADR-010-production-postgresql-on-rds.md) —**Propuesta**— sustituye el
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

Al iniciar, registrar los comandos exactos y las versiones disponibles. Mínimos:
`git diff --check`, enlaces relativos, UTF-8, LF y caracteres de control, búsqueda de
secretos sobre el entregable versionado y análisis del grafo de tareas. **Esta ficha no
autoriza ningún comando AWS mutante.**

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

[Canónico RDS §3](../architecture/production-postgresql-rds.md#3-decisiones-que-entrega-task029)
y [registro de decisiones](../architecture/open-decisions.md). Mientras `Task/028.2` no se
apruebe, ADR-010 es **Propuesta**.

## 13. Documentación creada o actualizada

Pendiente de ejecución: ADR-010 y el canónico, el registro de decisiones, costos,
contratos y runbooks, STATUS, ROADMAP, ficha y reporte.

## 14. Archivos modificados

Ninguno atribuible a la ejecución de esta tarea. Esta ficha la prepara `Task/028.2`.

## 15. Resultado de pruebas

No ejecutadas: la tarea está **Pendiente**. La coherencia de esta definición se valida
dentro de `Task/028.2`.

## 16. Problemas encontrados

Sin incidencias de ejecución: no iniciada. La viabilidad económica y los parámetros
finales siguen **pendientes** por diseño.

## 17. Pasos de validación para el usuario

Comprobar las decisiones con fuentes y precios de la fecha, revisar números y owners,
confirmar **cero recursos creados** y que ningún criterio sea imposible. Aprobar solo
cuando la tarea esté ejecutada y revisada.

## 18. Deuda técnica pendiente

`Task/030` *state* y S3 · `Task/031` red, RDS, configuración, CloudWatch, Grafana, acceso
privado y restore · `Task/032` Lambda real · `Task/033` API · `Task/034` Pages ·
`Task/035` DNS · `Task/036` migraciones y operación · `Task/037` CI frontend · `Task/038`
CI backend y migraciones · `Task/039` Terraform en CI · `Task/040` carga, seguridad, DR y
restore integral · `Task/041` costo real.
[Tabla contractual](../architecture/production-postgresql-rds.md#7-propietarios-dependencias-y-evidencia).

## 19. Próxima tarea

`Task/030-Desplegar-Amazon-S3`, cuando esta tarea esté **aprobada** y el gate de **D-13**
resuelto.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| Fecha de aprobación | Pendiente |
| Aprobado por | Pendiente — solo el usuario |
| Expresión requerida | `approved: Task/029-Preparar-PostgreSQL-Produccion-en-RDS` |

**No iniciada. Estado actual: Pendiente.**
