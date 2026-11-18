import csv, json, tempfile, unittest
from pathlib import Path
from scripts.procesar_wenner import apparent_resistivity, finite_depth_factor, process, read_records, write_outputs

ROOT = Path(__file__).parents[1]
CSV = ROOT / "datos_procesados" / "wenner_4_picas_transcripcion.csv"

class WennerTests(unittest.TestCase):
    def test_transcripcion_y_resultados(self):
        data = process(read_records(CSV)); self.assertEqual([r["ensayo"] for r in data["filas"]], ["W01", "W02"])
        self.assertAlmostEqual(data["filas"][0]["rho_aparente_ohm_m"], 3264.491758, places=5)
        self.assertAlmostEqual(data["filas"][1]["rho_aparente_ohm_m"], 3313.186444, places=5)
        self.assertAlmostEqual(data["estadisticas"]["resistencia_media_ohm"], 83.75)
        self.assertAlmostEqual(data["estadisticas"]["desviacion_estandar_muestral_ohm"], 0.070710678, places=6)
        self.assertAlmostEqual(data["estadisticas"]["coeficiente_variacion_descriptivo_pct"], 0.08443066, places=5)

    def test_formulas_y_dimensiones(self):
        self.assertAlmostEqual(apparent_resistivity(1, 1), 2*3.141592653589793)
        self.assertEqual(process(read_records(CSV))["filas"][0]["longitud_total_m"], 18.6)
        self.assertGreater(finite_depth_factor(6.2, 0.3), 1)

    def test_rechaza_valores_invalidos(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.csv"; path.write_text("ensayo,a_m,b_m,resistencia_ohm,fuente,observacion\nX,6.2,0.30,-1,s,o\n", encoding="utf-8")
            with self.assertRaises(ValueError): read_records(path)

    def test_exportaciones(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp); write_outputs(process(read_records(CSV)), out)
            self.assertTrue((out/"wenner_resultados.json").exists())
            with (out/"wenner_resultados.csv").open(encoding="utf-8") as handle: self.assertEqual(len(list(csv.DictReader(handle))), 2)
            self.assertEqual(len(json.loads((out/"wenner_resultados.json").read_text(encoding="utf-8"))["filas"]), 2)

if __name__ == "__main__": unittest.main()
