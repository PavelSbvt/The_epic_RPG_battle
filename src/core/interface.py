import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QTextEdit, QComboBox, QProgressBar,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette

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

    def __init__(self, title="Player", parent=None):
        super().__init__(parent)
        self.setObjectName("charCard")
        self.setMinimumWidth(280)
        self.setMinimumHeight(320)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(18, 18, 18, 18)

        self.header = QLabel(title)
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet(
            f"font-size: 13px; color: {MUTED}; font-weight: 600; letter-spacing: 1px;"
        )
        layout.addWidget(self.header)

        self.icon_label = QLabel("❓")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(self.icon_label)

        self.name_label = QLabel("Select Character")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet(
            f"font-size: 22px; font-weight: 800; color: {TEXT};"
        )
        layout.addWidget(self.name_label)

        hp_row = QHBoxLayout()
        hp_row.addWidget(QLabel("HP"))
        self.hp_bar = QProgressBar()
        self.hp_bar.setRange(0, 100)
        self.hp_bar.setValue(0)
        self.hp_bar.setFormat("%v / %m")
        self.hp_bar.setTextVisible(True)
        hp_row.addWidget(self.hp_bar, 1)
        layout.addLayout(hp_row)

        self.power_label = QLabel("")
        self.power_label.setStyleSheet(f"font-size: 14px; color: {GOLD};")
        layout.addWidget(self.power_label)

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

    def set_role(self, role: str):
        """role: 'self' | 'enemy'"""
        if role == "self":
            self.header.setText("🟢 ВЫ")
            self.header.setStyleSheet(
                f"font-size: 13px; color: {GREEN}; font-weight: 800; letter-spacing: 1px;"
            )
        elif role == "enemy":
            self.header.setText("🔴 ПРОТИВНИК")
            self.header.setStyleSheet(
                f"font-size: 13px; color: {RED}; font-weight: 800; letter-spacing: 1px;"
            )
        else:
            self.header.setText("ОЖИДАНИЕ")
            self.header.setStyleSheet(
                f"font-size: 13px; color: {MUTED}; font-weight: 600; letter-spacing: 1px;"
            )

    def update_from_state(self, info: dict):
        """info: {"name": ..., "hp": ..., "max_hp": ...}"""
        name = info.get("name", "?")
        hp = info.get("hp", 0)
        max_hp = info.get("max_hp", 1) or 1

        if name == "?":
            self.reset()
            return

        color, icon = self.COLORS.get(name, ("#888", "❓"))
        self.icon_label.setText(icon)
        self.name_label.setText(name)
        self.name_label.setStyleSheet(
            f"font-size: 22px; font-weight: 800; color: {color};"
        )
        self._apply_style(color)

        self.hp_bar.setRange(0, max_hp)
        self.hp_bar.setValue(hp)
        self.hp_bar.setFormat(f"{hp} / {max_hp}")

        pct = hp / max_hp if max_hp else 0
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

        if hp <= 0:
            self.status_label.setText("💀 DEFEATED")
            self.status_label.setStyleSheet(
                f"font-size: 14px; color: {RED}; font-weight: bold;"
            )
        else:
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet(
                f"font-size: 12px; color: {GREEN};"
            )

    def reset(self):
        self.icon_label.setText("❓")
        self.name_label.setText("Select Character")
        self.name_label.setStyleSheet(
            f"font-size: 22px; font-weight: 800; color: {TEXT};"
        )
        self.hp_bar.setRange(0, 100)
        self.hp_bar.setValue(0)
        self.hp_bar.setFormat("%v / %m")
        self.power_label.setText("")
        self.status_label.setText("")
        self._apply_style("#30363d")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚔️ The Epic RPG Battle")
        self.setMinimumSize(1100, 720)
        self.resize(1200, 800)

        self._roles_applied = False

        self._build_ui()
        self.setStyleSheet(STYLESHEET)

        # Единственный таймер: синхронизация с GAME_STATE
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self._sync_with_server)
        self.game_timer.start(100)

    def _build_ui(self) -> None:
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

        subtitle = QLabel("Сетевая битва • Выберите класс и ждите соперника")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"font-size: 14px; color: {MUTED}; margin-bottom: 8px;")
        root.addWidget(subtitle)

        top_row = QHBoxLayout()
        top_row.setSpacing(20)

        self.status_label = QLabel("Статус: Подключение...")
        self.status_label.setStyleSheet(
            f"font-size: 14px; color: {GOLD}; font-weight: bold;"
        )
        top_row.addWidget(self.status_label)

        top_row.addStretch()

        class_label = QLabel("Ваш класс:")
        class_label.setStyleSheet(f"font-size: 14px; color: {TEXT};")
        top_row.addWidget(class_label)

        self.class_combo = QComboBox()
        self.class_combo.addItems(["— Choose —", "Warrior", "Mage", "Assassin"])
        self.class_combo.currentTextChanged.connect(self._on_class_selected)
        top_row.addWidget(self.class_combo)

        root.addLayout(top_row)

        mid = QHBoxLayout()
        mid.setSpacing(20)

        self.card1 = CharacterCard("ОЖИДАНИЕ")
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

        self.act_buff = QPushButton("🛡️  Buff")
        self.act_normal = QPushButton("⚔️  Normal Attack")
        self.act_special = QPushButton("💥  Special Attack")

        self.act_buff.clicked.connect(Client.send_buff)
        self.act_normal.clicked.connect(Client.send_normal_attack)
        self.act_special.clicked.connect(Client.send_special_attack)

        for b in (self.act_buff, self.act_normal, self.act_special):
            b.setEnabled(False)
            ap_layout.addWidget(b)

        ap_layout.addStretch()
        mid.addWidget(action_panel)

        self.card2 = CharacterCard("ОЖИДАНИЕ")
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

        self.action_buttons = [self.act_buff, self.act_normal, self.act_special]

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"font-size: 11px; color: {MUTED}; font-weight: 600; letter-spacing: 0.5px;"
        )
        return lbl

    def _on_class_selected(self, text: str) -> None:
        if text == "— Choose —":
            return
        Client.send_class_choice(text)
        self.status_label.setText(f"Статус: выбран {text}, ждём соперника…")
        self.status_label.setStyleSheet(
            f"font-size: 14px; color: {GOLD}; font-weight: bold;"
        )
        self.class_combo.setEnabled(False)

    def _apply_player_roles(self) -> None:
        my = GAME_STATE.get("my_player")
        if my is None:
            return
        if my == 1:
            self.card1.set_role("self")
            self.card2.set_role("enemy")
        else:
            self.card1.set_role("enemy")
            self.card2.set_role("self")
        self._roles_applied = True

    def _sync_with_server(self) -> None:
        # 1. Роли — один раз, как только сервер сказал, кто мы
        if not self._roles_applied and GAME_STATE.get("my_player"):
            self._apply_player_roles()

        # 2. Реванш: сервер сбросил игру (p1/p2 = "?") — снова можно выбрать класс
        if GAME_STATE["p1"]["name"] == "?" and GAME_STATE["p2"]["name"] == "?":
            if not self.class_combo.isEnabled():
                self.class_combo.setEnabled(True)
                self.class_combo.setCurrentIndex(0)
            self.card1.update_from_state(GAME_STATE["p1"])
            self.card2.update_from_state(GAME_STATE["p2"])
            for b in self.action_buttons:
                b.setEnabled(False)
            if GAME_STATE.get("my_player"):
                self.status_label.setText("Статус: выберите класс")
                self.status_label.setStyleSheet(
                    f"font-size: 14px; color: {GOLD}; font-weight: bold;"
                )
            self._flush_logs()
            return

        # 3. Обычное обновление карточек
        self.card1.update_from_state(GAME_STATE["p1"])
        self.card2.update_from_state(GAME_STATE["p2"])

        # 4. Кнопки действий и статус
        if GAME_STATE["is_over"]:
            for b in self.action_buttons:
                b.setEnabled(False)
            self.status_label.setText("Статус: игра окончена")
            self.status_label.setStyleSheet(
                f"font-size: 14px; color: {RED}; font-weight: bold;"
            )
        else:
            for b in self.action_buttons:
                b.setEnabled(True)
            self.status_label.setText("Статус: игра идёт")
            self.status_label.setStyleSheet(
                f"font-size: 14px; color: {GREEN}; font-weight: bold;"
            )

        # 5. Логи
        self._flush_logs()

    def _flush_logs(self) -> None:
        from server.client import CLIENT_LOGS_QUEUE
        while CLIENT_LOGS_QUEUE:
            msg = CLIENT_LOGS_QUEUE.pop(0)
            self._append_log(msg)

    def _append_log(self, html: str) -> None:
        self.log.append(html)
        sb = self.log.verticalScrollBar()
        sb.setValue(sb.maximum())


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