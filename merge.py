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
# Merges (Loaded Dynamically for Real-Time Sync)
# ─────────────────────────────────────────────

def notas_por_curso() -> pd.DataFrame:
    """
    Relaciona calificaciones con estudiantes y cursos.
    FK: calificaciones.estudianteId -> estudiantes.id
    FK: calificaciones.cursoId      -> cursos.id
    """
    calificaciones = calificaciones_limpias()
    estudiantes    = estudiantes_limpios()
    cursos         = cursos_limpios()
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
    asistencias    = asistencias_limpias()
    calificaciones = calificaciones_limpias()
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
    cursos         = cursos_limpios()
    profesores     = profesores_limpios()
    calificaciones = calificaciones_limpias()
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
    asistencias    = asistencias_limpias()
    cursos         = cursos_limpios()
    estudiantes    = estudiantes_limpios()
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
    calificaciones = calificaciones_limpias()
    asistencias    = asistencias_limpias()
    estudiantes    = estudiantes_limpios()
    usuarios       = usuarios_limpios()
    perfiles       = perfiles_limpios()
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
    profesores     = profesores_limpios()
    cursos         = cursos_limpios()
    estudiantes    = estudiantes_limpios()
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
    profesores     = profesores_limpios()
    cursos         = cursos_limpios()
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
    estudiantes    = estudiantes_limpios()
    cursos         = cursos_limpios()

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
    Cuenta cuántos estudiantes están asociados a cada curso,
    combinando matrícula formal (campo cursos), calificaciones
    y asistencias para reflejar datos en tiempo real.
    Ordenado de mayor a menor.
    """
    import ast
    estudiantes    = estudiantes_limpios()
    cursos         = cursos_limpios()
    calificaciones = calificaciones_limpias()
    asistencias    = asistencias_limpias()

    # Mapeo curso id → nombre para las fuentes 2 y 3
    curso_id_nombre = cursos[["id", "nombre"]].copy()

    pares = []  # DataFrames con columnas [est_id, curso_nombre]

    # ── Fuente 1: Matrícula formal (campo "cursos" del estudiante) ──
    est = estudiantes.copy()
    est["cursos"] = est["cursos"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )
    est = est.explode("cursos").dropna(subset=["cursos"])
    if not est.empty:
        pares.append(
            est[["id", "cursos"]]
            .rename(columns={"id": "est_id", "cursos": "curso_nombre"})
        )

    # ── Fuente 2: Calificaciones registradas ──
    if not calificaciones.empty and "estudianteId" in calificaciones.columns and "cursoId" in calificaciones.columns:
        cal = (
            calificaciones[["estudianteId", "cursoId"]]
            .drop_duplicates()
            .merge(curso_id_nombre, left_on="cursoId", right_on="id", how="inner")
        )
        if not cal.empty:
            pares.append(
                cal[["estudianteId", "nombre"]]
                .rename(columns={"estudianteId": "est_id", "nombre": "curso_nombre"})
            )

    # ── Fuente 3: Asistencias registradas ──
    if not asistencias.empty and "estudianteId" in asistencias.columns and "cursoId" in asistencias.columns:
        asi = (
            asistencias[["estudianteId", "cursoId"]]
            .drop_duplicates()
            .merge(curso_id_nombre, left_on="cursoId", right_on="id", how="inner")
        )
        if not asi.empty:
            pares.append(
                asi[["estudianteId", "nombre"]]
                .rename(columns={"estudianteId": "est_id", "nombre": "curso_nombre"})
            )

    # Si no hay datos de ninguna fuente
    if not pares:
        return pd.DataFrame(columns=["nombre", "total_estudiantes"])

    # Unión de todas las fuentes sin duplicados
    todos = pd.concat(pares, ignore_index=True).drop_duplicates()

    return (
        todos.groupby("curso_nombre")["est_id"]
        .nunique()
        .reset_index()
        .rename(columns={"curso_nombre": "nombre", "est_id": "total_estudiantes"})
        .sort_values("total_estudiantes", ascending=False)
    )