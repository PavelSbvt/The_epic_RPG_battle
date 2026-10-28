
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTextEdit, QComboBox, QProgressBar,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette

from core.base import Warrior, Mage, Assassin, Battle, Actions, Character
from server.client import Client, GAME_STATE


DARK_BG = "#0d1117"
PANEL_BG = "#161b22"
CARD_BG = "#1c2128"
ACCENT = "#f0a500"
ACCENT2 = "#ff6b35"
TEXT = "#e6edf3"
MUTED = "#8b949e"
GREEN = "#3fb950"
RED = "#f85149"
BLUE = "#58a6ff"
PURPLE = "#bc8cff"
GOLD = "#e3b341"

STYLESHEET = f"""
QMainWindow {{
    background-color: {DARK_BG};
}}
QLabel {{
    color: {TEXT};
    font-family: 'Segoe UI', 'Ubuntu', sans-serif;
}}
QComboBox {{
    background-color: {CARD_BG};
    color: {TEXT};
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    min-width: 140px;
}}
QComboBox:hover {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{
    border: none;
}}
QComboBox QAbstractItemView {{
    background-color: {CARD_BG};
    color: {TEXT};
    selection-background-color: {ACCENT};
    border: 1px solid #30363d;
}}
QPushButton {{
    background-color: #21262d;
    color: {TEXT};
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: #30363d;
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: #161b22;
}}
QPushButton:disabled {{
    color: #484f58;
    border-color: #21262d;
}}
QTextEdit {{
    background-color: #0d1117;
    color: {TEXT};
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 12px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}}
QProgressBar {{
    border: none;
    border-radius: 6px;
    background-color: #21262d;
    text-align: center;
    color: white;
    font-weight: bold;
    font-size: 11px;
    height: 18px;
}}
QProgressBar::chunk {{
    border-radius: 6px;
}}
"""


class GlowButton(QPushButton):
    def __init__(self, text, color=ACCENT, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 {ACCENT2});
                color: #0d1117;
                border: none;
                border-radius: 12px;
                padding: 12px 22px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {ACCENT2}, stop:1 {color});
            }}
            QPushButton:disabled {{
                background: #30363d;
                color: #6e7681;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(color))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)


class CharacterCard(QFrame):
    COLORS = {
        "Warrior": ("#c9a227", "🛡️"),
        "Mage": ("#7c3aed", "🧙"),
        "Assassin": ("#dc2626", "🗡️"),
    }

    def __init__(self, title="Player 1", parent=None):
        super().__init__(parent)
        self.char = None
        self.setObjectName("charCard")
        self.setMinimumWidth(280)
        self.setMinimumHeight(320)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(18, 18, 18, 18)

        self.header = QLabel(title)
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet(f"font-size: 13px; color: {MUTED}; font-weight: 600; letter-spacing: 1px;")
        layout.addWidget(self.header)

        self.icon_label = QLabel("❓")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(self.icon_label)

        self.name_label = QLabel("Select Character")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {TEXT};")
        layout.addWidget(self.name_label)

        hp_row = QHBoxLayout()
        hp_row.addWidget(QLabel("HP"))
        self.hp_bar = QProgressBar()
        self.hp_bar.setRange(0, 100)
        self.hp_bar.setValue(100)
        self.hp_bar.setFormat("%v / %m")
        self.hp_bar.setTextVisible(True)
        hp_row.addWidget(self.hp_bar, 1)
        layout.addLayout(hp_row)

        self.power_label = QLabel("Power: —")
        self.power_label.setStyleSheet(f"font-size: 14px; color: {GOLD};")
        layout.addWidget(self.power_label)

        self.buff_label = QLabel("Buff: None")
        self.buff_label.setWordWrap(True)
        self.buff_label.setStyleSheet(f"font-size: 13px; color: {BLUE};")
        layout.addWidget(self.buff_label)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"font-size: 12px; color: {MUTED};")
        layout.addWidget(self.status_label)

        layout.addStretch()
        self._apply_style("#30363d")

    def _apply_style(self, border_color: str):
        self.setStyleSheet(f"""
            #charCard {{
                background-color: {CARD_BG};
                border: 2px solid {border_color};
                border-radius: 16px;
            }}
        """)

    def set_character(self, char):
        self.char = char
        if char is None:
            self.icon_label.setText("❓")
            self.name_label.setText("Select Character")
            self.hp_bar.setRange(0, 100)
            self.hp_bar.setValue(0)
            self.power_label.setText("Power: —")
            self.buff_label.setText("Buff: None")
            self.status_label.setText("")
            self._apply_style("#30363d")
            return

        color, icon = self.COLORS.get(char.name, ("#888", "❓"))
        self.icon_label.setText(icon)
        self.name_label.setText(char.name)
        self.name_label.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {color};")
        self._apply_style(color)
        self.update_stats()

    def update_stats(self):
        if not self.char:
            return
        c = self.char
        self.hp_bar.setRange(0, c.max_hp)
        self.hp_bar.setValue(c.hp)
        self.hp_bar.setFormat(f"{c.hp} / {c.max_hp}")

        pct = c.hp / c.max_hp if c.max_hp else 0
        if pct > 0.6:
            chunk = GREEN
        elif pct > 0.3:
            chunk = GOLD
        else:
            chunk = RED

        self.hp_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 6px;
                background-color: #21262d;
                text-align: center;
                color: white;
                font-weight: bold;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {chunk}, stop:1 {chunk}aa);
                border-radius: 6px;
            }}
        """)

        # Power (с учётом баффа ассасина)
        effective = c.get_effective_power()
        self.power_label.setText(f"⚔ Power: {effective}")

        # Buffs
        buffs = []
        if c.iron_skin_active:
            buffs.append("🛡️ Iron Skin")
        if c.arcane_shield_active:
            buffs.append("🔮 Arcane Shield")
        if c.assassin_charges > 0:
            buffs.append(f"🗡️ Instinct ({c.assassin_charges})")
        self.buff_label.setText("✨ " + (", ".join(buffs) if buffs else "None"))

        if not c.is_alive():
            self.status_label.setText("💀 DEFEATED")
            self.status_label.setStyleSheet(f"font-size: 14px; color: {RED}; font-weight: bold;")
        else:
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet(f"font-size: 12px; color: {GREEN};")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚔️ The Epic RPG Battle")
        self.setMinimumSize(1100, 720)
        self.resize(1200, 800)

        self.battle = None
        self.char1 = None
        self.char2 = None

        self._build_ui()
        self.setStyleSheet(STYLESHEET)

        # Таймер для обновления интерфейса
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_ui_from_server)
        self.update_timer.start(100)

    def _build_ui(self) -> None:
        """
        Создание интерфейса главного окна.
        """

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(16)
        root.setContentsMargins(24, 20, 24, 20)

        title = QLabel("⚔️ THE EPIC RPG BATTLE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 32px;
            font-weight: 900;
            color: {ACCENT};
            letter-spacing: 3px;
            padding: 8px;
        """)
        root.addWidget(title)

        subtitle = QLabel("Сетевая битва • Ожидание игроков")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"font-size: 14px; color: {MUTED}; margin-bottom: 8px;")
        root.addWidget(subtitle)

        top_row = QHBoxLayout()
        top_row.setSpacing(20)

        self.status_label = QLabel("Статус: Подключение...")
        self.status_label.setStyleSheet(f"font-size: 14px; color: {GOLD}; font-weight: bold;")
        top_row.addWidget(self.status_label)

        top_row.addStretch()

        self.btn_start = GlowButton("НАЧАТЬ БОЙ", ACCENT)
        self.btn_start.clicked.connect(self._start_battle)
        self.btn_start.setVisible(False)
        top_row.addWidget(self.btn_start)

        root.addLayout(top_row)

        mid = QHBoxLayout()
        mid.setSpacing(20)

        self.card1 = CharacterCard("PLAYER 1")
        mid.addWidget(self.card1)

        action_panel = QFrame()
        action_panel.setObjectName("actionPanel")
        action_panel.setStyleSheet(f"""
            #actionPanel {{
                background-color: {PANEL_BG};
                border: 1px solid #30363d;
                border-radius: 16px;
            }}
        """)
        action_panel.setMinimumWidth(260)
        ap_layout = QVBoxLayout(action_panel)
        ap_layout.setContentsMargins(16, 20, 16, 20)
        ap_layout.setSpacing(12)

        act_title = QLabel("⚡ ВАШИ ДЕЙСТВИЯ")
        act_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        act_title.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {ACCENT};")
        ap_layout.addWidget(act_title)

        ap_layout.addWidget(self._section_label("Выберите действие на этот ход"))

        self.act1_buff = QPushButton("🛡️  Buff")
        self.act1_normal = QPushButton("⚔️  Normal Attack")
        self.act1_special = QPushButton("💥  Special Attack")

        for b in (self.act1_buff, self.act1_normal, self.act1_special):
            b.setEnabled(True)
            if b == self.act1_buff:
                b.clicked.connect(Client.send_buff)
            elif b == self.act1_normal:
                b.clicked.connect(Client.send_normal_attack)
            elif b == self.act1_special:
                b.clicked.connect(Client.send_special_attack)
            ap_layout.addWidget(b)

        ap_layout.addStretch()
        mid.addWidget(action_panel)

        self.card2 = CharacterCard("PLAYER 2")
        mid.addWidget(self.card2)

        root.addLayout(mid, 1)

        log_label = QLabel("📜 BATTLE LOG")
        log_label.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {MUTED};")
        root.addWidget(log_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(180)
        self.log.setPlaceholderText("Ожидание начала битвы...")
        root.addWidget(self.log)

        self.action_buttons = [self.act1_buff, self.act1_normal, self.act1_special]

        for b in self.action_buttons:
            b.setEnabled(False)

        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self._sync_with_server)
        self.game_timer.start(100)

    def _update_ui_from_server(self):
        """Читает GAME_STATE и обновляет карточки"""
        if not GAME_STATE["p1"]["name"]:
            return

        # Обновляем карточку 1
        self.card1.name_label.setText(GAME_STATE["p1"]["name"])
        self.card1.hp_bar.setRange(0, GAME_STATE["p1"]["max_hp"])
        self.card1.hp_bar.setValue(GAME_STATE["p1"]["hp"])

        # Обновляем карточку 2
        self.card2.name_label.setText(GAME_STATE["p2"]["name"])
        self.card2.hp_bar.setRange(0, GAME_STATE["p2"]["max_hp"])
        self.card2.hp_bar.setValue(GAME_STATE["p2"]["hp"])

        # Если игра окончена, блокируем кнопки
        if GAME_STATE["is_over"]:
            self.btn_buff.setEnabled(False)
            self.btn_normal.setEnabled(False)
            self.btn_special.setEnabled(False)

    def _sync_with_server(self) -> None:
        """
        Читает глобальные переменные клиента и обновляет интерфейс.
        Вызывается каждые 100 мс по таймеру.
        """
        # Импортируем внутри метода, чтобы не было циклического импорта
        from server.client import GAME_STATE, CLIENT_LOGS_QUEUE

        # 1. Обновляем карточки, если данные от сервера пришли
        if GAME_STATE["p1"]["name"] != "?":
            # Если кнопки еще заблокированы, а игра началась — разблокируем
            if not self.action_buttons[0].isEnabled() and not GAME_STATE["is_over"]:
                for b in self.action_buttons:
                    b.setEnabled(True)
                self.status_label.setText("Статус: Игра идёт")
                self.status_label.setStyleSheet(f"font-size: 14px; color: {GREEN}; font-weight: bold;")

            # Обновляем карточку 1
            self.card1.name_label.setText(GAME_STATE["p1"]["name"])
            self.card1.hp_bar.setRange(0, GAME_STATE["p1"]["max_hp"])
            self.card1.hp_bar.setValue(GAME_STATE["p1"]["hp"])
            self.card1.hp_bar.setFormat(f"{GAME_STATE['p1']['hp']} / {GAME_STATE['p1']['max_hp']}")

            # Обновляем карточку 2
            self.card2.name_label.setText(GAME_STATE["p2"]["name"])
            self.card2.hp_bar.setRange(0, GAME_STATE["p2"]["max_hp"])
            self.card2.hp_bar.setValue(GAME_STATE["p2"]["hp"])
            self.card2.hp_bar.setFormat(f"{GAME_STATE['p2']['hp']} / {GAME_STATE['p2']['max_hp']}")

        # 2. Проверяем, не закончилась ли игра
        if GAME_STATE["is_over"]:
            for b in self.action_buttons:
                b.setEnabled(False)
            self.status_label.setText("Статус: Игра окончена")
            self.status_label.setStyleSheet(f"font-size: 14px; color: {RED}; font-weight: bold;")

        # 3. Выводим новые сообщения из очереди логов
        while CLIENT_LOGS_QUEUE:
            msg = CLIENT_LOGS_QUEUE.pop(0)
            self._append_log(msg)

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 11px; color: {MUTED}; font-weight: 600; letter-spacing: 0.5px;")
        return lbl

    def _create_char(self, name: str):
        return {
            "Warrior": Warrior,
            "Mage": Mage,
            "Assassin": Assassin,
        }.get(name, lambda: None)()

    def _on_select1(self, text: str):
        self.char1 = self._create_char(text) if text != "— Choose —" else None
        self.card1.set_character(self.char1)
        self._check_ready()

    def _on_select2(self, text: str):
        self.char2 = self._create_char(text) if text != "— Choose —" else None
        self.card2.set_character(self.char2)
        self._check_ready()

    def _check_ready(self):
        ready = self.char1 is not None and self.char2 is not None
        self.btn_start.setEnabled(ready and self.battle is None)

    def _start_battle(self):
        if not self.char1 or not self.char2:
            return

        # Создаём свежие экземпляры
        self.char1 = self._create_char(self.char1.name)
        self.char2 = self._create_char(self.char2.name)
        self.card1.set_character(self.char1)
        self.card2.set_character(self.char2)

        self.battle = Battle(self.char1, self.char2)
        self.combo1.setEnabled(False)
        self.combo2.setEnabled(False)
        self.btn_start.setEnabled(False)
        self.btn_reset.setEnabled(True)

        for b in self.act1_buttons + self.act2_buttons:
            b.setEnabled(True)
            b.setChecked(False)

        self.selected_act1 = None
        self.selected_act2 = None
        self.btn_execute.setEnabled(False)

        self._append_log(f"<b style='color:{ACCENT}'>⚔️ BATTLE STARTED!</b>")
        self._append_log(f"{self.char1.name} vs {self.char2.name}")
        self._append_log("─" * 40)

    def _select_action(self, btn: QPushButton, player: int):
        buttons = self.act1_buttons if player == 1 else self.act2_buttons
        for b in buttons:
            if b is not btn:
                b.setChecked(False)

        action_map = {
            self.act1_buff: Actions.BUFF,
            self.act1_normal: Actions.NORMAL_ATTACK,
            self.act1_special: Actions.SPECIAL_ATTACK,
            self.act2_buff: Actions.BUFF,
            self.act2_normal: Actions.NORMAL_ATTACK,
            self.act2_special: Actions.SPECIAL_ATTACK,
        }
        act = action_map.get(btn)

        if player == 1:
            self.selected_act1 = act if btn.isChecked() else None
        else:
            self.selected_act2 = act if btn.isChecked() else None

        self.btn_execute.setEnabled(
            self.selected_act1 is not None and self.selected_act2 is not None and self.battle is not None
        )

    def _execute_turn(self):
        if not self.battle or self.selected_act1 is None or self.selected_act2 is None:
            return

        result = self.battle.play_turn(self.selected_act1, self.selected_act2)

        act_names = {
            Actions.BUFF: "Buff",
            Actions.NORMAL_ATTACK: "Normal Attack",
            Actions.SPECIAL_ATTACK: "Special Attack",
        }

        self._append_log(
            f"<span style='color:{BLUE}'>{self.char1.name}</span> → {act_names[self.selected_act1]}   |   "
            f"<span style='color:{PURPLE}'>{self.char2.name}</span> → {act_names[self.selected_act2]}"
        )

        if "won!" in result:
            self._append_log(f"<b style='color:{GREEN}; font-size:15px'>{result}</b>")
            self._end_battle()
        elif result == "This battle is over!":
            self._append_log(f"<span style='color:{MUTED}'>{result}</span>")
        else:
            self._append_log(f"<span style='color:{GOLD}'>{result}</span>")

        self.card1.update_stats()
        self.card2.update_stats()

        for b in self.act1_buttons + self.act2_buttons:
            b.setChecked(False)
        self.selected_act1 = None
        self.selected_act2 = None
        self.btn_execute.setEnabled(False)

        if self.battle.is_over:
            self._end_battle()

    def _end_battle(self):
        for b in self.act1_buttons + self.act2_buttons:
            b.setEnabled(False)
        self.btn_execute.setEnabled(False)
        self._append_log("─" * 40)
        self._append_log("<b>Battle finished. Press RESET to play again.</b>")

    def _reset(self):
        self.battle = None
        self.combo1.setEnabled(True)
        self.combo2.setEnabled(True)
        self.combo1.setCurrentIndex(0)
        self.combo2.setCurrentIndex(0)
        self.char1 = None
        self.char2 = None
        self.card1.set_character(None)
        self.card2.set_character(None)
        self.btn_start.setEnabled(False)
        self.btn_reset.setEnabled(False)
        for b in self.act1_buttons + self.act2_buttons:
            b.setEnabled(False)
            b.setChecked(False)
        self.btn_execute.setEnabled(False)
        self.log.clear()
        self._append_log("Ready for a new epic battle...")

    def _append_log(self, html: str):
        self.log.append(html)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(DARK_BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(CARD_BG))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(PANEL_BG))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor("#21262d"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#0d1117"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()