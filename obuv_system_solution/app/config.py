from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / 'shoe_store.sqlite3'
RESOURCES_DIR = BASE_DIR / 'resources'
IMAGES_DIR = RESOURCES_DIR / 'images'
IMPORT_DIR = RESOURCES_DIR / 'import'
DEFAULT_PICTURE = RESOURCES_DIR / 'picture.png'
APP_ICON = RESOURCES_DIR / 'icon.png'

APP_TITLE = 'ООО «Обувь»'
FONT_FAMILY = 'Times New Roman'
COLOR_MAIN_BG = '#FFFFFF'
COLOR_SECONDARY_BG = '#7FFF00'
COLOR_ACCENT = '#00FA9A'
COLOR_DISCOUNT_OVER_15 = '#2E8B57'
COLOR_OUT_OF_STOCK = '#ADD8E6'
COLOR_ERROR = '#FFECEC'
