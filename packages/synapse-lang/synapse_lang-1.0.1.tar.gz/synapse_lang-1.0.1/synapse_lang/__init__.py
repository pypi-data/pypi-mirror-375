"""
Synapse Programming Language
A revolutionary language for scientific computing with parallel execution and uncertainty quantification.

This software is proprietary and requires a valid license for commercial use.
Community Edition is available for personal and educational use.
"""

__version__ = "1.0.0"
__author__ = "Michael Benjamin Crowe"
__email__ = "michael@synapse-lang.com"
__license__ = "Proprietary (Dual License: Community/Commercial)"

# Initialize license manager
from .license_manager import get_license_manager, check_license_feature, track_usage

# Check license on import
_license = get_license_manager()
_license_info = _license.get_license_info()

print(f"Synapse Language v{__version__} - {_license_info['type'].title()} Edition")
if _license_info['type'] == 'community':
    print("ℹ️  For commercial use and full features, visit https://synapse-lang.com/pricing")

# Track initialization
track_usage("init", {"version": __version__})

# Core imports
from .interpreter import SynapseInterpreter
from .parser import parse_synapse_code
from .errors import SynapseError, ParseError, RuntimeError as RuntimeErrorSynapse

# Optimized imports
try:
    from .interpreter_optimized import OptimizedInterpreter, run_program
except ImportError:
    # Fallback if optimizations not available
    from .interpreter import SynapseInterpreter as OptimizedInterpreter
    def run_program(code: str, **kwargs):
        interpreter = SynapseInterpreter()
        return interpreter.interpret(code)

# Uncertainty support
from .interpreter import UncertainValue

# High-level API
def execute(code: str, *, optimized: bool = True, **kwargs):
    """
    Execute Synapse code with optional optimization.
    
    Args:
        code: Synapse source code
        optimized: Use optimized interpreter (default: True)
        **kwargs: Additional arguments for interpreter
    
    Returns:
        Execution result
    """
    if optimized:
        return run_program(code, **kwargs)
    else:
        interpreter = SynapseInterpreter()
        return interpreter.interpret(code)

def version():
    """Return the version string."""
    return __version__

__all__ = [
    "__version__",
    "SynapseInterpreter",
    "OptimizedInterpreter",
    "parse_synapse_code",
    "execute",
    "run_program",
    "UncertainValue",
    "SynapseError",
    "ParseError",
    "RuntimeErrorSynapse",
    "version",
]