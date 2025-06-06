import sys
import os
import json
import subprocess # Importamos subprocess para ejecutar comandos externos
import shlex      # Importamos shlex para parsear comandos complejos

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QFileDialog, QMessageBox, QLabel, QListWidgetItem,
    QInputDialog # Importamos QInputDialog para pedir texto al usuario
)
from PyQt6.QtCore import Qt

# Archivo de configuración: se guarda en el directorio de inicio del usuario
CONFIG_FILE = os.path.expanduser("~/.doom_launcher_config")

class DoomLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lanzador de Doom WAD")
        # Ajustamos la altura de la ventana para acomodar los nuevos elementos de UI
        self.setGeometry(100, 100, 550, 500) 

        # Inicializamos los atributos para el directorio de WADs y el comando del motor de Doom
        self.wad_dir = None
        self.doom_engine_command = None 

        # Inicializamos los componentes de la interfaz de usuario a None
        self.wad_list_widget = None
        self.run_button = None
        self.change_dir_button = None
        self.close_button = None
        self.doom_engine_command_label = None # Etiqueta para mostrar el comando del motor
        self.config_doom_engine_button = None # Botón para configurar el comando del motor

        # Configuramos el layout principal de la ventana
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Inicializamos primero los elementos de la UI para la configuración del motor de Doom
        self._initialize_doom_engine_config_ui() 
        # Luego, inicializamos los demás componentes de la interfaz
        self._initialize_ui_components()

        # Cargamos la configuración guardada (directorio de WADs y comando del motor)
        self.load_config()

        # Lógica de configuración inicial:
        # Primero, verificamos si el comando del motor de Doom está configurado
        if not self.doom_engine_command:
            # Si no está configurado, le pedimos al usuario que lo introduzca.
            # Si el usuario cancela, cerramos la aplicación.
            if not self.ask_for_doom_engine_command(initial_setup=True):
                self.close() 

        # Después de asegurar que el motor de Doom está configurado, verificamos el directorio de WADs
        if not self.wad_dir:
            # Si el directorio de WADs no está configurado, le pedimos al usuario que lo seleccione.
            # Si el usuario cancela, mostramos un mensaje y deshabilitamos el botón de ejecución.
            if not self.ask_for_wad_dir(initial_setup=True):
                QMessageBox.information(self, "Información", 
                                        "Operación cancelada. Por favor, seleccione un directorio WAD para cargar los juegos.")
                self.wad_list_widget.clear()
                self.wad_list_widget.addItem("Directorio WAD no configurado. Haga clic en 'Cambiar Directorio WAD'.")
                self.run_button.setEnabled(False) # Deshabilitar si no hay WADs
        else:
            # Si el directorio de WADs ya está configurado, cargamos los archivos WAD de inmediato
            self.load_wad_files() 

        # Actualizamos la etiqueta que muestra el comando del motor de Doom en la UI
        self.update_doom_engine_command_label()


    def _initialize_doom_engine_config_ui(self):
        """Inicializa los elementos de la interfaz de usuario para la configuración del comando del motor de Doom."""
        engine_layout = QHBoxLayout()
        # Etiqueta para "Motor de Doom:"
        engine_label = QLabel("<b>Motor de Doom:</b>")
        engine_layout.addWidget(engine_label)

        # Etiqueta que mostrará el comando del motor de Doom actual
        self.doom_engine_command_label = QLabel("No configurado")
        # Permite seleccionar el texto de la etiqueta con el ratón
        self.doom_engine_command_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse) 
        engine_layout.addWidget(self.doom_engine_command_label)

        # Botón para configurar el comando del motor de Doom
        self.config_doom_engine_button = QPushButton("Configurar Motor Doom")
        self.config_doom_engine_button.clicked.connect(self.ask_for_doom_engine_command)
        engine_layout.addWidget(self.config_doom_engine_button)

        # Añadimos el layout de configuración del motor al layout principal
        self.main_layout.addLayout(engine_layout)
        self.main_layout.addSpacing(15) # Añadimos un poco de espacio


    def _initialize_ui_components(self):
        """Inicializa los demás widgets generales de la interfaz de usuario."""
        # Lista de archivos WAD
        self.wad_list_widget = QListWidget()
        # Conectamos el doble clic en un ítem para ejecutar el WAD
        self.wad_list_widget.itemDoubleClicked.connect(self.execute_selected_wad)
        self.main_layout.addWidget(self.wad_list_widget)

        # Layout para los botones inferiores
        button_layout = QHBoxLayout()

        # Botón "Ejecutar Doom"
        self.run_button = QPushButton("Ejecutar Doom")
        self.run_button.clicked.connect(self.on_run_button_clicked)
        # Deshabilitado por defecto hasta que se carguen WADs y el motor esté configurado
        self.run_button.setEnabled(False) 
        button_layout.addWidget(self.run_button)

        # Botón "Cambiar Directorio WAD"
        self.change_dir_button = QPushButton("Cambiar Directorio WAD")
        self.change_dir_button.clicked.connect(self.ask_for_wad_dir)
        button_layout.addWidget(self.change_dir_button)

        # Botón "Cerrar Programa"
        self.close_button = QPushButton("Cerrar Programa")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        # Añadimos el layout de botones al layout principal
        self.main_layout.addLayout(button_layout)


    def load_config(self):
        """Carga el directorio de WADs y el comando del motor de Doom desde el archivo de configuración."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.wad_dir = config.get('wad_dir')
                    self.doom_engine_command = config.get('doom_engine_command')
            except json.JSONDecodeError:
                print(f"Error al decodificar JSON desde {CONFIG_FILE}. Iniciando desde cero.")
                self.wad_dir = None
                self.doom_engine_command = None
        else:
            self.wad_dir = None
            self.doom_engine_command = None
        # Actualizamos la etiqueta de la UI en caso de que se haya cargado una configuración
        self.update_doom_engine_command_label()


    def save_config(self):
        """Guarda el directorio de WADs y el comando del motor de Doom en el archivo de configuración."""
        config = {
            'wad_dir': self.wad_dir,
            'doom_engine_command': self.doom_engine_command
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4) # Usamos 'indent' para una mejor legibilidad del archivo JSON
            print(f"Configuración guardada en {CONFIG_FILE}")
        except IOError as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la configuración: {e}")

    def update_doom_engine_command_label(self):
        """Actualiza la QLabel que muestra el comando del motor de Doom."""
        if self.doom_engine_command:
            # Mostramos una versión acortada si el comando es muy largo,
            # pero el texto completo estará disponible al pasar el ratón (tooltip).
            display_text = self.doom_engine_command
            if len(display_text) > 50: # Se puede ajustar la longitud
                display_text = display_text[:47] + "..."
            self.doom_engine_command_label.setText(f"<i>{display_text}</i>")
            self.doom_engine_command_label.setToolTip(self.doom_engine_command) # Texto completo en tooltip
        else:
            self.doom_engine_command_label.setText("<i>No configurado</i>")

    def ask_for_doom_engine_command(self, initial_setup=False):
        """
        Pide al usuario el comando del motor de Doom usando un QInputDialog.
        Retorna True si la configuración fue exitosa, False si se canceló o falló.
        """
        # Valor inicial para el QInputDialog
        initial_value = self.doom_engine_command if self.doom_engine_command else "flatpak run io.github.fabiangreffrath.Doom"
        
        # Título y texto de la ventana de diálogo
        dialog_title = "Configurar Comando del Motor de Doom"
        dialog_label = ("Introduce el comando COMPLETO o la RUTA al ejecutable de tu motor de Doom:\n\n"
                        "Ejemplos:\n"
                        "  - crispy-doom\n"
                        "  - flatpak run io.github.fabiangreffrath.Doom\n"
                        "  - /usr/games/chocolate-doom\n"
                        "  - gzdoom")
        
        # Muestra el diálogo de entrada de texto
        comando, ok = QInputDialog.getText(self, dialog_title, dialog_label, 
                                            text=initial_value)
        
        if ok and comando: # Si el usuario hizo clic en OK y se introdujo texto
            self.doom_engine_command = comando.strip() # Guardamos el comando y eliminamos espacios extra
            self.save_config() # Guardamos la configuración
            self.update_doom_engine_command_label() # Actualizamos la etiqueta en la UI
            QMessageBox.information(self, "Configuración Guardada", 
                                    f"Comando del motor de Doom guardado:\n'{self.doom_engine_command}'")
            self.load_wad_files() # Recargar WADs para habilitar el botón de ejecutar si el motor está configurado
            return True # Éxito en la configuración
        elif ok and not comando: # Si el usuario hizo clic en OK pero no introdujo texto
            QMessageBox.warning(self, "Advertencia", "No se introdujo ningún comando para el motor de Doom.")
            if initial_setup:
                return False # Si es la configuración inicial, indicamos un fallo
            return True # En otros casos, permitimos que el usuario intente de nuevo
        else: # Si el usuario canceló el diálogo
            QMessageBox.information(self, "Información", "Configuración del motor de Doom cancelada.")
            if initial_setup:
                return False # Si es la configuración inicial, indicamos un fallo para cerrar la app
            return True # En otros casos, simplemente no cambiamos la configuración


    def ask_for_wad_dir(self, initial_setup=False):
        """
        Pide al usuario que seleccione el directorio WAD.
        Retorna True si la configuración fue exitosa, False si se canceló.
        """
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setWindowTitle("Seleccione el directorio WAD")

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_dir = dialog.selectedFiles()[0]
            if selected_dir:
                self.wad_dir = selected_dir
                self.save_config()
                self.load_wad_files() # Carga los archivos después de seleccionar un nuevo directorio
                return True 
            else:
                QMessageBox.warning(self, "Advertencia", "No se seleccionó ningún directorio.")
                if initial_setup:
                    return False 
                return True
        else: # Si el usuario canceló el diálogo
            if initial_setup:
                return False 
            return True


    def load_wad_files(self):
        """Carga los archivos WAD del directorio configurado en el widget de lista."""
        self.wad_list_widget.clear()
        if self.wad_dir and os.path.exists(self.wad_dir):
            found_wads = False
            for wad_file in sorted(os.listdir(self.wad_dir)):
                if wad_file.upper().endswith(".WAD"): # Comprobación sin distinción entre mayúsculas y minúsculas
                    item = QListWidgetItem(wad_file)
                    self.wad_list_widget.addItem(item)
                    found_wads = True
            if not found_wads:
                self.wad_list_widget.addItem("No se encontraron archivos .WAD en este directorio.")
                self.run_button.setEnabled(False) # Deshabilitar el botón si no hay WADs
            else:
                # Habilitar el botón de ejecución solo si hay WADs Y el motor de Doom está configurado
                self.run_button.setEnabled(self.doom_engine_command is not None) 
        else:
            self.wad_list_widget.addItem("Directorio WAD no configurado o no existe.")
            self.run_button.setEnabled(False)


    def on_run_button_clicked(self):
        """Manejador para el clic del botón 'Ejecutar Doom'."""
        self.execute_selected_wad()


    def execute_selected_wad(self):
        """Ejecuta el WAD seleccionado usando el comando configurado del motor de Doom."""
        # Primero, verificamos que el comando del motor de Doom esté configurado
        if not self.doom_engine_command:
            QMessageBox.critical(self, "Error de Configuración", 
                                 "El comando del motor de Doom no está configurado. Por favor, configúrelo primero.")
            return

        selected_item = self.wad_list_widget.currentItem()
        if selected_item:
            wad_file_name = selected_item.text()
            if wad_file_name.upper().endswith(".WAD"):
                full_wad_path = os.path.join(self.wad_dir, wad_file_name)
                
                try:
                    # Usamos shlex.split para analizar el comando correctamente.
                    # Esto es crucial para manejar comandos con espacios o argumentos especiales (como Flatpak).
                    command_parts = shlex.split(self.doom_engine_command)
                    
                    # Añadimos el argumento -iwad con la ruta completa del WAD,
                    # solo si no está ya presente en el comando del usuario.
                    if '-iwad' not in command_parts and '--iwad' not in command_parts:
                        command_parts.extend(['-iwad', full_wad_path])
                    else:
                        # Si el usuario ya incluyó '-iwad' o '--iwad' en su comando,
                        # asumimos que lo ha gestionado. Una lógica más avanzada podría
                        # reemplazar el valor existente si se desea.
                        pass 
                    
                    print(f"Ejecutando comando: {' '.join(command_parts)}")
                    
                    # Usamos subprocess.Popen para ejecutar el comando de forma no bloqueante.
                    # Esto significa que la interfaz gráfica de tu lanzador no se congelará
                    # mientras el juego de Doom se está ejecutando.
                    # start_new_session=True ayuda a desvincular el proceso de Doom
                    # del proceso del lanzador, para que Doom siga ejecutándose incluso
                    # si cierras el lanzador.
                    subprocess.Popen(command_parts, start_new_session=True)
                    
                except FileNotFoundError:
                    QMessageBox.critical(self, "Error de Ejecución", 
                                         f"El ejecutable del motor de Doom '{command_parts[0]}' no se encontró."
                                         f"\nAsegúrate de que la ruta o el comando sean correctos y estén en tu PATH.")
                except subprocess.CalledProcessError as e:
                    # Este error ocurre si el motor de Doom se ejecuta pero devuelve un código de error
                    QMessageBox.critical(self, "Error al Ejecutar", 
                                         f"El motor de Doom falló con el código de salida {e.returncode}."
                                         f"\nComando: {e.cmd}\nSalida de error (si hay): {e.stderr.decode(errors='ignore')}")
                except Exception as e:
                    # Captura cualquier otro error inesperado
                    QMessageBox.critical(self, "Error Inesperado", 
                                         f"Ocurrió un error inesperado al intentar ejecutar Doom: {e}")
            else:
                QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un archivo .WAD válido.")
        else:
            QMessageBox.information(self, "Información", "Por favor, seleccione un archivo WAD de la lista para ejecutar.")


if __name__ == "__main__":
    # Crea la aplicación PyQt
    app = QApplication(sys.argv)
    # Crea una instancia de la ventana del lanzador
    window = DoomLauncher()
    # Muestra la ventana
    window.show()
    # Inicia el bucle de eventos de la aplicación
    sys.exit(app.exec())

