import os

# Path to base directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


# Link to file with application icon
Assets_directory_name = "Assets"
App_icon_name = "icon.png"
ASSETS_DIR = os.path.join(CURRENT_DIR, ".." , Assets_directory_name)
APP_ICON = os.path.join(ASSETS_DIR, App_icon_name)