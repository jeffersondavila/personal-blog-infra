# Task/031 — Documento de traspaso (2026-10-21)

Estado: **Aprobada el 2026-10-21** mediante `approved: Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`, con la
aceptación expresa de las excepciones 5, 6 y 8 ([reporte §52](TASK-031-report.md#52-aprobación-y-cierre-2026-10-21)).
Este documento es el traspaso **previo** a la aprobación y se conserva como historia: se escribió con la tarea
en **CIERRE TÉCNICO COMPLETADO — Lista para validación**.

Fuente de verdad: el [reporte de Task/031](TASK-031-report.md), sobre todo la
[§51](TASK-031-report.md#51-h-031-6-aplicada-y-verificada-y-h-031-7-completa-2026-10-20-y-2026-10-21). También
la [ficha](../tasks/TASK-031-deploy-network-rds-ssm-cloudwatch.md). No contiene secretos, cuentas, hosts ni
identificadores de recursos.

## 1. Objetivo y alcance

Desplegar la capa de datos productiva de ETAPA 10: red privada, PostgreSQL en RDS privado (ADR-010), credenciales en
SSM SecureString, observabilidad de CloudWatch (D-11) y lectura de Grafana (D-20). Además:
- la ejecutora privada de administración de D-24;
- la prueba real de recuperación, con PITR sintético.

Todo con Terraform como fuente de verdad, en el root `terraform-datos`, con el backend S3 y lock nativo de D-06.

**Fuera de alcance:** Lambda de la aplicación (`Task/032`), migraciones (`Task/036`), automatización del canal
(`Task/038`) y la validación de carga, seguridad y recuperación final (`Task/040`).

## 2. Arquitectura desplegada

39 recursos gestionados en `terraform-datos` (us-east-2):

| Módulo | Recursos |
| --- | --- |
| `red` (16) | VPC; 2 subredes privadas y sus tablas de rutas; *gateway endpoint* de S3; `sg-admin`, `sg-lambda` y `sg-rds` con reglas por referencia; sin IGW, NAT ni EIGW |
| `base_de_datos` (5) | RDS PostgreSQL 17.11, `db.t4g.micro`, gp3 de 20 GiB, Single-AZ, privada, cifrada con `aws/rds`, protegida contra borrado y con backups de **1 día**; *parameter group* `postgres17` con `rds.force_ssl = 1`; *subnet group*; grupo de logs; SecureString de la master |
| `credenciales_sql` (2) | SecureString de `blog_migrate` y `blog_app` (`value_wo`, `alias/aws/ssm`, v1) |
| `ejecutor_privado` (4) | Lambda `blog-prod-ejecutor` con el código h0316 en `sg-admin`, sin concurrencia reservada (D-24 modificada); su rol, su política `-ejecucion` y logs de 14 días |
| `exportacion` (2) | Política `-exportacion` (`s3:PutObject` condicional en `exportaciones/*`) y la regla `sg-admin` → S3:443 |
| `alarmas_rds` (8) | Alarmas de D-11, sin acciones |
| `lectura_grafana` (2) | Rol `PersonalBlogLecturaGrafana` de D-20 y su política de solo lectura |

En PostgreSQL:
- los roles `blog_migrate` (5 conexiones) y `blog_app` (89), con los privilegios de D-23;
- el esquema `verificacion` y la tabla `verificacion.marcador`, que está vacía.

## 3. Historias y criterios

| Historia | Estado |
| --- | --- |
| H-031-1 y H-031-1A | Completadas, sin conexión |
| H-031-IAM | Completa por decisión del usuario: identidad `PersonalBlogAdministrator` (§24) |
| H-031-2 | Su plan quedó superado por H-031-3; la casilla de la ficha sigue sin marcar por historia |
| H-031-3 | Completa: red y RDS desplegadas y convergentes |
| H-031-5 | Desplegada y convergente el 2026-10-19 |
| **H-031-6** | **Aplicada, convergente y SQL conforme el 2026-10-20** |
| **H-031-7** | **Completa el 2026-10-21**: PITR real con integridad, RPO 180 s y RTO 774 s, sin residuos |
| H-031-8 y H-031-9 | Aplicadas y convergentes el 2026-10-15 |

Los criterios de aceptación 1 a 4, 7, 9 y 10 de la ficha tienen evidencia completa en el reporte; la matriz final está en §51.16. Tres **no se cumplen
tal como se redactaron**: tienen una **desviación documentada** respecto del requisito original (§48.8 y §51.16 del
reporte) y solo se cierran con la aceptación expresa del usuario, **concedida el 2026-10-21**:
- el 5: backups de 1 día, porque el plan FREE no admite 7;
- el 6: la identidad operativa es `PersonalBlogAdministrator` (§24);
- el 8: las alarmas no tienen acciones y falta calibrar `memoria`; de D-19 queda la comprobación al terminar el trial.

## 4. Evidencias

**H-031-6** (§51.3 a §51.5):
- **Terraform:** apply exacto del plan `8d1a7307…7a6d` (4 creaciones, 1 actualización en sitio y 0 destrucciones);
  refresh-only `H0316_REFRESH_OK`; `ACTIONABLE_CONVERGENCE_OK` 0/0/0 sobre 39 recursos.
- **Readback:** SSM, con el valor custodiado igual al generado en memoria; IAM; reglas; la función con el pin h0316.
- **SQL:**
  - `identidades`, con la relectura exacta del contrato desplegado;
  - `verify` con TLSv1.3 `verify-full` y controles negativos;
  - DDL rechazado a `blog_app`;
  - `export` con manifiesto `d24-export-v1`, validado **sin tablas de aplicación**.
- **Secretos:** la master y las dos credenciales, ausentes de todos los archivos.

**H-031-7** (§51.8 a §51.10):
- **PITR real:** la temporal llegó a `available` y la integridad dio `true`.
- **Tiempos:** RPO 180 s (objetivo 900) y RTO 774 s (objetivo 14 400).
- **Limpieza:** un único `RestoreDBInstanceToPointInTime` y un único `DeleteDBInstance` en CloudTrail; cero residuos;
  marcador retirado y confirmado ausente; productiva idéntica a su línea base.
- **Costo:** entre 0.0041 y 0.0046 USD.

**Evidencia privada**, local y sin versionar:
- `%LOCALAPPDATA%/PersonalBlog/application/data/`: planes, JSON, manifiesto `h0317-manifiesto.json` y copias de sus
  checkpoints, progreso SQL con su historial, logs e informes `h0317-informe-final.json`;
- `tmp/h0320/`: runners, pruebas sin conexión y `evidencia/`.

## 5. Excepciones y decisiones del usuario

- **Plan AWS FREE:**
  - retención de backups de 1 día, no de 7;
  - el restore sintético sí se admite;
  - CloudTrail no registra los rechazos `FreeTierRestrictionError`, así que su prueba es la respuesta síncrona.
- **Identidad operativa:** `PersonalBlogAdministrator` (§24).
- **D-24 modificada** (aprobada el 2026-10-19): sin concurrencia reservada; escrituras administrativas con
  `pg_try_advisory_xact_lock(3364, 1)`; invocaciones sin reintentos.
- **§40:** semántica de la deriva móvil, aprobada el 2026-10-19.
- **Alarmas sin acciones, sin alertamiento efectivo:** desde el 2026-10-21, `Task/040` asume bajo D-11 los canales de notificación aprobados, la conexión de las alarmas y la prueba de recepción, además de la calibración de `memoria`. D-11 sigue abierta hasta verificarlos.
- **D-19:** queda la comprobación al terminar el trial de Grafana.
- **R-12:** abierto, con seguimiento en `Task/040`.
- **Cuota de Lambda:** la solicitud de 1001 sigue abierta y no es necesaria.
- **Validador SQL:** `rds_force_ssl` llega nulo en una sesión de RDS. Se acepta solo con tres pruebas: la API, el
  rechazo del servidor sin TLS y `verify-full` (autorización del 2026-10-20).
- **Correcciones del orquestador**, con TDD: el rechazo 4xx definitivo y el 404 `DBInstanceAutomatedBackupNotFound`
  contado como cero.
- **Exportación:** validada sin tablas de aplicación; los datos reales y su retención quedan para `Task/036` y
  `Task/040`.

## 6. Estado final de AWS y Terraform (2026-10-21, 02:28Z)

- **State `terraform-datos`:** serial 18, 39/39, sin taints ni lock; SHA-256 `8abda37e…4196`. Última convergencia:
  0/0/0. Desde entonces no se ha ejecutado ningún apply.
- **RDS productiva:** `available`, privada, protegida, sin cambios pendientes e idéntica a su línea base.
- **Ninguna instancia temporal, backup, *snapshot* ni grupo de logs** de H-031-7. Ningún recurso fuera de Terraform,
  salvo los objetos de datos esperados:
  - la exportación en `exportaciones/20261020T051414Z/`;
  - los roles y el esquema de PostgreSQL.
- **Secretos:** solo en SSM SecureString. Ninguno en archivos, logs, plan ni state.

## 7. Git: archivos y pendientes

- **Ramas:** `personal-blog-infra` en `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`, sin commits.
  `personal-blog-backend` y `personal-blog-frontend`, limpios en `main`: la tarea no los toca.
- **Cambios en infra:** 163 archivos, 28 modificados y 135 nuevos (inventario por áreas en la §51.15 del reporte).
  - **Terraform:** `terraform-datos/`, 7 módulos en `terraform/modulos/`, `bootstrap/operador-datos/`.
  - **Scripts:** `scripts/terraform_datos/` (guardas, empaquetado, operador, orquestador del restore),
    `scripts/laboratorio/`.
  - **Pruebas:** `tests/terraform_datos/`, `tests/laboratorio/`.
  - **CI:** `.github/workflows/ci-infra.yml`, `.gitignore`.
  - **Documentación:** reporte, ficha, este traspaso, arquitectura, *runbooks*, STATUS, ROADMAP y STAGE-10.
- **Ignorados y privados, correctamente:** `tmp/`, `terraform-datos/errored.tfstate`, `.terraform/`,
  `backend.generado.tf`, `generado/`.
- **Resuelto el 2026-10-21** (§51.15 del reporte): `terraform/modulos/ejecutor_privado/codigo_h0316/rds-ca-us-east-2.pem`
  estaba ignorado por la regla `*.pem`.
  - Es la CA **pública** de RDS: 3 certificados y ninguna clave privada.
  - Es una de las 4 fuentes del ZIP fijado, y `tests/terraform_datos/test_empaquetar_ejecutor_h0316.py` la necesita.
  - Sin ella, un checkout limpio no reconstruye el artefacto y esa prueba falla en el CI.
  - Se añadió la excepción exacta `!terraform/modulos/ejecutor_privado/codigo_h0316/rds-ca-us-east-2.pem`, sin
    tocar `*.pem`. El empaquetado desde un checkout limpio reproduce el pin `98f41bfd…8e43`.

## 8. Comandos de verificación útiles

Desde `personal-blog-infra`, en Git Bash, con `PYTHONUTF8=1`. Ninguno modifica AWS.

```bash
python -B -m unittest discover -s tests/terraform_datos -v      # 723 pruebas
python -B tmp/h0320/gates-h0316-final/gates.py                  # 32 gates sin conexión (privado)
python -B tmp/h0320/enlaces.py docs/task-reports/TASK-031-report.md   # enlaces y anclas (privado)
aws sts get-caller-identity --profile personal-blog --region us-east-2
python -B tmp/h0320/cierre_h0317.py                             # cierre de H-031-7, solo lectura (privado)
```

## 9. Pendientes verdaderos

1. ~~La revisión del usuario y la aceptación de las desviaciones de §5~~: concedidas el 2026-10-21.
2. ~~La decisión sobre el `.pem` de §7~~: resuelta el 2026-10-21.
3. Con `approved`, el flujo de cierre de `docs/claude/PROJECT_INSTRUCTIONS.md` §8, iniciado el 2026-10-21
   ([reporte §52](TASK-031-report.md#52-aprobación-y-cierre-2026-10-21)):
   - commits, integración en `dev` con `--no-ff` y publicación;
   - la rama Task en `origin` y el PR `Task/031 → main`, que no se fusiona;
   - volver a `main` y borrar la rama local con `-d`.
4. Seguimiento fuera de esta tarea (§51.16 del reporte):
   - el alertamiento efectivo de RDS, la calibración de `memoria` y R-12, en `Task/040`; D-11 sigue abierta;
   - D-19, en `Task/041`;
   - la exportación con datos reales, en `Task/036` y `Task/040`;
   - la retención de 7 días, al pasar al plan PAID.

   La supervisión manual de los backups (B3) sigue vigente.

**No hay ninguna operación de AWS pendiente**, ni ningún recurso temporal ni costo en curso.

## 10. Instrucciones para la nueva sesión

- **No repetir** ningún apply, refresh-only, plan productivo, SQL, `export`, PITR ni limpieza. H-031-1 a H-031-9 están
  cerradas. Cualquier operación productiva nueva necesita una autorización explícita.
- Empezar por verificar en solo lectura:
  - `git status`;
  - que esta rama sigue siendo `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`;
  - la regresión de `tests/terraform_datos`.
- Si hace falta AWS, la sesión de `aws login` caduca con la sesión de rol de la consola (1 h):
  - cambiar de rol **después** de que caduque la anterior y dejar `aws login` como último paso;
  - comprobar la sesión correlacionando la clave en uso con `sessionContext.attributes.creationDate`;
  - mantener los 35 min de margen.
- Esperar el `approved` literal del usuario antes de cualquier commit.
