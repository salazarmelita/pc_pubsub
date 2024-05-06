
# Función para obtener la hora actual
get_timestamp() {
    date +"%Y-%m-%d %H:%M:%S"
}

# Obtener la hora de inicio
start_time=$(get_timestamp)
echo "Hora de inicio: $start_time"

# Preguntar al usuario si está en Windows o Linux
read -p "¿Estás en Windows o Linux? (w/l): " sistema_operativo

#npm install -g firebase-tools
firebase login

# configuración proyecto backend
cd cloud_functions

# configurar proyecto para deploy
firebase use --add

# Deploy cloud functions

directorios=$(ls -d */)

# Configuración de variables
if [ "$sistema_operativo" == "w" ]; then
    create_venv="python -m venv venv"
    activate_venv="source venv/Scripts/activate"
else
    create_venv="python3.12 -m venv venv"
    activate_venv="source venv/bin/activate"
fi

install_python_dependencies="pip install -r requirements.txt"

# Configuración de variables node
install_node_dependencies="npm install"

# instalo dependencias de functions por defecto
cd functions
$create_venv
$activate_venv
$install_python_dependencies
deactivate
cd ..


# Carpetas a ignorar
carpetas_ignoradas=("functions" "workflows")

# configuración firebase deploy
deploy_functions="firebase deploy --only functions:"

# Iterar sobre cada directorio
for dir in $directorios; do
    # Verificar si el directorio está en la lista de carpetas ignoradas
    if [[ " ${carpetas_ignoradas[@]} " =~ " ${dir%/} " ]]; then
        echo "Ignorando directorio: $dir"
    else
        echo "Procesando directorio: $dir"
        
        # Entrar en el directorio
        cd $dir

        # Verificar la existencia de main.py o index.js
        if [ -e "main.py" ]; then
            echo "Detectado main.py, instalando dependencias de Python"
            # Verificar si ya existe venv
            if [ ! -d "venv" ]; then
                $create_venv
                $activate_venv
                $install_python_dependencies
                $deploy_functions${dir%/} -m "Deploy cloud functions from repository script: ${dir%/}"
                deactivate
            else
                echo "Ya existe venv, omitiendo instalación de dependencias de Python."
            fi
            $deploy_functions${dir%/} -m "Deploy cloud functions from repository script: ${dir%/}"
            
        elif [ -e "index.js" ]; then
            echo "Detectado index.js, instalando dependencias de Node.js"
            # Verificar si ya existe node_modules
            if [ ! -d "node_modules" ]; then
                $install_node_dependencies
            else
                echo "Ya existe node_modules, omitiendo instalación de dependencias de Node.js."
            fi
            $deploy_functions${dir%/} -m "Deploy cloud functions from repository script: ${dir%/}"

        elif [ -e "tsconfig.json" ]; then
            echo "Detectado index.ts, instalando dependencias de TypeScript"
            # Verificar si ya existe node_modules
            if [ ! -d "node_modules" ]; then
                $install_node_dependencies
            else
                echo "Ya existe node_modules, omitiendo instalación de dependencias de TypeScript."
            fi
            echo "Compilando TypeScript..."
            tsc
            $deploy_functions"${dir%/}" -m "Deploy cloud functions from repository script: ${dir%/}"
        else
            echo "No se detectó main.py ni index.js en ${dir%/}"
        fi

        # Volver al directorio raíz
        cd ..
    fi
done

# Obtener la hora de finalización
end_time=$(get_timestamp)
echo "Hora de finalización: $end_time"

# Calcular la duración
start_seconds=$(date -d "$start_time" '+%s')
end_seconds=$(date -d "$end_time" '+%s')
duration=$((end_seconds - start_seconds))
echo "Duración: $((duration / 60)) minutos"