import sys
import os
import json
import subprocess
import shlex
import shutil  # Importado para operaciones de archivos
from datetime import datetime  # Importado para la marca de tiempo

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QFileDialog, QMessageBox, QLabel, QListWidgetItem,
    QInputDialog, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QScrollArea, QSlider, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer

# Definición de la variable de configuración global.
CONFIG_FILE = os.path.expanduser("~/.doom_launcher_config")

# --- MAPAS DE TRADUCCIÓN DE TECLAS (SCAN CODES DE IBM) ---
SCAN_CODE_TO_NAME = {
    1: "Escape", 2: "1", 3: "2", 4: "3", 5: "4", 6: "5", 7: "6", 8: "7", 9: "8", 10: "9", 11: "0",
    12: "-", 13: "=", 14: "Retroceso", 15: "Tab", 16: "Q", 17: "W", 18: "E", 19: "R", 20: "T",
    21: "Y", 22: "U", 23: "I", 24: "O", 25: "P", 26: "[", 27: "]", 28: "Enter", 29: "Ctrl Izquierdo",
    30: "A", 31: "S", 32: "D", 33: "F", 34: "G", 35: "H", 36: "J", 37: "K", 38: "L", 39: ";",
    40: "'", 41: "`", 42: "Shift Izquierdo", 43: "\\", 44: "Z", 45: "X", 46: "C", 47: "V", 48: "B",
    49: "N", 50: "M", 51: ",", 52: ".", 53: "/", 54: "Shift Derecho", 55: "* (Numpad)", 56: "Alt Izquierdo",
    57: "Espacio", 58: "Bloq Mayús", 59: "F1", 60: "F2", 61: "F3", 62: "F4", 63: "F5", 64: "F6",
    65: "F7", 66: "F8", 67: "F9", 68: "F10", 69: "Bloq Num", 70: "Bloq Despl", 71: "7 (Numpad)",
    72: "Arriba", 73: "9 (Numpad)", 74: "- (Numpad)", 75: "Izquierda", 76: "5 (Numpad)",
    77: "Derecha", 78: "+ (Numpad)", 79: "1 (Numpad)", 80: "Abajo",
    81: "3 (Numpad)", 82: "Insert", 83: "Delete", 87: "F11", 88: "F12"
}

QT_KEY_TO_SCAN_CODE = {
    Qt.Key.Key_Escape: 1, Qt.Key.Key_1: 2, Qt.Key.Key_2: 3, Qt.Key.Key_3: 4, Qt.Key.Key_4: 5,
    Qt.Key.Key_5: 6, Qt.Key.Key_6: 7, Qt.Key.Key_7: 8, Qt.Key.Key_8: 9, Qt.Key.Key_9: 10,
    Qt.Key.Key_0: 11, Qt.Key.Key_Minus: 12, Qt.Key.Key_Equal: 13, Qt.Key.Key_Backspace: 14,
    Qt.Key.Key_Tab: 15, Qt.Key.Key_Q: 16, Qt.Key.Key_W: 17, Qt.Key.Key_E: 18, Qt.Key.Key_R: 19,
    Qt.Key.Key_T: 20, Qt.Key.Key_Y: 21, Qt.Key.Key_U: 22, Qt.Key.Key_I: 23, Qt.Key.Key_O: 24,
    Qt.Key.Key_P: 25, Qt.Key.Key_BracketLeft: 26, Qt.Key.Key_BracketRight: 27, Qt.Key.Key_Return: 28,
    Qt.Key.Key_Enter: 28, Qt.Key.Key_Control: 29, Qt.Key.Key_A: 30, Qt.Key.Key_S: 31, Qt.Key.Key_D: 32,
    Qt.Key.Key_F: 33, Qt.Key.Key_G: 34, Qt.Key.Key_H: 35, Qt.Key.Key_J: 36, Qt.Key.Key_K: 37,
    Qt.Key.Key_L: 38, Qt.Key.Key_Semicolon: 39, Qt.Key.Key_Apostrophe: 40, Qt.Key.Key_Agrave: 41,
    Qt.Key.Key_Shift: 42, Qt.Key.Key_Backslash: 43, Qt.Key.Key_Z: 44, Qt.Key.Key_X: 45, Qt.Key.Key_C: 46,
    Qt.Key.Key_V: 47, Qt.Key.Key_B: 48, Qt.Key.Key_N: 49, Qt.Key.Key_M: 50, Qt.Key.Key_Comma: 51,
    Qt.Key.Key_Period: 52, Qt.Key.Key_Slash: 53, Qt.Key.Key_Asterisk: 55, Qt.Key.Key_Alt: 56,
    Qt.Key.Key_Space: 57, Qt.Key.Key_CapsLock: 58, Qt.Key.Key_F1: 59, Qt.Key.Key_F2: 60,
    Qt.Key.Key_F3: 61, Qt.Key.Key_F4: 62, Qt.Key.Key_F5: 63, Qt.Key.Key_F6: 64, Qt.Key.Key_F7: 65,
    Qt.Key.Key_F8: 66, Qt.Key.Key_F9: 67, Qt.Key.Key_F10: 68, Qt.Key.Key_NumLock: 69,
    Qt.Key.Key_ScrollLock: 70, Qt.Key.Key_Up: 72, Qt.Key.Key_Left: 75, Qt.Key.Key_Right: 77,
    Qt.Key.Key_Down: 80, Qt.Key.Key_Insert: 82, Qt.Key.Key_Delete: 83, Qt.Key.Key_F11: 87,
    Qt.Key.Key_F12: 88,
}

MOUSE_BUTTON_TO_NAME = {
    0: "Botón Izquierdo", 1: "Botón Derecho", 2: "Botón Central", 3: "Botón 4",
    -1: "Sin Asignar"
}


class KeyCaptureButton(QPushButton):
    """Un botón que puede capturar teclas del teclado o botones del ratón."""
    def __init__(self, capture_type, initial_value, parent=None):
        super().__init__(parent)
        self.capture_type = capture_type  # 'key' o 'mouse'
        self.value = -1
        try:
            self.value = int(initial_value)
        except (ValueError, TypeError):
            pass  # Si el valor no es un número, se queda en -1
        
        self.is_capturing = False
        self.update_text()
        self.clicked.connect(self.start_capture)

    def start_capture(self):
        self.is_capturing = True
        self.setText("[ Presiona un botón... ]")
        self.grabKeyboard()

    def stop_capture(self):
        self.is_capturing = False
        self.update_text()
        self.releaseKeyboard()

    def keyPressEvent(self, event):
        if self.is_capturing and self.capture_type == 'key':
            qt_key = event.key()
            if qt_key in QT_KEY_TO_SCAN_CODE:
                self.value = QT_KEY_TO_SCAN_CODE[qt_key]
            else:
                QMessageBox.warning(self, "Tecla no reconocida", "La tecla presionada no tiene un Scan Code de IBM conocido.")
            self.stop_capture()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if not self.is_capturing:
            super().mousePressEvent(event)
            return

        if self.is_capturing and self.capture_type == 'mouse':
            button_map = {Qt.MouseButton.LeftButton: 0, Qt.MouseButton.RightButton: 1, Qt.MouseButton.MiddleButton: 2}
            if event.button() in button_map:
                self.value = button_map[event.button()]
            else:
                QMessageBox.warning(self, "Botón no reconocido", "Solo se reconocen los botones izquierdo, derecho y central.")
            self.stop_capture()
        else:
            super().mousePressEvent(event)
            
    def update_text(self):
        """Actualiza el texto del botón con el nombre legible del control."""
        if self.capture_type == 'key':
            display_name = SCAN_CODE_TO_NAME.get(self.value, f"Desconocido ({self.value})")
        elif self.capture_type == 'mouse':
            display_name = MOUSE_BUTTON_TO_NAME.get(self.value, f"Desconocido ({self.value})")
        else:
            display_name = "Error"
        self.setText(display_name)

    def get_value(self):
        """Devuelve el valor numérico para guardarlo en el .cfg."""
        return str(self.value)


class ConfigEditorDialog(QDialog):
    """Diálogo para editar el archivo de configuración (default.cfg)."""
    def __init__(self, config_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editor de Configuración de Doom")
        self.config_path = config_path
        self.setGeometry(150, 150, 500, 600)

        form_layout = QFormLayout()
        self.editor_widgets = {}

        # Definimos qué claves usarán qué widgets especiales
        SLIDER_KEYS = ['sfx_volume', 'music_volume', 'mouse_sensitivity', 'mouse_sensitivity_x2', 'mouse_sensitivity_y']
        CHECKBOX_KEYS = ['use_mouse', 'show_messages', 'use_joystick', 'usegamma']
        
        try:
            with open(self.config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith(';'):
                        continue

                    parts = shlex.split(line, comments=True)
                    if len(parts) < 2:
                        key, value = parts[0], ""
                    else:
                        key, value = parts[0], parts[1]

                    # --- Lógica de selección de widgets mejorada ---
                    if key in SLIDER_KEYS:
                        editor = QSlider(Qt.Orientation.Horizontal)
                        # Rango diferente para volumen vs sensibilidad
                        range_max = 15 if 'volume' in key else 9
                        editor.setRange(0, range_max)
                        editor.setTickPosition(QSlider.TickPosition.TicksBelow)
                        try:
                            editor.setValue(int(value))
                        except (ValueError, TypeError):
                            editor.setValue(0)
                    elif key in CHECKBOX_KEYS:
                        editor = QCheckBox()
                        editor.setChecked(value == '1')
                    elif key.startswith('key_'):
                        editor = KeyCaptureButton('key', value)
                    elif key.startswith('mouseb_'):
                        editor = KeyCaptureButton('mouse', value)
                    else:
                        editor = QLineEdit(value)
                    
                    form_layout.addRow(QLabel(key), editor)
                    self.editor_widgets[key] = editor

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer el archivo de configuración:\n{e}")
            QTimer.singleShot(0, self.reject)
            return

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        container_widget = QWidget()
        container_widget.setLayout(form_layout)
        scroll_area.setWidget(container_widget)

        button_box = QDialogButtonBox()
        backup_button = button_box.addButton("Crear Backup", QDialogButtonBox.ButtonRole.ActionRole)
        button_box.addButton(QDialogButtonBox.StandardButton.Save)
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        
        backup_button.clicked.connect(self.create_backup)
        button_box.accepted.connect(self.save_config)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(button_box)

    def create_backup(self):
        """Crea una copia de seguridad del archivo de configuración con una marca de tiempo."""
        try:
            base_path, extension = os.path.splitext(self.config_path)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_path = f"{base_path}_{timestamp}.bak"
            shutil.copy2(self.config_path, backup_path)
            QMessageBox.information(self, "Backup Creado", 
                                    f"Se ha creado una copia de seguridad en:\n{backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error de Backup", 
                                 f"No se pudo crear la copia de seguridad:\n{e}")

    def save_config(self):
        """Reescribe el archivo .cfg con los nuevos valores del formulario."""
        try:
            with open(self.config_path, 'w') as f:
                for key, widget in self.editor_widgets.items():
                    # --- Lógica de guardado mejorada ---
                    if isinstance(widget, KeyCaptureButton):
                        value = widget.get_value()
                    elif isinstance(widget, QSlider):
                        value = str(widget.value())
                    elif isinstance(widget, QCheckBox):
                        value = '1' if widget.isChecked() else '0'
                    else: # QLineEdit
                        value = widget.text()
                        if key.startswith('chatmacro'):
                            value = f'"{value}"'
                    
                    f.write(f"{key.ljust(30)}{value}\n")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la configuración:\n{e}")


class DoomLauncher(QWidget):
    # El resto de esta clase es idéntico a la versión anterior.
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lanzador de Doom WAD")
        self.setGeometry(100, 100, 550, 500)

        self.wad_dir = None
        self.doom_engine_command = None
        self.default_cfg_path = None

        self.wad_list_widget = None
        self.run_button = None
        self.change_dir_button = None
        self.close_button = None
        self.edit_config_button = None
        self.doom_engine_command_label = None
        self.config_doom_engine_button = None

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self._initialize_doom_engine_config_ui()
        self._initialize_ui_components()

        self.load_config()

        if not self.doom_engine_command:
            if not self.ask_for_doom_engine_command(initial_setup=True):
                self.close()

        if not self.wad_dir:
            if not self.ask_for_wad_dir(initial_setup=True):
                QMessageBox.information(self, "Información",
                                        "Operación cancelada. Por favor, seleccione un directorio WAD para cargar los juegos.")
                self.wad_list_widget.clear()
                self.wad_list_widget.addItem("Directorio WAD no configurado. Haga clic en 'Cambiar Directorio WAD'.")
                self.run_button.setEnabled(False)
        else:
            self.load_wad_files()

        self.update_doom_engine_command_label()

    def _initialize_doom_engine_config_ui(self):
        engine_layout = QHBoxLayout()
        engine_label = QLabel("<b>Motor de Doom:</b>")
        engine_layout.addWidget(engine_label)
        self.doom_engine_command_label = QLabel("No configurado")
        self.doom_engine_command_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        engine_layout.addWidget(self.doom_engine_command_label)
        self.config_doom_engine_button = QPushButton("Configurar Motor Doom")
        self.config_doom_engine_button.clicked.connect(self.ask_for_doom_engine_command)
        engine_layout.addWidget(self.config_doom_engine_button)
        self.main_layout.addLayout(engine_layout)
        self.main_layout.addSpacing(15)

    def _initialize_ui_components(self):
        self.wad_list_widget = QListWidget()
        self.wad_list_widget.itemDoubleClicked.connect(self.execute_selected_wad)
        self.main_layout.addWidget(self.wad_list_widget)
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Ejecutar Doom")
        self.run_button.clicked.connect(self.on_run_button_clicked)
        self.run_button.setEnabled(False)
        button_layout.addWidget(self.run_button)
        self.edit_config_button = QPushButton("Editar Configuración")
        self.edit_config_button.clicked.connect(self.open_config_editor)
        button_layout.addWidget(self.edit_config_button)
        self.change_dir_button = QPushButton("Cambiar Directorio WAD")
        self.change_dir_button.clicked.connect(self.ask_for_wad_dir)
        button_layout.addWidget(self.change_dir_button)
        self.close_button = QPushButton("Cerrar Programa")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        self.main_layout.addLayout(button_layout)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.wad_dir = config.get('wad_dir')
                    self.doom_engine_command = config.get('doom_engine_command')
                    self.default_cfg_path = config.get('default_cfg_path')
            except json.JSONDecodeError:
                print(f"Error al decodificar JSON desde {CONFIG_FILE}. Iniciando desde cero.")
                self.wad_dir = self.doom_engine_command = self.default_cfg_path = None
        else:
            self.wad_dir = self.doom_engine_command = self.default_cfg_path = None
        self.update_doom_engine_command_label()

    def save_config(self):
        config = {
            'wad_dir': self.wad_dir,
            'doom_engine_command': self.doom_engine_command,
            'default_cfg_path': self.default_cfg_path
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Configuración guardada en {CONFIG_FILE}")
        except IOError as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la configuración: {e}")

    def open_config_editor(self):
        if not self.default_cfg_path or not os.path.exists(self.default_cfg_path):
            if not self.ask_for_default_cfg_path():
                 QMessageBox.warning(self, "Operación Cancelada", "No se seleccionó un archivo de configuración válido.")
                 return

        if self.default_cfg_path and os.path.exists(self.default_cfg_path):
            dialog = ConfigEditorDialog(self.default_cfg_path, self)
            dialog.exec()

    def ask_for_default_cfg_path(self):
        dialog = QFileDialog()
        dialog.setWindowTitle("Selecciona tu archivo de configuración (default.cfg)")
        dialog.setNameFilter("Archivos de Configuración (*.cfg)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_file = dialog.selectedFiles()[0]
            if selected_file:
                self.default_cfg_path = selected_file
                self.save_config()
                return True
        return False
        
    def update_doom_engine_command_label(self):
        if self.doom_engine_command:
            display_text = self.doom_engine_command
            if len(display_text) > 50:
                display_text = display_text[:47] + "..."
            self.doom_engine_command_label.setText(f"<i>{display_text}</i>")
            self.doom_engine_command_label.setToolTip(self.doom_engine_command)
        else:
            self.doom_engine_command_label.setText("<i>No configurado</i>")

    def ask_for_doom_engine_command(self, initial_setup=False):
        initial_value = self.doom_engine_command if self.doom_engine_command else "crispy-doom"
        dialog_title = "Configurar Comando del Motor de Doom"
        dialog_label = ("Introduce el comando COMPLETO o la RUTA al ejecutable de tu motor de Doom:\n\n"
                        "Ejemplos:\n"
                        "  - crispy-doom\n"
                        "  - flatpak run io.github.fabiangreffrath.Doom\n"
                        "  - /usr/games/chocolate-doom\n"
                        "  - gzdoom")
        comando, ok = QInputDialog.getText(self, dialog_title, dialog_label, text=initial_value)
        if ok and comando:
            self.doom_engine_command = comando.strip()
            self.save_config()
            self.update_doom_engine_command_label()
            QMessageBox.information(self, "Configuración Guardada",
                                    f"Comando del motor de Doom guardado:\n'{self.doom_engine_command}'")
            self.load_wad_files()
            return True
        elif ok and not comando:
            QMessageBox.warning(self, "Advertencia", "No se introdujo ningún comando para el motor de Doom.")
            if initial_setup: return False
            return True
        else:
            QMessageBox.information(self, "Información", "Configuración del motor de Doom cancelada.")
            if initial_setup: return False
            return True

    def ask_for_wad_dir(self, initial_setup=False):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setWindowTitle("Seleccione el directorio WAD")
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_dir = dialog.selectedFiles()[0]
            if selected_dir:
                self.wad_dir = selected_dir
                self.save_config()
                self.load_wad_files()
                return True
            else:
                QMessageBox.warning(self, "Advertencia", "No se seleccionó ningún directorio.")
                if initial_setup: return False
                return True
        else:
            if initial_setup: return False
            return True

    def load_wad_files(self):
        self.wad_list_widget.clear()
        if self.wad_dir and os.path.exists(self.wad_dir):
            found_wads = False
            for wad_file in sorted(os.listdir(self.wad_dir)):
                if wad_file.upper().endswith(".WAD"):
                    item = QListWidgetItem(wad_file)
                    self.wad_list_widget.addItem(item)
                    found_wads = True
            if not found_wads:
                self.wad_list_widget.addItem("No se encontraron archivos .WAD en este directorio.")
                self.run_button.setEnabled(False)
            else:
                self.run_button.setEnabled(self.doom_engine_command is not None)
        else:
            self.wad_list_widget.addItem("Directorio WAD no configurado o no existe.")
            self.run_button.setEnabled(False)

    def on_run_button_clicked(self):
        self.execute_selected_wad()

    def execute_selected_wad(self):
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
                    command_parts = shlex.split(self.doom_engine_command)
                    if '-iwad' not in command_parts and '--iwad' not in command_parts:
                        command_parts.extend(['-iwad', full_wad_path])
                    
                    print(f"Ejecutando comando: {' '.join(command_parts)}")
                    subprocess.Popen(command_parts, start_new_session=True)

                except FileNotFoundError:
                    QMessageBox.critical(self, "Error de Ejecución",
                                         f"El ejecutable del motor de Doom '{command_parts[0]}' no se encontró.\n"
                                         f"Asegúrate de que la ruta o el comando sean correctos y estén en tu PATH.")
                except subprocess.CalledProcessError as e:
                    QMessageBox.critical(self, "Error al Ejecutar",
                                         f"El motor de Doom falló con el código de salida {e.returncode}.\n"
                                         f"Comando: {e.cmd}\nSalida de error (si hay): {e.stderr.decode(errors='ignore')}")
                except Exception as e:
                    QMessageBox.critical(self, "Error Inesperado",
                                         f"Ocurrió un error inesperado al intentar ejecutar Doom: {e}")
            else:
                QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un archivo .WAD válido.")
        else:
            QMessageBox.information(self, "Información", "Por favor, seleccione un archivo WAD de la lista para ejecutar.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DoomLauncher()
    window.show()
    sys.exit(app.exec())
