# Handles Reviewer settings GUI dialogs and overrides

from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import *

def setup_reviewer() -> None:
    # Any custom hooks for reviewing can be declared here
    pass

def show_settings_dialog() -> None:
    config = mw.addonManager.getConfig(__name__) or {}
    
    dialog = QDialog(mw)
    dialog.setWindowTitle("Sequential Cloze Revealer Settings")
    dialog.setMinimumWidth(390)
    
    # Stylize the dialog with native light grey styling and clean input styles
    dialog.setStyleSheet("""
        QDialog {
            background-color: #f7f7f7;
        }
        QLabel {
            color: #111111;
            font-size: 11px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QCheckBox {
            font-size: 11px;
            color: #111111;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QLineEdit, QSpinBox {
            background-color: #ffffff;
            border: 1px solid #adadad;
            border-radius: 3px;
            padding: 2px 4px;
            color: #111111;
            font-size: 11px;
            min-height: 18px;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QLineEdit:focus, QSpinBox:focus {
            border: 1px solid #0078d7;
        }
    """)
    
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 15, 20, 15)
    layout.setSpacing(10)
    
    # Bold logo header inside the settings panel matching Mockup 1
    title_layout = QHBoxLayout()
    title_layout.setSpacing(6)
    icon_label = QLabel()
    addon_dir = os.path.dirname(__file__)
    logo_path = os.path.join(addon_dir, "logo.svg")
    logo_pixmap = QPixmap(logo_path)
    if not logo_pixmap.isNull():
        logo_pixmap = logo_pixmap.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(logo_pixmap)
    else:
        icon_label.setText("📂")
    title_layout.addWidget(icon_label)
    
    title_text = QLabel("Sequential Cloze Revealer")
    title_font = QFont()
    title_font.setPointSize(12)
    title_font.setBold(True)
    title_text.setFont(title_font)
    title_text.setStyleSheet("color: #000000; font-weight: bold; font-family: 'Segoe UI';")
    title_layout.addWidget(title_text)
    title_layout.addStretch()
    layout.addLayout(title_layout)
    
    form = QFormLayout()
    form.setSpacing(6)
    
    center_mode_cb = QCheckBox()
    center_mode_cb.setChecked(config.get("center_mode", True))
    form.addRow("Enable Centered Mode:", center_mode_cb)
    
    mitcent_mode_cb = QCheckBox()
    mitcent_mode_cb.setChecked(config.get("mitcent_mode", True))
    form.addRow("Enable Mitcent Mode:", mitcent_mode_cb)
    
    reveal_speed_sb = QSpinBox()
    reveal_speed_sb.setRange(0, 1000)
    reveal_speed_sb.setSingleStep(10)
    reveal_speed_sb.setSuffix(" ms")
    reveal_speed_sb.setValue(config.get("reveal_speed", 120))
    form.addRow("Cloze Reveal Transition:", reveal_speed_sb)
    
    click_reveal_cb = QCheckBox()
    click_reveal_cb.setChecked(config.get("enable_click_reveal", True))
    form.addRow("Enable Click to Reveal:", click_reveal_cb)
    
    show_info_cb = QCheckBox()
    show_info_cb.setChecked(config.get("show_info_by_default", False))
    form.addRow("Show Info by Default:", show_info_cb)
    
    dark_compat_cb = QCheckBox()
    dark_compat_cb.setChecked(config.get("enable_dark_compatibility", True))
    form.addRow("Enable Dark Compatibility:", dark_compat_cb)
    
    auto_reveal_back_cb = QCheckBox()
    auto_reveal_back_cb.setChecked(config.get("auto_reveal_back", True))
    form.addRow("Auto-reveal Back Card:", auto_reveal_back_cb)
    
    cl_rev_custom_cb = QCheckBox()
    cl_rev_custom_cb.setChecked(config.get("cloze_revealed_custom", False))
    form.addRow("Custom Cloze Word Color (Revealed):", cl_rev_custom_cb)
    
    cl_rev_layout = QHBoxLayout()
    cl_rev_color_le = QLineEdit()
    cl_rev_color_le.setText(config.get("cloze_revealed_color", "#c00000"))
    cl_rev_color_le.setPlaceholderText("#c00000")
    cl_rev_btn = QPushButton()
    cl_rev_btn.setFixedSize(20, 20)
    cl_rev_btn.setToolTip("Pick a color")
    cl_rev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    cl_rev_btn.setStyleSheet(f"background-color: {config.get('cloze_revealed_color', '#c00000')}; border: 1px solid #7a7a7a; border-radius: 3px;")
    
    def on_choose_rev_color():
        currentColor = QColor(cl_rev_color_le.text() if cl_rev_color_le.text() else "#c00000")
        color = QColorDialog.getColor(currentColor, dialog, "Pick Ink Color")
        if color.isValid():
            cl_rev_color_le.setText(color.name())
            cl_rev_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #7a7a7a; border-radius: 3px;")
            
    cl_rev_btn.clicked.connect(on_choose_rev_color)
    cl_rev_color_le.textChanged.connect(lambda text: cl_rev_btn.setStyleSheet(f"background-color: {text if text else '#c00000'}; border: 1px solid #7a7a7a; border-radius: 3px;"))
    cl_rev_layout.addWidget(cl_rev_color_le)
    cl_rev_layout.addWidget(cl_rev_btn)
    form.addRow("Revealed Word Color (Hex):", cl_rev_layout)
    
    cl_hid_custom_cb = QCheckBox()
    cl_hid_custom_cb.setChecked(config.get("cloze_hidden_custom", False))
    form.addRow("Custom Cloze Bracket Color (Hidden):", cl_hid_custom_cb)
    
    cl_hid_layout = QHBoxLayout()
    cl_hid_color_le = QLineEdit()
    cl_hid_color_le.setText(config.get("cloze_hidden_color", "#0284c7"))
    cl_hid_color_le.setPlaceholderText("#0284c7")
    cl_hid_btn = QPushButton()
    cl_hid_btn.setFixedSize(20, 20)
    cl_hid_btn.setToolTip("Pick a color")
    cl_hid_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    cl_hid_btn.setStyleSheet(f"background-color: {config.get('cloze_hidden_color', '#0284c7')}; border: 1px solid #7a7a7a; border-radius: 3px;")
    
    def on_choose_hid_color():
        currentColor = QColor(cl_hid_color_le.text() if cl_hid_color_le.text() else "#0284c7")
        color = QColorDialog.getColor(currentColor, dialog, "Pick Ink Color")
        if color.isValid():
            cl_hid_color_le.setText(color.name())
            cl_hid_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #7a7a7a; border-radius: 3px;")
            
    cl_hid_btn.clicked.connect(on_choose_hid_color)
    cl_hid_color_le.textChanged.connect(lambda text: cl_hid_btn.setStyleSheet(f"background-color: {text if text else '#0284c7'}; border: 1px solid #7a7a7a; border-radius: 3px;"))
    cl_hid_layout.addWidget(cl_hid_color_le)
    cl_hid_layout.addWidget(cl_hid_btn)
    form.addRow("Hidden Bracket Color (Hex):", cl_hid_layout)
    
    mouse_scroll_cb = QCheckBox()
    mouse_scroll_cb.setChecked(config.get("mouse_scroll_reveal", False))
    form.addRow("Mouse Scroll Reveal:", mouse_scroll_cb)
    
    shortcut_roll_le = QLineEdit()
    shortcut_roll_le.setText(config.get("shortcut_roll", "Space"))
    form.addRow("Roll Shortcut Hotkey:", shortcut_roll_le)
    
    shortcut_info_le = QLineEdit()
    shortcut_info_le.setText(config.get("shortcut_info", "I"))
    form.addRow("Info Shortcut Hotkey:", shortcut_info_le)
    
    layout.addLayout(form)
    
    # Custom button stylesheet featuring beautiful and responsive cursor hovers!
    button_qss = """
    QPushButton {
        background-color: #ffffff;
        border: 1px solid #adadad;
        border-radius: 4px;
        padding: 5px 12px;
        color: #333333;
        font-family: 'Segoe UI', Arial;
        font-size: 11px;
    }
    QPushButton:hover {
        background-color: #eaf2f8;
        border-color: #0078d7;
        color: #000000;
    }
    QPushButton:pressed {
        background-color: #daebf4;
        border-color: #005499;
    }
    """

    primary_button_qss = """
    QPushButton {
        background-color: #0078d7;
        border: 1px solid #005499;
        border-radius: 4px;
        padding: 5px 18px;
        color: #ffffff;
        font-family: 'Segoe UI', Arial;
        font-size: 11px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1883db;
        border-color: #0078d7;
        color: #ffffff;
    }
    QPushButton:pressed {
        background-color: #004d8c;
        border-color: #003a6c;
        color: #ffffff;
    }
    """
    
    # Help & Maintenance separator matching native guide
    sep = QFrame()
    sep.setStyleSheet("background-color: #d1d5db; border: none; margin-top: 4px; margin-bottom: 2px;")
    sep.setMinimumHeight(1)
    sep.setMaximumHeight(1)
    layout.addWidget(sep)
    
    help_lbl = QLabel("HELP & SUPPORT")
    help_font = QFont()
    help_font.setBold(True)
    help_font.setPointSize(8)
    help_lbl.setFont(help_font)
    help_lbl.setStyleSheet("color: #777777; margin-bottom: 2px;")
    layout.addWidget(help_lbl)
    
    def on_help_guide():
        dialog.reject()
        help_dialog = QDialog(mw)
        help_dialog.setWindowTitle("Sequential Cloze Revealer — Guide")
        help_dialog.setMinimumWidth(440)
        help_dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        h_layout = QVBoxLayout()
        h_layout.setContentsMargins(24, 20, 24, 20)
        h_layout.setSpacing(10)

        # Title/Header
        header_lbl = QLabel("Sequential Cloze Revealer")
        h_font = QFont()
        h_font.setPointSize(14)
        h_font.setBold(True)
        header_lbl.setFont(h_font)
        header_lbl.setStyleSheet("color: #111111; font-weight: bold;")
        h_layout.addWidget(header_lbl)

        sub_lbl = QLabel("Focus directly on your cards with clean, center-mode layout and custom clozes.")
        sub_lbl.setStyleSheet("color: #666666; font-size: 11px;")
        h_layout.addWidget(sub_lbl)

        # Thick charcoal divider line below subtitle
        sep_line = QFrame()
        sep_line.setStyleSheet("background-color: #1c1c1c; border: none; margin-top: 4px; margin-bottom: 8px;")
        sep_line.setMinimumHeight(2)
        sep_line.setMaximumHeight(2)
        h_layout.addWidget(sep_line)

        # What it does Section
        what_section = QLabel("<b>What it does</b>")
        what_section.setStyleSheet("font-size: 12px; color: #111111;")
        h_layout.addWidget(what_section)

        what_texts = [
            "• Keeps card review focal points physically centered both vertically & horizontally.",
            "• Reduces mental fatigue by automatically filtering and hiding passive segments.",
            "• Click to Reveal opens isolated cloze items individually during key steps.",
            "• Configurable transition delays for eye-friendly, comfortable visual fades.",
            "• Support for both native Light / Dark styles based on client skin parameters."
        ]
        for t in what_texts:
            lbl = QLabel(t)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color: #444444; font-size: 11px; margin-left: 5px;")
            h_layout.addWidget(lbl)

        # How to use Section
        how_section = QLabel("<b>How to use</b>")
        how_section.setStyleSheet("font-size: 12px; color: #111111; margin-top: 8px;")
        h_layout.addWidget(how_section)

        how_texts = [
            "• Click on any hidden segment [...] or Hint text to unveil its content.",
            "• Double tap or press keyboard Space or Enter to roll the folder sequence.",
            "• Press keyboard shortcut I to instantly slide supplementary mnemonic Info open.",
            "• Choose rating scores using number hotkeys: Again (1), Hard (2), Good (3), Easy (4)."
        ]
        for t in how_texts:
            lbl = QLabel(t)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color: #444444; font-size: 11px; margin-left: 5px;")
            h_layout.addWidget(lbl)

        # Settings path Section
        settings_section = QLabel("<b>Settings (Tools &rarr; Sequential Cloze Revealer Settings)</b>")
        settings_section.setStyleSheet("font-size: 11.5px; color: #111111; margin-top: 8px;")
        h_layout.addWidget(settings_section)

        settings_texts = [
            "• Toggle Centered Modes to lock reviews at fixed spatial coordinates.",
            "• Customize revealed text highlighting vs hidden brackets separately.",
            "• Fine tune the milliseconds reveal transition slider for comfortable response times."
        ]
        for t in settings_texts:
            lbl = QLabel(t)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color: #444444; font-size: 11px; margin-left: 5px;")
            h_layout.addWidget(lbl)

        # Thick charcoal divider line above buttons
        sep_line2 = QFrame()
        sep_line2.setStyleSheet("background-color: #1c1c1c; border: none; margin-top: 12px; margin-bottom: 8px;")
        sep_line2.setMinimumHeight(2)
        sep_line2.setMaximumHeight(2)
        h_layout.addWidget(sep_line2)

        # Button Row
        btn_layout = QHBoxLayout()
        open_settings_btn = QPushButton("Open Settings")
        open_settings_btn.setStyleSheet(button_qss)
        
        def open_settings_and_close_help():
            help_dialog.accept()
            show_settings_dialog()
            
        open_settings_btn.clicked.connect(open_settings_and_close_help)
        
        got_it_btn = QPushButton("Got it ✓")
        got_it_btn.setStyleSheet(primary_button_qss)
        got_it_btn.clicked.connect(help_dialog.accept)

        btn_layout.addWidget(open_settings_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(got_it_btn)
        h_layout.addLayout(btn_layout)

        # Spacer line/separator
        sep_foot = QFrame()
        sep_foot.setStyleSheet("background-color: #1c1c1c; border: none; margin-top: 12px; margin-bottom: 8px;")
        sep_foot.setMinimumHeight(2)
        sep_foot.setMaximumHeight(2)
        h_layout.addWidget(sep_foot)

        # Footnote
        footnote_lbl = QLabel("<b>Sequential Cloze Revealer</b> v1.0.0 — Created by Adel")
        footnote_lbl.setStyleSheet("color: #777777; font-size: 10px; margin-top: 2px;")
        h_layout.addWidget(footnote_lbl)

        help_dialog.setLayout(h_layout)
        help_dialog.exec()

    guide_btn = QPushButton("Open Help Guide")
    guide_btn.setStyleSheet(button_qss)
    guide_btn.clicked.connect(on_help_guide)
    layout.addWidget(guide_btn)
    
    report_btn = QPushButton("⚑ Report an Issue")
    report_btn.setStyleSheet(button_qss)
    def on_report():
        import webbrowser
        webbrowser.open("https://github.com/Doummar/Sequential-Cloze-Revealer/issues")
    report_btn.clicked.connect(on_report)
    layout.addWidget(report_btn)
    
    reset_btn = QPushButton("↺ Reset to Default")
    reset_btn.setStyleSheet(button_qss)
    def on_reset():
        config.clear()
        config.update({
            "center_mode": True,
            "mitcent_mode": True,
            "reveal_speed": 120,
            "enable_click_reveal": True,
            "show_info_by_default": False,
            "enable_dark_compatibility": True,
            "auto_reveal_back": True,
            "cloze_revealed_custom": False,
            "cloze_revealed_color": "#c00000",
            "cloze_hidden_custom": False,
            "cloze_hidden_color": "#0284c7",
            "welcome_shown": True
        })
        mw.addonManager.writeConfig(__name__, config)
        dialog.reject()
        showInfo("Settings reset successfully.", parent=mw)
        show_settings_dialog()
    reset_btn.clicked.connect(on_reset)
    layout.addWidget(reset_btn)
    
    # Spacing and separator for buttons
    sep2 = QFrame()
    sep2.setStyleSheet("background-color: #d1d5db; border: none; margin-top: 4px; margin-bottom: 2px;")
    sep2.setMinimumHeight(1)
    sep2.setMaximumHeight(1)
    layout.addWidget(sep2)

    # OK / Cancel Dialog button box
    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    
    def save() -> None:
        config["center_mode"] = center_mode_cb.isChecked()
        config["mitcent_mode"] = mitcent_mode_cb.isChecked()
        config["reveal_speed"] = reveal_speed_sb.value()
        config["enable_click_reveal"] = click_reveal_cb.isChecked()
        config["show_info_by_default"] = show_info_cb.isChecked()
        config["enable_dark_compatibility"] = dark_compat_cb.isChecked()
        config["auto_reveal_back"] = auto_reveal_back_cb.isChecked()
        config["cloze_revealed_custom"] = cl_rev_custom_cb.isChecked()
        config["cloze_revealed_color"] = cl_rev_color_le.text()
        config["cloze_hidden_custom"] = cl_hid_custom_cb.isChecked()
        config["cloze_hidden_color"] = cl_hid_color_le.text()
        config["mouse_scroll_reveal"] = mouse_scroll_cb.isChecked()
        config["auto_theme_mode"] = True
        config["shortcut_roll"] = shortcut_roll_le.text()
        config["shortcut_info"] = shortcut_info_le.text()
        
        mw.addonManager.writeConfig(__name__, config)
        dialog.accept()
        showInfo("Settings saved successfully. Please reload/restart Anki to apply.", parent=mw)
        
    buttons.accepted.connect(save)
    buttons.rejected.connect(dialog.reject)
    
    # Customise buttons in buttonBox
    ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
    if ok_btn:
        ok_btn.setStyleSheet(primary_button_qss)
        ok_btn.setText("Save")
    cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
    if cancel_btn:
        cancel_btn.setStyleSheet(button_qss)
        cancel_btn.setText("Cancel")

    layout.addWidget(buttons)
    
    dialog.setLayout(layout)
    dialog.exec()
