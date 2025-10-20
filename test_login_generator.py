from login_options_generator import LoginOptionsGenerator

def test_login_options():
    # Ejemplo: nombre y apellidos que generan logins ofensivos y no ofensivos
    casos = [
        ("Hugo", "Alberto", "Triana Bejarano"),  # Normal
        ("A", "B", "Bejarano"),                  # Apellido en blacklist
        ("A", "B", "Bonilla"),                  # Apellido en blacklist
        ("Carlos", "Eduardo", "Gomez Perez"),   # Normal
        ("", "", "pedos Hugo"),                   # Apellido en blacklist
    ]
    for nombres in casos:
        gen = LoginOptionsGenerator(*nombres)
        opciones = gen.generar_opciones()
        print(f"Opciones para {nombres}: {opciones}")

if __name__ == "__main__":
    test_login_options()
