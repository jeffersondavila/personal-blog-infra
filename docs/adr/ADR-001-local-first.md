# ADR-001 — Estrategia local-first

| Campo | Valor |
| --- | --- |
| **Estado** | Aceptada |
| **Fecha** | 2026-07-26 |
| **Tarea** | `Task/001-Inicializar-Workspace-y-Roadmap` |
| **Reemplaza a** | — |
| **Reemplazada por** | — |

---

## Contexto

Se va a construir un blog personal con sitio público, panel administrativo, base de
datos y almacenamiento de archivos, operado por una sola persona y con presupuesto
mínimo.

Dos caminos posibles:

1. **Cloud-first:** crear cuentas y recursos desde el inicio y desarrollar contra ellos.
2. **Local-first:** construir y validar todo en local, y desplegar solo cuando el
   producto esté demostrado.

El camino cloud-first implica pagar y administrar infraestructura durante todo el
desarrollo, cuando el producto todavía no existe y su alcance aún cambia.

## Decisión

**Todo debe funcionar primero localmente.**

1. **No se crearán cuentas cloud hasta validar el blog completo.**
   La primera interacción con AWS o Cloudflare ocurre en la Etapa 09, después de que la
   Etapa 07 (`Task/022-Validacion-Local-Production-Like`) haya demostrado el sistema
   completo funcionando en local.

2. **El desarrollo local se hace mediante Docker Compose.**
   Un único comando levanta frontend, backend, PostgreSQL, MinIO y reverse proxy. El
   entorno debe poder reconstruirse desde cero siguiendo un runbook escrito.

3. **Portainer CE se usa solo para supervisión local.**
   Sirve para inspeccionar contenedores, logs, healthchecks, volúmenes y redes durante
   el desarrollo y la validación. **No se despliega en producción.**

4. **La preparación para la nube ocurre sin cuentas.**
   La Etapa 08 produce el adaptador Lambda, el artefacto ZIP, los módulos de Terraform y
   los runbooks, todo validado en seco, con costo cero.

## Consecuencias

### Positivas

- Costo cero durante todo el desarrollo, que abarca 22 de las 41 tareas.
- Ciclo de iteración rápido: sin esperas de despliegue ni de propagación.
- Ningún riesgo de factura inesperada mientras el alcance todavía se mueve.
- El entorno reproducible obliga a documentar cómo se levanta el sistema.
- Si el proyecto se pausa, no hay nada consumiendo dinero.

### Negativas

- Las diferencias entre local y nube aparecen tarde, en la Etapa 08.
  *Mitigación:* están inventariadas desde ahora en
  [local-to-cloud-mapping.md](../architecture/local-to-cloud-mapping.md), sección
  *Diferencias que exigen atención explícita*.
- MinIO no es Amazon S3 y el reverse proxy no es API Gateway; hay comportamientos que
  solo se verifican en la nube.
  *Mitigación:* la interfaz `ObjectStorage` (`Task/010`) aísla la diferencia, y las
  tareas de la Etapa 08 la abordan explícitamente.
- Requiere recursos de la máquina local (CPU, memoria, disco) para varios contenedores.
- El primer despliegue real concentra riesgo por acumulación.
  *Mitigación:* runbooks con rollback definido (`Task/026`) y despliegue por incrementos
  a lo largo de siete tareas en la Etapa 10.

### Neutras

- El proyecto no será público hasta la Etapa 10. Es una consecuencia aceptada,
  no un problema: el blog se publica cuando tiene contenido y calidad para publicarse.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
| --- | --- |
| Cloud-first desde la Etapa 01 | Costo continuo durante meses sobre un producto inexistente, y riesgo de gasto no controlado antes de que existan presupuestos y alarmas. |
| Híbrido: base de datos administrada desde el inicio | Introduce costo fijo y dependencia de red en la fase de mayor iteración, sin beneficio real. |
| Desarrollo sin contenedores, directamente sobre la máquina | Entorno no reproducible; aleja el desarrollo de las condiciones de producción y complica la validación de la Etapa 07. |

## Cumplimiento

Esta decisión se verifica en:

- `Task/022-Validacion-Local-Production-Like` — puerta de control antes de la nube.
- El criterio "no se creó ningún recurso cloud" en la Definition of Done de todas las
  tareas anteriores a la Etapa 09.

## Referencias

- [ADR-002 — Tres repositorios](ADR-002-three-repositories.md)
- [ADR-003 — Nube serverless de bajo costo](ADR-003-serverless-low-cost-cloud.md)
- [Arquitectura — Visión general](../architecture/overview.md)
