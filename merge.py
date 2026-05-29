import pandas as pd
from analisis import (
    calificaciones_limpias,
    estudiantes_limpios,
    cursos_limpios,
    asistencias_limpias,
    profesores_limpios,
    usuarios_limpios,
    perfiles_limpios,
)

# ─────────────────────────────────────────────
# Carga de DataFrames limpios
# ─────────────────────────────────────────────

calificaciones = calificaciones_limpias()
estudiantes    = estudiantes_limpios()
cursos         = cursos_limpios()
asistencias    = asistencias_limpias()
profesores     = profesores_limpios()
usuarios       = usuarios_limpios()
perfiles       = perfiles_limpios()


# ─────────────────────────────────────────────
# Merges
# ─────────────────────────────────────────────

def notas_por_curso() -> pd.DataFrame:
    """
    Relaciona calificaciones con estudiantes y cursos.
    FK: calificaciones.estudianteId -> estudiantes.id
    FK: calificaciones.cursoId      -> cursos.id
    """
    base = pd.merge(
        calificaciones,
        estudiantes,
        left_on="estudianteId",
        right_on="id",
        how="left",
        suffixes=("_cal", "_est"),
    )
    return pd.merge(
        base,
        cursos,
        left_on="cursoId",
        right_on="id",
        how="left",
        suffixes=("", "_cur"),
    )


def asistencia_vs_nota() -> pd.DataFrame:
    """
    Relaciona el porcentaje de asistencia de cada estudiante con su nota por curso.
    FK: asistencias.estudianteId = calificaciones.estudianteId
    FK: asistencias.cursoId      = calificaciones.cursoId
    """
    asistencia_pct = (
        asistencias
        .groupby(["estudianteId", "cursoId"])["presente"]
        .mean()
        .reset_index(name="pct_asistencia")
    )
    return pd.merge(
        asistencia_pct,
        calificaciones[["estudianteId", "cursoId", "nota"]],
        on=["estudianteId", "cursoId"],
        how="left",
    )


def rendimiento_por_profesor() -> pd.DataFrame:
    """
    Relaciona cada profesor con los cursos que imparte y las calificaciones.
    FK: cursos.nombreProfesor -> profesores.nombreCompleto
    FK: calificaciones.cursoId -> cursos.id
    """
    base = pd.merge(
        cursos,
        profesores,
        left_on="nombreProfesor",
        right_on="nombreCompleto",
        how="left",
        suffixes=("_cur", "_prof"),
    )
    return pd.merge(
        base,
        calificaciones,
        left_on="id_cur",
        right_on="cursoId",
        how="left",
        suffixes=("", "_cal"),
    )


def tendencia_asistencia(frecuencia: str = "W") -> pd.DataFrame:
    """
    Relaciona asistencias con cursos y estudiantes agrupado por período.
    FK: asistencias.cursoId      -> cursos.id
    FK: asistencias.estudianteId -> estudiantes.id

    Args:
        frecuencia: 'W' semanal, 'M' mensual, 'D' diario (default 'W')
    """
    base = pd.merge(
        asistencias,
        cursos,
        left_on="cursoId",
        right_on="id",
        how="left",
        suffixes=("_asis", "_cur"),
    )
    base = pd.merge(
        base,
        estudiantes,
        left_on="estudianteId",
        right_on="id",
        how="left",
        suffixes=("", "_est"),
    )
    base["fecha"]   = pd.to_datetime(base["fecha"])
    base["periodo"] = base["fecha"].dt.to_period(frecuencia)
    return base


def perfil_estudiante(estudiante_id: int = None) -> pd.DataFrame:
    """
    Vista completa: estudiante + usuario + perfil + notas + asistencia.
    FK: estudiantes.usuarioId -> usuarios.id
    FK: perfiles.usuarioId    -> usuarios.id

    Args:
        estudiante_id: si se pasa, filtra un solo alumno; si no, retorna todos.
    """
    notas = (
        calificaciones
        .groupby("estudianteId")["nota"]
        .mean()
        .reset_index(name="promedio_notas")
    )
    asist = (
        asistencias
        .groupby("estudianteId")["presente"]
        .mean()
        .reset_index(name="pct_asistencia")
    )
    base = pd.merge(
        estudiantes,
        usuarios,
        left_on="usuarioId",
        right_on="id",
        how="left",
        suffixes=("_est", "_usr"),
    )
    base = pd.merge(
        base,
        perfiles,
        left_on="usuarioId",
        right_on="usuarioId",
        how="left",
        suffixes=("", "_per"),
    )
    base = pd.merge(
        base,
        notas,
        left_on="id_est",
        right_on="estudianteId",
        how="left",
    )
    base = pd.merge(
        base,
        asist,
        left_on="id_est",
        right_on="estudianteId",
        how="left",
    )
    if estudiante_id is not None:
        base = base[base["id_est"] == estudiante_id]
    return base

def estudiantes_por_profesor() -> pd.DataFrame:
    """
    Relaciona cada profesor con los estudiantes de sus cursos.
    FK: cursos.nombreProfesor  -> profesores.nombreCompleto
    FK: estudiantes.cursos     -> cursos.nombre
    """
    base = pd.merge(
        profesores,
        cursos,
        left_on="nombreCompleto",
        right_on="nombreProfesor",
        how="left",
        suffixes=("_prof", "_cur"),
    )
    return pd.merge(
        base,
        estudiantes,
        left_on="nombre",
        right_on="cursos",
        how="left",
        suffixes=("_cur", "_est"),
    )


def cursos_por_profesor() -> pd.DataFrame:
    """
    Relaciona cada profesor con los cursos que imparte.
    FK: cursos.nombreProfesor -> profesores.nombreCompleto
    """
    return pd.merge(
        profesores,
        cursos,
        left_on="nombreCompleto",
        right_on="nombreProfesor",
        how="left",
        suffixes=("_prof", "_cur"),
    )


def cursos_por_estudiante() -> pd.DataFrame:
    """
    Relaciona cada estudiante con los cursos en los que está matriculado.
    FK: estudiantes.cursos -> cursos.nombre
    """
    import ast

    df = estudiantes.copy()
    df["cursos"] = df["cursos"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )
    df = df.explode("cursos")

    return pd.merge(
        df,
        cursos,
        left_on="cursos",
        right_on="nombre",
        how="left",
        suffixes=("_est", "_cur"),
    )


def cursos_con_mas_estudiantes() -> pd.DataFrame:
    """
    Cuenta cuántos estudiantes están matriculados en cada curso,
    ordenado de mayor a menor.
    FK: estudiantes.cursos -> cursos.nombre
    """
    import ast

    df = estudiantes.copy()
    df["cursos"] = df["cursos"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )
    df = df.explode("cursos")

    base = pd.merge(
        df,
        cursos,
        left_on="cursos",
        right_on="nombre",
        how="left",
        suffixes=("_est", "_cur"),
    )
    return (
        base.groupby("nombre")["id_est"]
        .count()
        .reset_index(name="total_estudiantes")
        .sort_values("total_estudiantes", ascending=False)
    )