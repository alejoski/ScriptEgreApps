from modelos import EgresadoProcesar, VistaBanner
import oracledb as cx_Oracle
import os
###########################################################################
# Estas lineas son necesarias para que funcione oracledb
# Se pueden comentar cuando se conecta a la BD de PRODUCCION
import oracledb
oracledb.init_oracle_client(lib_dir=r"C:\\BD\\oracle\\instantclient_19_28")
############################################################################


class OracleConnector:
    

    def __init__(self, user, password, dsn, dataBase=None):
        self.user = user
        self.password = password
        self.dsn = dsn
        self.connection = None
        self.dataBase = dataBase

    def connect(self):
        try:
            self.connection = cx_Oracle.connect(user=self.user, password=self.password, dsn=self.dsn)
            print(f'Conectado a Oracle <{self.dataBase}>')
        except Exception as e:
            print(f'Error conectando a Oracle: {e}')

    def close(self):
        if self.connection:
            self.connection.close()



    def get_egresados_procesar(self):
        if not self.connection:
            print('No hay conexión a Oracle.')
            return []
        try:
            cursor = self.connection.cursor()
            SQL = """
                    SELECT 
                        ID,
                        DOCUMENTO,
                        DA,
                        BANNER,
                        CRM,
                        ESTADO_AD,
                        LOGIN
                    FROM USUARIOS_PROCESAR 
                    WHERE ESTADO_AD IS NULL ORDER BY ID
                    """
            cursor.execute(SQL)
            rows = cursor.fetchall()
            cursor.close()
            egresados = [EgresadoProcesar(*row) for row in rows]
            return egresados
        except Exception as e:
            print(f'Error consultando USUARIOS_PROCESAR: {e}')
            return []
        
    
    def update_usuario_procesar(self, id, **campos):
        if not self.connection:
            print('No hay conexión a Oracle.')
            return False
        if not campos:
            print('No se especificaron campos para actualizar.')
            return False
        try:
            set_clause = ', '.join([f"{campo} = :{campo}" for campo in campos.keys()])
            sql = f"UPDATE USUARIOS_PROCESAR SET {set_clause} WHERE ID = :id"
            params = campos.copy()
            params['id'] = id
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            self.connection.commit()
            cursor.close()
            print(f'Registro {id} actualizado correctamente.')
            return True
        except Exception as e:
            print(f'Error actualizando USUARIOS_PROCESAR: {e}')
            return False
        

    def get_egresado_vista_banner(self, document):
        if not self.connection:
            print('No hay conexión a Oracle.')
            return []
        try:
            cursor = self.connection.cursor()

            SQL = """
                    SELECT  
                      PIDM,
                      DOCUMENTO, 
                      PRIMER_NOMBRE, 
                      SEGUNDO_NOMBRE, 
                      APELLIDOS,
                      GENERO, 
                      CARNET, 
                      EMAIL_PERSONAL, 
                      DES_GRADO, 
                      COD_GRADO,
                      '' as displayName,
                      '' as givenName,
                      '' as sn
                    FROM DATOS_MIM_EGRESADOS 
                    WHERE DOCUMENTO = :document                     
                  """
            #print((SQL  , {'document': document.strip()}))
            cursor.execute(SQL  , {'document': document.strip()})
            rows = cursor.fetchall()
            cursor.close()
            vista_banner = [VistaBanner(*row) for row in rows]
            return vista_banner
        except Exception as e:
            print(f'Error consultando DATOS_MIM_EGRESADOS: {e}')
            return []


    def actualizar_goremal(self, pidm, mail, existe=False, autocommit=True, esquema=None):
        """
        Ejecuta los procedimientos almacenados upd_banner o upd_banner_2 según si el usuario existe.
        
        Args:
            pidm (str): Número de identificación del usuario
            mail (str): Email del usuario
            existe (bool): True si el usuario ya existe (usa upd_banner_2), False para nuevo usuario (usa upd_banner)
            autocommit (bool): True para hacer commit automático, False para transacción manual
            esquema (str): Esquema específico a usar (ej: 'WWW_EGRE'), si None usa el actual
            
        Returns:
            str: Resultado del procedimiento almacenado o None si hay error
        """
        if not self.connection:
            print('No hay conexión a Oracle.')
            return False
            
        esquema_actual = "UA_AUTOSERVI_EGRE"
            
            
        try:
            cursor = self.connection.cursor()
            
            # Seleccionar el procedimiento según si el usuario existe
            # BEGIN :r := UA_AUTOSERVI_EGRE.upd_banner(:i, :m); END;
            if existe:
                procedure_call = f'BEGIN :r := {esquema_actual}.upd_banner_2(:i, :m); END;'
                proc_name = "upd_banner_2"
            else:
                procedure_call = f'BEGIN :r := {esquema_actual}.upd_banner(:i, :m); END;'
                proc_name = "upd_banner"
            
            print(f'Intentando ejecutar {proc_name} en esquema: {esquema_actual}')
            print(f'  Usuario(pidm): {pidm}, Email: {mail}')
            print(f'  Llamada: {procedure_call}')
            
            # Crear variable de salida para el resultado
            result_var = cursor.var(cx_Oracle.STRING, size=500)
            
            # Ejecutar el procedimiento almacenado
            cursor.execute(procedure_call, {
                'i': pidm,
                'm': mail,
                'r': result_var
            })
            
            # Obtener el resultado
            resultado = result_var.getvalue()
            
            if autocommit:
                self.connection.commit()
                print(f'✓ Banner actualizado correctamente con {esquema_actual}.{proc_name}')
                print(f'  Resultado: {resultado}')
            else:
                print(f'✓ Procedimiento ejecutado (sin commit) con {esquema_actual}.{proc_name}')
                print(f'  Resultado: {resultado}')
                
            cursor.close()
            
            if 'unique constraint' in resultado or 'ORA-' in resultado or 'Error' in resultado:                
                return False
            else:
                return True
            
        except Exception as e:
            print(f'✗ Error con esquema {esquema_actual}: {str(e)[:100]}...')
            try:
                cursor.close()
            except:
                pass
            
    


        if autocommit:
            try:
                self.connection.rollback()
                print('Rollback ejecutado por error.')
            except:
                pass
            
        return False
    




    def actualiza_gobtpac(self, pidm, mail, autocommit=True, esquema=None):
        """
        Ejecuta el procedimiento almacenado ua_autoservi_egre.actualizar_gobtpac_banner(:ni, :lp)
        Args:
            usuario (dict): Debe tener las claves 'numero_identificacion' y 'newlogin'
            autocommit (bool): True para commit automático
            esquema (str): Esquema a usar (opcional)
        Returns:
            str: Mensaje de resultado o error
        """
        if not self.connection:
            print('No hay conexión a Oracle.')
            return "No hay conexión a Oracle."


        esquema_actual = "UA_AUTOSERVI_EGRE"
        
        try:
            cursor = self.connection.cursor()
            procedure_call = f"BEGIN {esquema_actual}.actualizar_gobtpac_banner(:ni, :lp); END;"
            print(f"Llamando: {procedure_call}")
            print(f"  numero_identificacion: {pidm}, newlogin: {mail}")
            cursor.execute(procedure_call, {
                'ni': pidm,
                'lp': mail
            })
            if autocommit:
                self.connection.commit()
            # msg = f"Se actualizo GOBTPAC documento: {pidm} y mail {mail} exitosamente"  
          
            cursor.close()
            return True
        except Exception as e:
            try:
                cursor.close()
            except:
                pass
            if autocommit:
                try:
                    self.connection.rollback()
                    print('Rollback ejecutado por error. ', e)
                except:
                    pass
            return f"Error: {str(e)}"
        
    



    def verificar_paquetes_disponibles(self):
        """
        Verifica qué paquetes ua_autoservi_egre están disponibles en diferentes esquemas.
        Útil para diagnóstico cuando hay problemas de acceso.
        """
        if not self.connection:
            print('No hay conexión a Oracle.')
            return
            
        try:
            cursor = self.connection.cursor()
            
            # Consultar paquetes disponibles
            sql_paquetes = """
                SELECT OWNER, OBJECT_NAME, STATUS 
                FROM ALL_OBJECTS 
                WHERE OBJECT_TYPE = 'PACKAGE' 
                AND UPPER(OBJECT_NAME) LIKE '%UA_AUTOSERVI_EGRE%'
                ORDER BY OWNER, OBJECT_NAME
            """
            
            print("=== PAQUETES UA_AUTOSERVI_EGRE DISPONIBLES ===")
            cursor.execute(sql_paquetes)
            paquetes = cursor.fetchall()
            
            if paquetes:
                for owner, name, status in paquetes:
                    print(f"  {owner}.{name} - Estado: {status}")
            else:
                print("  No se encontraron paquetes ua_autoservi_egre")
            
            # Consultar procedimientos dentro del paquete si existe
            sql_procs = """
                SELECT OWNER, PROCEDURE_NAME, OBJECT_NAME 
                FROM ALL_PROCEDURES 
                WHERE UPPER(PROCEDURE_NAME) LIKE '%BANNER%'
                AND UPPER(OBJECT_NAME) LIKE '%EGRE%'
                ORDER BY OWNER, PROCEDURE_NAME, OBJECT_NAME
            """
            
            print("\n=== PROCEDIMIENTOS UPD_BANNER DISPONIBLES ===")
            cursor.execute(sql_procs)
            procedimientos = cursor.fetchall()
            
            if procedimientos:
                for owner, package, proc in procedimientos:
                    print(f"  {owner}.{package}.{proc}")
            else:
                print("  No se encontraron procedimientos upd_banner/upd_banner_2")
            
            # Mostrar el usuario actual
            cursor.execute("SELECT USER FROM DUAL")
            usuario_actual = cursor.fetchone()[0]
            print(f"\n=== INFORMACIÓN DE CONEXIÓN ===")
            print(f"  Usuario conectado: {usuario_actual}")
            print(f"  Base de datos: {self.dataBase}")
            
            cursor.close()
            
        except Exception as e:
            print(f'Error verificando paquetes: {e}')





 