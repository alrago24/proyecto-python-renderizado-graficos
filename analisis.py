from types import SimpleNamespace
import requests
import pandas as pd
from carga import (
    get_usuarios,
    get_perfiles,
    get_cursos,
    get_calificaciones,
    get_estudiantes,
    get_profesores,
    get_asistencias,
    )


# ─────────────────────────────────────────────
# Utilidades
# ─────────────────────────────────────────────
def limpiar_base_de_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Limpieza genérica aplicable a todos los DataFrames."""
    df = df.dropna(how="all").reset_index(drop=True)  # Elimina filas con valores faltantes
    df = df.dropna(axis=1, how="all")  # Elimina filas duplicadas

    # Convertir columnas con tipos no hashables (list, dict) a string
    # para que drop_duplicates pueda operar sobre ellas

    for col in df.columns:
        if df[col].apply(lambda v: isinstance(v, (list, dict))).any():
            df[col] = df[col].apply(str)

    # Eliminar filas duplicadas
    df = df.drop_duplicates().reset_index(drop=True)

    # Limpiar espacios en columnas de texto
    str_cols = df.select_dtypes(include=["object"]).columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    return df

def _convertir_fechas(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """Intenta convertir las columnas indicadas a datetime."""
    for col in columnas:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

# ─────────────────────────────────────────────
# Limpieza por entidad
# ─────────────────────────────────────────────

def limpiar_usuarios(df: pd.DataFrame) -> pd.DataFrame:
    df = limpiar_base_de_datos(df)
    # Descartar registros sin identificador
    if "id" in df.columns:
        df = df.dropna(subset=["id"])
    # Normalizar nombre a título si existe
    if "nombre" in df.columns:
        df["nombre"] = df["nombre"].str.title()
    return df.reset_index(drop=True)

def limpiar_perfiles(df: pd.DataFrame) -> pd.DataFrame:
    df = limpiar_base_de_datos(df)
    # Descartar registros sin identificador
    if "id" in df.columns:
        df = df.dropna(subset=["id"])
    return df.reset_index(drop=True)

def limpiar_cursos(df: pd.DataFrame) -> pd.DataFrame:
    df = limpiar_base_de_datos(df)
    # Descartar registros sin identificador
    if "id" in df.columns:
        df = df.dropna(subset=["id"])
    # Normalizar nombre a título si existe
    if "nombre" in df.columns:
        df["nombre"] = df["nombre"].str.title()
    if "descripcion" in df.columns:
        df["descripcion"] = df["descripcion"].str.strip()
    return df.reset_index(drop=True)

def limpiar_calificaciones(df: pd.DataFrame) -> pd.DataFrame:
    df = limpiar_base_de_datos(df)
    # Descartar registros sin identificador
    if "id" in df.columns:
        df = df.dropna(subset=["id"])
    # Asegurar que la nota sea numérica
    if "nota" in df.columns:
        df["nota"] = pd.to_numeric(df["nota"], errors="coerce")
    return df.reset_index(drop=True)

def limpiar_estudiantes(df: pd.DataFrame) -> pd.DataFrame:
    df = limpiar_base_de_datos(df)
    # Descartar registros sin identificador
    if "id" in df.columns:
        df = df.dropna(subset=["id"])
    # Normalizar nombre a título si existe
    if "nombreCompleto" in df.columns:
        df["nombreCompleto"] = df["nombreCompleto"].str.title()
    if "carrera" in df.columns:
        df["carrera"] = df["carrera"].str.strip()
    if "semestre" in df.columns:
        df["semestre"] = pd.to_numeric(df["semestre"], errors="coerce")
    return df.reset_index(drop=True)

def limpiar_profesores(df: pd.DataFrame) -> pd.DataFrame:
    df = limpiar_base_de_datos(df)
    # Descartar registros sin identificador
    if "id" in df.columns:
        df = df.dropna(subset=["id"])
    # Normalizar nombre a título si existe
    if "nombreCompleto" in df.columns:
        df["nombreCompleto"] = df["nombreCompleto"].str.title()
    if "departamento" in df.columns:
        df["departamento"] = df["departamento"].str.strip()
    if "especialidad" in df.columns:
        df["especialidad"] = df["especialidad"].str.strip()
    return df.reset_index(drop=True)

def limpiar_asistencias(df: pd.DataFrame) -> pd.DataFrame:
    df = limpiar_base_de_datos(df)
    # Descartar registros sin identificador
    if "id" in df.columns:
        df = df.dropna(subset=["id"])
    # Convertir fecha a datetime
    df = _convertir_fechas(df, ["fecha"])
    return df.reset_index(drop=True)


# ─────────────────────────────────────────────
# Funciones públicas fetch + limpieza
# ─────────────────────────────────────────────

def usuarios_limpios() -> pd.DataFrame:
    return limpiar_usuarios(get_usuarios())

def perfiles_limpios() -> pd.DataFrame:
    return limpiar_perfiles(get_perfiles())

def cursos_limpios() -> pd.DataFrame:
    return limpiar_cursos(get_cursos())

def calificaciones_limpias() -> pd.DataFrame:
    return limpiar_calificaciones(get_calificaciones())

def estudiantes_limpios() -> pd.DataFrame:
    return limpiar_estudiantes(get_estudiantes())

def profesores_limpios() -> pd.DataFrame:
    return limpiar_profesores(get_profesores())

def asistencias_limpias() -> pd.DataFrame:
    return limpiar_asistencias(get_asistencias())


# ─────────────────────────────────────────────
# Función principal
# ─────────────────────────────────────────────

def cargar_y_limpiar() -> SimpleNamespace:
    """
    Obtiene y limpia todos los DataFrames desde la API.
    Retorna un SimpleNamespace para acceder por atributo:
        datos = cargar_y_limpiar()
        datos.usuarios / datos.perfiles / ...
    """
    return SimpleNamespace(
        usuarios=usuarios_limpios(),
        perfiles=perfiles_limpios(),
        cursos=cursos_limpios(),
        calificaciones=calificaciones_limpias(),
        estudiantes=estudiantes_limpios(),
        profesores=profesores_limpios(),
        asistencias=asistencias_limpias()
    )