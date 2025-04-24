from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input_imgs"
INPRO_DIR = BASE_DIR / "inpro_imgs"
EXIT_DIR = BASE_DIR / "exit_imgs"

def create_dirs():
    """Create all required directories"""
    for directory in [INPUT_DIR, INPRO_DIR, EXIT_DIR]:
        directory.mkdir(exist_ok=True)