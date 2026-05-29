# diagnostico.py
from merge import calificaciones, estudiantes, cursos, asistencias, profesores, usuarios, perfiles

for nombre, df in [
    ("calificaciones", calificaciones),
    ("estudiantes",    estudiantes),
    ("cursos",         cursos),
    ("asistencias",    asistencias),
    ("profesores",     profesores),
    ("usuarios",       usuarios),
    ("perfiles",       perfiles),
]:
    print(f"{nombre}: {list(df.columns)}")