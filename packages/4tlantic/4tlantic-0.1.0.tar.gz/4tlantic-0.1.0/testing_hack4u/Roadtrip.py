class Roadtrip:
    
    def __init__(self, nombre, Km, tiempo):
        self.nombre = nombre
        self.Km = Km
        self.tiempo = tiempo


    def __repr__(self):
        return f"Llegas a {self.nombre} en {self.tiempo} y recorres {self.Km} kilometros"


viajes = [
    Roadtrip("Lugo", "67", "35min"),
    Roadtrip("Vigo", "89", "45min"),
    Roadtrip("Ourense", "123", "110min")

]

def trip():
    for ciudad in viajes:
        print(ciudad)

def buscar():
    name = input("Ingresa el nombre de la ciudad --> ")
    for ciudad in viajes:
        if ciudad.nombre == name:
            return ciudad
        
    return None

