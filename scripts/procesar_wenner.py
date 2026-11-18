"""Procesamiento reproducible del ensayo de cuatro picas (Wenner)."""
from __future__ import annotations
import argparse, csv, json, math
from dataclasses import asdict, dataclass
from pathlib import Path

@dataclass(frozen=True)
class WennerRecord:
    ensayo: str; a_m: float; b_m: float; resistencia_ohm: float; fuente: str; observacion: str

def _positive(value: str, field: str) -> float:
    try: number = float(value)
    except (TypeError, ValueError) as exc: raise ValueError(f"{field} debe ser numérico") from exc
    if not math.isfinite(number) or number <= 0: raise ValueError(f"{field} debe ser finito y mayor que cero")
    return number

def read_records(path: Path) -> list[WennerRecord]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle: rows = list(csv.DictReader(handle, skipinitialspace=True))
    required = {"ensayo", "a_m", "b_m"}
    if not rows or not required.issubset(rows[0]) or not ({"R_ohm", "resistencia_ohm"} & set(rows[0])): raise ValueError("CSV sin columnas requeridas")
    records, seen = [], set()
    for row in rows:
        ensayo = row["ensayo"].strip()
        if not ensayo or ensayo in seen: raise ValueError(f"ensayo vacío o repetido: {ensayo!r}")
        seen.add(ensayo); a = _positive(row["a_m"], "a_m"); b = _positive(row["b_m"], "b_m"); resistance = _positive(row.get("resistencia_ohm", row.get("R_ohm")), "R_ohm")
        if a <= 10 * b: raise ValueError(f"La aproximación exige a >> b; recibido a={a}, b={b}")
        source = row.get("fuente", row.get("fuente_archivo", "")).strip(); observation = row.get("observacion", "").strip()
        records.append(WennerRecord(ensayo, a, b, resistance, source, observation))
    return records

def apparent_resistivity(a_m: float, resistance_ohm: float) -> float:
    return 2 * math.pi * a_m * resistance_ohm

def finite_depth_factor(a_m: float, b_m: float) -> float:
    denominator = 1 + 2*a_m/math.sqrt(a_m**2 + 4*b_m**2) - 2*a_m/math.sqrt(4*a_m**2 + 4*b_m**2)
    return 2 / denominator

def process(records: list[WennerRecord]) -> dict:
    if len(records) < 2: raise ValueError("Se requieren al menos dos observaciones para estadística muestral")
    rows, resistances = [], []
    for record in records:
        rho = apparent_resistivity(record.a_m, record.resistencia_ohm); factor = finite_depth_factor(record.a_m, record.b_m)
        rows.append({**asdict(record), "longitud_total_m": 3*record.a_m, "rho_aparente_ohm_m": rho, "factor_profundidad": factor, "rho_corregida_ohm_m": rho*factor})
        resistances.append(record.resistencia_ohm)
    mean = sum(resistances)/len(resistances); sample_sd = math.sqrt(sum((r-mean)**2 for r in resistances)/(len(resistances)-1)); cv = 100*sample_sd/mean
    return {"metodo":"Wenner de cuatro picas", "ecuacion_simplificada":"rho_a = 2*pi*a*R", "relacion_geometrica":"L = 3*a", "filas":rows, "estadisticas":{"resistencia_media_ohm":mean, "desviacion_estandar_muestral_ohm":sample_sd, "coeficiente_variacion_descriptivo_pct":cv, "diferencia_absoluta_ohm":abs(resistances[1]-resistances[0]), "diferencia_relativa_vs_W01_pct":100*abs(resistances[1]-resistances[0])/resistances[0]}, "nota_interpretacion":"Las dos lecturas usan separaciones a diferentes; no constituyen un ensayo de repetibilidad."}

def write_outputs(data: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True); (output_dir/"wenner_resultados.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    with (output_dir/"wenner_resultados.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data["filas"][0])); writer.writeheader(); writer.writerows(data["filas"])
    lines = ["# Resultados procesados: Wenner de cuatro picas", "", "| Ensayo | a (m) | b (m) | R (Ω) | ρ simplificada (Ω·m) | ρ corregida (Ω·m) |", "|---|---:|---:|---:|---:|---:|"]
    lines += [f"| {r['ensayo']} | {r['a_m']:.2f} | {r['b_m']:.2f} | {r['resistencia_ohm']:.1f} | {r['rho_aparente_ohm_m']:.2f} | {r['rho_corregida_ohm_m']:.2f} |" for r in data["filas"]]
    s=data["estadisticas"]; lines += ["", f"Resistencia media: {s['resistencia_media_ohm']:.4f} Ω", f"Desviación estándar muestral: {s['desviacion_estandar_muestral_ohm']:.4f} Ω", f"CV descriptivo: {s['coeficiente_variacion_descriptivo_pct']:.4f} %", "", "Fuente: datos_procesados/wenner_4_picas_transcripcion.csv."]
    (output_dir/"wenner_resultados.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    stats = data["estadisticas"]
    (output_dir/"wenner_estadisticas.json").write_text(json.dumps({"R_ohm": {"n": len(data["filas"]), "media": stats["resistencia_media_ohm"], "s_muestral": stats["desviacion_estandar_muestral_ohm"], "cv_descriptivo_pct": stats["coeficiente_variacion_descriptivo_pct"]}, "cautela": data["nota_interpretacion"]}, ensure_ascii=False, indent=2), encoding="utf-8")

def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--input", type=Path, default=Path("datos_procesados/wenner_4_picas_transcripcion.csv")); parser.add_argument("--output-dir", type=Path, default=Path("resultados/wenner")); args=parser.parse_args(); write_outputs(process(read_records(args.input)), args.output_dir)

if __name__ == "__main__": main()
