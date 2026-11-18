"""Pruebas de regresión: método Wenner."""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from procesar_wenner import resistividad_wenner, estadisticas_descriptivas, procesar

class TestWenner(unittest.TestCase):
    def test_ensayo_1(self):
        self.assertAlmostEqual(resistividad_wenner(6.2, 83.8), 3264.491758198226)
    def test_ensayo_2(self):
        self.assertAlmostEqual(resistividad_wenner(6.3, 83.7), 3313.1864443288673)
    def test_entrada_invalida(self):
        with self.assertRaises(ValueError):
            resistividad_wenner(0, 83.8)
    def test_estadisticos(self):
        e = estadisticas_descriptivas([83.8, 83.7])
        self.assertEqual(e["n"], 2)
        self.assertAlmostEqual(e["media"], 83.75)
        self.assertAlmostEqual(e["s_muestral"], math.sqrt(0.005))
    def test_transcripcion(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            data = procesar(output_dir=Path(folder))
            self.assertEqual(len(data), 2)
            self.assertAlmostEqual(data[0]["distancia_total_m"], 18.6)
            self.assertAlmostEqual(data[1]["distancia_total_m"], 18.9)

if __name__ == "__main__":
    unittest.main()
