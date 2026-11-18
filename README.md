# Análisis Wenner — INA-CENATE

Este repositorio conserva los documentos originales de la actividad y añade un flujo reproducible, limitado al método de cuatro picas (Wenner), para estimar la resistividad aparente del terreno.

## Ejecución

```powershell
python scripts/procesar_wenner.py
python -m unittest discover -s pruebas -v
python scripts/generar_informe_wenner.py
```

Los resultados se escriben en `resultados/wenner/` y el informe en `entregables/`. El CSV de entrada conserva la procedencia de cada lectura. Las mediciones de otros métodos no se procesan.

## Modelo

El resultado principal usa `rho_a = 2*pi*a*R` y `L=3*a`. La corrección por profundidad finita se calcula aparte como sensibilidad. Las dos lecturas tienen separaciones diferentes y no se tratan como repetibilidad.
