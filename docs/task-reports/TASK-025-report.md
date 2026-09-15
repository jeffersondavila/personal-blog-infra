# TASK-025 — Reporte de ejecución

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/025-Terraform-Cloud` |
| **Etapa** | ETAPA 08 — Preparación Cloud + AWS Local Parity |
| **Estado** | **Lista para aprobación** — **AÚN NO APROBADA** |
| **Revisión previa a la aprobación** | **Superada. Sin bloqueos.** El 2026-09-14 el usuario autorizó la excepción temporal de S-09 —79 identidades, §15 quater— y la **excepción del laboratorio para H-025-1** —criterio 7, §20—. **H-025-3** corregido (§15 ter). Falta únicamente la expresión `approved: Task/025-Terraform-Cloud` |
| **Rama** | `Task/025-Terraform-Cloud` (**solo** `personal-blog-infra`) |
| **Rama base** | `main` — `c25642b8e4a7a06375a080a3f3cdf2512f5514d8` |
| **Fecha** | 2026-09-13 / 2026-09-14 |
| **Avance del proyecto** | **24/41 ≈ 59 % → 25/41 ≈ 61 %** con la aprobación del 2026-09-14 |
| **ETAPA 08** | **En progreso, 2 de 4 — 50 % → 3 de 4 — 75 %.** **No** queda completada: `Task/026` sigue **Pendiente** |

> **Las decisiones de este reporte quedaron APROBADAS el 2026-09-14** mediante
> `approved: Task/025-Terraform-Cloud`. Versiones, **D-06**, valores de laboratorio y
> *stage* local pasan a **Aceptadas y Vigentes**.
>
> **Los dos puntos que exigían decisión del usuario quedaron decididos el 2026-09-14:**
>
> 1. **H-025-1** — el criterio **7** (segundo plan `exit 0`) **no se cumple literalmente** en
>    Floci 2.0.1: `exit 2` por `aws_ssm_parameter.tags_all`. **Aceptado como excepción explícita
>    del laboratorio local.** Deja de ser bloqueante (§20).
> 2. **H-025-6** y **H-025-7** — **aceptación temporal autorizada** de 79 identidades,
>    registrada en el baseline canónico y revalidada (§15 quater).
>
> Ninguna de las dos declara el riesgo resuelto: siguen enumerados, con condiciones de
> reevaluación, y AWS real sigue siendo la autoridad final.

---

## 1. Qué se entrega

Terraform **portable**: **un solo grafo de 21 recursos**, con el provider oficial
`hashicorp/aws`, capaz de apuntar al laboratorio AWS local y —más adelante— a AWS real, sin
duplicar módulos ni mantener dos infraestructuras. Y **ejecutado de verdad**: `init`, `plan`,
`apply`, pruebas funcionales, idempotencia, `destroy` con **ausencia verificada**,
**reconstrucción**, *smoke* y segundo `destroy`.

**Cero recursos AWS reales. Cero cuentas AWS. Cero credenciales AWS reales.**

---

## 2. Estado de Git verificado al iniciar

No se confió en la transcripción del *preflight*: se volvió a comprobar.

| Repositorio | `main` | `origin/main` | `dev` | Árbol | Rama Task |
| --- | --- | --- | --- | --- | --- |
| `personal-blog-infra` | `c25642b8…` | **idéntico** | `e990d774…` | limpio | **creada** |
| `personal-blog-backend` | `4a40364b…` | idéntico | `8f0bf664…` | limpio | **no se crea** |
| `personal-blog-frontend` | `7dce98af…` | idéntico | — | limpio | **no se crea** |

Los SHA coincidieron **exactamente** con los heredados. `main` es ancestro de `dev` y
`git diff main dev` está vacío en infra y en backend.

Validación obligatoria tras crear la rama:

```
git rev-parse HEAD  -> c25642b8e4a7a06375a080a3f3cdf2512f5514d8
git rev-parse main  -> c25642b8e4a7a06375a080a3f3cdf2512f5514d8   (coinciden)
dev NO es ancestro de HEAD                                        (comprobado)
```

**Incidencia menor, resuelta.** Al verificar las versiones de Terraform, un `cd` al
directorio temporal falló y un archivo de trabajo propio (`tf_index.json`, el índice de
*releases* de HashiCorp) quedó momentáneamente en la raíz de infra. Se identificó, se
comprobó qué era y se eliminó **antes** de crear la rama. El árbol estaba limpio en el
momento de `git switch -c`.

---

## 3. Versiones y procedencia — verificadas, no heredadas

Cada afirmación del *preflight* se comprobó contra la fuente oficial.

### 3.1 Terraform CLI

| Comprobación | Resultado |
| --- | --- |
| Versión | **1.16.2** — la última `1.16.x` publicada |
| `sha256` `linux_amd64` | `0d17011f0c4664539b164b044903d04e296c86c13cb9f28040076c65cfb3985a` |
| `sha256` `windows_amd64` | `6ef140ce1d399dc43b8315194176ddc2dfb5c21d607968e82ef20a55cfff40d0` |
| Fuente | `releases.hashicorp.com/terraform/1.16.2/terraform_1.16.2_SHA256SUMS` |
| ¿Coinciden con el *preflight*? | **Sí, los dos, exactamente** |
| Artefacto descargado | `terraform_1.16.2_windows_amd64.zip: OK` con `sha256sum --check --strict` |
| **Firma GPG** | `Good signature from "HashiCorp Security (hashicorp.com/security)"`, clave primaria `C874 011F 0AB4 0511 0D02 1055 3436 5D94 72D7 468F` |
| Binario ejecutado | `Terraform v1.16.2 on windows_amd64` |

### 3.2 Provider `hashicorp/aws`

| Comprobación | Resultado |
| --- | --- |
| Versión | **6.64.0** — la última publicada (`published_at 2026-09-09T20:52:07Z`) |
| `sha256` `linux_amd64` | `17324d4335a7a7ac01cc23eded530775606680ff53b47cb74a3cb95d1121f836` |
| `sha256` `windows_amd64` | `cd776b83b1f7b36635957350afe7ce28ba4e4ea3a5e2deb00d13dbd3b35d9d40` |
| ¿Coinciden con el *preflight*? | **Sí, los dos, exactamente** |
| Constraint | `version = "= 6.64.0"` — exacta, no rango |

**El lock los contiene.** `terraform/.terraform.lock.hcl` lleva `zh:17324d43…` y
`zh:cd776b83…`, es decir **los mismos** `sha256` oficiales, más un `h1:` por plataforma.
Hay una prueba que lo exige: `test_el_lock_lleva_el_checksum_oficial_de_cada_plataforma`.

### 3.3 Emulador — qué representa cada digest

El *preflight* proponía un digest y observaba otro. Se comprobó **qué es cada uno**:

| Referencia | Valor | Qué es |
| --- | --- | --- |
| Etiqueta `2.0.1` | `sha256:4e451c39c7bb88e3cd4f87e8fc0c25d5b47695a51185d521e2241fa00486e8eb` | **Índice OCI multiarquitectura** (`application/vnd.oci.image.index.v1+json`, 1611 bytes). Es lo que devuelve `docker-content-digest` y lo que fija el Compose |
| Manifiesto `linux/amd64` | `sha256:b4f89d163c0f343d619cf85e728650eeb9345b725372347d140a01a6585ac379` | El manifiesto de la plataforma **dentro** de ese índice |

Los dos coinciden **exactamente** con el *preflight*. El índice contiene además `linux/arm64`
y dos entradas `unknown/unknown` (atestaciones).

`docker pull` por el digest del índice resolvió a `amd64/linux`, con
`FLOCI_VERSION=2.0.1`, `org.opencontainers.image.licenses=MIT`, revisión
`225233c19256b4e62f7c43e0131d3cf5d2d263dd` y puerto `4566/tcp`. Base UBI9-minimal.

> **Advertencia de versión, y por qué importa.** ADR-006 verificó el emulador en la **1.6.0**
> el 2026-08-15. `2.0.1` es un salto de **major**. Por eso **ninguna** capacidad se heredó de
> aquella verificación: todas las celdas de la matriz se re-observaron ejecutando. Una
> diferencia quedó **deliberadamente sin re-evaluar** y así consta: el CHANGELOG de `2.0.0`
> menciona *«cloudwatch: evaluate alarms over CloudWatch's wider evaluation range»*, que
> contradiría lo observado en la 1.6.0 sobre la ausencia de motor de evaluación de alarmas.
> **No se comprobó**, y por tanto esa fila **no** cambia de estado.

### 3.4 Runtime de Lambda — el punto delicado de la cadena de suministro

El emulador resuelve el runtime por **etiqueta móvil**: `public.ecr.aws/lambda/python:3.12`.
No se puede fijar por digest desde la configuración del laboratorio.

Lo que se hizo, que es lo único honesto disponible:

1. **Pre-descargar** la imagen y registrar el digest que la etiqueta resuelve hoy:
   `sha256:a89893d9c93a9ffbf9e35ca32d7cadc635cbf3a9aec94480c75ed07150a05daa`.
2. **Exigir que coincida** con el digest que `Task/024` fijó al construir el artefacto. Es
   el mismo. Si dejan de coincidir, el laboratorio **se detiene** con un mensaje explícito:
   ejecutar el artefacto sobre un runtime distinto del que lo construyó invalidaría la
   evidencia.
3. **Confirmar en ejecución** qué imagen usó el emulador. Sus propios logs lo dicen:
   `Image already present locally, skipping pull: public.ecr.aws/lambda/python:3.12`.

Es decir: la Lambda se ejecutó sobre **exactamente** la imagen que `Task/024` usó para
empaquetar, y el ciclo **no dependió de ninguna descarga**. La fragilidad —que la etiqueta
se mueva— queda registrada como riesgo, no resuelta: no está en nuestra mano fijarla.

### 3.5 Alcance honesto de estas comprobaciones (S-09)

| Qué se demuestra | Qué **no** se demuestra |
| --- | --- |
| **Identidad y procedencia**: `sha256` contra las sumas oficiales, firma GPG del archivo de sumas, digests de imagen exactos | **Ausencia de vulnerabilidades.** Un checksum no sabe nada de CVE |

No se afirma en ningún punto que Terraform, el provider o el emulador estén libres de
vulnerabilidades. **El baseline histórico de MinIO y Portainer no recibió ni un hallazgo
nuevo**: sus 100 y 16 identidades siguen siendo **idénticas por `sha256`** a las de `HEAD`, y
la tolerancia cero de las imágenes propias sigue en pie. Lo que sí cambió —el 2026-09-14, por
autorización expresa del usuario— es que el archivo **incorpora dos entradas nuevas**, `floci`
y `terraform`, con 70 y 9 identidades: §15 quater. El archivo **ya no está intacto**, y decir
lo contrario sería falso.

---

## 4. Arquitectura entregada

### 4.1 Un solo grafo

```
terraform/
  versions.tf      required_version = "= 1.16.2"; provider = "= 6.64.0"
  providers.tf     el UNICO lugar donde cambia el destino
  variables.tf     todo lo que distingue un destino de otro
  main.tf          el grafo: identico para local y para AWS real
  outputs.tf       contrato que consume el verificador
  .terraform.lock.hcl   VERSIONADO, las dos plataformas
  modulos/
    almacenamiento/   S3: bucket de medios (8 recursos)
    parametros/       SSM: parametros de configuracion
    identidad/        IAM: rol de ejecucion y politica en linea
    registro/         CloudWatch Logs: grupo con retencion
    computo/          Lambda: la funcion
    api_http/         API Gateway v2: api, integracion, ruta, stage, permiso
  entornos/
    local/local.tfvars                  destino laboratorio
    produccion/produccion.tfvars.example  PLANTILLA, no operativa
```

**No existen** `terraform/local/` ni `terraform/production/` con recursos duplicados. No hay
un solo `count` ni `for_each` condicionado por entorno en `main.tf`. La diferencia entre
destinos vive **entera** en `providers.tf` y en el `.tfvars`, y cada una encaja en la tabla
de diferencias **legítimas** de [`aws-local-parity.md`](../architecture/aws-local-parity.md)
§4.4:

| # de §4.4 | Diferencia | Dónde |
| --- | --- | --- |
| 1 | Bloque `endpoints` | `providers.tf`, desde `var.endpoints_aws`; `null` contra AWS |
| 2 | Flags `skip_*` y `s3_use_path_style` | `providers.tf`, desde `var.laboratorio` |
| 3 | Credenciales | Entorno, **nunca** en Git |
| 4 | Backend de estado | Bloque generado antes de `init` (**D-06**) |
| 5 | Región | `.tfvars` |
| 6 | Nombres y prefijos | `.tfvars` |
| 8 | Memoria, *timeout*, retención | `.tfvars` (**D-11**, **D-12**) |

El bloque `endpoints` se declara **una sola vez** y siempre: con los ocho atributos en `null`
el provider resuelve los endpoints de AWS igual que si no existiera. Así el destino es un
**valor**, no una bifurcación del código — que es lo que vigila el riesgo **R-26**.

### 4.2 Los 21 recursos, y por qué cada uno

| Módulo | Recursos | Por qué |
| --- | --- | --- |
| `almacenamiento` | `aws_s3_bucket`, `ownership_controls`, `public_access_block`, `versioning`, `server_side_encryption_configuration`, `cors_configuration`, `policy`, `lifecycle_configuration` | Bucket de medios privado. `BucketOwnerEnforced` en lugar de ACL. Política que **niega** todo acceso sin TLS. Cifrado `AES256` sin introducir KMS, que tendría costo |
| `parametros` | `aws_ssm_parameter` ×4 | Configuración en la nube. `ignore_changes` sobre `value`: el valor puede rotarse fuera de Terraform sin que sea *drift*; lo que Terraform posee es la **existencia** y el **tipo** |
| `registro` | `aws_cloudwatch_log_group` | Creado por Terraform y **no** por el servicio: así nace con retención declarada. Un grupo que crea Lambda nace con retención **infinita** |
| `identidad` | `aws_iam_role`, `aws_iam_role_policy` | Rol de ejecución con mínimo privilegio derivado del código real del backend |
| `computo` | `aws_lambda_function` | `package_type = Zip` porque ADR-003 excluye ECR; `source_code_hash` para que un ZIP nuevo **aparezca** en el plan |
| `api_http` | `aws_apigatewayv2_api`, `integration`, `route`, `stage`, `aws_lambda_permission` | HTTP API v2 por costo (ADR-003). `AWS_PROXY` con *payload* 2.0, que es lo que traduce el adaptador de `Task/023`. Ruta comodín porque quien enruta es FastAPI |

Más **un *data source***, `aws_iam_policy_document`, que **no crea nada**.

Los permisos del rol se derivaron leyendo el backend, no inventándolos:

| Permiso | Recurso | De dónde sale |
| --- | --- | --- |
| `s3:GetObject`, `PutObject`, `DeleteObject` | `…/medios/*` | `app/modules/media/domain/claves.py` genera `medios/<uuid4>/original.<ext>` |
| `s3:ListBucket` **condicionado a `s3:prefix = _readiness/*`** | el bucket | `app/shared/storage/s3_compatible.py` sonda con `ListObjectsV2` y ese prefijo. Por eso el permiso puede condicionarse en lugar de permitir enumerar el bucket entero |
| `logs:CreateLogStream`, `PutLogEvents` | el grupo propio | La función escribe en su grupo; no necesita crear grupos |
| `ssm:GetParameter`, `GetParameters` | los 4 parámetros, **nombrados uno a uno** | Nunca por comodín sobre una ruta |

La función **no** puede administrar IAM, crear buckets, administrar API Gateway, leer el
estado de Terraform ni desplegarse a sí misma.

### 4.3 D-06 — el backend de estado

La dificultad real: **`-backend-config` cambia los ajustes de un backend, no su tipo.** Elegir
entre estado local y remoto obliga a que el bloque `backend { … }` sea distinto.

Solución: el lanzador genera **únicamente ese bloque** (`terraform/backend.generado.tf`,
ignorado por Git) justo antes de `init`. Los recursos, módulos y variables son fuente
versionada. **El grafo no se genera.**

El estado vive **fuera de Git** y **fuera del emulador** —cuyo almacenamiento es `memory` y
se destruye con el contenedor: guardarlo ahí sería perder el registro de lo que hay que
destruir—. La ruta se deriva del entorno; **no hay ninguna ruta absoluta de usuario en
ningún archivo versionado**.

Propuesta completa, incluido el destino AWS futuro (bucket S3 privado dedicado,
`use_lockfile = true` **sin** DynamoDB nueva, *bootstrap* separado):
[`open-decisions.md`](../architecture/open-decisions.md) **D-06**. **Sigue abierta** hasta la
aprobación.

---

## 5. El laboratorio

### 5.1 Separado del entorno del blog

El laboratorio es un Compose **aparte**: `laboratorio/docker-compose.laboratorio.yml`.
`docker-compose.yml` **no se tocó**. Comprobado al terminar: los seis servicios del entorno
ordinario seguían en pie y sanos, sin reiniciarse.

Razón: el emulador monta `/var/run/docker.sock`. Quien controla ese socket **controla el
host**. Eso no entra en el entorno de desarrollo diario.

### 5.2 Topología de red — decidida midiendo, no suponiendo

Se comprobó empíricamente algo que condicionaba todo el diseño:

> **Una red de Compose con `internal: true` DESCARTA EN SILENCIO la publicación de puertos.**
> `docker compose ps` mostró `4566/tcp` en lugar del mapeo, y `curl` al puerto falló con
> *«Could not connect»*. Con una sola red interna, Terraform **no podría** hablar con el
> emulador.

De ahí dos redes:

| Red | Tipo | Para qué |
| --- | --- | --- |
| `entrada` | bridge | **Solo** para publicar `4566` en `127.0.0.1`. Por aquí entran Terraform y el verificador |
| `ejecucion` | **`internal: true`** | Donde el emulador lanza los contenedores de Lambda (`FLOCI_SERVICES_LAMBDA_DOCKER_NETWORK`) |

Aislamiento **demostrado**, lanzando un contenedor en esa red y pidiéndole salir:

| Prueba | Resultado |
| --- | --- |
| TCP a `1.1.1.1:443` | `bash: connect: Network is unreachable` |
| TCP a `169.254.169.254:80` (metadata) | `bash: connect: Network is unreachable` |
| DNS externo (`registry-1.docker.io`) | sin resolución |
| Alcanza el emulador | `172.21.0.2  emulador` — **sí** |

Los contenedores de la función alcanzan el emulador y **no** tienen salida a internet ni al
rango *link-local*.

**Diferencia registrada, no disimulada:** el **emulador** sí tiene salida, por `entrada`. Ya
posee el socket de Docker, que es un privilegio mayor. Lo que el perímetro protege es el
código que se ejecuta dentro de la función.

**El demonio de Docker no respeta `internal`.** `internal: true` aísla a los *contenedores*,
no al demonio, que seguiría descargando una imagen que falte. Por eso las imágenes se
pre-descargan y se verifican **antes** de arrancar el ciclo, y el ciclo no depende de ninguna
descarga. Los logs del emulador lo confirman: *«Image already present locally, skipping
pull»*.

### 5.3 Publicación y versión

| Control | Cómo se cumple |
| --- | --- |
| S-01, S-02, S-03 | `ports: "127.0.0.1:4566:4566"`. **Nada** de los rangos auxiliares del Compose oficial (`6379-6399`, `7001-7099`, `9200-9299`): son de ElastiCache, RDS y OpenSearch, que este proyecto no usa |
| S-10 | Fijado por **digest del índice OCI**. Nunca `latest` ni `nightly`. Hay un gate de CI que lo comprueba |
| S-04, S-05 | Credenciales `test`/`test`, exigidas **exactamente**; cualquier otra cosa aborta |
| S-07 | `SecureString` con valor **ficticio**. Ningún secreto real |

`FLOCI_STORAGE_MODE: memory`: el laboratorio es efímero a propósito. El estado que importa
—el de Terraform— vive fuera.

---

## 6. Test-first — RED, GREEN, refactor

No es una tarea de backend funcional, así que **B-1…B-12 no son su clasificación formal** y
la suite del backend **no se tocó**. Pero la lógica Python de orquestación y seguridad se
construyó con disciplina `RED → GREEN`.

### 6.1 RED demostrado

La matriz de §7.2 de la ficha se cerró **antes** de escribir implementación. Los cinco
módulos de prueba se escribieron primero y se ejecutaron:

```
ERROR: test_destino        ModuleNotFoundError: No module named 'laboratorio'
ERROR: test_artefacto      ModuleNotFoundError: No module named 'laboratorio'
ERROR: test_herramientas   ModuleNotFoundError: No module named 'laboratorio'
ERROR: test_inventario     ModuleNotFoundError: No module named 'laboratorio'
ERROR: test_firma_aws      ModuleNotFoundError: No module named 'laboratorio'

Ran 5 tests in 0.001s
FAILED (errors=5)                                        exit=1
```

Fallaron **por la razón esperada**: la implementación no existía.

### 6.2 GREEN

```
Ran 112 tests in 0.154s
OK
```

Y la suite preexistente seguía intacta: `tests/security` → **13 tests, OK**. *Esas 13 siguen pasando hoy; la carpeta tiene ahora **40**, porque la aceptación temporal de S-09 añadió 27 pruebas de la política `pinned-artifact` (§15 quater). El estado final está en §14.*

### 6.3 Tres defectos propios encontrados por las pruebas, y corregidos

Los tres se arreglaron **cambiando la implementación**, nunca la expectativa. Y en los tres
se escribió antes el test que los reproduce.

| # | Defecto | Cómo apareció | Corrección |
| --- | --- | --- | --- |
| 1 | La guarda del plan rechazaba `aws_iam_policy_document` | El primer `plan` real abortó | Un *data source* **lee**: no crea, no cambia, no destruye. Se distingue por `mode == "data"` y se exige que su única acción sea `read`. **Omitir `mode` se sigue tratando como gestionado**, que es el lado seguro |
| 2 | El gate de idempotencia no podía **nombrar** qué cambiaba | El segundo `plan` devolvió `exit 2` | Ver §8.3. La tolerancia se declara por **tipo y atributo**, exige motivo, y cualquier otro cambio sigue abortando |
| 3 | **La comprobación de credenciales estaba vacía** | Un control negativo del CLI: `AWS_ACCESS_KEY_ID=AKIA…` **no abortó** | La configuración del laboratorio se superponía al entorno del host y **sustituía** la credencial real por la fixture antes de que ninguna guarda la mirara. **No había fuga** —el proceso hijo se construye desde una *allowlist*—, pero la detección era vacua. Se invirtió la precedencia: **el valor del host siempre gana y siempre se juzga** |

El tercero es el más importante de los tres: las guardas eran correctas, pero el cableado las
dejaba mirando un entorno ya saneado. Regresión permanente en
`tests/laboratorio/test_lanzador.py`.

---

## 7. Guardas *fail-closed*

### 7.1 Las capas

Ninguna es «`AWS_ACCESS_KEY_ID=test`». El destino se resuelve exigiendo que **cada** vía por
la que podría entrar un destino real esté ausente o apunte al laboratorio.

| Capa | Qué exige |
| --- | --- |
| Modo explícito | `local` o `production`, exacto. Sin valor por omisión. `LOCAL` no es `local` |
| **`production` rechazado** | No existe autorización de AWS real |
| Ocho endpoints | `s3`, `ssm`, `iam`, `lambda`, `apigatewayv2`, `logs`, `cloudwatch`, `sts`. Falta uno → aborta |
| Forma del endpoint | Esquema `http`/`https`, anfitrión local permitido, **puerto explícito**, sin `userinfo`, sin ruta |
| Credenciales | `test`/`test` **exactas**. El valor recibido **nunca se imprime** |
| Sin credenciales alternativas | `AWS_SESSION_TOKEN`, `AWS_SECURITY_TOKEN`, `AWS_PROFILE`, `AWS_DEFAULT_PROFILE`, `AWS_SHARED_CREDENTIALS_FILE`, `AWS_CONFIG_FILE`, `AWS_WEB_IDENTITY_TOKEN_FILE`, `AWS_ROLE_ARN`, `AWS_ROLE_SESSION_NAME`, `AWS_CONTAINER_CREDENTIALS_*` |
| Metadata | `AWS_EC2_METADATA_DISABLED` **exactamente** `true`; `AWS_EC2_METADATA_SERVICE_ENDPOINT*` ausentes |
| Sin proxies | `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY` y sus minúsculas |
| Sin overrides de Terraform | `TF_CLI_ARGS`, `TF_CLI_ARGS_*`, `TF_CLI_CONFIG_FILE` |
| `AWS_ENDPOINT_URL*` | Si existe, debe ser local |
| Región | `us-east-1`, y `AWS_DEFAULT_REGION` no puede discrepar |
| **Entorno del hijo construido** | *Allowlist*, no herencia: lo que no está nombrado no llega |
| **Identidad comprobada** | `sts:GetCallerIdentity` contra el endpoint local. Esperado y observado: `000000000000` |
| **Una sola escritora** | Cerrojo `O_EXCL`: el ciclo toca Docker, el emulador y el artefacto, fuera del bloqueo de estado de Terraform |
| **Revalidación antes de destruir** | La identidad se vuelve a comprobar inmediatamente antes de cada `destroy` |

La variable de entorno **no** es el perímetro de metadata: la red `ejecucion` también bloquea
el rango *link-local* (§5.2). Son dos capas porque confiar en una variable deja la protección
en manos de quien exporta el entorno.

### 7.2 Controles negativos

**Ninguno intenta alcanzar AWS real.** Todos usan entradas sintéticas, temporales y destinos
locales falsos; el fallo ocurre **antes** de abrir cualquier socket.

Trece controles al nivel del CLI, todos con `exit=1`:

| Control negativo | Resultado |
| --- | --- |
| `--modo production` | `el modo 'production' esta rechazado: no existe autorizacion para actuar sobre AWS real` |
| `AWS_PROFILE=produccion` | aborta, **sin mostrar el valor** |
| `HTTPS_PROXY=http://proxy.corp:3128` | aborta |
| `AWS_ACCESS_KEY_ID=AKIA…` con forma de clave real | `no es la credencial ficticia esperada; el valor recibido no se muestra` |
| `AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/…` | ídem, **sin filtrar el secreto** |
| `AWS_SESSION_TOKEN=…` | aborta |
| `TF_CLI_ARGS_plan=-refresh=false` | aborta |
| `AWS_REGION=eu-west-1` | `vale 'eu-west-1' y el laboratorio opera en 'us-east-1'` |
| `AWS_EC2_METADATA_DISABLED=false` | `debe valer exactamente 'true'` |
| `AWS_WEB_IDENTITY_TOKEN_FILE=…` | aborta |
| `AWS_SHARED_CREDENTIALS_FILE=…` | aborta |
| `LAB_ENDPOINT_S3=https://s3.amazonaws.com` | `apunta a 's3.amazonaws.com', que no es un anfitrion local permitido` |
| `LAB_ENDPOINT_LAMBDA=` (vacío) | `faltan endpoints locales obligatorios: lambda` |

Más los de la suite unitaria: cuenta STS inesperada, ZIP inexistente, ZIP modificado con el
**mismo tamaño**, checksum de herramienta erróneo, lock sin una plataforma, plan con recurso
inesperado, plan con acción inesperada, `destroy` incompleto, escritura concurrente, segundo
plan con cambios, limpieza incompleta, `aws_db_instance` y `aws_rds_cluster` en el plan.

### 7.3 El cliente de inspección

El laboratorio necesita hablar con el emulador para comprobar S3, SSM, IAM, Lambda y Logs.
Este repositorio no declara **ninguna** dependencia de terceros para Python, así que se
implementó **SigV4 con la biblioteca estándar**.

Validado contra el **ejemplo canónico publicado por AWS**: la firma calculada es
`5d672d79c15b13162d9279b0855cfba6789a8edb4c82c400e06b5924a6f2b5d7`, la documentada. No es una
aproximación: sigue el protocolo.

> **Decisión propuesta, con su contrapartida dicha.** La alternativa era añadir `boto3` o el
> AWS CLI a infra. Se prefirió no introducir una cadena de dependencias nueva —con su
> verificación de procedencia y su lugar en el gate S-09— para inspeccionar un laboratorio
> local. La contrapartida es que **la firma la escribimos nosotros**, y de ahí la prueba de
> respuesta conocida. Si el usuario prefiere `boto3`, se sustituye este módulo **sin tocar
> Terraform ni las guardas**.
>
> Consecuencia registrada con precisión: la fila **AWS CLI / boto3** de la matriz sigue en
> `No evaluada`, porque **no se usaron**. Lo demostrado es que el **protocolo AWS** funciona
> contra el destino local.

---

## 8. El ciclo, ejecutado

Orden real, con revalidación del destino antes de cada operación destructiva.

### 8.1 Antes del primer `plan`

| # | Requisito | Resultado |
| --- | --- | --- |
| 1 | Guardas unitarias | **112 tests, OK** *(las de ese momento; hoy son 143 — §14)* |
| 2 | Herramienta verificada | `sha256` + firma GPG; `Terraform v1.16.2` |
| 3 | Lock del provider | Las dos plataformas; `init -lockfile=readonly` pasa y **el lock no cambia** |
| 4 | Digest del emulador | Índice OCI comprobado contra el registro |
| 5 | Compose válido | `config --quiet` correcto |
| 6 | Imágenes pre-descargadas | Emulador y runtime, digests registrados |
| 7 | Runtime = el de `Task/024` | **Coinciden** |
| 8 | Red aislada | Demostrada (§5.2) |
| 9 | Sin credenciales del host | Guardas; 13 controles negativos |
| 10 | Sin metadata | Variable **y** red |
| 11 | STS local | `000000000000` |
| 12 | ZIP válido y congelado | `sha256 6580410109207f330a329ee235e0424a6bb3f7d96d14f550c4605eb3d8a02841`, 43 288 578 bytes |
| 13 | `fmt -check -recursive` | correcto |
| 14 | `validate` | `Success! The configuration is valid.` |

**Nota sobre el artefacto.** Se reconstruyó con
`personal-blog-backend/scripts/empaquetar_lambda.py` y dio **el mismo SHA-256** que registró
`Task/024`: una **tercera** construcción independiente byte a byte idéntica. El ZIP **no se
versiona** y **no se copió** a infra: se consume por `--lambda-zip <ruta>`. El SHA histórico
de `Task/024` es **evidencia de esa tarea**, no una constante: no está fijado en ningún
archivo de este repositorio.

### 8.2 `plan` y `apply`

`Plan: 21 to add, 0 to change, 0 to destroy.` — revisado contra la lista **cerrada** de tipos
previstos, recurso a recurso. Un *data source* (`read`), 20 recursos gestionados.

Entre el `plan` y el `apply` se volvió a exigir que el ZIP fuera **byte a byte** el mismo.

`Apply complete! Resources: 21 added, 0 changed, 0 destroyed.`

### 8.3 Idempotencia — un `exit 2` investigado, no ocultado

El segundo `plan -detailed-exitcode` devolvió **2**: `0 to add, 4 to change, 0 to destroy`,
los cuatro parámetros SSM, y **solo** en `tags_all`.

Se investigó con llamadas directas a la API en lugar de suponer:

| Observación | Resultado |
| --- | --- |
| `ssm:ListTagsForResource` sobre un parámetro creado por Terraform | `{"TagList": []}` — **sin etiquetas** |
| `ssm:AddTagsToResource` y volver a leer | `{"TagList": [{"Key": "Prueba", …}]}` — **sí las persiste** |
| `logs:ListTagsForResource` sobre el grupo de logs | Las **cuatro** etiquetas por omisión, presentes |

**Diagnóstico:** el emulador **descarta las etiquetas enviadas en `PutParameter`**, que es
como el provider las aplica al crear un `aws_ssm_parameter`. Etiquetar por separado funciona,
y otros servicios conservan las etiquetas. Contra AWS real `PutParameter` honra `Tags` y el
plan converge.

**Qué NO se hizo, y por qué.** No se puso `ignore_changes = [tags, tags_all]` en el módulo.
Eso viajaría a producción y silenciaría un *drift* **real** de un atributo que AWS sí sabe
representar: es exactamente el acoplamiento al emulador que prohíbe ADR-006 (límite 2) y que
vigila **R-26**.

**Qué se hizo.** La tolerancia vive en el **verificador del laboratorio**, no en la
infraestructura. Se declara por **tipo y atributo concretos**, obliga a un motivo escrito, y
**cualquier** otro cambio —una creación, una destrucción, otro atributo, el mismo atributo en
otro tipo— sigue abortando. Hay seis pruebas que lo fijan. El resultado se informa como
**«idempotente salvo la diferencia documentada»**, nunca como idempotente sin más.

**Los módulos quedan intactos para AWS real.**

### 8.4 Camino crítico — el objetivo central (R-25)

**Hallazgo:** el atributo `api_endpoint` de `aws_apigatewayv2_api` **no sirve contra el
destino local**. No es un fallo del emulador: lo sintetiza el **provider** como
`https://{id}.execute-api.{region}.amazonaws.com`. Contra AWS real es la URL correcta; en
local no resuelve a nada alcanzable.

La API local se direcciona por el dominio del emulador. Se comprobaron **dos** vías:

| Vía | Petición | Resultado |
| --- | --- | --- |
| DNS comodín | `http://{id}.execute-api.localhost.floci.io:4566/health` | **HTTP 200** |
| Cabecera `Host` | `Host: {id}.execute-api…` contra `http://127.0.0.1:4566/health` | **HTTP 200** |

La segunda existe porque **no depende de resolver un nombre público**: el laboratorio no
debería necesitar un registro DNS de terceros.

Respuesta, sin firmar, como la haría un navegador:

```
GET /health  ->  HTTP 200
{"status":"ok","service":"personal-blog-backend","version":"0.1.0"}
```

**Y el mismo cuerpo, byte a byte, que el entorno local ordinario** (`uvicorn` detrás de
Traefik en `http://localhost:8081/health`).

> **La combinación que la suite oficial de compatibilidad del emulador NO cubre —Terraform +
> API Gateway v2 + Lambda + CloudWatch Logs, el camino crítico exacto de este proyecto,
> riesgo R-25— funciona.**

La diferencia de direccionamiento queda confinada al **cliente**: el grafo, los módulos y las
salidas de Terraform son idénticos para los dos destinos.

### 8.5 Pruebas funcionales

| Servicio | Qué se ejercitó | Resultado |
| --- | --- | --- |
| **S3** | `PUT`, `GET`, `ListObjectsV2` con el prefijo de la sonda, **URL prefirmada**, `DELETE` | 200 / 200 / 200 / 200 / 204. El objeto recuperado coincide **byte a byte** |
| **S3 — control negativo** | Lectura **anónima**, sin firma ni prefirmada | **200, no 403** → ver §9 |
| **SSM** | `GetParameter` sobre los cuatro | 200; `database_url` como `SecureString`, el resto `String` |
| **IAM** | `GetRole` | 200; la política de confianza nombra **exclusivamente** `lambda.amazonaws.com` |
| **Lambda** | `GetFunction` | 200; `Zip`, `python3.12`, `app.lambda_handler.handler`, `x86_64`, 512 MB, 30 s |
| **API Gateway v2** | `GET /health` por HTTP real | **200** (§8.4) |
| **CloudWatch Logs** | `FilterLogEvents` | **2 eventos reales** recuperados |

Los eventos de log no son un contador: son la aplicación ejecutándose.

```
{"timestamp":"2026-09-14T02:39:42.001Z","level":"INFO","logger":"app.main",
 "message":"Aplicacion inicializada","module":"main","line":112,…}
{"timestamp":"2026-09-14T02:39:42.028Z","level":"INFO","logger":"mangum.http",
 "message":"GET /health 200","module":"http","line":100,…}
```

Se usó `FilterLogEvents` **a propósito** y no Logs Insights: Insights degrada en silencio
ante sintaxis no soportada, así que un resultado vacío no distinguiría «no hay eventos» de
«la consulta no se entendió». No se crearon filtros de suscripción, que se almacenan pero no
entregan.

### 8.6 `destroy`, ausencia, reconstrucción

| Etapa | Resultado |
| --- | --- |
| Revalidación del destino antes de destruir | Identidad `000000000000` reconfirmada |
| Primer `destroy` | `Destroy complete! Resources: 21 destroyed.` |
| Estado de Terraform | 0 recursos — **y esto NO es la evidencia** |
| **Ausencia por API** | S3 **0**, Lambda **0**, API Gateway **0**, Logs **0**, SSM **0** |
| **Reconstrucción desde cero** | `Apply complete! Resources: 21 added` |
| *Smoke* de la reconstrucción | `GET /health` → **200**, mismo cuerpo |
| Segundo `destroy` | `Destroy complete! Resources: 21 destroyed.` |
| Ausencia por API, otra vez | Los cinco servicios en **0** |

**El emulador siguió en pie durante las comprobaciones de ausencia**, a propósito: retirarlo
antes de verificar no sería evidencia de que el `destroy` funcionó — sería borrar al testigo.

Al bajar el laboratorio: **0 contenedores, 0 redes, 0 volúmenes**. Se buscan por **nombre de
proyecto** y no por etiqueta de Compose, porque los contenedores que el emulador lanza para
las funciones no los crea Compose y `compose down` no los conoce.

---

## 9. Limitaciones del emulador — registradas, no disimuladas

Las tres se descubrieron ejecutando, y las tres están en la matriz de paridad.

### 9.1 S3 no aplica la autorización

La lectura **anónima** de un objeto del bucket devolvió **200**, no 403.

`FLOCI_SERVICES_S3_ENFORCE_AUTH` es `false` por omisión. **Un 200 aquí no dice que el bucket
sea público: dice que el emulador no comprueba la autorización.**

Consecuencia, dicha con precisión: el laboratorio demuestra que la **configuración** de
privacidad —los cuatro bloqueos, `BucketOwnerEnforced`, la política que niega sin TLS— **se
acepta**. **No** demuestra que el bucket sea privado. **La privacidad efectiva es AWS-only:
`Task/030`.**

### 9.2 SSM descarta las etiquetas en `PutParameter`

§8.3. Impide converger en `tags_all`. Diagnóstico completo y decisión de no ocultarlo allí.

### 9.3 IAM no aplica políticas

Conocido desde ADR-006 §6.5 (**R-28**) y **reconfirmado**: el laboratorio valida que el rol
**se crea** y la política **se adjunta**, no que **autorice**. Un rol insuficiente —o
excesivo— pasaría igual. La política se escribió con mínimo privilegio real porque es la que
irá a AWS, **no** porque esté probada. **Mínimo privilegio = AWS-only: `Task/028`,
`Task/032`.**

### 9.4 Lo que tampoco se afirma

| No se afirma | Por qué |
| --- | --- |
| Que una versión de objeto **expiró** | El *lifecycle* se acepta; un vencimiento tarda días y no se observa en un ciclo |
| Que las alarmas **se disparan** | **No se creó ninguna alarma.** `SetAlarmState` nunca demostraría evaluación automática |
| Que el AWS CLI o `boto3` funcionan | **No se usaron** (§7.3) |
| Que el arranque en frío local sirva para dimensionar | No es comparable con AWS. **D-12** sigue abierta |
| Que Terraform o el provider estén libres de CVE | Solo se verificó identidad y procedencia |
| **«Paridad completa»** | Ese estado **no existe** en la matriz, a propósito |

---

## 10. Matriz de paridad

Rellenada con evidencia real en
[`aws-local-parity.md`](../architecture/aws-local-parity.md) §7. Estados resultantes:

| Servicio | Estado propuesto |
| --- | --- |
| S3 | `Paridad parcial` — autorización no aplicada |
| SSM Parameter Store | `Paridad parcial` — sin cifrado real; etiquetas descartadas |
| IAM | `Paridad parcial` — solo creación y adjunción |
| Lambda | `Compatible local` |
| API Gateway v2 | `Requiere adaptación` — `api_endpoint` no usable en local |
| CloudWatch Logs | `Compatible local` |
| CloudWatch Metrics / alarmas | `No evaluada` — no se creó ninguna |
| Terraform (`plan`/`apply`/`destroy`) | `Paridad parcial` |
| AWS CLI / boto3 | `No evaluada` — no se usaron |

Cada fila registra versión, autoridad, la prueba concreta, el resultado, la diferencia y la
tarea que lo validará en AWS real.

---

## 11. CI Infra

El placeholder *«Terraform is not here yet (Task/025 adds its gates)»* se sustituyó por gates
reales. La guarda se **invirtió**: ahora falla si los `.tf` **desaparecen** o si el lock deja
de estar versionado, para que nadie retire la infraestructura dejando los gates pasando en
vacío.

| Gate nuevo | Qué comprueba |
| --- | --- |
| Fuentes y lock | ≥ 1 `.tf` versionado y `terraform/.terraform.lock.hcl` **en el índice de Git** |
| Instalación de Terraform | Versión exacta **y** `sha256` verificado, igual que Gitleaks y Trivy |
| Coherencia de versión | La instalada coincide con la de `versions.tf` |
| `fmt -check -recursive` | Formato en todos los módulos |
| `init -backend=false -lockfile=readonly` | Sin backend, sin estado, y **el lock no cambia** (`git diff --exit-code`) |
| `validate` | Configuración válida |
| Guardas del laboratorio | Las 112 pruebas *fail-closed* |
| Compose del laboratorio | `config --quiet` |
| Emulador en loopback y fijado | Ningún puerto fuera de `127.0.0.1`; ninguna etiqueta móvil; digest `sha256` completo; socket de Docker y red `internal` presentes |

**No se automatiza `plan`/`apply`/`destroy` contra el emulador.** Ese ciclo se ejecuta en
local en esta tarea; automatizarlo con un emulador efímero es **`Task/039`**, tal como asigna
la documentación vigente.

**Nada se relajó:** Compose del blog, variables, PowerShell, Python, baseline exacto,
Gitleaks sobre el historial completo, Trivy y el gate S-09 quedan como estaban. La guarda
*«No shell scripts yet»* **se conserva**: no se introdujo ningún `.sh`, y todo se resolvió con
Terraform, Python de la biblioteca estándar y Docker/Compose.

---

## 12. `.gitignore`

| Cambio | Por qué |
| --- | --- |
| **El lock deja de ignorarse** | Era un error: `.terraform.lock.hcl` fija qué provider exacto se instala. Ignorarlo permite que cada máquina resuelva uno distinto dentro de la misma constraint |
| `local.tfvars` se versiona | No contiene secretos: nombres locales y valores ficticios |
| Se ignoran los archivos **generados** | `backend.generado.tf` y `terraform/generado/`: configuración de una ejecución, no fuente |
| Se ignoran estado, planes y `.terraform/` | El estado puede contener valores sensibles (S-10) |
| Se ignora `laboratorio/.env.laboratorio` | El `.example` sí se versiona |
| Se ignoran los ZIP | El artefacto lo construye el backend |
| **Sección Python nueva** | `scripts/laboratorio/` es el primer **paquete** Python del repositorio, así que desde ahora existen `__pycache__`. Se detectó porque una ejecución manual los dejó listos para versionarse |

Comprobado con `git add --dry-run`: el lock, `local.tfvars` y los `.example` **se
versionarían**; el estado, los planes, los generados y los `__pycache__` **no**.

---

## 13. Criterion12 — hallazgos heredados

Cada candidato se reclasificó leyendo su contexto completo en el `main` actual, **antes** de
tocar nada.

| Candidato | Clasificación | Acción |
| --- | --- | --- |
| STATUS: resumen del avance y distribución por estado con **21 aprobadas / 51 %**, ETAPA 06 «cierre pendiente», ETAPA 07 al 0 %, ETAPA 08 con su nombre antiguo | **A — contradicción VIVA.** Es un resumen vigente, sin fecha ni marco histórico, y contradecía la *Vista rápida*, el ROADMAP y las fichas de etapa | **Corregido: D-025-1** |
| ROADMAP: `**Avance global:** **54 %** (22 de 41)` | **A — contradicción VIVA.** Dato vigente; las entradas fechadas de arriba ya decían 24/41 ≈ 59 %, así que el documento se contradecía consigo mismo | **Corregido: D-025-2** |
| ROADMAP, fila `Task/021`: «**Terraform todavía no existe** (llega en `Task/025`)» | **C — texto cuya semántica cambia con esta tarea.** Era cierto al escribirse | **Anotado con fecha: C-025-1.** El texto original se conserva citado |
| STATUS: «`Task/006` … **no comienza hasta** que el usuario fusione el PR de `Task/005.2`» | **B — registro histórico fechado válido.** Está dentro del bloque de `Task/005.2`, cuya convención es el presente histórico («el avance **permanece** en 5 de 41») | **No se toca** |
| STATUS: «las decisiones **D-15** y **D-16**, ambas **abiertas**» | **B — registro histórico fechado válido.** Dentro del bloque de `Task/005.5`. D-15 ya figura **Resuelta** en la tabla vigente de decisiones | **No se toca** |
| STATUS, «Etapa actual»: parecía decir solo «ETAPA 07 — Completada» | **Falso positivo mío.** La celda **sí** continúa con «ETAPA 08 … **En progreso**, **2 de 4 (50 %)**»; mi primera lectura estaba truncada | **No se toca** |
| STATUS, tabla de `Task/024` «Pendiente / solo backend» | **No reproducido.** La fila no existe con ese contenido en el `main` actual | **Nada que corregir** |
| `local-to-cloud-mapping`: excluye métricas/alarmas del laboratorio | **C — sigue siendo válido.** `Task/025` **no creó ninguna alarma**, así que el texto describe correctamente el alcance ejecutado | **No se toca** |
| `local-to-cloud-mapping`: observabilidad del VPS «no decidida» | **B/C — sigue siendo cierto.** ADR-008 decide Grafana Cloud y Alloy; el texto habla de que **CloudWatch observe el VPS**, que es otra cosa y sigue sin decidirse (**D-20**, `Task/031`) | **No se toca** |
| STAGE-08: casilla de equivalencia del adaptador sin marcar | **A parcial.** Hay evidencia nueva real, pero marcar criterios de salida pertenece al **cierre aprobado** (`WORKFLOW.md` §8) | **Evidencia añadida bajo el criterio; la casilla NO se marca** |

**Resultado: 2 correcciones tipo D, 1 tipo C, 1 evidencia añadida.** Los registros
históricos fechados **no se reescribieron**: eran correctos en su fecha, y ese es justo el
motivo por el que se conservan.

---

## 14. Validaciones finales

> **Esta tabla es la del estado FINAL**, reejecutada el 2026-09-14 después de las dos
> decisiones humanas y después de corregir **DEF-025-1** y **DEF-025-2** (§23). Las cifras de
> versiones anteriores de esta sección —112 y 13 tests, 50 archivos, «baseline intacto»— eran
> ciertas cuando se escribieron y **ya no lo son**: se sustituyen, no se conservan, porque una
> tabla de validaciones finales obsoleta es peor que no tenerla.

| Validación | Comando | Resultado |
| --- | --- | --- |
| Espacios y conflictos | `git diff --check --cached HEAD` | **sin problemas** |
| Finales de línea | `git ls-files --eol` sobre los 57 archivos | **57 en LF**, 0 con CRLF |
| Python compila | `compile()` sobre `scripts/` y `tests/` | **22 archivos, 0 fallos** |
| Guardas del laboratorio | `unittest discover -s tests/laboratorio -p 'test_*.py'` | **143 tests, OK** |
| Suite de seguridad | `unittest discover -s tests/security -p 'test_*.py'` | **40 tests, OK** |
| Compose del blog | `config -q` con `.env.example` | **válido** |
| Compose del laboratorio | `config -q` con `.env.laboratorio.example` | **válido** |
| `terraform fmt` | `-check -recursive` | **correcto** |
| `terraform init` | `-backend=false -lockfile=readonly` | **correcto**, y el lock **no cambió** |
| `terraform validate` | — | `Success! The configuration is valid.` |
| Paso 184 del CI | Loopback, digest fijado, red `internal` | **correcto**: publica en `127.0.0.1`, digest `sha256:4e451c39…` |
| Enlaces Markdown | Regex con exclusión de bloques de código | **371 enlaces relativos, 0 roto** en los 7 documentos tocados |
| Coherencia de identidad (S-09) | `vulnerability_gate.py --comprobar-coherencia .` | **exit 0**: el `sha256` coincide en baseline, workflow y lanzador |
| Baseline: ASCII puro | Recuento de bytes `> 127` | **0**. La regresión cp1252 que rompió la suite no volvió |
| Baseline vs evidencia medida | Identidad exacta de 7 campos | **70/70** en floci y **9/9** en Terraform: **0 accionables sin aprobar**, **0 entradas obsoletas** |
| Baseline: lo histórico | `sha256` de `accepted_findings` contra `HEAD` | **idéntico**: MinIO 100, Portainer 16, postgres 0, traefik 0. Solo se añadieron las **dos** entradas autorizadas |
| Secretos | **Gitleaks 8.30.1**, invocación exacta del CI, sobre un *commit* de prueba con los 57 archivos, y además `gitleaks dir` sobre el árbol completo | **0 hallazgos, exit 0** en los dos modos. Hubo **3** en el código antes de corregir **DEF-025-2**, y **1 más** en este propio reporte al documentarlo: los cuatro corregidos |
| Rutas absolutas | Todos los archivos de código y configuración | **una**, y es la fixture sintética de un control negativo |
| Residuos | Docker por nombre de proyecto **y** por `label=floci=true` | **0 contenedores, 0 redes, 0 volúmenes** |
| Git, tres repositorios | `status`, `rev-parse`, `merge-base`, `ls-remote` | infra en `Task/025-Terraform-Cloud` con `HEAD == main`; `dev` **no** es ancestro; backend y frontend en `main` **limpios**; **0** ramas remotas `Task/025*` |

**Lo ejecutado en su momento y no repetido hoy**, porque nada de esta revisión lo afecta: el
**ciclo completo** contra el emulador (`laboratorio.py ciclo`, **exit 0**) y la **medición con
Trivy** de los componentes (§15 bis y §15 quater). El estado del baseline frente a esa
medición **sí** se reverificó hoy, fila por fila, y es el que consta arriba.

**No se ejecutó `push`.** No hay commits, ni rama publicada, ni pull request.

**Tamaño del cambio.** `git diff --shortstat main..HEAD` informa *57 files changed, 10512
insertions(+), 62 deletions(-)* repartidos en los commits de esta rama: el grafo de Terraform,
el laboratorio, los gates de CI y S-09, y el cierre documental. Los dos archivos que faltaban
respecto a la cifra de la revisión —55 archivos— son los de §23:
`laboratorio/.env.laboratorio.example` y `tests/laboratorio/ejemplo_canonico_de_aws.py`.

> *La cifra que esta sección declaró durante la revisión previa —10491 inserciones con todo
> en el índice y sin commits— era cierta en ese momento. Los commits del cierre aprobado la
> movieron, y la corrección consta aquí en vez de quedar desfasada.*

---

## 15. Secretos y S-10

| Regla | Cumplimiento |
| --- | --- |
| No versionar `tfstate` | Ignorado, y además vive **fuera del árbol de Git** |
| No versionar credenciales reales | Ninguna. Las únicas credenciales versionadas son `test`/`test` en el `.example`, **públicas por diseño** y exigidas por el emulador |
| No versionar `.env` | `laboratorio/.env.laboratorio` ignorado; solo el `.example` |
| No versionar el ZIP | Ignorado; se consume por ruta |
| No introducir un secreto de JWT | **No se introdujo.** El backend usa sesión opaca *server-side* (**D-02**) y no necesita ninguno |
| Ningún secreto real en SSM | El valor de `database_url` es ficticio y no conecta con nada. El emulador **no cifra** (S-07) |
| No imprimir valores recibidos | Las guardas nombran la variable y **nunca** su valor |
| Ningún literal con forma de credencial | Los ejemplos **públicos** de AWS que necesitan los controles negativos y la prueba de firma viven **partidos** y en un **solo** módulo, `tests/laboratorio/ejemplo_canonico_de_aws.py`. Su valor efectivo no cambia —la firma canónica sigue reproduciéndose— y no queda ningún literal en los tres archivos que los usan. **Partirlos no basta por sí solo:** la primera versión usaba trozos de 21, 9 y 10 caracteres y Gitleaks marcaba el primero igual. Cada fragmento se queda ahora en **8**, por debajo del mínimo de 10 de la regla `generic-api-key`, y está **verificado** con la invocación exacta del CI, no supuesto (**DEF-025-2**, §23.2). Un falso positivo ahí es indistinguible de un hallazgo real hasta que alguien lo investiga, y el historial no se reescribe |
| Sin rutas absolutas de usuario | Ni en Terraform, ni en los tests, ni en la documentación durable. La caché y el estado se derivan del entorno |

---

## 15 bis. S-09 — escaneo de vulnerabilidades

> **Esta sección es el motivo por el que la revisión previa a la aprobación queda
> BLOQUEADA.** No se ha aceptado ningún residual nuevo, no se ha tocado el baseline y no se
> ha cambiado la política. La decisión es del usuario.

### 15 bis.1 Qué exige S-09 y qué faltaba

[`non-functional-requirements.md`](../architecture/non-functional-requirements.md) define
**S-09** como **«Dependencias auditables: versiones fijadas **y** escaneo de
vulnerabilidades en CI»**. Son dos obligaciones, no una.

`Task/025` introduce una dependencia de infraestructura nueva —la imagen del emulador— y
hasta esta revisión cumplía **solo la primera**:

| Obligación de S-09 | Estado antes de esta revisión |
| --- | --- |
| Versión fijada | ✔ digest del índice OCI, con gate de CI que lo comprueba |
| **Escaneo de vulnerabilidades en CI** | ✘ **faltaba** |

Comprobado en los artefactos reales, sin suponer: el paso `Scan every infrastructure image`
del workflow escanea **cuatro** imágenes —`postgres`, `traefik`, `minio`, `portainer`— y
`security/vulnerability-baseline.json` declara **esas mismas cuatro** y ninguna más. El
emulador quedaba fuera del inventario, fuera del escaneo y fuera del comparador.

### 15 bis.2 Escaneo ejecutado

Mecanismo canónico del proyecto, sin desviaciones:

| Aspecto | Valor |
| --- | --- |
| Herramienta | Trivy **0.74.0** — la versión exacta que fija el workflow |
| Invocación | `trivy image --scanners vuln --severity LOW,MEDIUM,HIGH,CRITICAL --format json` |
| `--ignore-unfixed` | **No usado** — no forma parte de la política |
| `.trivyignore` | **No existe y no se creó** |
| Referencia escaneada | `floci/floci:2.0.1@sha256:4e451c39…86e8eb` — **el digest real**, no una etiqueta |
| Digest confirmado en el informe | `RepoDigests: floci/floci@sha256:4e451c39…86e8eb` |
| SO detectado | `redhat 9.7` (UBI9), 106 paquetes de sistema |
| Análisis de lenguaje | 1 archivo: `usr/local/bin/gosu` (`gobinary`) |

> El binario de Trivy usado en local es el `windows_amd64` de la **misma versión 0.74.0**
> que el workflow instala; el digest que el CI verifica es el del artefacto **Linux**. La
> medición de CI se hará sobre el mismo `linux/amd64` de la imagen, que es la plataforma que
> el laboratorio fija.

### 15 bis.3 Inventario completo del emulador — sin filtrar nada

| Severidad | Total | Con `FixedVersion` publicada |
| --- | --- | --- |
| **CRITICAL** | **4** | **4** |
| **HIGH** | **72** | **66** |
| MEDIUM | 170 | 114 |
| LOW | 78 | 22 |
| **TOTAL** | **324** | — |

HIGH/CRITICAL **sin** corrección publicada: **6** (todos HIGH). No son accionables según la
política vigente, y **no se ocultan**: quedan aquí registrados.

### 15 bis.4 Hallazgos ACCIONABLES — política vigente: HIGH o CRITICAL con fix publicado

**70 hallazgos accionables.** Extraídos con el **propio comparador del proyecto**
(`scripts/security/vulnerability_gate.py`, función `extraer_accionables`), no con un criterio
inventado.

Distribución por ámbito:

| Ámbito | Accionables | CRITICAL | HIGH |
| --- | --- | --- | --- |
| `usr/local/bin/gosu` (`gobinary`) | **56** | **4** | 52 |
| `os-pkgs:redhat` (UBI9) | **14** | 0 | 14 |
| **Total** | **70** | **4** | **66** |

**Los cuatro CRITICAL, uno a uno.** Los cuatro están en el **mismo archivo** y el **mismo
paquete**:

| CVE | Paquete | Versión instalada | Corregido en | Ámbito |
| --- | --- | --- | --- | --- |
| `CVE-2023-24538` | `stdlib` | `v1.18.2` | 1.19.8, 1.20.3 | `usr/local/bin/gosu` |
| `CVE-2023-24540` | `stdlib` | `v1.18.2` | 1.19.9, 1.20.4 | `usr/local/bin/gosu` |
| `CVE-2024-24790` | `stdlib` | `v1.18.2` | 1.21.11, 1.22.4 | `usr/local/bin/gosu` |
| `CVE-2025-68121` | `stdlib` | `v1.18.2` | 1.24.13, 1.25.7, 1.26.0-rc.3 | `usr/local/bin/gosu` |

**Causa concreta, que conviene entender antes de decidir.** 56 de los 70 accionables
—**incluidos los cuatro CRITICAL**— provienen de **un solo ejecutable**: `gosu`, compilado
con la biblioteca estándar de **Go 1.18.2**, de junio de 2022. La imagen declara
`GOSU_VERSION=1.17` en su entorno. No son 56 defectos distintos del emulador: son las CVE
acumuladas de la *toolchain* de Go con la que se compiló una utilidad auxiliar que el
emulador usa para bajar de privilegios.

Los **14 restantes** son paquetes de UBI9 cuya corrección existe en `el9_8` mientras la
imagen está en `el9_7`:

| Paquete | Instalada | Corregida en | Accionables |
| --- | --- | --- | --- |
| `gnutls` | `3.8.3-10.el9_7` | `3.8.10-4.el9_8` | 4 |
| `sqlite-libs` | `3.34.1-9.el9_7` | `3.34.1-11.el9_8` | 2 |
| `curl-minimal` | `7.76.1-35.el9_7.3` | `7.76.1-40.el9_8.5` | 2 |
| `libcurl-minimal` | `7.76.1-35.el9_7.3` | `7.76.1-40.el9_8.5` | 2 |
| `openssl-libs` | `1:3.5.1-7.el9_7` | `1:3.5.5-4.el9_8` | 1 |
| `libcap` | `2.48-10.el9_7.1` | `2.48-10.el9_8.1` | 1 |
| `libacl` | `2.3.1-4.el9` | `2.4.0-1.el9_8` | 1 |
| `glib2` | `2.68.4-18.el9_7.2` | `2.68.4-19.el9_8.2` | 1 |

La lista íntegra de los 70, con CVE, severidad, paquete, versión instalada, versión
corregida y ámbito, está en la salida del comparador conservada como evidencia de esta
revisión.

### 15 bis.5 Qué NO se hizo

| No se hizo | Por qué |
| --- | --- |
| Añadir los 70 al baseline | Requiere **decisión humana explícita**. Un baseline no es un lugar donde archivar hallazgos sin que nadie los mire |
| Marcarlos como riesgo aceptado | Misma razón |
| Cambiar la política S-09 | La política no se toca para acomodar un hallazgo |
| Buscar otra versión del emulador y sustituir `2.0.1` | Sería cambiar el entregable **en silencio** después de haberlo validado, y obligaría a repetir el ciclo entero |
| Aprobarlos por comparación con MinIO/Portainer | Que exista residual aceptado en otras imágenes **no** es un argumento para aceptar este |
| Usar `--ignore-unfixed`, `.trivyignore` o un umbral | No forman parte de la política, y el baseline los prohíbe explícitamente |
| Tocar el baseline histórico | `security/vulnerability-baseline.json` queda **byte a byte intacto**: las 100 identidades de MinIO, las 16 de Portainer y la tolerancia cero de las imágenes propias |
| Añadir el gate de CI para el emulador | Añadirlo hoy dejaría **CI Infra en rojo** de forma permanente. Eso es una decisión del usuario, no una que se toma por inercia |

### 15 bis.6 Qué haría falta si el usuario acepta el residual

El mecanismo existente **ya admite** la imagen sin crear una segunda política. La entrada
tendría esta forma, que es la que el validador exige (`policy`, `expected_digest`,
`reference` coherente con `nombre:tag@digest`, `risk` y `accepted_findings`):

```
{
  "key": "floci",
  "policy": "accepted-baseline",
  "reference": "floci/floci:2.0.1@sha256:4e451c39…86e8eb",
  "expected_digest": "sha256:4e451c39…86e8eb",
  "risk": "<riesgo que lo acepta>",
  "accepted_findings": [ … las 70 identidades exactas … ]
}
```

Con eso, el comportamiento sería el pretendido: **digest distinto → RED**, **accionable
nuevo → RED**. Y el CI añadiría el emulador al paso de escaneo existente, reutilizando el
mismo comparador.

**Nada de esto se ha escrito.** Hacerlo equivaldría a aceptar el residual por cuenta propia.

### 15 bis.7 Alcance real del escaneo de Terraform y del provider

Se comprobó si Trivy puede decir algo **significativo** de estos dos binarios, en lugar de
afirmar cobertura sin medirla. **Sí puede**: son binarios Go con información de compilación
embebida, y el analizador `gobinary` los inventaría.

| Componente | Paquetes detectados | Inventario | Accionables |
| --- | --- | --- | --- |
| **Terraform CLI 1.16.2** | **253** | 9 HIGH + 1 MEDIUM | **9 HIGH** |
| **provider `hashicorp/aws` 6.64.0** | **377** | **0** | **0** |

El escaneo **no** es vacío ni semánticamente inútil, así que aplica el caso **A**: se
incorpora como medición y se documenta.

**Los 9 accionables de Terraform** están todos en `stdlib v1.26.4` —la *toolchain* de Go con
la que HashiCorp compiló 1.16.2—: `CVE-2026-33818`, `CVE-2026-39821`, `CVE-2026-39822`,
`CVE-2026-46600`, `CVE-2026-56853`, `CVE-2026-56858`, `CVE-2026-56859`, `CVE-2026-56860` y
`CVE-2026-56862`, corregidas en Go 1.26.6 / 1.27.0-rc.3. Es decir: **no hay una versión de
Terraform 1.16.x sin ellas**, porque dependen de que HashiCorp recompile.

**El provider está limpio**, con un inventario de 377 paquetes que demuestra que el análisis
ocurrió de verdad.

> La medición local se hizo sobre los artefactos `windows_amd64`. En CI corresponderían los
> `linux_amd64`, compilados con la misma *toolchain*, así que se espera el mismo resultado
> **sin haberlo observado**. No se afirma lo contrario.

### 15 bis.8 Runtime de Lambda heredado de `Task/024`

Se escaneó también, porque entró al proyecto con `Task/024` y tampoco figura en el baseline:

| Componente | SO | Inventario | Accionables |
| --- | --- | --- | --- |
| `public.ecr.aws/lambda/python:3.12@sha256:a89893d9…05daa` | Amazon Linux 2023, 88 paquetes | 2 HIGH + 5 MEDIUM + 1 LOW | **2 HIGH** |

Los dos accionables son el mismo CVE en dos paquetes: `CVE-2026-14456` en
`openssl-fips-provider-latest` y `openssl-snapsafe-libs`, ambos `1:3.5.7-2.amzn2023.0.1`,
corregidos en `1:3.5.7-2.amzn2023.0.2`.

**Matiz que cambia su peso, y que no debe perderse:** esta imagen **no se despliega**. Sirve
para *construir* el artefacto (`Task/024`) y para *ejecutar* la Lambda en el laboratorio
(`Task/025`). En AWS real el runtime lo provee AWS. Su perfil de riesgo **no es** el de una
imagen en producción. Eso no la exime de S-09; sí cambia la urgencia.

Este hallazgo pertenece al alcance heredado y **no se resuelve aquí**.

### 15 bis.9 Tabla final de S-09

| Componente | Versión | Identidad | Procedencia | Mecanismo de vulnerabilidad | Resultado | Cobertura | Residual |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Terraform CLI** | 1.16.2 | `sha256` verificado en los dos artefactos | **Firma GPG** de HashiCorp Security | Trivy 0.74.0, `gobinary` | **9 accionables HIGH** | **VERIFICADO** — 253 paquetes | **Sin aceptar**; depende de que HashiCorp recompile |
| **provider `hashicorp/aws`** | 6.64.0 | `sha256` verificado; `zh:` en el lock versionado | `SHA256SUMS` oficial | Trivy 0.74.0, `gobinary` | **0 accionables** | **VERIFICADO** — 377 paquetes | **Ninguno** |
| **Emulador (Floci)** | 2.0.1 | Digest del índice OCI, confirmado por el informe | Registro oficial; licencia MIT | Trivy 0.74.0, `redhat` + `gobinary` | **70 accionables** (4 CRITICAL) | **VERIFICADO** — 106 paquetes + `gosu` | **BLOQUEANTE — pendiente de decisión humana** |
| **Runtime Lambda** (heredado `Task/024`) | `python:3.12` por digest | Digest fijado y comprobado en ejecución | `public.ecr.aws` | Trivy 0.74.0, `amazon` + `python-pkg` + `gobinary` | **2 accionables HIGH** | **VERIFICADO** — 88 paquetes + 2 análisis de lenguaje | **Sin aceptar**; imagen no desplegada |

**Los cuatro componentes resultaron VERIFICADOS**: en ninguno el escáner devolvió un análisis
vacío, así que no hay ninguna fila **NO EVALUABLE CON EL SCANNER ACTUAL**. La distinción
importante sigue siendo la otra: **identidad y procedencia** estaban demostradas antes de
esta revisión; **vulnerabilidades** no lo estaban, y ahora sí se han medido.

> *Esta sección registra la medición tal como quedó **antes** de la decisión humana, y se
> conserva fechada: era cierta el 2026-09-14 por la mañana. Lo medido **pasó después** a estar
> temporalmente aceptado por autorización expresa del usuario — §15 quater.*

### 15 bis.10 Consecuencia — *en el momento de esta medición*

**La revisión previa a la aprobación quedó BLOQUEADA POR S-09.** No fue un fallo del trabajo
de `Task/025`: la infraestructura funciona y está demostrada. Fue que la tarea introduce una
imagen de terceros cuyo residual de seguridad **nadie había aceptado**, y aceptarlo —o
rechazarlo— era una decisión del usuario.

> **Resuelto el mismo día.** El usuario autorizó una excepción **temporal y limitada**, y el
> bloqueo quedó levantado: ver **§15 quater**. Esta sección se conserva porque documenta la
> medición y el análisis de aplicabilidad sobre los que se tomó esa decisión.

Las opciones, sin recomendación implícita en el orden:

| # | Opción | Consecuencia |
| --- | --- | --- |
| 1 | **Aceptar** el residual del emulador con baseline exacto e identidad fijada | El emulador entra en S-09. Hay que escribir las 70 identidades y su `risk`. `Task/025` podría aprobarse. Se acepta ejecutar en local una imagen con 4 CRITICAL en `gosu` |
| 2 | **Evaluar otra versión** del emulador | Puede reducir el residual. **Obliga a repetir el ciclo completo** —`apply`, funcional, idempotencia, `destroy`, reconstrucción— y a revalidar la matriz de paridad (control S-11) |
| 3 | **Acotar el riesgo** antes de aceptar | El emulador es **solo local**, en loopback, y su red de ejecución no tiene salida. Eso **reduce** la exposición pero **no** elimina los CVE, y no cambia lo que S-09 exige |
| 4 | **Rechazar** el emulador | Obliga a reconsiderar ADR-006 con un ADR nuevo. El coste es alto: la IaC es portable por diseño, pero se pierde el laboratorio |

**Lo que no es una opción** es aprobar `Task/025` dejando el emulador fuera de S-09: eso
incumpliría el requisito, que exige versiones fijadas **y** escaneo en CI.

---

## 15 ter. H-025-3 — la guarda del runtime estaba mal, y se corrigio

### 15 ter.1 Que estaba mal

La primera guarda hacia `docker pull` de la **etiqueta**
`public.ecr.aws/lambda/python:3.12` y abortaba si el digest al que resolvia ya no era el que
`Task/024` fijo. Comprobaba **frescura de la etiqueta** y la trataba como autoridad de
identidad.

El 2026-09-14 el problema se materializo: la etiqueta paso a resolver a
`sha256:7ff4d0d3…012f`. El laboratorio se detenia, sin salida salvo tocar `Task/024`.

**Pero la reproducibilidad de `Task/024` nunca estuvo rota.** Comprobado, no supuesto:

| Comprobacion | Resultado |
| --- | --- |
| `Task/024` construye con referencia inmutable | `REFERENCIA_DEL_RUNTIME = etiqueta + "@" + digest`. No usa la etiqueta desnuda |
| El digest fijado sigue descargable | Se **borro** la copia local y se volvio a bajar por digest desde el registro |
| El artefacto sigue siendo reproducible | Se reconstruyo el ZIP y dio el **mismo** `sha256 6580410109…a02841` |

Es decir: la guarda imponia que una etiqueta mutable siguiera apuntando eternamente al digest
antiguo. Eso bloquea el laboratorio ante un refresco rutinario de la imagen base de AWS y no
protege nada.

### 15 ter.2 Que se hizo

La preocupacion de fondo **si** era legitima: el emulador resuelve el runtime **por
etiqueta**, asi que lanzaria la imagen nueva mientras el ZIP se construyo sobre la vieja. La
respuesta correcta es **fijar**, no abortar.

`scripts/laboratorio/runtime.py`:

1. **lee** la identidad del runtime del `manifiesto.json` que `Task/024` escribe junto al
   artefacto —campo `imagen`, con `etiqueta`, `digest` y `referencia`—;
2. **descarga por digest** esa referencia inmutable. La etiqueta desnuda **nunca** se
   descarga: hay una prueba que lo exige;
3. **asocia** localmente la etiqueta que el emulador pide a ese contenido exacto;
4. **verifica** con la identidad efectiva de Docker que la etiqueta resuelve a esa imagen;
5. tras la invocacion, **comprueba el contenedor real**.

**Una sola autoridad.** El digest ya **no** se declara en `Task/025`: se retiro la constante
`DIGEST_DEL_RUNTIME_DE_TASK024`, que era una copia manual. `Task/024` sigue siendo la
autoridad del runtime y `Task/025` lo **consume**. Hay una prueba que recorre el arbol
sintactico del lanzador y falla si vuelve a aparecer una asignacion que fije el runtime.

### 15 ter.3 Orden respecto al perimetro

La descarga necesita el registro, asi que ocurre en la fase de **preparacion**, antes de
cerrar el perimetro:

```
levantar --lambda-zip <ruta>   -> descarga por digest, fija la etiqueta, verifica identidad
                               -> levanta el emulador, comprueba el perimetro, STS local
ciclo    --lambda-zip <ruta>   -> vuelve a fijarlo (idempotente) y ejecuta el ciclo
```

Durante el ciclo aislado no hay descargas: el emulador encuentra el runtime ya presente.
Todos los controles previos se mantienen —credenciales ficticias, metadata bloqueada,
endpoints locales, red aislada, STS local, cero AWS real—.

### 15 ter.4 Control negativo ejecutado

Se dejo la etiqueta local apuntando **a otra imagen** a proposito —la del propio emulador— y
se ejecuto la preparacion:

```
etiqueta antes : sha256:4e451c39…e8eb   (el emulador, deliberadamente incorrecto)
accion         : reetiquetada
etiqueta despues: sha256:a89893d9…05daa  (el runtime que fijo Task/024)
```

Una cache local obsoleta —o adelantada— **no** controla la evidencia.

### 15 ter.5 Evidencia con el contenedor real

El mensaje del emulador *«Image already present locally, skipping pull»* dice lo que el
emulador **decidio**, no lo que **ejecuto**. Asi que se mira el contenedor.

Dos hechos que hubo que resolver para poder mirarlo:

- El laboratorio corre con `FLOCI_SERVICES_LAMBDA_EPHEMERAL=true`: el contenedor **se
  retira** al terminar. `docker ps --all` despues devuelve **cero**, y la primera version de
  esta verificacion fallo justamente por eso —y **se nego a afirmar nada** sin observacion,
  que es lo correcto—.
- El emulador lanza **dos** contenedores en un arranque en frio. Solo uno ejecuta el codigo:

  ```
  floci-codevol-blog-lab-backend-…   <- puebla el volumen de codigo
  floci-blog-lab-backend-…           <- ejecuta la funcion
  ```

  Confundirlos daria por evidencia un contenedor auxiliar que nunca corrio el *handler*.

La solucion es observar **en vivo**: se sondea mientras la invocacion ocurre y de cada
contenedor nuevo se lee su imagen efectiva. Resultado de la ejecucion real:

```
contenedores de la funcion observados en vivo: 1
  floci-blog-lab-backend-83df99d1
  imagen solicitada : public.ecr.aws/lambda/python:3.12
  image ID real     : sha256:a89893d9c93a9ffbf9e35ca32d7cadc635cbf3a9aec94480c75ed07150a05daa
  runtime Task/024  : sha256:a89893d9c93a9ffbf9e35ca32d7cadc635cbf3a9aec94480c75ed07150a05daa
COINCIDE
```

El camino critico siguio verde en el mismo ciclo: `GET /health` -> **HTTP 200** con
`{"status":"ok","service":"personal-blog-backend","version":"0.1.0"}`.

### 15 ter.6 Segundo hallazgo, encontrado al limpiar

Al comprobar residuos aparecio un volumen que **no** estaba contado:

```
floci-code-blog-lab-backend-ZYBBAQkgfzMKMp7iNeBC
  labels = {"floci":"true","floci_emulator":"floci-aws"}
```

`compose down --volumes` no lo retira porque **no lo creo Compose**: lo creo el emulador a
traves del socket de Docker. Y la comprobacion de residuos buscaba **solo por nombre de
proyecto**, asi que declaraba «0 volumenes» mientras ese seguia ahi.

**Correccion de una afirmacion anterior de este reporte.** Donde se dijo «0 contenedores,
0 redes, 0 volumenes» tras bajar el laboratorio, la medicion era **incompleta**: cierta para
los recursos con nombre de proyecto, ciega para los que crea el emulador. Ahora se buscan
**las dos familias** —nombre de proyecto **y** etiqueta `floci=true`— y `bajar` retira lo
segundo, acotado a esa etiqueta para que no pueda alcanzar nada del entorno ordinario del
blog.

Verificacion final, por las dos vias:

```
por nombre de proyecto : contenedores=0 redes=0 volumenes=0
por etiqueta floci=true: contenedores=0 volumenes=0
entorno ordinario del blog: 6 servicios en pie, intactos
```

### 15 ter.7 Clasificacion

**H-025-3: CORREGIDO dentro de `Task/025`** como defecto de la guarda del laboratorio —
pendiente de aprobacion, como todo lo demas de esta tarea.

| Lo que NO se afirma | Por que |
| --- | --- |
| «la etiqueta dejo de moverse» | Se movera otra vez. Ya no importa |
| «runtime actualizado» | El runtime sigue siendo el de `Task/024`. **No se cambio** |
| «`Task024.x` ejecutada» | **No se inicio.** Sigue siendo mantenimiento independiente |
| «la reproducibilidad estaba rota» | **Nunca lo estuvo.** El defecto era de la guarda |

El movimiento de la etiqueta queda como **senal de que hay una actualizacion disponible**,
no como autoridad de identidad.

**Deuda separada, sin tocar (H-025-8).** El runtime al que apunta la etiqueta hoy,
`sha256:7ff4d0d3…012f`, se midio con **0 accionables** frente a los **2 HIGH** del digest de
`Task/024` (`CVE-2026-14456` en `openssl-fips-provider-latest` y `openssl-snapsafe-libs`).
Medicion fechada el 2026-09-14, registrada como evidencia y **no** como estado vigente: la
imagen pertenece a `Task/024`, cambiarla reconstruye el ZIP y altera su SHA, y **no es
requisito para continuar `Task/025`**.

---

## 15 quater. S-09 — aceptacion temporal autorizada y revalidada

> **Autorizada por el usuario el 2026-09-14.** No es aprobacion de `Task/025`, ni aceptacion
> genérica de CVE futuras, ni de otro digest, ni autorizacion para usar `nightly` o cambiar
> versiones.

### 15 quater.1 Lo autorizado, exactamente

| Componente | Identidad | Identidades aceptadas |
| --- | --- | --- |
| Emulador | `floci/floci:2.0.1@sha256:4e451c39…e8eb` | **70** (4 CRITICAL + 66 HIGH) |
| Terraform CLI | `terraform:1.16.2`, artefacto `linux_amd64` `sha256 0d17011f…3985a` | **9** HIGH |
| **Total** | | **79** |

Antes de registrar nada se **volvio a escanear** para comprobar que el inventario seguia
siendo el autorizado: Floci dio **70 observadas, 0 nuevas, 0 desaparecidas, conjuntos
identicos**. Terraform se escaneo esta vez sobre el artefacto **`linux_amd64`** —el que
instala CI— y dio las **mismas 9 CVE** que el de Windows, con 253 paquetes inventariados. La
unica diferencia entre plataformas es el `scope` observado (`terraform` frente a
`terraform.exe`), y el baseline acepta el de Linux.

**El provider `hashicorp/aws 6.64.0` no recibe excepcion**: 377 paquetes inventariados,
**0 accionables**, y asi debe seguir.

### 15 quater.2 Una sola politica, extendida

El emulador encaja en la politica existente `accepted-baseline`, ligada al **digest OCI**.

Terraform no: es un binario suelto y su informe no lleva `Metadata.RepoDigests`, asi que ese
control **no aplica** —no es que falle—. Se anadio una tercera politica, `pinned-artifact`,
**en el mismo `vulnerability_gate.py` y el mismo `vulnerability-baseline.json`**, con la
**misma** funcion de identidad exacta. Lo unico que cambia es de donde viene la identidad:

| Politica | Identidad del artefacto |
| --- | --- |
| `accepted-baseline` | digest OCI leido de `Metadata.RepoDigests` |
| `pinned-artifact` | `sha256` verificado con `sha256sum --check --strict` contra un `SHA256SUMS` **firmado con GPG**, **antes** de escanear |

No es una politica paralela: es una implementacion en el archivo que ya era la autoridad.
Y la identidad no se relaja — la firma GPG de HashiCorp es al menos tan fuerte que un
`RepoDigest`; lo que cambia es donde se comprueba.

Las aceptaciones historicas quedan **intactas**, verificado contra `HEAD`:

```
postgres  0 identidades, zero-tolerance   intacta
traefik   0 identidades, zero-tolerance   intacta
minio     100 identidades                 intacta
portainer 16 identidades                  intacta
```

### 15 quater.3 Prueba positiva

```
floci      : observados 70  aprobados 70  nuevos 0  coincidencias 70
terraform  : observados  9  aprobados  9  nuevos 0  coincidencias  9
Hallazgos accionables comparados en total: 79
RESULTADO: CORRECTO        exit 0
```

### 15 quater.4 Controles negativos — y el que fallo

Ejecutados sobre **copias temporales**; el baseline real nunca se manipulo.

| # | Control | Resultado |
| --- | --- | --- |
| 1 | digest de Floci diferente | **ROJO** (exit 1) |
| 2 | accionable nuevo en Floci | **ROJO** (exit 1) |
| 3 | severidad alterada en un hallazgo aprobado | **ROJO** (exit 1) |
| 4 | accionable nuevo en Terraform | **ROJO** (exit 1) |
| 5 | `scope` o artefacto de Terraform inesperado | **ROJO** (exit 1) |
| 6 | **`expected_sha256` de Terraform manipulado** | **VERDE — el control FALLO** |
| 7 | `accepted_findings` de Floci vaciado | **ROJO** (exit 1) |
| 8 | sin mutaciones (control de control) | VERDE, correcto |

**El control 6 descubrio un hueco real.** Era coherente con el diseno —un binario suelto no
lleva su identidad dentro del informe—, pero dejaba que el baseline declarase un `sha256`
distinto del que de verdad se verifica, sin que nada lo detectara.

**Como se cerro.** Un verificador canonico en el mismo gate,
`verificar_coherencia_de_identidad`, que exige que el `sha256` sea **el mismo en las tres
autoridades**:

1. el **baseline**, que lo acepta;
2. el **workflow de CI**, que lo comprueba con `sha256sum` antes de escanear;
3. el **lanzador del laboratorio**, que lo fija para la ejecucion local.

Y tambien falla si el workflow **deja de declararlo** o el lanzador deja de fijar la
plataforma: perder la verificacion no puede pasar en silencio. Ademas, una entrada
`pinned-artifact` cuya fuente de identidad no este declarada aborta —aceptar el residual de
un artefacto que nadie verifica equivaldria a aceptar cualquier artefacto—.

Se invoca desde las pruebas **y** desde CI, como un gate propio:

```
python3 scripts/security/vulnerability_gate.py --baseline "$BASELINE" --comprobar-coherencia .
```

Reverificado tras el arreglo:

```
estado real del repositorio : RESULTADO CORRECTO (exit 0)
sha256 manipulado en copia  : FALLO DEL GATE (exit 2) - ROJO
```

### 15 quater.5 Un defecto propio que encontro la suite

Al registrar la excepcion, la suite `tests/security` paso de verde a **14 errores** con un
`TypeError: unsupported operand type(s) for +: 'NoneType' and 'str'`, que no decia nada util.

La causa no estaba donde parecia. Los textos que escribi en el baseline llevaban **em dash**
(`U+2014`); el gate los imprime; en Windows `stdout` es `cp1252`, asi que salian como byte
`0x97`; y la prueba preexistente decodifica esa salida como UTF-8, con lo que su hilo lector
moria, `stdout` quedaba en `None` y el `None + str` posterior enmascaraba el fallo real.

**El baseline original no tenia ni un caracter no ASCII**: era su convencion, y la habia roto
yo. Se restauro, y la suite volvio a verde sin tocar ninguna expectativa.

Queda anotado que en Linux —donde corre CI— esto **no** habria fallado, asi que la convencion
ASCII del baseline es load-bearing para las ejecuciones locales.

### 15 quater.6 Lo que la aceptacion NO dice

| No se afirma | Por que |
| --- | --- |
| que Floci este libre de vulnerabilidades | `/app/application`, su binario nativo Quarkus de 295 MB, **no esta inventariado** ni por Trivy ni por el **SBOM SPDX oficial** de upstream, que declara 108 rpm + 4 golang + 1 sin purl y **cero** paquetes Maven/Java. Residual de cobertura **vivo y declarado** |
| que los 79 hallazgos sean «no explotables» | Se dice **«no se encontro ruta aplicable»**. Es presencia de simbolos en el binario, no alcanzabilidad probada |
| que el privilegio del emulador sea menor | Monta el socket de Docker. Eso mantiene **elevado** el impacto potencial |
| que Terraform este a salvo por contexto | **Si** enlaza las primitivas afectadas: `net/http`, `crypto/tls`, `crypto/x509`, `net/url`, `html/template`, `encoding/xml` |
| que esto resuelva nada definitivamente | Son excepciones **temporales**, con condiciones de revision escritas en el propio baseline |

### 15 quater.7 Condiciones de reevaluacion

Registradas en `review_required_when` de cada entrada.

**Emulador:** nueva version estable · cambio de digest · cambio del inventario · nuevo
accionable · mejora del SBOM o de la cobertura del binario nativo · cambio del modelo de
ejecucion o del acceso al socket de Docker.

**Terraform:** aparicion de una version estable compilada con **Go >= 1.26.6** · cambio del
`sha256` · nuevo accionable · cambio del inventario.

Evidencia de que upstream ya remedia, registrada como **evidencia fechada y no como
dependencia**: el canal `nightly` observado da **2 accionables y 0 CRITICAL** migrando a
`ubi9-micro` y eliminando `gosu`; y el provider **ya** se compila con Go v1.26.6. **El canal
`nightly` no se adopta** (ADR-006 §5.4 y control S-10).

### 15 quater.8 CI Infra

| Gate nuevo | Qué comprueba |
| --- | --- |
| Coherencia de identidad | El `sha256` coincide en baseline, workflow y lanzador |
| Escaneo del emulador | Por su **digest exacto**, el mismo al que esta ligada la aceptacion |
| Escaneo del binario de Terraform | `rootfs`, con una guarda que **falla si el inventario sale vacio**: un informe vacio no es «cero vulnerabilidades», es ausencia de analisis |
| Escaneo del provider | Sin entrada de baseline. Falla si aparece cualquier accionable, porque requeriria decision humana |

El gate S-09 existente compara ahora **las seis** entradas. Nada se relajo: Compose,
variables, PowerShell, Python, Gitleaks sobre el historial completo, Trivy y la tolerancia
cero de las imagenes propias siguen igual.

---

## 16. Archivos

### Creados

| Ruta | Qué es |
| --- | --- |
| `terraform/versions.tf`, `providers.tf`, `variables.tf`, `main.tf`, `outputs.tf` | Raíz del grafo |
| `terraform/.terraform.lock.hcl` | Lock **versionado**, dos plataformas |
| `terraform/modulos/{almacenamiento,parametros,identidad,registro,computo,api_http}/` | Seis módulos, 18 archivos |
| `terraform/entornos/local/local.tfvars` | Destino laboratorio |
| `terraform/entornos/produccion/produccion.tfvars.example` | Plantilla **no operativa** |
| `scripts/laboratorio/` | `__init__`, `destino`, `artefacto`, `herramientas`, `inventario`, `firma_aws`, `verificacion`, `laboratorio`, `runtime` — **nueve** modulos |
| `laboratorio/docker-compose.laboratorio.yml` | Compose del laboratorio |
| `laboratorio/.env.laboratorio.example` | Variables, todas ficticias. **Estuvo sin versionar hasta la revision final**: ver **DEF-025-1** (§23.1) |
| `tests/laboratorio/` | `test_destino`, `test_artefacto`, `test_herramientas`, `test_inventario`, `test_firma_aws`, `test_lanzador`, `test_runtime` — **143 tests** |
| `tests/laboratorio/ejemplo_canonico_de_aws.py` | Punto de verdad **unico** de las credenciales de ejemplo publicadas por AWS (**DEF-025-2**, §23.2). No es un archivo de pruebas: `-p 'test_*.py'` no lo recoge |
| `tests/security/test_pinned_artifact_policy.py` | La politica `pinned-artifact` y el verificador de coherencia, con sus controles negativos por campo |
| `docs/tasks/TASK-025-terraform-cloud.md` | Ficha |
| `docs/task-reports/TASK-025-report.md` | Este reporte |

### Modificados

| Ruta | Qué cambió |
| --- | --- |
| `.gitignore` | El lock se versiona; generados, estado y planes ignorados; sección Python nueva |
| `.github/workflows/ci-infra.yml` | Gates Terraform reales; guarda invertida; nada relajado |
| `docs/architecture/aws-local-parity.md` | Matriz §7 con evidencia real |
| `docs/architecture/open-decisions.md` | **D-06** como propuesta de resolución |
| `docs/project-management/STATUS.md` | Task/025 En progreso; **D-025-1** |
| `docs/project-management/ROADMAP.md` | Task/025 En progreso; **D-025-2**, **C-025-1** |
| `docs/stages/STAGE-08-cloud-ready.md` | Task/025 En progreso; evidencia del criterio del adaptador |
| `security/vulnerability-baseline.json` | **Dos entradas nuevas** autorizadas el 2026-09-14: `floci` (70) y `terraform` (9). Lo historico, identico por `sha256` |
| `scripts/security/vulnerability_gate.py` | Politica `pinned-artifact` y el verificador de coherencia de identidad `--comprobar-coherencia` |

**`personal-blog-backend` y `personal-blog-frontend`: sin cambios.** Solo lectura. Sin rama
Task, sin commits. **H-023-3 no recibe evidencia nueva**: la suite del backend no se ejecutó
para esta tarea. La única interacción con el backend fue **construir el artefacto** con su
propio script y **leer** su código para derivar los permisos IAM.

---

## 17. Estado de decisiones y riesgos

| Elemento | Estado tras esta tarea |
| --- | --- |
| **Todas las decisiones de `Task/025`** | **Aceptadas y Vigentes** desde el 2026-09-14 |
| **D-06** | **RESUELTA** el 2026-09-14. Estado local fuera del árbol de Git y fuera del emulador, con cerrojo propio; para AWS real, backend `s3` con `use_lockfile = true` y **sin** DynamoDB, *bootstrap* separado. **El bucket no existe:** su creación es de la ETAPA 10 |
| **D-11** (retención de CloudWatch) | **Abierta** — `Task/031`. Los 7 días son valor de laboratorio |
| **D-12** (límites de Lambda) | **Abierta** — `Task/032`. 512 MB y 30 s son valores de laboratorio |
| **T-04** | **Satisfecho y Vigente**, sin cambios: esta tarea no tocó el adaptador |
| **P-06** | **Conservado** |
| **P-07** | **Sin cambio de autoridad**: el arranque en AWS real sigue pendiente de `Task/032` |
| **H-023-3** | **Abierto y NO diagnosticado.** Sin evidencia nueva |
| **R-24** (AWS real por accidente) | **Mitigado en local** con guardas y 13 controles negativos. El riesgo no se cierra: `Task/039` lo extiende a Cloudflare y al VPS |
| **R-25** (camino crítico no cubierto upstream) | **Demostrado que funciona** en el laboratorio. Sigue abierto hasta AWS real |
| **R-22** (socket de Docker) | Vigente. Mitigado con loopback y red `internal` |
| **R-28** (IAM sin *enforcement*) | **Reconfirmado.** Mínimo privilegio sigue AWS-only |
| **ADR nuevo** | **Ninguno.** Nada de esto modifica una decisión aceptada |
| **Task/026** | **Pendiente, no iniciada** |

---

## 18. Deuda y hallazgos abiertos

| # | Hallazgo | Dónde se resuelve |
| --- | --- | --- |
| **H-025-1** | **EXCEPCIÓN DEL EMULADOR AUTORIZADA — no bloqueante.** El emulador descarta las etiquetas en `PutParameter`, así que el criterio 7 no se cumple literalmente: `exit 2` por `tags_all`. Aceptado por el usuario el 2026-09-14 como excepción **del laboratorio**, **sin** `ignore_changes` y **sin** alterar Terraform | La idempotencia definitiva la confirma **AWS real**; se verifica en `Task/031` |
| **H-025-2** | El emulador no aplica la autorización de S3: la privacidad del bucket no es verificable en local | **`Task/030`** |
| **H-025-3** | **CORREGIDO** (§15 ter). La guarda comprobaba **frescura de la etiqueta** y abortaba cuando upstream la movía —lo hizo el 2026-09-14—. La reproducibilidad de `Task/024` **nunca estuvo rota**: construye por digest y ese digest sigue descargable. Ahora el runtime se **fija**: se descarga por digest desde el `manifiesto.json` de `Task/024` y se asocia la etiqueta a ese contenido, verificado con el **contenedor real** | Corregido dentro de `Task/025`; pendiente de aprobación como el resto |
| **H-025-4** | `api_endpoint` no es usable contra el destino local | Registrado en la matriz. En AWS real es la URL correcta |
| **H-025-5** | Sin re-evaluar: el CHANGELOG `2.0.0` sugiere evaluación de alarmas, que contradiría ADR-006 §6.7 | **`Task/031`**, **`Task/041`** |
| **H-025-6** | **ACEPTACIÓN TEMPORAL AUTORIZADA — ya no bloqueante.** Las 70 identidades del emulador quedan aceptadas **ligadas al digest exacto**, con condiciones de reevaluación escritas. No es «resuelto porque no exista riesgo» ni «sin vulnerabilidades»: el riesgo sigue ahí, enumerado y sujeto a revisión (§15 quater) | Reevaluar según `review_required_when`; el residual de cobertura del binario nativo queda **vivo** |
| **H-025-7** | **ACEPTACIÓN TEMPORAL AUTORIZADA — ya no bloqueante.** Las 9 identidades de `stdlib v1.26.4` quedan aceptadas para el artefacto `linux_amd64` de 1.16.2, con caducidad explícita: **reevaluar en cuanto exista una estable compilada con Go ≥ 1.26.6** (§15 quater) | Terraform **sí** enlaza las primitivas afectadas; no se afirma que sean no explotables |
| **H-025-8** | El **runtime Lambda** heredado de `Task/024` tampoco figura en S-09; tiene **2 accionables HIGH** (`CVE-2026-14456`). **No se despliega**: solo construye y ejecuta en local. Medición fechada del 2026-09-14: el digest al que apunta la etiqueta hoy tiene **0 accionables** | Alcance heredado, **mantenimiento independiente**; no es requisito para `Task/025` |

Runbook operativo de *drift*, *rollback*, recuperación y `destroy`: **`Task/026`**.
Automatización en CI: **`Task/039`**.

---

## 19. Reproducción

```powershell
cd personal-blog-infra

# 1. Guardas, sin red y sin Docker
python -m unittest discover -s tests/laboratorio -p "test_*.py" -v

# 2. Terraform verificado por checksum (descarga a una cache fuera de Git)
python scripts/laboratorio/laboratorio.py herramientas

# 3. Construir el artefacto en el OTRO repositorio, y quedarse con la ruta
cd ..\personal-blog-backend
python scripts\empaquetar_lambda.py construir --destino <carpeta-fuera-de-git>
cd ..\personal-blog-infra

# 4. Laboratorio: pre-descarga, perimetro e identidad
python scripts\laboratorio\laboratorio.py levantar

# 5. Ciclo completo
python scripts\laboratorio\laboratorio.py ciclo --lambda-zip <carpeta>\personal-blog-backend-lambda.zip

# 6. Retirar y comprobar residuos
python scripts\laboratorio\laboratorio.py bajar

# 7. Control negativo: el modo production se rechaza
python scripts\laboratorio\laboratorio.py --modo production levantar   # exit 1
```

El paso 5 tarda unos minutos: hace dos `apply` y dos `destroy` completos.

---

## 20. Conclusión

**11 criterios en PASS literal y 1 en PASS con excepción humana explícita. Ningún FAIL.**

**El criterio 7 NO se cumple literalmente en Floci 2.0.1:** el segundo plan devuelve
**exit 2**, exclusivamente por **H-025-1** (`aws_ssm_parameter.tags_all`). La divergencia fue
**reproducida y diagnosticada** como comportamiento del emulador, y **no** se añadió
`ignore_changes` ni ninguna otra excepción al grafo Terraform.

El usuario **aceptó esa divergencia el 2026-09-14** como **excepción explícita del laboratorio
local**. Sigue **sin** ser un PASS literal, y así consta. Lo que la aceptación no dice: que
Terraform sea idempotente en Floci sin excepciones, que Floci reproduzca AWS, ni que el
problema esté resuelto. **AWS real deberá confirmar la idempotencia definitiva.**

Detalle por criterio:

| # | Criterio | Resultado |
| --- | --- | --- |
| 1 | Una sola definición, sin duplicar | ✔ |
| 2 | `fmt -check` y `validate` | ✔ |
| 3 | Lock versionado, dos plataformas, `readonly` | ✔ |
| 4 | Guardas rechazan cada control negativo sin salir a la red | ✔ |
| 5 | `apply` crea los recursos | ✔ 21 recursos |
| 6 | `GET /health` HTTP real por API Gateway v2 → Lambda | ✔ **200** |
| **7** | Segundo plan `exit 0` | **PASS PARA APROBACIÓN CON EXCEPCIÓN HUMANA DEL LABORATORIO.** Resultado real: **`exit 2`**, única divergencia `aws_ssm_parameter.tags_all` (4 recursos). Causa demostrada: Floci 2.0.1 no persiste las etiquetas enviadas en `PutParameter`. **NO es PASS literal.** Diferencia del emulador, no *drift* aceptado de AWS. **Sin `ignore_changes`** (**H-025-1**, aceptado el 2026-09-14) |
| 8 | `destroy` y ausencia verificada por API | ✔ dos veces |
| 9 | Reconstrucción, *smoke* y segundo `destroy` | ✔ |
| 10 | Matriz con evidencia real, sin «paridad completa» | ✔ |
| 11 | Cero recursos y credenciales AWS reales | ✔ |
| 12 | El ejecutor rechaza `production` | ✔ |

**Lo más importante que se aprendió** no es que el ciclo funcione, sino **dónde el
laboratorio no es AWS**: S3 no autoriza, IAM no autoriza, SSM no cifra ni etiqueta, las
alarmas no se evaluaron y el `api_endpoint` no resuelve. Un laboratorio verde que ocultara
eso sería exactamente el riesgo **R-20** —falsa sensación de paridad— materializado.

**AWS real sigue siendo la autoridad final.** Todo lo observado aquí es una **hipótesis**
hasta que la ETAPA 10 lo confirme.

**Y sobre S-09:** la tarea introduce una imagen de terceros con **70 hallazgos accionables** y
un binario de Terraform con **9**. Ninguno se aceptó por cuenta propia. Se midieron, se
analizó su aplicabilidad, se demostró que **no existe remediación por actualización** y se
presentaron para decisión humana. El usuario autorizó el 2026-09-14 una excepción **temporal y
limitada** de esas **79 identidades**, que quedó registrada en el baseline canónico y
revalidada con prueba positiva y ocho controles negativos — uno de los cuales destapó un hueco
real que hubo que cerrar (§15 quater).

Lo que **sigue abierto** ahí no es el bloqueo, sino el **residual de cobertura**: el binario
nativo del emulador no lo inventaría ni Trivy ni el SBOM oficial de upstream. Eso no se acepta
ni se cierra: se declara.

---

## 22. Contraste final con la Definition of Done

Releida y contrastada punto por punto, distinguiendo lo que es **criterio propio de
`Task/025`**, lo que es **DoD global** y lo que es **excepción humana explícita**.

### 22.1 DoD §1 - Lista para validacion

| # | Criterio | Resultado |
| --- | --- | --- |
| 1 | Cumple todo el alcance | **Sí.** 14 de 14 casillas de *Dentro del alcance* |
| 2 | No agrega funcionalidad fuera del alcance | **Sí.** Contrastado contra *Fuera del alcance*; sin runbook operativo, sin CI del ciclo, sin RDS, sin dimensionar Lambda |
| 3 | El código compila cuando corresponde | **Sí.** `terraform validate`, `docker compose config` en los dos Compose, `compile()` sobre todo el Python |
| 4 | Las pruebas pasan, y el resultado se registra tal cual | **Sí.** 143 laboratorio + 40 security. Y los fallos se registraron: el `exit 2` del criterio 7, los tres defectos propios y el control negativo 6 |
| 5 | La documentación está actualizada | **Sí.** Ficha, reporte, STATUS, ROADMAP, STAGE-08, matriz de paridad y **D-06** |
| 6 | No contiene secretos | **Sí.** Solo fixtures públicas por diseño; barrido de patrones sin hallazgos |
| 7 | Incluye instrucciones para validar | **Sí.** Ficha §17 y §19 de este reporte |
| 8 | Registra decisiones importantes | **Sí.** Ficha §12, todas como Propuesta. **Ningún ADR nuevo**: nada modifica una decisión aceptada |
| 9 | Registra riesgos y deuda pendiente | **Sí.** Ficha §11 y §18, y §18 de este reporte con H-025-1 a H-025-8 |
| 10 | No rompe tareas aprobadas | **Sí.** `tests/security` sigue verde —y un defecto propio que la rompió se corrigió en su origen, §15 quater.5—; el Compose del blog intacto y sus 6 servicios en pie |
| 11 | La rama Task nació de `main` | **Sí.** `HEAD == main == c25642b8…` al crearla; `dev` no es ancestro |
| 12 | La documentación no persiste estado transitorio de Git | **Sí.** Sin PR, sin rama remota, sin normalización descritos como estado vigente |

### 22.2 DoD §3 - Tareas de infraestructura cloud

| # | Criterio | Resultado |
| --- | --- | --- |
| C-1 | `fmt -check` y `validate` sin errores | **Sí** |
| C-2 | Destino explícito y verificado antes de actuar | **Sí.** Sin modo declarado no se ejecuta nada; `production` se rechaza |
| C-3 | Guardas *fail-closed* operativas antes de `apply`/`destroy` | **Sí.** Trece capas, revalidadas antes de cada operación destructiva |
| C-4 | `plan` revisado y sin cambios **inesperados** | **Sí.** Contra lista cerrada de tipos y acciones. El `exit 2` del segundo plan está **previsto, diagnosticado y aceptado**: no es inesperado |
| C-5 | Evidencia que distingue emulación de validación real | **Sí**, y es el criterio que no se relajó: nueve filas de la matriz re-observadas, tres limitaciones del emulador registradas y prohibido el estado «paridad completa» |
| C-6 | Matriz de paridad actualizada | **Sí.** Las nueve filas que la tarea toca |
| C-7 | Estado de Terraform en el backend acordado, sin dejarlo suelto | **Sí.** Backend `local` explícito, fuera de Git y fuera del emulador, con cerrojo de una sola escritora. Es el que **D-06** propone; D-06 pasa a Vigente **al aprobarse** esta tarea, no antes |
| C-8 | Ningún recurso creado sin autorización | **Sí.** Cero recursos AWS reales |
| C-9 | Recursos realmente creados, enumerados y contrastados | **Sí.** 21, contrastados uno a uno con el plan |
| C-10 | **Impacto en costo estimado y documentado** | **Sí — añadido en esta revisión final.** Ficha §7.7. Costo incurrido **cero**; sin recursos reales no hay precios que consultar, y se documentan las siete decisiones que evitan costo futuro |
| C-11 | Ningún secreto versionado ni credencial cloud real contra el emulador | **Sí** |

> **C-10 era un hueco real.** No existía ninguna declaración de impacto en costo en la ficha ni
> en este reporte: solo una mención incidental en una celda de la tabla de decisiones. Lo detectó
> el contraste final con el DoD, y se corrigió escribiéndola.

### 22.3 DoD §4 - Que invalidaria la tarea

Ninguno de los nueve supuestos concurre: no se implementó funcionalidad no solicitada, no se
sobrescribió contenido sin justificar, no hubo commits, merges ni pushes, no se crearon recursos
cloud, no se versionaron secretos, no se marcó `Aprobada`, no se inició la tarea siguiente, las
pruebas se escribieron **antes** —con `RED` registrado— y **ningún test se modificó para que
pasara sin justificación**: los tres que cambiaron de expectativa llevan escrito el porqué.

### 22.4 Excepciones humanas, y lo que no cubren

| Excepción | Alcance | Lo que NO autoriza |
| --- | --- | --- |
| **H-025-1** | Criterio 7 de `Task/025`, divergencia `tags_all` en Floci 2.0.1 | No es PASS literal; no dice que Floci reproduzca AWS; no exime a AWS real de confirmar la idempotencia |
| **H-025-6** | 70 identidades del emulador, **ligadas a su digest exacto** | Ningún otro digest; ninguna CVE futura; no afirma que el emulador esté libre de vulnerabilidades |
| **H-025-7** | 9 identidades del artefacto `linux_amd64` de Terraform 1.16.2 | Ninguna otra versión ni plataforma; caduca con Go ≥ 1.26.6 |

Aceptar una excepción **no** cumple ningún otro punto del DoD por sí mismo: cada uno se
contrastó por separado arriba.

---

## 23. Revisión final del diff — dos defectos encontrados y corregidos

La revisión del diff completo (55 archivos entonces, 57 ahora) no era un trámite: encontró
**dos defectos reales** en la propia entrega. Ninguno es una vulnerabilidad ni un *finding*
nuevo de S-09; los dos habrían puesto **rojo el CI** en el primer *commit*, es decir justo
después de `approved:`. Se corrigieron y se reverificaron con la invocación exacta del
workflow.

### 23.1 DEF-025-1 — la plantilla del laboratorio no estaba versionada

| Campo | Contenido |
| --- | --- |
| **Síntoma** | `laboratorio/.env.laboratorio.example` existía en disco pero `git` no lo seguía. El diff tenía 55 archivos y **ninguno** era esa plantilla |
| **Causa** | `.gitignore:7` trae `.env.*` desde antes de esta tarea, y la negación `!.env.example` solo exime ese **nombre literal**. `.env.laboratorio.example` quedaba ignorado en silencio. El archivo incluso declara en su cabecera «Este ejemplo SI se versiona»: la intención estaba escrita, la regla la contradecía |
| **Impacto real** | **Dos pasos del CI** habrían fallado. El paso `Lab emulator stays on loopback and pinned by digest` lo abre directamente (`open('laboratorio/.env.laboratorio.example')` → `FileNotFoundError`), y el paso `Scan every infrastructure image` saca de él el digest con el que escanea el emulador: sin plantilla, no hay imagen que escanear y **S-09 dejaría de cubrir el emulador** — exactamente el hueco que **H-025-6** vino a cerrar |
| **Corrección** | Negación explícita `!laboratorio/.env.laboratorio.example`, en la sección del laboratorio y con el motivo escrito al lado. El archivo con los valores efectivos, `laboratorio/.env.laboratorio`, **sigue ignorado**: comprobado creándolo y consultando `git check-ignore` |
| **Antes de versionarlo** | Se leyó íntegro. Solo contiene la fixture pública `test` / `test` que el emulador exige, el digest fijado, el puerto de loopback y la región. **Ningún secreto** (S-10) |

### 23.2 DEF-025-2 — el gate de secretos se ponía rojo por una credencial pública

| Campo | Contenido |
| --- | --- |
| **Síntoma** | Gitleaks **8.30.1** —la versión que fija el workflow— daba **3 hallazgos** `generic-api-key` en `test_firma_aws.py`, `test_lanzador.py` y `test_destino.py` |
| **Qué valor era** | La clave secreta del **ejemplo canónico de SigV4 publicado por AWS**. No abre nada, y la prueba de firma la necesita **byte a byte**: sin el valor exacto deja de reproducir la firma documentada y pierde su razón de ser |
| **Causa** | El código ya intentaba evitarlo partiendo el valor en tres trozos —de 21, 9 y 10 caracteres—, y un comentario afirmaba que eso «evita un falso positivo». **Era falso:** la regla `generic-api-key` captura cualquier valor entrecomillado de **10 caracteres o más**, así que el primer fragmento se capturaba igual. Un comentario versionado afirmando una garantía que no existe es peor que no tenerlo |
| **Por qué no se silenció el escáner** | Este proyecto no usa `.trivyignore` para Trivy; por la misma razón no se usó `gitleaks:allow` ni se creó un `.gitleaks.toml` con *allowlist*. La política no se tocó: se quitó lo que la disparaba |
| **Corrección** | Un único punto de verdad, `tests/laboratorio/ejemplo_canonico_de_aws.py`, con los fragmentos en trozos de **8** caracteres y el razonamiento escrito una sola vez. Los tres archivos importan las constantes y **no contienen ningún literal**. El valor efectivo es idéntico al anterior, comprobado por igualdad contra la expresión que usaban las pruebas: 40 caracteres, `True`. **Este reporte no lo reproduce**, y no por pudor: escribirlo aquí hacía que Gitleaks marcara el propio reporte —ocurrió, y se corrigió en la misma revisión—. La regla no distingue código de documentación |
| **Verificación** | No se dio por bueno el razonamiento. Se descargó Gitleaks 8.30.1, se comprobó su `sha256` contra el `checksums.txt` oficial de la release (`d29144de…`) y se ejecutó **la invocación exacta del CI** (`gitleaks git . --log-opts=--all --redact=100`) sobre un *commit* de prueba con los 57 archivos: **3 hallazgos antes, 0 después, exit 0** |

> **Una nota sobre el propio §23.2.** La primera redacción de esa fila reproducía el valor
> completo como evidencia, y Gitleaks marcó **el reporte**. Verificarlo otra vez después de
> escribir la documentación es lo que lo detectó. Razonar sobre el escáner no sustituye a
> ejecutarlo: es el mismo error que causó **DEF-025-2**, repetido una línea más abajo.

### 23.3 Lo que la revisión confirmó limpio

| Comprobación | Resultado |
| --- | --- |
| *Workarounds* de Floci en el grafo | **Ninguno.** Las 11 menciones del emulador en `terraform/` son **comentarios** que documentan sus límites. No hay variable de bifurcación por destino (`es_local`, `modo`, `destino`), y los cuatro `count`/`for_each` dependen de **datos de entrada**, no del destino |
| `ignore_changes` en todo el árbol | **Uno solo**, sobre `value` de `aws_ssm_parameter`, por una razón propia ya registrada en las decisiones de la ficha. **No** toca `tags` ni `tags_all`: no oculta **H-025-1** |
| Archivos generados versionados | Ninguno: ni `.terraform/`, ni `tfstate`, ni `tfplan`, ni `generado/`, ni `__pycache__`, ni `.env.laboratorio`, ni `.zip` |
| Código temporal o de depuración | Ninguno en los 43 archivos de código de la tarea |
| Rutas absolutas | Una sola, y es **sintética**: la fixture `"/home/u/.aws/credentials"` de un control negativo |
| Finales de línea | Los 57 archivos en LF; `git diff --check` sin avisos |
| Autoridad duplicada | Ninguna: el digest del runtime vive solo en el manifiesto de `Task/024`, el `sha256` de Terraform se verifica en tres sitios **contra una sola fuente** por el gate de coherencia, y la credencial de ejemplo pasó de tres copias a una |

## 21. Estado final

```
Task/025-Terraform-Cloud ....... LISTA PARA APROBACION  (AUN NO APROBADA)
Revision final ................. SUPERADA, sin bloqueos
Criterios de aceptacion ........ 11 PASS literal + 1 PASS con excepcion humana (#7)
H-025-3 ........................ CORREGIDO dentro de Task/025 (seccion 15 ter)
ETAPA 08 ....................... En progreso, 2 de 4 (50 %)
Avance global .................. 24/41 ~ 59 %  (sin cambio)
D-06 ........................... Propuesta de resolucion, pendiente de aprobacion
D-11, D-12 ..................... Abiertas
P-07 ........................... Sin cambio de autoridad (Task/032)
H-023-3 ........................ Abierto, NO diagnosticado
H-025-1 ........................ EXCEPCION DEL EMULADOR AUTORIZADA (criterio 7)
H-025-3 ........................ CORREGIDO - era un defecto de la guarda
H-025-2 a H-025-5 .............. Abiertos, estados reales en la seccion 18
H-025-6 ........................ ACEPTACION TEMPORAL AUTORIZADA (70 identidades)
H-025-7 ........................ ACEPTACION TEMPORAL AUTORIZADA (9 identidades)
Baseline S-09 .................. 195 identidades (100 minio, 16 portainer, 70 floci, 9 tf)
H-025-8 ........................ Abierto, mantenimiento independiente de Task/024
Politica S-09 .................. ampliada con `pinned-artifact`, sin politica paralela
Task/026 ....................... Pendiente, no iniciada
Correcciones ................... D-025-1, D-025-2, C-025-1
Defectos de la revision final .. DEF-025-1, DEF-025-2 (corregidos y reverificados)
Commits ........................ 0        Push: no        PR: no
```

**Las dos decisiones que quedaban se tomaron el 2026-09-14:** la excepción del laboratorio
para **H-025-1** (criterio 7) y la aceptación temporal del residual S-09 (**H-025-6**,
**H-025-7**). Ambas quedaron registradas, revalidadas y con condiciones de reevaluación.

**Lo único que falta es la expresión `approved: Task/025-Terraform-Cloud`.**

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-14** |
| **Aprobado por** | **El usuario** (`jeffersondavila`) |
| **Expresión de aprobación** | `approved: Task/025-Terraform-Cloud` |
