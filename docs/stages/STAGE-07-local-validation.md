# ETAPA 07 — Validación Local

| Campo | Valor |
| --- | --- |
| **Número** | 07 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 06](STAGE-06-continuous-integration.md) |
| **Tareas** | 1 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | Blog validado íntegramente en local. Puerta de entrada a la nube. |

---

## Objetivo

Demostrar que el blog completo funciona, se reconstruye desde cero y conserva sus datos,
en condiciones equivalentes a producción — **antes** de crear ninguna cuenta cloud.

## Por qué esta etapa existe

Es la puerta de control de [ADR-001](../adr/ADR-001-local-first.md): no se gasta ni un
centavo ni se crea una sola cuenta hasta que el producto esté demostrado en local.

## Tareas

### `Task/022-Validacion-Local-Production-Like` — *Pendiente*

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

- [ ] El entorno se reconstruye desde cero sin intervención manual no documentada.
- [ ] Todas las migraciones aplican sobre base vacía.
- [ ] Es posible crear, editar, publicar y archivar cada tipo de contenido.
- [ ] Las imágenes subidas se sirven correctamente en el sitio público.
- [ ] Los datos y archivos sobreviven a un reinicio completo.
- [ ] Un backup se restaura con éxito y los datos coinciden.
- [ ] Todos los servicios aparecen sanos en Portainer.
- [ ] Se registra evidencia de cada punto anterior.

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
