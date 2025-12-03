from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.parent

MODEL_DIR = PROJECT_ROOT / "models"

LINK_PRED_MODEL = MODEL_DIR / "link_pred.pth"
EDGE_PRED_MODEL = MODEL_DIR / "edge_pred.pth"

print(PROJECT_ROOT)