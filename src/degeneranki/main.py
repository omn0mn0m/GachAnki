import functools
import sys
import urllib3
from os import path
from enum import Enum

from .gacha import GachaMachine
from .database import Database
from .api.ambr import Weapon, Character

# import the main window object (mw) from aqt
from aqt import gui_hooks, mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *

from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

gacha = GachaMachine()
http = urllib3.PoolManager()

MAX_ROLL_IMAGE_WIDTH = 1280
MAX_ROLL_IMAGE_HEIGHT = 720

sys.path.insert(1, path.abspath(path.dirname(__file__)))
root_project_dir = path.abspath(path.dirname(__file__))
res_files_dir = path.join(root_project_dir, "res")

class Franchise(Enum):
    GENSHIN_IMPACT = 'Genshin Impact'
    HONKAI_STAR_RAIL = 'Honkai Star Rail (Coming Soon)'
    PROJECT_SEKAI = 'Project Sekai (Coming Soon)'
    BANG_DREAM = 'Bang Dream: Girls Band Party (Coming Soon)'

class DegenerankiWidget(QTabWidget):
    
    def __init__(self, *args, **kwargs):
        super(DegenerankiWidget, self).__init__(*args, **kwargs)
        
        self.gachaTab = GachaWidget()
        self.addTab(self.gachaTab, "Gacha")

        self.charactersTab = InventoryWidget(InventoryWidget.InventoryTypes.CHARACTERS)
        self.addTab(self.charactersTab, "Characters")

        self.weaponsTab = InventoryWidget(InventoryWidget.InventoryTypes.WEAPONS)
        self.addTab(self.weaponsTab, "Weapons")

        self.settingsTab = SettingsWidget()
        self.addTab(self.settingsTab, "Settings")

        self.gachaTab.character_roll_finished.connect(self.charactersTab.on_roll_finished)
        self.gachaTab.weapon_roll_finished.connect(self.weaponsTab.on_roll_finished)

class SettingsWidget(QWidget):
    
    def __init__(self, *args, **kwargs):
        super(SettingsWidget, self).__init__(*args, **kwargs)

        self.layout = QVBoxLayout(self)

        hlayout = QHBoxLayout()
        self.layout.addLayout(hlayout)

        account_groupbox = QGroupBox("Account")
        account_hlayout = QHBoxLayout(account_groupbox)

        login_form_vertical_layout = QVBoxLayout()
        account_hlayout.addLayout(login_form_vertical_layout)

        login_form = QFormLayout()
        self.email_edit = QLineEdit()
        login_form.addRow("Email", self.email_edit)
        self.password_edit = QLineEdit()
        login_form.addRow("Password", self.password_edit)
        login_form_vertical_layout.addLayout(login_form)

        login_buttons_layout = QHBoxLayout()
        self.sign_up_button = QPushButton("Sign Up")
        login_buttons_layout.addWidget(self.sign_up_button)
        self.sign_up_button.clicked.connect(self.sign_up)

        self.log_in_button = QPushButton("Log In")
        login_buttons_layout.addWidget(self.log_in_button)
        self.log_in_button.clicked.connect(self.log_in)

        self.log_out_button = QPushButton("Log Out")
        self.log_out_button.setEnabled(False)
        login_buttons_layout.addWidget(self.log_out_button)
        self.log_out_button.clicked.connect(self.log_out)

        login_form_vertical_layout.addLayout(login_buttons_layout)

        STATS_LABEL_WIDTH = 150
        account_stats_groupbox = QGroupBox("Account Stats")
        account_stats_layout = QVBoxLayout(account_stats_groupbox)
        self.lifetime_pity_label = QLabel("Lifetime Pity: {}".format(gacha.data.lifetime_rolls))
        self.lifetime_pity_label.setMinimumWidth(STATS_LABEL_WIDTH)
        account_stats_layout.addWidget(self.lifetime_pity_label)
        self.pity_4_star_label = QLabel("4-Star Pity: {}".format(gacha.data.pity_4_star))
        self.pity_4_star_label.setMinimumWidth(STATS_LABEL_WIDTH)
        account_stats_layout.addWidget(self.pity_4_star_label)
        self.pity_5_star_label = QLabel("5-Star Pity: {}".format(gacha.data.pity_5_star))
        self.pity_5_star_label.setMinimumWidth(STATS_LABEL_WIDTH)
        account_stats_layout.addWidget(self.pity_5_star_label)

        hlayout.addWidget(account_groupbox)
        hlayout.addWidget(account_stats_groupbox)
        
        franchise_groupbox = QGroupBox("Enable or Disable Franchises")
        franchise_vlayout = QVBoxLayout(franchise_groupbox)
        
        for franchise in Franchise:
            franchise_vlayout.addWidget(QCheckBox(franchise.value))

        self.layout.addWidget(franchise_groupbox)

        settings_buttons_layout = QHBoxLayout()
        
        self.save_settings_button = QPushButton("Save Settings")
        settings_buttons_layout.addWidget(self.save_settings_button)
        self.save_settings_button.clicked.connect(self.save_config)
        
        self.revert_settings_button = QPushButton("Revert Settings")
        settings_buttons_layout.addWidget(self.revert_settings_button)
        self.revert_settings_button.clicked.connect(self.load_config)
        
        self.layout.addLayout(settings_buttons_layout)
        
        vertical_spacer = QSpacerItem(20,
                                      40,
                                      QSizePolicy().Policy.Minimum,
                                      QSizePolicy().Policy.Expanding,)
        self.layout.addSpacerItem(vertical_spacer)

        self.load_config()

    def sign_up(self):
        response = gacha.data.account_signup(self.email_edit.text(), self.password_edit.text())

        if response.user.aud == 'authenticated':
            self.sign_up_button.setEnabled(False)
            self.log_in_button.setEnabled(False)
            self.log_out_button.setEnabled(True)

            config = mw.addonManager.getConfig("degeneranki.py")
            config['email'] = self.email_edit.text()
            config['password'] = self.password_edit.text()
            mw.addonManager.writeConfig("degeneranki.py", config)

    def log_in(self):
        data = gacha.data.account_login(self.email_edit.text(), self.password_edit.text())
        
        if data.user.aud == 'authenticated':
            self.sign_up_button.setEnabled(False)
            self.log_in_button.setEnabled(False)
            self.log_out_button.setEnabled(True)

            config = mw.addonManager.getConfig("degeneranki.py")
            config['email'] = self.email_edit.text()
            config['password'] = self.password_edit.text()
            mw.addonManager.writeConfig("degeneranki.py", config)

    def log_out(self):
        response = gacha.data.account_signout()
        self.sign_up_button.setEnabled(True)
        self.log_in_button.setEnabled(True)
        self.log_out_button.setEnabled(False)

    def load_config(self):
        config = mw.addonManager.getConfig("degeneranki.py")

    def save_config(self):
        mw.addonManager.writeConfig("degeneranki.py", config)

class InventoryWidget(QScrollArea):

    MAX_COL_ITEMS = 4

    class InventoryTypes(Enum):
        WEAPONS = 'Weapon',
        CHARACTERS = 'Character'
    
    def __init__(self, inventory_type, *args, **kwargs):
        super(InventoryWidget, self).__init__(*args, **kwargs)

        self.inventory_type = inventory_type
        
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_finished)

        self.wrapper_widget = QWidget()
        self.grid_layout = QGridLayout(self.wrapper_widget)
        self.setWidget(self.wrapper_widget)
        self.setWidgetResizable(True)

        self.row = 0
        self.col = 0

        self.grid_contents = []

        if inventory_type == InventoryWidget.InventoryTypes.WEAPONS:
            for i, data in enumerate(gacha.data.get_owned_weapons()):
                info = gacha.data.weapons[data[0]]
                self.add_to_grid(info)
        elif inventory_type == InventoryWidget.InventoryTypes.CHARACTERS:
            for i, data in enumerate(gacha.data.get_owned_characters()):
                info = gacha.data.characters[data[0]]
                self.add_to_grid(info)

    def add_to_grid(self, info):
        if info not in self.grid_contents:
            request = QNetworkRequest(QUrl(info.icon))
            self.network_manager.get(request)
            self.grid_contents.append(info)

    @pyqtSlot(QNetworkReply)
    def on_finished(self, reply):
        inventory_label = QLabel()
        label_measure = self.width() // self.MAX_COL_ITEMS
        inventory_label.setSizePolicy(QSizePolicy().Policy.Fixed, QSizePolicy().Policy.Fixed)
        inventory_label.setFixedSize(label_measure, label_measure)
        inventory_label.setMaximumSize(label_measure, label_measure)
        
        image = QImage()
        image.loadFromData(reply.readAll())
        
        image_pixmap = QPixmap.fromImage(image)
        inventory_label.setPixmap(image_pixmap.scaled(inventory_label.size(), 
                                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                                      Qt.TransformationMode.SmoothTransformation))
        self.grid_layout.addWidget(inventory_label, self.row, self.col, Qt.AlignmentFlag.AlignHCenter)

        self.col += 1

        if self.col == self.MAX_COL_ITEMS:
            self.col = 0
            self.row += 1

    @pyqtSlot(Weapon)
    @pyqtSlot(Character)
    def on_roll_finished(self, roll):
        self.add_to_grid(roll)

class GachaWidget(QWidget):
    weapon_roll_finished = pyqtSignal(Weapon)
    character_roll_finished = pyqtSignal(Character)
    
    def __init__(self, *args, **kwargs):
        super(GachaWidget, self).__init__(*args, **kwargs)

        wish_bg_image = QImage()
        with open(path.join(res_files_dir, "wish-background.jpg"), 'rb') as img:
            wish_bg_image.loadFromData(img.read())
        self.wish_bg_pixmap = QPixmap(wish_bg_image).scaled(MAX_ROLL_IMAGE_WIDTH, MAX_ROLL_IMAGE_HEIGHT)

        self.flash_bg_pixmap = QPixmap(MAX_ROLL_IMAGE_WIDTH, MAX_ROLL_IMAGE_HEIGHT)
        self.flash_bg_pixmap.fill()
        
        roll_bg_image = QImage()
        with open(path.join(res_files_dir, "roll-background.jpg"), 'rb') as img:
            roll_bg_image.loadFromData(img.read())
        self.roll_bg_pixmap = QPixmap(roll_bg_image).scaled(MAX_ROLL_IMAGE_WIDTH, MAX_ROLL_IMAGE_HEIGHT)

        self.layout = QVBoxLayout(self)
        
        self.roll_image = QLabel()
        self.roll_image.setPixmap(self.wish_bg_pixmap)
        
        self.layout.addWidget(self.roll_image, alignment=Qt.AlignmentFlag.AlignCenter)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)
        
        self.roll_button = QPushButton("Roll (Cost: 100 Gacha Points)", self)
        self.roll_button.clicked.connect(self.roll)
        self.layout.addWidget(self.roll_button)
        
        # Bottom bar
        self.roll_stats_layout = QHBoxLayout()
        self.layout.addLayout(self.roll_stats_layout)

        self.gacha_points = QLabel("Gacha Points Left: {}".format(gacha.data.gacha_points))
        self.roll_stats_layout.addWidget(self.gacha_points)

    def roll(self) -> None:
        self.roll_image.setPixmap(self.wish_bg_pixmap)

        roll = gacha.roll()

        roll_pixmap = self.roll_bg_pixmap.copy(0, 0, self.roll_bg_pixmap.width(), self.roll_bg_pixmap.height())

        painter = QPainter()
        painter.begin(roll_pixmap)
        
        image = QImage()

        if hasattr(roll, 'gacha'):
            image.loadFromData(http.request("GET", roll.gacha).data)
        else:
            image.loadFromData(http.request("GET", roll.icon).data)
        image_pixmap = QPixmap(image)
        image_pixmap = image_pixmap.scaled(
            max(480, image_pixmap.width()), # ambr images have too much horizontal whitespace
            max(480, MAX_ROLL_IMAGE_HEIGHT),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)

        start_x = (MAX_ROLL_IMAGE_WIDTH // 2) - (image_pixmap.width() // 2)
        start_y = (MAX_ROLL_IMAGE_HEIGHT // 2) - (image_pixmap.height() // 2)

        painter.drawPixmap(start_x, start_y, image_pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Arial', 28))
        painter.drawText(32, (MAX_ROLL_IMAGE_HEIGHT // 2), roll.name)
        painter.setPen(QColor(255, 215, 0))
        painter.drawText(32, (MAX_ROLL_IMAGE_HEIGHT // 2) + 40, "★" * roll.rarity)

        painter.end()

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        
        # Flash a white background
        timer_callback = functools.partial(self.show_white, roll_pixmap=roll_pixmap)
        self.timer.timeout.connect(timer_callback)
        self.timer.start(150)
        
        # Update roll counts
        self.lifetime_rolls.setText("Lifetime Rolls: {}".format(gacha.data.lifetime_rolls))
        self.pity_4_star.setText("4-Star Pity: {}".format(gacha.data.pity_4_star))
        self.pity_5_star.setText("5-Star Pity: {}".format(gacha.data.pity_5_star))

        if type(roll) == Weapon:
            self.weapon_roll_finished.emit(roll)
        elif type(roll) == Character:
            self.character_roll_finished.emit(roll)

    def show_white(self, roll_pixmap):
        self.roll_image.setPixmap(self.flash_bg_pixmap)
        self.timer.stop()
        
        # Show the actual pull result
        timer_callback = functools.partial(self.show_pull, roll_pixmap=roll_pixmap)
        self.timer.timeout.connect(timer_callback)
        self.timer.start(250)
        
    def show_pull(self, roll_pixmap):
        self.roll_image.setPixmap(roll_pixmap)
        self.timer.stop()

def showWidget() -> None:
    mw.myWidget = widget = DegenerankiWidget()
    widget.resize(1280, 900)
    widget.show()

def on_answer_button(reviewer, card, ease) -> None:
    if ease == 3 or ease == 4: # Good or Easy
        gacha.data.gacha_points = gacha.data.gacha_points + 1
    else:
        pass

    gacha.data.save()

# create a new menu item, "test"
action = QAction("Degeneranki", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, showWidget)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

# Hooks
gui_hooks.reviewer_did_answer_card.append(on_answer_button)
