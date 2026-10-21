"""H-031-6: verificadores SCRAM-SHA-256 calculados por el operador (Task/031).

PostgreSQL guarda tal cual un PASSWORD que ya llega en formato SCRAM, y advierte que una contrasena en texto plano
puede quedar en el log del servidor. Con `log_statement = ddl` exportado a CloudWatch, la ejecutora solo recibe
verificadores: la contrasena de `blog_app` y `blog_migrate` nunca llega a la funcion ni al log de RDS.

El algoritmo se prueba contra el vector de RFC 7677: con la clave almacenada y la de servidor derivadas aqui, la
prueba del cliente y la firma del servidor del intercambio publicado deben reproducirse exactamente.
"""
import base64
import hashlib
import hmac
import re
import unittest

from scripts.terraform_datos import scram

#: Intercambio de ejemplo de RFC 7677 §3 (usuario `user`, contrasena `pencil`).
SAL_RFC = "W22ZaJ0SNY7soEsUEjb6gQ=="
CLIENTE_PRIMERO = "n=user,r=rOprNGfwEbeRWgbNEkqO"
SERVIDOR_PRIMERO = "r=rOprNGfwEbeRWgbNEkqO%hvYDpWUa2RaTCAfuxFIlj)hNlF$k0,s=W22ZaJ0SNY7soEsUEjb6gQ==,i=4096"
CLIENTE_FINAL_SIN_PRUEBA = "c=biws,r=rOprNGfwEbeRWgbNEkqO%hvYDpWUa2RaTCAfuxFIlj)hNlF$k0"
PRUEBA_RFC = "dHzbZapWIk4jUhN+Ute9ytag9zjfMHgsqmmiz7AndVQ="
FIRMA_RFC = "6rriTRBi23WpRR/wtup+mMhUZUn/dB5nLTJRsjl95G4="
FORMATO = re.compile(r"^SCRAM-SHA-256\$4096:[A-Za-z0-9+/]{22}==\$[A-Za-z0-9+/]{43}=:[A-Za-z0-9+/]{43}=$")


class VectorDeRfc7677(unittest.TestCase):
    def test_claves_reproducen_el_intercambio_publicado(self):
        sal = base64.b64decode(SAL_RFC)
        clave_cliente, almacenada, servidor = scram.claves("pencil", sal, 4096)
        mensaje = ",".join((CLIENTE_PRIMERO, SERVIDOR_PRIMERO, CLIENTE_FINAL_SIN_PRUEBA)).encode()
        firma_cliente = hmac.new(almacenada, mensaje, hashlib.sha256).digest()
        prueba = bytes(a ^ b for a, b in zip(clave_cliente, firma_cliente))
        self.assertEqual(base64.b64encode(prueba).decode(), PRUEBA_RFC)
        self.assertEqual(base64.b64encode(hmac.new(servidor, mensaje, hashlib.sha256).digest()).decode(), FIRMA_RFC)
        self.assertEqual(almacenada, hashlib.sha256(clave_cliente).digest())

    def test_verificador_con_la_sal_del_vector_tiene_el_formato_de_postgresql(self):
        # `pencil` no cumple la politica de contrasenas (test_solo_contrasenas_alfanumericas_largas): el algoritmo ya
        # quedo probado arriba con `claves`; aqui se prueba el formato con una contrasena admitida y la misma sal.
        contrasena = "Pencil" * 6
        v = scram.verificador(contrasena, sal=base64.b64decode(SAL_RFC))
        _, almacenada, servidor = scram.claves(contrasena, base64.b64decode(SAL_RFC), 4096)
        self.assertEqual(v, f"SCRAM-SHA-256$4096:{SAL_RFC}${base64.b64encode(almacenada).decode()}:"
                            f"{base64.b64encode(servidor).decode()}")
        self.assertRegex(v, FORMATO)


class Verificador(unittest.TestCase):
    CONTRASENA = "A" * 24 + "b7" * 12

    def test_formato_exacto_y_4096_iteraciones(self):
        self.assertRegex(scram.verificador(self.CONTRASENA), FORMATO)

    def test_sal_aleatoria_de_16_bytes(self):
        uno, dos = scram.verificador(self.CONTRASENA), scram.verificador(self.CONTRASENA)
        self.assertNotEqual(uno, dos)
        self.assertEqual(len(base64.b64decode(uno.split("$")[1].split(":")[1])), 16)

    def test_determinista_con_la_misma_sal(self):
        sal = bytes(range(16))
        self.assertEqual(scram.verificador(self.CONTRASENA, sal=sal), scram.verificador(self.CONTRASENA, sal=sal))

    def test_el_verificador_no_contiene_la_contrasena(self):
        self.assertNotIn(self.CONTRASENA, scram.verificador(self.CONTRASENA))

    def test_solo_contrasenas_alfanumericas_largas(self):
        for mala in ("corta1", "con espacio" * 4, "ñ" * 40, "x" * 31, "x" * 65, "", None, 7):
            with self.subTest(mala=repr(mala)[:20]):
                with self.assertRaisesRegex(ValueError, "CONTRASENA_NO_ADMITIDA"):
                    scram.verificador(mala)

    def test_sal_invalida_rechazada(self):
        for sal in (b"", b"x" * 15, "texto"):
            with self.subTest(sal=sal):
                with self.assertRaisesRegex(ValueError, "SAL_NO_ADMITIDA"):
                    scram.verificador(self.CONTRASENA, sal=sal)


if __name__ == "__main__":
    unittest.main()
