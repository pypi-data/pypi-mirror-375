"""spotify_data_analytics package."""

__all__ = ["extract_main", "transform_main", "load_main"]
__version__ = "0.1.0"

# convenience imports (expose main helpers)
from .extract_data import main as extract_main
from .transform_data import main as transform_main
from .load_data import main as load_main
