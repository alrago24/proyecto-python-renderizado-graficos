from analisis import (
    usuarios_limpios,
    perfiles_limpios,
    cursos_limpios,
    calificaciones_limpias,
    estudiantes_limpios,
    profesores_limpios,
    asistencias_limpias,
)

def probar_carga_y_limpieza():
    dfs = {
        "usuarios": usuarios_limpios(),
        "perfiles": perfiles_limpios(),
        "cursos": cursos_limpios(),
        "calificaciones": calificaciones_limpias(),
        "estudiantes": estudiantes_limpios(),
        "profesores": profesores_limpios(),
        "asistencias": asistencias_limpias(),
    }

    for nombre, df in dfs.items():
        print(f"\n{'='*50}")
        print(f"  {nombre}  ({df.shape[0]} filas, {df.shape[1]} columnas)")
        print(f"{'='*50}")
        print(df.to_string(index=False))


if __name__ == "__main__":
    probar_carga_y_limpieza()