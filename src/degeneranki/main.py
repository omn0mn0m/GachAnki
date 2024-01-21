import functools
import sys
import urllib3
from os import path
from enum import Enum

from .gacha import GachaMachine
from .database import Database

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

class DegenerankiWidget(QTabWidget):
    
    def __init__(self, *args, **kwargs):
        super(DegenerankiWidget, self).__init__(*args, **kwargs)

        self.gachaTab = GachaWidget()
        self.addTab(self.gachaTab, "Gacha")

        self.charactersTab = InventoryWidget(InventoryWidget.InventoryTypes.CHARACTERS)
        self.addTab(self.charactersTab, "Characters")

        self.weaponsTab = InventoryWidget(InventoryWidget.InventoryTypes.WEAPONS)
        self.addTab(self.weaponsTab, "Weapons")

class InventoryWidget(QScrollArea):

    class InventoryTypes(Enum):
        WEAPONS = 0,
        CHARACTERS = 1
    
    def __init__(self, inventory_type, *args, **kwargs):
        super(InventoryWidget, self).__init__(*args, **kwargs)
        
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_finished)

        self.wrapper_widget = QWidget()
        self.grid_layout = QGridLayout(self.wrapper_widget)
        self.setWidget(self.wrapper_widget)
        self.setWidgetResizable(True)

        self.max_col_items = 4

        self.row = 0
        self.col = 0

        self.grid_info = {}

        if inventory_type == InventoryWidget.InventoryTypes.WEAPONS:
            for i, data in enumerate(gacha.data.get_owned_weapons()):
                info = gacha.data.weapons[data[0]]
                self.add_to_grid(info)
        elif inventory_type == InventoryWidget.InventoryTypes.CHARACTERS:
            for i, data in enumerate(gacha.data.get_owned_characters()):
                info = gacha.data.characters[data[0]]
                self.add_to_grid(info)

    def add_to_grid(self, info):
        request = QNetworkRequest(QUrl(info.icon))
        self.network_manager.get(request)

    @pyqtSlot(QNetworkReply)
    def on_finished(self, reply):
        inventory_label = QLabel()
        label_measure = self.width() // self.max_col_items
        inventory_label.setFixedWidth(label_measure)
        inventory_label.setFixedHeight(label_measure)
        
        image = QImage()
        image.loadFromData(reply.readAll())
        
        image_pixmap = QPixmap.fromImage(image)
        inventory_label.setPixmap(image_pixmap.scaled(inventory_label.size(), 
                                                      Qt.AspectRatioMode.KeepAspectRatio, 
                                                      Qt.TransformationMode.SmoothTransformation))
        self.grid_layout.addWidget(inventory_label, self.row, self.col)

        self.col += 1

        if self.col == self.max_col_items:
            self.col = 0
            self.row += 1

class GachaWidget(QWidget):
    
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

        self.lifetime_rolls = QLabel("Lifetime Rolls: {}".format(gacha.data.lifetime_rolls))
        self.roll_stats_layout.addWidget(self.lifetime_rolls)

        self.pity_4_star = QLabel("4-Star Pity: {}".format(gacha.data.pity_4_star))
        self.roll_stats_layout.addWidget(self.pity_4_star)

        self.pity_5_star = QLabel("5-Star Pity: {}".format(gacha.data.pity_5_star))
        self.roll_stats_layout.addWidget(self.pity_5_star)

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
            max(480, image_pixmap.width()), # max(480, min(image_pixmap.width(), MAX_ROLL_IMAGE_WIDTH)),
            max(480, image_pixmap.height()), # max(480, min(image_pixmap.height(), MAX_ROLL_IMAGE_HEIGHT)),
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

    def show_inventory(self):
        pass

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
