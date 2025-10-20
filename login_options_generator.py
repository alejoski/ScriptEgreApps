class LoginOptionsGenerator:
    def __init__(self, primer_nombre, segundo_nombre, apellidos):
        self.primer_nombre = primer_nombre.strip()
        self.segundo_nombre = segundo_nombre.strip() if segundo_nombre else ""
        partes_apellido = apellidos.strip().split()
        self.primer_apellido = partes_apellido[0] if len(partes_apellido) > 0 else ""
        self.segundo_apellido = partes_apellido[1] if len(partes_apellido) > 1 else ""

    def generar_opciones(self):
        opciones = []
        # Primera letra de cada nombre
        letra1 = self.primer_nombre[0].lower() if self.primer_nombre else ""
        letra2 = self.segundo_nombre[0].lower() if self.segundo_nombre else ""
        # Primer apellido y segunda letra de apellido
        pa = self.primer_apellido.lower()
        sa = self.segundo_apellido.lower() if self.segundo_apellido else ""
        # Opción 1: primeras letras de nombres + punto + primer apellido
        op1 = f"{letra1}{letra2}.{pa}"
        opciones.append(op1[:20])
        # Opción 2: primeras letras de nombres + punto + primer apellido + primera letra segundo apellido
        op2 = f"{letra1}{letra2}.{pa}{sa[0] if sa else ''}"
        opciones.append(op2[:20])
        # Siguientes 5 opciones: opción 2 + consecutivo
        for i in range(1, 6):
            op = f"{op2}{i}"
            opciones.append(op[:20])
        # Reemplazar ñ y Ñ por n en cada login propuesto
        opciones = [op.replace('ñ', 'n').replace('Ñ', 'n') for op in opciones]
        # Filtrar opciones usando blacklist (substring match)
        blacklist = self._load_blacklist()
        opciones_filtradas = []
        for op in opciones:
            op_lower = op.lower()
            # Excluir si contiene 'pedos' como subcadena
            if 'pedos' in op_lower:
                opciones_filtradas.append("BLOQUEADO")
                continue
            # Excluir si coincide exactamente con alguna palabra del blacklist
            if op_lower in blacklist:
                opciones_filtradas.append("BLOQUEADO")
                continue
            opciones_filtradas.append(op)
        return opciones_filtradas

    def _load_blacklist(self):        
        blacklist = set()
        blacklist_path = "batch_script/ofensivas.txt"        
        try:
            with open(blacklist_path, "r", encoding="utf-8") as f:
                blacklist = set(line.strip().lower() for line in f if line.strip())
        except Exception as e:
            print(f"Error leyendo blacklist: {e}")
        # Forzar inclusión de 'pedos' para depuración
        blacklist.add('pedos')
        return blacklist





# Ejemplo de uso:
if __name__ == "__main__":
    gen = LoginOptionsGenerator("Hugo", "Alberto", "Triana Bejarano")
    print(gen.generar_opciones())
