# Lanzador de WADs de Doom

Un lanzador simple y fachero para tus WADs de Doom, con un enfoque especial en motores clásicos como Crispy Doom y Chocolate Doom. Se acabó el andar escribiendo comandos en la terminal cada vez que quieres jugar.

Con este launcher, configurás tu motor de Doom preferido una sola vez y después solo te dedicás a elegir el WAD y jugar.

![Screenshot del Lanzador](![Launcher](Launcher.png)  

## Características Principales

* **Interfaz Gráfica Simple**: Creado con PyQt6 para una experiencia de usuario limpia y directa.
* **Configura tu Motor Favorito**: Aunque está pensado para Crispy/Chocolate Doom, funciona con cualquier motor que se pueda ejecutar por línea de comandos (GZDoom, PrBoom+, Flatpaks, etc.).
* **Editor Gráfico de Controles y Opciones**: Modifica las teclas, el ratón, el sonido y más desde una interfaz intuitiva dentro del mismo lanzador.
* **Detección Automática de WADs**: Apunta el lanzador a tu carpeta de WADs y los listará a todos automáticamente.
* **Configuración Persistente**: Guarda la ruta de tu motor y tu carpeta de WADs para que no tengas que volver a configurarlo todo cada vez que lo abras.
* **Lanzamiento Rápido**: Ejecuta el WAD seleccionado con un doble clic o con el botón "Ejecutar Doom".

## Instalación y Uso

Tienes dos maneras de usar este lanzador.

### 1. Usando el Ejecutable (Recomendado)

La forma más fácil. No necesitas instalar nada más.

1.  Ve a la sección de **Deploy > Releases** en este repositorio de GitLab.
2.  Descarga el archivo `DoomLauncher-Linux` de la última versión disponible.
3.  Dale permisos de ejecución:
    ```bash
    chmod +x DoomLauncher-Linux
    ```
4.  ¡Ejecuta el programa y a jugar!
    ```bash
    ./DoomLauncher-Linux
    ```

### 2. Ejecutando desde el Código Fuente

Si prefieres ejecutarlo directamente con Python.

1.  Clona este repositorio.
2.  Asegúrate de tener Python 3 y PyQt6 instalado.
    ```bash
    pip install PyQt6
    ```
3.  Ejecuta el script:
    ```bash
    python doom_launcher_qt.py
    ```

## Primer Uso

La primera vez que ejecutes el programa, te pedirá dos cosas:

1.  **El Comando del Motor de Doom**: Aquí debes introducir el comando exacto para ejecutar tu motor. Por ejemplo: `crispy-doom`, `gzdoom`, o si usas Flatpak: `flatpak run io.github.fabiangreffrath.Doom`.
2.  **El Directorio de WADs**: Selecciona la carpeta en tu PC donde guardas todos tus archivos `.WAD`.

Una vez hecho esto, el lanzador guardará tu configuración y no volverá a preguntarte. Podrás cambiar estas opciones en cualquier momento desde la propia aplicación.

### Editor de Configuración Avanzado

El lanzador incluye una potente herramienta para modificar los controles y opciones del juego.

1.  Haz clic en el botón **"Editar Configuración"**.
2.  La primera vez, te pedirá que localices tu archivo `default.cfg`. Generalmente se encuentra en `~/.config/crispy-doom/` o una ruta similar, dependiendo de tu motor.
3.  Una vez abierto, verás una ventana con todas las opciones:
    * **Sensibilidad y Volumen:** Se ajustan con cómodos controles deslizantes.
    * **Controles de Teclado y Ratón:** Haz clic en el botón de cualquier control y luego presiona la tecla (o el botón del ratón) que deseas asignar. ¡El programa lo captura automáticamente!
    * **Crear Backup:** Antes de guardar, puedes hacer clic en **"Crear Backup"** para generar una copia de seguridad de tu configuración actual con la fecha y hora. ¡Ideal por si algo sale mal!

![Screenshot del Editor](![Config](Config.png)

## Tecnologías Utilizadas

* **Python 3**
* **PyQt6** para la interfaz gráfica.
* **PyInstaller** para la compilación del ejecutable.
* **GitLab CI/CD** para la compilación y publicación automática de los releases.

---

## Licencia

Este proyecto está licenciado bajo la GNU General Public License v3.0. Consulta el archivo `LICENSE` para más detalles.

