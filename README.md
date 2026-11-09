# Proyecto Integrador · Perfil de barrios para arrendar o comprar vivienda en Colombia

## Propósito

Crear un informe con el que las personas puedan perfilar fácilmente los barrios de una ciudad y presupuestar el valor de arrendar o comprar un inmueble, como base para plantear su búsqueda según sus necesidades. Puede aplicarse a varias ciudades de Colombia.

## Necesidad

Quien busca vivienda no tiene una referencia sencilla de cuánto cuesta cada barrio ni de cuánta oferta hay en arriendo y en venta. El proyecto busca:

1. Conocer, por barrio, el costo típico de arriendo y de venta.
2. Filtrar por barrio el costo y la cantidad de ofertas de arriendo y de venta.
3. Identificar los barrios con más ofertas.

## Dataset

- **Identificador:** `aptologia/arriendo-rentabilidad-por-barrio-colombia-2026`
- **Enlace:** https://huggingface.co/datasets/aptologia/arriendo-rentabilidad-por-barrio-colombia-2026
- **Configuración / split:** `rentabilidad_arriendo_venta_barrio` / `train` (dataset completo, sin muestra)
- **Revisión fijada:** `b752ea67e4c2615a723900d7654e3553e6a546c1` (garantiza las mismas cifras en cada ejecución)
- **Contenido:** 979 barrios de 13 ciudades; avisos y precio mediano de apartamentos en arriendo y en venta, al 5 de octubre de 2026
- **Autor y licencia:** Daniel Mauricio Pinzón Pineda / Aptología, CC BY 4.0 (permite publicar los datos derivados citando la fuente)
- **Acceso:** público; los notebooks lo descargan automáticamente y no requiere token.

## Estructura

```
AE2/                                          # Entrega AE2: exploración descriptiva
├── Soportes/documento_inicial.md
├── notebooks/AE2_exploracion_inmuebles.ipynb
└── resultados/resumen_dataframe.txt
AE3/                                          # Entrega AE3: transformación y enriquecimiento
├── documento/AE3_Informe_avance.docx         # Documento de avance (metodología, diccionario, resultados)
├── notebooks/AE3_transformacion_enriquecimiento.ipynb
├── src/utilidades_ae3.py                     # Bitácora de calidad, comparación antes/después, exportación verificada
├── datos/dataset_preparado.csv               # DataFrame final transformado y enriquecido (979 × 36)
└── resultados/
    ├── resumen_dataframe_final.txt           # Descripción del DataFrame final (se regenera en cada ejecución)
    └── tablas/
        ├── p1_costo_por_barrio.csv
        ├── p2_ofertas_por_barrio.csv
        ├── p2_predominio_por_ciudad.csv
        ├── p3_top10_oferta_por_ciudad.csv
        ├── p4_arrendar_vs_comprar.csv
        ├── p5_resumen_por_ciudad.csv
        ├── control_bitacora_calidad.csv
        └── control_comparacion_estructura.csv
src/
├── clases_po/                                # Clases reutilizables
│   ├── hf_loader.py                          # HFDatasetLoader: Hugging Face → DataFrame (admite revisión fija)
│   └── reportes.py                           # Reportes: DataFrame → .txt (admite metadatos)
└── actividad1/                               # Actividad 1 (dataset de casa vs. apartamento)
requirements.txt
```

## AE3: transformación y enriquecimiento

### Preguntas de negocio abordadas

| # | Pregunta | Tabla de resultados |
|---|---|---|
| P1 | ¿Cuánto cuesta arrendar y comprar en cada barrio? | `AE3/resultados/tablas/p1_costo_por_barrio.csv` |
| P2 | ¿Cuántas ofertas de arriendo y de venta tiene cada barrio y cuál predomina? | `p2_ofertas_por_barrio.csv`, `p2_predominio_por_ciudad.csv` |
| P3 | ¿Qué barrios concentran más oferta en cada ciudad? | `p3_top10_oferta_por_ciudad.csv` |
| P4 | ¿En qué barrios conviene más arrendar o comprar? | `p4_arrendar_vs_comprar.csv` |
| P5 | ¿Cómo se comparan las ciudades en costo y oferta? | `p5_resumen_por_ciudad.csv` |

Ajustes frente a AE2: se usa la **mediana** (el dataset no trae avisos individuales para calcular promedios) y se agregan P4 y P5 para cubrir el "valor del negocio" y la aplicación a otras ciudades del objetivo general.

### Transformaciones (15 controles registrados en `control_bitacora_calidad.csv`)

- Fechas de texto a fecha y unificación de `fecha_arriendo` y `fecha_venta` en `fecha_corte`.
- Verificación de tipos, duplicados (0), clave compuesta `ciudad_id` + `barrio_id` (85 identificadores de barrio se repiten entre ciudades).
- Limpieza y normalización de textos; nombre normalizado `barrio_clave`.
- Rangos válidos y coherencia de los cálculos de la fuente (0 diferencias); reglas de calidad `ok_todos` (≥ 30 avisos) y `ok_2alc` (≥ 20 avisos de 2 alcobas).
- Nulos estructurales (671 barrios) explicados y **no imputados**; 60 barrios con rentabilidad atípica (regla de Tukey) **marcados, no eliminados**.
- Precios de COP a millones de COP y columnas renombradas con su unidad.
- Se conservan los 979 barrios (los rankings usan los 620 con muestra suficiente).

### Enriquecimiento (15 variables nuevas)

`barrio_ciudad`, `periodo`, `arriendo_anual_mill_cop`, `anios_arriendo_equivalentes`, `rango_arriendo_ciudad`, `rango_venta_ciudad`, `banda_presupuesto_arriendo`, `banda_presupuesto_venta`, `total_avisos`, `pct_avisos_arriendo`, `predominio_oferta`, `participacion_oferta_ciudad_pct`, `puesto_oferta_ciudad`, `nivel_confianza`, `nivel_rentabilidad_2alc`. La fórmula y el significado de cada una están en el notebook y en el diccionario de datos del documento.

### Validaciones

Las participaciones suman 100 % por ciudad; los totales cuadran (979 barrios, 282.591 avisos); cada CSV se relee y se compara con su tabla; las rentabilidades por ciudad coinciden con la ficha oficial del dataset (Bogotá 7,0 %, Medellín 6,6 %).

## Pasos de ejecución

1. Crear y activar un entorno virtual, e instalar las dependencias:

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # En Windows: venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. Abrir la carpeta raíz del repositorio en VS Code (o ejecutar `jupyter notebook`).
3. Abrir el notebook y seleccionar como kernel el Python de `venv`:
   - AE2: `AE2/notebooks/AE2_exploracion_inmuebles.ipynb`
   - AE3: `AE3/notebooks/AE3_transformacion_enriquecimiento.ipynb`
4. Ejecutar todas las celdas (**Run All**). El notebook de AE3 descarga el dataset, aplica las transformaciones y el enriquecimiento, y regenera `AE3/datos/dataset_preparado.csv`, las tablas de `AE3/resultados/tablas/` y `AE3/resultados/resumen_dataframe_final.txt`. Todas las rutas son relativas a la raíz del repositorio.
5. Guardar el notebook con sus resultados y subir los cambios a GitHub.

## Actividad 1

`src/actividad1/Actividad1_vivienda_colombia.ipynb` carga el dataset `aptologia/casa-vs-apartamento-precio-m2-ciudades-colombia-2026`, le aplica seis transformaciones y guarda el reporte en `src/actividad1/reportes/vivienda_colombia.txt`.

## Fuente de datos

Pinzón Pineda, D. M. (2026). *Rentabilidad bruta del arriendo por barrio en Colombia: arriendo pedido frente a precio de venta pedido* [Conjunto de datos]. Aptología. https://doi.org/10.5281/zenodo.23246241 (CC BY 4.0).
