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

- `main`: versión estable y revisada por el usuario.
- `dev`: integración de tareas aprobadas.
- `Task/<numero>-<nombre>`: trabajo aislado de una tarea.

Toda rama Task debe crearse desde `dev` actualizado.

No crear una rama Task en un repositorio que no será modificado.

Cuando una tarea afecta varios repositorios, utilizar el mismo nombre de rama
Task en todos los repositorios afectados.


## 4. Preparación de una tarea

Antes de crear una nueva rama Task, en cada repositorio afectado:

1. Ejecutar `git fetch --prune origin`.
2. Cambiar a `main`.
3. Ejecutar `git pull --ff-only origin main`.
4. Cambiar a `dev`.
5. Ejecutar `git pull --ff-only origin dev`.
6. Verificar si `main` contiene commits que `dev` no contiene.
7. Si los contiene, integrar `main` dentro de `dev`.
8. Publicar la sincronización de `dev`.
9. Crear la rama Task desde `dev`.
10. Confirmar la rama activa y el estado del árbol.

No comenzar una tarea desde `main`.


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


## 14. Restricciones del proyecto

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

Consultar siempre los ADR y documentos vigentes antes de cambiar estas
decisiones.

Una modificación a una decisión arquitectónica aceptada requiere:

1. Registrar la necesidad.
2. Crear o reemplazar un ADR.
3. Dejarlo como propuesta.
4. Esperar aprobación explícita del usuario.


## 15. Orden de autoridad

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
