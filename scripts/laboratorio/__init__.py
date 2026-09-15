"""Laboratorio AWS local del proyecto (`Task/025`).

Paquete de orquestacion y seguridad del **Modo B** descrito en
`docs/architecture/aws-local-parity.md`: prepara la herramienta Terraform, valida
el destino con guardas *fail-closed*, levanta el emulador, ejecuta el ciclo
`init` / `plan` / `apply` / pruebas / `destroy` y comprueba la ausencia de los
recursos al terminar.

Solo biblioteca estandar. Este repositorio no declara ninguna dependencia de
terceros para Python, y esta pieza no la introduce.
"""
