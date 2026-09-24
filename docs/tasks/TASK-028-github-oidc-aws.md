# TASK-028 — GitHub OIDC AWS

| Campo | Valor |
| --- | --- |
| Identificador / rama de trabajo | `Task/028-GitHub-OIDC-AWS` |
| Etapa | ETAPA 09 — Cuentas y Seguridad Cloud |
| Estado | **En progreso** |
| Repositorio | **personal-blog-infra**, exclusivamente |
| Dependencias | Task/025, Task/026 y Task/027 aprobadas; cierre de Task/027 + Task/027.1 comunicado por el usuario |
| Rama base | **main**, nunca dev |
| SHA base verificado | `65fbf860a7ba47460eecad70431f0ba8f5bcfab1` |
| Autorización / aceptación del diseño | 2026-09-21 |
| Inicio de ejecución / última actualización | 2026-09-22 / 2026-09-24 |

## 0. Preparación Git

El 2026-09-22 se ejecutaron fetch, switch main y pull --ff-only según
[WORKFLOW §2.1](../project-management/WORKFLOW.md). Se verificaron árbol limpio,
ausencia de Task/028 local/remota y `main == origin/main` con el SHA de arriba.
Inmediatamente después de crear la rama desde main, `HEAD == main` coincidían.
Esta evidencia es histórica; Git es la fuente del estado vivo de ramas.

## 1. Objetivo

Demostrar federación real GitHub Actions → AWS STS sin access keys permanentes,
con un rol exclusivo de validación sin políticas de recursos. El checkpoint actual
entrega únicamente implementación y pruebas locales: **no acredita AWS real**.

## 2. Contexto

D-06 está **Resuelta y Vigente desde Task/025**. Su bucket aún no se ha
materializado. El diseño reconciliado de Task/028 está aceptado como diseño de
trabajo; no constituye aprobación de la tarea ni autorización de operaciones cloud.

## 3. Dentro del alcance

- [x] Root aislado `bootstrap/github-oidc/`, guardas y pruebas locales.
- [x] Workflow de verificación sin publicación ni ejecución en este checkpoint.
- [x] Runbook, reconciliación documental y evidencia local.
- [ ] Tras autorización independiente: inventario, bootstrap, federación real y
  dos publicaciones premerge autorizadas individualmente.
- [ ] Trust final exclusiva de main y reconfirmación postmerge desde main.

El 2026-09-24, con autorización acotada a **solo lectura AWS y plan**, se ejecutó
una parte del tercer punto: inventario real (caso A, ownership A), recuperación
cifrada verificada y plan revisado. Apply, federación real y publicaciones siguen
sin autorizar y sin ejecutar, de modo que el punto permanece abierto.

## 4. Fuera del alcance

Aplicación Terraform Task/025, recursos de aplicación, deploy, backend/frontend,
VPS, S3, DynamoDB, permisos de despliegue y branch protection. Task/030 materializa
D-06; Task/038 define permisos backend, Task/039 permisos Terraform y Task/040
valida integralmente. La protección de main debe preceder roles de despliegue efectivos.
Este checkpoint prohíbe AWS CLI autenticada, apply AWS, configuración GitHub,
variables, commit, push, PR, merge y dev; tampoco prepara publicaciones de prueba.

## 5. Entregables

| Entregable | Ruta en infra |
| --- | --- |
| Terraform independiente | `bootstrap/github-oidc/` |
| Guardas y verificación | `scripts/oidc/` y `tests/oidc/` |
| Workflow / expectativa versionada | `.github/workflows/verify-aws-oidc.yml`, `security/oidc-validation.json` |
| Procedimiento humano | [Runbook](../runbooks/github-oidc-bootstrap.md) |
| Evidencia del checkpoint | [Reporte](../task-reports/TASK-028-report.md) |

## 6. Criterios de aceptación

1. Provider A ausente: creación administrada; B compatible exacto: data source
   sin ownership; C discrepante o indeterminado: detener, sin modificar/importar.
2. Rol `PersonalBlogGitHubOidcValidation`, MaxSessionDuration 3600, sesiones 900,
   cero managed/inline policies. Nunca AdministratorAccess ni ReadOnlyAccess.
3. Trust temporal: subject inmutable exacto de Task/028, audience exacta,
   DateLessThan literal, futuro y máximo dos horas. Final: solo main sin caducidad.
4. Configuración, estado, planes y copias fuera de Git, custodia EX-028-C7.
5. Guardas rechazan destino/principal equivocados, adopción y planes inesperados.
6. Evidencia real pendiente: trust exacta, cero políticas, identidad correcta y
   operaciones negativas concretas con AccessDenied. Ninguna conclusión universal
   sobre todas las resource-based policies de la cuenta.
7. DoD general 1–12 y cloud C-1–C-11 evaluados en el reporte. C-7 **no PASS
   literal**: excepción EX-028-C7 aceptada como diseño, acotada al bootstrap.
8. La reconfirmación postmerge mediante `workflow_dispatch` desde `main` **solo puede
   ejecutarse después del merge humano**, de modo que **no es prerrequisito de
   `approved: Task/028-GitHub-OIDC-AWS`**. Es una validación **postmerge obligatoria**
   antes de dar por integrada Task/028 y antes de avanzar con normalidad a la tarea
   siguiente. Si esa validación falla, el avance se detiene y Task/028 se corrige.
   Ninguna aprobación se sustenta en pruebas mock ni se infiere de las ejecuciones
   premerge.

## 7. TDD / Plan test-first

No aplica el TDD de backend funcional: no se cambia backend. Sí se requieren
pruebas de infraestructura positivas/negativas para identidad, provider A/B/C,
ownership, rutas privadas, caducidad, trust, planes, workflow y saneamiento de errores.
Los mocks locales no cuentan como federación real ni como autorización efectiva AWS.

## 8. Plan de validación

Terraform fmt/init sin backend/validate y planes mock; unittest OIDC, seguridad y
laboratorio; actionlint/parser YAML; Gitleaks del worktree, enlaces, criterio 12,
conteos y diff. Cloud y ejecuciones GitHub quedan pendientes de autorización.

## 9. Comandos de validación

```text
terraform -chdir=bootstrap/github-oidc fmt -check
terraform -chdir=bootstrap/github-oidc init -backend=false -input=false -lockfile=readonly
terraform -chdir=bootstrap/github-oidc validate
terraform -chdir=bootstrap/github-oidc test
python -B -m unittest discover -s tests/oidc -v
python -B -m unittest discover -s tests/security -v
python -B -m unittest discover -s tests/laboratorio -v
git diff --check
```

## 10. Evidencia esperada

El reporte distingue gates locales, operaciones no ejecutadas y resultados reales
pendientes. No publicar JWT, credenciales STS, account ID real, correos privados ni
material de cifrado. No adjuntar estados, planes o logs crudos de AWS.

## 11. Riesgos

Pérdida/duplicación de estado local; proveedor compartido; trust mal acotada;
sesiones ya emitidas que siguen vivas; permisos por resource policy fuera del
inventario; main todavía sin protección; diferencias entre mocks y AWS.
Mitigaciones y propietarios: [runbook](../runbooks/github-oidc-bootstrap.md).

## 12. Decisiones técnicas

Diseño de trabajo aceptado, sin ADR nuevo ni aprobación de Task/028:

- Root IAM separado, sin recursos/políticas del grafo de aplicación.
- Human bootstrap mediante sesión MFA de `PersonalBlogAdministrator` en CloudShell;
  ese privilegio nunca se transmite al rol de CI. Cero access keys permanentes.
- Provider existente se referencia y nunca se importa. El propio creado por A
  conserva ownership verificable en el estado; no se reclasifica como compartido B.
- Trust Task caducable se sustituye entera por trust main, nunca se unen ambas.
- **EX-028-C7:** estado local privado fuera de Git solo para este bootstrap,
  directorios 0700/archivos 0600, un escritor, lock y backups cifrados externos con
  recuperación verificada. Revisión a 30 días de primera creación cloud; extinción
  obligatoria en Task/030 antes del primer apply de infraestructura de aplicación.
- Task/030 conserva módulos de aplicación Task/025 y recibe excepción explícita de
  ETAPA 10 para bootstrap S3 dedicado de D-06, sus protecciones y ambos estados.
- Dos publicaciones premerge futuras: Task SUCCESS con trust temporal; Task DENIED
  con trust final. Cada una requiere autorización propia; postmerge main SUCCESS.

## 13. Documentación creada o actualizada

Ficha, reporte y runbook; STATUS/ROADMAP; D-06, instrucciones, arquitectura,
límites/paridad y STAGE-08/09/10/11. Solo drift vigente; historia preservada.

## 14. Archivos modificados

Inventario completo y diff estadístico en el [reporte](../task-reports/TASK-028-report.md).
Solo infra. El código de aplicación y los otros dos repositorios quedan intactos.

## 15. Resultado de pruebas

Se registra la ejecución real local en el reporte. La evidencia de GitHub es
**pendiente**, no sustituida por pruebas sintéticas. El 2026-09-24 se incorporó la
evidencia AWS real de solo lectura y del plan revisado
([reporte §12](../task-reports/TASK-028-report.md)); la federación real sigue sin
demostrarse.

## 16. Problemas encontrados

Drift vigente de D-06 y contradicción de propiedad del backend reconciliados.
Las incidencias de implementación y gates se registran en el reporte.

## 17. Pasos de validación para el usuario

Revisar diff, ejecutar §9 con versiones fijadas y leer runbook/reporte. Ningún paso
cloud del runbook está autorizado por la implementación local. Las autorizaciones
futuras se limitan a operaciones concretas revisadas, sin pedir secretos al agente.

## 18. Deuda técnica pendiente

Federación real y cierre Task/028; materialización/migración D-06 en Task/030,
incluido estado del propio bucket; protección de main antes de despliegue;
permisos mínimos separados en Task/038 y Task/039; validación Task/040.

## 19. Próxima tarea

Task/029: PostgreSQL en VPS. No iniciada por este trabajo; requiere cierre de
Task/028 según WORKFLOW. Este checkpoint no cambia 27/41 ni ETAPA 09 1/3.

## 20. Aprobación

Pendiente, exclusivamente del usuario. Estado **En progreso**. La autorización
local del 2026-09-21 no autoriza cierre, publicaciones ni recursos externos. La
autorización del 2026-09-24 cubrió únicamente lectura AWS y plan: no autoriza
apply, publicaciones, cierre ni aprobación.
