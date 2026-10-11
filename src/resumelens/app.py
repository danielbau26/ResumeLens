import sys
from pathlib import Path
import runpy

# Agrega src para poder importar el paquete resumelens.
FOLDER = Path(__file__).resolve().parent
sys.path.insert(0, str(FOLDER.parent))

# Ejecuta la interfaz ubicada en ui.
runpy.run_path(
    str(FOLDER / "ui" / "interface.py"),
    run_name="__main__" #Hace que sea el archivo principal
)