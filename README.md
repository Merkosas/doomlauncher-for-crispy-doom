Lanzador de WADs de Doom, pensado para crispy-doom y chocolate-doom, pero puedes utilizarlo de la manera que te funcione y guste.

Un lanzador simple y fachero para tus WADs de Doom. Se acabó el andar escribiendo comandos en la terminal cada vez que quieres jugar.

Con este launcher, configurás tu motor de Doom preferido una sola vez y después solo te dedicás a elegir el WAD y jugar.

Características Principales

    Interfaz Gráfica Simple: Creado con PyQt6 para una experiencia de usuario limpia y directa.
    Configura tu Motor Favorito: Funciona con cualquier motor de Doom que se pueda ejecutar por línea de comandos (GZDoom, Crispy-Doom, Chocolate-Doom, Flatpaks, etc.).
    Detección Automática de WADs: Apunta el lanzador a tu carpeta de WADs y los listará a todos automáticamente.
    Configuración Persistente: Guarda la ruta de tu motor y tu carpeta de WADs para que no tengas que volver a configurarlo todo cada vez que lo abras.
    Lanzamiento Rápido: Ejecuta el WAD seleccionado con un doble clic o con el botón "Ejecutar Doom".

Instalación y Uso

Tienes dos maneras de usar este lanzador.
1. Usando el Ejecutable

La forma más fácil. No necesitas instalar nada más.

    Ve a la sección de Releases en este repositorio de GitLab.
    Descarga el archivo DoomLauncher-Linux de la última versión disponible.
    Dale permisos de ejecución:
    Bash

chmod +x DoomLauncher-Linux

¡Ejecuta el programa y a jugar!
Bash

    ./DoomLauncher-Linux

2. Ejecutando desde el Código Fuente

Si prefieres ejecutarlo directamente con Python.

    Clona este repositorio:
    Bash

git clone URL_DE_TU_REPO
cd NOMBRE_DEL_DIRECTORIO

Asegúrate de tener Python 3 y PyQt6 instalado.
Bash

pip install PyQt6

Ejecuta el script:
Bash

    python doom_launcher_qt.py

Primer Uso

La primera vez que ejecutes el programa, te pedirá dos cosas:

    El Comando del Motor de Doom: Aquí debes introducir el comando exacto para ejecutar tu motor. Por ejemplo: gzdoom, crispy-doom, o si usas Flatpak: flatpak run io.github.fabiangreffrath.Doom.
    El Directorio de WADs: Selecciona la carpeta en tu PC donde guardas todos tus archivos .WAD.

Una vez hecho esto, el lanzador guardará tu configuración y no volverá a preguntarte. Podrás cambiar estas opciones en cualquier momento desde la propia aplicación.
Tecnologías Utilizadas

    Python 3
    PyQt6 para la interfaz gráfica.
    PyInstaller para la compilación del ejecutable.
    GitLab CI/CD para la compilación y publicación automática de los releases.

---

## Licencia

Este proyecto está licenciado bajo la GNU General Public License v3.0. Consulta el archivo `LICENSE` para más detalles.