# Auditoría del análisis Wenner de cuatro picas

## Alcance y procedencia

Este análisis se limita al método de cuatro picas en arreglo Wenner. La fuente transcrita es `datos_procesados/wenner_4_picas_transcripcion.csv`, extraída de `Informe con telurometro 1.docx`. Las imágenes finales del documento (`word/media/image7.png` e `image8.png`) muestran, respectivamente, 83,8 Ω y 83,7 Ω en la pantalla del telurómetro. Las demás lecturas de los documentos originales corresponden a otros métodos y no se incorporan.

## Geometría y modelo

Para cuatro electrodos igualmente espaciados se usa, en la aproximación de picas poco profundas, `\(\rho_a = 2\pi aR\)`. La longitud entre la primera y la última pica es `\(L=3a\)`. En ambos registros `b/a` es menor que 0,05; se documenta la aproximación como adecuada para este análisis didáctico, sin presentarla como validación metrológica del terreno.

Como sensibilidad, el script también calcula separadamente:

`\[\rho_{a,c}=\frac{4\pi aR}{1+\frac{2a}{\sqrt{a^2+4b^2}}-\frac{2a}{\sqrt{4a^2+4b^2}}}.\]`

No se mezclan ambos modelos en un mismo promedio.

## Resultados verificados

| Ensayo | a (m) | b (m) | R (Ω) | ρ simplificada (Ω·m) | ρ corregida (Ω·m) |
|---|---:|---:|---:|---:|---:|
| W01 | 6,2 | 0,30 | 83,8 | 3264,49 | 3277,82 |
| W02 | 6,3 | 0,30 | 83,7 | 3313,19 | 3326,29 |

Resistencia media: **83,7500 Ω**. Desviación estándar muestral: **0,0707 Ω**. Coeficiente de variación descriptivo: **0,0844 %**. Diferencia absoluta: **0,1000 Ω**; diferencia relativa respecto de W01: **0,1193 %**.

Las dos observaciones tienen separaciones diferentes; por tanto, no se describen como repetibilidad ni se calculan intervalos de confianza.

## Limitaciones

La evidencia permite verificar las lecturas de pantalla y la separación declarada, pero no sustituye una bitácora metrológica completa (calibración, incertidumbre, resistividad estratificada, alineación exacta y homogeneidad del suelo). La corrección de profundidad se ofrece como sensibilidad, no como resultado principal.
