# BACKEND TESTING STRATEGY — Práctica test-first del backend

Fuente de verdad **única y completa** de cómo se prueba `personal-blog-backend`.

[`PROJECT_INSTRUCTIONS.md`](../claude/PROJECT_INSTRUCTIONS.md),
[`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md), [`TASK_TEMPLATE.md`](TASK_TEMPLATE.md),
[`ROADMAP.md`](ROADMAP.md) y la [ETAPA 03](../stages/STAGE-03-domain-and-backend.md)
**referencian** este documento en lugar de repetirlo. Si algo de aquí entra en conflicto con
otro documento, **manda este** en materia de pruebas del backend.

- **Estado:** Vigente
- **Creado por:** `Task/005.1-Formalizar-TDD-Backend` (mantenimiento)
- **Aplica desde:** `Task/008-Modelo-de-Datos`

---

## 1. Por qué existe

`Task/005` dejó el backend con estructura, configuración, logging, errores y acceso a datos,
pero **sin una sola regla de negocio**. A partir de `Task/008` empieza el dominio real: es el
momento exacto de fijar cómo se prueba, antes de que exista código sobre el que sea caro
cambiar de práctica.

Las pruebas de este proyecto no son un trámite de cobertura. Cumplen cinco funciones:

| Función | Qué significa |
| --- | --- |
| **Especificación ejecutable** | El test dice qué debe hacer el sistema, antes que el código. |
| **Red de regresión** | Un comportamiento acordado no puede romperse en silencio. |
| **Contrato de comportamiento** | Define qué es observable y qué es detalle interno. |
| **Límite para los agentes** | Un agente de programación no puede redefinir el comportamiento acordado por su cuenta. |
| **Documentación técnica del dominio** | El nombre del test explica la regla de negocio. |

---

## 2. La regla central

> **Test-first law.** Todo comportamiento funcional **nuevo** del backend empieza por una
> prueba que **falla**. El ciclo obligatorio es **RED → GREEN → REFACTOR**.

No se acepta escribir la implementación primero y las pruebas después para alcanzar un
porcentaje. Una suite escrita a posteriori documenta lo que el código **hace**; una suite
escrita antes documenta lo que el código **debe hacer**. Solo la segunda detecta que la
implementación está equivocada.

---

## 3. Dónde es obligatorio

TDD es **obligatorio** para comportamiento nuevo en:

| Área | Incluye |
| --- | --- |
| **Dominio** | Invariantes, entidades, *value objects*, transiciones de estado, validaciones de negocio. |
| **Reglas de contenido** | Publicación, borrador, archivado y sus transiciones. |
| **Aplicación** | Casos de uso, servicios de aplicación, orquestación, decisiones de permisos. |
| **API pública** | Contratos HTTP, búsquedas, paginación, filtros, exposición exclusiva de contenido publicado. |
| **API administrativa** | CRUD, publicación, gestión de medios. |
| **Persistencia** | Repositorios, consultas, constraints, transacciones. |
| **Seguridad** | Autenticación, autorización, auditoría, reglas verificables de seguridad. |
| **Almacenamiento** | Interfaz `ObjectStorage` y sus implementaciones (MinIO, S3-compatible). |
| **Errores funcionales** | Códigos, modelo común de error, ausencia de filtraciones. |

Aplica de forma especialmente estricta a **`Task/008` … `Task/012`**, que construyen el
backend funcional real.

---

## 4. Excepciones razonables

TDD estricto **no** se impone artificialmente a:

- Documentación y archivos declarativos.
- `Dockerfile`, Compose, Terraform.
- *Wiring* trivial y configuración sin lógica.
- Cambios puramente mecánicos (renombrados, formato, movimientos de archivos).
- Scripts triviales.
- Migraciones estructurales, donde la prueba correcta es una **validación de integración**
  (`upgrade`, `downgrade`, reaplicación contra PostgreSQL real) y no un test unitario.

> **Una excepción a TDD no es una excepción a validar.** Todo cambio sigue necesitando la
> verificación apropiada a su naturaleza, y esa verificación se registra en el reporte de la
> tarea.

---

## 5. Ciclo obligatorio por comportamiento

### 5.1 ESPECIFICAR — antes de tocar la implementación

1. Leer el criterio de aceptación de la ficha.
2. Identificar el **comportamiento observable** (no la implementación).
3. Construir la **matriz de casos** (§6).
4. Identificar las **invariantes** que nunca pueden romperse.
5. Identificar el **happy path**.
6. Identificar los **edge cases**.
7. Identificar los **errores** esperados y su contrato.
8. Identificar las **condiciones de seguridad**.
9. Decidir **qué capa** debe demostrar cada comportamiento (§7 y §8).

### 5.2 RED

1. Escribir **primero** el test.
2. Ejecutarlo.
3. Confirmar que **falla**.
4. Confirmar que falla **por la razón esperada** — no por un `ImportError`, un *typo* ni una
   fixture ausente.

> **Evidencia obligatoria.** El reporte de la tarea conserva la salida de RED: el nombre del
> test y el motivo del fallo.

> **Señal de alarma.** Un test que **ya pasa** antes de implementar no demuestra el ciclo: o
> el comportamiento ya existía, o el test no comprueba lo que dice comprobar. Debe
> investigarse y explicarse antes de continuar.

### 5.3 GREEN

1. Implementar la **mínima solución suficiente**.
2. No añadir comportamiento futuro que nadie ha pedido.
3. Ejecutar el test.
4. Confirmar GREEN.

### 5.4 REFACTOR

1. Mejorar el diseño.
2. Eliminar duplicación.
3. Mejorar nombres.
4. Mantener los límites arquitectónicos de [ADR-004](../adr/ADR-004-modular-monolith.md).
5. **No cambiar el comportamiento observable.**

Después del refactor se ejecutan **de nuevo** todas las pruebas afectadas, más la suite
completa antes de cerrar la tarea.

Si el refactor no hace falta, se declara explícitamente: *"refactor no necesario, el diseño
resultante ya es el mínimo razonable"*.

---

## 6. Matriz de comportamiento

Toda funcionalidad no trivial **empieza** por su matriz. No se programa la funcionalidad
hasta que la matriz tiene cobertura suficiente.

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| Happy path | … | … | … | dominio |
| Edge | … | … | … | aplicación |
| Error | … | … | … | HTTP |
| Seguridad | … | … | … | integración |

La matriz vive en la **ficha de la tarea**, en la sección *TDD / Plan test-first*
([`TASK_TEMPLATE.md`](TASK_TEMPLATE.md) §7).

---

## 7. Pirámide de pruebas

```
                 pocas
            E2E / HTTP
          integracion real
      casos de uso / aplicacion
     dominio e invariantes
                 muchas
```

**No se fijan proporciones numéricas**: un porcentaje inventado empuja a escribir pruebas
para cuadrar una estadística. La intención es:

- **Muchas** pruebas de dominio, rápidas y sin infraestructura.
- **Suficientes** pruebas de aplicación sobre la orquestación.
- **Integración real** donde la tecnología concreta importa.
- **Pocas** pruebas E2E, caras y lentas, reservadas a los recorridos críticos.

---

## 8. Tipos de prueba del backend

### 8.1 Unitarias / dominio

**Para:** reglas puras, invariantes, *value objects*, transiciones de estado, validaciones.

**Deben:** ser rápidas, no necesitar base de datos, no depender de FastAPI y no depender de
Docker. Si una prueba de dominio necesita alguna de esas tres cosas, el diseño está
filtrando infraestructura hacia el dominio.

### 8.2 Casos de uso

**Para:** orquestación, uso de repositorios abstractos, decisiones de aplicación y permisos
funcionales.

Mocks o *fakes* **solo en límites claros** (repositorio, almacenamiento, reloj).

### 8.3 PostgreSQL real

Se usa **PostgreSQL real** cuando el comportamiento depende de: SQL, constraints, índices,
transacciones, consultas, o de la semántica específica de PostgreSQL.

> **Prohibido sustituir PostgreSQL por SQLite para aparentar integración.** Una prueba contra
> otro motor no demuestra el comportamiento del motor que se usa en producción; demuestra el
> de SQLite.

El entorno local ya provee ese PostgreSQL
([runbook](../runbooks/local-environment.md)).

#### 8.3.1 Base de datos de pruebas aislada — obligatorio

> **Vigente desde `Task/005.6`.** Las reglas de este bloque no son recomendaciones: son
> condiciones para que la integración pueda ejecutarse.

Las pruebas de integración son **destructivas**: el ciclo de migraciones ejecuta
`alembic downgrade base`, que revierte el esquema entero.

| Regla | Detalle |
| --- | --- |
| **Base dedicada** | La integración se ejecuta contra una base **exclusiva de pruebas** (`personal_blog_test`), nunca contra `personal_blog`, la base cotidiana de desarrollo. |
| **Nunca migraciones destructivas sobre la base de desarrollo** | Antes de `Task/008` esa base solo tenía `alembic_version`; a partir de `Task/008` tendrá el contenido real del blog. Un `downgrade base` sobre ella **destruye datos**. |
| **La guarda es *fail-closed*** | No comprueba que el destino sea peligroso: exige **demostrar** que es seguro. Si no puede demostrarlo, **falla**. |
| **La guarda no confía en la URL** | Además del sufijo `_test` en el nombre, la base debe llevar la marca `personal-blog:test-database` en su **comentario de PostgreSQL**. La marca vive **dentro** de la base: escribir bien una URL no la fabrica, y apuntar por error a la base de desarrollo no la encuentra. |
| **Artefactos de prueba fuera de las migraciones** | Las tablas auxiliares que una prueba necesite se crean y se destruyen en su *fixture*, con el `DROP` en un `finally`. Nunca entran en las migraciones de negocio. |

Provisionar la base: [runbook del entorno local](../runbooks/local-environment.md) §9.

#### 8.3.2 Skip y fail: la distinción es obligatoria

Solo hay dos casos, y confundirlos convierte la integración en decorativa:

| Caso | Situación | Resultado exigido |
| --- | --- | --- |
| **1** | `PERSONAL_BLOG_TEST_DATABASE_URL` **no definida** | `SKIP`, con motivo explícito. No hay entorno de integración que ejecutar. |
| **2** | La variable **está definida** | PostgreSQL **debe funcionar**. Credenciales incorrectas, host caído, driver ausente, conexión fallida o una regresión del motor son **`FAIL`**. |

> **Prohibido degradar un fallo a `skip`.** Un `except Exception: pytest.skip(...)` alrededor
> de la conexión hace que la suite quede verde exactamente cuando el acceso a datos está
> roto, que es el único momento en que esa prueba tenía algo que decir. Solo la **ausencia
> declarada** del entorno justifica omitir.

#### 8.3.3 Commit y rollback: verificación semántica

Comprobar que `session.commit()` o `session.rollback()` **fueron llamados** no demuestra
nada: son las dos afirmaciones que un `session_scope` roto sigue satisfaciendo.

| Comportamiento | Cómo se demuestra |
| --- | --- |
| **Commit** | El dato se escribe dentro del `session_scope` y se lee después desde **otra sesión independiente**. Debe estar. |
| **Rollback** | El dato se escribe, se comprueba que **es visible dentro** de la transacción, se provoca el error, y después se lee desde **otra sesión**. No debe estar. |

La comprobación intermedia del rollback es obligatoria: sin ella, un `INSERT` que nunca
llegara a ejecutarse produciría el mismo resultado final y la prueba pasaría sin haber
probado nada.

#### 8.3.4 Pruebas de migraciones que no caducan

Una prueba de migraciones **no puede afirmar el estado del esquema de un momento concreto
del roadmap**. La aserción `tablas <= {"alembic_version"}` —«el proyecto no tiene tablas de
negocio»— era cierta antes de `Task/008` y se habría puesto roja al aparecer la primera
tabla legítima del blog.

El contrato durable de **M-04** es: `upgrade head` → `downgrade base` → `upgrade head`
funciona, y el esquema tras `upgrade` + `downgrade` es **idéntico** al de antes. Eso detecta
el defecto real —una migración que crea un objeto y olvida soltarlo en su `downgrade`— y
sigue siendo válido con cualquier número de tablas. La revisión `head` se lee del directorio
de scripts, nunca se fija en el código de la prueba.

#### 8.3.5 Aislamiento del `.env` del desarrollador — desde la *collection*

> **Ampliado en `Task/005.7`** (`CERT-AUD-001`). Hasta entonces esta sección describía dos
> mecanismos que solo cubrían el **cuerpo** de las pruebas.

Las pruebas **no leen** el `.env` de la máquina, y la garantía empieza en la **collection**,
no en la primera *fixture*.

| # | Mecanismo | Qué cubre |
| --- | --- | --- |
| **1** | El paquete `tests` neutraliza el dotenv para **todo el proceso** (`env_file=None` en `model_config`) y limpia el entorno antes de que pytest coleccione nada. | *Collection*, imports, `get_settings()`, ruta de integración. |
| **2** | Una *fixture* `autouse` deja el entorno de cada prueba en el mismo estado controlado. | Aislamiento entre pruebas. |
| **3** | La *factory* de configuración construye con `_env_file=None`. | Configuración explícita de cada prueba. |

**Por qué el mecanismo 1 es imprescindible y no lo sustituye ningún `autouse`.** Las
*fixtures* se ejecutan **después** de la *collection*. `app/main.py` construye la instancia
ASGI **al importarse** —arranque fail-fast, requisito T-01—, así que cualquier import de ese
módulo durante la *collection* resuelve la configuración con el `.env` que haya en el
directorio de trabajo. Se reprodujo: un `.env` intruso cambiaba `app_name`, `log_level` y
`app_debug` del proceso de pruebas. Ninguna *fixture* llega a tiempo de impedirlo.

Reglas vigentes:

- **El harness no importa `app.main` durante la *collection*.** Ese import vive dentro de la
  *fixture* que construye la aplicación. Es una segunda capa independiente del mecanismo 1:
  perder una en una refactorización no reabre el defecto.
- **La regresión se ejecuta en un subproceso limpio**, desde un directorio de trabajo propio
  con un `.env` intruso. Es la única forma de observar la *collection* desde fuera y de no
  depender del `.env` real ni del *cwd* habitual del repositorio.
- **Toda prueba de aislamiento lleva su guarda anti-tautología**: se demuestra que el `.env`
  intruso **sí** es legible sin el aislamiento. Sin eso, un archivo colocado en una ruta
  equivocada haría pasar la prueba sin probar nada.
- **La ruta de integración también es hermética.** Las *fixtures* que dejan el proceso
  apuntando a la base real fijan la URL de destino y nada más: el resto de campos `BLOG_*` no
  se heredan de ningún archivo.
- **No se cambia el comportamiento de producción para que pasen las pruebas.** La aplicación
  real sigue leyendo su `.env`; lo que se aísla es el **harness**.

**Alcance de la garantía:** el harness oficial. No se afirma que ningún código Python
imaginable pueda leer un `.env`; se afirma que **arrancar y ejecutar esta suite no lo hace**.

#### 8.3.6 El harness de integración es *fail-closed* por construcción

> **Vigente desde `Task/005.7`** (`CERT-AUD-002`).

**Garantía exacta, y es la única que puede afirmarse:**

> Ninguna *fixture* del harness oficial de integración entrega `Settings`, `Engine`,
> `Session`, conexión o `Config` de Alembic apuntando al destino de integración **antes** de
> haber verificado que ese destino es seguro.

**Lo que NO se afirma** —sería falso y la documentación no debe prometer más protección de la
que existe—: que resulte imposible que código Python arbitrario abra una conexión a otra base.
`create_engine` está al alcance de quien lo escriba. La protección es del **harness**, que es
donde una prueba futura se equivocaría por accidente.

Reglas de diseño que hacen cumplible esa garantía:

| Regla | Motivo |
| --- | --- |
| **Un único resolutor del destino** | Una sola *fixture* convierte `PERSONAL_BLOG_TEST_DATABASE_URL` en configuración y motor, y **verifica antes de hacer `yield`**. Todo lo demás se deriva de ella. |
| **No coexisten una ruta segura y otra insegura** | Que `database_engine` verificara no bastaba mientras `database_settings` entregara la configuración sin verificar: el harness ofrecía dos caminos y confiaba en que nadie tomara el malo. Se reprodujo ejecutando DDL contra una base `_test` **sin marca**. |
| **Las dos barreras se comprueban antes de exponer nada** | Sufijo `_test` en el nombre **y** marca `personal-blog:test-database` dentro de la base. Si algo no puede demostrarse, **`FAIL`**. |
| **`personal_blog` no es alcanzable como destino destructivo** | Su nombre no termina en `_test` y no lleva la marca: el rechazo ocurre **antes** de cualquier DDL, `downgrade` o migración. |
| **La estructura se comprueba, no se confía** | Una prueba recorre el grafo de *fixtures* y exige que **todas** dependan del resolutor verificado. No necesita PostgreSQL levantado, así que se ejecuta siempre. |
| **Los módulos del harness se descubren, no se enumeran** | El conjunto inspeccionado se obtiene **del directorio** `tests/integration/`, no de una lista escrita a mano. Una lista manual falla **abierta**: quien añade un módulo nuevo y no se acuerda de registrarlo pierde la protección en silencio — justo la convención humana que esta regla existe para eliminar. Con descubrimiento, un módulo entra en la comprobación por el hecho de existir. |
| **El descubrimiento tiene su propia guarda** | Se exige que encuentre los módulos y las *fixtures* ya conocidos. Sin eso, un descubrimiento roto dejaría el conjunto vacío y la comprobación pasaría **sin haber inspeccionado nada**. |

#### 8.3.7 Concurrencia — pendiente, con propietario

**La suite de integración NO es segura para ejecución concurrente sobre la misma base**
(`CERT-AUD-009`, riesgo **R-37**): nombre de tabla auxiliar fijo, `downgrade base` sobre
esquema compartido y mutación de entorno y cachés de proceso.

Hoy **no hay ejecución paralela oficial** —`pytest-xdist` no está instalado— así que el
riesgo no es explotable. **Propietario: `Task/020-CI-Backend`.** Debe resolverse **antes** de
habilitar cualquier paralelismo; habilitarlo es lo que activa el riesgo.

---

Las pruebas de integración se **omiten con motivo explícito** cuando no hay entorno de
integración definido (caso 1), nunca se declaran superadas sin ejecutarse.

### 8.4 HTTP / FastAPI

**Valida:** códigos HTTP, contrato JSON, modelo común de error, paginación, filtros,
autenticación y autorización, no exposición de contenido no publicado y ausencia de
filtraciones de datos internos.

### 8.5 ObjectStorage

Primero, **el contrato** de la interfaz. Después, la integración: MinIO local, otro
S3-compatible y, más adelante, S3 real. El orden importa: el contrato es lo que permite
cambiar de implementación sin reescribir el dominio.

### 8.6 Seguridad

Se incluyen **deliberadamente** casos negativos:

- Usuario no autenticado y usuario sin permisos.
- Contenido inexistente y contenido no publicado.
- Identificadores inválidos o malformados.
- Entradas maliciosas.
- Filtración de datos en respuestas de error.
- Duplicados.
- *Race conditions* cuando sean relevantes.

Un endpoint protegido no está probado hasta que existe una prueba que demuestra que
**rechaza** al no autorizado.

---

## 9. Protección de los tests

> **Una implementación incorrecta NO se resuelve modificando el test para que pase.**

Los tests representan el comportamiento acordado. Un test **solo** puede modificarse cuando:

1. El requisito cambió.
2. El test contradice explícitamente la documentación vigente.
3. El test contiene un error **demostrado**.
4. El comportamiento esperado fue redefinido por una **decisión documentada**.

Cuando se detecte una contradicción entre **requisito**, **arquitectura** y **test**, hay que
**detenerse y documentarla** antes de cambiar ninguna expectativa. La contradicción es
información valiosa: resolverla en silencio la destruye.

**Está prohibido:**

- Reducir *asserts* solo para obtener GREEN.
- Borrar edge cases porque fallan.
- Marcar pruebas como `skip` sin justificación registrada.
- Usar `xfail` para ocultar un defecto.
- Mockear tanto que el comportamiento real deje de probarse.
- Cambiar los datos esperados para acomodar una implementación incorrecta.

Esta sección aplica **por igual** a las personas y a los agentes de programación.

---

## 10. Mocks: solo en los límites

- Mock **solo en boundaries**: repositorios, almacenamiento, reloj, servicios externos.
- **No** mockear los internals de la unidad que se está probando.
- Preferir un **fake simple** cuando exprese mejor el contrato que un mock con expectativas.
- Para PostgreSQL: integración real cuando el comportamiento depende de PostgreSQL (§8.3).
- Para almacenamiento: contrato **más** integración.
- Los tests **no** deben acoplarse a detalles privados: si un cambio interno sin efecto
  observable rompe la suite, la suite está mal acoplada.

---

## 11. Regresión

> **No bug fix without regression test.**

Todo defecto corregido sigue esta secuencia:

1. **Reproducirlo** con una prueba que **falla**.
2. Corregirlo.
3. **Dejar esa prueba permanentemente** en la suite.

La única excepción es una imposibilidad técnica, que debe quedar **documentada** en el
reporte de la tarea con su motivo.

---

## 12. Cobertura

> **Coverage is a signal, not the specification.**

La cobertura mide qué líneas se ejecutaron, no si el comportamiento es correcto. Un 100 % con
*asserts* triviales no prueba nada.

**No se acepta:**

- Tests sin *asserts* útiles.
- Tests triviales creados solo para subir el porcentaje.
- Exclusiones de cobertura sin justificación.

**Sí se exige:** para comportamiento de negocio nuevo, **todo branch significativo** debe
estar cubierto por un caso explícito de la matriz.

> **Umbral en CI.** Este documento **no** fija un porcentaje mínimo: la política definitiva de
> CI corresponde a `Task/020-CI-Backend`. Hasta entonces la cobertura se registra e
> interpreta, no se convierte en una puerta automática.

---

## 13. Property-based testing

Cuando una regla tenga un espacio de entrada amplio, podrá incorporarse **Hypothesis** u otra
herramienta *property-based*. Candidatos naturales: generación de *slugs*, paginación,
normalización de texto, límites numéricos, serialización, sanitización e invariantes de
estado.

Dos límites:

- **La dependencia no se añade en esta tarea.** Se incorporará en la tarea que realmente la
  necesite, con su justificación.
- **No usarla por obligación.** Cuando unos pocos ejemplos explícitos expresan mejor la
  regla, los ejemplos explícitos son la respuesta correcta.

---

## 14. Nomenclatura y estructura

### 14.1 Estructura objetivo

```
tests/
├── unit/          dominio e invariantes
├── integration/   PostgreSQL real, MinIO
├── contract/      contratos HTTP y de ObjectStorage
└── conftest.py
```

> **No se reorganizan ahora los tests de `Task/005`.** Esa tarea está aprobada y su estructura
> actual (`tests/` con `tests/integration/`) funciona. La estructura evolucionará cuando
> `Task/008` aporte volumen suficiente para que la separación sea útil, no por estética.

### 14.2 Nombres

El nombre de una prueba describe **el comportamiento**, no un número:

```python
# Bien: se lee como la regla de negocio
def test_no_se_puede_publicar_un_articulo_sin_contenido() -> None: ...

# Mal: no dice nada sobre qué se espera
def test_post_7() -> None: ...
```

Un fallo en CI debe ser comprensible **por su nombre**, sin abrir el archivo.

---

## 15. Evidencia exigida en cada tarea backend funcional

El reporte de la tarea debe contener:

| Evidencia | Detalle |
| --- | --- |
| **Matriz de casos** | Con la capa asignada a cada caso. |
| **RED** | Test escrito primero, ejecutado, fallando por la razón esperada. |
| **GREEN** | El mismo test en verde tras la implementación mínima. |
| **REFACTOR** | Ejecutado, o declarado innecesario con su razón. |
| **Suite completa** | Resultado real, incluidos fallos y omisiones con su motivo. |
| **Integración** | Ejecutada contra PostgreSQL real cuando aplique. |
| **Casos negativos y de seguridad** | Presentes cuando la funcionalidad los admita. |
| **Warnings** | Cero warnings no documentados. |

---

## 16. Documentos relacionados

- [`PROJECT_INSTRUCTIONS.md`](../claude/PROJECT_INSTRUCTIONS.md) — resumen operativo de la
  regla para cada sesión de Claude Code.
- [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md) — cuándo una tarea backend funcional puede
  marcarse `Lista para validación`.
- [`TASK_TEMPLATE.md`](TASK_TEMPLATE.md) — sección *TDD / Plan test-first* de cada ficha.
- [`WORKFLOW.md`](WORKFLOW.md) — ciclo de vida y aprobación de las tareas.
- [ETAPA 03](../stages/STAGE-03-domain-and-backend.md) — dónde empieza a aplicarse de verdad.
- [ADR-004](../adr/ADR-004-modular-monolith.md) — límites arquitectónicos que el refactor no
  puede romper.
- [`non-functional-requirements.md`](../architecture/non-functional-requirements.md) —
  requisitos M-01 a M-06 sobre mantenibilidad y pruebas.
