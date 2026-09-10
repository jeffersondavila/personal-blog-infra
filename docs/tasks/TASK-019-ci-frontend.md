# TASK-019 — CI Frontend

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/019-CI-Frontend` |
| **Nombre** | CI Frontend |
| **Etapa** | ETAPA 06 — Integración Continua |
| **Estado** | **Aprobada** el 2026-09-08 |
| **Repositorios involucrados** | personal-blog-frontend; personal-blog-infra solo documentación |
| **Dependencias** | `Task/018-Endurecimiento-de-Seguridad`, aprobada el 2026-09-08 |
| **Rama** | `Task/019-CI-Frontend` |
| **Rama base** | `main` — única base permitida |
| **Fecha de inicio / actualización** | 2026-09-08 |
| **Reporte** | [TASK-019-report.md](../task-reports/TASK-019-report.md) |

## 0. Preparación Git

Observado el 2026-09-08: en ambos repositorios se ejecutaron `fetch --prune`,
`switch main` y `pull --ff-only origin main`; `main == origin/main`, árboles
limpios y ausencia de Task019 local/remota. Se creó la rama desde `main` y se
comprobó inmediatamente `HEAD == main`, cero commits adicionales y árbol limpio.
El contenido de `main` y `origin/dev` coincidía al hacer el preflight.

| Repositorio | SHA base histórico |
| --- | --- |
| frontend | `2ee153422642b8cfcf41b230bfd8ff32b5da8210` |
| infra | `4ca82210a1eef7f53f9cc654eeea2b3750d830da` |

Regla de ramas: [WORKFLOW §2.1](../project-management/WORKFLOW.md). El backend
está fuera del alcance.

## 1. Objetivo

Automatizar formato, lint, tipos, build, pruebas y auditoría de vulnerabilidades
del frontend en GitHub Actions. Demostrar ejecución remota real por `push` y
controles negativos locales sobre los mismos comandos.

## 2. Contexto

Task018 dejó 703 tests verdes y auditoría npm sin vulnerabilidades en su cierre.
Su verificación puntual no satisface la automatización exigida por S-09.
ETAPA 05 está completada; el avance aprobado se conserva en **18/41 — 44 %**,
ETAPA 06 **0/3 — 0 %**. Task019 no suma hasta aprobación explícita.

Fuentes: ROADMAP, STATUS, WORKFLOW, DEFINITION_OF_DONE, TASK_TEMPLATE, STAGE-05/06,
NFR, security-boundaries, open-decisions, ficha/reporte de Task018 y los archivos
reales del frontend, incluido su lockfile y la documentación de contribución.
No existían fichas ni reportes anteriores de Task019–021 en las fuentes consultadas.

**Autorización histórica del 2026-09-08:** el usuario permitió commits y pushes
pre-aprobación exclusivamente de la rama frontend Task019 para validar el
bootstrap real de CI. No autorizó integrar en `dev`, crear PR, modificar
`main`/`dev`, settings, secretos, environments ni desplegar. El DoD permanece
intacto; las pruebas locales no sustituyen GitHub Actions. Infra conserva el
flujo ordinario de aprobación.

## 3. Dentro del alcance

- [x] Workflow para cada push y pull request, sin filtros de ramas/rutas.
- [x] Gates canónicos y auditoría del árbol npm completo (S-09 frontend).
- [x] Runtime coherente con Dockerfile; instalación por lockfile; un job y caché.
- [x] Permisos mínimos, acciones oficiales fijadas y control de costo.
- [x] Reproducir y corregir la advertencia Vite con regresión permanente.
- [x] Baseline, controles negativos con restauración por hash y regresión final.
- [x] Ejecución real `push` en GitHub y revisión de sus logs.
- [x] Documentación, riesgos y criterio 12 completos.

## 4. Fuera del alcance

Backend y su S-09: Task020. Infra y escaneo de secretos de todo el historial
disponible: Task021, con comprobación en el cierre global de STAGE-06.
Terraform: Task025 ampliará CI cuando exista. No se añaden E2E, cobertura mínima,
Lighthouse, Docker build, matrix, CD, cloud, OIDC, secretos ni GitHub settings.
No se cambia D-21, la política de seguridad HTTP ni el modelo de rendering.

La ejecución real del trigger `pull_request` y el verde sobre `dev` quedaron
fuera del alcance del bootstrap y se obtuvieron después, durante el cierre
autorizado: *observado el 2026-09-09 UTC*, las ejecuciones **34308296565**
(`pull_request`) y **34308234554** (`push` sobre `dev`) concluyeron `success`.
La mutación remota **sigue requiriendo autorización adicional**; no se publican
cambios deliberadamente rotos con el permiso de bootstrap.

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Workflow | frontend | `.github/workflows/ci-frontend.yml` |
| Corrección Vite y regresión | frontend | `vite.config.ts`, `vite.config.test.ts`, `tsconfig.node.json` |
| Instrucciones reproducibles | frontend | `CONTRIBUTING.md` |
| Gobierno y evidencia | infra | Esta ficha, reporte, STATUS, ROADMAP, STAGE-06, NFR, índice de reportes |

## 6. Criterios de aceptación

1. Todos los gates locales verdes, sin alterar timeouts ni workers.
2. Mutaciones de lint, TypeScript, test y build rechazadas; hashes restaurados y
   los mismos comandos de vuelta en verde. Ausencia de variables rechazada.
3. Workflow real de GitHub Actions por push con SHA correcto y conclusión
   `success`, gates visibles, duración y logs inspeccionados.
4. Sin secretos, cambios ajenos ni decisiones arquitectónicas nuevas; criterio 12 C=0.
5. Ficha y reporte completos; aprobación y conteos no adelantados.

## 7. TDD / Plan test-first

La ley de backend funcional no aplica: no se modifica backend. La corrección
Vite sí sigue la regla frontend de regresión antes del arreglo.

### 7.1 Comportamientos a construir

Ejecutar los gates existentes en CI y cargar la configuración de Vite sin
incompatibilidades de imports con el futuro loader nativo.

### 7.2 Matriz de casos

| Caso | Entrada / precondición | Resultado esperado | Capa |
| --- | --- | --- | --- |
| Vite heredado | Imports sin extensión | Regresión falla por advertencia real | Configuración |
| Vite corregido | Imports explícitos `.ts`, `noEmit` | Regresión verde; mismos artefactos | Configuración/build |
| Lint negativo | `console.log` en archivo analizado | `npm run lint` falla por `no-console` | Estática |
| Tipos negativos | Número asignado a `string` | `npm run typecheck` falla por TS2322 | TypeScript |
| Test negativo | Invertir una expectativa válida | `npm run test:run` falla por assertion | Vitest |
| Build negativo | Módulo inexistente en index.html | `npm run build` falla al resolverlo | Vite |
| Entorno inválido | Falta cada origen obligatorio | Build falla nombrando la variable | Configuración |
| Checkout limpio | Build antes de tests | Guardas SEO y P-05 ejecutadas | CI |

### 7.3 Tests RED esperados

`vite.config.test.ts` carga la configuración real mediante la API de Vite y
observa su logger. Con los imports heredados debe fallar por los dos avisos de
extensión, sin reemplazar ni silenciar el logger.

### 7.4 Integración necesaria

GitHub Actions real para el bootstrap. Ningún backend ni servicio de datos;
npm consulta el registro y las vulnerabilidades. Los valores VITE son ficticios.

### 7.5 Casos negativos y de seguridad

La matriz de §7.2 y el examen de YAML: sin permisos de escritura, sin contexto
de evento interpolado en shell y sin credenciales persistidas por checkout.

### 7.6 Regresiones relevantes

Suite canónica completa, artefactos SEO/P-05 y cabeceras aprobadas en Task018.
No cambian los tiempos de espera, workers ni expectativas existentes.

## 8. Plan de validación

Baseline Windows con versiones instaladas; ejecución de los comandos del YAML
con Node 22.23.2; controles negativos y restauración; equivalencia de builds
bundle/native; auditoría de archivos versionables y revisión del diff. Solo
después del verde local se usa el permiso excepcional de commit/push. Inspección
remota por GitHub CLI de evento, rama, SHA, jobs, pasos y logs.

## 9. Comandos de validación

Desde frontend, Node 22.23.2 y npm incluido:

```powershell
npm ci
npm run format:check
npm run lint
npm run typecheck
$env:VITE_API_BASE_URL = 'https://api.example.test'
$env:VITE_SITE_BASE_URL = 'https://example.test'
npm run build
npm run test:run
npm audit
git diff --check
```

No usar `npm install`, `--maxWorkers=2` ni aumentar timeouts para obtener verde.

## 10. Evidencia esperada

Reporte con exit codes, duración, tests, warnings, hashes de mutaciones,
acciones/runtime identificados, URL/SHA de ejecución remota y auditoría de logs.

## 11. Riesgos

| Riesgo | Impacto | Mitigación / propietario |
| --- | --- | --- |
| R-016-1, suite sensible a contención local | Timeout heredado | Conservar fallos y tiempos; suite canónica en runner real; Task019 |
| Consumo de minutos / cuelgues | Costo y feedback tardío | Un job, caché npm, cancelación por evento/ref, 10 minutos |
| Auditoría dependiente del registro | Fallo de red o nueva vulnerabilidad bloquea CI | Fail-closed, investigar sin silenciar ni ejecutar audit fix automáticamente |
| Historial de secretos todavía sin CI | Criterio global no cerrado | Task021 y cierre STAGE-06; no afirmar cobertura histórica aquí |

## 12. Decisiones técnicas

**Vigentes** desde la aprobación del 2026-09-08. No se requiere ADR: son
decisiones de implementación reversibles dentro del stack aprobado.

| Decisión | Alternativa considerada | Justificación |
| --- | --- | --- |
| Node 22.23.2, Ubuntu 24.04 | Copiar Node Windows 24 o matrix | Mismo parche del builder y un único runtime |
| Un job secuencial, build antes de tests | Jobs separados / tests primero | Un npm ci; guardas sobre artefacto real sin omisiones |
| `npm audit` sin flags | Umbral `high` / omitir dev | Conserva el comando verde de Task018; cubre al menos el mínimo crítico/alto de STAGE-05 |
| checkout/setup-node por SHA | Tags móviles | Reproducibilidad sin crear política global; releases oficiales verificadas |
| Caché por lockfile | Cachear node_modules | Reutiliza descargas manteniendo instalación reproducible |
| Concurrency workflow/event/ref | Agrupar todas las ramas | Aísla PR diferentes, main/dev y push/PR |
| Timeout de 10 minutos | 60 minutos / sin límite | Baseline medido; margen documentado en reporte |
| Imports `.ts`, loader vigente | Activar native / suprimir aviso | Corrección mínima sin cambiar el loader ni el artefacto |

## 13. Documentación creada o actualizada

Ficha, reporte, STATUS, ROADMAP, STAGE-06, non-functional-requirements e índice
de reportes en infra; CONTRIBUTING en frontend. DoD y WORKFLOW no se modifican.

## 14. Archivos modificados

Los de §5; listado exacto y acciones en el reporte §M. Sin archivos de backend,
manifiestos npm, lockfile, Dockerfile, código de producto ni tests previos alterados.

## 15. Resultado de pruebas

Resultados fechados completos en el reporte §C, §D, §I y §J. El baseline
registró 702/703 verdes con timeout en `formularios.test.tsx:260`; no se omite
ese fallo preexistente. La regresión Vite demostró RED y GREEN. La reproducción
con Node 22.23.2 y la ejecución remota **34305529115** —`push`, `success`, 79 s—
dieron **704 pruebas en 75 archivos** y **0 vulnerabilidades**. Ese verde remoto
aislado **no cierra R-016-1**.

## 16. Problemas encontrados

El requisito de CI real chocaba con la prohibición inicial de push. El usuario
lo resolvió con la autorización limitada de §2, manteniendo el DoD. Advertencia
Vite heredada reproducida y corregida; guardas de artefacto requieren construir
antes de tests. R-016-1 conserva su evidencia en el reporte.

## 17. Pasos de validación para el usuario

Ejecutar §9; revisar el YAML y el diff respecto a los SHA base; consultar las
ejecuciones remotas identificadas en el reporte §J. Los controles negativos
registrados no son evidencia de un push roto. El trigger `pull_request` **no** se
comprobó antes de aprobar —no se crea un PR pre-aprobación— sino en el cierre
ordinario, con la ejecución **34308296565**.

## 18. Deuda técnica pendiente

Task020: CI backend, lock/escaneo correspondientes. Task021: CI infra y cobertura
del historial de secretos de STAGE-06. Task025: gates Terraform cuando exista IaC.
Negativo remoto: requiere estrategia y autorización adicional del usuario.
R-016-1 no se cierra por una sola ejecución remota verde.

La ejecución `pull_request` y el verde sobre `dev` **dejaron de ser deuda** al
obtenerse en el cierre autorizado (§4). El criterio de salida de STAGE-06 sigue
exigiendo los **tres** repositorios, no solo el frontend.

## 19. Próxima tarea

`Task/020-CI-Backend` — pendiente, no iniciada. No se inicia en esta tarea.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-08** |
| **Aprobado por** | El usuario |
| **Expresión recibida** | `approved: Task/019-CI-Frontend` |

El permiso excepcional de bootstrap del 2026-09-08 **no** fue la aprobación de
Task019: la aprobación es la expresión registrada arriba, posterior y separada.
