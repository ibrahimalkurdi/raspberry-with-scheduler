#!/usr/bin/env python3
import sys
import os
import configparser
import subprocess
import csv


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
    QFrame,
    QListWidget,
    QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics

# ---------------- Paths ----------------

DESKTOP_DIR = "/home/ihms/Desktop"

MAIN_DIR = os.path.join(DESKTOP_DIR, "scheduler")

SETTINGS_INI_FILE = os.path.join(MAIN_DIR, "config", "config.ini")
QURAN_AUDIO_DIR = os.path.join(MAIN_DIR, "audio", "quran")
APPLY_SETTINGS_SCRIPT_FILE = os.path.join(MAIN_DIR, "config", "scripts", "apply_settings.sh")
APPLY_SETTINGS_LOG_FILE = os.path.join(MAIN_DIR, "logs", "apply_settings.log")
PRAYER_CSV_FILE = os.path.join(DESKTOP_DIR, "إدخال-مواقيت-الصلاة-للمستخدم.csv")

EXPECTED_CSV_HEADER = [
    "Month", "Day", "Fajr", "Sunrise",
    "Dhuhr", "Asr", "Maghrib", "Isha"
]



# ---------------- Defaults ----------------
TAHAJJUD_ENABLE = "enable_tahajjud_prayer"
TAHAJJUD_TIME = "tahajjud_time"

ATHKAR_ELSABAH_ENABLE = "enable_athkar_elsabah"
ATHKAR_ELSABAH_TIME = "athkar_elsabah_time"

ATHKAR_ELMASA_ENABLE = "enable_athkar_elmasa"
ATHKAR_ELMASA_TIME = "athkar_elmasa_time"

DUHA_ENABLE = "enable_duha_prayer"
DUHA_TIME = "duha_time"

QURAN_ENABLE = "enable_listen_to_quran"
DEFAULT_CRON = "06:30"

DEFAULTS_INT = {
    TAHAJJUD_TIME: 20,
    DUHA_TIME: 60,
    ATHKAR_ELSABAH_TIME: 240,
    ATHKAR_ELMASA_TIME: 20,

}

DEFAULTS_BOOL = {
    TAHAJJUD_ENABLE: True,
    DUHA_ENABLE: True,
    QURAN_ENABLE: True,
    ATHKAR_ELSABAH_ENABLE: True,
    ATHKAR_ELMASA_ENABLE: True,
}

PRAYER_PREFIX = "enable_prayer_"
PRAYER_TIMES = [
    ("fajr", "الفجر"),
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

        # ---------------- ATHKAR ALSABAH Section ----------------
        self.athkar_elsabah_frame = self.create_section_frame("أذكار الصباح")
        athkar_elsabah_layout = self.athkar_elsabah_frame.layout()

        self.athkar_elsabah_chk = QCheckBox("تفعيل أذكار الصباح")
        self.athkar_elsabah_chk.setChecked(self.config["Settings"].getboolean(ATHKAR_ELSABAH_ENABLE))
        self.athkar_elsabah_chk.setStyleSheet("font-size: 22px; padding: 5px;")
        self.athkar_elsabah_chk.setLayoutDirection(Qt.RightToLeft)
        athkar_elsabah_layout.addWidget(self.athkar_elsabah_chk)

        self.athkar_elsabah_spin = self.create_spinbox(
            self.config["Settings"].get(ATHKAR_ELSABAH_TIME, DEFAULTS_INT[ATHKAR_ELSABAH_TIME])
        )
        athkar_elsabah_form = QFormLayout()
        self.add_spinbox_row(athkar_elsabah_form, "وقت أذكار الصباح بعد صلاة الفجر (دقيقة)", self.athkar_elsabah_spin)
        athkar_elsabah_layout.addLayout(athkar_elsabah_form)
        main_layout.addWidget(self.athkar_elsabah_frame)

        # ---------------- ATHKAR ELMASA Section ----------------
        self.athkar_elmasa_frame = self.create_section_frame("أذكار المساء")
        athkar_elmasa_layout = self.athkar_elmasa_frame.layout()

        self.athkar_elmasa_chk = QCheckBox("تفعيل أذكار المساء")
        self.athkar_elmasa_chk.setChecked(self.config["Settings"].getboolean(ATHKAR_ELMASA_ENABLE))
        self.athkar_elmasa_chk.setStyleSheet("font-size: 22px; padding: 5px;")
        self.athkar_elmasa_chk.setLayoutDirection(Qt.RightToLeft)
        athkar_elmasa_layout.addWidget(self.athkar_elmasa_chk)

        self.athkar_elmasa_spin = self.create_spinbox(
            self.config["Settings"].get(ATHKAR_ELMASA_TIME, DEFAULTS_INT[ATHKAR_ELMASA_TIME])
        )
        athkar_elmasa_form = QFormLayout()
        self.add_spinbox_row(athkar_elmasa_form, "وقت أذكار المساء بعد صلاة المغرب (دقيقة)", self.athkar_elmasa_spin)
        athkar_elmasa_layout.addLayout(athkar_elmasa_form)
        main_layout.addWidget(self.athkar_elmasa_frame)

        # ---------------- Cron Section ----------------
        self.cron_frame = self.create_section_frame("توقيت قراءة سور مختارة من القرآن الكريم")
        cron_layout = self.cron_frame.layout()

        self.cron_chk = QCheckBox("تفعيل جدولة قراءة القرآ ن الكريم")
        self.cron_chk.setChecked(self.config["Settings"].getboolean(QURAN_ENABLE))
        self.cron_chk.setStyleSheet("font-size: 22px; padding: 5px;")
        self.cron_chk.setLayoutDirection(Qt.RightToLeft)
        cron_layout.addWidget(self.cron_chk)

        # Load cron job
        cron_job = self.config["Settings"].get("listen_to_quran", DEFAULT_CRON)
        try:
            hour, minute = cron_job.split(":")
            hour_val = int(hour)
            minute_val = int(minute)
        except (ValueError, AttributeError):
            hour_val, minute_val = 6, 30


        self.cron_hour_spin = self.create_spinbox(hour_val, 0, 23)
        self.cron_min_spin = self.create_spinbox(minute_val, 0, 59)

        cron_form = QFormLayout()
        cron_form.setLabelAlignment(Qt.AlignRight)
        cron_form.setFormAlignment(Qt.AlignRight)

        comment_lbl = QLabel(" تحديد وقت قراءة المختارات من القرآن الكريم يوميا:")
        comment_lbl.setStyleSheet("font-size: 20px; font-weight: bold;")

        comment_layout = QHBoxLayout()
        comment_layout.setDirection(QBoxLayout.RightToLeft)
        comment_layout.addWidget(comment_lbl)
        cron_form.addRow(comment_layout)

        self.add_spinbox_row(cron_form, "الساعة", self.cron_hour_spin)
        self.add_spinbox_row(cron_form, "الدقيقة", self.cron_min_spin)

        cron_layout.addLayout(cron_form)

        # -------- NEW: Quran audio list --------
        files_label = QLabel("اختر السور التي سيتم تشغيلها:")
        files_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.quran_audio_list = self.create_checkable_audio_list(QURAN_AUDIO_DIR)

        # Load checked state from config
        self.load_quran_audio_checked_state()

        cron_layout.addWidget(files_label)
        cron_layout.addWidget(self.quran_audio_list)

        # Always enable Quran list
        self.quran_audio_list.setEnabled(True)


        main_layout.addWidget(self.cron_frame)

        # ---------------- Buttons ----------------
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(15)
        apply_btn = QPushButton("حفظ  وتفعيل الإعدادت")
        reset_btn = QPushButton("إعادة ضبط الإعدادات")
        close_btn = QPushButton("إغلاق")

        # Button styling
        apply_btn.setFixedHeight(60)
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 22px;
                border-radius: 14px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3e8e41; }
        """)
        reset_btn.setFixedHeight(60)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 22px;
                border-radius: 14px;
            }
            QPushButton:hover { background-color: #FB8C00; }
            QPushButton:pressed { background-color: #EF6C00; }
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

        apply_btn.clicked.connect(self.save_and_apply_settings)
        reset_btn.clicked.connect(self.reset_settings)
        close_btn.clicked.connect(self.close)

        for b in [apply_btn, reset_btn, close_btn]:
            btn_layout.addWidget(b)

        main_layout.addLayout(btn_layout)
        self.setCentralWidget(scroll)

        # ---------------- Increase form label fonts ----------------
        label_font = QFont()
        label_font.setPointSize(16)
        for layout in [tahajjud_form, duha_form, athkar_elsabah_form, athkar_elmasa_form, cron_form]:
            for i in range(layout.rowCount()):
                item = layout.itemAt(i, QFormLayout.LabelRole)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.setFont(label_font)

        # ---------------- Link checkboxes to spinboxes ----------------
        self.setup_checkbox_link(self.tahajjud_chk, self.tahajjud_spin)
        self.setup_checkbox_link(self.duha_chk, self.duha_spin)
        self.setup_checkbox_link(self.athkar_elsabah_chk, self.athkar_elsabah_spin)
        self.setup_checkbox_link(self.athkar_elmasa_chk, self.athkar_elmasa_spin)
        self.setup_checkbox_link(self.cron_chk, self.cron_hour_spin)
        self.setup_checkbox_link(self.cron_chk, self.cron_min_spin)
        self.last_valid_duha = self.duha_spin.value()
        self.duha_spin.editingFinished.connect(self.validate_duha_time)


    # ---------------- Helpers ----------------
    def validate_duha_time(self):
        value = self.duha_spin.value()
        if value <= 30:
            QMessageBox.warning(
                self,
                "تنبيه",
                "هذا الوقت مكروه لأداء صلاة الضحى، لذا يُرجى اختيار وقت أكبر من 30 دقيقة"
            )
            # Revert to last valid value
            self.duha_spin.setValue(self.last_valid_duha)
        else:
            self.last_valid_duha = value


    def create_checkable_audio_list(self, directory):
        list_widget = QListWidget()
        list_widget.setFixedHeight(220)
        list_widget.setLayoutDirection(Qt.RightToLeft)
        list_widget.setStyleSheet("""
            QListWidget {
                font-size: 20px;
                border: 1px solid #ccc;
                border-radius: 6px;
            }
        """)

        if not os.path.isdir(directory):
            item = QListWidgetItem("❌ مجلد الملفات غير موجود")
            item.setFlags(Qt.NoItemFlags)
            list_widget.addItem(item)
            return list_widget

        for fname in sorted(f for f in os.listdir(directory) if f.lower().endswith(".mp3")):
            item = QListWidgetItem(fname)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            list_widget.addItem(item)

        return list_widget

    def load_quran_audio_checked_state(self):
        """Load checked state from config.ini"""
        checked_files = self.config["Settings"].get("quran_audio_checked", "")
        checked_set = set(f.strip() for f in checked_files.split(",") if f.strip())
        for i in range(self.quran_audio_list.count()):
            item = self.quran_audio_list.item(i)
            if item.text() in checked_set:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)


    def save_quran_audio_checked_state(self):
        checked_files = []
        for i in range(self.quran_audio_list.count()):
            item = self.quran_audio_list.item(i)
            if item.checkState() == Qt.Checked:
                checked_files.append(item.text())
        self.config["Settings"]["quran_audio_checked"] = ",".join(checked_files)

    def validate_prayer_csv(self):
        # 1 Check file existence
        if not os.path.isfile(PRAYER_CSV_FILE):
            QMessageBox.critical(
                self,
                "خطأ",
                "ملف إدخال-مواقيت-الصلاة-للمستخدم.csv غير موجود على سطح المكتب"
            )
            return False

        try:
            with open(PRAYER_CSV_FILE, newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)

            # 2 Check empty file
            if not rows:
                raise ValueError("empty file")

            # 3 Validate header
            header = [h.strip() for h in rows[0]]
            if header != EXPECTED_CSV_HEADER:
                QMessageBox.critical(
                    self,
                    "خطأ",
                    "ملف إدخال-مواقيت-الصلاة-للمستخدم.csv ليس مولد بالصغة المطلوبة التي هي\n\n"
                    "على سبيل المثال:\n"
                    "Month,Day,Fajr,Sunrise,Dhuhr,Asr,Maghrib,Isha\n"
                    "1,1,06:10,08:10,12:15,13:50,16:09,17:55"
                )
                return False

            # 4 Ensure at least one data row
            if len(rows) < 2:
                raise ValueError("no data rows")

        except Exception:
            QMessageBox.critical(
                self,
                "خطأ",
                "ملف إدخال-مواقيت-الصلاة-للمستخدم.csv ليس مولد بالصغة المطلوبة التي هي\n\n"
                "على سبيل المثال:\n"
                "Month,Day,Fajr,Sunrise,Dhuhr,Asr,Maghrib,Isha\n"
                "1,1,06:10,08:10,12:15,13:50,16:09,17:55"
            )
            return False

        return True


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
        checkbox.stateChanged.connect(
            lambda s: spinbox.setEnabled(s == Qt.Checked)
        )

    def apply_config_to_ui(self):
        s = self.config["Settings"]

        # Checkboxes
        self.tahajjud_chk.setChecked(s.getboolean(TAHAJJUD_ENABLE))
        self.duha_chk.setChecked(s.getboolean(DUHA_ENABLE))
        self.athkar_elsabah_chk.setChecked(s.getboolean(ATHKAR_ELSABAH_ENABLE))
        self.athkar_elmasa_chk.setChecked(s.getboolean(ATHKAR_ELMASA_ENABLE))
        self.cron_chk.setChecked(s.getboolean(QURAN_ENABLE))

        # Spinboxes
        self.tahajjud_spin.setValue(int(s[TAHAJJUD_TIME]))
        self.duha_spin.setValue(int(s[DUHA_TIME]))
        self.athkar_elsabah_spin.setValue(int(s[ATHKAR_ELSABAH_TIME]))
        self.athkar_elmasa_spin.setValue(int(s[ATHKAR_ELMASA_TIME]))

        # Prayer checkboxes
        for key, chk in self.prayer_checkboxes.items():
            chk.setChecked(s.getboolean(key))

        # Cron time
        try:
            hour, minute = s["listen_to_quran"].split(":")
            self.cron_hour_spin.setValue(int(hour))
            self.cron_min_spin.setValue(int(minute))
        except Exception:
            self.cron_hour_spin.setValue(6)
            self.cron_min_spin.setValue(30)

        # Quran audio list
        for i in range(self.quran_audio_list.count()):
            self.quran_audio_list.item(i).setCheckState(Qt.Checked)
        self.load_quran_audio_checked_state()


    # ---------------- Config ----------------
    def load_config(self):
        self.config.read(SETTINGS_INI_FILE, encoding="utf-8")
        if "Settings" not in self.config:
            self.config["Settings"] = {}
        for k, v in DEFAULTS_INT.items():
            self.config["Settings"].setdefault(k, str(v))
        for k, v in DEFAULTS_BOOL.items():
            self.config["Settings"].setdefault(k, str(v))
        self.config["Settings"].setdefault("listen_to_quran", DEFAULT_CRON)
        
        # Set default for Quran audio: all checked if new config
        if "quran_audio_checked" not in self.config["Settings"] or not self.config["Settings"]["quran_audio_checked"]:
            checked_files = [f for f in os.listdir(QURAN_AUDIO_DIR) if f.lower().endswith(".mp3")]
            self.config["Settings"]["quran_audio_checked"] = ",".join(checked_files)

    def save_settings(self, show_message=True):
        # --- Validation for Duha ---
        if self.duha_spin.value() <= 30:
            QMessageBox.warning(
                self,
                "تنبيه",
                "هذا الوقت مكروه لأداء صلاة الضحى، لذا يُرجى اختيار وقت أكبر من 30 دقيقة"
            )
            return


        s = self.config["Settings"]
        s[TAHAJJUD_ENABLE] = str(self.tahajjud_chk.isChecked())
        s[TAHAJJUD_TIME] = str(self.tahajjud_spin.value())
        s[DUHA_ENABLE] = str(self.duha_chk.isChecked())
        s[DUHA_TIME] = str(self.duha_spin.value())
        s[ATHKAR_ELSABAH_ENABLE] = str(self.athkar_elsabah_chk.isChecked())
        s[ATHKAR_ELSABAH_TIME] = str(self.athkar_elsabah_spin.value())
        s[ATHKAR_ELMASA_ENABLE] = str(self.athkar_elmasa_chk.isChecked())
        s[ATHKAR_ELMASA_TIME] = str(self.athkar_elmasa_spin.value())
        s[QURAN_ENABLE] = str(self.cron_chk.isChecked())

        for key, chk in self.prayer_checkboxes.items():
            s[key] = str(chk.isChecked())

        if self.cron_chk.isChecked():
            s["listen_to_quran"] = f"{self.cron_hour_spin.value():02d}:{self.cron_min_spin.value():02d}"
        else:
            s["listen_to_quran"] = ""

        # Save checked Quran audio files
        self.save_quran_audio_checked_state()

        with open(SETTINGS_INI_FILE, "w", encoding="utf-8") as f:
            self.config.write(f)

        if show_message:
            QMessageBox.information(self, "تم الحفظ", "تم حفظ الإعدادات بنجاح")


    def reset_settings(self):
        reply = QMessageBox.question(
            self,
            "تأكيد إعادة الضبط",
            "هل أنت متأكد من إعادة جميع الإعدادات إلى الوضع الافتراضي؟",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            # Create fresh config with defaults
            self.config = configparser.ConfigParser(interpolation=None)
            self.config["Settings"] = {}

            for k, v in DEFAULTS_INT.items():
                self.config["Settings"][k] = str(v)

            for k, v in DEFAULTS_BOOL.items():
                self.config["Settings"][k] = str(v)

            self.config["Settings"]["listen_to_quran"] = DEFAULT_CRON
            self.config["Settings"]["quran_audio_checked"] = ""

            # Check all Quran audio boxes on reset
            for i in range(self.quran_audio_list.count()):
                self.quran_audio_list.item(i).setCheckState(Qt.Checked)
            self.save_quran_audio_checked_state()


            # Ensure config directory exists
            os.makedirs(os.path.dirname(SETTINGS_INI_FILE), exist_ok=True)

            # Write config.ini (override)
            with open(SETTINGS_INI_FILE, "w", encoding="utf-8") as f:
                self.config.write(f)

            # Reload UI from config
            self.apply_config_to_ui()

            QMessageBox.information(
                self,
                "تمت إعادة الضبط",
                "تمت إعادة جميع الإعدادات إلى الوضع الافتراضي"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "خطأ",
                f"فشل إعادة ضبط الإعدادات:\n{e}"
            )


    def restart_app(self):
        try:
            with open(APPLY_SETTINGS_LOG_FILE, "w") as log_file:
                subprocess.Popen(
                    ["/bin/bash", APPLY_SETTINGS_SCRIPT_FILE],
                    stdout=log_file,
                    stderr=subprocess.STDOUT
                )

            QMessageBox.information(
                self,
                "إعادة التشغيل",
                "تم تطبيق الإعدادات وإعادة تشغيل البرامج بنجاح"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "خطأ",
                f"فشل تشغيل سكربت إعادة التشغيل:\n{e}"
            )

    def save_and_apply_settings(self):
        # Validate prayer CSV first
        if not self.validate_prayer_csv():
            return  # STOP everything

        # Continue only if validation passed
        self.save_settings(show_message=False)
        self.restart_app()




# ---------------- Run ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ControlApp()
    window.showMaximized()
    sys.exit(app.exec_())

