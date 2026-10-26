"""Generación de reportes de DataFrames."""
from __future__ import annotations  # Permite usar anotaciones de tipo modernas en cualquier versión

from pathlib import Path  # Path maneja rutas de archivos de forma independiente del sistema operativo

import pandas as pd  # Librería para trabajar con DataFrames


class Reportes:  # Clase que resume un DataFrame y lo exporta a un archivo .txt
    """Imprime y guarda un resumen legible de un DataFrame."""

    def generar_reporte(self, df: pd.DataFrame, titulo: str = "REPORTE DEL DATAFRAME") -> str:  # Arma el reporte como texto
        """Genera el contenido textual del reporte."""
        self._validar_dataframe(df)  # Verificamos que lo recibido sea un DataFrame
        numericas = df.select_dtypes(include="number")  # Seleccionamos solo las columnas numéricas
        texto = df.select_dtypes(exclude="number")  # Seleccionamos las columnas no numéricas (texto/categorías)
        lineas = [  # Lista de líneas del reporte, en orden
            titulo,  # Título del reporte
            "=" * 60,  # Línea separadora de 60 signos "="
            f"Filas: {len(df)}",  # Cantidad de filas
            f"Columnas: {len(df.columns)}",  # Cantidad de columnas
            f"Duplicados: {int(df.duplicated().sum())}",  # Cantidad de filas repetidas
            "",  # Línea en blanco
            "Columnas y tipos:",  # Encabezado de la sección de tipos
            *[f"- {columna}: {tipo}" for columna, tipo in df.dtypes.items()],  # Una línea por columna con su tipo
            "",  # Línea en blanco
            "Valores nulos por columna:",  # Encabezado de la sección de nulos
            *[f"- {columna}: {cantidad}" for columna, cantidad in df.isna().sum().items()],  # Nulos de cada columna
        ]

        if not numericas.empty:  # Si hay columnas numéricas...
            lineas += [  # ...agregamos sus estadísticas
                "",  # Línea en blanco
                "Estadísticas numéricas:",  # Encabezado de la sección
                numericas.describe().round(3).to_string(),  # Media, desviación, mínimo, cuartiles y máximo
            ]

        if not texto.empty:  # Si hay columnas de texto...
            lineas += ["", "Columnas categóricas:"]  # ...agregamos su sección
            for columna in texto.columns:  # Recorremos cada columna de texto
                unicos = texto[columna].nunique()  # Contamos cuántos valores distintos tiene
                if unicos <= 10:  # Si son pocos (ej. categorías)...
                    conteo = texto[columna].value_counts()  # ...contamos cuántas veces aparece cada valor
                    lineas.append(f"- {columna} ({unicos} valores distintos):")  # Nombre de la columna
                    lineas += [f"    {valor}: {n}" for valor, n in conteo.items()]  # Una línea por valor con su conteo
                else:  # Si son muchos (ej. nombres de ciudades)...
                    ejemplos = ", ".join(map(str, texto[columna].unique()[:5]))  # ...mostramos solo 5 ejemplos
                    lineas.append(f"- {columna} ({unicos} valores distintos). Ejemplos: {ejemplos}")  # Nombre + ejemplos

        return "\n".join(lineas) + "\n"  # Unimos todas las líneas con saltos de línea

    def imprimir_reporte(self, df: pd.DataFrame, titulo: str = "REPORTE DEL DATAFRAME") -> None:  # Muestra el reporte en pantalla
        """Imprime en la consola el reporte del DataFrame."""
        print(self.generar_reporte(df, titulo), end="")  # Generamos e imprimimos el texto

    def guardar_reporte(self, df: pd.DataFrame, ruta: str | Path, titulo: str = "REPORTE DEL DATAFRAME") -> Path:  # Guarda el reporte en .txt
        """Guarda el reporte en un archivo de texto y devuelve su ruta."""
        path = Path(ruta)  # Convertimos la ruta a un objeto Path
        path.parent.mkdir(parents=True, exist_ok=True)  # Creamos la carpeta de destino si no existe
        path.write_text(self.generar_reporte(df, titulo), encoding="utf-8")  # Escribimos el reporte en UTF-8 (respeta tildes)
        return path  # Devolvemos la ruta del archivo creado

    @staticmethod  # Método estático: no usa ni el objeto ni la clase
    def _validar_dataframe(df: pd.DataFrame) -> None:  # Comprueba que el parámetro sea un DataFrame
        if not isinstance(df, pd.DataFrame):  # Si no es un DataFrame...
            raise TypeError("df debe ser un pandas.DataFrame.")  # ...lanzamos un error claro
