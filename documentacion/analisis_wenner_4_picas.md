# Mediciones de cuatro picas (Wenner) — INA-CENATE

**Análisis:** 18 de noviembre de 2026. **Responsable del informe:** Mateo Cerdas Barboza.

## Procedencia y transcripción

La fuente primaria del repositorio es `Informe con telurometro 1.docx`, sección «Método de 4 picas». El texto registra separación inicial de 6,2 m, profundidad de picas de 0,30 m e incremento de separación de 0,10 m. Las imágenes 7 y 8 del documento muestran lecturas de 83,8 Ω y 83,7 Ω, respectivamente. El promedio «84 Ω» indicado por el documento fuente es un redondeo y no una tercera lectura.

La tabla transcrita sin modificaciones arbitrarias está en `datos_procesados/wenner_4_picas_transcripcion.csv`. No mezclar otras técnicas de medición.

## Ecuaciones en LaTeX

$$
L_{P1-P4}=3a
$$

$$
\rho_a \approx 2\pi aR
$$

$$
\overline{x}=\frac{1}{n}\sum_{i=1}^{n}x_i
$$

$$
s_x=\sqrt{\frac{\sum_{i=1}^{n}(x_i-\overline{x})^2}{n-1}}
$$

## Datos y resultados

| Ensayo | a (m) | b (m) | R (Ω) | ρa aproximada (Ω·m) |
|---|---:|---:|---:|---:|
| W01 | 6,2 | 0,30 | 83,8 | 3264,49 |
| W02 | 6,3 | 0,30 | 83,7 | 3313,19 |

Media descriptiva de resistencia: 83,75 Ω. Media aritmética de resistividad aparente: 3288,84 Ω·m. Variación de W01 a W02: +1,61 % en a, −0,12 % en R y +1,49 % en ρa. **No interpretar estas diferencias como repetibilidad ni como incertidumbre instrumental**, porque las dos geometrías difieren y n = 2.

Los valores de resistividad con centésimas se muestran solo para auditoría aritmética y no indican tal precisión instrumental.

## Reproducción

```powershell
python scripts/procesar_wenner.py
python -m unittest discover -s pruebas -v
```

Salida: `resultados/wenner_resultados.csv` y `resultados/wenner_estadisticas.json`.

## Referencias

- Evidencia fuente: `Informe con telurometro 1.docx`, rama main de este repositorio.
- INA-CENATE, *Procedimiento para medición de resistencia de varilla Copperweld y tierra*, versión corregida de 2026, apartado de cuatro picas.
- Fluke, *Soil Resistivity Measurement*: https://www.fluke.com/en-us/learn/blog/grounding/soil-resistivity
- ASTM G57-20 (referencia metodológica, no certificación de conformidad): https://store.astm.org/standards/g57
