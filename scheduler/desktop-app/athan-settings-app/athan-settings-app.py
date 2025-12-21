#!/usr/bin/env python3
import sys
import os
import configparser

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QBoxLayout,
    QMessageBox,
    QSpinBox,
    QCheckBox,
    QScrollArea,
    QSizePolicy,
    QFormLayout,
    QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics

# ---------------- Paths ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")

# ---------------- Defaults ----------------
TAHAJJUD_ENABLE = "enable_tahajjud_prayer"
TAHAJJUD_TIME = "tahajjud_time"

DUHA_ENABLE = "enable_duha_prayer"
DUHA_TIME = "duha_time"

CRON_ENABLE = "enable_quran_cron_job"
DEFAULT_CRON = "30 06 * * *"

DEFAULTS_INT = {
    TAHAJJUD_TIME: 20,
    DUHA_TIME: 6,
}

DEFAULTS_BOOL = {
    TAHAJJUD_ENABLE: True,
    DUHA_ENABLE: True,
    CRON_ENABLE: True,
}

PRAYER_PREFIX = "enable_prayer_"
PRAYER_TIMES = [
    ("fajr", "الفجر"),
    ("sunrise", "الشروق"),
    ("dhuhr", "الظهر"),
    ("asr", "العصر"),
    ("maghrib", "المغرب"),
    ("isha", "العشاء"),
]

for key, _ in PRAYER_TIMES:
    DEFAULTS_BOOL[f"{PRAYER_PREFIX}{key}"] = True

# ---------------- Main App ----------------
class ControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" إعدادات البرامج  ")
        self.setGeometry(0, 0, 800, 480)
        self.config = configparser.ConfigParser(interpolation=None)
        self.load_config()

        # ---------------- Scroll Area ----------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setLayoutDirection(Qt.LeftToRight)

        # ---------------- Main Container ----------------
        main_widget = QWidget()
        scroll.setWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # ---------------- Title ----------------
        title = QLabel(" الإعدادت ")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        main_layout.addWidget(title)

        # ---------------- Prayer Times Section ----------------
        self.prayer_frame = self.create_section_frame("ضبط الأذان")
        prayer_layout = self.prayer_frame.layout()

        self.prayer_checkboxes = {}

        for key, arabic_name in PRAYER_TIMES:
            cfg_key = f"{PRAYER_PREFIX}{key}"

            chk = QCheckBox(f"تفعيل صوت أذان {arabic_name}")
            chk.setChecked(self.config["Settings"].getboolean(cfg_key))
            chk.setStyleSheet("font-size: 22px; padding: 5px;")
            chk.setLayoutDirection(Qt.RightToLeft)

            prayer_layout.addWidget(chk)
            self.prayer_checkboxes[cfg_key] = chk

        main_layout.addWidget(self.prayer_frame)

        # ---------------- Tahajjud Section ----------------
        self.tahajjud_frame = self.create_section_frame("صلاة التهجد")
        tahajjud_layout = self.tahajjud_frame.layout()

        self.tahajjud_chk = QCheckBox("تفعيل نداء التهجد")
        self.tahajjud_chk.setChecked(self.config["Settings"].getboolean(TAHAJJUD_ENABLE))
        self.tahajjud_chk.setStyleSheet("font-size: 22px; padding: 5px;")
        self.tahajjud_chk.setLayoutDirection(Qt.RightToLeft)
        tahajjud_layout.addWidget(self.tahajjud_chk)

        self.tahajjud_spin = self.create_spinbox(
            self.config["Settings"].get(TAHAJJUD_TIME, DEFAULTS_INT[TAHAJJUD_TIME])
        )
        tahajjud_form = QFormLayout()
        self.add_spinbox_row(tahajjud_form, "وقت صلاة التهجد قبل صلاة الفجر (دقيقة)", self.tahajjud_spin)
        tahajjud_layout.addLayout(tahajjud_form)
        main_layout.addWidget(self.tahajjud_frame)

        # ---------------- Duha Section ----------------
        self.duha_frame = self.create_section_frame("صلاة الضحى")
        duha_layout = self.duha_frame.layout()

        self.duha_chk = QCheckBox("تفعيل نداء الضحى")
        self.duha_chk.setChecked(self.config["Settings"].getboolean(DUHA_ENABLE))
        self.duha_chk.setStyleSheet("font-size: 22px; padding: 5px;")
        self.duha_chk.setLayoutDirection(Qt.RightToLeft)
        duha_layout.addWidget(self.duha_chk)

        self.duha_spin = self.create_spinbox(
            self.config["Settings"].get(DUHA_TIME, DEFAULTS_INT[DUHA_TIME])
        )
        duha_form = QFormLayout()
        self.add_spinbox_row(duha_form, "وقت صلاة الضحى قبل صلاة الظهر (دقيقة)", self.duha_spin)
        duha_layout.addLayout(duha_form)
        main_layout.addWidget(self.duha_frame)

        # ---------------- Cron Section ----------------
        self.cron_frame = self.create_section_frame("توقيت قراءة سور مختارة من القرآن الكريم")
        cron_layout = self.cron_frame.layout()

        self.cron_chk = QCheckBox("تفعيل جدول قراءة القرآن")
        self.cron_chk.setChecked(self.config["Settings"].getboolean(CRON_ENABLE))
        self.cron_chk.setStyleSheet("font-size: 22px; padding: 5px;")
        self.cron_chk.setLayoutDirection(Qt.RightToLeft)  # Only for the checkbox text
        cron_layout.addWidget(self.cron_chk)

        # Load cron job
        cron_job = self.config["Settings"].get("quran_cron_job", DEFAULT_CRON)
        if cron_job:
            minute, hour, *_ = cron_job.split()
            hour_val = int(hour)
            minute_val = int(minute)
        else:
            hour_val, minute_val = 6, 20

        self.cron_hour_spin = self.create_spinbox(hour_val, 0, 23)
        self.cron_min_spin = self.create_spinbox(minute_val, 0, 59)

        cron_form = QFormLayout()
        cron_form.setLabelAlignment(Qt.AlignRight)  # Force labels right
        cron_form.setFormAlignment(Qt.AlignRight)   # Align the whole form to right

        # Comment / section title
        comment_lbl = QLabel("تحديد وقت قراءة المختارات من القرآن الكريم")
        comment_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")

        # Wrap label in a horizontal layout
        comment_layout = QHBoxLayout()
        comment_layout.setDirection(QBoxLayout.RightToLeft)  # Force RTL
        comment_layout.addWidget(comment_lbl)
        cron_form.addRow(comment_layout)  # Add layout as a row

        # Spinbox rows
        self.add_spinbox_row(cron_form, "الساعة", self.cron_hour_spin)
        self.add_spinbox_row(cron_form, "الدقيقة", self.cron_min_spin)

        # Add the QFormLayout to the frame layout
        cron_layout.addLayout(cron_form)  # <-- Correct: addLayout, not addWidget

        main_layout.addWidget(self.cron_frame)

        # ---------------- Buttons ----------------
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(15)
        save_btn = QPushButton("حفظ الإعدادات")
        restart_btn = QPushButton("إعادة تشغيل التطبيق")
        close_btn = QPushButton("إغلاق")

        # Button styling
        save_btn.setFixedHeight(60)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 22px;
                border-radius: 14px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3e8e41; }
        """)
        restart_btn.setFixedHeight(60)
        restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 22px;
                border-radius: 14px;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:pressed { background-color: #1565C0; }
        """)
        close_btn.setFixedHeight(60)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                font-size: 22px;
                border-radius: 14px;
            }
            QPushButton:hover { background-color: #D32F2F; }
            QPushButton:pressed { background-color: #B71C1C; }
        """)

        save_btn.clicked.connect(self.save_settings)
        restart_btn.clicked.connect(self.restart_app)
        close_btn.clicked.connect(self.close)

        for b in [save_btn, restart_btn, close_btn]:
            btn_layout.addWidget(b)

        main_layout.addLayout(btn_layout)
        self.setCentralWidget(scroll)

        # ---------------- Increase form label fonts ----------------
        label_font = QFont()
        label_font.setPointSize(16)
        for layout in [tahajjud_form, duha_form, cron_form]:
            for i in range(layout.rowCount()):
                item = layout.itemAt(i, QFormLayout.LabelRole)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.setFont(label_font)

        # ---------------- Link checkboxes to spinboxes ----------------
        self.setup_checkbox_link(self.tahajjud_chk, self.tahajjud_spin)
        self.setup_checkbox_link(self.duha_chk, self.duha_spin)
        self.setup_checkbox_link(self.cron_chk, self.cron_hour_spin)
        self.setup_checkbox_link(self.cron_chk, self.cron_min_spin)

    # ---------------- Helpers ----------------
    def create_section_frame(self, title):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 10px;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        frame.setLayout(layout)
        frame.setLayoutDirection(Qt.RightToLeft)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(lbl)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        return frame

    def create_spinbox(self, value, min_val=1, max_val=300):
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(int(value))
        spin.setFixedHeight(50)
        spin.setStyleSheet("""
            QSpinBox {
                font-size: 22px;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding-right: 5px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 25px;
                height: 25px;
            }
        """)
        spin.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        font_metrics = QFontMetrics(spin.font())
        spin.setMinimumWidth(font_metrics.horizontalAdvance(str(max_val)) + 30)
        return spin

    def add_spinbox_row(self, form_layout, label_text, spinbox):
        form_layout.addRow(label_text, spinbox)
        form_layout.setLabelAlignment(Qt.AlignRight)

    def setup_checkbox_link(self, checkbox, spinbox):
        spinbox.setEnabled(checkbox.isChecked())
        def update_state(state):
            spinbox.setEnabled(state == Qt.Checked)
        checkbox.stateChanged.connect(update_state)

    # ---------------- Config ----------------
    def load_config(self):
        self.config.read(CONFIG_FILE, encoding="utf-8")
        if "Settings" not in self.config:
            self.config["Settings"] = {}
        for k, v in DEFAULTS_INT.items():
            self.config["Settings"].setdefault(k, str(v))
        for k, v in DEFAULTS_BOOL.items():
            self.config["Settings"].setdefault(k, str(v))
        self.config["Settings"].setdefault("quran_cron_job", DEFAULT_CRON)

    def save_settings(self):
        s = self.config["Settings"]
        s[TAHAJJUD_ENABLE] = str(self.tahajjud_chk.isChecked())
        s[TAHAJJUD_TIME] = str(self.tahajjud_spin.value())
        s[DUHA_ENABLE] = str(self.duha_chk.isChecked())
        s[DUHA_TIME] = str(self.duha_spin.value())
        s[CRON_ENABLE] = str(self.cron_chk.isChecked())

        for key, chk in self.prayer_checkboxes.items():
            s[key] = str(chk.isChecked())

        if self.cron_chk.isChecked():
            s["quran_cron_job"] = f"{self.cron_min_spin.value():02d} {self.cron_hour_spin.value():02d} * * *"
        else:
            s["quran_cron_job"] = ""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            self.config.write(f)
        QMessageBox.information(self, "تم الحفظ", "تم حفظ الإعدادات بنجاح")

    def restart_app(self):
        os.execl(sys.executable, sys.executable, *sys.argv)


# ---------------- Run ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ControlApp()
    window.showMaximized()
    sys.exit(app.exec_())

