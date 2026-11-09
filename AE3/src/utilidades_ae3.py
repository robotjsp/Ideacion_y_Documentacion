"""
utilidades_ae3.py
Funciones de apoyo para la AE3: comparar la estructura de un DataFrame antes y después
de transformarlo, registrar los controles de calidad, clasificar barrios dentro de su
ciudad y exportar tablas a CSV verificando que el archivo coincida con el DataFrame.
"""
from __future__ import annotations  # Permite usar anotaciones de tipo modernas (ej. str | None)

import unicodedata  # Para quitar tildes al normalizar textos
from pathlib import Path  # Manejo de rutas de archivos

import pandas as pd  # Librería para trabajar con DataFrames


def normalizar_texto(valor: str) -> str:  # Convierte un texto a una forma comparable
    """Devuelve el texto en minúsculas, sin tildes y sin espacios repetidos."""
    sin_tildes = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode()  # Quita tildes: "Medellín" -> "Medellin"
    return " ".join(sin_tildes.lower().split())  # Minúsculas y un solo espacio entre palabras


def comparar_estructura(  # Tabla de cambios por columna
    antes: pd.DataFrame,  # DataFrame original
    despues: pd.DataFrame,  # DataFrame transformado
    renombres: dict[str, str] | None = None,  # Diccionario nombre_original -> nombre_nuevo
) -> pd.DataFrame:  # Devuelve una fila por columna
    """Compara tipo y nulos de cada columna original con su versión final (siguiendo los renombres)."""
    renombres = renombres or {}  # Si no se indican renombres, usamos un diccionario vacío
    filas = []  # Aquí acumulamos una fila por columna
    usadas = set()  # Columnas finales que ya se relacionaron con una original
    for col in antes.columns:  # Recorremos las columnas originales
        final = renombres.get(col, col)  # Nombre que tiene la columna al final
        if final in despues.columns:  # Si sigue existiendo (con el mismo nombre o renombrada)...
            usadas.add(final)  # ...la marcamos como relacionada
            cambios = []  # Lista de cambios detectados
            if final != col:  # ¿Cambió el nombre?
                cambios.append("renombrada")
            if str(antes[col].dtype) != str(despues[final].dtype):  # ¿Cambió el tipo?
                cambios.append("tipo cambiado")
            estado = ", ".join(cambios) if cambios else "sin cambios"  # Texto del estado
        else:  # Si ya no existe...
            final, estado = "—", "eliminada (reemplazada o redundante)"  # ...la marcamos como eliminada
        filas.append({  # Fila de la comparación
            "columna_original": col,  # Nombre original
            "columna_final": final,  # Nombre final (o "—")
            "tipo_antes": str(antes[col].dtype),  # Tipo original
            "tipo_despues": str(despues[final].dtype) if final != "—" else "—",  # Tipo final
            "nulos_antes": int(antes[col].isna().sum()),  # Nulos originales
            "nulos_despues": int(despues[final].isna().sum()) if final != "—" else None,  # Nulos finales
            "estado": estado,  # Qué le pasó a la columna
        })
    for col in despues.columns:  # Columnas finales que no vienen de ninguna original
        if col not in usadas:  # Si no se relacionó con una original...
            filas.append({"columna_original": "—", "columna_final": col, "tipo_antes": "—",  # ...es una columna nueva
                          "tipo_despues": str(despues[col].dtype), "nulos_antes": None,
                          "nulos_despues": int(despues[col].isna().sum()), "estado": "nueva"})
    tabla = pd.DataFrame(filas)  # Convertimos a DataFrame
    return tabla.astype({"nulos_antes": "Int64", "nulos_despues": "Int64"})  # Enteros que admiten vacío


def resumen_dimensiones(antes: pd.DataFrame, despues: pd.DataFrame) -> pd.DataFrame:  # Filas, columnas y nulos totales
    """Tabla corta con filas, columnas y nulos totales antes y después."""
    return pd.DataFrame(  # Construimos la tabla de 3 filas
        {
            "antes": [len(antes), antes.shape[1], int(antes.isna().sum().sum())],  # Valores originales
            "despues": [len(despues), despues.shape[1], int(despues.isna().sum().sum())],  # Valores finales
        },
        index=["filas", "columnas", "valores nulos (total)"],  # Nombre de cada fila
    ).assign(diferencia=lambda t: t["despues"] - t["antes"])  # Columna con la diferencia


class BitacoraCalidad:  # Registro de cada control de calidad aplicado
    """Acumula los controles de calidad con su resultado y la decisión tomada."""

    def __init__(self) -> None:  # Constructor
        self.registros: list[dict] = []  # Lista vacía de controles

    def registrar(self, control: str, regla: str, afectados: int, decision: str) -> None:  # Agrega un control
        """Guarda un control: qué se revisó, con qué regla, cuántos registros afectó y qué se decidió."""
        self.registros.append({  # Agregamos el registro
            "paso": len(self.registros) + 1,  # Número consecutivo del control
            "control": control,  # Nombre del control
            "regla": regla,  # Regla o criterio aplicado
            "registros_afectados": int(afectados),  # Cantidad de registros afectados o detectados
            "decision": decision,  # Tratamiento aplicado y su justificación
        })

    def tabla(self) -> pd.DataFrame:  # Devuelve la bitácora como DataFrame
        """Devuelve todos los controles registrados como tabla."""
        return pd.DataFrame(self.registros)  # Convertimos la lista en DataFrame


def rango_relativo_en_ciudad(  # Clasifica cada barrio frente a los demás barrios de su ciudad
    df: pd.DataFrame,  # DataFrame con los datos
    columna: str,  # Columna numérica a clasificar (ej. arriendo)
    grupo: str = "ciudad",  # Columna que define el grupo (la ciudad)
    min_barrios: int = 8,  # Mínimo de barrios en la ciudad para que la clasificación tenga sentido
) -> pd.Series:  # Devuelve una serie de etiquetas
    """Asigna Bajo / Medio-bajo / Medio-alto / Alto según el cuartil del barrio dentro de su ciudad."""
    percentil = df.groupby(grupo)[columna].rank(pct=True)  # Posición relativa (0 a 1) del barrio dentro de su ciudad
    etiquetas = pd.cut(  # Convertimos la posición en 4 categorías
        percentil,  # Valores entre 0 y 1
        bins=[0, 0.25, 0.50, 0.75, 1.0],  # Cortes en los cuartiles
        labels=["Bajo", "Medio-bajo", "Medio-alto", "Alto"],  # Nombre de cada cuartil
        include_lowest=True,  # Incluye el valor más bajo en el primer grupo
    ).astype(str)  # Pasamos a texto para poder agregar otra etiqueta
    barrios_por_ciudad = df.groupby(grupo)[columna].transform("count")  # Cuántos barrios tiene la ciudad de cada fila
    return etiquetas.where(barrios_por_ciudad >= min_barrios, "Sin rango (pocos barrios)")  # Ciudades pequeñas no se clasifican


def exportar_csv_verificado(tabla: pd.DataFrame, ruta: str | Path) -> Path:  # Exporta y comprueba el CSV
    """Guarda la tabla en CSV (UTF-8), la vuelve a leer y verifica que coincida con el DataFrame."""
    ruta = Path(ruta)  # Convertimos la ruta a Path
    ruta.parent.mkdir(parents=True, exist_ok=True)  # Creamos la carpeta si no existe
    tabla.to_csv(ruta, index=False, encoding="utf-8")  # Escribimos el CSV sin la columna de índice
    releida = pd.read_csv(ruta, encoding="utf-8")  # Leemos el archivo recién escrito
    esperada = tabla.reset_index(drop=True).copy()  # Copia de la tabla original con índice limpio
    for col in esperada.columns:  # Recorremos cada columna para comparar valores, no formatos
        if isinstance(esperada[col].dtype, pd.api.extensions.ExtensionDtype) and pd.api.types.is_numeric_dtype(esperada[col]):  # Enteros con vacíos (Int64)
            esperada[col] = esperada[col].astype("float64")  # Al leer el CSV vuelven como decimales con NaN
        elif pd.api.types.is_datetime64_any_dtype(esperada[col]):  # Las fechas se escriben como texto AAAA-MM-DD
            esperada[col] = esperada[col].dt.strftime("%Y-%m-%d")  # Pasamos la fecha al mismo formato del CSV
            releida[col] = releida[col].astype(str)  # La releída ya es texto
        elif esperada[col].dtype == bool or str(esperada[col].dtype) in ("category", "object", "str", "string"):  # Columnas de texto o lógicas
            esperada[col] = esperada[col].astype(str)  # Comparamos como texto
            releida[col] = releida[col].astype(str)  # Igual en la tabla releída
    pd.testing.assert_frame_equal(  # Lanza un error si las tablas no coinciden
        esperada, releida, check_dtype=False, check_exact=False, rtol=1e-9  # Tolerancia mínima por decimales
    )
    return ruta  # Devolvemos la ruta del archivo verificado
