import json
from math import e
from dotenv import load_dotenv
import logging
from login_options_generator import LoginOptionsGenerator
from modules.crm_salesforce import crear_multipurpose
from modules.oracle import OracleConnector
from modules.ad import ActiveDirectoryConnector
from modules.api import APIClient
from modules.send_mail import enviar_correo_graph
import codecs
import os
class Container:#Borrrar
    pass

#load_dotenv('./batch_script/.env') #PRODUCTION
load_dotenv('./batch_script/.env.dev') #DEVELOPMENT

# Configuración de logging
logging.basicConfig(filename='script.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


# Incialización de variables globales para las conexiones  
def init_conections():
    global oracle_egre, oracle_vb, ad, dominio

    # Conexión a Oracle - Egre Apps
    oracle_user = os.getenv('ORACLE_USER_EGRE')
    oracle_password = os.getenv('ORACLE_PASSWORD_EGRE')
    oracle_dsn = os.getenv('ORACLE_DSN_EGRE')
    dominio = os.getenv('DOMINIO')
    oracle_egre = OracleConnector(oracle_user, oracle_password, oracle_dsn, "EGRESADOS")
    oracle_egre.connect()


    # Conexión a Oracle - VISTA BANNER
    oracle_user_vb = os.getenv('ORACLE_USER_VISTA_BANNER')
    oracle_password_vb = os.getenv('ORACLE_PASSWORD_VISTA_BANNER')
    oracle_dsn_vb = os.getenv('ORACLE_DSN_VISTA_BANNER')
    oracle_vb = OracleConnector(oracle_user_vb, oracle_password_vb, oracle_dsn_vb, "BANNER")
    oracle_vb.connect()

    # Active Directory 
    ad = ActiveDirectoryConnector()
    ad.connect()


# Finalizacion de conexiones
def close_conections():
    global oracle_egre, oracle_vb
    if oracle_egre:
        oracle_egre.close()
    if oracle_vb:
        oracle_vb.close()



def normalizar_datos_egre(egresado):

    egresado.pidm = egresado.pidm
    egresado.primer_nombre = egresado.primer_nombre.strip().title() if egresado.primer_nombre is not None else "" 
    egresado.segundo_nombre = egresado.segundo_nombre.strip().title() if egresado.segundo_nombre is not None else ""
    egresado.apellidos = egresado.apellidos.strip().title() if egresado.apellidos is not None else ""
    egresado.genero = egresado.documento.strip()
    egresado.carnet = egresado.documento.strip()
    egresado.email_personal = egresado.documento.strip()
    egresado.des_grado = egresado.documento.strip()
    egresado.cod_grado = egresado.documento.strip()
    egresado.displayName = f"{egresado.primer_nombre} {egresado.segundo_nombre if egresado.segundo_nombre else ''} {egresado.apellidos}"   
    egresado.givenName  = egresado.primer_nombre + " " + egresado.segundo_nombre
    egresado.sn = egresado.apellidos

    return egresado


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#     Funcion principal, desde aqui se inicia el proceso  
#
#     
#     MAIN()
#     
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def main():
    global oracle_egre, oracle_vb, ad, dominio
    

    init_conections()

    # enviar_correo_graph("cuenta@uniandes.edu.co", "napardoz@gmail.com", "Correo prueba", "Correo recibido!")
    # exit(0)
    
    egresado = Container()
    egresado.id = 1    
    print(egresado)
    print(egresado.id)
    resultado_banner = proceso_banner(egresado, 954, 'j.ortizd2')    
    
    print("FINALIZO PROCESO BANNER" ,  resultado_banner )
    
    exit(0)




    print("[1] ----------- Consultando Egresados a Procesar")
    
    # Consulta de los primeros 10 registros de UA_EGRE_PROHIBIDOS
    egresados_procesar = oracle_egre.get_egresados_procesar()
    print('Primeros registros de USUARIOS_PROCESAR:')
    
    
    codigos_procesar = [egresado.documento.strip() for egresado in egresados_procesar]
    print('Códigos de documentos a procesar:', codigos_procesar)


    codigos_procesar = ",".join(f"'{egresado.documento.strip()}'" for egresado in egresados_procesar)
    codigos_procesar = f"({codigos_procesar})"
    print('Códigos de documentos a procesar 2:', codigos_procesar)


    print("[2] ----------- Consultando Datos en Vista Banner")  
 
    for egresado in egresados_procesar:
        print("------------------------------------------------------------------------------------------------------")
        print("------------------------------------------------------------------------------------------------------")
        print("------------------------------------------------------------------------------------------------------")
        print("------------------------------------------------------------------------------------------------------")
    
        print(f'EGRESADO -> {egresado}')
        egresado_vista_banner = oracle_vb.get_egresado_vista_banner(egresado.documento)
        
        print(f'EGRESADO VISTA BANNER -> {egresado_vista_banner}')



        print("[3] ----------- Existe en Vista Banner?")  
        if(egresado_vista_banner):
            vb_egre = normalizar_datos_egre(egresado_vista_banner[0])
            
            print("=============== EXISTE EN VISTA BANNER: =============== ")
            print(vb_egre)

            #############################################################
            ## Proceso de creación de usuario en AD 
            ## Retorna {"login": login_definitivo, "estado": True/False, "mensaje": "creado_en_ad"/"error_creando_en_ad"/"exsiste_documento_en_ad"}
            #############################################################
            CREACION_DA = proceso_directorio_activo(vb_egre, egresado)
           
            print("RESULTADO CREACION AD ", CREACION_DA)
            
            
            #############################################################
            ## Proceso de creación de usuario BANNER (Goremal, Gobtpac)
            ## 
            #############################################################
            if(CREACION_DA['estado']):
                print("[9] ----------- Crear usuario en Banner (Goremal")  
                CREACION_BANNER =  proceso_banner(egresado, vb_egre.pidm, CREACION_DA.login)
                
                
                if(CREACION_BANNER):
                    print("TODO OK EN BANNER Y AD ")
                    #oracle_egre.update_usuario_procesar(egresado.id, ESTADO_VISTA='PROCESADO_OK' )

                    

    
        else:
            print("[4] ----------- NO EXISTE EN VISTA BANNER")
            print("NO EXISTE ")
            oracle_egre.update_usuario_procesar(egresado.id, ESTADO_VISTA='NO_EXSITE_EN_VISTA')

    #Cerrando conexiones
    close_conections()
 
 
 
 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#       Funcion de creacion de usuarios en el Directorio Activo
#
#     Retorna {"login": login_definitivo, 
#              "estado": True/False, 
#              "mensaje": "creado_en_ad"/"error_creando_en_ad"/"exsiste_documento_en_ad"} 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def proceso_directorio_activo(vb_egre, egresado):
    global oracle_egre, ad, dominio
    login_definitivo = ""
    
    print("[5] ----------- Busca egresado por documento en AD ")  
    egresado_ad = ad.search_user(vb_egre.documento, "employeeID")


    print("[6] ----------- Existe en AD? ", vb_egre.documento)
    if(egresado_ad):
        print("[7] ================ YA EXISTE EN AD =============== ")
        print(egresado_ad)  
        login_en_ad = str(egresado_ad.cn)
        print("LOGIN EN AD ", login_en_ad)
        print("DETALLE ", egresado_ad.distinguishedName)
        login_en_ad = str(egresado_ad.cn)
        login_en_ad = str(egresado_ad.cn)
        detalle = str(egresado_ad.distinguishedName)
        oracle_egre.update_usuario_procesar(egresado.id, ESTADO_AD='EXISTE_DOCUMENTO_EN_AD', LOGIN=login_en_ad, DETALLE=detalle)
        login_definitivo = login_en_ad

        print("YA EXISTE EN AD ") 
        print("EGRESADO AD ", egresado_ad)
        return {"login": login_definitivo, "estado": True, "mensaje": "exsiste_documento_en_ad"}

    elif(not egresado_ad):

        print("[8] ----------- NO EXISTE EN AD ")

        print("...............Generando login............")

        print("primer_nombre ", vb_egre.get_primer_nombre())
        print("segundo_nombre ", vb_egre.get_segundo_nombre())
        print("apellidos ", vb_egre.get_apellidos())


        gen = LoginOptionsGenerator(
                vb_egre.get_primer_nombre(),
                vb_egre.get_segundo_nombre(),
                vb_egre.get_apellidos()                        
            )
        print("[8.1] ----------- Generando opciones sugeridas de login ")
        opciones = gen.generar_opciones()

        login_seleccionado = None
        for login in opciones:
            print("Opciones login ", opciones)
            print(f"[8.2] ----------- Ya existe login {login} en AD?  ")
            temp_valida_Login = ad.search_user(login, "sAMAccountName")
            

            if(temp_valida_Login):
                print("[8.3] ----------- Ya existe login en AD, generar uno nuevo (", login, ")")
                                    

            elif(not temp_valida_Login):
                print("[8.4] ----------- No existe este login en AD, proceder a crear (", login, ")")
                login_seleccionado = login
                break

            print("...............Siguiente............")  
            
        print("...............PROCEDE A CREAR............")

        
        #Preparando clave inicial
        password = 'claveSegura2024!'
        pwd_utf16 = f'"{password}"'.encode('utf-16-le')

        
        attributes_da = {
            'sAMAccountName': login_seleccionado, #login sin @
            'userPrincipalName': login_seleccionado + '@'+dominio, #login con @dominio
            'displayName': vb_egre.displayName, #Nombre completo
            'givenName': vb_egre.givenName, #Nombres
            'sn': vb_egre.sn, #Apellidos
            'mail': login_seleccionado + '@'+dominio, #login con @dominio
            'employeeID': vb_egre.documento,#documento
            'employeeNumber': vb_egre.carnet,#codigo uniandes
            'otherMailbox': vb_egre.email_personal, #personal email
            'businessCategory': 'UAEgresado', #Tipo de usuario
            'extensionAttribute12': 'EGRE', #Grado                    
            # --- Estos son los parametros para forzar el cambio de clave al primer inicio ---                    
            'userAccountControl': '512',  #Habilitar cuenta
            'pwdLastSet': '0',  #El usuario debe cambiar la clave al primer inicio
            'unicodePwd': pwd_utf16 #Clave inicial en formato correcto
        }

        

            #'userAccountControl': '512',  #Habilitar cuenta
            #'pwdLastSet': '0',  #El usuario debe cambiar la clave al primer inicio
            #'unicodePwd': 'hola' #Clave inicial en formato correcto


        print("#####################################")
        #print(json.dumps(attributes_da, indent=4, ensure_ascii=False))  
        print(attributes_da)
        print("#####################################")
        
        print("...............Creando usuario en AD............")
        if ad.create_user(attributes_da):
            print("...............Usuario creado en AD............")
            oracle_egre.update_usuario_procesar(egresado.id, ESTADO_AD='CREADO_EN_AD', LOGIN=login_seleccionado, DA="OK" )
            login_definitivo = login_seleccionado
            print("...............Fin  usuario en AD OK............")
            return {"login": login_definitivo, "estado": True, "mensaje": "creado_en_ad"}         
        else:
            print("Error creando usuario en AD o ya existe....")
            print("...............Fin  usuario en AD Fallido............")
            oracle_egre.update_usuario_procesar(egresado.id, ESTADO_AD='ERROR_CREANDO_AD', DETALLE="Error creando usuario en AD " + login_seleccionado )
            return {"login": login_definitivo, "estado": False, "mensaje": "error_creando_en_ad"}
            
            
        
     
     
     
     
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#       Funcion de creacion de usuarios en Banner
# 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #        

def proceso_banner(egresado, pidm_par, login):
    global oracle_egre,  dominio
    respuesta_goremal = False
    respuesta_gobtepac = False
    print("[9] ----------- Proceso Banner ")
    print(pidm_par)
    print(login)


    #oracle_egre.verificar_paquetes_disponibles()

    print("-------------------INICIA CREACION GOREMAL-------------------------" )
    
    print("[9.1] ----------- Se intenta crear el usuario como nuevo en Banner " )
    respuesta_goremal = oracle_egre.actualizar_goremal(pidm=pidm_par,mail=login + '@uniandes.edu.co',existe=False,autocommit=True)
    
    print("Respuesta_goremal Banner: ", respuesta_goremal)  

    if respuesta_goremal == False:
        print("[9.2] ----------- el usuario ya existe en Banner, intentando actualizar..." )
        
        respuesta_goremal = oracle_egre.actualizar_goremal(pidm=pidm_par,mail=login + '@uniandes.edu.co',existe=True,autocommit=True)
        
        if respuesta_goremal == False:
            print("[9.3] ----------- Error actualizando usuario en Banner " )
            oracle_egre.update_usuario_procesar(egresado.id, ESTADO_BANNER='ERROR_EN_BANNER', DETALLE="Error actualizando GOREMAL" )    
        else:
            print("[9.4] ----------- actualizado usuario en Banner " )
            oracle_egre.update_usuario_procesar(egresado.id, ESTADO_BANNER='ACTUALIZADO_EN_BANNER', GOREMAL="OK", DETALLE="" ) 
        
    else:
        print("[9.4] ----------- Usuario creado/actualizado en Banner con exito " )
        oracle_egre.update_usuario_procesar(egresado.id, ESTADO_BANNER='CREADO_EN_BANNER', GOREMAL="OK", DETALLE="" )
        
        
    
    if(respuesta_goremal):        
        print("-------------------INICIA CREACION GOBTEPAC-------------------------" )
        respuesta_gobtepac = oracle_egre.actualiza_gobtpac(pidm=pidm_par,mail=login ,autocommit=True)        
        print("Resultado GOBTPAC: ", respuesta_gobtepac) 
        
        if respuesta_gobtepac == False:
            print("[9.3] ----------- Error actualizando usuario en Banner " )
            oracle_egre.update_usuario_procesar(egresado.id, ESTADO_BANNER='ERROR_EN_BANNER', DETALLE="Error actualizando GOBTEPAC" )    
        else:
            print("[9.4] ----------- actualizado usuario en Banner " )
            oracle_egre.update_usuario_procesar(egresado.id, ESTADO_BANNER='ACTUALIZADO_EN_BANNER', GOBTPAC="OK", DETALLE="" ) 
        
    print("=== resultado_banner_goremal " , respuesta_goremal , " respuesta_gobtepac ", respuesta_gobtepac)
        
    return respuesta_goremal and respuesta_gobtepac
        
    
    
     
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#       Funcion de creacion de usuarios en Banner
# 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #        

def proceso_CRM(egresado, pidm_par, login):
    crear_multipurpose("1001342560")    
     
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#       Envio de correo de notificacion al egresado
# 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #        

def enviar_correo_notificacion(egresado, login, password):
    
    enviar_correo_graph("cuenta@uniandes.edu.co", "napardoz@gmail.com", "Correo prueba", "Correo recibido!")
    # exit(0)





    
        



# Consumo de API REST
# api = APIClient()
# api.call_endpoint()
# logging.info('Fin del script')





if __name__ == "__main__":
    main()
