import os

#------------------------------------------------------ User Zone ------------------------------------------------------

# Font settings
FONT_SIZE = 14
FONT = "Arial"
WARNING_FONT_SIZE = 24

#---------------------------------------------------- NOT User Zone ----------------------------------------------------

# Path to base directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Link to file with application icon
Assets_directory_name = "Assets"
App_icon_name = "icon.png"
ASSETS_DIR = os.path.join(CURRENT_DIR, ".." , Assets_directory_name)
APP_ICON = os.path.join(ASSETS_DIR, App_icon_name)

# Minimum graphic Y
MIN_GRAPHIC_Y_RANGE = 1000

