"""H-031-1A: el grupo por omision de la VPC no se gestiona y nada lo usa.

El usuario rechazo dar al rol operativo un permiso para etiquetar un grupo sin
etiquetas del proyecto y retirarle reglas. El aislamiento se preserva por NO USO:
ningun recurso del root de datos ni de sus modulos lo declara ni lo referencia,
y cada recurso que necesita grupo lleva uno explicito.

Control estatico sobre las fuentes. La guarda del plan (`check_plan.py`) repite
la comprobacion sobre la seccion `configuration` del plan real.
"""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FUENTES = [
    *sorted((RAIZ / "terraform-datos").glob("*.tf")),
    *sorted((RAIZ / "terraform" / "modulos" / "red").glob("*.tf")),
    *sorted((RAIZ / "terraform" / "modulos" / "base_de_datos").glob("*.tf")),
    # H-031-5: la ejecutora tambien lleva un grupo explicito (`sg-admin`) y nunca el por omision.
    *sorted((RAIZ / "terraform" / "modulos" / "ejecutor_privado").glob("*.tf")),
    # H-031-6: la salida de `export` sale de `sg-admin`, nunca del grupo por omision.
    *sorted((RAIZ / "terraform" / "modulos" / "exportacion").glob("*.tf")),
]


def sin_comentarios(texto):
    return "\n".join(re.sub(r"\s*#.*$", "", linea) for linea in texto.splitlines())


class GrupoPorOmisionSinUsoTests(unittest.TestCase):
    def test_hay_fuentes_que_revisar(self):
        self.assertGreaterEqual(len(FUENTES), 9)

    def test_ningun_recurso_ni_referencia_al_grupo_por_omision(self):
        for fuente in FUENTES:
            with self.subTest(fuente=fuente.name):
                codigo = sin_comentarios(fuente.read_text(encoding="utf-8"))
                self.assertNotIn("aws_default_security_group", codigo)
                self.assertNotIn("default_security_group_id", codigo)

    def test_rds_solo_lleva_sg_rds(self):
        codigo = sin_comentarios((RAIZ / "terraform/modulos/base_de_datos/main.tf").read_text(encoding="utf-8"))
        self.assertRegex(codigo, r"vpc_security_group_ids\s*=\s*\[var\.id_sg_rds\]")

    def test_los_tres_grupos_son_explicitos(self):
        codigo = sin_comentarios((RAIZ / "terraform/modulos/red/main.tf").read_text(encoding="utf-8"))
        grupos = re.findall(r'resource\s+"aws_security_group"\s+"(\w+)"', codigo)
        self.assertEqual(sorted(grupos), ["admin", "lambda", "rds"])

    def test_el_gateway_endpoint_no_lleva_grupos(self):
        codigo = sin_comentarios((RAIZ / "terraform/modulos/red/main.tf").read_text(encoding="utf-8"))
        bloque = re.search(r'resource\s+"aws_vpc_endpoint"\s+"s3"\s*\{(.*?)\n\}', codigo, re.S).group(1)
        self.assertIn('vpc_endpoint_type = "Gateway"', bloque)
        self.assertNotIn("security_group_ids", bloque)
        self.assertNotIn("subnet_ids", bloque)


if __name__ == "__main__":
    unittest.main()
