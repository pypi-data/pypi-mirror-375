from .Dfiles import DuckyFiles

# Creamos instancias o funciones directas
duck = DuckyFiles()

# Exportamos funciones para que se puedan usar así
create_file = duck.create_file
read_file = duck.read_file
delete_file = duck.delete_file
create_folder = duck.create_folder
delete_folder = duck.delete_folder
move = duck.move
list = duck.list
