# Instrucciones del proyecto — Blog Personal

## 1. Alcance del workspace

El workspace está ubicado en:

`C:\Users\jeffe\Downloads\Blog_Personal`

Contiene tres repositorios independientes:

- `personal-blog-backend`
- `personal-blog-frontend`
- `personal-blog-infra`

`personal-blog-infra` es la fuente de verdad para:

- Roadmap.
- Estado del proyecto.
- Workflow.
- Definition of Done.
- ADR.
- Arquitectura.
- Alcance del MVP.
- Reportes y fichas de tareas.

Antes de trabajar, consultar según corresponda:

- `docs/project-management/STATUS.md`
- `docs/project-management/ROADMAP.md`
- `docs/project-management/WORKFLOW.md`
- `docs/project-management/DEFINITION_OF_DONE.md`
- La ficha de la tarea activa.
- Los ADR relacionados.
- Los documentos de producto y arquitectura relacionados.

No asumir que el estado descrito en una conversación anterior continúa
vigente. Verificar siempre Git y la documentación local.


## 2. Reglas generales

- Trabajar únicamente dentro del workspace indicado.
- Ejecutar una sola tarea a la vez.
- No iniciar la tarea siguiente sin cerrar la actual.
- No modificar repositorios fuera del alcance de la tarea.
- No agregar secretos, tokens, contraseñas ni credenciales.
- No crear recursos cloud sin autorización explícita.
- No hacer operaciones destructivas.
- No usar `git reset --hard`, `git clean -fd`, `git push --force` ni
  `git branch -D` sin autorización explícita.
- No reemplazar trabajo del usuario sin revisarlo.
- Verificar siempre la rama activa antes de editar.
- Mantener los árboles de trabajo limpios al terminar un cierre aprobado.
- Los prompts, reportes y explicaciones para el usuario se redactan en español.


## 3. Ramas

Ramas permanentes:

- `main`: versión estable y revisada por el usuario. **Única base permitida de
  las ramas Task.**
- `dev`: **solo integración** de tareas aprobadas y normalización posterior al
  PR. **Nunca base de una Task.**
- `Task/<numero>-<nombre>`: trabajo aislado de una tarea. **Nace de `main`.**

### INVARIANTE CRÍTICO

**Toda rama `Task/<...>` se crea SIEMPRE desde `main` actualizado y limpio.**

**`dev` NUNCA es la rama base de una Task.** `dev` es exclusivamente rama de
integración.

No crear una rama Task en un repositorio que no será modificado.

Cuando una tarea afecta varios repositorios, utilizar el mismo nombre de rama
Task en todos los repositorios afectados, **y todas nacen de `main`**.


## 4. Preparación de una tarea

Antes de crear una nueva rama Task, en cada repositorio afectado:

```powershell
git fetch --prune origin
git switch main
git pull --ff-only origin main
```

Validar **antes** de crear la rama:

```powershell
git status --porcelain      # debe estar vacio
git rev-parse main
git rev-parse origin/main   # deben coincidir
```

Solo entonces:

```powershell
git switch -c Task/<nombre>
```

Validación **obligatoria e inmediata** después de crearla:

```powershell
git rev-parse HEAD
git rev-parse main          # deben coincidir
```

Si `HEAD` no coincide con `main`, la rama está mal creada: detenerse y
reportarlo.

### Prohibido

```powershell
git switch dev
git switch -c Task/<nombre>     # PROHIBIDO
```

Y cualquier flujo equivalente que use `dev` —o una rama derivada de `dev`—
como base de una Task.

**Motivo:** `dev` contiene commits de integración que no deben formar parte de
la ascendencia de una tarea nueva. Si una Task nace de `dev`, el pull request
`Task → main` puede heredar historial exclusivo de integración. Detalle
completo en
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1.

> **Nota histórica.** Hasta el 2026-08-15 esta sección indicaba `dev` como base
> y añadía «No comenzar una tarea desde `main`», lo que era **incorrecto**. La
> regla quedó corregida en `Task/005.4-Corregir-Base-Ramas-Task-Main`. El
> historial de las tareas anteriores **no se reescribe**.


## 5. Estados de una tarea

Estados permitidos:

- Pendiente.
- En progreso.
- Lista para validación.
- Aprobada.
- Bloqueada.
- Descartada.

Claude puede cambiar una tarea a:

- En progreso.
- Lista para validación.
- Bloqueada.

Claude nunca puede cambiar una tarea a Aprobada por decisión propia.

La tarea solamente está aprobada cuando el usuario escribe exactamente:

`approved: Task/<nombre-de-rama>`


## 6. Antes de la aprobación

Mientras la tarea esté En progreso o Lista para validación:

- No hacer merge hacia `dev`.
- No hacer push de la rama Task, salvo autorización explícita.
- No crear pull request.
- No modificar `main`.
- No marcar ADR o decisiones como aceptadas.
- No iniciar la siguiente tarea.
- Dejar un reporte completo para validación.
- Por defecto, dejar los cambios sin commit, salvo que el prompt de la tarea
  autorice commits locales.

Las decisiones producidas por una tarea no aprobada deben estar marcadas como:

`Propuesta — pendiente de aprobación`


## 7. Significado de approved

Cuando el usuario escriba:

`approved: Task/<nombre-de-rama>`

queda autorizado el flujo completo de cierre descrito a continuación.

Antes de ejecutar, confirmar:

- Que la rama indicada existe.
- Que es la rama activa o contiene los cambios correctos.
- Que las validaciones de la tarea finalizaron correctamente.
- Que no hay cambios ajenos mezclados.
- Qué repositorios fueron modificados.


## 8. Flujo obligatorio de cierre aprobado

En cada repositorio afectado:

1. Registrar documentalmente la aprobación.
2. Promover ADR y decisiones de Propuesta a Aceptada o Vigente.
3. Actualizar STATUS, ROADMAP, ficha, reporte y avance cuando corresponda.
4. Ejecutar las validaciones finales.
5. Crear uno o más commits si existen cambios pendientes.
6. Cambiar a `dev`.
7. Actualizar `dev` con `pull --ff-only`.
8. Integrar la rama Task dentro de `dev` mediante merge `--no-ff`.
9. Publicar `dev`.
10. Publicar la rama Task en origin.
11. Crear un pull request con:

    - Base: `main`
    - Head: la rama `Task/<nombre>`
    - Nunca usar `dev` como head del pull request.

12. Confirmar expresamente que el PR es:

    `Task/<nombre> → main`

13. No aceptar ni fusionar el pull request.
14. Volver a `main`.
15. Ejecutar `fetch --prune` y `pull --ff-only`.
16. Eliminar la rama Task local mediante:

    `git branch -d Task/<nombre>`

17. No usar `git branch -D`.
18. No eliminar la rama Task remota.
19. No iniciar la siguiente tarea.
20. Presentar el reporte de cierre y la URL del PR.

Regla crítica:

**No crear PR `dev → main`.**

El pull request de cada tarea aprobada debe ser:

**`Task/<nombre> → main`.**

La integración en `dev` y el PR hacia `main` son operaciones separadas.


## 9. Responsabilidad exclusiva del usuario

Solo el usuario puede:

- Revisar el pull request hacia `main`.
- Aceptar o rechazar el pull request.
- Fusionar el pull request.
- Decidir eliminar la rama remota desde GitHub.
- Autorizar cambios destructivos.
- Autorizar recursos cloud.
- Aprobar una tarea.

Claude nunca debe hacer merge automático hacia `main`.


## 10. Después de que el usuario acepta el PR

Cuando el usuario confirme que fusionó el PR, haya decidido o no eliminar la
rama Task remota:

En cada repositorio afectado:

1. Ejecutar `git fetch --prune origin`.
2. Cambiar a `main`.
3. Ejecutar `git pull --ff-only origin main`.
4. Cambiar a `dev`.
5. Ejecutar `git pull --ff-only origin dev`.
6. Verificar los commits de `main` ausentes en `dev`.
7. Integrar `main` dentro de `dev`, preferiblemente mediante merge `--no-ff`
   cuando exista un commit de merge propio del PR.
8. Publicar `dev`.
9. Volver a `main`.
10. Ejecutar `fetch --prune`.
11. Confirmar que:
    - La rama Task local no existe.
    - El estado de la rama Task remota coincide con la decisión del usuario.
    - `main` y `dev` tienen el mismo contenido.
    - Los árboles de trabajo están limpios.

Esta sincronización evita que `main` y `dev` conserven commits de merge
divergentes.

No crear la siguiente rama Task hasta completar esta normalización.


## 11. GitHub CLI

Los repositorios utilizan HTTPS.

GitHub CLI está instalado en:

`C:\Program Files\GitHub CLI\gh.exe`

En shells donde `gh` no aparezca en PATH, ejecutar primero:

```powershell
$env:PATH = "$env:PATH;C:\Program Files\GitHub CLI"
gh auth status
```

`gh` está configurado como proveedor de credenciales de Git para
`https://github.com`, por lo que las operaciones remotas de Git funcionan sin
solicitar credenciales.

Cuenta activa: `jeffersondavila`. Protocolo Git: HTTPS.

Para crear un pull request, usar `--body-file` con un archivo temporal en lugar
de pasar el cuerpo en línea: evita problemas de escape en PowerShell.

```powershell
gh pr create --repo jeffersondavila/<repositorio> `
  --base main --head Task/<nombre> `
  --title "Task/<numero> - <Nombre>" `
  --body-file <ruta-al-archivo>
```

No usar `gh pr merge`: aceptar el pull request es responsabilidad exclusiva del
usuario (sección 9).


## 12. Validaciones de Git

Antes y después de una operación de cierre, registrar:

- `git status`
- `git branch -vv`
- `git branch -r`
- `git log --oneline --decorate --graph --all`
- Diferencias entre Task, dev y main.
- Archivos creados, modificados y eliminados.
- Resultado de pruebas, lint y validaciones aplicables.
- Búsqueda de secretos.

Antes de crear un pull request, comprobar:

- Que la rama Task existe en origin.
- Que el pull request no existe previamente.
- Que la base sea `main`.
- Que el head sea exactamente la rama Task.
- Que el árbol de trabajo esté limpio.
- Que todas las validaciones aplicables hayan terminado correctamente.

Si una operación falla:

- Detener el flujo.
- No intentar ocultar el error.
- No avanzar al paso siguiente.
- Explicar el estado exacto.
- Proponer una recuperación no destructiva.
- No repetir automáticamente una operación potencialmente destructiva.


## 13. Reglas por repositorio

### personal-blog-infra

Contiene:

- Documentación central.
- Docker Compose local.
- Terraform.
- Runbooks.
- ADR.
- Estado y roadmap.
- Instrucciones versionadas para Claude Code.

No contiene:

- Código React.
- Código FastAPI.
- Lógica de negocio de la aplicación.

### personal-blog-backend

Contiene:

- FastAPI.
- Dominio.
- Casos de uso.
- Persistencia.
- Migraciones.
- Autenticación.
- Auditoría.
- Adaptadores de almacenamiento.

No contiene:

- Interfaz de usuario.
- Componentes React.
- Terraform.
- Administración de Docker local.

### personal-blog-frontend

Contiene:

- Sitio público.
- Panel administrativo.
- React.
- TypeScript.
- Componentes y estilos.
- Cliente HTTP.
- SEO del frontend.

No contiene:

- Lógica de negocio definitiva.
- Persistencia.
- Migraciones.
- Terraform.
- Secretos.

Una tarea solo debe crear una rama Task en los repositorios que realmente
modificará.


## 14. BACKEND TEST-FIRST LAW

Regla obligatoria para **todo comportamiento funcional nuevo** de
`personal-blog-backend`. Aplica de forma estricta desde `Task/008`.

Fuente completa y única:
[`docs/project-management/BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md).
Leerla **antes** de escribir código de dominio, casos de uso, API, persistencia,
autenticación, auditoría o almacenamiento.

Reglas mínimas que ninguna sesión puede saltarse:

- **Matriz de comportamiento antes de implementar.** Casos, precondiciones,
  resultado esperado y capa. Sin matriz no se programa la funcionalidad.
- **RED demostrado.** El test se escribe primero, se ejecuta y **falla por la
  razón esperada**. La evidencia se conserva en el reporte de la tarea.
- **GREEN demostrado.** Implementación mínima suficiente, sin comportamiento
  futuro no solicitado.
- **REFACTOR.** Ejecutado sin cambiar el comportamiento observable, o declarado
  innecesario con su razón.
- **Regresión completa.** La suite afectada y la suite entera vuelven a
  ejecutarse antes de cerrar la tarea.
- **Los tests no se cambian para acomodar código incorrecto.** Solo pueden
  modificarse si el requisito cambió, si contradicen la documentación vigente,
  si contienen un error demostrado o si una decisión documentada redefinió el
  comportamiento. Ante una contradicción entre requisito, arquitectura y test:
  **detenerse y documentarla**, nunca reescribir la expectativa en silencio.
- **Sin bug fix sin test de regresión.** Primero se reproduce el defecto con un
  test que falla; ese test se queda en la suite.
- **La cobertura es una señal, no la especificación.** No se aceptan pruebas sin
  *asserts* útiles ni exclusiones injustificadas.

Excepciones razonables —documentación, `Dockerfile`, configuración sin lógica,
*wiring* trivial, cambios mecánicos, migraciones estructurales— están definidas
en la estrategia, §4. **Una excepción a TDD no es una excepción a validar.**


## 15. AWS LOCAL PARITY LAW

Regla de infraestructura. Aplica desde la ETAPA 08 (`Task/023`–`Task/026`) y a toda
tarea que escriba Terraform o toque el laboratorio AWS local.

Fuente completa y única:
[`docs/architecture/aws-local-parity.md`](../architecture/aws-local-parity.md).
Decisión: [`ADR-006`](../adr/ADR-006-local-aws-parity-with-floci.md) —
**Aceptada** el 2026-08-15 (`Task/005.2`). Vigente y de cumplimiento obligatorio.

- **Terraform es la fuente de verdad** de la infraestructura cloud.
- **Floci es el destino local; AWS real es el destino definitivo y la autoridad
  final.** Lo observado en Floci es hipótesis hasta validarse en AWS.
- **No duplicar módulos local/cloud.** Una sola definición, un solo grafo de
  recursos. Nada de recursos Terraform específicos de Floci.
- **No acoplar la aplicación a Floci.** Backend y herramientas usan AWS SDK /
  boto3, AWS CLI y el provider oficial `hashicorp/aws`.
- **Las diferencias van a la matriz de paridad**, nunca a una bifurcación del
  diseño. **Nunca declarar «paridad completa».**
- **Nunca usar credenciales AWS reales contra Floci**, ni secretos reales en su
  SSM emulado: no cifra.
- **Versión de Floci fijada.** Nunca `latest` ni `nightly`.
- **Guardas fail-closed** antes de cualquier `apply` o `destroy` local: un
  comando pensado para Floci no puede acabar hablando con AWS real.
- **Floci es infraestructura local privilegiada** (socket de Docker): solo
  local, nunca expuesto, mismo tratamiento que Portainer.
- **AWS real sigue siendo la validación final.** El laboratorio no sustituye a
  la ETAPA 10.

No decide **D-06** (backend de estado de Terraform, `Task/025`): sigue abierta.
**D-01** quedó **resuelta** por `Task/005.3` en cuanto al **modelo** (sección
16); el **proveedor** sigue en `Task/029`.


## 16. PRODUCTION DATABASE LAW

Regla de la capa de datos de producción. **Vigente** desde el 2026-08-15
(`Task/005.3`).

Fuente completa y única:
[`docs/architecture/production-postgresql-vps.md`](../architecture/production-postgresql-vps.md).
Decisión: [`ADR-007`](../adr/ADR-007-production-postgresql-on-vps.md) —
**Aceptada**. Vigente y de cumplimiento obligatorio.

1. **PostgreSQL productivo vive en un VPS externo**, autogestionado. **No RDS.**
2. **FastAPI permanece en AWS Lambda.** API Gateway, IAM, S3, SSM y CloudWatch
   permanecen en AWS.
3. **PostgreSQL nunca se expone directamente a Internet.**
4. **PgBouncer es el punto de entrada** de la capa de datos: el único
   endpoint de esa capa alcanzable desde fuera del VPS. El SSH
   administrativo es un canal separado, ajeno a la capa de datos.
5. **`Lambda → PgBouncer` exige TLS** con validación del certificado del
   servidor. **SCRAM-SHA-256** es el mecanismo de autenticación preferente;
   **mTLS** es opcional y todavía no obligatorio.
6. **El código de aplicación solo depende de `DATABASE_URL`.** No conoce
   proveedor, IP, Docker, Floci ni PgBouncer.
7. **Proveedor, región y tamaño se deciden en `Task/029`**, con precios
   actuales — nunca con cifras heredadas.
8. **Los backups deben salir del VPS.** Una copia que solo vive en el host no
   protege de perder el host.
9. **El restore debe probarse.** Un backup no está validado hasta haberse
   restaurado.
10. **No introducir NAT Gateway ni VPC** únicamente por PostgreSQL sin una
    decisión explícita basada en un requisito real.
11. **AWS y Floci no simulan la base de datos productiva.** `Task/025` no debe
    crear recursos RDS.
12. **PostgreSQL local sigue siendo el destino normal de desarrollo.**

No resuelve **D-06**, ni el proveedor concreto, ni los tamaños de pool, ni
`max_connections`, ni la frecuencia de backups: todo eso es de `Task/029`.


## 17. Restricciones del proyecto

Arquitectura acordada y vigente:

- Monolito modular.
- Clean Architecture pragmática.
- React + TypeScript + Vite.
- FastAPI.
- PostgreSQL.
- MinIO en local.
- Amazon S3 en producción mediante `ObjectStorage`.
- Docker Compose únicamente para el entorno local.
- Portainer únicamente local.
- Cloudflare Pages para el frontend.
- API Gateway HTTP API y AWS Lambda para el backend.
- Terraform para infraestructura cloud.
- GitHub Actions para automatización.
- Sin microservicios.
- Sin Portainer en producción.
- Sin EC2, ECS, EKS, ECR, ALB ni NAT Gateway en la arquitectura inicial.
- Local-first antes de crear recursos cloud.
- Floci como laboratorio AWS **local** para validar la IaC (sección 15).
  **Vigente** desde 2026-08-15 (ADR-006). No es un servicio de producción ni
  altera la arquitectura cloud objetivo.
- PostgreSQL de producción **autogestionado en un VPS externo**, con PgBouncer
  delante (sección 16). **Vigente** desde 2026-08-15 (ADR-007). **RDS no es el
  destino de producción.**

Consultar siempre los ADR y documentos vigentes antes de cambiar estas
decisiones.

Una modificación a una decisión arquitectónica aceptada requiere:

1. Registrar la necesidad.
2. Crear o reemplazar un ADR.
3. Dejarlo como propuesta.
4. Esperar aprobación explícita del usuario.


## 18. Orden de autoridad

Cuando exista conflicto entre:

- Una conversación anterior.
- Una suposición del agente.
- La documentación versionada.
- CLAUDE.md.
- El estado real de Git.
- Una instrucción actual del usuario.

Usar este orden de autoridad:

1. Instrucción explícita actual del usuario.
2. Estado real de Git, GitHub y el sistema local.
3. Documentación vigente versionada.
4. CLAUDE.md y sus documentos importados.
5. Conversaciones y reportes históricos.
6. Suposiciones del agente.

Nunca inventar:

- El estado de una rama.
- La existencia de un commit.
- El resultado de un push.
- La existencia o dirección de un pull request.
- La aprobación de una tarea.
- La aceptación de un ADR.
- La creación de un recurso cloud.

Cuando el estado no pueda comprobarse, detenerse y declararlo como no
verificado.
