import os, shutil

class DuckyFiles:
    def __init__(self, base_path="."):
        self.base_path = base_path  # Carpeta donde trabajaremos

    # archivos
    def create_file(self, nombre, contenido=""):
        ruta = os.path.join(self.base_path, nombre)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        return (f"File created: {ruta}")
    
    def read_file(self, nombre):
        ruta = os.path.join(self.base_path, nombre)
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                return f.read()
        print("The file not exist")
        return None
    
    def delete_file(self, nombre):
        ruta = os.path.join(self.base_path, nombre)
        if os.path.exists(ruta):
            os.remove(ruta)
            print(f"File deleted: {ruta}")
        else:
            print("The file not exist")

    #carpetas
    def create_folder(self, nombre):
        ruta = os.path.join(self.base_path, nombre)
        os.makedirs(ruta, exist_ok=True)
        print(f"Folder created: {ruta}")

    def delete_folder(self, nombre):
        ruta = os.path.join(self.base_path, nombre)
        if os.path.exists(ruta):
            shutil.rmtree(ruta)
            print(f"Folder deleted: {ruta}")
        else:
            print("The folder not exist")

    # Mover archivo o carpeta
    def move(self, origen, destino):
        ruta_origen = os.path.join(self.base_path, origen)
        ruta_destino = os.path.join(self.base_path, destino)
        if os.path.exists(ruta_origen):
            shutil.move(ruta_origen, ruta_destino)
            print(f"Movido: {ruta_origen} -> {ruta_destino}")
        else:
            print("Origen no existe")

    def list(self):
        return os.listdir(self.base_path)