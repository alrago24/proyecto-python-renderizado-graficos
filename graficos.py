"""
graficos.py

  HEADLESS → Python hace el ETL y retorna list[dict] (JSON-serializable).
             Spring Boot / React consumen los datos y renderizan el gráfico.

  PULL     → Python dibuja la imagen en RAM (BytesIO) y retorna bytes PNG.
             Evita I/O en disco en servidores concurrentes.
"""

from io import BytesIO
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd

from merge import (
    notas_por_curso,
    asistencia_vs_nota,
    rendimiento_por_profesor,
    tendencia_asistencia,
    perfil_estudiante,
    estudiantes_por_profesor,
    cursos_por_profesor,
    cursos_por_estudiante,
    cursos_con_mas_estudiantes,
)


# ══════════════════════════════════════════════════════════
# UTILIDADES INTERNAS
# ══════════════════════════════════════════════════════════

def _fig_to_bytes(fig: Figure) -> bytes:
    """Serializa una figura matplotlib a PNG en memoria RAM."""
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _col(df: pd.DataFrame, *candidatos: str) -> str:
    """Retorna la primera columna candidata que exista en el DataFrame."""
    for c in candidatos:
        if c in df.columns:
            return c
    raise KeyError(f"Ninguna de las columnas {candidatos} existe en el DataFrame.")


# ══════════════════════════════════════════════════════════
# MODELO HEADLESS  →  list[dict]
# ══════════════════════════════════════════════════════════

def headless_promedio_notas_por_curso() -> list[dict]:
    """Promedio de notas agrupado por curso."""
    df = notas_por_curso()
    col = _col(df, "nombre_cur", "nombre")
    resumen = (
        df.groupby(col)["nota"]
        .mean()
        .reset_index(name="promedio_nota")
        .sort_values("promedio_nota", ascending=False)
    )
    return resumen.to_dict(orient="records")


def headless_asistencia_vs_nota() -> list[dict]:
    """Porcentaje de asistencia y nota por estudiante y curso."""
    df = asistencia_vs_nota()
    return df.to_dict(orient="records")


def headless_rendimiento_por_profesor() -> list[dict]:
    """Promedio de notas de los estudiantes agrupado por profesor."""
    df = rendimiento_por_profesor()
    col = _col(df, "nombreCompleto", "nombreCompleto_prof", "nombre")
    resumen = (
        df.groupby(col)["nota"]
        .mean()
        .reset_index(name="promedio_nota")
        .sort_values("promedio_nota", ascending=False)
    )
    return resumen.to_dict(orient="records")


def headless_asistencia_por_curso() -> list[dict]:
    """Porcentaje promedio de asistencia agrupado por curso."""
    df = tendencia_asistencia()
    col = _col(df, "nombre_cur", "nombre")
    resumen = (
        df.groupby(col)["presente"]
        .mean()
        .reset_index(name="pct_asistencia")
        .sort_values("pct_asistencia", ascending=False)
    )
    return resumen.to_dict(orient="records")


def headless_perfil_estudiantes() -> list[dict]:
    """Promedio de notas y asistencia por cada estudiante."""
    df = perfil_estudiante()
    col = _col(df, "nombreCompleto_est", "nombreCompleto")
    return df[[col, "promedio_notas", "pct_asistencia"]].to_dict(orient="records")

def headless_estudiantes_por_profesor() -> list[dict]:
    """Cantidad de estudiantes agrupados por profesor."""
    df = estudiantes_por_profesor()
    resumen = (
        df.groupby("nombreCompleto_cur")["id_prof"]
        .count()
        .reset_index(name="total_estudiantes")
        .sort_values("total_estudiantes", ascending=False)
    )
    return resumen.to_dict(orient="records")


def headless_cursos_por_profesor() -> list[dict]:
    """Cantidad de cursos que imparte cada profesor."""
    df = cursos_por_profesor()
    col = _col(df, "nombreCompleto_prof", "nombreCompleto")
    resumen = (
        df.groupby(col)["nombre"]
        .count()
        .reset_index(name="total_cursos")
        .sort_values("total_cursos", ascending=False)
    )
    return resumen.to_dict(orient="records")


def headless_cursos_por_estudiante() -> list[dict]:
    """Cantidad de cursos en los que está matriculado cada estudiante."""
    df = cursos_por_estudiante()
    col = _col(df, "nombreCompleto_est", "nombreCompleto")
    resumen = (
        df.groupby(col)["nombre"]
        .count()
        .reset_index(name="total_cursos")
        .sort_values("total_cursos", ascending=False)
    )
    return resumen.to_dict(orient="records")


def headless_cursos_con_mas_estudiantes() -> list[dict]:
    """Cursos ordenados por cantidad de estudiantes matriculados."""
    df = cursos_con_mas_estudiantes()
    return df.to_dict(orient="records")


# ══════════════════════════════════════════════════════════
# MODELO PULL  →  bytes PNG
# ══════════════════════════════════════════════════════════

def pull_promedio_notas_por_curso() -> bytes:
    """Barras verticales: promedio de notas por curso."""
    df = pd.DataFrame(headless_promedio_notas_por_curso())
    col = df.columns[0]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df[col], df["promedio_nota"], color="steelblue")
    ax.set_title("Promedio de notas por curso")
    ax.set_xlabel("Curso")
    ax.set_ylabel("Promedio")
    plt.xticks(rotation=45, ha="right")
    return _fig_to_bytes(fig)


def pull_asistencia_vs_nota() -> bytes:
    """Dispersión: porcentaje de asistencia vs nota."""
    df = pd.DataFrame(headless_asistencia_vs_nota())

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df["pct_asistencia"], df["nota"], color="darkorange", alpha=0.6)
    ax.set_title("Asistencia vs Nota")
    ax.set_xlabel("% Asistencia")
    ax.set_ylabel("Nota")
    return _fig_to_bytes(fig)


def pull_rendimiento_por_profesor() -> bytes:
    """Barras horizontales: promedio de notas por profesor."""
    df = pd.DataFrame(headless_rendimiento_por_profesor())
    col = df.columns[0]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(df[col], df["promedio_nota"], color="seagreen")
    ax.set_title("Rendimiento por profesor")
    ax.set_xlabel("Promedio de notas")
    ax.invert_yaxis()
    return _fig_to_bytes(fig)


def pull_asistencia_por_curso() -> bytes:
    """Barras verticales: porcentaje de asistencia por curso."""
    df = pd.DataFrame(headless_asistencia_por_curso())
    col = df.columns[0]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df[col], df["pct_asistencia"], color="mediumpurple")
    ax.set_title("Asistencia por curso")
    ax.set_xlabel("Curso")
    ax.set_ylabel("% Asistencia")
    plt.xticks(rotation=45, ha="right")
    return _fig_to_bytes(fig)


def pull_perfil_estudiantes() -> bytes:
    """Dispersión: promedio de notas vs asistencia por estudiante."""
    df = pd.DataFrame(headless_perfil_estudiantes())
    col = df.columns[0]

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        df["pct_asistencia"],
        df["promedio_notas"],
        color="tomato",
        alpha=0.7,
    )
    for _, row in df.iterrows():
        ax.annotate(row[col], (row["pct_asistencia"], row["promedio_notas"]),
                    fontsize=7, alpha=0.8)
    ax.set_title("Perfil de estudiantes: notas vs asistencia")
    ax.set_xlabel("% Asistencia")
    ax.set_ylabel("Promedio de notas")
    return _fig_to_bytes(fig)

def pull_estudiantes_por_profesor() -> bytes:
    """Barras horizontales: total de estudiantes por profesor."""
    df = pd.DataFrame(headless_estudiantes_por_profesor())

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(df["nombreCompleto_cur"], df["total_estudiantes"], color="steelblue")
    ax.set_title("Estudiantes por profesor")
    ax.set_xlabel("Total estudiantes")
    ax.invert_yaxis()
    return _fig_to_bytes(fig)


def pull_cursos_por_profesor() -> bytes:
    """Barras horizontales: total de cursos por profesor."""
    df = pd.DataFrame(headless_cursos_por_profesor())
    col = df.columns[0]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(df[col], df["total_cursos"], color="darkorange")
    ax.set_title("Cursos por profesor")
    ax.set_xlabel("Total cursos")
    ax.invert_yaxis()
    return _fig_to_bytes(fig)


def pull_cursos_por_estudiante() -> bytes:
    """Barras verticales: total de cursos por estudiante."""
    df = pd.DataFrame(headless_cursos_por_estudiante())
    col = df.columns[0]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df[col], df["total_cursos"], color="seagreen")
    ax.set_title("Cursos por estudiante")
    ax.set_xlabel("Estudiante")
    ax.set_ylabel("Total cursos")
    plt.xticks(rotation=45, ha="right")
    return _fig_to_bytes(fig)


def pull_cursos_con_mas_estudiantes() -> bytes:
    """Barras horizontales: cursos con más estudiantes matriculados."""
    df = pd.DataFrame(headless_cursos_con_mas_estudiantes())

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(df["nombre"], df["total_estudiantes"], color="mediumpurple")
    ax.set_title("Cursos con más estudiantes matriculados")
    ax.set_xlabel("Total estudiantes")
    ax.invert_yaxis()
    return _fig_to_bytes(fig)

# ══════════════════════════════════════════════════════════
# PRUEBA LOCAL
# ══════════════════════════════════════════════════════════

_HEADLESS = {
    "promedio_notas_por_curso":      headless_promedio_notas_por_curso,
    "asistencia_vs_nota":            headless_asistencia_vs_nota,
    "rendimiento_por_profesor":      headless_rendimiento_por_profesor,
    "asistencia_por_curso":          headless_asistencia_por_curso,
    "perfil_estudiantes":            headless_perfil_estudiantes,
    "estudiantes_por_profesor":      headless_estudiantes_por_profesor,
    "cursos_por_profesor":           headless_cursos_por_profesor,
    "cursos_por_estudiante":         headless_cursos_por_estudiante,
    "cursos_con_mas_estudiantes":    headless_cursos_con_mas_estudiantes,
}
_PULL = {
    "promedio_notas_por_curso":      pull_promedio_notas_por_curso,
    "asistencia_vs_nota":            pull_asistencia_vs_nota,
    "rendimiento_por_profesor":      pull_rendimiento_por_profesor,
    "asistencia_por_curso":          pull_asistencia_por_curso,
    "perfil_estudiantes":            pull_perfil_estudiantes,
    "estudiantes_por_profesor":      pull_estudiantes_por_profesor,
    "cursos_por_profesor":           pull_cursos_por_profesor,
    "cursos_por_estudiante":         pull_cursos_por_estudiante,
    "cursos_con_mas_estudiantes":    pull_cursos_con_mas_estudiantes,
}


def probar_headless():
    """Imprime el JSON que se enviaría a Spring Boot / React."""
    print("\n" + "═" * 55)
    print("  MODELO HEADLESS  →  list[dict]")
    print("═" * 55)
    for nombre, fn in _HEADLESS.items():
        print(f"\n── {nombre} ──")
        try:
            datos = fn()
            print(json.dumps(datos, ensure_ascii=False, indent=2, default=str))
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")


def probar_pull(carpeta: str = "graficos_prueba"):
    """Guarda los PNG en una carpeta local para inspeccionarlos."""
    os.makedirs(carpeta, exist_ok=True)
    print("\n" + "═" * 55)
    print(f"  MODELO PULL  →  PNG en '{carpeta}/'")
    print("═" * 55)
    for nombre, fn in _PULL.items():
        ruta = os.path.join(carpeta, f"{nombre}.png")
        try:
            with open(ruta, "wb") as f:
                f.write(fn())
            print(f"  ✓  {ruta}")
        except Exception as e:
            print(f"  [ERROR] {nombre}: {type(e).__name__}: {e}")


if __name__ == "__main__":
    probar_headless()
    probar_pull()