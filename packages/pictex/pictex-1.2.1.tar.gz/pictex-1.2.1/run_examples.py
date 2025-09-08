import subprocess
import sys
from pathlib import Path

root = Path("examples")

for py_file in root.rglob("*.py"):
    print(f"Ejecutando {py_file}...")
    subprocess.run(
        [sys.executable, str(py_file.name)],
        check=True,
        cwd=py_file.parent  # 👈 cambiamos el directorio de trabajo al del script
    )
