# Entrar al directorio 

cd C:\Proyectos Uniandes\EgreAppsNew\

# Activar environment
.venv/Scripts/activate

#Ejecutar script
py batch_script\main.py 

# Para limiar la tabla de usuarios_procesar
update usuarios_procesar set login = null, da = null, banner = null, estado = null