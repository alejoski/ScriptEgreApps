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
[ ] Invocar paquetes de banner, verificar como se debe invocar el paquete
