# Arquitectura — Visión general

**Última actualización:** 2026-07-26
**Estado:** propuesta inicial. Se cierra formalmente en `Task/002-Definir-MVP-y-Arquitectura`.

---

## 1. Qué es este sistema

Un blog personal con sitio público y panel administrativo propio, construido con
estrategia **local-first**: todo funciona y se valida en local antes de existir en la
nube ([ADR-001](../adr/ADR-001-local-first.md)).

Secciones previstas del blog:

| Sección | Contenido |
| --- | --- |
| Inicio | Presentación y contenido destacado. |
| Quién soy | Perfil personal y profesional. |
| Artículos | Publicaciones técnicas y personales. |
| Reviews de libros | Reseñas con valoración. |
| Videos y explicaciones | Contenido audiovisual referenciado. |
| Proyectos y laboratorio | Trabajos y experimentos. |
| Contacto y enlaces | Formas de contacto y redes. |
| Panel administrativo | Gestión de todo el contenido anterior. |

---

## 2. Componentes

| Componente | Responsabilidad |
| --- | --- |
| **Frontend** | Sitio público y panel administrativo. React + TypeScript + Vite. |
| **Backend** | API pública y administrativa, dominio, autenticación. FastAPI. |
| **Base de datos** | Persistencia relacional del contenido. PostgreSQL. |
| **Almacenamiento de objetos** | Imágenes y archivos. MinIO en local, S3 en la nube. |
| **Entrada HTTP** | Enrutado y TLS. Reverse proxy en local, API Gateway en la nube. |
| **Supervisión** | Portainer CE en local. CloudWatch en la nube. |

---

## 3. Arquitectura local

```
                    ┌──────────────────────────┐
   navegador  ────► │   Reverse proxy local    │
                    └───────────┬──────────────┘
                                │
                  ┌─────────────┴─────────────┐
                  ▼                           ▼
        ┌──────────────────┐        ┌──────────────────┐
        │ Frontend         │        │ Backend          │
        │ React + Vite     │        │ FastAPI          │
        └──────────────────┘        └────────┬─────────┘
                                             │
                              ┌──────────────┴──────────────┐
                              ▼                             ▼
                    ┌──────────────────┐         ┌──────────────────┐
                    │ PostgreSQL       │         │ MinIO (S3 API)   │
                    └──────────────────┘         └──────────────────┘

        Todo orquestado con Docker Compose y supervisado con Portainer CE.
```

Portainer **no forma parte del camino de la petición**: es solo un panel de supervisión
de Docker (contenedores, logs, healthchecks, volúmenes, redes).

---

## 4. Arquitectura cloud objetivo

```
                    ┌──────────────────────────┐
   navegador  ────► │    Cloudflare (DNS)      │
                    └──────┬─────────────┬─────┘
                           │             │
                           ▼             ▼
              ┌──────────────────┐   ┌──────────────────────┐
              │ Cloudflare Pages │   │ API Gateway HTTP API │
              │ (React estático) │   └──────────┬───────────┘
              └──────────────────┘              │
                                                ▼
                                     ┌──────────────────────┐
                                     │ AWS Lambda (FastAPI) │
                                     └──────────┬───────────┘
                                                │
                   ┌────────────────┬───────────┴────┬────────────────┐
                   ▼                ▼                ▼                ▼
          ┌────────────────┐ ┌────────────┐ ┌───────────────┐ ┌──────────────┐
          │ PostgreSQL     │ │ Amazon S3  │ │ SSM Parameter │ │ CloudWatch   │
          │ administrado   │ │            │ │ Store         │ │ (limitado)   │
          └────────────────┘ └────────────┘ └───────────────┘ └──────────────┘
```

Justificación de estas elecciones:
[ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md).

---

## 5. Principios de diseño

1. **Local-first.** Nada se despliega antes de estar validado en local.
2. **Paridad local–nube por interfaz, no por servicio.** El código habla con
   abstracciones (`ObjectStorage`), no con MinIO ni con S3 directamente.
3. **Costo como restricción de diseño.** Sin servicios de costo fijo mensual.
4. **Configuración fuera del código.** `.env` en local, SSM Parameter Store en la nube.
5. **Sin credenciales permanentes.** GitHub Actions accede a AWS mediante OIDC.
6. **Contenido primero.** El modelo de datos y la API pública se diseñan para el
   contenido que el blog realmente publicará.
7. **Reproducibilidad.** El entorno completo se reconstruye desde cero siguiendo un
   runbook escrito.

---

## 6. Límites entre repositorios

| Repositorio | Contiene | No contiene |
| --- | --- | --- |
| `personal-blog-frontend` | UI pública y panel, cliente HTTP, estilos, tests de UI. | Lógica de dominio, acceso a base de datos, secretos. |
| `personal-blog-backend` | API, dominio, persistencia, migraciones, autenticación. | UI, Terraform, definición del entorno. |
| `personal-blog-infra` | Planificación, Docker Compose, Terraform, runbooks, ADR. | Código de aplicación. |

Razones y costos de esta separación:
[ADR-002](../adr/ADR-002-three-repositories.md).

---

## 7. Correspondencia local → nube

Ver [local-to-cloud-mapping.md](local-to-cloud-mapping.md).

---

## 8. Qué falta decidir

Se resuelve en `Task/002-Definir-MVP-y-Arquitectura` y en tareas posteriores:

- Alcance exacto del MVP por sección.
- Contratos concretos de la API pública y administrativa.
- Mecanismo de autenticación (sesión con cookie o token).
- Modelo conceptual detallado del dominio.
- Proveedor de PostgreSQL administrado (`Task/029`).
- Backend de estado de Terraform (`Task/025`).
