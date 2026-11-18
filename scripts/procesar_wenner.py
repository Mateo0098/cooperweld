"""Cálculos reproducibles del método Wenner de 4 picas (INA-CENATE).
Ejecutar desde cualquier directorio con: python scripts/procesar_wenner.py
"""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "datos_procesados" / "wenner_4_picas_transcripcion.csv"
OUTPUT = ROOT / "resultados"

def resistividad_wenner(a_m: float, r_ohm: float) -> float:
    """Resistividad aparente aproximada, Ω·m, para picas poco profundas."""
    if not math.isfinite(a_m) or not math.isfinite(r_ohm) or a_m <= 0 or r_ohm < 0:
        raise ValueError("La separación debe ser positiva y R no negativa.")
    return 2 * math.pi * a_m * r_ohm

def estadisticas_descriptivas(values: list[float]) -> dict:
    if len(values) < 2:
        raise ValueError("Se requieren al menos 2 observaciones.")
    m = mean(values)
    s = stdev(values)
    return {"n": len(values), "media": m, "min": min(values),
            "max": max(values), "s_muestral": s,
            "cv_descriptivo_pct": 100 * s / m if m else None}

def procesar(input_path: Path = INPUT, output_dir: Path = OUTPUT) -> list[dict]:
    with input_path.open(newline="", encoding="utf-8-sig") as file:
        raw = list(csv.DictReader(file))
    if not raw:
        raise ValueError("No hay observaciones.")
    data = []
    for row in raw:
        a, b, r = float(row["a_m"]), float(row["b_m"]), float(row["R_ohm"])
        if b <= 0 or b >= a:
            raise ValueError("Profundidad o separación no válidas.")
        data.append({**row, "a_m": a, "b_m": b, "R_ohm": r,
                     "distancia_total_m": 3 * a,
                     "profundidad_relativa_pct": 100 * b / a,
                     "rho_aparente_ohm_m": resistividad_wenner(a, r)})
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "wenner_resultados.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)
    summary = {
        "R_ohm": estadisticas_descriptivas([x["R_ohm"] for x in data]),
        "rho_ohm_m": estadisticas_descriptivas([x["rho_aparente_ohm_m"] for x in data]),
        "cautela": "Con diferentes separaciones y n=2, s y CV no representan repetibilidad o incertidumbre."
    }
    (output_dir / "wenner_estadisticas.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return data

if __name__ == "__main__":
    for row in procesar():
        print(f'{row["ensayo"]}: a={row["a_m"]} m; R={row["R_ohm"]} Ω; '
              f'rho={row["rho_aparente_ohm_m"]:.2f} Ω·m')
