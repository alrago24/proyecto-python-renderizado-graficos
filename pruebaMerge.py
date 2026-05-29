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


def probar_merges():
    merges = {
        "CALIFICACIONES  ←→  ESTUDIANTES  ←→  CURSOS":  notas_por_curso,
        "ASISTENCIAS     ←→  CALIFICACIONES":            asistencia_vs_nota,
        "CURSOS          ←→  PROFESORES   ←→  NOTAS":   rendimiento_por_profesor,
        "ASISTENCIAS     ←→  CURSOS (tendencia)":        tendencia_asistencia,
        "VISTA COMPLETA  (est + usr + per + notas)":     perfil_estudiante,
        "ESTUDIANTES     ←→  PROFESOR":                  estudiantes_por_profesor,
        "CURSOS          ←→  PROFESOR":                  cursos_por_profesor,
        "CURSOS          ←→  ESTUDIANTE":                cursos_por_estudiante,
        "CURSOS CON MÁS ESTUDIANTES MATRICULADOS":       cursos_con_mas_estudiantes,
    }

    for nombre, fn in merges.items():
        print(f"\n{'='*60}")
        print(f"  {nombre}")
        print(f"{'='*60}")
        try:
            df = fn()
            print(f"  {df.shape[0]} filas  |  {df.shape[1]} columnas")
            print(f"  Columnas: {list(df.columns)}\n")
            print(df.to_string(index=False))
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")


if __name__ == "__main__":
    probar_merges()