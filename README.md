# PI3_2026Q4 · Actividad 1: obtener y preparar datos desde Hugging Face

Carga el dataset [`aptologia/casa-vs-apartamento-precio-m2-ciudades-colombia-2026`](https://huggingface.co/datasets/aptologia/casa-vs-apartamento-precio-m2-ciudades-colombia-2026) (precio de oferta por m² de casas y apartamentos en 38 ciudades de Colombia, 2026; Aptología, CC BY 4.0), le aplica seis transformaciones y genera un reporte en `.txt`.

## Estructura

```
.github/workflows/ejecutar-actividad-1.yml   # Ejecuta el notebook en GitHub en cada push a main
src/
├── clases_po/
│   ├── __init__.py
│   ├── hf_loader.py      # Clase HFDatasetLoader: Hugging Face → DataFrame (y CSV opcional)
│   └── reportes.py       # Clase Reportes: DataFrame → reporte .txt
└── actividad1/
    ├── Actividad1_vivienda_colombia.ipynb   # Coordina las clases y transforma los datos
    ├── datos/vivienda_colombia.csv          # Datos originales (generado)
    └── reportes/vivienda_colombia.txt       # Reporte del DataFrame transformado (generado)
requirements.txt
```

## Flujo

```
HFDatasetLoader → DataFrame → 6 transformaciones → Reportes → reportes/vivienda_colombia.txt
```

Transformaciones: renombrar columnas, precios en millones de COP, columna `mas_barato`, columna `total_anuncios`, filtro de ciudades con al menos 1.000 anuncios y orden por `diferencia_pct`.

## Ejecución local

```bash
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
jupyter notebook src/actividad1/Actividad1_vivienda_colombia.ipynb
```

En Jupyter: **Kernel → Restart & Run All** y guarda el notebook.

## Ejecución automática en GitHub Actions

Cada push a `main` ejecuta el notebook en GitHub. Al terminar, el workflow sube en un commit `chore: actualizar resultados de Actividad 1 [skip ci]` el notebook con sus resultados, el CSV y el reporte `.txt`. También se puede lanzar a mano desde la pestaña **Actions → Ejecutar Actividad 1 → Run workflow**.

Para que el workflow pueda subir los resultados: **Settings → Actions → General → Workflow permissions → Read and write permissions**.
