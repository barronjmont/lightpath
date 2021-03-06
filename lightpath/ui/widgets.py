"""
Definitions for Lightpath Widgets
"""
import logging
from enum import Enum

from pydm.PyQt.QtCore import Qt
from pydm.PyQt.QtGui import QPen, QSizePolicy, QHBoxLayout, QWidget, QLabel
from pydm.PyQt.QtGui import QFont, QSpacerItem, QPushButton
from pydm.widgets.drawing import PyDMDrawingRectangle


logger = logging.getLogger(__name__)


class InactiveRow:
    """
    Inactive row for happi container
    """
    font = QFont()
    font.setPointSize(14)
    # Italic
    italic = QFont()
    font.setPointSize(12)
    italic.setItalic(True)
    # Bold
    bold = QFont()
    bold.setBold(True)

    def __init__(self, device, parent=None):
        self.device = device
        # Create labels
        self.name_label = QLabel(parent=parent)
        self.name_label.setText(device.name)
        self.name_label.setFont(self.bold)
        self.prefix_label = QLabel(parent=parent)
        self.prefix_label.setObjectName('prefix_frame')
        self.prefix_label.setText('({})'.format(device.prefix))
        self.prefix_label.setFont(self.italic)
        self.state_label = QLabel('Disconnected', parent=parent)
        self.state_label.setFont(self.bold)
        self.state_label.setStyleSheet("QLabel {color : rgb(255,0,255)}")
        # Create Beam Indicator
        self.indicator = PyDMDrawingRectangle(parent=parent)
        self.indicator.setMinimumSize(45, 55)
        self.indicator.setSizePolicy(QSizePolicy.Fixed,
                                     QSizePolicy.Expanding)
        self.indicator._pen = QPen(Qt.SolidLine)
        # Spacer
        self.spacer = QSpacerItem(40, 20)

    @property
    def widgets(self):
        """
        Ordered list of widgets to add to designer
        """
        return [self.indicator,
                self.name_label,
                self.prefix_label,
                self.spacer,
                self.state_label]

    def clear_sub(self):
        """
        Implemented by rows that have subscriptions
        """
        pass


class LightRow(InactiveRow):
    """
    Basic Widget to display LightDevice information

    The widget shows the device information and state, updating looking at the
    devices :attr:`.inserted` and :attr:`.removed` attributes. The
    :attr:`.remove_button` also allows the user to remove devices by calling
    the :meth:`.remove` method of the given device. The identical button is
    setup if the device is determined to have an `insert` method. Finally,
    PyDMRectangle is used to show the current path of the beam through the
    table

    Parameters
    ----------
    device : obj

    path : BeamPath

    parent : QObject, optional
    """
    def __init__(self, device, parent=None):
        super().__init__(device, parent=parent)
        # Create button widget
        self.buttons = QWidget(parent=parent)
        self.button_layout = QHBoxLayout()
        self.buttons.setLayout(self.button_layout)
        # Create Insert PushButton
        if hasattr(device, 'insert'):
            self.insert_button = QPushButton('Insert', parent=parent)
            self.insert_button.setFont(self.font)
            self.button_layout.addWidget(self.insert_button)
            self.button_layout.addItem(QSpacerItem(10, 20))
        # Create Remove PushButton
        if hasattr(device, 'remove'):
            self.remove_button = QPushButton('Remove', parent=parent)
            self.remove_button.setFont(self.font)
            self.button_layout.addWidget(self.remove_button)
        # Subscribe device to state changes
        try:
            # Wait for later to update widget
            self.device.subscribe(self.update_state,
                                  event_type=self.device.SUB_STATE,
                                  run=False)
        except Exception:
            logger.error("Widget is unable to subscribe to device %s",
                         device.name)

    def update_state(self, *args, **kwargs):
        """
        Update the state label

        The displayed state can be one of ``Unknown`` , ``Inserted``,
        ``Removed`` or ``Error``, with ``Unknown`` being if the device is not
        inserted or removed, and error being if the device is reporting as both
        inserted and removed. The color of the label is also adjusted to either
        green or red to quickly
        """
        states = Enum('states', ('Unknown', 'Inserted', 'Removed', 'Error'))
        # Interpret state
        try:
            state = 1 + int(self.device.inserted) + 2*int(self.device.removed)
        except Exception as exc:
            logger.error(exc)
            state = states.Error.value
        # Set label to state description
        self.state_label.setText(states(state).name)
        # Set the color of the label
        if state == states.Removed.value:
            self.state_label.setStyleSheet("QLabel {color : rgb(124,252,0)}")
        elif state == states.Unknown.value:
            self.state_label.setStyleSheet("QLabel {color : rgb(255, 215, 0)}")
        else:
            self.state_label.setStyleSheet("QLabel {color : red}")
        # Disable buttons if necessary
        if hasattr(self, 'insert_button'):
            self.insert_button.setEnabled(state != states.Inserted.value)
        if hasattr(self, 'remove_button'):
            self.remove_button.setEnabled(state != states.Removed.value)

    @property
    def widgets(self):
        """
        Ordered list of widgets to add to designer
        """
        return [self.indicator,
                self.name_label,
                self.prefix_label,
                self.spacer,
                self.state_label,
                self.buttons]

    def clear_sub(self):
        """
        Clear the subscription event
        """
        self.device.clear_sub(self.update_state)
