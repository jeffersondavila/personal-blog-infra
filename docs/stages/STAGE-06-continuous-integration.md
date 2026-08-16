# ETAPA 06 — Integración Continua

| Campo | Valor |
| --- | --- |
| **Número** | 06 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 05](STAGE-05-quality-security.md) |
| **Tareas** | 3 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | CI verde en los tres repositorios. |

---

## Objetivo

Automatizar la verificación de calidad en cada cambio de los tres repositorios, de modo
que ningún cambio roto llegue a `dev` ni a `main`.

## Por qué esta etapa existe

Las verificaciones de la Etapa 05 solo tienen valor sostenido si se ejecutan solas.
Aquí se convierten en una barrera automática, no en un ritual manual.

## Tareas

### `Task/019-CI-Frontend` — *Pendiente*

Lint, type-check, tests y build en GitHub Actions.

**Depende de:** `Task/018`. **Repositorio:** `personal-blog-frontend`.

### `Task/020-CI-Backend` — *Pendiente*

Ruff, MyPy, Pytest, verificación de migraciones, build de imagen Docker y escaneo.

**Depende de:** `Task/018`. **Repositorio:** `personal-blog-backend`.

### `Task/021-CI-Infraestructura` — *Pendiente*

`docker compose config`, validación de scripts y escaneo de secretos.

> **Corrección de `Task/005.5`.** Esta tarea pertenece a la ETAPA 06 y **no existe todavía
> ningún archivo Terraform**: el primero lo crea `Task/025`, en la ETAPA 08. Declarar aquí
> `terraform fmt` y `terraform validate` produciría **checks permanentemente en verde por
> no tener nada que validar**, que es peor que no tenerlos: aparentan cobertura.
>
> Regla vigente: `Task/021` configura el CI de infraestructura **para los artefactos que
> existen en ese momento**, y **`Task/025` es responsable de ampliarlo** con `terraform
> fmt -check` y `terraform validate` cuando cree la IaC. Ese *ownership* futuro es
> explícito, no implícito.

**Depende de:** `Task/018`. **Repositorio:** `personal-blog-infra`.

## Criterios de salida de la etapa

- [ ] Cada repositorio ejecuta su workflow en cada push y pull request.
- [ ] Los tres workflows terminan en verde sobre `dev`.
- [ ] Un cambio deliberadamente roto hace fallar el workflow correspondiente.
- [ ] Ningún secreto aparece en los logs de CI.
- [ ] El tiempo de ejecución de cada workflow está documentado y es razonable.
- [ ] El escaneo de secretos cubre todo el historial disponible.
- [ ] **Ningún check pasa por no tener nada que verificar.** Si una verificación no aplica
      todavía, se declara explícitamente con la tarea que la incorporará.

## Fuera del alcance de la etapa

- Despliegue automático (Etapa 11).
- Credenciales cloud y OIDC (Etapa 09).
- `terraform plan` contra una cuenta real (Etapa 09/10).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Consumo de minutos de GitHub Actions. | Workflows acotados, caché de dependencias, sin matrices innecesarias. |
| CI que falla de forma intermitente y se ignora. | Tests deterministas; cualquier fallo intermitente se trata como defecto. |
| Escaneos que bloquean por falsos positivos. | Lista de excepciones justificada y revisada. |

## Siguiente etapa

[ETAPA 07 — Validación Local](STAGE-07-local-validation.md)
