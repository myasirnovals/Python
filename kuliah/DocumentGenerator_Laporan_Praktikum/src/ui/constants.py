"""constants.py - Centralized UI constants and configuration."""

# Code file handling
CODE_EXTENSIONS = {
    ".html",
    ".css",
    ".js",
    ".jsx",
    ".ts",
    ".php",
    ".py",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".cs",
    ".pl",
    ".rb",
    ".go",
    ".swift",
    ".xml",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".sql",
    ".txt",
}

CODE_FILETYPE_PATTERN = (
    "*.html;*.css;*.js;*.jsx;*.ts;*.php;*.py;*.java;*.cpp;*.c;*.h;*.cs;*.pl;"
    "*.rb;*.go;*.swift;*.xml;*.json;*.yaml;*.yml;*.md;*.sql;*.txt"
)

MAX_CODE_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

# Image handling
SUPPORTED_IMAGE_FORMATS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"}
IMAGE_FILETYPE_PATTERN = "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff"
MAX_IMAGE_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# UI dimensions
WINDOW_WIDTH = 950
WINDOW_HEIGHT = 630
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 550
DEFAULT_PADDING = 15
DIALOG_PADDING = 20

# Dialog dimensions
EDITOR_DIALOG_WIDTH = 980
EDITOR_DIALOG_HEIGHT = 600
EDITOR_MIN_WIDTH = 860
EDITOR_MIN_HEIGHT = 540

MODUL_DIALOG_WIDTH = 560
MODUL_DIALOG_HEIGHT = 180

# Content settings
CONTENT_TYPE_SOURCE_CODE = "1"
CONTENT_TYPE_WORK_STEPS = "2"
CONTENT_TYPE_Q_AND_A = "3"

# Listbox settings
LISTBOX_FONT = ("Segoe UI", 11)
LISTBOX_FONT_SMALL = ("Segoe UI", 9)
LISTBOX_FONT_MONO = ("Consolas", 10)
LISTBOX_SELECT_COLOR = "#007bff"
LISTBOX_HEIGHT_SMALL = 3
LISTBOX_HEIGHT_MEDIUM = 6

# Dialog messages
MSG_VALIDATION_TITLE = "Validasi"
MSG_SUCCESS_TITLE = "Berhasil"
MSG_ERROR_TITLE = "Kesalahan"
MSG_WARNING_TITLE = "Peringatan"
MSG_AI_ERROR_TITLE = "AI Error"

# Tab labels
TAB_LABEL_RESULTS = "Hasil Praktikum"
TAB_LABEL_TASKS = "Tugas Praktikum"
TAB_LABEL_CONCLUSION = "Kesimpulan"
TAB_LABEL_GENERATE = "Selesai"

# Content type labels
LABEL_SOURCE_CODE = "Source Code"
LABEL_WORK_STEPS = "Langkah Kerja"
LABEL_Q_AND_A = "Q and A"
