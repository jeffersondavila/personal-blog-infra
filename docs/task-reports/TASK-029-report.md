# TASK-029 — Reporte: preparar PostgreSQL de producción en Amazon RDS

| Campo | Valor |
| --- | --- |
| Tarea | `Task/029-Preparar-PostgreSQL-Produccion-en-RDS` |
| Etapa | ETAPA 09 — Cuentas y Seguridad Cloud, tercera de tres. **Cuenta entre las 41** |
| Estado | **Lista para validación** — 2026-09-27 |
| Repositorios modificados | **Solo `personal-blog-infra`** |
| Rama | `Task/029-Preparar-PostgreSQL-Produccion-en-RDS`, creada desde `main` |
| SHA base | `d96d5d569a673d2a0ddfae3cc9b09cfff078b837` |
| Recursos AWS creados | **Cero** |
| Secretos generados o leídos | **Cero** |
| Avance | **28/41 ≈ 68 %** · ETAPA 09 **2/3 ≈ 67 %** — **no se mueve hasta la aprobación** |

> **Resultado en una frase.** Las cuatro decisiones del alcance —**D-22**, **D-23**,
> **D-24** y **D-10**— quedan resueltas como **Propuesta** con precios y capacidades
> verificados contra fuentes primarias, y el candidato **sin NAT** se confirma sobre el
> código real. Los dos puntos que el agente no podía cerrar —el **gate de D-13**, que ninguna
> configuración de RDS satisface, y el **plan de la cuenta, que la cierra sola**— **los
> resolvió el usuario el mismo día**, y de la segunda decisión salió una obligación de diseño
> nueva: **una vía de salida fuera de la cuenta**, sin la cual «no continuar» no sería
> ejecutable.

**Esta tarea tuvo dos rondas, en la misma rama y el mismo día.** La primera entregó el paquete
de decisiones y aisló cuatro puntos en un checkpoint humano; la segunda incorporó las
decisiones del usuario (**H-1** a **H-4**), formalizó **EX-029-D13**, recalculó el modelo
económico con los créditos verificados y añadió la vía de salida. **No queda ninguna decisión
humana pendiente en el alcance de `Task/029`**; el detalle está en la [§11](#11-decisiones-del-usuario-resueltas).

---

## 1. Estado Git inicial verificado

Los tres repositorios se comprobaron **antes** de crear nada.

| Comprobación | Resultado |
| --- | --- |
| `git fetch --prune origin` (infra) | Sin cambios |
| `git status --porcelain` en infra, backend y frontend | **Vacío** en los tres |
| `git rev-parse main` (infra) | `d96d5d569a673d2a0ddfae3cc9b09cfff078b837` |
| `git rev-parse origin/main` (infra) | `d96d5d569a673d2a0ddfae3cc9b09cfff078b837` — **coinciden** |
| `git rev-parse dev` (infra) | `99e895d44a16e49e38460ce253abe79266c9fb2e` |
| `git diff --stat main dev` | **Vacío**: la normalización de `Task/028.2` está intacta |
| `git branch -r` | Solo `origin/main`, `origin/dev` y `origin/HEAD`. La rama remota de `Task/028.2` **ya estaba eliminada** |
| `Task/028.2` integrada | **Sí**: `d96d5d5` es el *merge* del PR #52, con `b353914` y `6c61e8e` en la ascendencia |
| CI Infra | `main` **SUCCESS** (run 36344866735) · `dev` **SUCCESS** (run 36345367052) |
| Otra Task activa | **Ninguna**. `git worktree list` devuelve solo el árbol principal; backend en `main` (`4a40364`) y frontend en `main` (`7dce98a`) |

Todo coincide con el estado que el prompt declaraba. **Nada quedó sin verificar.**

## 2. Rama creada

```
git switch -c Task/029-Preparar-PostgreSQL-Produccion-en-RDS
git rev-parse HEAD   -> d96d5d569a673d2a0ddfae3cc9b09cfff078b837
git rev-parse main   -> d96d5d569a673d2a0ddfae3cc9b09cfff078b837
```

**`HEAD == main`.** Creada desde `main`, **nunca** desde `dev`, conforme al invariante
crítico de [CLAUDE.md](../claude/PROJECT_INSTRUCTIONS.md) §4 y
[WORKFLOW](../project-management/WORKFLOW.md) §2.1.

**Rama creada solo en infra.** La inspección del backend no encontró ninguna dependencia
que obligue a modificarlo: el contrato de TLS viaja en `BLOG_DATABASE_URL` y no exige
código nuevo (§5). `personal-blog-backend` y `personal-blog-frontend` quedan en `main`,
limpios y **sin rama**, conforme a la regla de no crear ramas en repositorios que no se
modificarán.

## 3. Investigación AWS — cómo se obtuvieron los números

**Las páginas comerciales de precios no sirvieron:** se renderizan por JavaScript y al
recuperarlas no contienen ninguna cifra. Se recurrió a la fuente que esas páginas consumen
y a la **AWS Price List API**, que es autoritativa y lleva fecha de publicación propia.

| Fuente | Publicación de la fuente | Qué aportó |
| --- | --- | --- |
| `pricing.us-east-1.amazonaws.com/.../AmazonRDS/current/{us-east-1,us-east-2,sa-east-1}/index.csv` | **2026-09-24T21:10:11Z** | Instancia, gp3/gp2/io2, *backup*, IOPS y *throughput* gp3, CPU Credits, RDS Proxy |
| `.../awskms/current/...` | 2026-09-11 | CMK 1.00/mes; 0.03/10.000 peticiones; 20.000 gratis |
| `.../AWSSecretsManager/current/...` | 2026-09-11 | 0.40/secreto/mes; 0.05/10.000 peticiones |
| `.../AmazonVPC/current/...` | 2026-09-17 | Interface endpoint 0.010 USD/h (0.021 en sa-east-1); gateway S3 **sin tarifa** |
| `.../AmazonCloudWatch/current/...` | 2026-09-22 | Logs 0.50/GB, almacenamiento 0.03/GB-mes, alarmas 0.10, *free tier* |
| Documentación oficial de RDS, Lambda, Systems Manager y Billing | consultada **2026-09-27** | Versiones, `NO_CREATE`, línea base gp3, CA, `rds.force_ssl`, límites de IAM DB auth y de Proxy, detención de 7 días, Lambda en VPC, planes del Free Tier |

Tabla completa con URL y fechas:
[paquete de decisiones §1](../architecture/production-postgresql-rds-decisions.md#1-fuentes-primarias-y-trazabilidad-de-los-números).
**Ningún precio se heredó del repositorio.**

## 4. Decisiones entregadas

Todas **Propuesta — pendiente de aprobación**. Argumentación completa en el
[paquete de decisiones](../architecture/production-postgresql-rds-decisions.md).

### 4.1 D-22 — red, topología y capacidad

| Punto | Decisión | Dato que la sostiene |
| --- | --- | --- |
| Región | **us-east-2** — *confirmación del usuario* | 13.98/mes, empatada con us-east-1; `sa-east-1` cuesta **2,1×** (29.20) sin mejorar la latencia. **No existía región canónica**: `us-east-1` es laboratorio y plantilla, y `us-east-2` solo aparecía como CloudShell temporal de `Task/028` |
| Versión | **PostgreSQL 17.11** | **Es la que el proyecto ya usa**: `.env` y el CI del backend fijan `postgres:17.11-alpine@sha256:18cfe3ef…`. Publicada en RDS el 2026-08-25; major 17 soportado hasta 2030-02-28 |
| Clase | **db.t4g.micro** (2 vCPU, 1 GiB) | 11.68/mes, la más pequeña de generación actual. Cambio *in-place*: **reversible** |
| Almacenamiento | **gp3 20 GiB**, *autoscaling* a 50 | gp2 cuesta igual con peor línea base; magnetic **deprecado** |
| IOPS / *throughput* | **No se configuran** | Bajo 400 GiB, gp3 incluye **3.000 IOPS y 125 MiB/s** y el rango aprovisionable es *«Not applicable»*. **Cerrado por el servicio, no por criterio** |
| Disponibilidad | **Single-AZ** | Multi-AZ cuesta **+13.98/mes** por un RTO de minutos en un blog que tolera horas. **R-29 aceptado por escrito** |
| Red | VPC `10.40.0.0/16`, 2 subnets privadas en 2 AZ, sin IGW, **sin NAT** | El DB subnet group **exige 2 AZ incluso en Single-AZ**; una subnet pública **no** da IP pública a la Lambda |
| Security groups | 3, **por referencia de grupo** | Si las subnets cambian la regla sigue correcta y ningún CIDR entra por coincidencia |
| Operación | *backup* 07:00–07:30 UTC; mantenimiento dom 08:00–09:00 UTC; minor **automático**, major **manual**; *parameter group* **propio** | Madrugada local (UTC−6). Desactivar el minor automático crearía el *drift* de **R-42** |

### 4.2 D-23 — TLS, KMS, secretos y autenticación SQL

- **`sslmode=verify-full`** —`verify-ca` no valida el *hostname*— con `rds.force_ssl = 1`
  explícito y CA **`rds-ca-rsa2048-g1`**, el default, con rotación automática del
  certificado de servidor. En el *trust store*, **solo el root**.
- **KMS gestionada por AWS**, 0.00, frente a **+1.00/mes** de una CMK que además añadiría
  una forma irreversible de perder los datos (**R-35**).
- **Tres identidades SQL** separadas. `blog_app` **sin DDL**: es la garantía estructural de
  que una migración no puede ocurrir al arrancar la Lambda.
- **SSM `SecureString`, sin migrar.** Parámetros estándar **sin cargo**; Secrets Manager
  costaría 0.40/secreto/mes y su única ventaja real —rotación gestionada— no se justifica
  con tres credenciales estables.
- **Entrega en despliegue, no en *runtime*.** El backend **no tiene lector de SSM** y leerlo
  en *runtime* exigiría un **interface endpoint a +14.60/mes** más latencia de arranque.
  Contrapartida aceptada y escrita: **rotar exige redesplegar**.
- **IAM DB auth descartada por un dato, no por opinión:** exige **300–1000 MiB extra** de
  memoria y `db.t4g.micro` tiene **1 GiB en total** — entre el 30 % y el 100 %.

### 4.3 D-24 — canal privado

**Lambda ejecutora dedicada** en subnets privadas, invocada por el plano de control,
concurrencia reservada **= 1**. Alternativas descartadas con motivo: un *runner* público
**no alcanza** la VPC; EC2 y SSM Session Manager **exigen un servicio excluido**; Client VPN
cuesta **≈ 73/mes**; abrir RDS a Internet está **prohibido**.

**Límite reconocido y no disfrazado:** el techo de Lambda es **900 s**. Las tres revisiones
del MVP caben; si una futura no cabe, **se detiene y se pide decisión explícita**.
`Task/036` mide la duración real.

Runbook preparado y **no ejecutado**:
[rds-private-administration.md](../runbooks/rds-private-administration.md). Incluye el
diseño de **R-43** (recuperación del administrador) y **R-44** (purga con retenciones de 7
y 30 días, ejecutada con `blog_migrate` y **nunca** con `blog_app`).

### 4.4 D-10 — recuperación

Retención **7 días** —nunca 0, que desactiva los *backups*—, PITR activo, *snapshot*
manual **antes de cada migración**, `deletion_protection = true`, *snapshot* final
obligatorio. **RPO ≤ 15 min** y **RTO ≤ 4 h**, coherentes con Single-AZ y con que PITR
**restaura a una instancia nueva**. *Backup* dentro de la asignación gratuita —igual al
almacenamiento aprovisionado—, luego **0.00** mientras no se exceda. Copia entre regiones
**no** se adopta ahora.

### 4.5 D-12 — presupuesto preliminar de conexiones

`max_connections` = `LEAST(DBInstanceClassMemory/9531392, 5000)` = **112** con 1 GiB.
Restando `superuser_reserved_connections` (3) y reservas de migraciones (5), administración
(3), monitorización (2) y *churn* (10): **presupuesto de aplicación = 89**.

| `pool_size` | `max_overflow` | Efectivo | Entornos que caben |
| --- | --- | --- | --- |
| 5 | 5 *(default local)* | 10 | **8** |
| **1** | **1** | **2** | **44** |

**El default local solo admite 8 entornos concurrentes**: esa es la razón concreta de no
trasladarlo. Candidato: **`pool_size=1`, `max_overflow=1`, *Reserved Concurrency* = 20** →
40 conexiones, margen de 2,2×. Se sostiene porque el backend es **síncrono y una invocación
atiende una petición**, documentado en `session.py`.

**La configuración del backend no se modificó**: el cambio pertenece a `Task/032`.

**RDS Proxy descartado.** **+21.90/mes** (0.015 × 2 vCPU × 730) más Secrets Manager, que
**exige**: **+22.70/mes**, ~1,6× la instancia. Además PostgreSQL **no admite filtros de
*session pinning***. Criterio objetivo de reincorporación —cuatro condiciones medibles— en
[§6.3](../architecture/production-postgresql-rds-decisions.md#63-rds-proxy--decisión-negativa-con-criterio-objetivo).

## 5. Inventario de tráfico A–E y hallazgos del código

Inspección estática de `personal-blog-backend` sobre `d96d5d5`, en **solo lectura**, sin
leer `.env` ni credenciales.

| Clase | Resultado |
| --- | --- |
| **A** intra-VPC | PostgreSQL 5432 desde `session.py`; `/ready` con conexión propia |
| **B** gateway | S3: `put_object`, `get_object`, `head_object`, `delete_object`, `list_objects_v2`. `generate_presigned_url` **no hace red** |
| **B** no aplica | **SSM no se lee en *runtime***: cero coincidencias reales; las aparentes son la subcadena `ssm` de `classmethod` |
| **C** gestionado | Logs de Lambda, credenciales del rol, invocación de API Gateway, métricas y *backups* de RDS |
| **D** Internet | **VACÍA.** Ninguna API externa requerida. Dependencias de ejecución: `boto3` es el único SDK AWS; **no hay `requests`, `httpx`, `aiohttp` ni `smtplib`** |
| **E** no usado | Cloudflare, Grafana, Floci, *registry*, SMTP |

**El candidato sin NAT es viable con el código vigente**, y lo es porque la clase D está
vacía — no por preferencia.

### 5.1 Tres hallazgos con consecuencia concreta

1. **TLS no está en el código.** No hay `sslmode` ni `sslrootcert` en
   `app/shared/database/` ni en `app/shared/configuration/`: `sqlalchemy_url` solo antepone
   el driver y `connect_args` solo fija `connect_timeout`. Por tanto **el TLS viaja en
   `BLOG_DATABASE_URL`** y **el backend no necesita cambios** —lo que confirma que esta
   tarea no debía tocarlo—, pero **el ZIP de la Lambda debe incluir el bundle de la CA**:
   requisito de empaquetado para `Task/032`, y caso negativo obligatorio en `Task/040`.
2. **Lambda reclama la Hyperplane ENI tras 14 días de inactividad** y la siguiente
   invocación **falla**, volviendo la función a `Pending`. En un blog de tráfico bajo esto
   **no es hipotético** y no se mitiga con NAT ni con más memoria. No estaba previsto en el
   canónico. Owner: `Task/032`.
3. **Alembic es compatible con RDS sin excepciones.** **Ninguna migración usa `CREATE
   EXTENSION`** —la búsqueda solo devuelve coincidencias dentro de `.venv`—, así que **no
   se necesita `rds_superuser`**. `alembic.ini` deja `sqlalchemy.url` vacío a propósito y
   `env.py` usa `get_settings()`: **las migraciones respetan el contrato `DATABASE_URL`**.

## 6. Modelo económico y gate de D-13 — **NO CABE**

Escenario A, el mínimo absoluto: `db.t4g.micro` Single-AZ, gp3 20 GiB, clave gestionada por
AWS, SSM estándar, solo gateway endpoint S3, sin Proxy, sin endpoints de interfaz, sin NAT.

| Partida | Cálculo | us-east-2 | sa-east-1 |
| --- | --- | --- | --- |
| Instancia | 0.016 × 730 | **11.68** | 24.82 |
| Almacenamiento | 20 × 0.115 | **2.30** | 4.38 |
| IOPS, *backup*, KMS, secretos, *endpoints*, NAT, CloudWatch | — | **0.00** | 0.00 |
| **RDS bruto/mes** | | **13.98** | **29.20** |

| Variante (us-east-2) | Total | Delta |
| --- | --- | --- |
| Multi-AZ | 27.96 | +13.98 |
| `t4g.small` | 25.66 | +11.68 |
| CMK propia | 14.98 | +1.00 |
| Secrets Manager (2) | 14.78 | +0.80 |
| **RDS Proxy (arrastra Secrets Manager)** | **36.68** | **+22.70** |
| 1 interface endpoint / 2 AZ | 28.58 | +14.60 |
| *Backup* de 40 GB | 15.88 | +1.90 |

Restore temporal de 48 h: **≈ 0.92 USD** por prueba, con limpieza autorizada obligatoria.

### 6.1 Gate de D-13 y la excepción EX-029-D13

| Concepto | USD/mes |
| --- | --- |
| RDS bruto | 13.98 |
| Resto de AWS estimado | ≈ 1.50 |
| **Subtotal AWS** vs **sublímite original 5.00** | **≈ 15.48 — 3,1×, NO CABE** |
| No AWS estimado | ≈ 1.00 |
| **Total proyecto** vs **techo global 20.00** | **≈ 16.48 — CABE, margen ≈ 3.52** |

**No existe configuración de RDS que quepa en el sublímite AWS de USD 5/mes.** No se manipuló
ningún cálculo para que cupiera, y el agente **no cambió D-13**: registró la incompatibilidad y
la elevó, que es el gate que ADR-010 y el canónico previeron.

**El usuario lo resolvió el 2026-09-27** aceptando el exceso para la etapa experimental
financiada con créditos, con la instrucción expresa de **no maquillar** la estimación. Se
formaliza como **EX-029-D13**:

| Campo | Valor |
| --- | --- |
| Suspende | **Solo** el sublímite de **USD 5/mes de AWS** de D-13 |
| No cambia | El **techo global de USD 20/mes**, íntegro y con ≈ 3.52 de margen. **D-13 sigue Resuelta**; ningún otro presupuesto sube |
| Referencia aprobada | **≈ 15.48/mes** de AWS; una desviación material exige revisión |
| Vigencia | Hasta el agotamiento de los créditos o el **2027-03-15**, lo que ocurra primero |
| No autoriza | **Ningún recurso**, ni cambiar de plan, ni tocar Billing |
| Al expirar | **No se renueva por inercia** |

**Parar la instancia no es estrategia:** máximo **7 días consecutivos**, después RDS la
arranca sola, y mientras está detenida se siguen cobrando almacenamiento y *backups*.

### 6.2 Las cuatro cifras, con los créditos verificados

Datos **verificados por el usuario** en AWS Console el 2026-09-27. **El agente no consultó
facturación.**

| Dato observado | Valor |
| --- | --- |
| Saldo disponible | **USD 120.00** |
| Fecha límite | **2027-03-15** |
| Días restantes | **170** — coherente con los 169 días exclusivos contando ambos extremos |
| Moneda · restricciones | USD · ninguna observada |

**A · Costo bruto:** ≈ **15.48/mes** de AWS más ≈ 1.00 no AWS. Es la cifra que el proyecto
vigila y **no baja porque haya créditos**.

**B · Crédito consumido**, según cuándo exista RDS —que no es hoy: antes van `Task/030` y
`Task/031`—:

| RDS creado el | Meses hasta el límite | Consumido | Caducaría sin usar |
| --- | --- | --- | --- |
| 2026-10-01 | 5.42 | 83.92 | **36.08** |
| 2026-11-01 | 4.40 | 68.15 | **51.85** |
| 2026-12-01 | 3.42 | 52.89 | **67.11** |
| 2027-01-01 | 2.40 | 37.13 | **82.87** |

> **Hallazgo del cálculo: manda la fecha, no el saldo.** USD 120 a 15.48/mes durarían **7,75
> meses** —hasta el 2027-05-21—, pero solo quedan **5,55** hasta el límite. Incluso con RDS
> existiendo **hoy**, el consumo máximo posible sería **USD 85.95** y **caducarían ≈ USD 34
> sin usar**.
>
> Consecuencia: **no tiene sentido optimizar para estirar el saldo**; no es el recurso escaso.
> Y **tampoco es razón para acelerar `Task/030` ni para saltarse el gate de D-06**: es razón
> para no justificar gasto extra con el argumento de que «hay saldo de sobra».

Cifras teóricas y reproducibles. El **consumo real** lo verifica `Task/041` contra Billing.

**C · Desembolso:** **USD 0.00** de AWS mientras rija el plan gratuito —*«No charges incur
during usage»*—, y el mecanismo que lo garantiza es precisamente el que **cierra la cuenta**.
Lo no AWS —dominio, con Cloudflare y Grafana en tier gratuito— queda fuera de los créditos:
≈ 1.00/mes real.

**D · Poscrédito:** **no es un costo, es una decisión fechada.** Ver §6.3.

### 6.3 El plan de la cuenta y la decisión fechada

La documentación de AWS establece que el **Free Plan** —el que `Task/027` observó activo—
otorga hasta **USD 200** y *«ends after six months or when your credits are fully used —
whichever occurs first»*, y que *«after your free account plan expires, your account closes
automatically, and you lose access to your resources and data»*, con 90 días de retención.

El agente propuso hacer el **Paid Plan prerrequisito de `Task/031`**. **El usuario decidió lo
contrario** y se acata: se conserva el plan gratuito, el Paid Plan **no** es prerrequisito, y
la continuidad se decide **antes** del agotamiento o del **2027-03-15** entre **A** pagar y
continuar o **B** desmontar, migrar o preservar.

**Lo que el agente añadió en consecuencia, porque la decisión lo hacía necesario:**

> **La opción B no era ejecutable.** Los *backups* automáticos de RDS, los *snapshots* y el
> bucket de medios **viven dentro de la cuenta y desaparecen con ella**. **D-10** protegía de
> fallos de AZ, de error humano y de corrupción — **no** de la pérdida de la cuenta.

Por eso **D-10 incorpora una vía de salida** ([decisiones §10.1](../architecture/production-postgresql-rds-decisions.md#101-vía-de-salida-exportación-fuera-de-la-cuenta)):
el **esquema** no se exporta —son las revisiones de Alembic ya versionadas en Git—; los
**datos** salen con `COPY … TO STDOUT` en CSV desde el ejecutor privado usando `psycopg`
—**sin añadir el binario `pg_dump`**—, se escriben en un prefijo dedicado del bucket por el
**gateway endpoint** y **un humano autorizado** los descarga a su estación, donde los custodia
el respaldo local de `Task/004` (**R-12**). **Sin NAT, sin servicio nuevo, sin binario extra.**

**Criterio de salida:** `Task/040` debe **restaurar desde ella** en un PostgreSQL 17.11 local.
**Un CSV en un bucket no es una salida probada.**

**Reglas para que la decisión no se tome por omisión:** ningún runbook depende de una
renovación automática; la fecha y el saldo son un **gate operativo** de `Task/041`; se
recomienda un **recordatorio ~30 días antes**; y **el silencio no es una opción neutra**,
porque el resultado por defecto es perder la cuenta. **R-47** reformulado en consecuencia.

## 7. Reparto 030–041 confirmado, sin ciclos

| Task | Qué debe demostrar, en una línea |
| --- | --- |
| **030** | *State* D-06 y **extinción de EX-028-C7** **antes** de cualquier `apply` de aplicación, incluido el de `Task/031`; bucket de medios y D-08 sin romper las URL prefirmadas |
| **031** | Red y RDS privados, TLS, KMS, 3 identidades SQL con `blog_app` **sin DDL** comprobado por fallo, **restore sintético y PITR con tiempos medidos**, acceso privado operativo, CloudWatch y D-20 tras verificar D-19 |
| **032** | SQL real con `verify-full`, **tráfico sin NAT demostrado**, **D-12 medida**, latencia medida, y el **comportamiento de la ENI tras inactividad** |
| **033**–**035** | API Gateway, Pages y DNS, sin acceso a la base de datos |
| **036** | Primera migración por el canal privado con *snapshot* previo, **duración real contra los 900 s**, R-43 y R-44 implementados |
| **038** | Canal repetible serializado, rol propio, reversión probada |
| **039** | Terraform en CI con guardas; **sin `destroy` real automático** |
| **040** | Negativos de SG, IAM y **TLS sin `sslrootcert`**, carga y saturación, **restore reciente con RPO/RTO medidos**, alarmas disparadas, DR **y restaurar desde la vía de salida** en un PostgreSQL 17.11 local |
| **041** | Factura real contra el escenario A; créditos, caducidad y D-19; **gate fechado del 2027-03-15** con recordatorio ~30 días antes |

**Ninguna tarea exige evidencia de un recurso que crea una tarea posterior**, y ninguna
depende de otra que dependa de ella. `Task/029` **no** exigió RDS, Lambda, restore ni RTT
reales. Criterios completos en
[§9](../architecture/production-postgresql-rds-decisions.md#9-qué-debe-demostrar-cada-tarea-posterior).

## 8. Contratos de Terraform — preparados, no implementados

Tres módulos nuevos contratados: `modulos/red`, `modulos/base_de_datos` y
`modulos/ejecutor_privado`, con entradas, salidas y orden de dependencias, deducido por
referencias y **sin `depends_on` de módulo**.

**Hallazgo del grafo real:** `terraform/providers.tf` lista hoy 8 servicios en su bloque
`endpoints` y **le faltan `ec2`** —VPC, subnets, SG y *endpoints* se crean por la API de
EC2— **y `rds`**. Es una **diferencia legítima** de la matriz de paridad (fila 1) y debe
añadirla `Task/031`, no esta tarea.

**Lo que `Task/029` no hizo, comprobable en el `git diff`:** ningún `aws_db_instance`,
`aws_db_subnet_group`, `aws_vpc`, `aws_subnet`, `aws_security_group`, `aws_kms_key`,
`aws_vpc_endpoint` ni `aws_db_proxy`. **Ni un solo archivo de `terraform/` modificado.**

## 9. Gates ejecutados

Versiones usadas: Git `2.53.0.windows.1`, Python `3.12.10`, Gitleaks `8.30.1` —la versión
que fija el CI—.

| Gate | Comando | Resultado |
| --- | --- | --- |
| Espacios y conflictos | `git diff --check` | **OK** — sin hallazgos |
| UTF-8, LF, controles y BOM | Script sobre los 9 archivos de la tarea | **OK** — 0 CRLF, 0 CR sueltos, 0 caracteres de control, 0 BOM |
| Enlaces relativos y anclas | Script que **ignora fences y *code spans*** | **OK** — **526** enlaces relativos comprobados, **0 rotos** |
| Encabezados duplicados | *Slugs* repetidos en los documentos de la tarea | **OK** — 0 duplicados, tras corregir una colisión (§9.1) |
| Secretos | `gitleaks dir . --redact=100 --config .gitleaks.toml` sobre el entregable versionado | **OK** — 5,70 MB, 263 archivos, **0 *leaks*** |
| Grafo de tareas | Script que lee las dependencias declaradas en el ROADMAP | **OK** — 0 ciclos, 0 dependencias hacia una tarea posterior |
| Terraform | `git status` y `git diff` sobre `terraform/` | **OK** — **`terraform/` sin cambios**; ver §9.1 |
| Sin recursos Terraform | Ningún `.tf`, `.tfvars` ni `.hcl` en el diff · ninguna línea `^+resource "aws_` · los 3 archivos nuevos son Markdown bajo `docs/` · ningún fence `hcl`/`terraform` | **OK** en las cuatro comprobaciones |
| Python y PowerShell | `compileall` y parser | **No aplica** — ningún `.py` ni `.ps1` modificado |

### 9.1 Cinco notas de método, para que otra sesión no repita el trabajo

1. **El gate de enlaces encontró un defecto real y se corrigió, dos veces.** 22 anclas en la
   primera ronda y 13 en la segunda habían perdido las tildes que GitHub **conserva** en sus
   *slugs*: `#7-modelo-economico-…` frente a `#7-modelo-económico-…`. Se corrigieron en
   lectura y escritura **binaria** para no alterar los finales de línea. Que reapareciera en
   la segunda ronda confirma que **es un error fácil de repetir** y que el gate tiene que
   comprobar **la ancla, no solo que el archivo exista**.
2. **El alcance del escaneo de secretos importa.** Escanear el directorio completo devuelve
   **586 hallazgos sobre 4,58 GB**: son `tmp/`, `.venv` y directorios de trabajo no
   versionados. Escanear **solo el entregable** —`git ls-files` más los archivos nuevos, 263
   en total, copiados conservando rutas y con `.gitleaks.toml` dentro— devuelve **0**. La
   ruta relativa es necesaria para que la *allowlist* del archivo de configuración aplique.
3. **`terraform fmt`/`validate` no se re-ejecutaron, y se explica por qué.** No hay binario
   de Terraform instalado en la estación, y `terraform/` **no tiene un solo archivo
   modificado**, lo que se verificó con `git status` y `git diff`. El propósito del gate
   —confirmar que el grafo de recursos sigue intacto— se cumple con esa comprobación, que es
   más directa. El CI ejecutará `fmt -check` y `validate` con la versión fijada `1.16.2` al
   abrirse el PR.

4. **Una colisión de numeración, detectada por el mismo gate.** Al insertar las secciones
   nuevas del modelo económico quedaron **dos §7.7** en el paquete de decisiones, con el mismo
   *slug*. La de Grafana pasó a **§7.8**. Desde entonces el gate comprueba también
   **encabezados duplicados**, no solo enlaces.
5. **El gate «sin recursos AWS» necesitaba precisión.** La versión inicial buscaba
   `aws_db_instance`, `aws_vpc` y compañía en el diff, y devolvía **una coincidencia**: la
   propia línea que **documenta el gate**. Un `grep` de nombres de recurso no distingue prosa
   de declaración. La versión definitiva comprueba cuatro cosas independientes: que **ningún
   `.tf`, `.tfvars` ni `.hcl` esté en el diff**, que no haya ninguna línea
   `^+resource "aws_`, que los tres archivos nuevos sean **Markdown bajo `docs/`** y que no
   haya **fences `hcl` ni `terraform`**. Las cuatro pasan.

Los scripts de validación quedaron en el directorio temporal de la sesión: **no se añadió
herramienta nueva al repositorio**, porque la ficha no lo pedía y `scripts/` no está en el
alcance.

### 9.2 Grafo de tareas verificado

Dependencias leídas del ROADMAP, no supuestas:

```
027 <- 026      032 <- 030, 031      037 <- 036
028 <- 027      033 <- 032           038 <- 036
029 <- 027, 028 034 <- 033           039 <- 037, 038
030 <- 029      035 <- 034           040 <- 039
031 <- 030      036 <- 035           041 <- 040
```

**0 ciclos. 0 dependencias hacia una tarea posterior.** El gate de **D-06** se conserva:
`Task/031` —red y RDS— depende de `Task/030` —*state*—, así que **ningún recurso de
aplicación puede crearse antes de que D-06 esté resuelta**. `Task/029` depende solo de
`Task/027` y `Task/028`, ambas aprobadas.

## 10. Archivos tocados

| Archivo | Cambio |
| --- | --- |
| `docs/architecture/production-postgresql-rds-decisions.md` | **Nuevo.** Paquete de decisiones: 15 secciones, inventario A–E, costo, conexiones, contratos, planes de prueba y checkpoint humano |
| `docs/runbooks/rds-private-administration.md` | **Nuevo.** Runbook del canal privado: migración, purga, restore y recuperación del administrador. **Preparado y no ejecutado** |
| `docs/architecture/production-postgresql-rds.md` | Enmienda de instancia; §3 con el estado de entrega; **§6.1 nueva** con el resultado del gate y el hallazgo del plan de la cuenta; §9 con la re-verificación de fuentes |
| `docs/architecture/open-decisions.md` | D-22, D-23, D-24 y D-10 con su **Propuesta**; D-12 con el presupuesto derivado; D-11 y D-19 con estimación; D-13 con el resultado del gate; índice y nota de recuento |
| `docs/project-management/STATUS.md` | Entrada fechada; *Vista rápida* con tarea en curso y próxima; **R-47 nuevo** con su justificación de ID; recuento 47 → 48; aporte de `Task/029` a R-29–R-44 |
| `docs/project-management/ROADMAP.md` | Estado de ETAPA 09 y fila de `Task/029`; nota sobre la columna «Define / construye» y las dos condiciones previas nuevas |
| `docs/tasks/TASK-029-prepare-production-postgresql-rds.md` | §0 con la preparación Git ejecutada; estado; §9–§20 con resultados reales |
| `docs/runbooks/README.md` | Índice con el runbook nuevo |
| `docs/task-reports/TASK-029-report.md` | **Nuevo.** Este reporte |

**Añadido en la segunda ronda, sobre los mismos nueve archivos** —no se creó ninguno nuevo—:
**§7.5 EX-029-D13**, **§7.6** con las cuatro cifras y los créditos verificados, **§7.7** con
la decisión fechada, **§10.1** con la vía de salida y **§11** reescrita como registro de
decisiones en el paquete; **§6.2** en el canónico; **EX-029-D13** y la ampliación de D-10 en
el registro de decisiones; entrada fechada y **R-47 reformulado** —con su formulación
original conservada en un bloque plegable— en STATUS; fila nueva en el mapa transversal del
ROADMAP; y **§6.1** en el runbook con el procedimiento de exportación.

**Totales:** 3 archivos nuevos —2.029 líneas— y 6 modificados, con **+750 / −37** en los
modificados. **`terraform/`, `scripts/`, `bootstrap/`, `docker-compose.yml` y los workflows:
sin un solo cambio.**

**`personal-blog-backend` y `personal-blog-frontend`: cero archivos modificados, cero ramas**
—verificado al cierre: ambos en `main`, con el árbol limpio—.

## 11. Decisiones del usuario, resueltas

Las cuatro quedaron resueltas el **2026-09-27**. Registro íntegro en
[§11 del paquete](../architecture/production-postgresql-rds-decisions.md#11-decisiones-del-usuario--h-1-a-h-4-resueltas).

| # | Qué se pedía | Decisión del usuario | Efecto |
| --- | --- | --- | --- |
| **H-1** | Confirmar la región | **`us-east-2`**, coincide con la recomendación | Región objetivo fijada; precios y bundle de CA ya eran los de us-east-2 |
| **H-2** | Resolver el gate de D-13 | **Acepta el exceso** para la etapa experimental, **sin maquillar** el cálculo | **EX-029-D13**: suspende solo el sublímite AWS; **techo global intacto**; vence con los créditos o el 2027-03-15 |
| **H-3** | Datos privados de créditos | **USD 120.00**, límite **2027-03-15**, USD, sin restricciones | Modelo de consumo completo. **Manda la fecha, no el saldo** |
| **H-4** | Plan de la cuenta | **No** pasar a Paid Plan y **no** hacerlo prerrequisito de `Task/031` | Decisión fechada A/B, y **vía de salida obligatoria** añadida a D-10 |

**En H-4 el usuario decidió en contra de la propuesta del agente, y se acata.** La decisión
es coherente con el propósito declarado de la etapa. Lo que el agente aportó no fue insistir,
sino señalar la consecuencia que la decisión dejaba abierta —la opción B no era
ejecutable— y **cerrarla con diseño**: la vía de salida de la §6.3.

### 11.1 Un dato opcional por verificar, que no bloquea nada

La documentación dice que el Free Plan termina *«after six months or when your credits are
fully used»*. `Task/027` observó el plan activo el **2026-09-17** y el límite de créditos es
el **2027-03-15**. Si la cuenta se abrió hacia el **2026-09-15**, esos seis meses caen
**exactamente** en esa fecha, y entonces no sería solo el vencimiento del crédito: sería el
**cierre de la cuenta**.

**Es una hipótesis por coincidencia aritmética, no un hecho**: el agente no conoce la fecha de
apertura. Si el usuario quiere cerrarla, basta mirar en **Billing and Cost Management → Free
tier** si figura una fecha de finalización del plan gratuito, y aportar solo esa fecha.

**No bloquea** porque la política elegida —decidir antes del agotamiento **o** del
2027-03-15— es correcta en su calendario en ambos casos. Lo único que cambiaría es la
**severidad** de no decidir a tiempo, y eso ya está recogido en **R-47**.

### 11.2 Decisiones humanas que esta tarea traslada, con fecha y propietario

| Decisión futura | Cuándo | Propietario |
| --- | --- | --- |
| Continuidad: pagar o desmontar | **Antes del agotamiento del crédito o del 2027-03-15** | Usuario, con `Task/041` como gate |
| Elevar el gasto por RDS Proxy, Secrets Manager, Multi-AZ o un interface endpoint | Solo si se cumple su criterio objetivo **medido** | Usuario, sobre evidencia de `Task/032`/`Task/040` |
| Introducir NAT Gateway o un servicio excluido | Solo con necesidad demostrada | Usuario |

## 12. Pasos de validación para el usuario

1. Comprobar que la rama es `Task/029-Preparar-PostgreSQL-Produccion-en-RDS`, nace de `main`
   en `d96d5d5` y **solo existe en infra**.
2. Revisar el
   [paquete de decisiones](../architecture/production-postgresql-rds-decisions.md),
   especialmente el **resumen ejecutivo de §14** y el registro de decisiones de **§11**.
3. Verificar el **gate de D-13** de §6.1: los precios unitarios permiten recalcular cada
   subtotal a mano.
4. Comprobar que la **§11** recoge fielmente sus cuatro decisiones y que **EX-029-D13** está
   acotada como acordó: suspende solo el sublímite AWS, **no** toca el techo global, vence con
   los créditos o el 2027-03-15 y **no autoriza recursos**.
5. Revisar la **vía de salida** de la §6.3: es la pieza que hace ejecutable la opción «no
   continuar», y su prueba está asignada a `Task/040`.
6. Confirmar que no hay recursos AWS creados: ningún `.tf` en el diff, ninguna declaración
   `resource "aws_`, y `terraform/` intacto.
7. Comprobar que ningún criterio de §7 exige un recurso que su propia tarea no crea.
8. Opcional, un minuto: la **fecha de finalización del plan gratuito** en *Billing → Free
   tier*, si AWS la muestra (§11.1). Afinaría la severidad del gate, no lo cambia.

## 13. Límites y estado

- **Cero recursos AWS creados.** Cero `apply`, `import`, `destroy`, `-target` y cero
  operaciones sobre el *state*.
- **Cero secretos** generados, leídos o almacenados. **Cero consultas de facturación:** los
  datos de créditos los verificó y aportó el usuario.
- **Cero llamadas mutantes a AWS.**
- **No se activó Paid Plan, no se modificó Billing y no se cambió el plan de la cuenta.**
- **El techo global de D-13 no se tocó.** **EX-029-D13** suspende solo el sublímite AWS, está
  fechada y **no autoriza ningún recurso**.
- **`Task/030` no iniciada. `Task/031` no iniciada.**
- **Backend y frontend intactos**, sin rama y en `main`.
- **ADR-010 no se reescribió:** no apareció contradicción que exija gobierno nuevo. El
  hallazgo del plan de la cuenta es un **riesgo operativo nuevo** (**R-47**), no un conflicto
  con la decisión arquitectónica.
- **Sin commit, sin push, sin PR, sin merge**, conforme a
  [PROJECT_INSTRUCTIONS](../claude/PROJECT_INSTRUCTIONS.md) §6.

## 14. Aprobación

| Campo | Valor |
| --- | --- |
| Estado | **Lista para validación** |
| Fecha de aprobación | Pendiente |
| Aprobado por | Pendiente — **solo el usuario** |
| Expresión requerida | `approved: Task/029-Preparar-PostgreSQL-Produccion-en-RDS` |

Toda decisión de esta tarea es **Propuesta — pendiente de aprobación**. **El agente no
autoaprueba.**
