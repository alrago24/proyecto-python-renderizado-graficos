import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno desde el archivo .env

BASE_URL = os.getenv("API_BASE_URL")  # Usa la variable de entorno o un valor por defecto

def _get_dataframe(endpoint: str) -> pd.DataFrame:
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url)
    response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
    return pd.DataFrame(response.json())  # Convierte la respuesta JSON a un DataFrame

def get_usuarios() -> pd.DataFrame:
    return _get_dataframe("api/usuarios")

def get_perfiles() -> pd.DataFrame:
    return _get_dataframe("api/perfiles")

def get_cursos() -> pd.DataFrame:
    return _get_dataframe("api/cursos")

def get_calificaciones() -> pd.DataFrame:
    return _get_dataframe("api/calificaciones")

def get_estudiantes() -> pd.DataFrame:
    return _get_dataframe("api/estudiantes")

def get_profesores() -> pd.DataFrame:
    return _get_dataframe("api/profesores")

def get_asistencias() -> pd.DataFrame:
    return _get_dataframe("api/asistencias")

def get_estudiante_curso() -> pd.DataFrame:
    return _get_dataframe("api/estudiante_curso")