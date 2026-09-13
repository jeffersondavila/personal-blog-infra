# ETAPA 07 — Validación Local

| Campo | Valor |
| --- | --- |
| **Número** | 07 |
| **Estado** | **Completada** el **2026-09-12**, con la aprobación de `Task/022` |
| **Dependencias** | [ETAPA 06](STAGE-06-continuous-integration.md) |
| **Tareas** | 1 |
| **Aprobadas** | 1 |
| **Avance** | **100 %** |
| **Hito que completa** | Blog validado íntegramente en local. Puerta de entrada a la nube. **Alcanzado** el 2026-09-12 |

---

## Objetivo

Demostrar que el blog completo funciona, se reconstruye desde cero y conserva sus datos,
en condiciones equivalentes a producción — **antes** de crear ninguna cuenta cloud.

## Por qué esta etapa existe

Es la puerta de control de [ADR-001](../adr/ADR-001-local-first.md): no se gasta ni un
centavo ni se crea una sola cuenta hasta que el producto esté demostrado en local.

## Tareas

### `Task/022-Validacion-Local-Production-Like` — **Aprobada** el 2026-09-12

[Ficha](../tasks/TASK-022-local-production-like-validation.md) ·
[Reporte](../task-reports/TASK-022-report.md).

- Reconstrucción completa del entorno desde cero.
- Aplicación de migraciones.
- Carga de datos semilla.
- Recorrido completo del flujo administrativo.
- Publicación de contenido real de prueba.
- Verificación de persistencia tras reinicio.
- Ejecución y restauración de un backup.
- Revisión del estado de todos los servicios en Portainer.

**Depende de:** `Task/019`, `Task/020`, `Task/021`.
**Repositorios:** los tres.

## Criterios de salida de la etapa

**Los ocho quedaron cumplidos**, y con la aprobación del usuario del **2026-09-12** la
etapa queda **Completada**.
Evidencia completa en [TASK-022-report](../task-reports/TASK-022-report.md) §2.

- [x] El entorno se reconstruye desde cero sin intervención manual no documentada
      — **tras corregir siete defectos del runbook que solo una reconstrucción real
      podía destapar** (reporte §5).
- [x] Todas las migraciones aplican sobre base vacía — `0003`, 17 tablas, partiendo de
      0 tablas y sin `alembic_version`.
- [x] Es posible crear, editar, publicar y archivar cada tipo de contenido — los cuatro
      verbos sobre `Post`, `BookReview`, `Video` y `Project`, por HTTP real.
- [x] Las imágenes subidas se sirven correctamente en el sitio público — enlace firmado
      `200` con los **mismos 4836 bytes** y su `alt_text`.
- [x] Los datos y archivos sobreviven a un reinicio completo — estado idéntico tras
      `down` + `up` sin tocar volúmenes.
- [x] Un backup se restaura con éxito y los datos coinciden — conteos iguales y **huella
      `md5` idéntica fila a fila**; además, recuperación total con el entorno **operativo**.
- [x] Todos los servicios aparecen sanos en Portainer — **confirmado por el usuario** el
      2026-09-12. `migrations` no cuenta: es del perfil `admin` y se ejecuta con
      `run --rm`.
- [x] Se registra evidencia de cada punto anterior — reporte de la tarea.

**Requisito no funcional cerrado:** **T-07**. Ningún otro.

## Fuera del alcance de la etapa

- Cualquier acción en proveedores cloud.
- Adaptación a Lambda (Etapa 08).
- Terraform (Etapa 08).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Pasos manuales no documentados que impiden reproducir el entorno. | Reconstrucción desde cero siguiendo únicamente el runbook escrito. |
| Backup que nunca se probó restaurar. | La restauración es criterio obligatorio de salida. |
| Diferencias sutiles entre local y la futura nube. | Se abordan explícitamente en la Etapa 08. |

## Siguiente etapa

[ETAPA 08 — Preparación Cloud sin Cuentas](STAGE-08-cloud-ready.md)
