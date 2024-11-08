import os

# Función para listar archivos en una carpeta
def get_files_from_folder(folder_path, extensions):
    return [f for f in os.listdir(folder_path) if any(f.endswith(ext) for ext in extensions)]