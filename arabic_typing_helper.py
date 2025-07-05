import sys
import subprocess
import pkg_resources
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
    QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QComboBox, QSpinBox, QTabWidget, QScrollArea, QInputDialog, QMessageBox, QProgressDialog)
from PySide6.QtCore import Qt, QPoint, QEvent, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QKeyEvent, QTextOption, QTextBlockFormat, QIcon, QGuiApplication
import qtawesome as qta
import ctypes
import os
import json
from gemini_ai_helper import request_gemini
from gemini_response_helper import parse_gemini_response

def check_and_install_requirements():
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if not os.path.exists(req_file):
        return
    with open(req_file) as f:
        required = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = []
    for req in required:
        pkg_name = req.split(">=")[0].split("==")[0].lower()
        if pkg_name not in installed:
            missing.append(req)
    if missing:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        except Exception as e:
            QMessageBox.critical(None, "Instalasi Paket Gagal", f"Gagal menginstal paket: {missing}\n{e}")

check_and_install_requirements()

class GeminiWorker(QThread):
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt
    
    def run(self):
        try:
            response = request_gemini(self.prompt)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))

class ArabicTypingHelper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.active_buttons = {}
        self.original_styles = {}
        self.active_timers = {}
        self.current_modifiers = set()
        self.current_mode = "Arabic"
        self.gemini_worker = None
        self.progress_dialog = None
        self.set_app_icon_and_id()
        self.setup_ui()
        self.setup_window()
        self.setup_keyboard_shortcuts()
        self.center_on_screen()

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
        self.resize(1200, 600)
        self.setWindowTitle("Pembantu Pengetikan Arab - Edisi Lengkap")
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setMinimumSize(800, 400)

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
        settings_row = QHBoxLayout()
        mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["ABC", "Arab", "Pegon"])
        self.mode_combo.setCurrentText("Arab")
        self.mode_combo.currentTextChanged.connect(self.mode_changed)
        font_label = QLabel("Font:")
        self.font_combo = QComboBox()
        self.font_combo.addItems([
            "Noto Sans Arabic", "Arial Unicode MS", "Times New Roman", "Tahoma", "Amiri", "Scheherazade"
        ])
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

        api_key_btn = QPushButton(qta.icon('fa6s.key', color='gold'), "")
        api_key_btn.setToolTip("Konfigurasi Kunci API Gemini")
        api_key_btn.setMinimumWidth(40)
        api_key_btn.clicked.connect(self.configure_api_key)
        settings_row.addWidget(api_key_btn)

        gemini_btn = QPushButton(qta.icon('fa6s.star', color='deepskyblue'), "")
        gemini_btn.setToolTip("Gunakan AI Gemini (buat, perbaiki, atau auto-harakat teks Arab)")
        gemini_btn.setMinimumWidth(40)
        gemini_btn.clicked.connect(self.use_gemini_dialog)
        settings_row.addWidget(gemini_btn)

        main_layout.addLayout(settings_row)
        instruction_label = QLabel("Ketik di sini dan akan muncul dalam aksara yang dipilih - Klik tombol untuk menambah diakritik dan simbol")
        instruction_font = QFont()
        instruction_font.setPointSize(14)
        instruction_label.setFont(instruction_font)
        instruction_label.setStyleSheet("color: #666666; margin-bottom: 5px;")
        main_layout.addWidget(instruction_label)
        self.text_area = QTextEdit()
        self.text_area.setMinimumHeight(150)
        self.text_area.setLayoutDirection(Qt.RightToLeft)
        self.text_area.setAcceptRichText(False)
        self.text_area.setAcceptDrops(True)
        self.text_area.setContextMenuPolicy(Qt.DefaultContextMenu)
        arabic_font = QFont()
        arabic_font.setFamily("Noto Sans Arabic")
        arabic_font.setPointSize(20)
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
        def update_font():
            font = QFont()
            font.setFamily(self.font_combo.currentText())
            font.setPointSize(self.size_spin.value())
            self.text_area.setFont(font)
        def reset_font_settings():
            self.font_combo.setCurrentText("Noto Sans Arabic")
            self.size_spin.setValue(20)
            update_font()
        self.font_combo.currentTextChanged.connect(update_font)
        self.size_spin.valueChanged.connect(update_font)
        reset_btn.clicked.connect(reset_font_settings)
        keyboard_layout = QHBoxLayout()
        left_side = QVBoxLayout()
        self.letters_layout = QGridLayout()
        self.letters_layout.setSpacing(3)
        self.update_keyboard_layout()
        self.letters_widget = QWidget()
        self.letters_widget.setLayout(self.letters_layout)
        left_side.addWidget(self.letters_widget)
        special_layout = QHBoxLayout()
        space_btn = QPushButton(qta.icon('fa6s.shuttle-space', color='limegreen'), "Spasi")
        space_btn.setToolTip("Tekan Spasi")
        btn_font = QFont()
        btn_font.setPointSize(14)
        space_btn.setFont(btn_font)
        space_btn.setMinimumHeight(40)
        space_btn.setMinimumWidth(300)
        space_btn.clicked.connect(lambda: self.button_clicked(" ", "space"))
        special_layout.addWidget(space_btn)
        self.active_buttons["space"] = space_btn
        self.original_styles["space"] = ""
        special_widget = QWidget()
        special_widget.setLayout(special_layout)
        left_side.addWidget(special_widget)
        keyboard_layout.addLayout(left_side)
        right_side = QVBoxLayout()
        harakat_tabs = QTabWidget()
        harakat_tabs.setMaximumWidth(350)
        basic_tab = QWidget()
        basic_layout = QGridLayout()
        basic_layout.setSpacing(5)
        basic_harakat_chars = [
            ('ٍ', 'Tanwin Kasrah', '7'),
            ('ٌ', 'Tanwin Dammah', '8'),
            ('ـ', 'Kashida', '9'),
            ('ْ', 'Sukun', '4'),
            ('ّ', 'Shaddah', '5'),
            ('ً', 'Tanwin Fathah', '6'),
            ('َ', 'Fathah', '1'),
            ('ِ', 'Kasrah', '2'),
            ('ُ', 'Dammah', '3'),
            ('\u0619', 'Dammah Kecil', '0'),
        ]
        for idx, (char, name, key) in enumerate(basic_harakat_chars):
            if key == '0':
                row = 3
                col = 1
            else:
                row = idx // 3
                col = idx % 3
            btn = QPushButton(f"{char}\n{key}")
            btn_font = QFont()
            btn_font.setPointSize(22)
            btn.setFont(btn_font)
            btn.setStyleSheet("QPushButton { font-size: 22px; } QPushButton QLabel { font-size: 10px; }")
            btn.setToolTip(f"{name} - Tekan {key}")
            btn.setMinimumHeight(60)
            btn.setMinimumWidth(80)
            btn.clicked.connect(lambda checked, c=char, k=key: self.button_clicked(c, k))
            basic_layout.addWidget(btn, row, col)
            self.active_buttons[key] = btn
            self.original_styles[key] = ""
        basic_tab.setLayout(basic_layout)
        harakat_tabs.addTab(basic_tab, "Dasar")
        advanced_scroll = QScrollArea()
        advanced_scroll.setWidgetResizable(True)
        advanced_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        advanced_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        advanced_content = QWidget()
        advanced_layout = QGridLayout()
        advanced_layout.setSpacing(3)
        advanced_harakat_chars = [
            ('\u064B', 'Fathah Ganda'),
            ('\u064D', 'Kasrah Ganda'),
            ('\u064C', 'Dammah Ganda'),
            ('\u0652', 'Sukun'),
            ('\u0651', 'Shaddah'),
            ('\u0670', 'Alef Atas'),
            ('\u0656', 'Alef Bawah'),
            ('\u065F', 'Hamza Bergelombang Bawah'),
            ('\u0640', 'Tatweel'),
            ('\u064E', 'Fathah'),
            ('\u0650', 'Kasrah'),
            ('\u064F', 'Dammah'),
            ('\u0653', 'Maddah'),
            ('\u0654', 'Hamza Atas'),
            ('\u0655', 'Hamza Bawah'),
            ('\u0657', 'Dammah Terbalik'),
            ('\u0658', 'Tanda Nun Ghunnah'),
            ('\u0659', 'Zwarakay'),
            ('\u065A', 'Tanda Vokal V Kecil'),
            ('\u065B', 'Tanda Vokal V Kecil Terbalik'),
            ('\u065C', 'Tanda Vokal Titik Bawah'),
            ('\u065D', 'Dammah Terbalik'),
            ('\u065E', 'Fathah Dua Titik'),
            ('\u0660', 'Angka Arab-Hindi Nol'),
            ('\u0661', 'Angka Arab-Hindi Satu'),
            ('\u0662', 'Angka Arab-Hindi Dua'),
            ('\u0663', 'Angka Arab-Hindi Tiga'),
        ]
        for idx, (char, name) in enumerate(advanced_harakat_chars):
            row = idx // 3
            col = idx % 3
            btn = QPushButton(char)
            btn_font = QFont()
            btn_font.setPointSize(20)
            btn.setFont(btn_font)
            btn.setToolTip(name)
            btn.setMinimumHeight(60)
            btn.setMinimumWidth(80)
            btn.clicked.connect(lambda checked, c=char: self.button_clicked(c, ""))
            advanced_layout.addWidget(btn, row, col)
        advanced_content.setLayout(advanced_layout)
        advanced_scroll.setWidget(advanced_content)
        harakat_tabs.addTab(advanced_scroll, "Lanjutan")
        symbols_scroll = QScrollArea()
        symbols_scroll.setWidgetResizable(True)
        symbols_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        symbols_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        symbols_content = QWidget()
        symbols_layout = QGridLayout()
        symbols_layout.setSpacing(3)
        symbol_chars = [
            ('؟', 'Tanda Tanya'),
            ('؛', 'Titik Koma'),
            ('،', 'Koma'),
            ('؎', 'Pemisah Tanggal'),
            ('؏', 'Penanda Catatan Kaki'),
            ('ؐ', 'Tanda Sallallaahu Alayhe Wasallam'),
            ('ؑ', 'Tanda Alayhe Assallam'),
            ('ؒ', 'Tanda Rahmatullahi Alayhe'),
            ('ؓ', 'Tanda Radi Allaahu Anhu'),
            ('ؔ', 'Tanda Radi Allaahu Anha'),
            ('؈', 'Sinar'),
            ('؉', 'Rub El Hizb'),
            ('؊', 'Takhallus'),
            ('؋', 'Tanda Afghani'),
            ('؍', 'Misra'),
            ('\u06DD', 'Akhir Ayat'),
            ('\u06DE', 'Awal Rub El Hizb'),
            ('\u06DF', 'Tiga Titik Atas'),
        ]
        for idx, (char, name) in enumerate(symbol_chars):
            row = idx // 3
            col = idx % 3
            btn = QPushButton(char)
            btn_font = QFont()
            btn_font.setPointSize(20)
            btn.setFont(btn_font)
            btn.setToolTip(name)
            btn.setMinimumHeight(60)
            btn.setMinimumWidth(80)
            btn.clicked.connect(lambda checked, c=char: self.button_clicked(c, ""))
            symbols_layout.addWidget(btn, row, col)
        symbols_content.setLayout(symbols_layout)
        symbols_scroll.setWidget(symbols_content)
        harakat_tabs.addTab(symbols_scroll, "Simbol")
        right_side.addWidget(harakat_tabs)
        keyboard_layout.addLayout(right_side)
        keyboard_main_widget = QWidget()
        keyboard_main_widget.setLayout(keyboard_layout)
        main_layout.addWidget(keyboard_main_widget)

    def create_progress_dialog(self, title, message):
        progress = QProgressDialog(message, "Batal", 0, 0, self)
        progress.setWindowTitle(title)
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(True)
        progress.setAutoReset(True)
        progress.setMinimumDuration(0)
        progress.setWindowIcon(qta.icon('fa6s.star', color='deepskyblue'))
        progress.show()
        return progress

    def configure_api_key(self):
        current_key = self.get_current_api_key()
        masked_key = f"{'*' * (len(current_key) - 8)}{current_key[-8:]}" if current_key and len(current_key) > 8 else "Belum diatur"
        
        dlg = QInputDialog(self)
        dlg.setWindowTitle("Konfigurasi Kunci API Gemini")
        dlg.setLabelText(f"Kunci API Saat Ini: {masked_key}\n\nMasukkan Kunci API Gemini Baru:")
        dlg.setTextValue(current_key if current_key else "")
        dlg.setWindowIcon(qta.icon('fa6s.key', color='gold'))
        ok = dlg.exec()
        text = dlg.textValue()
        
        if ok and text.strip():
            if self.save_api_key(text.strip()):
                QMessageBox.information(self, "Berhasil", "Kunci API berhasil disimpan!")
            else:
                QMessageBox.warning(self, "Kesalahan", "Gagal menyimpan Kunci API ke file konfigurasi.")
        elif ok:
            QMessageBox.warning(self, "Input Tidak Valid", "Kunci API tidak boleh kosong.")

    def get_current_api_key(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            try:
                config_path = os.path.join(os.path.dirname(__file__), "config.json")
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    api_key = config.get("gemini", {}).get("api_key")
            except:
                pass
        return api_key

    def save_api_key(self, api_key):
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
            
            if "gemini" not in config:
                config["gemini"] = {}
            
            config["gemini"]["api_key"] = api_key
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception:
            return False

    def on_gemini_finished(self, response):
        print("=== RAW GEMINI RESPONSE ===")
        print(response)
        print("==========================")
        self.progress_dialog.close()
        self.progress_dialog = None
        
        parsed = parse_gemini_response(response)
        if parsed:
            self.text_area.setPlainText(parsed)
        else:
            QMessageBox.warning(self, "Peringatan Gemini", "Tidak ada hasil valid yang ditemukan dalam respons.")
        
        self.gemini_worker = None

    def on_gemini_error(self, error_message):
        self.progress_dialog.close()
        self.progress_dialog = None
        QMessageBox.critical(self, "Kesalahan Gemini", f"Kesalahan: {error_message}")
        self.gemini_worker = None

    def on_progress_cancelled(self):
        if self.gemini_worker and self.gemini_worker.isRunning():
            self.gemini_worker.terminate()
            self.gemini_worker.wait()
        self.gemini_worker = None

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

    def update_keyboard_layout(self):
        for i in reversed(range(self.letters_layout.count())):
            child = self.letters_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        self.active_buttons = {k: v for k, v in self.active_buttons.items() if k in ["space", "copy"]}
        keyboard_mapping = self.get_keyboard_mapping()
        keyboard_rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '⌫'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Enter'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'Del', 'Salin']
        ]
        for row_idx, row in enumerate(keyboard_rows):
            for col_idx, key in enumerate(row):
                if key == '⌫':
                    btn = QPushButton(qta.icon('fa6s.delete-left', color='red'), "")
                    btn.setToolTip("Backspace - Hapus karakter sebelumnya")
                    btn_font = QFont()
                    btn_font.setPointSize(16)
                    btn.setFont(btn_font)
                    btn.setMinimumHeight(60)
                    btn.clicked.connect(self.backspace)
                elif key == 'Del':
                    btn = QPushButton(qta.icon('fa6s.trash', color='orange'), "Hapus")
                    btn.setToolTip("Hapus Semua - Hapus semua teks")
                    btn_font = QFont()
                    btn_font.setPointSize(14)
                    btn.setFont(btn_font)
                    btn.setMinimumHeight(60)
                    btn.clicked.connect(self.clear_text)
                elif key == 'Salin':
                    btn = QPushButton(qta.icon('fa6s.copy', color='deepskyblue'), "Salin")
                    btn.setToolTip("Salin teks ke clipboard - Ctrl+C")
                    btn_font = QFont()
                    btn_font.setPointSize(14)
                    btn.setFont(btn_font)
                    btn.setMinimumHeight(60)
                    btn.clicked.connect(self.copy_text)
                    self.active_buttons["copy"] = btn
                    self.original_styles["copy"] = ""
                elif key == 'Enter':
                    btn = QPushButton(qta.icon('fa6s.arrow-turn-down', color='green'), "Enter")
                    btn.setToolTip("Tombol Enter")
                    btn_font = QFont()
                    btn_font.setPointSize(14)
                    btn.setFont(btn_font)
                    btn.setMinimumHeight(60)
                    btn.setMinimumWidth(100)
                    btn.clicked.connect(lambda checked, k=key: self.special_key_clicked(k))
                else:
                    mapped_char = self.get_keyboard_char(key.lower())
                    if self.current_mode == "Pegon":
                        mapped_char = self.get_pegon_display(key.lower())
                    if self.current_mode == "ABC":
                        btn = QPushButton(f"{key}\n{mapped_char}")
                    else:
                        btn = QPushButton(f"{mapped_char}\n{key}")
                    btn_font = QFont()
                    btn_font.setPointSize(16)
                    btn.setFont(btn_font)
                    btn.setToolTip(f"Karakter: {mapped_char} | Tombol: {key}")
                    btn.setMinimumHeight(60)
                    btn.clicked.connect(lambda checked, c=self.get_keyboard_char(key.lower()), k=key.lower(): self.button_clicked(c, k))
                    self.active_buttons[key.lower()] = btn
                    self.original_styles[key.lower()] = ""
                self.letters_layout.addWidget(btn, row_idx, col_idx)

    def get_keyboard_char(self, key):
        if self.current_mode == "Pegon":
            return self.get_pegon_mapping(key)
        mapping = self.get_keyboard_mapping()
        return mapping.get(key, key)

    def get_keyboard_mapping(self):
        if self.current_mode == "ABC":
            return {
                'q': 'q', 'w': 'w', 'e': 'e', 'r': 'r', 't': 't',
                'y': 'y', 'u': 'u', 'i': 'i', 'o': 'o', 'p': 'p',
                'a': 'a', 's': 's', 'd': 'd', 'f': 'f', 'g': 'g',
                'h': 'h', 'j': 'j', 'k': 'k', 'l': 'l',
                'z': 'z', 'x': 'x', 'c': 'c', 'v': 'v', 'b': 'b',
                'n': 'n', 'm': 'm'
            }
        elif self.current_mode == "Arabic":
            return {
                'q': 'ض', 'w': 'ص', 'e': 'ث', 'r': 'ق', 't': 'ف',
                'y': 'غ', 'u': 'ع', 'i': 'ه', 'o': 'خ', 'p': 'ح',
                'a': 'ش', 's': 'س', 'd': 'ي', 'f': 'ب', 'g': 'ل',
                'h': 'ا', 'j': 'ت', 'k': 'ن', 'l': 'م',
                'z': 'ئ', 'x': 'ء', 'c': 'ؤ', 'v': 'ر', 'b': 'ﻻ',
                'n': 'ى', 'm': 'ة'
            }
        elif self.current_mode == "Pegon":
            return {}

    def get_pegon_mapping(self, key, shift=False):
        pegon_map = {
            'q': ('ق', 'ك'), 'w': ('و', 'ؤ'), 'e': ('ء', 'ئ'), 'r': ('ر', 'ذ'), 't': ('ت', 'ث'),
            'y': ('ي', 'ى'), 'u': ('ى', 'ء'), 'i': ('ا', 'إ'), 'o': ('ه', 'ة'), 'p': ('ط', 'ظ'),
            'a': ('ا', 'أ'), 's': ('ش', 'س'), 'd': ('د', 'ض'), 'f': ('ق', 'غ'), 'g': ('غ', 'ع'),
            'h': ('ح', 'خ'), 'j': ('ج', 'چ'), 'k': ('ك', 'خ'), 'l': ('ل', 'آ'),
            'z': ('ز', 'ژ'), 'x': ('خ', 'ث'), 'c': ('ص', 'ض'), 'v': ('ف', 'ڤ'), 'b': ('ب', 'پ'),
            'n': ('ن', 'ں'), 'm': ('م', 'م')
        }
        modifiers = QApplication.keyboardModifiers()
        use_shift = shift or (modifiers & Qt.ShiftModifier)
        if key in pegon_map:
            return pegon_map[key][1] if use_shift else pegon_map[key][0]
        return key

    def get_pegon_display(self, key):
        pegon_map = {
            'q': ('ق', 'ك'), 'w': ('و', 'ؤ'), 'e': ('ء', 'ئ'), 'r': ('ر', 'ذ'), 't': ('ت', 'ث'),
            'y': ('ي', 'ى'), 'u': ('ى', 'ء'), 'i': ('ا', 'إ'), 'o': ('ه', 'ة'), 'p': ('ط', 'ظ'),
            'a': ('ا', 'أ'), 's': ('ش', 'س'), 'd': ('د', 'ض'), 'f': ('ق', 'غ'), 'g': ('غ', 'ع'),
            'h': ('ح', 'خ'), 'j': ('ج', 'چ'), 'k': ('ك', 'خ'), 'l': ('ل', 'آ'),
            'z': ('ز', 'ژ'), 'x': ('خ', 'ث'), 'c': ('ص', 'ض'), 'v': ('ف', 'ڤ'), 'b': ('ب', 'پ'),
            'n': ('ن', 'ں'), 'm': ('م', 'م')
        }
        if key in pegon_map:
            return pegon_map[key][0]
        return key

    def get_harakat_mapping(self):
        return {
            '1': 'َ', '2': 'ِ', '3': 'ُ', '4': 'ْ', '5': 'ّ',
            '6': 'ً', '7': 'ٍ', '8': 'ٌ', '9': 'ـ', '0': '\u0619'
        }

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
            btn.setStyleSheet("background-color: #007ACC; color: white;")
            def restore_style():
                if key in self.active_buttons:
                    btn.setStyleSheet(self.original_styles.get(key, ""))
                if key in self.active_timers:
                    self.active_timers[key].deleteLater()
                    del self.active_timers[key]
            timer = QTimer(self)
            timer.timeout.connect(restore_style)
            timer.setSingleShot(True)
            timer.start(150)
            self.active_timers[key] = timer

    def eventFilter(self, obj, event):
        if obj == self.text_area and event.type() == QEvent.KeyPress:
            if event.matches(QKeySequence.StandardKey.Copy):
                self.copy_text()
                self.highlight_button("copy")
                return True
            key = event.text().lower()
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
            elif event.key() == Qt.Key_Space:
                self.insert_text(" ")
                self.highlight_button("space")
                return True
            elif event.key() == Qt.Key_Backspace:
                self.backspace()
                return True
            elif event.key() == Qt.Key_Delete:
                self.clear_text()
                return True
            elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.insert_text("\n")
                return True
            elif event.key() == Qt.Key_Tab:
                self.insert_text("\t")
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

    def use_gemini_dialog(self):
        if self.gemini_worker and self.gemini_worker.isRunning():
            QMessageBox.warning(self, "Gemini Sibuk", "Gemini sedang memproses. Mohon tunggu.")
            return
        
        options = [
            "Tulis ulang dalam Arab",
            "Perbaiki (ejaan/harakat)",
            "Cek kesalahan",
            "Auto harakat",
            "Prompt bebas",
            "Cari ayat",
            "Cari hadith"
        ]
        
        dlg = QInputDialog(self)
        dlg.setWindowTitle("AI Gemini")
        dlg.setLabelText("Pilih aksi:")
        dlg.setComboBoxItems(options)
        dlg.setWindowIcon(qta.icon('fa6s.star', color='deepskyblue'))
        dlg.setComboBoxEditable(False)
        
        ok = dlg.exec()
        choice = dlg.textValue()
        if not ok:
            return
        
        user_text = self.text_area.toPlainText()
        prompt = ""
        
        if choice == "Tulis ulang dalam Arab":
            prompt = f"""Tuliskan ulang kalimat berikut dalam huruf Arab dengan harakat yang benar.
Jawab HANYA dalam format JSON berikut, tanpa penjelasan tambahan:

{{
  "result": "teks arab dengan harakat yang benar"
}}

Teks input: {user_text}"""
        
        elif choice == "Perbaiki (ejaan/harakat)":
            prompt = f"""Perbaiki ejaan dan harakat pada teks Arab berikut.
Jawab HANYA dalam format JSON berikut, tanpa penjelasan tambahan:

{{
  "result": "teks arab yang sudah diperbaiki"
}}

Teks input: {user_text}"""
        
        elif choice == "Cek kesalahan":
            prompt = f"""Cek dan perbaiki kesalahan pada teks Arab berikut.
Jawab HANYA dalam format JSON berikut, tanpa penjelasan tambahan:

{{
  "result": "teks arab yang sudah diperbaiki"
}}

Teks input: {user_text}"""
        
        elif choice == "Auto harakat":
            prompt = f"""Tambahkan harakat yang benar pada teks Arab berikut.
Jawab HANYA dalam format JSON berikut, tanpa penjelasan tambahan:

{{
  "result": "teks arab dengan harakat lengkap"
}}

Teks input: {user_text}"""
        
        elif choice == "Prompt bebas":
            custom_dlg = QInputDialog(self)
            custom_dlg.setWindowTitle("Prompt Bebas")
            custom_dlg.setLabelText("Masukkan prompt Gemini:")
            custom_dlg.setWindowIcon(qta.icon('fa6s.comment-dots', color='green'))
            ok2 = custom_dlg.exec()
            custom_prompt = custom_dlg.textValue()
            if not ok2 or not custom_prompt.strip():
                return
            prompt = custom_prompt.strip()
        
        elif choice == "Cari ayat":
            surah_dlg = QInputDialog(self)
            surah_dlg.setWindowTitle("Cari Ayat")
            surah_dlg.setLabelText("Masukkan nomor surah (1-114) atau nama surah:")
            surah_dlg.setWindowIcon(qta.icon('fa6s.book-open', color='orange'))
            ok_surah = surah_dlg.exec()
            surah = surah_dlg.textValue()
            if not ok_surah or not surah.strip():
                return
            
            ayat_dlg = QInputDialog(self)
            ayat_dlg.setWindowTitle("Cari Ayat")
            ayat_dlg.setLabelText("Masukkan nomor ayat (atau rentang, misal 1-5):")
            ayat_dlg.setWindowIcon(qta.icon('fa6s.book-open', color='orange'))
            ok_ayat = ayat_dlg.exec()
            ayat = ayat_dlg.textValue()
            if not ok_ayat or not ayat.strip():
                return
                
            arti_dlg = QInputDialog(self)
            arti_dlg.setWindowTitle("Opsi Ayat")
            arti_dlg.setLabelText("Sertakan arti?")
            arti_dlg.setComboBoxItems(["Ya", "Tidak"])
            arti_dlg.setWindowIcon(qta.icon('fa6s.language', color='green'))
            ok_arti = arti_dlg.exec()
            sertakan_arti = arti_dlg.textValue()
            if not ok_arti:
                return
                
            baca_dlg = QInputDialog(self)
            baca_dlg.setWindowTitle("Opsi Ayat")
            baca_dlg.setLabelText("Sertakan cara baca (latin)?")
            baca_dlg.setComboBoxItems(["Ya", "Tidak"])
            baca_dlg.setWindowIcon(qta.icon('fa6s.microphone', color='purple'))
            ok_baca = baca_dlg.exec()
            sertakan_cara_baca = baca_dlg.textValue()
            if not ok_baca:
                return
                
            asbab_dlg = QInputDialog(self)
            asbab_dlg.setWindowTitle("Opsi Ayat")
            asbab_dlg.setLabelText("Sertakan asbabun nuzul?")
            asbab_dlg.setComboBoxItems(["Ya", "Tidak"])
            asbab_dlg.setWindowIcon(qta.icon('fa6s.clock-rotate-left', color='brown'))
            ok_asbab = asbab_dlg.exec()
            sertakan_asbab = asbab_dlg.textValue()
            if not ok_asbab:
                return
                
            prompt = f"""Tulis ayat Al-Qur'an surah {surah} ayat {ayat} dalam huruf Arab lengkap dengan harakat."""
            if sertakan_arti == "Ya":
                prompt += "\nSertakan juga artinya dalam bahasa Indonesia."
            if sertakan_cara_baca == "Ya":
                prompt += "\nSertakan juga cara bacanya (latin/transliterasi)."
            if sertakan_asbab == "Ya":
                prompt += "\nSertakan juga asbabun nuzul jika tersedia."
            prompt += """
Jawab HANYA dalam format JSON berikut, tanpa penjelasan tambahan:

{
  "result": "teks ayat arab dengan harakat",
  "arti": "arti ayat (jika diminta)",
  "cara_baca": "cara baca latin (jika diminta)",
  "asbabun_nuzul": "asbabun nuzul (jika diminta)"
}"""
        
        elif choice == "Cari hadith":
            topik_dlg = QInputDialog(self)
            topik_dlg.setWindowTitle("Cari Hadith")
            topik_dlg.setLabelText("Masukkan topik, konteks, atau kata kunci hadith:")
            topik_dlg.setWindowIcon(qta.icon('fa6s.book-bookmark', color='purple'))
            ok_topik = topik_dlg.exec()
            topik = topik_dlg.textValue()
            if not ok_topik or not topik.strip():
                return
                
            prompt = f"""Carikan hadith sahih yang berkaitan dengan topik: "{topik}"

PENTING: 
- HANYA tampilkan hadith yang benar-benar SAHIH dari Bukhari, Muslim, atau koleksi sahih lainnya
- Jika hadith diragukan atau tidak sahih, berikan peringatan jelas
- Jika tidak menemukan hadith sahih tentang topik ini, katakan dengan jujur
- Sertakan sumber yang jelas (nama kitab, nomor hadith)

Jawab HANYA dalam format JSON berikut:

{{
  "result": "teks hadith dalam bahasa Arab (jika ada)",
  "hadith_text": "terjemahan hadith dalam bahasa Indonesia",
  "hadith_source": "sumber hadith (kitab, nomor, perawi)",
  "hadith_warning": "peringatan jika hadith diragukan atau saran untuk cross-check ke ustadz/guru (jika perlu)"
}}

Topik: {topik}"""

        else:
            prompt = f"""Proses teks berikut dan kembalikan HANYA dalam format JSON:

{{
  "result": "teks yang diproses"
}}

Input: {user_text}"""

        self.progress_dialog = self.create_progress_dialog("AI Gemini", f"Memproses permintaan: {choice}...")
        self.progress_dialog.canceled.connect(self.on_progress_cancelled)
        
        self.gemini_worker = GeminiWorker(prompt)
        self.gemini_worker.finished.connect(self.on_gemini_finished)
        self.gemini_worker.error.connect(self.on_gemini_error)
        self.gemini_worker.start()

def main():
    app = QApplication(sys.argv)
    window = ArabicTypingHelper()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()