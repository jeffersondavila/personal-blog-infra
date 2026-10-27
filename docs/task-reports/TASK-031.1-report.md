# TASK-031.1 — Reporte de mantenimiento documental

**Estado: Lista para validación — 2026-10-27** *(UTC, como el cierre de Task/031; en America/Guatemala, la noche
del 2026-10-26)*. Mantenimiento **fuera de las 41 tareas**.
[Ficha](../tasks/TASK-031.1-correct-pre-task032-documentation-discrepancies.md).

## 1. Resultado y alcance

La auditoría previa a Task/032 encontró **nueve discrepancias verificadas** (H1–H9) entre la documentación vigente y
el estado aprobado, todas documentales. Se corrigieron en `personal-blog-infra` seis documentos Markdown y los
comentarios de tres archivos no Markdown; STATUS y ROADMAP registran además la tarea.

Task/031 conserva su aprobación y Task/032 sigue **Pendiente, no iniciada**. Avance sin cambios: **31/41 ≈ 76 %**,
ETAPA 10 **2/7 ≈ 29 %**.

Nada de esto cambia:
- AWS, Terraform, el baseline S-09 ni las excepciones de seguridad;
- las listas cerradas y las guardas del laboratorio;
- la lógica de CI, el código funcional, el backend ni el frontend.

## 2. Método

1. **Inventario** de lo que la documentación presenta como vigente: versiones, cifras, estados de tareas y de
   decisiones, y estado de Git o GitHub.
2. **Contraste** de cada afirmación con su fuente: Git y GitHub, el código, el registro de decisiones, el baseline
   S-09, el manifiesto de MinIO y el módulo del laboratorio, importado y medido.
3. **Clasificación** con las clases de auditoría de [Task/029.1](TASK-029.1-report.md):
   - **A, historia válida:** entradas o notas fechadas, ciertas en su fecha;
   - **B, estado actual válido;**
   - **C, drift real:** se corrige.
4. **Barrido dirigido** de afirmaciones en presente sobre Task/029–Task/031 en los documentos vigentes, fuera de
   los bloques de historia. Encontró H9 y descartó los demás casos (§7).

Alcance auditado: README, CONTRIBUTING, la gestión del proyecto, la arquitectura, los runbooks, los ADR, las etapas,
las fichas, `docs/claude`, el producto, `.env.example`, los workflows y el laboratorio.

## 3. Hallazgos

Las líneas son las de `main` antes de esta tarea.

| # | Relevancia | Dónde | Qué afirmaba | Fuente que lo contradice |
| --- | --- | --- | --- | --- |
| H1 | Media-alta | `docs/claude/PROJECT_INSTRUCTIONS.md:530`, §16 regla 10 | «Task/029 sigue Pendiente» | ROADMAP: Task/029 aprobada el 2026-09-27, «**no provisiona nada**»; tabla canónica de STATUS |
| H2 | Media | `docs/project-management/STATUS.md:10`; `docs/task-reports/TASK-031-report.md:5697`, §53.6 punto 4 | La fusión del PR #57 seguía pendiente; «El PR #57 sigue abierto» | WORKFLOW §6.1, reglas 1 y 2 |
| H3 | Media | `docs/runbooks/deployment-recovery.md:96` y nota de H-031-1A en `:102` | «Las diez diferencias» del emulador y cinco entradas de deriva | `laboratorio.py`: **6** clases y **16** entradas hoy; 12 y 16 al aprobar Task/031 |
| H4 | Media | `docs/architecture/aws-local-parity.md:659`, `:663`, `:664`, `:666` y `:668` | Floci 2.1.0 descrito en presente; la fila de Terraform sin 2.3.0 | Reporte de Task/031 §53.2, `laboratorio.py` y `local.tfvars` |
| H5 | Media | `docs/project-management/STATUS.md:3353`, fila R-018-3 | Quedan **99** identidades aceptadas de MinIO | `security/vulnerability-baseline.json`: **10** |
| H6 | Baja | `.env.example:56` | La identidad vigente de MinIO es la de Task/028 | `docker/minio/build-manifest.json`, contrato v3 |
| H7 | Baja | `.github/workflows/ci-infra.yml:492` y `:531` | El verificador solo admite cambios en `/usr/bin/minio`; Floci tiene una aceptación temporal | `scripts/minio/artifact.py`; baseline de Floci sin aceptaciones |
| H8 | Baja | `terraform-datos/variables.tf:126` | El emulador «publica» `us-east-1-az1` | Reporte de Task/031 §53.2 y `local.tfvars` |
| H9 | Media | `docs/architecture/target-production-architecture.md:668`, §14 | D-22, D-23, D-24, D-10 y D-12 «siguen abiertas» y son de Task/029 | `open-decisions.md`: las cuatro primeras, Resueltas el 2026-09-27; D-12 abierta, propiedad de Task/032 |

**Relevancia.**
- **H1** vive en las instrucciones que cada sesión carga como vigentes: podía llevar a tratar Task/029 como trabajo
  pendiente.
- **H9** toca D-12, que cierra Task/032.
- Ningún hallazgo es un defecto técnico ni afecta a AWS.

## 4. Evidencia por hallazgo

### H1 — Task/029 Pendiente en las instrucciones del proyecto

- ROADMAP, ETAPA 09: «Task/029 aprobada el 2026-09-27». En la misma sección: «**decide y prepara** el RDS
  privado y **no provisiona nada**». La [ficha de Task/029](../tasks/TASK-029-prepare-production-postgresql-rds.md)
  dice lo mismo.
- STATUS: la tabla canónica registra Task/029 **Aprobada (2026-09-27)** desde H-030.2-counter-fix. Task/031 se
  aprobó el 2026-10-21.
- PROJECT_INSTRUCTIONS se mantiene como ley vigente: §15 ya registra estados posteriores, como D-06 Resuelta o
  EX-028-C7 Extinguida.

### H2 — Estado vivo del PR de Task/031

- WORKFLOW §6.1, regla 1: STATUS no afirma el estado vivo de un PR. Regla 2: los datos históricos llevan su fecha
  de observación.
- *Observado el 2026-10-27 en GitHub:*
  - PR #57 `MERGED`, `mergedAt` 2026-10-27T01:00:56Z, merge `1fdc843`, base `main`;
  - CI `success` en `main` (`1fdc843`) y en `dev` (`f833014`);
  - ninguna rama Task/031 local ni remota.
- **Corrección según el precedente de Task/004.2:**
  - STATUS separa la regla permanente —la fusión es exclusiva del usuario— del hecho fechado que la regla permite
    persistir.
  - El reporte conserva el punto 4 palabra por palabra y añade un complemento fechado.

### H3 — Tolerancias del laboratorio en el runbook

Importando `scripts/laboratorio/laboratorio.py` como lo hacen las pruebas:

| Momento | `DIFERENCIAS_DEL_DESTINO_LOCAL_DE_DATOS` | `DRIFT_DEL_DESTINO_LOCAL_DE_DATOS` |
| --- | --- | --- |
| H-031-1A (nota del runbook, 2026-10-03) | 10 | 5 |
| Aprobación de Task/031 (`e5daf78`) | **12** | **16** |
| `main` actual, Floci 2.3.0 | **6** | **16** |

El salto de H-031-6 está en el [reporte de Task/031
§50.3](TASK-031-report.md#503-laboratorio-causa-y-corrección-del-fallo-del-ciclo-completo): 11 declaraciones de
deriva y 2 diferencias nuevas. El de 2.3.0 está en
[§53.2](TASK-031-report.md#532-floci-230-tres-cambios-de-comportamiento-detectados-fallando-cerrado): se retiran 6
clases que ya no ocurren.

Las 6 vigentes son:
- `aws_db_instance`: `ca_cert_identifier`, `network_type`, `port` y `storage_type`;
- `aws_db_parameter_group.parameter`;
- `aws_cloudwatch_metric_alarm.extended_statistic`.

El ciclo no imprime las listas declaradas. `idempotencia_del_root_de_datos` imprime lo **observado** en
`resource_changes` y `resource_drift`, ya juzgado contra ellas.

### H4 — Floci 2.1.0 en presente en la matriz de paridad

- **Zonas:** §53.2 registra que 2.3.0 rechaza `us-east-1-az1` y publica el formato de AWS.
  `terraform-datos/entornos/local/local.tfvars` usa `use1-az1` y `use1-az2`.
- **Atributos:** al aprobar Task/031 (`e5daf78`), el laboratorio toleraba `aws_ssm_parameter.key_id`,
  `aws_ssm_parameter.tier` y `aws_cloudwatch_metric_alarm.datapoints_to_alarm`. Con 2.3.0 se retiraron porque el
  emulador ya devuelve esos atributos (comentario de `laboratorio.py`). `extended_statistic` sigue tolerada.
- **Fechas:** «(2026-10-26)» repite la forma que la propia matriz ya usa para el mantenimiento de CI: fila de RDS y
  cabecera. Esa es la fecha del ciclo completo final de §53.2.

### H5 — Recuento de R-018-3

Entrada `minio` del baseline: **10** aceptaciones, todas HIGH, ninguna temporal:
- 6 en `usr/bin/minio`;
- 2 en `usr/bin/mc`;
- 2 en `os-pkgs:redhat`, `libcap` y `libacl`.

Su `rationale`:
- Task/028 redujo las 99 a 10.
- El contrato v3 de Task/031 corrigió dentro del derivado las 18 identidades nuevas «sin aceptar ninguna».

Task/028 se aprobó el 2026-09-26.

### H6 — Comentario de `MINIO_VERSION`

`docker/minio/build-manifest.json`:
- esquema **v3** y constructor `golang:1.27.3`;
- `minio` y `mc` con grpc v1.83.2, x/net v0.60.0 y klauspost/compress v1.18.7;
- `package_updates` con `pcre2` de Task/031;
- `supersedes` con la identidad de Task/028 y, anidada, la de Task/027.1.

El valor de `MINIO_VERSION`, etiqueta y digest `sha256:95b28f31…`, **no cambia**.

### H7 — Comentarios de CI

- `scripts/minio/artifact.py`, `BUILD_VERSION = 3`: el derivado puede llevar los binarios y **una** capa de paquetes
  declarada con sus miembros exactos.
- Entrada `floci` del baseline: **0** aceptaciones. Su `expected_digest` coincide con `LAB_EMULADOR_DIGEST` de
  `laboratorio/.env.laboratorio.example`. H-025-6 y H-025-7 se cerraron por remediación.
- Solo cambian líneas de comentario: todas las líneas `-`/`+` del diff empiezan por `#`.

### H8 — Comentario de la validación de `subredes`

La expresión regular no cambia y sigue aceptando los dos formatos. Solo el comentario pasa a pasado lo que publicaba
Floci 2.1.0.

### H9 — Decisiones de Task/029 en la arquitectura objetivo

- [Registro](../architecture/open-decisions.md): D-10, D-22, D-23 y D-24 **Resuelta (2026-09-27)**. D-12 sigue
  «Abierta — presupuesto preliminar **aprobado** el 2026-09-27 con `Task/029` … `Task/032` cierra **con
  medición**».
- `git log -L` del párrafo: su último cambio es de Task/028.2, del 2026-09-27, anterior a la aprobación de Task/029.
- **Fuera de alcance:** el párrafo equivalente dentro del bloque «Historia» del modelo VPS es historia válida (A) y
  no se toca.

## 5. Archivos y diffs

### 5.1 Inventario

| Archivo | Hallazgo | Cambio |
| --- | --- | --- |
| `docs/claude/PROJECT_INSTRUCTIONS.md` | H1 | §16, regla 10 |
| `docs/project-management/STATUS.md` | H2, H5 y registro | Entrada del 2026-10-26, fila R-018-3, entrada de Task/031.1 y *Vista rápida* |
| `docs/project-management/ROADMAP.md` | Registro | Entrada de Task/031.1 |
| `docs/task-reports/TASK-031-report.md` | H2 | Complemento fechado tras §53.6 |
| `docs/runbooks/deployment-recovery.md` | H3 | Párrafo de §4 y complemento fechado |
| `docs/architecture/aws-local-parity.md` | H4 | Cinco filas de la matriz |
| `docs/architecture/target-production-architecture.md` | H9 | Párrafo de §14 |
| `.env.example` | H6 | Comentario de `MINIO_VERSION` |
| `.github/workflows/ci-infra.yml` | H7 | Dos comentarios |
| `terraform-datos/variables.tf` | H8 | Comentario de la validación de `subredes` |
| [Ficha TASK-031.1](../tasks/TASK-031.1-correct-pre-task032-documentation-discrepancies.md) | — | Nueva |
| Este reporte | — | Nuevo |

### 5.2 Diffs

**H1**, PROJECT_INSTRUCTIONS §16:

```diff
 10. Esta regla no crea recursos ni secretos: cada recurso exige su tarea propietaria
-    y la autorización explícita del usuario. Task/029 sigue Pendiente.
+    y la autorización explícita del usuario. Task/029 —aprobada el 2026-09-27— no
+    provisionó nada; la red y el RDS los provisionó Task/031, aprobada el 2026-10-21.
```

**H2**, entrada del 2026-10-26 de STATUS, con los enlaces abreviados:

```diff
-Ningún cambio en AWS; el estado aprobado, el avance y las decisiones no cambian. La fusión del PR #57 sigue siendo
-del usuario. [Reporte §53](…).
+Ningún cambio en AWS; el estado aprobado, el avance y las decisiones no cambian. La fusión del PR es exclusiva del
+usuario, y su estado vivo se consulta en GitHub ([WORKFLOW §6.1](…)).
+*Observado el 2026-10-27: PR #57 fusionado en `main` con el merge `1fdc843`; normalización `main → dev` en
+`f833014`.* [Reporte §53](…).
```

**H2**, reporte de Task/031. El punto 4 se conserva y el complemento se añade al final de §53.6:

```diff
 GitHub es la fuente viva del estado de los checks.
+
+> **Complemento del 2026-10-27 (`Task/031.1`).** El punto 4 describía el estado que se observó al escribir este
+> registro, el 2026-10-26. Según [WORKFLOW §6.1](…),
+> el estado vivo de un PR no se versiona como vigente, así que se conserva aquí solo como esa observación. Las fechas
+> son UTC, como el resto del cierre ([§52](…)).
+>
+> *Observado el 2026-10-27:* el PR #57 se fusionó en `main` con el merge `1fdc843`, la normalización
+> `main → dev` es `f833014` y la rama Task031 se eliminó en local y en remoto. El CI de `main` y el de `dev`
+> terminaron en `success`.
```

**H3**, runbook de recuperación. La nota de H-031-1A se conserva entera:

```diff
-plan de datos solo tolera las diez diferencias estrechas del emulador declaradas en la
-[matriz de paridad](../architecture/aws-local-parity.md), nunca drift nuevo ni `ignore_changes`.
+plan de datos solo tolera las diferencias estrechas del emulador declaradas en la
+[matriz de paridad](../architecture/aws-local-parity.md) y en `DIFERENCIAS_DEL_DESTINO_LOCAL_DE_DATOS` de
+`scripts/laboratorio/laboratorio.py` —seis clases con Floci 2.3.0—, nunca drift nuevo ni `ignore_changes`.
```

```diff
+> **Actualizado el 2026-10-27 (`Task/031.1`).** Las cifras de la nota anterior son las de H-031-1A y se conservan
+> como historia. Su evolución:
+> - **Desde H-031-6** (ciclo del 2026-10-20, [reporte de Task/031 §50.3](…)):
+>   la lista cerrada de `resource_drift` tiene **16** entradas y `resource_changes` toleraba **12** clases.
+> - **Con Floci 2.3.0** (mantenimiento de CI de `Task/031`, 2026-10-26): `resource_changes` tolera **6** clases. La
+>   entrada de `aws_db_instance` exige `latest_restorable_time` con el contrato `instante_movil` de la convergencia
+>   productiva.
+>
+> La fuente es `scripts/laboratorio/laboratorio.py`. El resumen del ciclo imprime lo observado en las dos secciones,
+> ya juzgado contra esas listas.
```

**H4**, matriz de paridad. Son filas de tabla de una sola línea, así que se muestran solo los fragmentos que
cambian:

| Fila | Antes | Después |
| --- | --- | --- |
| Terraform | «…tres canarios ausentes*» | «…tres canarios ausentes. Con Floci 2.3.0 (mantenimiento de CI, 2026-10-26): 6 clases de diferencia y las mismas 16 entradas de deriva, con `latest_restorable_time` como instante móvil*» |
| VPC y red | «Publica los ID de zona como `us-east-1-az1`…» | «Floci 2.1.0 publicaba los ID de zona como `us-east-1-az1`…» y, tras el cambio de configuración: «Desde 2.3.0 (2026-10-26) publica el formato de AWS y `local.tfvars` usa `use1-az1`.» |
| KMS, TLS y backups | «SecureString sin cifrar y sin `KeyId`/`Tier` devueltos» | «SecureString sin cifrar. Floci 2.1.0 no devolvía `KeyId` ni `Tier`; 2.3.0 sí (2026-10-26), sin que eso implique cifrado» |
| Ejecutora h0316 | «(Floci no devuelve `KeyId` ni `Tier`)» | «(Floci 2.1.0 no devolvía `KeyId` ni `Tier`; 2.3.0 sí)» |
| Alarmas de D-11 | «Floci **no devuelve** `DatapointsToAlarm` ni `ExtendedStatistic`» | «Floci 2.1.0 **no devolvía** `DatapointsToAlarm` ni `ExtendedStatistic`» y, a continuación: «Desde 2.3.0 (2026-10-26) devuelve `DatapointsToAlarm` y sigue sin devolver `ExtendedStatistic`.» |

**H5**, fila R-018-3 de STATUS, columna de estado. El resto de la celda no cambia:

| Antes | Después |
| --- | --- |
| «**Abierto.** No lo cierra `Task/027.1`: quedan **99** identidades aceptadas —52 en `usr/bin/minio`, 45 en `usr/bin/mc`, 2 de paquetes del sistema; 95 HIGH y 4 CRITICAL—.» | «**Abierto.** Quedan **10** identidades aceptadas desde `Task/028` (2026-09-26) —6 en `usr/bin/minio`, 2 en `usr/bin/mc` y 2 de paquetes del sistema, `libcap` y `libacl`; las 10 HIGH—. `Task/031` (mantenimiento de CI, 2026-10-26) corrigió dentro del derivado las 18 identidades nuevas sin aceptar ninguna. *(Historia: tras `Task/027.1` quedaban 99 —52 en `usr/bin/minio`, 45 en `usr/bin/mc` y 2 de paquetes del sistema; 95 HIGH y 4 CRITICAL—; tampoco aquella tarea lo cerró.)*» |

**H6**, `.env.example`:

```diff
-# Esta identidad reconstruye /usr/bin/minio y /usr/bin/mc con grpc v1.83.2
-# (Task/028, H-028-2). La anterior, que conservaba CVE-2026-84445 alcanzable,
-# sigue publicada como historia y esta declarada en `supersedes` de
-# `docker/minio/build-manifest.json`. NO se usa.
+# Esta identidad es el contrato v3 (Task/031): reconstruye /usr/bin/minio y
+# /usr/bin/mc con Go 1.27.3, grpc v1.83.2, x/net v0.60.0 y klauspost/compress
+# v1.18.7, y actualiza pcre2 dentro del derivado en una capa de paquetes
+# declarada. Las anteriores (Task/028 y Task/027.1) siguen publicadas como
+# historia y estan declaradas en `supersedes` de
+# `docker/minio/build-manifest.json`. NO se usan.
```

**H7**, `ci-infra.yml`:

```diff
           # sujeta a tolerancia cero. Se construye sin cache, como OCI local y
-          # sin publicar; el verificador exige que solo cambie /usr/bin/minio.
+          # sin publicar; el verificador exige que solo cambie lo declarado en el
+          # build manifest: los dos binarios y la capa de paquetes (contrato v3).
```

```diff
           # El emulador del laboratorio se escanea por su DIGEST exacto, que es
-          # tambien la identidad a la que esta ligada su aceptacion temporal.
+          # tambien la identidad que fija su entrada del baseline.
```

**H8**, `terraform-datos/variables.tf`:

```diff
-    # Dos formatos de ID: el de AWS (`use2-az1`) y el que publica el emulador
-    # (`us-east-1-az1`), que es un VALOR del destino local, no un diseno
-    # distinto (hallazgo de H-031-1, matriz de paridad). Un nombre de AZ como
-    # `us-east-2a` sigue rechazado: depende de la cuenta.
+    # Dos formatos de ID: el de AWS (`use2-az1`) y el que publicaba el emulador
+    # hasta Floci 2.1.0 (`us-east-1-az1`), un VALOR del destino local y no un
+    # diseno distinto (hallazgo de H-031-1, matriz de paridad); desde 2.3.0 el
+    # emulador publica el de AWS. Un nombre de AZ como `us-east-2a` sigue
+    # rechazado: depende de la cuenta.
```

**H9**, arquitectura objetivo §14:

```diff
-**Sigue abierto** y pertenece a `Task/029`: región, versión, clase, almacenamiento y
-disponibilidad (**D-22**); TLS, KMS y credenciales (**D-23**); canal privado de
-administración y migraciones (**D-24**); backups y recuperación (**D-10**); presupuesto
-preliminar de conexiones (**D-12**).
+**Decidido.** `Task/029`, aprobada el 2026-09-27, resolvió ese día **D-22** (región,
+versión, clase, almacenamiento y disponibilidad), **D-23** (TLS, KMS y credenciales),
+**D-24** (canal privado de administración y migraciones) y **D-10** (backups y
+recuperación), y aprobó el presupuesto preliminar de conexiones. **D-12** no se cerró con
+ella: la cierra `Task/032` con medición. Estado vivo de cada decisión: el
+[registro](open-decisions.md). *(Hasta `Task/031.1` este párrafo decía que todo ello «sigue
+abierto y pertenece a `Task/029`», cierto antes de su aprobación.)*
```

**Registro.**
- Entradas nuevas en la cabecera de STATUS y ROADMAP.
- En la *Vista rápida* de STATUS:
  - **Tarea actual** pasa de «Ninguna en curso» a Task/031.1 Lista para validación;
  - **Próxima tarea prevista** sitúa el nacimiento de Task/032 después del cierre de Task/031.1 y de su
    normalización `main → dev`.

## 6. Historia preservada

- Reporte de Task/031, §53.6 punto 4: intacto, con el complemento fechado a continuación.
- Runbook de recuperación, nota de H-031-1A («diez diferencias», «cinco entradas»): intacta, con su complemento.
- STATUS, R-018-3: las 99 identidades y la frase sobre Task/027.1 se conservan como historia entre paréntesis.
- Matriz de paridad: lo observado con 2.1.0 se conserva, en pasado.
- Arquitectura objetivo, §14: la redacción anterior se conserva entre paréntesis. El bloque «Historia» del modelo VPS
  no se toca.
- Ningún otro reporte, ficha ni entrada fechada cambia.

## 7. Observaciones no corregidas

No contradicen el estado aprobado. Se registran para que no se confundan con lagunas.

| Dónde | Observación | Clase | Por qué no se corrige |
| --- | --- | --- | --- |
| `README.md` §2 | Instantánea del 2026-09-27 | A | Instantánea fechada, válida según WORKFLOW §6.1, regla 2 |
| `docs/adr/ADR-010-production-postgresql-on-rds.md`, «Aceptación y transición» | «Task/029 sigue **Pendiente**» | A | Registro fechado de la aceptación del 2026-09-27. Un ADR aceptado no se reescribe; el estado vivo está en STATUS |
| `docs/architecture/security-boundaries.md` §13.4; `target-production-architecture.md` §15 | «`Task/029` prepara su contrato de custodia y `Task/031` su revisión» (R-12) | A | Plan de la enmienda de Task/028.2, ya cumplido. El resultado —R-12 abierto, con seguimiento en Task/040— está en las dos filas R-12 de STATUS |
| `docs/architecture/production-postgresql-rds-decisions.md` §8 | Contrato de custodia «que `Task/029` entrega» y «se decide con `Task/031`» | A | Entrega fechada de Task/029. Task/031 la revisó y el usuario decidió el 2026-10-16 |
| `production-postgresql-rds-decisions.md`, notas de la ejecutora | «La cuota … no permite reservar» (2026-10-06); «La solicitud de cuota a 1001 sigue abierta» (2026-10-18) | A | Notas fechadas, ciertas en su fecha. Desde el 2026-10-18 la ejecutora no reserva concurrencia; la cuota de 1000 observada el 2026-10-19 está en el reporte de Task/031 §49 (§10) |
| `docs/architecture/open-decisions.md`, D-13 | «El VPS permanece sin cifra hasta `Task/029`» | A | Bloque «Estado al 2026-09-17», seguido de la nota de Task/028.2 sobre RDS |
| `target-production-architecture.md` §22 | Tabla de decisiones abiertas con D-10, D-16, D-17, D-18… | A | Declarada «del 2026-08-23», remite al registro vivo y la sigue la tabla de enmienda |
| `docs/stages/STAGE-10-cloud-deployment.md` y ROADMAP, fila de Task/032 | PgBouncer y VPS en la redacción original | A | Cada celda lleva su enmienda de Task/028.2, con Lambda en VPC y RDS |
| NFR, S-09 | No describe la política de artefactos fijados ni la caducidad temporal | B | Incompleto, no contradictorio. La gate lo hace cumplir y el reporte de Task/031 §53.4 lo documenta |
| `open-decisions.md`, fila D-10 | Enuncia el objetivo de 7 días sin la excepción 5 | B | El objetivo sigue siendo 7. La retención de 1 día es una excepción temporal documentada en STATUS y en el runbook §8 |

## 8. Gates y validaciones

Cifras de la última ejecución, sobre el entregable final.

| Gate | Resultado |
| --- | --- |
| Enlaces y anclas de los 9 documentos Markdown del entregable | **674** enlaces, **0** rotos |
| Enlaces y anclas de todo el repositorio | **181** documentos, **2377** enlaces, **0** rotos |
| `git diff --check` del árbol y del índice | **PASS** |
| Finales de línea | Los **12** archivos del entregable, en LF, sin BOM y con salto final |
| Solo comentarios fuera de Markdown | **0** líneas cambiadas fuera de comentarios en `.env.example`, `ci-infra.yml` y `variables.tf` |
| Gates offline de CI, con Terraform 1.16.7 y el provider 6.70.0 | **37/37** con exit 0 (desglose abajo) |
| Gitleaks 8.30.1 sobre el entregable exportado del índice | **433** archivos, sin hallazgos |
| ID de cuenta real | **0** apariciones |
| Cuenta de Grafana y `ExternalId` | **0** apariciones |
| Valores privados del tfvars de datos | Solo el ARN del bucket de medios: **1** aparición en el reporte de Task/030, preexistente en `main` y fuera de este diff, como ya registra el reporte de Task/031 §53.5 |
| Backend y frontend | En `main`, sin cambios |
| `terraform-datos/backend.generado.tf` | Intacto: mismo SHA-256 y sigue ignorado por Git |

**Desglose de las 37 gates**, con la invocación de `ci-infra.yml`:
- `terraform fmt -check` de `terraform/modulos`.
- En los seis roots: `fmt`, `init` con el lock en solo lectura, `validate` y `test`, sin cambios en los locks. Las
  pruebas de `terraform test` suman **82**, sin fallos:
  - 0 en `terraform`;
  - 7 en `terraform-medios`;
  - **54** en `terraform-datos`;
  - 5 en `bootstrap/terraform-state`;
  - 9 en `bootstrap/github-oidc`;
  - 7 en `bootstrap/operador-datos`.
- Las cinco suites de Python suman **1254** pruebas, todas OK:
  - `oidc`: 62, con 1 omitida porque comprueba permisos POSIX y solo corre en Linux;
  - `terraform_state`: 12;
  - `terraform_datos`: 725;
  - `laboratorio`: 335;
  - `security`: 120.
- Compose del laboratorio y Compose principal, con sus 7 servicios.
- Las 26 variables del Compose están declaradas en `.env.example`.
- Coherencia de identidades S-09: `RESULTADO: CORRECTO`.
- `git diff --check` del árbol y del índice.

Los escaneos que necesitan red o el historial completo, S-09 con Trivy y Gitleaks sobre todo el historial, los
ejecuta CI en el PR. GitHub es la fuente viva de su resultado.

## 9. Gobierno y Git

- **Rama:** creada desde `main` limpio y actualizado de infra, conforme a WORKFLOW §2.1, con la comprobación
  `HEAD = main`. Backend y frontend se verifican en solo lectura.
- **Fuera del versionado:** los detalles operacionales de Git se entregan en la sesión, conforme a §6.1.
- **Autorización:** el usuario la dio para iniciar esta tarea, crear commits y preparar un PR hacia `main` sin
  fusionarlo.
- **Pendiente de la aprobación expresa:** la integración en `dev` y el resto del cierre de PROJECT_INSTRUCTIONS §8.
- No hay ADR ni decisiones que promover.

## 10. Herencias para Task/032

Este mantenimiento no las cambia. Se recogen para el arranque de Task/032:

- **D-12:** presupuesto preliminar de 112 / 89 / 40 con `pool_size=1`, `overflow=1` y RC=20. Task/032 la cierra
  **con medición** ([decisiones §9.3](../architecture/production-postgresql-rds-decisions.md#93-task032--lambda-real)).
- **Cuota de concurrencia de Lambda:** 10 hasta el 2026-10-16 y **1000** observada el 2026-10-19. Con 1000 caben
  hasta 900 reservables, así que RC=20 es posible. Task/032 la confirmará con `get-account-settings`
  ([reporte de Task/031 §49](TASK-031-report.md#49-d-24-modificada-y-plan-de-h-031-5-2026-10-18)).
- **D-11 y D-19 siguen abiertas:**
  - alertamiento efectivo y calibración de `memoria` en Task/040;
  - comprobación del *trial* de Grafana en Task/041.
- **Portainer, aceptación temporal de CVE-2026-95837:** revisión el **2026-11-06** y vencimiento después del
  **2026-11-30**. Desde el día siguiente, la gate S-09 bloquea CI.
- **Retención temporal de backups de 1 día** mientras la cuenta siga en el plan FREE (excepción 5;
  [runbook §8](../runbooks/deployment-recovery.md#8-rds-productivo-con-retención-temporal-de-1-día-plan-free)).
- **Arranque de Task/032:** nace de `main` actualizado y limpio, después del cierre de este mantenimiento y de su
  normalización `main → dev`.
