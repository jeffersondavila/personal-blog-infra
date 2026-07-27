# Guía de contribución — personal-blog-infra

Este repositorio es la **fuente de verdad** de la planificación del proyecto.
Cualquier cambio de alcance, etapa, tarea o decisión arquitectónica se registra aquí.

---

## 1. Alcance del repositorio

Se aceptan cambios en:

- Documentación de gestión (`docs/project-management/`).
- Fichas de etapa (`docs/stages/`).
- Fichas de tarea (`docs/tasks/`) y reportes (`docs/task-reports/`).
- Arquitectura y ADR (`docs/architecture/`, `docs/adr/`).
- Infraestructura local (`docker-compose`) — a partir de `Task/003`.
- Infraestructura cloud (Terraform) — a partir de `Task/025`.

**No** se acepta código de aplicación (React, FastAPI) en este repositorio.

---

## 2. Flujo de trabajo

El proceso completo está en
[`docs/project-management/WORKFLOW.md`](docs/project-management/WORKFLOW.md).
Resumen:

1. Selecciona una tarea `Pendiente` en `STATUS.md`.
2. Verifica sus dependencias en `ROADMAP.md`.
3. Crea la rama `Task/<numero>-<nombre>` **desde `dev`**.
4. Marca la tarea `En progreso` en `STATUS.md`.
5. Implementa **solo** el alcance de la tarea.
6. Ejecuta las validaciones declaradas.
7. Crea la ficha en `docs/tasks/` y el reporte en `docs/task-reports/`.
8. Marca la tarea `Lista para validación`.
9. Espera la validación del usuario.

La aprobación es **exclusiva del usuario** mediante:

```
approved: Task/<nombre-de-rama>
```

---

## 3. Estrategia de ramas

| Rama | Propósito |
| --- | --- |
| `main` | Versión estable o liberable. No recibe merge automático. |
| `dev` | Integración de tareas aprobadas. |
| `Task/<numero>-<nombre>` | Trabajo aislado de una tarea, creado desde `dev`. |

Cuando una tarea afecta a varios repositorios, se usa **el mismo nombre de rama Task**
en todos los repositorios afectados.

---

## 4. Convención de commits

```
<tipo>(<ámbito>): <descripción en imperativo>

Task/<numero>-<nombre>
```

Tipos: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `build`.

Ejemplo:

```
docs(project-management): registrar roadmap inicial y backlog de 41 tareas

Task/001-Inicializar-Workspace-y-Roadmap
```

---

## 5. Reglas de seguridad

- **Nunca** se versionan secretos, credenciales, tokens, claves privadas ni `.env` reales.
- Los valores sensibles se documentan como **nombres de variable**, nunca como valores.
- En la nube, la configuración vive en **AWS SSM Parameter Store**.
- Todo archivo de ejemplo debe llamarse `*.example` y contener valores ficticios.

---

## 6. Estilo de documentación

- Idioma: **español**.
- Formato: Markdown, líneas orientadas a ~100 caracteres.
- Enlaces entre documentos: **rutas relativas**.
- Fechas: formato `AAAA-MM-DD`.
- Estados de tarea: solo los seis oficiales
  (`Pendiente`, `En progreso`, `Lista para validación`, `Aprobada`, `Bloqueada`, `Descartada`).
- Evitar duplicar contenido: el roadmap vive **solo** en este repositorio; los demás
  repositorios lo referencian.

---

## 7. Antes de marcar una tarea como lista

Revisa [`docs/project-management/DEFINITION_OF_DONE.md`](docs/project-management/DEFINITION_OF_DONE.md).
