from dataclasses import dataclass

@dataclass
class EgresadoProcesar:
    id: int
    documento: str
    da: str
    banner: str
    crm: str
    estado_ad: str
    isEgresado: bool = False



@dataclass
class VistaBanner:
    pidm: str
    documento: str   
    primer_nombre: str   
    segundo_nombre: str  
    apellidos: str
    genero: str  
    carnet: str  
    email_personal: str  
    des_grado: str   
    cod_grado: str  
    displayName: str
    givenName: str
    sn: str



    def get_documento(self):
        return self.documento

    def get_primer_nombre(self):
        return self.primer_nombre

    def get_segundo_nombre(self):
        return self.segundo_nombre

    def get_apellidos(self):
        return self.apellidos

    def get_genero(self):
        return self.genero

    def get_carnet(self):
        return self.carnet

    def get_email_personal(self):
        return self.email_personal

    def get_des_grado(self):
        return self.des_grado

    def get_cod_grado(self):
        return self.cod_grado




