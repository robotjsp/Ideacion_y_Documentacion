"""Carga datasets de Hugging Face y, opcionalmente, los guarda en disco."""
from __future__ import annotations  # Permite usar anotaciones de tipo modernas (ej. str | None) en cualquier versión

from pathlib import Path  # Path maneja rutas de archivos de forma independiente del sistema operativo
from typing import Literal  # Literal restringe un tipo a un conjunto fijo de valores
from datasets import load_dataset  # Función que descarga datasets desde Hugging Face
import pandas as pd  # Librería para trabajar con DataFrames

FileType = Literal["csv", "json", "parquet", "xlsx"]  # Formatos de archivo en los que se puede guardar el DataFrame


class HFDatasetLoader:  # Clase encargada de conectarse a Hugging Face y entregar un DataFrame
    """Descarga un dataset de Hugging Face y lo devuelve como DataFrame.

    Args:
        dataset_name: Identificador del dataset en Hugging Face (ej. "usuario/nombre").
        config: Configuración del dataset, si tiene más de una.
        split: División que se desea cargar.
        token: Token de Hugging Face para datasets privados.
        cache_dir: Directorio de caché de Hugging Face.
        max_rows: Cantidad máxima de filas a cargar.
        filename: Ruta opcional donde se guardará el DataFrame.
        file_type: Formato opcional de salida: csv, json, parquet o xlsx.
            Si no se indica, se infiere desde la extensión de filename.
    """

    _SUPPORTED_FILE_TYPES = {"csv", "json", "parquet", "xlsx"}  # Conjunto de formatos válidos para guardar

    def __init__(  # Constructor: se ejecuta al crear el objeto
        self,  # Referencia al propio objeto
        dataset_name: str,  # Identificador del dataset (obligatorio)
        config: str | None = None,  # Subconjunto del dataset (opcional)
        split: str = "train",  # División a cargar; por defecto "train"
        token: str | None = None,  # Token para datasets privados (opcional)
        cache_dir: str | None = None,  # Carpeta de caché (opcional)
        max_rows: int | None = None,  # Límite de filas (opcional)
        filename: str | Path | None = None,  # Archivo donde guardar los datos (opcional)
        file_type: str | None = None,  # Formato del archivo de salida (opcional)
    ) -> None:  # El constructor no devuelve nada
        self.dataset_name = dataset_name  # Guardamos el identificador del dataset
        self.config = config  # Guardamos la configuración
        self.split = split  # Guardamos el split
        self.token = token  # Guardamos el token
        self.cache_dir = cache_dir  # Guardamos la carpeta de caché
        self.max_rows = max_rows  # Guardamos el límite de filas
        self.filename = Path(filename) if filename is not None else None  # Convertimos la ruta a Path si se indicó
        self.file_type = self._normalize_file_type(file_type)  # Validamos y normalizamos el formato de salida
        self.df: pd.DataFrame | None = None  # Aquí quedará el DataFrame después de llamar a load()

        if self.max_rows is not None and self.max_rows < 0:  # Si se indicó un límite negativo...
            raise ValueError("max_rows debe ser mayor o igual que cero.")  # ...lanzamos un error
        if self.file_type is not None and self.filename is None:  # Si hay formato pero no hay archivo...
            raise ValueError("filename es obligatorio cuando se indica file_type.")  # ...lanzamos un error

    def load(self) -> pd.DataFrame:  # Método principal: descarga y devuelve el DataFrame
        """Descarga el dataset, lo guarda si se configuró una salida y retorna el DataFrame."""
        dataset = load_dataset(  # Nos conectamos a Hugging Face y descargamos el dataset
            self.dataset_name,  # Qué dataset descargar
            self.config,  # Qué configuración (None = la única o la predeterminada)
            split=self.split,  # Qué división descargar
            token=self.token,  # Token, si el dataset es privado
            cache_dir=self.cache_dir,  # Dónde guardar la caché
        )
        if self.max_rows is not None:  # Si se pidió un límite de filas...
            dataset = dataset.select(range(min(self.max_rows, len(dataset))))  # ...nos quedamos solo con esas filas

        self.df = dataset.to_pandas()  # Convertimos el dataset de Hugging Face en DataFrame de pandas
        if self.filename is not None:  # Si se indicó un archivo de salida...
            self._save(self.df)  # ...guardamos el DataFrame en disco
        return self.df  # Devolvemos el DataFrame para usarlo en el notebook

    def info(self) -> dict[str, str | int | None]:  # Devuelve datos básicos del último DataFrame cargado
        """Devuelve información básica del último DataFrame cargado."""
        if self.df is None:  # Si todavía no se ha cargado nada...
            raise RuntimeError("Llama a load() primero.")  # ...avisamos que primero hay que llamar a load()
        return {  # Diccionario con la información
            "dataset": self.dataset_name,  # Nombre del dataset
            "config": self.config,  # Configuración usada
            "split": self.split,  # Split usado
            "filas": len(self.df),  # Cantidad de filas
            "columnas": len(self.df.columns),  # Cantidad de columnas
        }

    @classmethod  # Método de clase: no necesita un objeto creado para usarse
    def _normalize_file_type(cls, file_type: str | None) -> str | None:  # Valida y normaliza el formato
        if file_type is None:  # Si no se indicó formato...
            return None  # ...no hay nada que normalizar
        normalized = file_type.lower().lstrip(".")  # Pasamos a minúsculas y quitamos el punto inicial (".CSV" -> "csv")
        if normalized == "excel":  # Aceptamos "excel" como sinónimo...
            normalized = "xlsx"  # ...de "xlsx"
        if normalized not in cls._SUPPORTED_FILE_TYPES:  # Si el formato no es uno de los permitidos...
            supported = ", ".join(sorted(cls._SUPPORTED_FILE_TYPES))  # ...armamos la lista de formatos válidos
            raise ValueError(f"Tipo de archivo no soportado: {file_type}. Use: {supported}.")  # ...y lanzamos un error
        return normalized  # Devolvemos el formato normalizado

    def _save(self, df: pd.DataFrame) -> None:  # Guarda el DataFrame en el archivo configurado
        assert self.filename is not None  # Verificamos que exista una ruta de salida
        file_type = self.file_type or self._normalize_file_type(self.filename.suffix)  # Usamos el formato indicado o lo deducimos de la extensión
        if file_type is None:  # Si no se pudo determinar el formato...
            raise ValueError(  # ...lanzamos un error explicando qué hacer
                "No se pudo inferir el tipo de archivo. Indique file_type "
                "o use una extensión compatible en filename."
            )

        self.filename.parent.mkdir(parents=True, exist_ok=True)  # Creamos la carpeta de destino si no existe
        if file_type == "csv":  # Si el formato es CSV...
            df.to_csv(self.filename, index=False)  # ...guardamos como CSV sin la columna de índice
        elif file_type == "json":  # Si es JSON...
            df.to_json(self.filename, orient="records", force_ascii=False)  # ...una lista de registros, con tildes legibles
        elif file_type == "parquet":  # Si es Parquet...
            df.to_parquet(self.filename, index=False)  # ...guardamos en Parquet (requiere pyarrow)
        elif file_type == "xlsx":  # Si es Excel...
            df.to_excel(self.filename, index=False)  # ...guardamos en Excel (requiere openpyxl)
