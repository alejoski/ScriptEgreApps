# Entrar al directorio 

cd C:\Proyectos Uniandes\EgreAppsNew\

# Activar environment
.venv/Scripts/activate

#Ejecutar script
py batch_script\main.py 

# Para limiar la tabla de usuarios_procesar
update usuarios_procesar set login = null, da = null, banner = null, estado = null



# TODO
[X] Verificar como se debe consultar los usuarios para garantizar que no exista cuando se esten validando los login's propuestos (80014818)
[X] Intentar crear con los nuevos parametros
[ ] Crear constraint unique a la columna documento
[X] Invocar paquetes de banner, verificar como se debe invocar el paquete
[ ]  Cuando el usuario ya existe en DA detodas formas se debe lanzar la creacion en CRM y BANNER?
    [] Que pasa cuando existe pero esta en una rama especial (Inactivas)

[ ] Validar si si esta creando los usuarios en BANNER porque la respuesta del paquete es exitosa
[ ] Pasar a prod la tabla de USUARIOS_PROCESO para avanzar en las pruebas

