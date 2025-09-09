"""
TwinTradeAi package
===================
Trading engine with indicators, signal building, risk management,
execution, runner, and API.
"""

__version__ = "1.0.1"

# --- Indicators ---
from twintradeai.indicators import add_indicators as add_indicators
ai = add_indicators  # alias

# --- Engine ---
from twintradeai.engine import (
    load_symbol_cfg,
    get_tf_data,
    build_signal,
    SYM_CFG,
)

# Aliases
lsc = load_symbol_cfg
gtf = get_tf_data
bs = build_signal

# --- RiskGuard ---
from twintradeai.risk_guard import RiskGuard
RG = RiskGuard  # alias

# --- Execution ---
from twintradeai.execution import execute_order, has_open_position, round_to_point

# Aliases
xo = execute_order
hop = has_open_position
rtp = round_to_point

# --- Runner ---
import twintradeai.runner as runner
run = runner  # alias

# --- API (lazy import) ---
def get_api_app():
    """Lazy load FastAPI app (prevents ZMQ bind on import)."""
    from twintradeai.api import app
    return app

# Expose lazy API app
api_app = get_api_app

# Export alias for clarity
api_layer = "twintradeai.api"  # just a reference string

# --- Export control ---
__all__ = [
    "__version__",

    # Indicators
    "add_indicators", "ai",

    # Engine
    "load_symbol_cfg", "get_tf_data", "build_signal", "SYM_CFG",
    "lsc", "gtf", "bs",

    # RiskGuard
    "RiskGuard", "RG",

    # Execution
    "execute_order", "has_open_position", "round_to_point",
    "xo", "hop", "rtp",

    # Runner
    "runner", "run",

    # API
    "get_api_app", "api_app", "api_layer",
]
