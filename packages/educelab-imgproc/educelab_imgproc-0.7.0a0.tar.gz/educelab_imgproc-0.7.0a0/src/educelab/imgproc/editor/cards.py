from functools import partial
from typing import List

from PySide6.QtCore import Signal
from PySide6.QtGui import QPalette, Qt
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QSizePolicy, QFrame,
                               QWidget, QHBoxLayout, QLabel, QSlider,
                               QScrollArea, QLayout,
                               QTreeWidget, QTreeWidgetItem, QDialog,
                               QDialogButtonBox, QGroupBox)

from educelab import imgproc
from educelab.imgproc.editor.widgets import DoubleSlider, LabeledDoubleSlider


class CardListWidget(QScrollArea):
    _cards_holder = None
    _cards = None

    settingsChanged = Signal()

    def __init__(self, parent=None):
        super(CardListWidget, self).__init__(parent=parent)

        self.setBackgroundRole(QPalette.Base)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setWidgetResizable(True)
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)
        self.setMinimumSize(100, 150)

        self._cards_holder = QWidget()
        self._cards_holder.setLayout(QVBoxLayout())
        self._cards_holder.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self._cards_holder.setSizePolicy(QSizePolicy.MinimumExpanding,
                                         QSizePolicy.MinimumExpanding)
        self._cards_holder.setMinimumSize(100, 100)
        self._add_card = AddCard()
        self._add_card.clicked.connect(self._on_new_card)
        self._cards_holder.layout().addWidget(self._add_card)
        self.setWidget(self._cards_holder)

        self._new_card_dialog = AdjustmentsMenu(parent=self)

        self._cards = []

    def _on_new_card(self):
        if self._new_card_dialog.exec():
            keys = self._new_card_dialog.selected_adjustment()
            val = _adjustments_menu
            for k in keys:
                val = val[k]
            self.add_card(val())

    def add_card(self, card: QWidget):
        card_cnt = self._cards_holder.layout().count()
        card.list_index = card_cnt
        self._cards_holder.layout().insertWidget(card_cnt - 1, card)
        self._cards.append(card)
        card.clickedClose.connect(self.remove_card)
        card.settingsChanged.connect(self.settingsChanged.emit)
        self.settingsChanged.emit()

    def remove_card(self, idx: int):
        w = self._cards.pop(idx - 1)
        w.setParent(None)
        self._cards_holder.layout().removeWidget(w)

        # update the cards
        for idx, w in enumerate(self._cards):
            w.list_index = idx + 1

        self.settingsChanged.emit()

    def cards(self):
        return self._cards

    def set_enabled(self, b: bool):
        self._add_card.setEnabled(b)
        for c in self._cards:
            c.set_enabled(b)

    # @property
    # def card_list(self):
    #     return [c.settings for c in self._cards]
    #
    # @card_list.setter
    # def card_list(self, cards):
    #     for c in cards:
    #         card = CopyJobCard()
    #         card.settings = c
    #         self.add_card(card)


class AddCard(QPushButton):
    def __init__(self, parent=None):
        super(AddCard, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setAlignment(Qt.AlignCenter)
        self.setMinimumSize(100, 40)
        self.setMaximumHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setToolTip('Add')

        self.setText('+')
        self.setForegroundRole(QPalette.PlaceholderText)
        self.setStyleSheet("""
            QPushButton {
                color: palette(window);
                border-width: 2px;
                border-style: dashed;
                border-color: palette(window);
                border-radius: 4px;
            }
            QPushButton:hover {
                color: palette(dark);
                border-color: palette(dark);
                background-color: palette(window);
            }
            QPushButton:pressed {
                color: palette(window-text);
                border-style: none;
                background-color: palette(dark);
            }
            """)

    @property
    def list_index(self) -> int:
        return -1

    @list_index.setter
    def list_index(self, index: int):
        pass


class BaseCard(QFrame):
    clickedClose = Signal(int)
    settingsChanged = Signal()

    _list_index = None
    _label = None

    def __init__(self, label=None, parent=None):
        super(BaseCard, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.setBackgroundRole(QPalette.Window)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setMinimumSize(100, 150)
        self.setMaximumHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout().setSpacing(0)

        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_widget.setLayout(title_layout)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        self.layout().addWidget(title_widget)

        self._card_label = QLabel()
        self._card_label.setForegroundRole(QPalette.PlaceholderText)
        self._card_label.setStyleSheet('QLabel{font-size: 10pt}')
        self._label = label
        title_layout.addSpacing(2)
        title_layout.addWidget(self._card_label, 0, Qt.AlignLeft)

        close_button = QPushButton('\u00d7')
        close_button.setForegroundRole(QPalette.PlaceholderText)
        close_button.setFlat(True)
        close_button.setLayout(QHBoxLayout())
        close_button.layout().setContentsMargins(0, 0, 0, 0)
        close_button.layout().setSpacing(0)
        close_button.layout().setAlignment(Qt.AlignCenter)
        close_button.setMinimumSize(24, 24)
        close_button.setMaximumSize(24, 24)
        close_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        close_button.setStyleSheet("""
            QPushButton {
                color: palette(dark);
            }
            QPushButton:hover {
                color: palette(text);
            }
            QPushButton:pressed {
                color: palette(text);
                border: none;
                background-color: palette(dark);
            }
            """)
        close_button.setToolTip('Remove')
        close_button.clicked.connect(self._on_click_close)
        self._close_button = close_button
        title_layout.addWidget(close_button, 0, Qt.AlignRight)

    def _on_click_close(self):
        self.clickedClose.emit(self._list_index)

    @property
    def list_index(self) -> int:
        return self._list_index

    @list_index.setter
    def list_index(self, index: int):
        self._list_index = index
        label = str(index)
        if self._label is not None:
            label = f'{label}: {self._label}'
        self._card_label.setText(label)


class DoubleSliderCard(BaseCard):
    _apply_fn = None

    def __init__(self, label, fn, x_min, x_max, step_size, show_ticks=False,
                 init_val=0, parent=None):
        super(DoubleSliderCard, self).__init__(label=label, parent=parent)

        ctrls_widget = QWidget()
        ctrls_layout = QVBoxLayout()
        ctrls_layout.setContentsMargins(0, 0, 0, 0)
        ctrls_widget.setLayout(ctrls_layout)
        self.layout().addWidget(ctrls_widget)
        self.setMinimumHeight(100)
        self.setMaximumHeight(100)

        self.slider = DoubleSlider()
        ctrls_layout.addWidget(self.slider)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMinimum(x_min)
        self.slider.setMaximum(x_max)
        if show_ticks:
            self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setInterval(step_size)
        self.slider.setValue(init_val)
        self.slider.doubleValueChanged.connect(
            lambda x: self.settingsChanged.emit())

        val_label = QLabel()
        ctrls_layout.addWidget(val_label)
        val_label.setAlignment(Qt.AlignHCenter)
        val_label.setText(str(init_val))
        self.slider.doubleValuePreview.connect(
            lambda v: val_label.setText(f'{v:.03g}'))

        self._apply_fn = fn

    @property
    def apply_function(self):
        return partial(self._apply_fn, val=self.slider.value())


class HighlightsShadowsCard(BaseCard):

    def __init__(self, parent=None):
        super(HighlightsShadowsCard, self).__init__('Highlights/Shadows',
                                                    parent)
        self.setMinimumHeight(600)
        self.setMaximumHeight(600)

        luma_ctrls = QGroupBox('Luma')
        luma_layout = QVBoxLayout()
        luma_ctrls.setLayout(luma_layout)
        self.layout().addWidget(luma_ctrls)

        # shadow % [-1, 1]
        luma_layout.addWidget(QLabel('Shadows'))
        self.sh_perc = LabeledDoubleSlider(Qt.Orientation.Horizontal)
        self.sh_perc.slider.setRange(-1, 1)
        self.sh_perc.slider.setInterval(0.05)
        self.sh_perc.slider.setValue(0)
        self.sh_perc.doubleValueChanged.connect(
            lambda x: self.settingsChanged.emit())
        luma_layout.addWidget(self.sh_perc)
        # highlight % [-1, 1]
        luma_layout.addWidget(QLabel('Highlights'))
        self.hl_perc = LabeledDoubleSlider(Qt.Orientation.Horizontal)
        self.hl_perc.slider.setRange(-1, 1)
        self.hl_perc.slider.setInterval(0.05)
        self.hl_perc.slider.setValue(0)
        self.hl_perc.doubleValueChanged.connect(
            lambda x: self.settingsChanged.emit())
        luma_layout.addWidget(self.hl_perc)

        chroma_ctrls = QGroupBox('Chroma')
        chroma_layout = QVBoxLayout()
        chroma_ctrls.setLayout(chroma_layout)
        self.layout().addWidget(chroma_ctrls)

        # shadow correct [0, 1]
        chroma_layout.addWidget(QLabel('Shadows'))
        self.sh_adj = LabeledDoubleSlider(Qt.Orientation.Horizontal)
        self.sh_adj.slider.setRange(0, 1)
        self.sh_adj.slider.setInterval(0.1)
        self.sh_adj.slider.setValue(1.)
        self.sh_adj.doubleValueChanged.connect(
            lambda x: self.settingsChanged.emit())
        chroma_layout.addWidget(self.sh_adj)

        # highlight correct [0, 1]
        chroma_layout.addWidget(QLabel('Highlights'))
        self.hl_adj = LabeledDoubleSlider(Qt.Orientation.Horizontal)
        self.hl_adj.slider.setRange(0, 1)
        self.hl_adj.slider.setInterval(0.1)
        self.hl_adj.slider.setValue(0.5)
        self.hl_adj.doubleValueChanged.connect(
            lambda x: self.settingsChanged.emit())
        chroma_layout.addWidget(self.hl_adj)

        adv_ctrls = QGroupBox('Advanced')
        adv_layout = QVBoxLayout()
        adv_ctrls.setLayout(adv_layout)
        self.layout().addWidget(adv_ctrls)

        # Midtone compression effect
        adv_layout.addWidget(QLabel('Compress'))
        self.md_perc = LabeledDoubleSlider(Qt.Orientation.Horizontal)
        self.md_perc.slider.setRange(0, 1)
        self.md_perc.slider.setInterval(0.05)
        self.md_perc.slider.setValue(0.5)
        self.md_perc.doubleValueChanged.connect(
            lambda x: self.settingsChanged.emit())
        adv_layout.addWidget(self.md_perc)

        adv_layout.addWidget(QLabel('Sigma'))
        self.sigma = LabeledDoubleSlider(Qt.Orientation.Horizontal)
        self.sigma.slider.setRange(0.05, 5)
        self.sigma.slider.setInterval(0.05)
        self.sigma.slider.setValue(1)
        self.sigma.doubleValueChanged.connect(
            lambda x: self.settingsChanged.emit())
        adv_layout.addWidget(self.sigma)

    @property
    def apply_function(self):
        return partial(imgproc.shadows_highlights,
                       shadows_gain=self.sh_perc.value(),
                       highlights_gain=self.hl_perc.value(),
                       shadows_correct=self.sh_adj.value(),
                       highlights_correct=self.hl_adj.value(),
                       compress=self.md_perc.value(),
                       sigma=self.sigma.value())


_adjustments_menu = {
    'Adjust': {
        'Brightness': partial(DoubleSliderCard, 'Brightness',
                              imgproc.brightness, -1., 1., 0.01),
        'Contrast': partial(DoubleSliderCard, 'Contrast', imgproc.contrast, -1.,
                            1., 0.01),
        'Exposure': partial(DoubleSliderCard, 'Exposure', imgproc.exposure, -5,
                            5, 0.1),
        'Highlights/Shadows': HighlightsShadowsCard,
        'Shadows': partial(DoubleSliderCard, 'Shadows', imgproc.shadows, -100,
                           100, 1)
    },
    'Correction': {},
    'Enhance': {},
    'Filters': {}
}


class AdjustmentsMenu(QDialog):
    def __init__(self, parent=None):
        super(AdjustmentsMenu, self).__init__(parent=parent)
        layout = QVBoxLayout()
        self.setWindowTitle('New Adjustment')
        self.setLayout(layout)
        self.setModal(True)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        items = []
        for group, values in _adjustments_menu.items():
            item = QTreeWidgetItem([group])
            for value in values.keys():
                child = QTreeWidgetItem([value])
                item.addChild(child)
            items.append(item)
        self._tree.insertTopLevelItems(0, items)
        self._tree.expandAll()
        layout.addWidget(self._tree)

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self._button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        layout.addWidget(self._button_box)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self):
        ok_button = self._button_box.button(QDialogButtonBox.Ok)
        selected = self._tree.selectedItems()[0]
        ok_button.setEnabled(
            selected.parent() is not None and selected.childCount() == 0)

    def selected_adjustment(self) -> List[str]:
        keys = []
        item = self._tree.selectedItems()[0]
        keys.append(item.text(0))
        while item.parent() is not None:
            item = item.parent()
            keys.insert(0, item.text(0))
        return keys
