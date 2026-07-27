# ADR-004 — Monolito modular con Clean Architecture pragmática

| Campo | Valor |
| --- | --- |
| **Estado** | **Aceptada** |
| **Fecha** | 2026-07-26 |
| **Fecha de aceptación** | 2026-07-26 |
| **Tarea** | `Task/002-Definir-MVP-y-Arquitectura` (**Aprobada**) |
| **Aprobada por** | jeffersondavila |
| **Reemplaza a** | — |
| **Reemplazada por** | — |

---

## Contexto

El backend debe cubrir nueve áreas de negocio (perfil, artículos, reviews, videos,
proyectos, etiquetas, medios, autenticación y auditoría), ejecutarse tanto como proceso
local en Docker como función AWS Lambda, y ser mantenido por **una sola persona** en su
tiempo disponible.

Las opciones razonables eran: microservicios, monolito por capas técnicas, monolito
modular, o una aplicación sin estructura definida.

Dos fuerzas empujan en direcciones contrarias:

- **A favor de estructura:** el proyecto durará años, con pausas largas; volver a un
  código sin límites claros después de meses es costoso.
- **En contra de estructura:** un solo desarrollador con un blog personal no puede pagar
  el peaje de una arquitectura ceremoniosa; el exceso de capas es tan dañino como su
  ausencia.

## Decisión

Se adopta un **monolito modular con Clean Architecture pragmática**.

### 1. Monolito

Un único backend desplegable. Un solo artefacto, una sola base de datos, un solo
despliegue.

### 2. Sin microservicios

Explícitamente descartados para este proyecto. Introducir uno requiere un ADR que
reemplace a este.

### 3. Separación por módulos de negocio

La división primaria es **por dominio, no por capa técnica**:

```
app/modules/{profile, posts, book_reviews, videos, projects, tags, media, authentication, audit}
app/shared/{database, storage, security, logging, pagination, errors, configuration}
```

No existe un paquete global `models/`, `services/` ni `repositories/`. Cada módulo es
dueño de su dominio completo.

### 4. Clean Architecture pragmática

Cada módulo **puede** contener `domain`, `application`, `infrastructure` y
`presentation`, con las dependencias apuntando hacia adentro:

```
presentation → application → domain ← infrastructure
```

**"Pragmática" significa que las capas se crean cuando resuelven un problema real.**
Un módulo simple como `tags` no necesita la misma ceremonia que `posts`. **Crear capas
vacías o abstracciones sin uso está explícitamente prohibido.**

### 5. Adaptadores en los bordes

Todo lo externo se consume tras una interfaz definida por el dominio:

| Externo | Adaptador |
| --- | --- |
| Base de datos | Repositorios: el dominio define la interfaz, la infraestructura la implementa. |
| Almacenamiento de objetos | `ObjectStorage`, con `MinIOStorage` y `S3Storage`. |
| Ejecución serverless | Adaptador Lambda como capa fina y removible (`Task/023`). |

**La lógica de negocio no conoce FastAPI, SQLAlchemy, MinIO, S3 ni Lambda.**

### 6. Restricciones adicionales

- Endpoints delgados: validar, invocar un caso de uso, serializar.
- Casos de uso explícitos, con nombre propio.
- Inyección de dependencias simple, la del framework.
- **No compartir modelos ORM directamente con la API.**
- Sin CQRS, sin event sourcing, sin bus de mensajes, sin patrones sin necesidad
  demostrada.

## Consecuencias

### Positivas

- **Coste operativo mínimo**: un despliegue, una base de datos, un conjunto de logs.
- **Sin latencia ni fallos de red entre módulos**: las llamadas son de proceso.
- **Transacciones simples**: una sola base de datos, sin consistencia eventual.
- **Encaja con Lambda**: un solo artefacto que empaquetar y desplegar.
- **Límites claros pese a ser un monolito**: la separación por módulos hace que el
  código siga siendo navegable tras meses de pausa.
- **Portabilidad real**: con el dominio aislado, cambiar MinIO por S3 o salir de Lambda
  afecta a adaptadores, no a reglas de negocio.
- **Verificable**: el dominio se prueba sin base de datos ni framework.

### Negativas

- **Riesgo de acoplamiento entre módulos.** Nada impide técnicamente que `posts` importe
  las entrañas de `media`.
  *Mitigación:* los módulos se comunican por interfaces públicas; las revisiones lo
  vigilan explícitamente.
- **Riesgo de sobreingeniería.** Clean Architecture invita a crear capas por reflejo.
  *Mitigación:* la regla "sin capas vacías" es normativa, no una sugerencia, y forma parte
  de la Definition of Done (M-06).
- **Riesgo opuesto: aplicación desigual.** Que cada módulo decida su profundidad puede
  producir incoherencia.
  *Mitigación:* `posts` se implementa primero (`Task/009`) y sirve de referencia para el
  resto.
- **Escalado en bloque.** No se puede escalar solo la parte cara.
  *Mitigación:* irrelevante en Lambda, que escala por invocación.
- **Un fallo grave afecta a todo el backend.** No hay aislamiento entre módulos.
  *Mitigación:* aceptable para un blog personal; el sitio público es de solo lectura y
  tolera degradación.
- **Indirección adicional** frente a escribir la lógica en el endpoint: más archivos por
  operación.
  *Mitigación:* el coste se paga una vez y se recupera en cada cambio posterior.

### Neutras

- La estructura de carpetas no se refleja en las rutas de la API: `/api/v1/posts` no
  implica nada sobre la organización interna del código.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
| --- | --- |
| **Microservicios** | Multiplicaría despliegues, bases de datos, observabilidad y costo por un problema que no tiene: no hay equipos independientes ni necesidad de escalar áreas por separado. Añadiría consistencia eventual y fallos de red donde hoy hay llamadas de función. Contradice además [ADR-003](ADR-003-serverless-low-cost-cloud.md). |
| **Monolito por capas técnicas** (`models/`, `services/`, `routers/`) | Es lo más común en proyectos FastAPI, pero dispersa cada funcionalidad entre carpetas distantes: tocar "artículos" obliga a abrir cinco directorios. Con nueve áreas de negocio, degenera rápido. |
| **Clean Architecture estricta** (las cuatro capas siempre, en todos los módulos) | Produciría decenas de archivos de una línea y mapeadores entre representaciones casi idénticas. Para un desarrollador único, el coste de ceremonia superaría el beneficio. |
| **Sin estructura definida** (lógica en los endpoints) | Es lo más rápido las primeras semanas y lo más caro después. Ataría la lógica de negocio a FastAPI, impidiendo probarla de forma aislada y complicando la portabilidad exigida por T-04. |

## Señales que justificarían reconsiderar esta decisión

Este ADR debería revisarse si aparece alguna de estas señales — y **solo** entonces:

1. **Más de un equipo o colaborador permanente** trabajando en áreas distintas, con
   conflictos frecuentes de integración.
2. **Un módulo con un perfil de recursos radicalmente distinto**: por ejemplo,
   procesamiento de imágenes o video que necesite mucha memoria o tiempo de ejecución y
   penalice al resto.
3. **Tráfico que obligue a escalar por área**, no de forma uniforme.
4. **Tiempo de despliegue o de pruebas inaceptable** por el tamaño del monolito.
5. **Un módulo que necesite otro lenguaje o *runtime***.
6. **Requisitos de aislamiento de fallos** que hoy no existen: que un área pueda caer sin
   afectar al resto.
7. **El artefacto de Lambda deja de caber** en los límites del servicio por su tamaño.

Señales que **no** justifican reconsiderarla: que el código crezca, que haya muchos
módulos, o que los microservicios estén de moda.

## Cumplimiento

- Ninguna tarea puede introducir un segundo servicio desplegable sin un ADR que reemplace
  a este.
- La regla "sin capas vacías" se verifica en la Definition of Done (M-06).
- `Task/005` establece la estructura base; `Task/009` fija el módulo de referencia.

## Referencias

- [software-architecture.md](../architecture/software-architecture.md)
- [ADR-003 — Nube serverless de bajo costo](ADR-003-serverless-low-cost-cloud.md)
- [non-functional-requirements.md](../architecture/non-functional-requirements.md)
