"""
huez - A Python package for huez
"""

__version__ = "0.0.1a1"
__author__ = "Huez Team"
__email__ = "huez@huez.org"

def hello():
    """
    A simple hello function for package verification.
    
    Returns:
        str: A greeting message
    """
    return f"Hello from huez v{__version__}!"

# Package metadata
__all__ = ["hello", "__version__", "__author__", "__email__"]