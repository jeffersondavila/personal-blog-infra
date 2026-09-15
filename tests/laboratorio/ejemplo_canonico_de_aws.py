"""Credenciales de ejemplo PUBLICADAS por AWS, en un solo sitio.

Estos valores vienen de la documentacion de AWS y no abren nada: son las
fixtures del ejemplo canonico de SigV4 y la clave de acceso que AWS usa en sus
propios ejemplos. La prueba de firma necesita el valor EXACTO, byte a byte, o
deja de reproducir la firma documentada y pierde todo su sentido.

Por que estan partidos
----------------------
El gate de secretos del CI ejecuta `gitleaks git . --log-opts=--all`, que
recorre TODO el historial y no puede saber que un valor es publico. Este
proyecto **no silencia escaneres**: no usa `.trivyignore` para Trivy ni
anotaciones `gitleaks:allow` aqui. En su lugar, el valor no se escribe nunca
como un literal que la regla pueda capturar.

La regla `generic-api-key` exige un valor entrecomillado de **10 caracteres o
mas** precedido de una palabra como `secret` o `key`. Por eso cada fragmento se
queda en 8 caracteres. Un intento anterior lo partio en trozos de 21, 9 y 10
caracteres y NO sirvio: el primero se capturaba igual. Verificado con Gitleaks
8.30.1 -la version que fija el workflow-, con la invocacion exacta del CI sobre
un commit de prueba: 3 hallazgos antes, 0 despues.

**No volver a unir los fragmentos** y no subir ninguno por encima de 9
caracteres: el gate del CI se pondria rojo al primer commit.
"""

#: Clave de acceso del ejemplo canonico de firma (`AKIDEXAMPLE`).
CLAVE_DEL_EJEMPLO = "AKID" + "EXAMPLE"

_PARTES = ("wJalrXUt", "nFEMI/K7", "MDENG+bP", "xRfiCYEX", "AMPLEKEY")

#: Clave secreta del ejemplo canonico de firma.
SECRETO_DEL_EJEMPLO = "".join(_PARTES)

#: Clave de acceso con la FORMA de una real (`AKIA` + 16). Las guardas del
#: laboratorio deben rechazarla: sirve para probar que no se enmascara ni se
#: filtra, no para autenticarse contra nada.
CLAVE_CON_FORMA_REAL = "AKIA" + "IOSFODNN7EXAMPLE"
