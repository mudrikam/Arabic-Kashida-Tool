"""
UI Components for Arabic Typing Helper
"""

from PySide6.QtWidgets import (QPushButton, QGridLayout, QScrollArea, 
                              QWidget, QTabWidget, QVBoxLayout, QHBoxLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import qtawesome as qta
from constants import (BASIC_HARAKAT_CHARS, ADVANCED_HARAKAT_CHARS, 
                      SYMBOL_CHARS, KEYBOARD_ROWS, UI_SETTINGS)

class UIComponentBuilder:
    def __init__(self, parent):
        self.parent = parent

    def create_basic_harakat_tab(self):
        """Create basic harakat tab with enhanced styling"""
        basic_tab = QWidget()
        basic_layout = QGridLayout()
        basic_layout.setSpacing(5)
        
        for idx, (char, name, key) in enumerate(BASIC_HARAKAT_CHARS):
            if key == '0':
                row = 3
                col = 1
            else:
                row = idx // 3
                col = idx % 3
            
            # Remove key display but keep functionality
            btn = QPushButton(char)
            btn_font = QFont()
            btn_font.setPointSize(UI_SETTINGS['harakat_font_size'])
            btn.setFont(btn_font)
            btn.setToolTip(f"{name} - Shortcut: {key}")
            btn.setMinimumHeight(UI_SETTINGS['button_min_height'])
            btn.setMinimumWidth(UI_SETTINGS['button_min_width'])
            btn.clicked.connect(lambda checked, c=char, k=key: self.parent.button_clicked(c, k))
            basic_layout.addWidget(btn, row, col)
            
            self.parent.active_buttons[key] = btn
            self.parent.original_styles[key] = ""
        
        basic_tab.setLayout(basic_layout)
        return basic_tab

    def create_advanced_harakat_tab(self):
        """Create advanced harakat tab with comprehensive Unicode characters"""
        advanced_scroll = QScrollArea()
        advanced_scroll.setWidgetResizable(True)
        advanced_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        advanced_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        advanced_content = QWidget()
        advanced_layout = QGridLayout()
        advanced_layout.setSpacing(3)
        
        for idx, (char, name) in enumerate(ADVANCED_HARAKAT_CHARS):
            row = idx // 3
            col = idx % 3
            btn = QPushButton(char)
            btn_font = QFont()
            btn_font.setPointSize(UI_SETTINGS['harakat_font_size'])
            btn.setFont(btn_font)
            btn.setToolTip(name)
            btn.setMinimumHeight(UI_SETTINGS['button_min_height'])
            btn.setMinimumWidth(UI_SETTINGS['button_min_width'])
            btn.clicked.connect(lambda checked, c=char: self.parent.button_clicked(c, ""))
            advanced_layout.addWidget(btn, row, col)
        
        advanced_content.setLayout(advanced_layout)
        advanced_scroll.setWidget(advanced_content)
        return advanced_scroll

    def create_symbols_tab(self):
        """Create symbols tab"""
        symbols_scroll = QScrollArea()
        symbols_scroll.setWidgetResizable(True)
        symbols_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        symbols_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        symbols_content = QWidget()
        symbols_layout = QGridLayout()
        symbols_layout.setSpacing(3)
        
        for idx, (char, name) in enumerate(SYMBOL_CHARS):
            row = idx // 3
            col = idx % 3
            btn = QPushButton(char)
            btn_font = QFont()
            btn_font.setPointSize(UI_SETTINGS['harakat_font_size'])
            btn.setFont(btn_font)
            btn.setToolTip(name)
            btn.setMinimumHeight(UI_SETTINGS['button_min_height'])
            btn.setMinimumWidth(UI_SETTINGS['button_min_width'])
            btn.clicked.connect(lambda checked, c=char: self.parent.button_clicked(c, ""))
            symbols_layout.addWidget(btn, row, col)
        
        symbols_content.setLayout(symbols_layout)
        symbols_scroll.setWidget(symbols_content)
        return symbols_scroll

    def create_harakat_tabs(self):
        """Create complete harakat tabs widget"""
        harakat_tabs = QTabWidget()
        harakat_tabs.setMaximumWidth(350)
        
        # Add tabs
        harakat_tabs.addTab(self.create_basic_harakat_tab(), "Dasar")
        harakat_tabs.addTab(self.create_advanced_harakat_tab(), "Lanjutan")
        harakat_tabs.addTab(self.create_symbols_tab(), "Simbol")
        
        return harakat_tabs

    def create_keyboard_layout(self):
        """Create main keyboard layout"""
        for i in reversed(range(self.parent.letters_layout.count())):
            child = self.parent.letters_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        self.parent.active_buttons = {k: v for k, v in self.parent.active_buttons.items() if k in ["space", "copy"]}
        
        for row_idx, row in enumerate(KEYBOARD_ROWS):
            for col_idx, key in enumerate(row):
                btn = self.create_keyboard_button(key)
                self.parent.letters_layout.addWidget(btn, row_idx, col_idx)

    def create_keyboard_button(self, key):
        """Create individual keyboard button"""
        if key == '⌫':
            btn = QPushButton(qta.icon('fa6s.delete-left', color='red'), "")
            btn.setToolTip("Backspace - Hapus karakter sebelumnya")
            btn.clicked.connect(self.parent.backspace)
        elif key == 'Del':
            btn = QPushButton(qta.icon('fa6s.trash', color='orange'), "Hapus")
            btn.setToolTip("Hapus Semua - Hapus semua teks")
            btn.clicked.connect(self.parent.clear_text)
        elif key == 'Salin':
            btn = QPushButton(qta.icon('fa6s.copy', color='deepskyblue'), "Salin")
            btn.setToolTip("Salin teks ke clipboard - Ctrl+C")
            btn.clicked.connect(self.parent.copy_text)
            self.parent.active_buttons["copy"] = btn
            self.parent.original_styles["copy"] = ""
        elif key == 'Enter':
            btn = QPushButton(qta.icon('fa6s.arrow-turn-down', color='green'), "Enter")
            btn.setToolTip("Tombol Enter")
            btn.setMinimumWidth(100)
            btn.clicked.connect(lambda checked, k=key: self.parent.special_key_clicked(k))
        else:
            mapped_char = self.parent.get_keyboard_char(key.lower())
            if self.parent.current_mode == "Pegon":
                mapped_char = self.parent.get_pegon_display(key.lower())
            
            if self.parent.current_mode == "ABC":
                btn = QPushButton(f"{key}\n{mapped_char}")
            else:
                btn = QPushButton(f"{mapped_char}\n{key}")
            
            btn.setToolTip(f"Karakter: {mapped_char} | Tombol: {key}")
            btn.clicked.connect(lambda checked, c=self.parent.get_keyboard_char(key.lower()), k=key.lower(): self.parent.button_clicked(c, k))
            self.parent.active_buttons[key.lower()] = btn
            self.parent.original_styles[key.lower()] = ""
        
        # Set common button properties
        btn_font = QFont()
        btn_font.setPointSize(UI_SETTINGS['keyboard_font_size'])
        btn.setFont(btn_font)
        btn.setMinimumHeight(UI_SETTINGS['button_min_height'])
        
        return btn

    def create_special_controls(self):
        """Create space button and other special controls"""
        special_layout = QHBoxLayout()
        
        space_btn = QPushButton(qta.icon('fa6s.shuttle-space', color='limegreen'), "Spasi")
        space_btn.setToolTip("Tekan Spasi")
        btn_font = QFont()
        btn_font.setPointSize(UI_SETTINGS['button_font_size'])
        space_btn.setFont(btn_font)
        space_btn.setMinimumHeight(40)
        space_btn.setMinimumWidth(300)
        space_btn.clicked.connect(lambda: self.parent.button_clicked(" ", "space"))
        special_layout.addWidget(space_btn)
        
        self.parent.active_buttons["space"] = space_btn
        self.parent.original_styles["space"] = ""
        
        return special_layout
