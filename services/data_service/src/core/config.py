from pathlib import Path 

PROJECT_ROOT = Path(__file__).parent.parent.parent 

DATA_DIR = PROJECT_ROOT / 'data'

BUSINESS_PATH = DATA_DIR /'businessfinal.json'
PHOTO_PATH = DATA_DIR / 'photosfinal.json'
REVIEW_PATH = DATA_DIR / 'reviewfinal.parquet'
USER_PATH = DATA_DIR / 'userfinal.parquet'