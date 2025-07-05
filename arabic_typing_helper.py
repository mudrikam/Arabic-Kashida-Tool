import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
    QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QComboBox, QSpinBox, QInputDialog, QMessageBox)
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QTextOption, QTextBlockFormat, QIcon, QGuiApplication
import qtawesome as qta
import ctypes
import os
from constants import (KEYBOARD_MAPPINGS, PEGON_MAPPING, HARAKAT_MAPPING, 
                      DEFAULT_FONTS, UI_SETTINGS)
from ui_components import UIComponentBuilder
from settings_manager import SettingsManager
from gemini_integration import GeminiIntegration

class ArabicTypingHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.active_buttons = {}
        self.original_styles = {}
        self.active_timers = {}
        self.current_modifiers = set()
        self.current_mode = "Arabic"
        
        # Initialize components
        self.settings_manager = SettingsManager()
        self.ui_builder = UIComponentBuilder(self)
        self.gemini_integration = GeminiIntegration(self)
        
        self.set_app_icon_and_id()
        self.setup_ui()
        self.setup_window()
        self.setup_keyboard_shortcuts()
        self.center_on_screen()
        self.load_saved_settings()

    def set_app_icon_and_id(self):
        icon_path = os.path.join(os.path.dirname(__file__), "appicon.ico")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            QApplication.setWindowIcon(app_icon)
            self.setWindowIcon(app_icon)
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("kashida.tool.arabic.typing.helper")
            except Exception:
                pass

    def setup_window(self):
        self.resize(*UI_SETTINGS['window_size'])
        self.setWindowTitle("Pembantu Pengetikan Arab - Edisi Lengkap")
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setMinimumSize(*UI_SETTINGS['min_size'])

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            window_geometry.moveCenter(screen_geometry.center())
            self.move(window_geometry.topLeft())

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Settings row
        settings_row = QHBoxLayout()
        mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["ABC", "Arab", "Pegon"])
        self.mode_combo.setCurrentText("Arab")
        self.mode_combo.currentTextChanged.connect(self.mode_changed)
        
        font_label = QLabel("Font:")
        self.font_combo = QComboBox()
        self.font_combo.addItems(DEFAULT_FONTS)
        self.font_combo.setCurrentText("Noto Sans Arabic")
        
        size_label = QLabel("Ukuran:")
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(20)
        
        reset_btn = QPushButton(qta.icon('fa6s.rotate-right', color='orange'), "Reset")
        reset_btn.setToolTip("Reset font dan ukuran ke default")
        
        settings_row.addWidget(mode_label)
        settings_row.addWidget(self.mode_combo)
        settings_row.addWidget(font_label)
        settings_row.addWidget(self.font_combo)
        settings_row.addWidget(size_label)
        settings_row.addWidget(self.size_spin)
        settings_row.addWidget(reset_btn)
        settings_row.addStretch()

        # API and Gemini buttons
        api_key_btn = QPushButton(qta.icon('fa6s.key', color='gold'), "")
        api_key_btn.setToolTip("Konfigurasi Kunci API Gemini")
        api_key_btn.setMinimumWidth(40)
        api_key_btn.clicked.connect(self.configure_api_key)
        settings_row.addWidget(api_key_btn)

        gemini_btn = QPushButton(qta.icon('fa6s.star', color='deepskyblue'), "")
        gemini_btn.setToolTip("Gunakan AI Gemini (buat, perbaiki, atau auto-harakat teks Arab)")
        gemini_btn.setMinimumWidth(40)
        gemini_btn.clicked.connect(self.gemini_integration.show_gemini_dialog)
        settings_row.addWidget(gemini_btn)

        main_layout.addLayout(settings_row)
        
        # Instruction label
        instruction_label = QLabel("Ketik di sini dan akan muncul dalam aksara yang dipilih - Klik tombol untuk menambah diakritik dan simbol")
        instruction_font = QFont()
        instruction_font.setPointSize(UI_SETTINGS['instruction_font_size'])
        instruction_label.setFont(instruction_font)
        instruction_label.setStyleSheet("color: #666666; margin-bottom: 5px;")
        main_layout.addWidget(instruction_label)
        
        # Text area
        self.text_area = QTextEdit()
        self.text_area.setMinimumHeight(150)
        self.text_area.setLayoutDirection(Qt.RightToLeft)
        self.text_area.setAcceptRichText(False)
        self.text_area.setAcceptDrops(True)
        self.text_area.setContextMenuPolicy(Qt.DefaultContextMenu)
        
        arabic_font = QFont()
        arabic_font.setFamily("Noto Sans Arabic")
        arabic_font.setPointSize(UI_SETTINGS['text_area_font_size'])
        arabic_font.setWeight(QFont.Normal)
        if not arabic_font.exactMatch():
            arabic_font.setFamily("Arial Unicode MS")
            if not arabic_font.exactMatch():
                arabic_font.setFamily("Times New Roman")
        self.text_area.setFont(arabic_font)
        self.text_area.setAlignment(Qt.AlignRight)
        
        doc = self.text_area.document()
        option = QTextOption()
        option.setAlignment(Qt.AlignRight)
        option.setTextDirection(Qt.RightToLeft)
        doc.setDefaultTextOption(option)
        self.text_area.installEventFilter(self)
        main_layout.addWidget(self.text_area)
        
        # Font update functions
        def update_font():
            font = QFont()
            font.setFamily(self.font_combo.currentText())
            font.setPointSize(self.size_spin.value())
            self.text_area.setFont(font)
        
        def reset_font_settings():
            self.font_combo.setCurrentText("Noto Sans Arabic")
            self.size_spin.setValue(20)
            self.text_area.clear()
            update_font()
        
        self.font_combo.currentTextChanged.connect(update_font)
        self.size_spin.valueChanged.connect(update_font)
        reset_btn.clicked.connect(reset_font_settings)
        
        # Keyboard layout
        keyboard_layout = QHBoxLayout()
        left_side = QVBoxLayout()
        
        self.letters_layout = QGridLayout()
        self.letters_layout.setSpacing(3)
        self.update_keyboard_layout()
        
        self.letters_widget = QWidget()
        self.letters_widget.setLayout(self.letters_layout)
        left_side.addWidget(self.letters_widget)
        
        # Special controls
        special_layout = self.ui_builder.create_special_controls()
        special_widget = QWidget()
        special_widget.setLayout(special_layout)
        left_side.addWidget(special_widget)
        
        keyboard_layout.addLayout(left_side)
        
        # Right side - Harakat tabs
        right_side = QVBoxLayout()
        harakat_tabs = self.ui_builder.create_harakat_tabs()
        right_side.addWidget(harakat_tabs)
        
        keyboard_layout.addLayout(right_side)
        
        keyboard_main_widget = QWidget()
        keyboard_main_widget.setLayout(keyboard_layout)
        main_layout.addWidget(keyboard_main_widget)

    def load_saved_settings(self):
        """Load saved appearance settings"""
        settings = self.settings_manager.get_appearance_settings()
        self.font_combo.setCurrentText(settings['font'])
        self.size_spin.setValue(settings['size'])
        self.mode_combo.setCurrentText(settings['mode'])

    def configure_api_key(self):
        current_key = self.settings_manager.get_api_key()
        masked_key = f"{'*' * (len(current_key) - 8)}{current_key[-8:]}" if current_key and len(current_key) > 8 else "Belum diatur"
        
        dlg = QInputDialog(self)
        dlg.setWindowTitle("Konfigurasi Kunci API Gemini")
        dlg.setLabelText(f"Kunci API Saat Ini: {masked_key}\n\nMasukkan Kunci API Gemini Baru:")
        dlg.setTextValue(current_key if current_key else "")
        dlg.setWindowIcon(qta.icon('fa6s.key', color='gold'))
        ok = dlg.exec()
        text = dlg.textValue()
        
        if ok and text.strip():
            if self.settings_manager.save_api_key(text.strip()):
                QMessageBox.information(self, "Berhasil", "Kunci API berhasil disimpan!")
            else:
                QMessageBox.warning(self, "Kesalahan", "Gagal menyimpan Kunci API ke file konfigurasi.")
        elif ok:
            QMessageBox.warning(self, "Input Tidak Valid", "Kunci API tidak boleh kosong.")

    def mode_changed(self, new_mode):
        if new_mode == "Arab":
            self.current_mode = "Arabic"
        else:
            self.current_mode = new_mode
        self.update_keyboard_layout()
        
        if new_mode == "ABC":
            self.text_area.setLayoutDirection(Qt.LeftToRight)
            doc = self.text_area.document()
            option = QTextOption()
            option.setAlignment(Qt.AlignLeft)
            option.setTextDirection(Qt.LeftToRight)
            doc.setDefaultTextOption(option)
        else:
            self.text_area.setLayoutDirection(Qt.RightToLeft)
            doc = self.text_area.document()
            option = QTextOption()
            option.setAlignment(Qt.AlignRight)
            option.setTextDirection(Qt.RightToLeft)
            doc.setDefaultTextOption(option)
        
        # Save settings
        self.settings_manager.save_appearance_settings(
            self.font_combo.currentText(),
            self.size_spin.value(),
            new_mode
        )

    def update_keyboard_layout(self):
        self.ui_builder.create_keyboard_layout()

    def get_keyboard_char(self, key):
        if self.current_mode == "Pegon":
            return self.get_pegon_mapping(key)
        mapping = self.get_keyboard_mapping()
        return mapping.get(key, key)

    def get_keyboard_mapping(self):
        return KEYBOARD_MAPPINGS.get(self.current_mode, KEYBOARD_MAPPINGS["Arabic"])

    def get_pegon_mapping(self, key, shift=False):
        modifiers = QApplication.keyboardModifiers()
        use_shift = shift or (modifiers & Qt.ShiftModifier)
        if key in PEGON_MAPPING:
            return PEGON_MAPPING[key][1] if use_shift else PEGON_MAPPING[key][0]
        return key

    def get_pegon_display(self, key):
        if key in PEGON_MAPPING:
            return PEGON_MAPPING[key][0]
        return key

    def get_harakat_mapping(self):
        return HARAKAT_MAPPING

    def button_clicked(self, character, key):
        self.insert_text(character)
        if key:
            self.highlight_button(key)

    def special_key_clicked(self, key):
        if key == 'Tab':
            self.insert_text('\t')
        elif key == 'Enter':
            self.insert_text('\n')

    def highlight_button(self, key):
        if key in self.active_buttons:
            btn = self.active_buttons[key]
            if key in self.active_timers:
                self.active_timers[key].stop()
                self.active_timers[key].deleteLater()
                del self.active_timers[key]
            if key not in self.original_styles or not self.original_styles[key]:
                self.original_styles[key] = btn.styleSheet()
            btn.setStyleSheet(f"background-color: {UI_SETTINGS['highlight_color']}; color: white;")
            
            def restore_style():
                if key in self.active_buttons:
                    btn.setStyleSheet(self.original_styles.get(key, ""))
                if key in self.active_timers:
                    self.active_timers[key].deleteLater()
                    del self.active_timers[key]
            
            timer = QTimer(self)
            timer.timeout.connect(restore_style)
            timer.setSingleShot(True)
            timer.start(UI_SETTINGS['highlight_duration'])
            self.active_timers[key] = timer

    def eventFilter(self, obj, event):
        if obj == self.text_area and event.type() == QEvent.KeyPress:
            if event.matches(QKeySequence.StandardKey.Copy):
                self.copy_text()
                self.highlight_button("copy")
                return True
            
            if event.key() == Qt.Key_Backspace:
                self.backspace()
                return True
            elif event.key() == Qt.Key_Delete:
                self.clear_text()
                return True
            elif event.key() == Qt.Key_Space:
                self.insert_text(" ")
                self.highlight_button("space")
                return True
            elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.insert_text("\n")
                return True
            elif event.key() == Qt.Key_Tab:
                self.insert_text("\t")
                return True
            
            key = event.text().lower()
            if not key:
                return False
            
            if self.current_mode == "Pegon":
                char = self.get_pegon_mapping(key, shift=event.modifiers() & Qt.ShiftModifier)
                self.insert_text(char)
                self.highlight_button(key)
                return True
            
            keyboard_mapping = self.get_keyboard_mapping()
            harakat_mapping = self.get_harakat_mapping()
            
            if key in harakat_mapping and self.current_mode != "ABC":
                self.insert_text(harakat_mapping[key])
                self.highlight_button(key)
                return True
            elif key in keyboard_mapping:
                self.insert_text(keyboard_mapping[key])
                self.highlight_button(key)
                return True
            
            return True
        return super().eventFilter(obj, event)

    def setup_keyboard_shortcuts(self):
        copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        copy_shortcut.activated.connect(self.copy_with_highlight)

    def copy_with_highlight(self):
        self.copy_text()
        self.highlight_button("copy")

    def insert_text(self, character):
        cursor = self.text_area.textCursor()
        if self.current_mode != "ABC":
            block_format = QTextBlockFormat()
            block_format.setAlignment(Qt.AlignRight)
            cursor.setBlockFormat(block_format)
        cursor.insertText(character)
        self.text_area.setTextCursor(cursor)

    def backspace(self):
        cursor = self.text_area.textCursor()
        cursor.deletePreviousChar()

    def clear_text(self):
        self.text_area.clear()

    def copy_text(self):
        text = self.text_area.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

def main():
    app = QApplication(sys.argv)
    window = ArabicTypingHelper()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()