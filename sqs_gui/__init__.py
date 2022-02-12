# Registers application resources (images, icons, etc...)
# Resources compiled with: pyrcc5.exe -o res.py .\res.qrc
from .app import resources

# Explicitly import some dependencies
# to make them imported by pyinstaller
import coloredlogs