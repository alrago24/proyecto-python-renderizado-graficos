from fastapi import FastAPI
from fastapi.responses import Response
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

from graficos import (
headless_promedio_notas_por_curso,
headless_asistencia_vs_nota,
headless_rendimiento_por_profesor,
headless_asistencia_por_curso,
headless_perfil_estudiantes,
headless_estudiantes_por_profesor,
headless_cursos_por_profesor,
headless_cursos_por_estudiante,
headless_cursos_con_mas_estudiantes,
pull_promedio_notas_por_curso,
pull_asistencia_vs_nota,
pull_rendimiento_por_profesor,
pull_asistencia_por_curso,
pull_perfil_estudiantes,
pull_estudiantes_por_profesor,
pull_cursos_por_profesor,
pull_cursos_por_estudiante,
pull_cursos_con_mas_estudiantes,
)

app = FastAPI(title="Motor Analítico Privado")

# ════════════════════════════════════════════════════════
# ENDPOINTS HEADLESS  →  JSON  (React / Spring Boot)
# ════════════════════════════════════════════════════════

@app.get("/headless/promedio-notas-por-curso")
def headless_promedio_notas_por_curso_endpoint():
    return headless_promedio_notas_por_curso()

@app.get("/headless/asistencia-vs-nota")
def headless_asistencia_vs_nota_endpoint():
    return headless_asistencia_vs_nota()

@app.get("/headless/rendimiento-por-profesor")
def headless_rendimiento_por_profesor_endpoint():
    return headless_rendimiento_por_profesor()

@app.get("/headless/asistencia-por-curso")
def headless_asistencia_por_curso_endpoint():
    return headless_asistencia_por_curso()

@app.get("/headless/perfil-estudiantes")
def headless_perfil_estudiantes_endpoint():
    return headless_perfil_estudiantes()

@app.get("/headless/estudiantes-por-profesor")
def headless_estudiantes_por_profesor_endpoint():
    return headless_estudiantes_por_profesor()

@app.get("/headless/cursos-por-profesor")
def headless_cursos_por_profesor_endpoint():
    return headless_cursos_por_profesor()

@app.get("/headless/cursos-por-estudiante")
def headless_cursos_por_estudiante_endpoint():
    return headless_cursos_por_estudiante()

@app.get("/headless/cursos-con-mas-estudiantes")
def headless_cursos_con_mas_estudiantes_endpoint():
    return headless_cursos_con_mas_estudiantes()

# ════════════════════════════════════════════════════════