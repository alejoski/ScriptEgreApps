import ldap3
import os
import ssl

class ActiveDirectoryConnector:
    


    def __init__(self):
        self.server = os.getenv('AD_SERVER')
        self.user = os.getenv('AD_USER')
        self.password = os.getenv('AD_PASSWORD')
        self.dn_crea = os.getenv('DN_CREA')
        self.dn_busca = os.getenv('DN_BUSCA')   
        self.connection = None

    def search_user(self, employeeID, atribute):
        if not self.connection:
            print('No hay conexión a Active Directory.')
            return None
        
        search_filter = f'({atribute}={employeeID})'
        try:
                 
            print(f'Buscando usuario en AD con filtro: {self.dn_busca} | {search_filter} ')
            self.connection.search(search_base=self.dn_busca , search_filter=search_filter, attributes=ldap3.ALL_ATTRIBUTES)
            if self.connection.entries:
                print(f'Usuario encontrado: {self.connection.entries[0]}')
                return self.connection.entries[0]
            else:
                print('Usuario no encontrado.')
                return None
        except Exception as e:
            print(f'Error consultando usuario en AD: {e}')
            return None
    



    def create_user(self, attributes):
        if not self.connection:
            print('No hay conexión a Active Directory.')
            return False
        try:

            dn = "CN=" + attributes['sAMAccountName']+"," + self.dn_crea

            print(f'Creando usuario en DN: {dn}')

            self.connection.add(dn, ['top', 'person', 'organizationalPerson', 'user'], attributes)
            if self.connection.result['result'] == 0:
                print(f'Usuario creado correctamente en {dn}')
                return True
            else:
                print(f'Error creando usuario: {self.connection.result}')
                return False
        except Exception as e:
            print(f'Error creando usuario en AD: {e}')
            return False
        

    """
        Modifica los atributos de un usuario existente en AD.
        sAMAccountName: login del usuario (sin @)
        changes: diccionario con los atributos a modificar, ejemplo: {'mail': 'nuevo@mail.com'}
    """  
    def update_user(self, sAMAccountName, changes):

        if not self.connection:
            print('No hay conexión a Active Directory.')
            return False
        try:
            dn = f"CN={sAMAccountName},{self.dn_crea}"
            print(f'Modificando usuario en DN: {dn}')
            # Formato de cambios para ldap3: {'attribute': [(ldap3.MODIFY_REPLACE, [valor])], ...}
            ldap_changes = {attr: [(ldap3.MODIFY_REPLACE, [value])] for attr, value in changes.items()}

            print(f'   ##            DN: {dn}')
            print(f'   ##            Cambios a aplicar: {ldap_changes}')

            self.connection.modify(dn, ldap_changes)
            if self.connection.result['result'] == 0:
                print(f'Usuario modificado correctamente en {dn}')
                return True
            else:
                print(f'Error modificando usuario: {self.connection.result}')
                return False
        except Exception as e:
            print(f'Error modificando usuario en AD: {e}')
            return False          


    def connect(self):
        try:
            # Si la variable AD_SERVER contiene ldaps://, extraer host y puerto
            if self.server and self.server.startswith('ldaps://'):
                # Ejemplo: ldaps://root02pr.fundacionuniandes.edu.co:636
                server_url = self.server.replace('ldaps://', '')
                if ':' in server_url:
                    host, port = server_url.split(':')
                    port = int(port)
                else:
                    host = server_url
                    port = 636

                # Configuración TLS sin validación de certificados (para entornos de desarrollo)
                tls_config = ldap3.Tls(
                    validate=ssl.CERT_NONE,
                    version=ssl.PROTOCOL_TLS,
                    ciphers='ALL:@SECLEVEL=0'
                )
                print(f'Conectando a AD via LDAPS a {host}:{port}')
                server = ldap3.Server(host, port=port, use_ssl=True, tls=tls_config)
            else:
                print(f'Conectando a AD via LDAP a {self.server}')
                server = ldap3.Server(self.server)
            
            # Crear la conexión para ambos casos
            self.connection = ldap3.Connection(server, user=self.user, password=self.password, auto_bind=True)
            print('Conectado a Active Directory exitosamente')
            
        except Exception as e:
            print(f'Error conectando a AD: {e}')
            self.connection = None
    # def connect(self):
    #     try:
    #         server = ldap3.Server(self.server)
    #         self.connection = ldap3.Connection(server, user=self.user, password=self.password, auto_bind=True)
    #         print('Conectado a Active Directory')
    #     except Exception as e:
    #         print(f'Error conectando a AD: {e}')


    def close(self):
        if self.connection:
            self.connection.unbind()
