# PostgreSQL productivo en RDS — paquete de decisiones de `Task/029`

| Campo | Valor |
| --- | --- |
| Estado | **Vigente** ✔ — aprobado el 2026-09-27 mediante `approved: Task/029-Preparar-PostgreSQL-Produccion-en-RDS`. **No autoriza recursos**: cada uno exige su tarea propietaria y la autorización del usuario |
| Canónico que amplía | [production-postgresql-rds.md](production-postgresql-rds.md) — **Vigente**, aprobado en `Task/028.2` |
| ADR | [ADR-010](../adr/ADR-010-production-postgresql-on-rds.md) — **Aceptada**. Este documento **no la modifica**: la instancia |
| Decisiones que resuelve | **D-22**, **D-23**, **D-24**, **D-10** · presupuesto preliminar de **D-12** · estimación de **D-11**/**D-19** · gate de **D-13** |
| Recursos creados | **Ninguno.** Cero `apply`, cero `import`, cero *state*, cero secretos, cero llamadas mutantes a AWS |
| Fecha de consulta de precios y capacidades | **2026-09-27** |

> **Qué es y qué no es este documento.** Es el contrato que `Task/031` implementará. **Que
> esté aprobado no provisiona nada**: cada recurso sigue exigiendo su tarea propietaria y la
> autorización explícita del usuario.
>
> **Los cuatro puntos que exigían decisión humana quedaron resueltos** por el usuario el
> 2026-09-27: región **us-east-2**, **excepción acotada a D-13** para la etapa financiada con
> créditos, saldo y vencimiento **verificados** (USD 120, límite 2027-03-15) y **el plan
> gratuito se conserva**, con la decisión de continuidad diferida a una fecha concreta.
> Registro íntegro en la [§11](#11-decisiones-del-usuario--h-1-a-h-4-resueltas). Queda **un
> dato opcional por verificar**, sin efecto bloqueante
> ([§11.5](#115-un-dato-por-verificar-sin-efecto-bloqueante)).
>
> **Aprobado el 2026-09-27**, junto con `Task/029`: **D-22**, **D-23**, **D-24** y **D-10**
> pasan a **Resueltas**, y **EX-029-D13** a **Aceptada y Vigente**. **D-12 sigue abierta**:
> aquí solo se aprueba su presupuesto **preliminar**, y `Task/032` la cierra **con medición**.

---

## 1. Fuentes primarias y trazabilidad de los números

Todo precio unitario de este documento proviene de una fuente primaria de AWS
consultada el **2026-09-27**, no de ejemplos previos del repositorio. Las listas de
precios llevan su propia fecha de publicación, que es la que manda.

| Fuente | Qué aporta | Fecha de publicación de la fuente |
| --- | --- | --- |
| `pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/<region>/index.csv` | Instancia, almacenamiento gp3/gp2/io2, *backup*, IOPS/throughput gp3, CPU Credits, RDS Proxy | **2026-09-24T21:10:11Z** |
| `.../aws/awskms/current/<region>/index.csv` | Clave CMK y peticiones KMS | 2026-09-11T12:46:01Z |
| `.../aws/AWSSecretsManager/current/<region>/index.csv` | Secreto/mes y peticiones | 2026-09-11T12:46:10Z |
| `.../aws/AmazonVPC/current/<region>/index.csv` | Hora de *endpoint* y GB procesados | 2026-09-17T19:05:28Z |
| `.../aws/AmazonCloudWatch/current/<region>/index.csv` | Logs, métricas, alarmas y *free tier* | 2026-09-22T02:17:15Z |
| [Calendario de versiones RDS PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-release-calendar.html) | Versiones disponibles y fin de soporte estándar | consultada 2026-09-27 |
| [Almacenamiento RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html) | Línea base gp3, umbral de 400 GiB, máximos por clase | consultada 2026-09-27 |
| [Backups automáticos](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html) y [FAQ RDS](https://aws.amazon.com/rds/faqs/) | Retención 0–35, asignación gratuita, borrado | consultada 2026-09-27 |
| [Detener una instancia](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_StopInstance.html) | Máximo 7 días y qué se sigue cobrando | consultada 2026-09-27 |
| [TLS en PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Concepts.General.SSL.html) y [CA](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html) | `rds.force_ssl`, CA vigentes, rotación automática | consultada 2026-09-27 |
| [IAM DB authentication](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.html) | Memoria extra exigida, vida del token, límites | consultada 2026-09-27 |
| [RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html) | Autenticación exigida, límites, *pinning* | consultada 2026-09-27 |
| [Lambda en VPC](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html) | Acceso sin NAT, Hyperplane ENI, inactividad de 14 días | consultada 2026-09-27 |
| [Planes del Free Tier](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html) y [AWS Free Tier](https://aws.amazon.com/free/) | Free Plan, créditos, duración y cierre de cuenta | consultada 2026-09-27 |
| [Precios de Systems Manager](https://aws.amazon.com/systems-manager/pricing/) | Parámetros estándar sin cargo | consultada 2026-09-27 |

**Convención de cálculo:** 730 horas/mes, moneda USD, precios *on-demand* sin
compromisos. Todo subtotal de la [§7](#7-modelo-económico-y-gate-de-d-13) es
`precio unitario × cantidad`, reproducible a mano con la tabla de precios.

---

## 2. Inventario de tráfico de la Lambda (A–E) sobre el código vigente

Inspección estática de `personal-blog-backend` en el commit base de esta tarea
(`main` = `d96d5d5`). **No** se leyeron `.env` reales ni credenciales. Rutas relativas
a `personal-blog-backend`.

| Clase | Destino | Evidencia en el código | Consecuencia de red |
| --- | --- | --- | --- |
| **A — intra-VPC** | PostgreSQL 5432 | `app/shared/database/session.py` crea el motor con `create_engine` sobre `settings.sqlalchemy_url`, driver `psycopg` 3; `app/api/readiness.py` usa una conexión propia | SG de la Lambda → SG de RDS. **No exige NAT ni endpoint** |
| **B — gateway endpoint** | S3 | `app/shared/storage/s3_compatible.py`: `put_object`, `get_object`, `head_object`, `delete_object` y `list_objects_v2` (sonda de `/ready`). `generate_presigned_url` **no hace red** (línea 154 lo documenta) | **Gateway endpoint S3**, sin tarifa de *endpoint*. **No exige NAT** |
| **B — no aplica hoy** | SSM Parameter Store | **No hay lector en *runtime*.** Búsqueda de `ssm`, `get_parameter` y `parameter_store` en `app/`: cero coincidencias reales (las aparentes son la subcadena `ssm` de `classmethod`) | **No se provisiona interface endpoint SSM.** Si `Task/032` introdujera lectura en *runtime*, requeriría endpoint de interfaz — con su costo, [§7](#7-modelo-económico-y-gate-de-d-13) B6 |
| **B — no aplica** | Secrets Manager, KMS, STS, CloudWatch por SDK | Ninguna llamada directa en `app/`. Dependencias de ejecución declaradas en `pyproject.toml`: `boto3` es el único SDK AWS; **no hay `requests`, `httpx`, `aiohttp` ni `smtplib`** | Sin endpoints adicionales |
| **C — servicio gestionado** | Logs de Lambda a CloudWatch, credenciales del *execution role*, invocación desde API Gateway, métricas y *backup* administrados de RDS | Fuera del tráfico de la aplicación en la VPC | Exigen **permisos**, no rutas. **No exigen NAT** |
| **C — KMS vía SSM** | Descifrado de `SecureString` | Parameter Store invoca KMS por cuenta propia | Autorización KMS, no conectividad desde la Lambda |
| **D — Internet público** | **Ninguno.** No hay API externa requerida por el backend | Las URL de perfiles y vídeos son **contenido** que resuelve el navegador | **No hay egress público que justificar** |
| **E — no usado en *runtime*** | API de Cloudflare, API de Grafana, emulador Floci, *registry* de imágenes, SMTP | Corresponden al navegador, al despliegue o a CI, con red distinta | Irrelevantes para la VPC |

### 2.1 Conclusión de red

**El candidato sin NAT Gateway es viable con el código vigente**, y lo es por evidencia,
no por preferencia: la clase D está **vacía**. Es una conclusión de diseño, no una
demostración desplegada — `Task/032` la prueba con tráfico real y `Task/040` la repite
con el producto completo.

### 2.2 Hallazgo operativo: ENI reclamada por inactividad

La documentación de Lambda en VPC establece que **si la función permanece inactiva 14
días, Lambda reclama la Hyperplane ENI y pasa la función a `Inactive`; la siguiente
invocación falla** y la función vuelve a `Pending` mientras se recrea la interfaz.

Para un blog personal de tráfico bajo esto **no es hipotético**. No se mitiga con NAT ni
con más memoria. Queda registrado como criterio medible de `Task/032` y `Task/040`
([§9](#9-qué-debe-demostrar-cada-tarea-posterior)), y su tratamiento —aceptar el primer
fallo, o mantener actividad mínima— es una decisión de operación de `Task/032`, no de
esta tarea.

---

## 3. D-22 — Red, topología y capacidad · **Resuelta**

### 3.1 Región

No existe región canónica de producción. `us-east-1` aparece en
`terraform/entornos/local/local.tfvars` como valor de **laboratorio** y en
`produccion.tfvars.example` como **plantilla** que el propio archivo marca «región y
nombres reales → ETAPA 10». `us-east-2` aparece una sola vez en el repositorio, en el
reporte de `Task/028`, y solo describe el CloudShell donde vivió temporalmente el
*state* del *bootstrap* OIDC: **no es una decisión de región**. Los recursos reales de
`Task/028` —proveedor OIDC y rol IAM— son **globales**.

| Región | Instancia t4g.micro Single-AZ | gp3 20 GiB | Total base | Latencia esperable desde Guatemala | Observaciones |
| --- | --- | --- | --- | --- | --- |
| **us-east-2** (Ohio) | 11.68 | 2.30 | **13.98** | Buena: mismo corredor que us-east-1 | Precio idéntico a us-east-1. Menos saturada. RDS Proxy sin restricción de AZ documentada |
| us-east-1 (N. Virginia) | 11.68 | 2.30 | **13.98** | Buena, la mejor típica hacia Centroamérica | Igual precio. **`use1-az3` no admite RDS Proxy** (irrelevante si no se adopta) |
| us-west-2 (Oregón) | 11.68 | 2.30 | **13.98** | Peor: costa oeste | Mismo precio, sin ventaja |
| sa-east-1 (São Paulo) | 24.82 | 4.38 | **29.20** | **Peor que us-east-\*** desde Guatemala: el tráfico suele transitar por Norteamérica | **2.1× el costo** sin ganancia de latencia |

**Región elegida: `us-east-2` (Ohio).** Precio mínimo empatado con us-east-1, latencia
equivalente en la práctica hacia Centroamérica, y sin la restricción de AZ que us-east-1
documenta para RDS Proxy — irrelevante hoy, gratuita como margen. `sa-east-1` queda
descartada: cuesta el doble y **no** acerca la base de datos al usuario.

La latencia real entre la Lambda y RDS es **intra-región**, no depende de la distancia al
autor, y **R-34** ya asigna su medición a `Task/032`. La cercanía al autor solo afecta al
acceso administrativo, que es ocasional.

> **Decidido por el usuario el 2026-09-27 (H-1):** `us-east-2` aceptada como **región
> objetivo** de la arquitectura RDS y de toda decisión que dependa de región. La
> justificación es la investigada arriba; el agente recomendó y el usuario decidió.
>
> Consecuencias que quedan fijadas: los precios de la [§7](#7-modelo-económico-y-gate-de-d-13)
> son los de `us-east-2`; el *trust store* usa el bundle regional
> **`us-east-2-bundle.pem`** ([§5.1](#51-tls-con-verificación)); el interface endpoint, si
> algún día se adoptara, cuesta **0.010 USD/h por AZ**; y `terraform/entornos/produccion/`
> declarará `region = "us-east-2"` cuando `Task/031` lo haga operativo. El valor
> `us-east-1` que hoy aparece en el laboratorio y en la plantilla **no se toca en esta
> tarea**: el laboratorio es un destino distinto.

### 3.2 Motor y versión

- **Motor:** Amazon RDS for PostgreSQL. Fijado por ADR-010; no se reabre.
- **Versión candidata: `17.11`.**

No es una elección arbitraria: **es exactamente la versión que el proyecto ya usa en
local**. `personal-blog-infra/.env` fija
`POSTGRES_VERSION=17.11-alpine@sha256:18cfe3ef…` y el CI del backend levanta el mismo
`postgres:17.11-alpine` con idéntico digest. RDS publicó `17.11` el **25 de agosto de
2026** y su fin de soporte estándar de minor es **septiembre de 2027**; el major 17
tiene fin de soporte estándar el **28 de febrero de 2030**.

| Alternativa | Por qué no | Dato |
| --- | --- | --- |
| `18.6` | Rompe la paridad con local y con el CI del backend, sin necesidad demostrada | Major 18 soportado hasta 2031, pero local está en 17 |
| `16.15` | Retrocede respecto a local sin ganar nada | Major 16 hasta 2029 |
| `17.8`, `16.12`, `15.16`, `14.21` | **`NO_CREATE`**: no se pueden crear instancias nuevas con ellas | Calendario de versiones |
| `13.x` | Fin de soporte estándar **28 de febrero de 2026**: ya pasó | Solo vía Extended Support, con cargo |

Regla que queda fijada: **la versión de producción sigue a la de local, no al revés.**
Subir el major en producción exige subirlo antes en local y en el CI del backend.

### 3.3 Clase, CPU y memoria

**Candidata: `db.t4g.micro`** — 2 vCPU, 1 GiB, Graviton (arm64).

| Clase | vCPU | Memoria | USD/mes Single-AZ (us-east-2) | Veredicto |
| --- | --- | --- | --- | --- |
| **db.t4g.micro** | 2 | 1 GiB | **11.68** | **Candidata.** La más pequeña de generación actual |
| db.t4g.small | 2 | 2 GiB | 23.36 | Solo si la memoria de 1 GiB se demuestra insuficiente |
| db.t3.micro | 2 | 1 GiB | 13.14 | Peor precio que t4g.micro por la misma capacidad (x86) |
| db.t4g.medium | 2 | 4 GiB | 47.45 | Muy por encima de la necesidad de un blog |

La arquitectura de CPU de RDS **no** está acoplada a la de la Lambda: son procesos
distintos y el contrato entre ellos es el protocolo PostgreSQL sobre TLS. Elegir
Graviton en RDS no obliga a `lambda_arquitectura`, que sigue siendo de `Task/032`.

**Riesgo aceptado explícitamente:** 1 GiB es poco. Condiciona `max_connections` a **112**
([§6](#6-d-12--presupuesto-preliminar-de-conexiones--aprobado-d-12-sigue-abierta)) y **excluye IAM DB
authentication** ([§5.4](#54-autenticación-sql-iam-db-auth)). La clase es un cambio
*in-place* con reinicio, así que el error es **reversible y baratо de corregir**; la
región y la clave KMS no lo son. Subir a `t4g.small` duplica el costo: solo con medición
de `Task/032`/`Task/040` que lo justifique.

**CPU Credits.** Las clases T facturan el exceso de *burst* a **USD 0.09/vCPU-hora**
(también aparece una tarifa de 0.075 según el tipo de uso). Con tráfico de blog no
debería devengarse, pero **no es cero garantizado**: `Task/031` añade alarma de
`CPUCreditBalance` y `Task/040` lo mide bajo carga.

### 3.4 Almacenamiento, IOPS y throughput

- **Tipo: gp3.** `gp2` cuesta lo mismo (0.115 USD/GiB-mes) y ofrece línea base peor
  (3 IOPS/GiB con *burst*) frente a la base fija de gp3. `io2` es
  desproporcionado. `magnetic` está **deprecado**: no se pueden crear instancias nuevas.
- **Tamaño inicial: 20 GiB**, el mínimo de gp3. El esquema del MVP son tablas de texto
  y metadatos; los medios viven en S3, no en la base de datos.
- **IOPS y throughput: no se configuran, y no hay línea de costo.** Para PostgreSQL con
  **20–399 GiB**, gp3 incluye **3.000 IOPS y 125 MiB/s** de línea base y la documentación
  marca el rango aprovisionable como *«Not applicable»*: por debajo de 400 GiB **no se
  puede** aprovisionar extra. La decisión se cierra por la propia mecánica del servicio.
- **Autoscaling de almacenamiento: sí, con techo bajo.** `max_allocated_storage = 50`
  GiB. Protege de `storage_full` —que detiene la base de datos y con ella los *backups*
  automáticos, **R-32**— sin abrir un crecimiento ilimitado. Cruzar 400 GiB cambiaría la
  línea base a volumen *striped*; el techo de 50 GiB garantiza que eso no ocurre por
  accidente.
- **Máximo de la clase:** `db.t4g.micro` admite hasta **6 TiB** con PostgreSQL. El techo
  de 50 GiB es una decisión de presupuesto, no un límite técnico.

### 3.5 VPC, subnets y DB subnet group

| Elemento | Decisión | Motivo |
| --- | --- | --- |
| VPC | Una, dedicada. CIDR `10.40.0.0/16` | No solapa con rangos habituales de Docker local (`172.17/16`, `172.18/16`) ni con el `10.0.0.0/16` de los ejemplos, para que un *peering* o VPN futuro no colisione |
| Subnets privadas | **2**, en 2 AZ: `10.40.0.0/20` y `10.40.16.0/20` | El **DB subnet group exige subnets en al menos dos AZ incluso para Single-AZ**. Son las mismas que usa la Lambda |
| Subnets públicas | **Ninguna** | Nada necesita IP pública. Una subnet pública **no** da IP pública a la Lambda, así que no aporta nada y sí superficie |
| DB subnet group | Sobre las 2 subnets privadas | Requisito del servicio |
| Tabla de rutas | Una por subnet privada, **sin ruta 0.0.0.0/0** | Clase D vacía: no hay destino público que enrutar |
| Internet Gateway | **Ninguno** | No hay tráfico público |
| NAT Gateway | **Ninguno** — ver [§4](#4-egress-y-nat--decisión-negativa-razonada) | Sin necesidad demostrada |
| `publicly_accessible` | **`false`**, explícito | ADR-010 y **R-30** |
| DNS de la VPC | `enable_dns_support` y `enable_dns_hostnames` en **`true`** | El *endpoint* de RDS se resuelve por DNS; conectarse por IP está prohibido por la propia documentación de RDS |

**Tener 2 subnets en 2 AZ no selecciona Multi-AZ.** Es un requisito del DB subnet group.
La disponibilidad se decide en [§3.7](#37-single-az-frente-a-multi-az).

### 3.6 Security groups

Tres grupos, sin reglas amplias y sin `0.0.0.0/0` en ninguna dirección.

| SG | Ingress | Egress | Nota |
| --- | --- | --- | --- |
| `sg-lambda` | **Ninguno** | TCP 5432 → `sg-rds`; HTTPS 443 → *prefix list* de S3 (gateway endpoint) | Egress por destino, nunca `0.0.0.0/0` |
| `sg-rds` | TCP 5432 ← **`sg-lambda`** y ← `sg-admin`, por **referencia de grupo**, nunca por CIDR | **Ninguno** | Una base de datos no inicia conexiones salientes |
| `sg-admin` | **Ninguno** | TCP 5432 → `sg-rds` | Ejecutor privado de administración y migraciones ([§8](#8-d-24--canal-privado-de-administración-y-migraciones--resuelta)) |

Referencia por grupo y no por CIDR: si las subnets cambian, la regla sigue siendo
correcta, y ningún rango accidental entra por coincidencia de direcciones.

### 3.7 Single-AZ frente a Multi-AZ

| Criterio | Single-AZ | Multi-AZ (instancia en espera) |
| --- | --- | --- |
| Costo bruto/mes (us-east-2) | **13.98** | **27.96** (instancia ×2 y almacenamiento ×2) |
| RTO ante fallo de AZ | Horas: restaurar desde *snapshot* o PITR a instancia nueva, más cambio de `DATABASE_URL` | 1–2 minutos, *failover* automático sin cambiar el *endpoint* |
| RPO | Igual en ambos: PITR ~5 min | Igual |
| Mantenimiento | Corte durante actualizaciones menores | Casi sin corte |
| Aprendizaje | Cubre lo esencial: privacidad, TLS, KMS, *backups*, restore | Añade *failover*, valioso pero no imprescindible ahora |
| Criticidad real | Blog personal, un autor, contenido reproducible desde Git y S3 | — |

**Recomendación: Single-AZ.** Multi-AZ duplica exactamente la partida que ya incumple
D-13 y compra un RTO de minutos para un blog que tolera horas.

**Riesgo que se acepta, con nombre y apellido (R-29):** un fallo de la AZ deja el blog
**sin contenido dinámico** hasta que un humano ejecute el runbook de restore. Single-AZ
**no elimina el punto único de fallo**; lo hace barato y recuperable. Las contrapartidas
que sí se adoptan: PITR activo, *deletion protection*, *snapshot* final, runbook escrito
antes de operar y restore **demostrado** en `Task/031`.

Multi-AZ es un cambio *in-place* posterior. Se reconsidera si el blog deja de ser
personal o si `Task/040` mide un RTO inaceptable.

### 3.8 Ventana de mantenimiento, actualizaciones y *parameter group*

| Parámetro | Valor | Motivo |
| --- | --- | --- |
| `backup_window` | `07:00–07:30` UTC (01:00–01:30 en Guatemala, UTC−6) | Madrugada local, mínimo tráfico |
| `maintenance_window` | `sun:08:00–sun:09:00` UTC | Después del *backup*, sin solaparlo, en domingo |
| `auto_minor_version_upgrade` | **`true`** | Parches de seguridad sin intervención. Con Single-AZ implica un corte breve en la ventana, que es exactamente lo que la ventana existe para acotar. Desactivarlo obligaría a un proceso manual que **R-42** identifica como fuente de *drift* |
| Actualización de major | **Manual y nunca automática** | Cambia el comportamiento. Se sube primero en local y en CI del backend (§3.2) |
| *Parameter group* | **Personalizado**, familia `postgres17`. Costo **0.00** | Hace explícitos los valores en Terraform en lugar de depender de defaults |

Valores explícitos del *parameter group*:

| Parámetro | Valor | Por qué explícito |
| --- | --- | --- |
| `rds.force_ssl` | `1` | **Ya es el default en PostgreSQL 15 y posteriores**, pero un default no es un contrato: declararlo impide que una versión futura lo cambie en silencio |
| `ssl_min_protocol_version` | `TLSv1.2` | Confirma el default y lo fija |
| `log_statement` | `ddl` | Registra cambios de esquema sin volcar datos ni parámetros de consultas. Coherente con **R-39** y **O-08** |
| `log_min_duration_statement` | `1000` (ms) | Diagnóstico de consultas lentas sin registrar todo el tráfico |
| `log_connections` / `log_disconnections` | `1` | Necesario para diagnosticar agotamiento de conexiones (**R-33**) |
| `superuser_reserved_connections` | `3` (default) | Explícito porque entra en el presupuesto de conexiones (§6) |

**No** se activa `log_min_duration_statement = 0` ni `log_statement = all`: volcarían
sentencias con parámetros a CloudWatch y de ahí, por **D-20**, a un tercero. `Task/031`
fija umbrales finales y `Task/032` verifica que no haya PII en los logs.

---

## 4. Egress y NAT — decisión negativa razonada

**No se adopta NAT Gateway.** No es una omisión: es el resultado del inventario de la
[§2](#2-inventario-de-tráfico-de-la-lambda-ae-sobre-el-código-vigente), donde **la clase
D está vacía**.

| Destino | Ruta elegida | Tarifa de *endpoint* |
| --- | --- | --- |
| PostgreSQL | Intra-VPC, SG a SG | 0.00 |
| S3 | **Gateway endpoint** | **0.00** — el gateway endpoint no tiene cargo por hora |
| Logs de Lambda, credenciales del rol, invocación de API Gateway, métricas y *backups* de RDS | Plano de servicio de AWS, fuera de la VPC de la aplicación | 0.00 |
| SSM, Secrets Manager, KMS, STS por SDK | **No se llaman desde el código vigente** | 0.00 |

Qué haría falta para que NAT entrara en la arquitectura, y no basta con una de las tres:

1. Un destino de **clase D real** en el código, identificado por archivo y línea.
2. Que ese destino **no** tenga *endpoint* de VPC, o que el *endpoint* cueste más que NAT.
3. Una **decisión explícita del usuario**, porque NAT está excluido en
   `PROJECT_INSTRUCTIONS.md` §17 y en ADR-010.

**IPv6 no se adopta como sustituto.** Exigiría subnets *dual-stack*, destinos
compatibles y controles de egress propios, y Lambda solo admite egress IPv6 si **todas**
las subnets conectadas son *dual-stack*. Añade superficie para resolver un problema que
no tenemos.

**Política del bucket de S3 — advertencia para `Task/030`.** Un `Deny` global por
`aws:SourceVpce` rompería las **URL prefirmadas** que el navegador usa, porque el
navegador no entra por el *endpoint* de la VPC. La firma es local y no necesita red; la
descarga sí. Validar con **D-08** en `Task/030`.

---

## 5. D-23 — TLS, KMS, secretos y autenticación SQL · **Resuelta**

### 5.1 TLS con verificación

| Punto | Decisión |
| --- | --- |
| Modo del cliente | **`sslmode=verify-full`**: valida cadena **y** *hostname*. `verify-ca` no detecta suplantación del nombre |
| Obligatoriedad en el servidor | `rds.force_ssl = 1` explícito (§3.8) |
| CA | **`rds-ca-rsa2048-g1`**, el **default** de RDS, con rotación automática del certificado de servidor |
| *Trust store* del cliente | Bundle **regional** de la región elegida, p. ej. `us-east-2-bundle.pem` desde `truststore.pki.rds.amazonaws.com`. Solo el **root**: registrar intermedios rompe la rotación automática |
| Rotación de la CA | El **certificado de servidor** lo rota RDS automáticamente (validez 1 año si el motor admite rotación sin reinicio; 3 si no). La **CA raíz** vive décadas. `Task/031` registra el `ValidTill` real con `describe-certificates` |

**Hallazgo del código, con consecuencia concreta.** No hay rastro de `sslmode`,
`sslrootcert` ni `ssl` en `app/shared/database/` ni en `app/shared/configuration/`:
`sqlalchemy_url` solo antepone el driver `psycopg`, y `connect_args` únicamente fija
`connect_timeout`. Por tanto:

1. **El contrato de TLS viaja en la propia `BLOG_DATABASE_URL`**, como
   `?sslmode=verify-full&sslrootcert=<ruta>`. **El backend no necesita cambios de
   código.** Esto confirma que `Task/029` no toca `personal-blog-backend`.
2. **El artefacto ZIP de la Lambda debe incluir el bundle de la CA** y `sslrootcert`
   debe apuntar a su ruta dentro del paquete. Es un requisito de empaquetado para
   `Task/032`, no de esta tarea.
3. Un caso negativo obligatorio de `Task/040`: con `sslrootcert` ausente o CA
   equivocada, la conexión **debe fallar**. Si conecta igual, `verify-full` no está
   activo de verdad.

### 5.2 Cifrado en reposo y KMS

| Punto | Decisión | Costo |
| --- | --- | --- |
| Cifrado en reposo | **Activado**, obligatorio. Cubre datos, *backups*, *snapshots* y réplicas | 0.00 |
| Clave | **Gestionada por AWS (`aws/rds`)** | **0.00** |
| Alternativa CMK propia | Aporta política, rotación y auditoría propias | **+1.00/mes** por versión de clave |

**Recomendación: clave gestionada por AWS.** La CMK aporta control de política y
*grants* que un blog de un solo administrador no necesita, y añade una forma nueva de
perder los datos de manera irreversible: **si se borra o deshabilita la clave, los
*snapshots* cifrados con ella no se pueden restaurar** (**R-35**).

Reglas que se fijan igualmente:

- **La clave se elige antes de crear la instancia.** Cambiarla no es una modificación
  *in-place*: obliga a *snapshot*, copia con otra clave y restauración.
- **No se deshabilita ni se programa el borrado de ninguna clave como parte de una
  prueba.** Ni en `Task/031` ni en `Task/040`.
- KMS tiene **dos usos distintos** que no se confunden: cifrado de RDS y descifrado de
  secretos de SSM. Un permiso IAM no es conectividad.
- *Free tier* de KMS: 20.000 peticiones/mes. Con una conexión que descifra al arrancar
  el entorno, queda holgadísimo.

### 5.3 Credenciales y almacén de secretos

**Tres identidades SQL separadas**, con contraseñas distintas y rotación independiente:

| Identidad | Uso | Privilegios | Quién la usa |
| --- | --- | --- | --- |
| `blogadmin` (*master*) | Creación inicial y recuperación | Propietario de la base; `rds_superuser` | **Nadie en operación normal.** Solo el canal privado ([§8](#8-d-24--canal-privado-de-administración-y-migraciones--resuelta)) |
| `blog_app` | La aplicación en Lambda | `CONNECT`, `USAGE` en el esquema, y `SELECT/INSERT/UPDATE/DELETE` sobre las tablas. **Sin DDL** | Lambda de la aplicación |
| `blog_migrate` | Alembic | DDL sobre el esquema y DML necesario | Solo el ejecutor de migraciones |

Que `blog_app` **no tenga DDL** es la garantía estructural de que una migración no puede
ejecutarse como efecto lateral del arranque de la Lambda: aunque alguien lo intentara, el
motor lo rechazaría.

**SSM Parameter Store `SecureString` frente a Secrets Manager:**

| Criterio | SSM `SecureString` (estándar) | Secrets Manager |
| --- | --- | --- |
| Costo | **0.00** — los parámetros estándar no tienen cargo | **0.40/secreto/mes** + 0.05/10.000 peticiones |
| Rotación | Manual o con automatización propia | **Rotación gestionada**, con integración RDS |
| Integración con RDS Proxy | **No sirve**: Proxy exige Secrets Manager o IAM DB auth | Nativa |
| Tamaño de valor | 4 KB en el tier estándar: una `DATABASE_URL` cabe de sobra | 64 KB |
| Base ya adoptada | **Sí**, ADR-003 y ADR-008 | No |

**Recomendación: SSM `SecureString`, sin migrar.** La rotación gestionada es la única
ventaja real, y con tres credenciales que cambian rara vez no justifica ni el costo ni
abandonar la base ya decidida. Con dos secretos, Secrets Manager costaría **+0.80/mes**
sobre un presupuesto AWS que ya está desbordado ([§7](#7-modelo-económico-y-gate-de-d-13)).

**Condición objetiva para reconsiderarlo:** si se adopta RDS Proxy —que **exige**
Secrets Manager o IAM DB auth— o si la rotación pasa a ser un requisito con frecuencia
definida. Ambas cosas se deciden con evidencia, no por inercia.

**Entrega del secreto a la Lambda: en despliegue, no en *runtime*.** El valor se
resuelve en el `apply` y llega como variable de entorno cifrada de la función. Motivos:
el backend **no tiene lector de SSM** hoy (§2), leer en *runtime* exigiría un
**interface endpoint SSM a +14.60/mes** (§7 B6) y añadiría latencia al arranque en frío.
Contrapartida aceptada: **rotar la credencial exige redesplegar**. Es asumible con tres
credenciales estables. Si `Task/032` demuestra que hace falta rotación sin despliegue,
entonces el lector en *runtime* y su endpoint entran con su propio costo y su plan
test-first en `Task/032` —no aquí.

**Reglas de custodia, sin excepción:**

- Ningún secreto en Git, `.tfvars` versionados, *outputs*, planes publicados ni logs.
- `sensitive = true` **no** elimina un valor del *state*. El *state* que contenga la
  contraseña es material sensible y su custodia es **D-06**, owner `Task/030`.
- La contraseña *master* **se genera en `Task/031`** por procedimiento privado y
  autorizado. **`Task/029` no genera ni lee ningún secreto.**

### 5.4 Autenticación SQL: IAM DB auth

**No se adopta.** La razón es técnica y decisiva, no de gusto:

> La documentación de IAM database authentication exige **entre 300 y 1000 MiB de memoria
> extra** en la instancia para conectividad fiable, y advierte explícitamente que en una
> clase *burstable* hay que reducir *buffers* y caché en la misma cantidad.

`db.t4g.micro` tiene **1 GiB en total**. IAM DB auth consumiría entre el **30 % y el
100 %** de la memoria de la instancia. Es incompatible con la clase elegida.

Argumentos secundarios, todos en la misma dirección:

- Token de **15 minutos**: obliga a regenerar y a manejar la expiración en el cliente.
- **CloudWatch y CloudTrail no registran la autenticación IAM**: se pierde rastro.
- En PostgreSQL, el rol `rds_iam` **toma precedencia** sobre la contraseña: un error de
  configuración puede dejar fuera al administrador (**R-43**).
- Con `verify-full` y contraseñas en SSM, el beneficio marginal es pequeño.

**Condición objetiva para reconsiderarlo:** si se sube a `db.t4g.small` (2 GiB) **y** se
adopta RDS Proxy, o si aparece un requisito de acceso humano federado. Se reevalúa en
`Task/031` si la clase cambia.

---

## 6. D-12 — Presupuesto preliminar de conexiones · **Aprobado; D-12 sigue abierta**

**Derivado, no medido.** La medición es de `Task/032`; la saturación, de `Task/040`.

### 6.1 Configuración real del backend hoy

Leída de `app/shared/configuration/settings.py`. **No se modifica en esta tarea**: la
ficha no lo autoriza y el cambio pertenece a `Task/032`.

| Ajuste | Default actual | Nota |
| --- | --- | --- |
| `database_pool_size` | **5** | Válido en local; **no** es dimensionamiento de producción |
| `database_pool_max_overflow` | **5** | Pool efectivo máximo **10 por proceso** |
| `database_pool_recycle_seconds` | 1800 | |
| `database_connect_timeout_seconds` | 10 | |
| `pool_pre_ping` | `True` (en `session.py`) | Detecta conexiones caducadas |

El motor y la fábrica de sesiones están memorizados con `lru_cache`: **un entorno de
ejecución caliente conserva su pool entre invocaciones.** No se puede suponer una
conexión por invocación ni que todas desaparezcan al terminar.

### 6.2 Presupuesto derivado

`max_connections` de RDS PostgreSQL es
`LEAST({DBInstanceClassMemory/9531392}, 5000)`. Para `db.t4g.micro` (1 GiB):
`LEAST(1.073.741.824 / 9.531.392, 5000) = LEAST(112,6; 5000) = **112**`.

| Concepto | Conexiones |
| --- | --- |
| `max_connections` derivado | **112** |
| − `superuser_reserved_connections` | −3 |
| = no privilegiadas | 109 |
| − migraciones (canal D-24) | −5 |
| − administración humana | −3 |
| − monitorización y diagnóstico | −2 |
| − margen de *churn*, reintentos y versiones concurrentes | −10 |
| **= presupuesto para la aplicación** | **89** |

Entornos Lambda concurrentes que caben, `89 ÷ pool_efectivo`:

| `pool_size` | `max_overflow` | Pool efectivo | Entornos que caben | Veredicto |
| --- | --- | --- | --- | --- |
| 5 | 5 | 10 | **8** | **Default local: no trasladar.** 8 entornos concurrentes agotarían la base |
| 2 | 3 | 5 | 17 | Gasta *slots* sin necesidad |
| **1** | **1** | **2** | **44** | **Candidato** |
| 1 | 0 | 1 | 89 | Sin margen para la sonda de `/ready` en la misma conexión |

**Candidato: `pool_size = 1`, `max_overflow = 1`, *Reserved Concurrency* = 20.** Techo de
`2 × 20 = 40` conexiones de aplicación, muy por debajo de las 89 disponibles. La
justificación es la forma del backend: **es síncrono y una invocación atiende una
petición** (documentado en `session.py`), así que un pool grande por proceso no compra
concurrencia — solo reserva *slots* que otro entorno no podrá usar.

`Task/032` fija los valores definitivos **con medición**: memoria, *timeout*,
concurrencia reservada, `pool_recycle` frente a `idle_in_transaction_session_timeout` y
comportamiento del arranque en frío.

### 6.3 RDS Proxy — decisión negativa con criterio objetivo

**No se adopta ahora.**

| Criterio | Sin Proxy | Con Proxy |
| --- | --- | --- |
| Costo/mes | **0.00** | **+21.90** (0.015 USD/vCPU-hora × 2 vCPU × 730 h) |
| Almacén de secretos | SSM, 0.00 | **Exige Secrets Manager o IAM DB auth**: +0.80/mes |
| Costo total añadido | — | **+22.70/mes**, ~1,6× la instancia entera |
| Conexiones | 89 disponibles frente a 40 previstas: **margen de 2,2×** | Multiplexa, pero no da conexiones ilimitadas |
| *Pinning* | No aplica | **PostgreSQL no admite filtros de *session pinning***; cualquier sentencia de más de 16 KB fija la sesión |
| Compatibilidad | psycopg 3 directo, ya probado en local | Sin cancelación de consultas, sin replicación en *streaming*, exige que exista la base `postgres` |
| Complejidad | Ninguna añadida | Recurso, SG, secretos, IAM y modo de autenticación nuevos |

Con 40 conexiones previstas frente a 89 disponibles, **el problema que Proxy resuelve no
existe todavía**. Y su costo supera al de la instancia.

**Criterio objetivo para incorporarlo.** Basta **uno** de estos, medido en `Task/032` o
`Task/040`, no estimado:

1. `DatabaseConnections` supera de forma sostenida el **70 %** del presupuesto de
   aplicación (≥ 62 de 89) con la concurrencia reservada ya acotada.
2. Se observan rechazos por `too many connections` con la configuración candidata.
3. El costo de establecer conexión domina la latencia de la petición de forma medible
   —comparado contra el mismo escenario con pool caliente—.
4. Se adopta Multi-AZ y se requiere preservar conexiones durante el *failover*.

Y en cualquier caso: **el gasto adicional exige decisión explícita del usuario**, porque
D-13 ya está desbordada sin Proxy. **No se instala PgBouncer**: con RDS pierde objeto y
exigiría un *host*, que la arquitectura excluye.

---

## 7. Modelo económico y gate de D-13

**El techo global de D-13 no se cambia: sigue en USD 20/mes.** Lo que cambia, por decisión
del usuario del 2026-09-27 (H-2), es que el **sublímite AWS de USD 5/mes queda suspendido
por una excepción acotada y fechada** durante la etapa experimental financiada con créditos:
**EX-029-D13**, definida en la [§7.5](#75-ex-029-d13--excepción-acotada-al-sublímite-aws).

Los créditos **siguen sin hacer gratis el costo bruto**: AWS Budgets excluye Credit y
Refund, y este documento mantiene separadas las cuatro cifras —**bruto**, **crédito
consumido**, **desembolso** y **escenario poscrédito**— exactamente como exige el canónico.

### 7.1 Precios unitarios usados (lista del 2026-09-24)

| Partida | us-east-2 / us-east-1 | sa-east-1 |
| --- | --- | --- |
| `db.t4g.micro` Single-AZ | 0.016 USD/h | 0.034 USD/h |
| `db.t4g.micro` Multi-AZ | 0.032 USD/h | 0.069 USD/h |
| `db.t4g.small` Single-AZ | 0.032 USD/h | 0.069 USD/h |
| gp3 Single-AZ | 0.115 USD/GiB-mes | 0.219 USD/GiB-mes |
| gp3 Multi-AZ | 0.230 USD/GiB-mes | 0.438 USD/GiB-mes |
| *Backup* sobre la asignación gratuita | 0.095 USD/GB-mes | 0.095 USD/GB-mes |
| CMK KMS | 1.00 USD/versión-mes | 1.00 USD/versión-mes |
| Secreto de Secrets Manager | 0.40 USD/mes | 0.40 USD/mes |
| RDS Proxy | 0.015 USD/vCPU-h | 0.015 USD/vCPU-h |
| Interface endpoint | 0.010 USD/h por AZ | 0.021 USD/h por AZ |
| Gateway endpoint S3 | **0.00** | **0.00** |
| Parámetro estándar de SSM | **0.00** | **0.00** |

*Free tier* relevante: **backup gratis hasta el total de almacenamiento aprovisionado en
la región**; KMS 20.000 peticiones/mes; CloudWatch 10 alarmas, 10 métricas
personalizadas, 5 GB de ingesta de logs, 5 GB de almacenamiento y 1.000.000 de
peticiones de API.

### 7.2 Escenario A — candidato recomendado

Single-AZ, gp3 20 GiB, clave gestionada por AWS, SSM estándar, gateway endpoint S3, sin
Proxy, sin endpoints de interfaz, sin NAT.

| Partida | Cálculo | us-east-2 | sa-east-1 |
| --- | --- | --- | --- |
| Instancia | 0.016 × 730 | **11.68** | 24.82 |
| Almacenamiento | 20 × 0.115 | **2.30** | 4.38 |
| IOPS / throughput | no aprovisionables bajo 400 GiB | **0.00** | 0.00 |
| *Backup* (≤ 20 GB) | dentro de la asignación gratuita | **0.00** | 0.00 |
| KMS | clave gestionada por AWS | **0.00** | 0.00 |
| Secretos | SSM estándar | **0.00** | 0.00 |
| *Endpoints* | solo gateway S3 | **0.00** | 0.00 |
| NAT | no adoptado | **0.00** | 0.00 |
| CloudWatch | métricas básicas; logs y alarmas dentro del *free tier* | **0.00** | 0.00 |
| **Total RDS bruto/mes** | | **13.98** | **29.20** |

### 7.3 Variantes y lo que cuesta cada decisión (us-east-2)

| Variante | Total bruto/mes | Delta sobre A |
| --- | --- | --- |
| **A — candidato** | **13.98** | — |
| Multi-AZ | 27.96 | +13.98 |
| Clase `t4g.small` | 25.66 | +11.68 |
| CMK propia | 14.98 | +1.00 |
| Secrets Manager (2 secretos) | 14.78 | +0.80 |
| **RDS Proxy (arrastra Secrets Manager)** | **36.68** | **+22.70** |
| 1 interface endpoint en 2 AZ | 28.58 | +14.60 |
| *Backup* de 40 GB (20 excedentes) | 15.88 | +1.90 |

### 7.4 Escenario de restore temporal

PITR y restore de *snapshot* **crean una instancia nueva**; no sobrescriben. Coste puntual
de una prueba de `Task/031` o `Task/040`, no recurrente:

| Concepto | Cálculo | USD |
| --- | --- | --- |
| Instancia temporal, 48 h | 0.016 × 48 | 0.77 |
| Almacenamiento prorrateado, 20 GiB / 48 h | 2.30 × 48/730 | 0.15 |
| **Total por prueba** | | **≈ 0.92** |

Cada prueba de restore exige **limpieza autorizada** al terminar: una instancia temporal
olvidada cuesta lo mismo que la productiva.

### 7.5 EX-029-D13 — excepción acotada al sublímite AWS

**El cálculo primero, sin maquillar.**

| Concepto | USD/mes |
| --- | --- |
| RDS bruto, escenario A en us-east-2 | 13.98 |
| Resto de AWS estimado: Lambda, API Gateway, S3 de medios, bucket de *state*, CloudWatch | ≈ 1.50 |
| **Subtotal AWS bruto** | **≈ 15.48** |
| Sublímite AWS original de D-13 | 5.00 |
| **Exceso sobre el sublímite original** | **+10.48 — 3,1×** |
| No AWS: dominio amortizado; Cloudflare y Grafana en tier gratuito | ≈ 1.00 |
| **Total del proyecto** | **≈ 16.48** |
| **Techo global de D-13 — NO se modifica** | **20.00** |
| Margen restante bajo el techo global | **3.52** |

**El sublímite AWS de USD 5/mes es incompatible con cualquier RDS.** No es un problema de la
configuración elegida: la instancia más pequeña de generación actual, en la región más
barata, con el almacenamiento mínimo y **todas** las opciones de pago descartadas, cuesta
**USD 13.98/mes**. **No existe configuración de RDS que quepa en USD 5.**

ADR-010 y el canónico previeron este caso: *«si no cabe, registrar una nueva decisión
explícita como gate de `Task/029`»*. El usuario la tomó el 2026-09-27.

#### La excepción

| Campo | Valor |
| --- | --- |
| **ID** | **EX-029-D13** |
| **Estado** | **Aceptada y Vigente** — aprobada el 2026-09-27 con `Task/029` |
| **Qué suspende** | **Solo** el sublímite de **USD 5/mes de AWS** de **D-13** |
| **Qué NO cambia** | El **techo global de USD 20/mes**, que se conserva íntegro y con margen de ≈ 3.52. Ningún otro presupuesto sube. **D-13 sigue Resuelta**: esta excepción no la reabre ni la sustituye |
| **Techo efectivo durante la excepción** | El **costo bruto de AWS** puede superar los USD 5/mes, **siempre que quepa bajo el techo global de USD 20/mes** junto con las partidas no AWS. El valor de referencia aprobado es **≈ 15.48/mes**; una desviación material exige revisión |
| **Motivo** | Etapa de **prueba y aprendizaje** financiada con créditos AWS ya disponibles. El objetivo declarado es usar y aprender RDS, VPC, KMS y CloudWatch con **visibilidad del costo bruto real** |
| **Vigencia** | Desde la aprobación de `Task/029` hasta **el agotamiento de los créditos o el 2027-03-15, lo que ocurra primero** |
| **Qué NO autoriza** | **Ningún recurso.** Cada uno sigue exigiendo su tarea propietaria y la autorización explícita del usuario. Tampoco autoriza cambiar de plan, tocar Billing ni elevar el techo global |
| **Al expirar** | **No se renueva por inercia.** Exige la decisión fechada de la [§7.7](#77-la-decisión-fechada-que-sustituye-al-escenario-poscrédito) |
| **Revisión** | `Task/041` y cualquier operación que se acerque al agotamiento o al vencimiento |

**Lo que la excepción explícitamente no dice:** no dice que el costo sea cero, ni que los
créditos lo hagan irrelevante, ni que el proyecto vaya a pagar USD 15.48/mes cuando los
créditos terminen. Esas tres cosas siguen siendo falsas.

**Parar la instancia no es una estrategia de presupuesto.** El máximo son **7 días
consecutivos**; después RDS la arranca sola, y mientras está detenida **se siguen cobrando
el almacenamiento y los *backups***.

### 7.6 Las cuatro cifras, separadas

Datos de créditos **verificados por el usuario** en AWS Console el 2026-09-27 (H-3). El
agente **no lee facturación**: estos valores son los que el usuario reportó.

| Dato observado | Valor |
| --- | --- |
| Saldo de créditos disponible | **USD 120.00** |
| Fecha límite mostrada por AWS | **2027-03-15** |
| Días restantes observados | **170** — coherente con los 169 días exclusivos entre 2026-09-27 y 2027-03-15 contando ambos extremos |
| Moneda | USD |
| Restricciones de servicio | Ninguna observada por el usuario |

#### A · Costo bruto

**≈ USD 15.48/mes de AWS** (13.98 de RDS + 1.50 del resto), más ≈ 1.00 no AWS. **Esta es la
cifra que el proyecto vigila**, y no baja porque haya créditos.

#### B · Crédito elegible consumido

Al ritmo de 15.48/mes, y según cuándo exista realmente RDS —que no es hoy: antes van
`Task/030` y `Task/031`—:

| RDS creado el | Meses hasta el 2027-03-15 | Crédito consumido | Saldo que caducaría sin usar |
| --- | --- | --- | --- |
| 2026-10-01 | 5.42 | 83.92 | **36.08** |
| 2026-10-15 | 4.96 | 76.80 | **43.20** |
| 2026-11-01 | 4.40 | 68.15 | **51.85** |
| 2026-12-01 | 3.42 | 52.89 | **67.11** |
| 2027-01-01 | 2.40 | 37.13 | **82.87** |

> **Hallazgo del cálculo: manda la fecha, no el saldo.** USD 120 al ritmo de 15.48/mes
> durarían **7,75 meses** —hasta el 2027-05-21—, pero solo quedan **5,55 meses** hasta el
> límite. Incluso si RDS existiera **hoy**, el consumo máximo posible antes del vencimiento
> sería **USD 85.95** y **caducarían ≈ USD 34 sin usar**.
>
> Consecuencia práctica: **no tiene sentido optimizar para estirar el saldo.** No es el
> recurso escaso. Lo escaso es el **tiempo**, y cada semana que RDS no existe es crédito que
> se pierde, no que se ahorra. Eso **no** es una razón para acelerar `Task/030` ni para
> saltarse el gate de **D-06**: es una razón para no justificar gasto adicional con el
> argumento de «hay saldo de sobra».

Cifras teóricas y reproducibles. **El consumo real se verificará contra Billing**, y su
propietario es `Task/041`.

#### C · Desembolso real

**USD 0.00 durante la vigencia del plan gratuito.** La documentación de AWS lo dice del Free
Plan: *«No charges incur during usage»* y *«Account closes when credits are depleted or when
the plan duration ends»*. Es decir: en este plan el desembolso no es bajo, es **cero por
construcción**, y el mecanismo que lo garantiza es precisamente el que cierra la cuenta.

Partidas no AWS —dominio, y Cloudflare y Grafana en tier gratuito— quedan **fuera** de los
créditos y son desembolso real, ≈ 1.00/mes.

#### D · Escenario poscrédito

**No es «pagar 15.48/mes».** Por decisión del usuario (H-4), el escenario poscrédito es una
**decisión fechada**, descrita en la [§7.7](#77-la-decisión-fechada-que-sustituye-al-escenario-poscrédito).

### 7.7 La decisión fechada que sustituye al escenario poscrédito

El usuario decidió el 2026-09-27 **no** pasar a Paid Plan ahora y **no** hacerlo
prerrequisito de `Task/031`. La política adoptada es:

> Construir y aprender durante el periodo cubierto por los créditos, **medir el costo real**
> y, **antes** de que se agoten o llegue el **2027-03-15**, pedir una decisión explícita
> entre:
>
> - **A — continuar:** pasar a un plan de pago y asumir ≈ USD 15.48/mes de AWS.
> - **B — no continuar:** desmontar, migrar o preservar lo necesario, sin seguir pagando.

**Ninguna de las dos se presume.** Y la consecuencia de diseño es concreta, no retórica:

> **La opción B solo es ejecutable si los datos ya están fuera de la cuenta.** Los *backups*
> automáticos de RDS, los *snapshots* y el bucket de medios **viven dentro de la cuenta** y
> desaparecen con ella. Una estrategia de recuperación que solo funciona mientras la cuenta
> exista no sirve para este escenario.

Por eso `Task/029` añade a **D-10** una **vía de salida** diseñada aquí y detallada en la
[§10.1](#101-vía-de-salida-exportación-fuera-de-la-cuenta): exportación lógica por el canal
privado hacia S3 y descarga a la estación del autor, **sin NAT, sin servicio nuevo y sin
binario añadido**.

**Reglas que quedan fijadas para que la decisión no se tome por omisión:**

1. **Ningún runbook depende de una renovación automática ni de una decisión implícita.** Si
   nadie decide, el resultado por defecto es la **pérdida** de la cuenta y sus datos, así
   que el silencio **no** es una opción neutra.
2. La fecha **2027-03-15** y el umbral de **saldo** son un **gate operativo** con
   propietario: `Task/041`, y cualquier operación que se acerque al vencimiento.
3. **La vía de salida debe estar probada antes de necesitarla**, con el mismo criterio que
   el resto de esta tarea: un *backup* que nunca se restauró no cuenta. Owner de la prueba:
   `Task/040`.
4. Se recomienda **fijar un recordatorio operativo con antelación suficiente** —del orden
   de 30 días antes del 2027-03-15— para que la decisión se tome con margen y no el mismo
   día. `Task/041` lo materializa.

Riesgo asociado, reformulado: **R-47** en [STATUS](../project-management/STATUS.md).

### 7.8 D-19 — Grafana Cloud

Sigue **abierta**; owner de la verificación, `Task/031`, antes de integrar. Lo que aporta
esta tarea al modelo:

- El objetivo es el **tier gratuito**, que es una preferencia presupuestaria y no una
  dependencia arquitectónica (**R-38**). Ninguna cifra comercial de Grafana se persiste
  aquí.
- El costo que **sí** es de AWS y sí se modela: las consultas de la API de CloudWatch que
  la integración **D-20** hará. `GetMetricData` cuesta **0.01 USD/1.000 métricas
  solicitadas**, con **1.000.000 de peticiones/mes** en el *free tier*. Un sondeo
  agresivo de muchas métricas es lo único que podría sacarlo del tier gratuito;
  `Task/031` fija el intervalo y el conjunto de métricas con ese límite a la vista.

---

## 8. D-24 — Canal privado de administración y migraciones · **Resuelta**

Con RDS privado **no hay SSH ni *host***, y un *runner* público de GitHub **no alcanza la
base de datos solo por tener identidad OIDC**: le falta la ruta de red.

### 8.1 Comparación de mecanismos

| Mecanismo | Alcanza RDS privado | Costo/mes | Servicios excluidos | Veredicto |
| --- | --- | --- | --- | --- |
| **Lambda ejecutora dedicada** en las subnets privadas, invocada por el plano de control | **Sí** | ≈ **0.00** — *free tier* y uso esporádico | Ninguno | **Elegido** |
| *Runner* público de GitHub Actions | **No**: sin ruta a la VPC | 0.00 | Ninguno | Descartado: no funciona |
| EC2 *bastion* o *host* efímero | Sí | Instancia + almacenamiento | **EC2 excluido** (§17) | Descartado sin decisión explícita |
| SSM Session Manager con *port forwarding* | Sí | Interface endpoints | **Exige una instancia gestionada: EC2** | Descartado |
| Client VPN | Sí | **0.10 USD/h por asociación** ≈ 73/mes, más horas de conexión | Ninguno, pero desproporcionado | Descartado por costo |
| Abrir RDS a Internet temporalmente | Sí | 0.00 | — | **Prohibido.** ADR-010, **R-30** |

**Elegido: Lambda ejecutora dedicada.** Reutiliza la VPC, las subnets y el patrón de
empaquetado que el proyecto ya domina, no introduce ningún servicio excluido y su costo
es despreciable para ejecuciones esporádicas.

### 8.2 Contrato del ejecutor

| Aspecto | Contrato |
| --- | --- |
| **Modos** | **Cuatro, y solo cuatro:** `upgrade`/`downgrade` de Alembic (§8.1) · `purge` de retención (§8.6) · `export` fuera de la cuenta ([§10.1](#101-vía-de-salida-exportación-fuera-de-la-cuenta), añadido el 2026-09-27 por la decisión H-4) · `verify` de solo lectura para el restore de `Task/031` (§8.4). Un modo nuevo exige justificarlo, no se añade por conveniencia |
| Identidad de ejecución | Rol IAM **propio**, distinto del rol de la Lambda de la aplicación, del rol de validación de `Task/028`, del de despliegue y del de Terraform |
| Identidad SQL | **`blog_migrate`** para migraciones; `blogadmin` **solo** para recuperación, en operación explícitamente autorizada |
| Red | Las mismas subnets privadas; SG `sg-admin`; **sin ruta a Internet** |
| Artefacto | ZIP con Alembic, `psycopg`, el bundle de la CA y las migraciones. **Versionado y con digest**, como el de la aplicación |
| Invocación | Por el plano de control de AWS —`lambda:InvokeFunction`— por una identidad humana autorizada o, desde `Task/038`, por el rol de despliegue |
| Serialización | **Obligatoria.** Concurrencia reservada **= 1**, más el bloqueo de aviso propio de Alembic. Dos migraciones simultáneas no pueden ocurrir |
| Duración máxima | Límite duro de Lambda: **900 s**. Ver §8.3 |
| Salida | Saneada: revisión y versión aplicada, **nunca** la `DATABASE_URL`, la contraseña ni volcados de datos. En modo `export` la salida es el **recuento de filas por tabla y la clave del objeto en S3**, no los datos |
| Permisos en S3 | **Solo** escritura sobre el **prefijo dedicado de exportación**, y solo en modo `export`. Ni lectura del resto del bucket ni acceso al prefijo de medios |
| *Backup* previo | **`Task/036` toma un *snapshot* manual antes de la primera migración.** Un *backup* automático no es un punto de control elegido |
| Reversión | Toda migración lleva `downgrade` probado en local, **y** el *snapshot* previo como red final. Si el `downgrade` no es seguro, se documenta el *roll-forward* |

### 8.3 Límite reconocido, sin disfrazarlo

**El techo de 900 s de Lambda es un límite real**, no una formalidad. Las migraciones del
MVP son tres revisiones de DDL sobre tablas pequeñas y caben con holgura, pero una
migración futura que reescriba una tabla grande podría no caber.

**No se resuelve ahora por adelantado.** Lo que se fija es la regla: si una migración no
cabe en 900 s, **se detiene y se pide una decisión explícita**; no se parte en trozos
silenciosamente ni se introduce un servicio excluido por la puerta de atrás. La duración
real de la primera migración la mide `Task/036` y es la que confirma o rompe este
supuesto.

### 8.4 Restore y acceso operativo

`Task/031` necesita acceso privado **antes** de que exista la aplicación, para su restore
sintético. Ese acceso es el mismo ejecutor con una operación de solo lectura y
verificación de integridad, invocado por la identidad humana operativa. **El primer
restore no depende de `Task/036`.**

### 8.5 R-43 — recuperación del administrador · **diseño**

`Task/029` diseña; `Task/036` implementa; `Task/040` verifica.

El bloqueo de cuenta tras cinco intentos fallidos es temporal (15 minutos) y no se
prolonga, pero la API responde igual que ante credenciales inválidas —decisión deliberada
para no revelar que el correo existe—. El propietario puede quedar fuera sin saber por
qué.

**Procedimiento diseñado**, por el canal privado y sin tocar la API pública:

1. Consultar el evento `authentication.account_locked` en la auditoría para **confirmar**
   que es un bloqueo y no una credencial equivocada.
2. Si hay que actuar antes de que expire: por el ejecutor privado, con `blog_migrate`,
   poner `locked_until` en el pasado para la cuenta afectada. **Una sentencia acotada a
   una fila, nunca un `DELETE` de tabla.**
3. Si además se perdió la contraseña: rotar el hash Argon2id por el mismo canal, con un
   valor generado fuera y **nunca** registrado en la salida.
4. Registrar la operación en el runbook con fecha, motivo y quién la ejecutó.

**No** se añade un *endpoint* de recuperación a la API pública: sería una superficie de
ataque nueva para un problema que ocurre cada varios años.

### 8.6 R-44 — purga y retención de tablas de estado · **diseño**

`Task/029` diseña; `Task/036` implementa; `Task/038` y `Task/040` verifican.

Dos tablas crecen de forma monótona y **ninguna** tiene purga productiva, porque el
backend no puede tener procesos residentes —debe funcionar igual en Lambda—:

| Tabla | Qué acumula | Retención propuesta |
| --- | --- | --- |
| `login_rate_limits` | Una fila por dirección IP observada. La mayor fuente de crecimiento con tráfico hostil | Borrar filas cuya ventana expiró hace más de **7 días** |
| `administrator_sessions` | Una fila por inicio de sesión con éxito; las caducadas y revocadas **no desaparecen** | Borrar caducadas o revocadas con más de **30 días** |

**Mecanismo: la misma Lambda ejecutora, en modo purga, con invocación programada.** No
introduce servicio nuevo, no requiere proceso residente y reutiliza identidad y red ya
definidas. Ninguna de las dos tablas alimenta un listado, así que la purga no afecta a
ninguna vista.

**Se ejecuta con `blog_migrate`, nunca con `blog_app`**: la aplicación no debe poder
borrar su propio historial de auditoría.

### 8.7 R-12 — custodia de los respaldos locales · **contrato**

El cierre por no aplicabilidad de **D-17** retiró la herramienta de secretos del *host*;
**no cifró** los respaldos locales de `local-backups/`, que siguen conteniendo los hashes
de autenticación de Portainer en claro sobre el equipo del autor.

**Contrato que `Task/029` entrega, para que `Task/031` lo revise y documente:**

1. `local-backups/` permanece **ignorado por Git** y marcado como sensible en el runbook
   y en `scripts/backup/README.md`. Verificado en esta tarea: sigue así.
2. Los respaldos locales **no** son el mecanismo de recuperación de producción. Producción
   usa *backups* administrados de RDS. Son cosas distintas y no se mezclan.
3. **No se monta un trabajo de respaldo desde el equipo hacia S3.** El *backup* de RDS y
   el bucket de medios o de *state* son responsabilidades diferentes.
4. El cifrado en reposo del directorio local sigue **fuera del alcance** y se decide con
   `Task/031`; retirar D-17 no lo resolvió y **el riesgo sigue abierto**.

---

## 9. Qué debe demostrar cada tarea posterior

Criterios **medibles**, sin ciclos y sin exigir recursos que la propia tarea no crea.

### 9.1 `Task/030` — antes que nada

1. *Bootstrap* separado del bucket de *state*, con versionado, cifrado, permisos y
   recuperación; backend S3 con `use_lockfile = true` y sin DynamoDB.
2. **Extinción de EX-028-C7** antes del primer `apply` de aplicación, incluido el de
   `Task/031`.
3. Bucket de medios y **D-08**, comprobando que la política **no rompe las URL
   prefirmadas** del navegador (§4).

**Gate que no se negocia: no existe RDS antes de que D-06 esté resuelta y aprobada.**

### 9.2 `Task/031` — provisión

| Criterio | Medible como |
| --- | --- |
| Red y RDS privados | `publicly_accessible = false` leído de la API; sin IGW ni NAT en el grafo; rutas sin `0.0.0.0/0` |
| SG mínimos | Reglas por referencia de grupo; cero reglas con `0.0.0.0/0`; inventario exportado |
| TLS | `rds.force_ssl = 1` leído del *parameter group* efectivo; CA registrada con `describe-certificates` y su `ValidTill` |
| KMS | `StorageEncrypted = true` y ARN de la clave registrado. **Ninguna prueba deshabilita ni programa el borrado de una clave** |
| Credenciales | Tres identidades SQL creadas con privilegios verificados por `\dp`. `blog_app` **sin DDL**, comprobado con un `CREATE TABLE` que **debe fallar** |
| *Backups* | Retención **7 días** aplicada; PITR activo; `LatestRestorableTime` avanzando |
| **Restore sintético** | Datos sintéticos, PITR a instancia nueva, integridad comprobada, **tiempo medido** y limpieza autorizada registrada |
| Acceso privado (D-24) | Ejecutor invocado por el plano de control, conecta, devuelve salida saneada |
| CloudWatch (D-11) | Retención explícita y **≤ 10 alarmas** para no salir del *free tier* |
| D-20 | Integración implementada **después** de verificar D-19; principal de solo lectura |
| Paridad | Filas nuevas de red y RDS marcadas **No evaluadas** si Floci no las soporta. **Nunca «paridad completa»** |

Alarmas mínimas: `CPUUtilization`, `CPUCreditBalance`, `FreeableMemory`,
`FreeStorageSpace`, `DatabaseConnections`, `ReadLatency`/`WriteLatency`, fallo de
*backup* y `MaximumUsedTransactionIDs`. Ocho señales, dentro de las 10 gratuitas. Los
umbrales los fija `Task/031`: **no se copian umbrales arbitrarios aquí**.

### 9.3 `Task/032` — Lambda real

1. Conexión SQL real con `sslmode=verify-full` y el bundle **dentro del ZIP**.
2. **Tráfico sin NAT demostrado**: S3 por gateway endpoint, PostgreSQL intra-VPC, logs
   entregados; inventario de flujos observados frente a la clase D vacía de §2.
3. **D-12 medida**: `DatabaseConnections` bajo tráfico real frente al presupuesto de 89;
   confirmar o corregir `pool_size = 1`, `max_overflow = 1` y `RC = 20`.
4. Latencia `Lambda ↔ RDS` **medida** (**R-34**), no estimada.
5. **Comportamiento de la ENI tras inactividad** (§2.2): observar si la primera
   invocación tras un periodo largo falla, y decidir su tratamiento.
6. Entrega del secreto según **D-23**: en despliegue. Si se demuestra que hace falta
   leerlo en *runtime*, el lector es trabajo de `Task/032` **con su propio plan
   test-first**, y arrastra el costo del interface endpoint.

### 9.4 `Task/036` y `Task/038` — migraciones

`Task/036`: *snapshot* manual previo; primera migración por el canal privado con
`blog_migrate`; **duración real medida** contra los 900 s (§8.3); `downgrade` probado;
recuperación del administrador (§8.5) y purga (§8.6) implementadas.

`Task/038`: canal repetible con ejecuciones serializadas; rol de despliegue backend
distinto; reversión probada; *branch protection* previa. **Un *runner* público no alcanza
RDS: invoca al ejecutor, no a la base de datos.**

### 9.5 `Task/040` — validación integral

1. Casos negativos: SG que debe rechazar, IAM que debe denegar, **TLS sin `sslrootcert`
   que debe fallar**, conexión sin SSL que debe ser rechazada por `rds.force_ssl`.
2. Carga y conexiones: agotamiento del pool y **recuperación** tras la saturación.
3. **Restore reciente con el esquema real** en destino aislado, con **RPO y RTO medidos**
   contra los objetivos de §10.
4. Alarmas disparadas en prueba segura y señales visibles en Grafana por **D-20**.
5. DR y *rollback*. **Sin destrucción automática de infraestructura real.**

### 9.6 `Task/041` — costo real

Comparar la factura real contra el escenario A de §7.2, con separación de costo bruto,
crédito consumido y desembolso; revisar caducidad de créditos y **D-19**; confirmar que
los tiers gratuitos siguen aplicando (**R-38**).

---

## 10. D-10 — Recuperación: backups, PITR, RPO y RTO · **Resuelta**

| Decisión | Valor | Motivo |
| --- | --- | --- |
| *Backups* automáticos | **Activados**. Retención **7 días** | El rango es 0–35 y el default 7. **Nunca 0**, que los desactiva. 7 días cubren el ciclo de publicación de un blog y caben en la asignación gratuita |
| PITR | **Activo**, consecuencia de la retención no nula | Granularidad ~5 minutos |
| *Snapshots* manuales | **Antes de cada migración** y antes de cualquier cambio estructural | Un punto de control **elegido**, no uno automático que quizá caiga en mal momento |
| `deletion_protection` | **`true`** | **R-35**. Un `terraform destroy` accidental no debe poder borrar la base productiva |
| `skip_final_snapshot` | **`false`** · `final_snapshot_identifier` fijado | Si algún día se borra, queda una copia |
| `copy_tags_to_snapshot` | `true` | Los *snapshots* heredan las etiquetas y son atribuibles en el costo |
| **RPO objetivo** | **≤ 15 minutos** | PITR da ~5 min; 15 es el compromiso con margen |
| **RTO objetivo** | **≤ 4 horas** | PITR restaura a **instancia nueva**: crear, esperar disponibilidad, verificar y cambiar `DATABASE_URL`. Coherente con Single-AZ |
| Protección frente a pérdida de región | **No se adopta ahora** | Copiar *snapshots* a otra región añade costo y transferencia. El contenido es reproducible desde Git y S3. Se reconsidera si el contenido deja de serlo |
| **Protección frente a pérdida de la cuenta** | **Vía de salida obligatoria**, §10.1 | **Añadida por la decisión H-4 del 2026-09-27.** Los *backups* administrados **no** sobreviven al cierre de la cuenta |
| Ambientes no productivos | `destroy`/`recreate` permitido, con caducidad y costo declarados | **Jamás** sobre producción, y **nunca** un `destroy` real automático en CI |

**Principio, y no es retórica: un *backup* existente no es un restore probado.** Ni un
estado `available`, ni un `LatestRestorableTime` que avanza, demuestran recuperación. Lo
demuestra restaurar y verificar: `Task/031` con datos sintéticos, `Task/036` con el
*backup* previo a la migración, `Task/040` con el esquema real y los tiempos medidos.

**Tres tramos, tres propietarios, cero solapamiento:** estrategia y objetivos en
`Task/029`; provisión y restore sintético en `Task/031`; restore reciente y RPO/RTO
medidos en `Task/040`.

### 10.1 Vía de salida: exportación fuera de la cuenta

**Añadida el 2026-09-27 como consecuencia directa de la decisión H-4.** El usuario conserva
el plan gratuito y difiere la continuidad a una decisión fechada
([§7.7](#77-la-decisión-fechada-que-sustituye-al-escenario-poscrédito)). Eso obliga a que la
**opción B —no continuar— sea realmente ejecutable**, y hoy no lo sería:

> Los *backups* automáticos de RDS, los *snapshots* manuales y el bucket de medios **viven
> dentro de la cuenta**. Si la cuenta se cierra, **desaparecen con ella**. La estrategia de
> **D-10** protege de fallos de AZ, de errores humanos y de corrupción — **no** de la pérdida
> de la cuenta.

#### Diseño

| Tramo | Mecanismo | Por qué así |
| --- | --- | --- |
| Esquema | **Las revisiones de Alembic ya versionadas en Git** | El esquema no necesita exportarse: es código. `alembic upgrade head` lo reconstruye en cualquier PostgreSQL 17.11 |
| Datos | **`COPY … TO STDOUT` por tabla, en CSV**, ejecutado por la Lambda ejecutora en modo `export` con `blog_migrate` | **No requiere el binario `pg_dump`** en el artefacto: `psycopg` 3 ya expone `copy()`. Un binario más sería dependencia nueva y superficie nueva |
| Destino intermedio | **Bucket S3 del proyecto, por el gateway endpoint** | Ya existe la ruta y **no cuesta tarifa de endpoint**. **Sin NAT** |
| Destino final | **Descarga a la estación del autor** con su propia identidad, desde fuera de la VPC | Es el único tramo que saca los datos de la cuenta, y lo hace un humano autorizado, no la Lambda |
| Custodia local | El mecanismo de respaldo local de `Task/004` | Ya está documentado como sensible y **fuera de Git** (**R-12**) |
| Medios | Sincronización del bucket a la estación con AWS CLI | Mismo principio: el humano los saca, no la aplicación |

**No introduce ningún servicio nuevo, ningún NAT, ningún binario y ningún permiso amplio.**
Reutiliza el ejecutor privado de **D-24**, el gateway endpoint de S3 y el respaldo local que
ya existe.

#### Dimensionamiento

El esquema del MVP son tablas de texto y metadatos; los medios están en S3. Con 20 GiB
aprovisionados y un blog personal, el volcado lógico está muy por debajo del
almacenamiento efímero de Lambda y de los **900 s** de techo. Si algún día no cupiera, aplica
la misma regla que las migraciones: **se detiene y se pide decisión explícita**, no se
trocea en silencio.

#### Propietarios

| Tarea | Qué le toca |
| --- | --- |
| `Task/029` | **Este diseño.** Nada más: no existe ejecutor, ni bucket, ni datos |
| `Task/031` | Incluir el **modo `export`** en el contrato del ejecutor privado y sus permisos mínimos de escritura en un prefijo dedicado del bucket |
| `Task/040` | **Demostrar que el artefacto exportado es restaurable fuera de AWS**, en un PostgreSQL 17.11 local. Un CSV en un bucket **no** es una salida probada |
| `Task/041` | El **gate fechado** y el recordatorio operativo |

**Criterio de salida, con el mismo estándar que el resto de esta tarea:** la vía de salida no
cuenta como existente hasta que `Task/040` restaure desde ella. Hasta entonces es diseño.

---

## 11. Decisiones del usuario — H-1 a H-4 resueltas

**Resueltas el 2026-09-27.** El agente investigó, calculó y recomendó; el usuario decidió.
Se registran aquí íntegras, con su efecto, para que no haya que reconstruirlas después.

### 11.1 H-1 · Región — **resuelta**

**Decisión: `us-east-2` (Ohio)**, aceptada como región objetivo de la arquitectura RDS y de
toda decisión que dependa de región. Coincide con la recomendación técnica.

Efecto: fijado en la [§3.1](#31-región). Precios de la [§7](#7-modelo-económico-y-gate-de-d-13)
recalculados sobre us-east-2 —ya lo estaban—; *trust store* con `us-east-2-bundle.pem`. El
`us-east-1` del laboratorio **no se toca**: es otro destino.

### 11.2 H-2 · Presupuesto — **resuelta con excepción acotada**

**Decisión:** el usuario acepta explícitamente que, durante esta etapa de prueba y
aprendizaje financiada con créditos, el **costo bruto de AWS supere el sublímite de USD
5/mes**, y ordena **no maquillar** la estimación de ≈ 15.48/mes para que quepa
artificialmente.

Efecto: se formaliza **EX-029-D13** en la
[§7.5](#75-ex-029-d13--excepción-acotada-al-sublímite-aws). **El techo global de USD 20/mes
no se modifica** y ningún otro presupuesto sube. **D-13 sigue Resuelta**: la excepción la
acota temporalmente, no la reabre. Las cuatro cifras siguen separadas en la
[§7.6](#76-las-cuatro-cifras-separadas).

### 11.3 H-3 · Créditos — **resuelta con datos verificados**

**Verificado por el usuario** en AWS Console, no por el agente: saldo **USD 120.00**, fecha
límite **2027-03-15**, **170 días** restantes, moneda **USD**, **sin restricciones de
servicio observadas**.

Efecto: modelo de consumo en la [§7.6](#76-las-cuatro-cifras-separadas). **El hallazgo
importante es que manda la fecha, no el saldo**: USD 120 durarían 7,75 meses pero solo
quedan 5,55, así que caducarían ≈ USD 34 sin usar. El consumo real lo verifica `Task/041`
contra Billing.

### 11.4 H-4 · Plan de la cuenta — **resuelta: no se cambia ahora**

**Decisión:** **no** pasar a Paid Plan ahora, **no** hacerlo prerrequisito de `Task/031`, y
conservar el plan gratuito mientras existan créditos y dentro del periodo mostrado por AWS.
La continuidad se decide **explícitamente antes** del agotamiento o del 2027-03-15, entre
**A — pagar y continuar** y **B — desmontar, migrar o preservar**.

Esto **sustituye** la propuesta del agente, que era hacer el Paid Plan prerrequisito de
`Task/031`. La decisión del usuario es coherente con el propósito declarado —una etapa
experimental— y se acata.

Efecto, y aquí está lo sustantivo: la opción B **no era ejecutable** con el diseño anterior,
porque los *backups* administrados, los *snapshots* y el bucket **mueren con la cuenta**. Por
eso esta ronda añade a **D-10** una **vía de salida** obligatoria
([§10.1](#101-vía-de-salida-exportación-fuera-de-la-cuenta)) y convierte el escenario
poscrédito en una **decisión fechada con gate**
([§7.7](#77-la-decisión-fechada-que-sustituye-al-escenario-poscrédito)). **R-47** queda
reformulado en consecuencia: ya no exige el cambio de plan, sino que la decisión se tome **a
tiempo y con la salida probada**.

**No se activó Paid Plan, no se tocó Billing y no se creó ningún recurso.**

### 11.5 Un dato por verificar, sin efecto bloqueante

**No es una decisión y no bloquea nada.** Es una comprobación de un minuto que haría más
preciso el gate fechado.

La documentación de AWS dice que el Free Plan *«ends after six months or when your credits
are fully used — whichever occurs first»*. `Task/027` observó el plan activo el **2026-09-17**
y el límite de créditos que el usuario reporta es el **2027-03-15**. Si la cuenta se abrió
alrededor del **2026-09-15**, esos seis meses caen **exactamente** en el 2027-03-15, y
entonces esa fecha no sería solo el vencimiento del crédito: sería también el **cierre de la
cuenta**.

**Es una hipótesis por coincidencia aritmética, no un hecho verificado**, y el agente no
conoce la fecha de apertura de la cuenta. Qué mirar, si el usuario quiere cerrarla:

> **AWS Console → Billing and Cost Management → Free tier** (o Billing Home), y comprobar si
> figura una **fecha de finalización del plan gratuito**.

Aporta solo esa fecha. **No** hace falta Account ID, *access keys*, *secret keys*, tokens,
contraseñas ni capturas con datos sensibles.

**Por qué no bloquea:** la política que el usuario eligió —decidir antes del agotamiento **o**
del 2027-03-15, lo que ocurra primero— es **correcta en su calendario en ambos casos**. Si la
hipótesis se confirma, lo único que cambia es la **severidad** de no decidir a tiempo: no
sería «empiezan los cargos», sería «se cierra la cuenta». Está recogido así en **R-47** y es
exactamente la razón por la que la vía de salida de la
[§10.1](#101-vía-de-salida-exportación-fuera-de-la-cuenta) pasa a ser obligatoria.

### 11.6 Estado del checkpoint

**No queda ninguna decisión humana pendiente dentro del alcance de `Task/029`.** Lo que queda
es la aprobación de la tarea, que es un acto distinto, y el dato opcional de la §11.5.

Decisiones humanas que esta tarea **traslada, con fecha y propietario**, a tareas posteriores:

| Decisión futura | Cuándo | Propietario |
| --- | --- | --- |
| Continuidad: pagar o desmontar | **Antes del agotamiento del crédito o del 2027-03-15** | Usuario, con `Task/041` como gate |
| Elevar el gasto por RDS Proxy, Secrets Manager, Multi-AZ o un interface endpoint | Solo si se cumple su criterio objetivo medido | Usuario, sobre evidencia de `Task/032`/`Task/040` |
| Introducir NAT Gateway o un servicio excluido | Solo con necesidad demostrada | Usuario |

---

## 12. Contratos de Terraform que `Task/031` implementará

**`Task/029` no añade ningún recurso.** Esto es el contrato: nombres, variables, salidas
y dependencias que `Task/031` materializará. Verificado contra el grafo real de
`terraform/`.

### 12.1 Módulos nuevos

| Módulo | Recursos que creará `Task/031` | Entradas | Salidas |
| --- | --- | --- | --- |
| `modulos/red` | `aws_vpc`, 2 `aws_subnet` privadas, 2 `aws_route_table` y sus asociaciones, `aws_vpc_endpoint` de S3 tipo `Gateway`, 3 `aws_security_group` con sus reglas | `cidr`, `azs`, `cidrs_de_subred`, `nombre` | `id_de_vpc`, `ids_de_subredes`, `id_sg_lambda`, `id_sg_rds`, `id_sg_admin`, `id_endpoint_s3` |
| `modulos/base_de_datos` | `aws_db_subnet_group`, `aws_db_parameter_group`, `aws_db_instance` | `ids_de_subredes`, `id_sg_rds`, `clase`, `version_del_motor`, `gib`, `gib_maximos`, `dias_de_retencion`, `ventana_de_backup`, `ventana_de_mantenimiento`, `arn_de_clave_kms` (null = clave gestionada por AWS) | `endpoint`, `puerto`, `id_del_recurso`, `arn` |
| `modulos/ejecutor_privado` | `aws_lambda_function` del ejecutor, su `aws_iam_role` y su `aws_cloudwatch_log_group` | `ids_de_subredes`, `id_sg_admin`, `lambda_zip_path`, `arns_de_parametros` | `nombre`, `arn` |

### 12.2 Cambios en la raíz que `Task/031` deberá hacer

| Archivo | Cambio | Nota de paridad |
| --- | --- | --- |
| `terraform/main.tf` | Añadir los tres módulos. Orden: `red` → `base_de_datos` → `ejecutor_privado`; `computo` pasa a depender de `red` para su `vpc_config`. Terraform deduce el orden de las referencias: **sin `depends_on` de módulo** | Un solo grafo. **Sin `count` por entorno y sin módulos alternativos** (regla de portabilidad, **R-26**) |
| `terraform/providers.tf` | El bloque `endpoints` lista hoy 8 servicios. Faltan **`ec2`** —VPC, subnets, SG y *endpoints* se crean por la API de EC2— y **`rds`**. Añadir también `kms` solo si se adopta CMK | **Diferencia legítima**, fila 1 de la matriz de paridad: `null` contra AWS, *endpoint* local en el laboratorio |
| `terraform/variables.tf` | Variables nuevas con validación, en el estilo de la validación de `region` ya presente | — |
| `terraform/entornos/produccion/produccion.tfvars.example` | Reflejar las variables nuevas **sin valores reales** y sin secretos | Sigue siendo plantilla no operativa |
| Matriz de paridad de `aws-local-parity.md` | Filas nuevas de red y RDS. Si Floci no soporta una capacidad, **AWS-only con evidencia**, no simulada | **Nunca «paridad completa»** |

**Lo que `Task/029` explícitamente no hace, y se comprueba en el `git diff`:** ningún
`aws_db_instance`, `aws_db_subnet_group`, `aws_vpc`, `aws_subnet`, `aws_security_group`,
`aws_kms_key`, `aws_vpc_endpoint` ni `aws_db_proxy`. Ningún `apply`, `import`, `destroy`,
`-target` ni operación sobre el *state*.

### 12.3 Identidades separadas

El *provider* de GitHub puede compartirse; los permisos, no.

| Identidad | Owner | Estado |
| --- | --- | --- |
| Validación OIDC, sin políticas | `Task/028` | **Existe.** Intacta; no se promueve ni se le añaden permisos |
| Humana operativa, mínima y autorizada | `Task/031` | Pendiente. **No depende del rol de CI de `Task/039`** |
| Ejecución de la Lambda de aplicación | `Task/032` | Pendiente |
| Ejecución del ejecutor privado | `Task/031` | Pendiente. Distinta de la anterior |
| Despliegue backend | `Task/038` | Pendiente |
| Terraform en CI | `Task/039` | Pendiente |
| Integración Grafana, solo lectura | `Task/031` | Pendiente |

---

## 13. Alembic, extensiones y privilegios frente a RDS

Revisión estática de `personal-blog-backend/alembic/`.

| Comprobación | Resultado | Consecuencia |
| --- | --- | --- |
| `CREATE EXTENSION` en migraciones | **Ninguna.** Búsqueda en todo el repositorio: solo coincidencias dentro de `.venv`, no en código del proyecto | **No se necesita `rds_superuser` para instalar extensiones.** Compatible con RDS sin excepciones |
| Revisiones presentes | `20260801_0001_baseline_del_esquema`, `20260826_0002_modelo_de_datos_del_mvp`, `20260831_0003_sesiones_administrativas_y_limite_de_acceso` | DDL sobre tablas pequeñas: caben con holgura en los 900 s (§8.3) |
| Versión del motor | Local **17.11**; candidata en RDS **17.11** | Paridad exacta: el mismo SQL en los dos destinos |
| `sqlalchemy.url` en `alembic.ini` | **Vacío a propósito**; `alembic/env.py` usa `get_settings()` y `create_database_engine()` | **Las migraciones respetan el contrato `DATABASE_URL`.** El ejecutor privado solo necesita su propia `BLOG_DATABASE_URL` con `blog_migrate` |
| Privilegios necesarios | DDL en el esquema de la aplicación | `blog_migrate` los tiene; `blog_app` **no** |

**Consecuencia de diseño:** `env.py` reutiliza `create_database_engine()`, y con él el
pool de la aplicación. En el ejecutor privado eso significa que el pool de migraciones
también sale de los mismos ajustes, y por eso el presupuesto de §6.2 reserva **5**
conexiones para migraciones. `Task/036` confirma el consumo real.

---

## 14. Resumen ejecutivo — decision pack

La columna «¿Decisión humana?» refleja el estado **tras la ronda del 2026-09-27**: las cuatro
decisiones que la requerían están **resueltas**.

| Decisión | Opción recomendada | Alternativas | Impacto | Costo/mes | Riesgo | ¿Decisión humana? |
| --- | --- | --- | --- | --- | --- | --- |
| Región | **us-east-2** | us-east-1 (igual precio), us-west-2, sa-east-1 (2,1×) | Fija el destino de todo lo demás | 0 delta | Cambiarla después obliga a recrear | **Resuelta — H-1** |
| Versión PostgreSQL | **17.11** | 18.6, 16.15 | Paridad exacta con local y CI | 0 | Fin de soporte de minor: sep 2027 | No |
| Clase | **db.t4g.micro** (2 vCPU, 1 GiB) | t4g.small (+11.68), t3.micro (+1.46) | `max_connections` 112; excluye IAM DB auth | 11.68 | 1 GiB es justo. **R-32**. Reversible *in-place* | No |
| Disponibilidad | **Single-AZ** | Multi-AZ (+13.98) | RTO de horas, no minutos | 0 delta | **R-29 aceptado**: SPOF | No |
| Almacenamiento | **gp3 20 GiB**, autoscaling a 50 | gp2 (igual precio, peor base), io2 | 3.000 IOPS y 125 MiB/s incluidos | 2.30 | **R-32**; alarma de espacio | No |
| IOPS / throughput | **No aprovisionables** bajo 400 GiB | — | Decisión cerrada por el servicio | 0 | Ninguno | No |
| KMS | **Clave gestionada por AWS** | CMK (+1.00) | Cifra datos, *backups* y *snapshots* | 0 | Perder una CMK es irreversible: se evita | No |
| TLS | **verify-full** + `rds.force_ssl=1` | verify-ca (insuficiente) | Bundle de CA dentro del ZIP | 0 | **R-30**; negativo obligatorio en `Task/040` | No |
| Secretos | **SSM `SecureString`**, en despliegue | Secrets Manager (+0.40/secreto) | Rotar exige redesplegar | 0 | **R-40** | No |
| IAM DB auth | **No** | Sí | Exige 300–1000 MiB extra en 1 GiB | 0 | Incompatible con la clase | No |
| *Backups* / PITR | **7 días**, PITR activo | 0 (prohibido), 35 | Dentro de la asignación gratuita | 0 | **R-31**: restore probado, no supuesto | No |
| RPO / RTO | **≤ 15 min / ≤ 4 h** | Multi-AZ mejora el RTO | Medidos en `Task/040` | 0 | Coherente con Single-AZ | No |
| Pool / concurrencia | **`pool_size=1`, `overflow=1`, RC=20** | Default local 5+5: solo 8 entornos | 40 de 89 conexiones | 0 | **R-33**; medir en `Task/032` | No |
| RDS Proxy | **No**, con criterio objetivo | Sí (+22.70) | Sin problema que resolver hoy | 0 | Reevaluar si se cumple el criterio de §6.3 | No (sí si se adopta) |
| VPC / subnets | **1 VPC, 2 subnets privadas, 2 AZ** | Subnet pública (sin utilidad) | Requisito del DB subnet group | 0 | **R-30** | No |
| *Endpoints* | **Solo gateway S3** | Interface SSM (+14.60) | Sin lector de SSM en *runtime* | 0 | Revisar si `Task/032` lo cambia | No |
| NAT Gateway | **No** | Sí | Clase D **vacía** en el inventario | 0 | Requiere decisión explícita si cambia | No |
| Canal admin / migraciones | **Lambda ejecutora dedicada** | EC2/SSM/VPN (excluidos o caros) | Serializada, RC=1 | ≈ 0 | Techo de 900 s reconocido | No |
| CloudWatch | **8 alarmas**, retención explícita | Database Insights avanzado | Dentro del *free tier* | 0 | Umbrales en `Task/031` | No |
| Grafana / D-20 | **Tier gratuito**, verificar antes de integrar | Plan de pago | Costo de `GetMetricData` modelado | 0 | **R-38**; **D-19** abierta | No |
| Vía de salida | **Exportación lógica por el canal privado a S3 y descarga** | *Snapshots*, que **mueren con la cuenta** | Hace ejecutable la opción B de la §7.7 | ≈ 0 | Diseño hasta que `Task/040` restaure desde ella | No |
| **Costo bruto** | **13.98** RDS · **≈ 15.48** AWS | sa-east-1: 29.20 | La cifra que el proyecto vigila | 15.48 | **R-02** | — |
| **Presupuesto** | **EX-029-D13**: sublímite AWS suspendido; **techo global intacto en 20.00** | Subir el techo global; revisar ADR-010 | Total del proyecto ≈ 16.48, margen 3.52 | — | **R-02** | **Resuelta — H-2** |
| **Créditos** | **USD 120, límite 2027-03-15**, verificados por el usuario | — | **Manda la fecha, no el saldo**: caducarían ≈ 34 sin usar | consumo teórico ≈ 86 | **R-47** | **Resuelta — H-3** |
| **Desembolso** | **0.00** de AWS durante el plan gratuito; ≈ 1.00 no AWS | — | El mecanismo que lo garantiza es el que cierra la cuenta | 0.00 | **R-47** | — |
| **Poscrédito** | **Decisión fechada A/B**, no un costo | Asumir continuidad pagada: **descartado** | Si nadie decide, se pierde la cuenta | — | **R-47** | **Resuelta — H-4**; vuelve a preguntarse antes del 2027-03-15 |
| **Plan de la cuenta** | **Se conserva el plan gratuito** | Paid Plan ahora: **descartado por el usuario** | Paid Plan **no** es prerrequisito de `Task/031` | — | **R-47** | **Resuelta — H-4** |

---

## 15. Límites de esta tarea

- **Cero recursos AWS creados.** Cero `apply`, `import`, `destroy`, `-target` y cero
  operaciones sobre el *state*.
- **Cero secretos** generados, leídos o almacenados.
- **Cero llamadas mutantes a AWS.** El agente **no consultó facturación**: los datos de
  créditos de la [§7.6](#76-las-cuatro-cifras-separadas) los verificó el usuario y los
  reportó.
- **No se activó Paid Plan, no se modificó Billing y no se cambió el plan de la cuenta.**
- **El techo global de D-13 no se tocó.** **EX-029-D13** suspende **solo** el sublímite AWS,
  está fechada y **no autoriza ningún recurso**.
- **`personal-blog-backend` y `personal-blog-frontend` no se modifican.** Se inspeccionaron
  en **solo lectura**; el inventario de §2, la configuración de §6.1 y la revisión de §13
  salen de esa lectura. No hizo falta rama en ellos.
- **ADR-010 no se reescribe.** No apareció contradicción que exija gobierno nuevo: este
  documento la instancia. El hallazgo del plan de la cuenta (§7.6) es un **riesgo
  operativo nuevo**, no un conflicto con la decisión arquitectónica.
- **Aprobado el 2026-09-27** mediante
  `approved: Task/029-Preparar-PostgreSQL-Produccion-en-RDS`. **D-22**, **D-23**, **D-24** y
  **D-10** quedan **Resueltas**; **EX-029-D13**, **Aceptada y Vigente**; **D-12 sigue
  abierta** con su presupuesto preliminar aprobado y su cierre en `Task/032`, con medición.
  **La aprobación no crea ningún recurso.**
