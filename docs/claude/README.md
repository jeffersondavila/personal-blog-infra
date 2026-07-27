# Claude Code — Instrucciones del proyecto

## Propósito

[`PROJECT_INSTRUCTIONS.md`](PROJECT_INSTRUCTIONS.md) contiene las reglas
persistentes y versionadas del workspace multi-repositorio. Centraliza el flujo
de Git, los límites de aprobación, las responsabilidades de cada repositorio y
las decisiones vigentes que Claude Code debe respetar.

## Archivo raíz

El workspace contiene este archivo no versionado:

`C:\Users\jeffe\Downloads\Blog_Personal\CLAUDE.md`

Su contenido es:

```markdown
# Personal Blog Workspace

@personal-blog-infra/docs/claude/PROJECT_INSTRUCTIONS.md
```

- La raíz `Blog_Personal` no es un repositorio Git.
- El archivo raíz `CLAUDE.md` no se versiona.
- `PROJECT_INSTRUCTIONS.md` sí se versiona en `personal-blog-infra`.
- Las reglas globales no deben duplicarse completas en backend y frontend.

## Restauración

Si el archivo raíz `CLAUDE.md` se pierde, debe restaurarse manualmente en
`C:\Users\jeffe\Downloads\Blog_Personal\CLAUDE.md` con el contenido anterior.

## Verificación

En Claude Code puede utilizarse:

```text
/memory
```

Este comando permite comprobar qué archivos de memoria o instrucciones fueron
cargados. También debe confirmarse visualmente que aparecen el `CLAUDE.md` del
workspace y el documento importado
`personal-blog-infra/docs/claude/PROJECT_INSTRUCTIONS.md`.

## Extensiones futuras

Podrán existir archivos `CLAUDE.md` específicos dentro de backend, frontend o
infra, pero solamente para comandos y reglas propias de cada repositorio.

Las reglas globales de Git y aprobación deben continuar centralizadas en
`PROJECT_INSTRUCTIONS.md`.
