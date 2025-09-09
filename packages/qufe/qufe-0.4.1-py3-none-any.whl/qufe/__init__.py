"""
qufe - A comprehensive Python utility library

A collection of utilities for data processing, file handling, database management,
automation tasks, and more.

This library uses optional dependencies to minimize the impact on your environment.
Install only the features you need:

    pip install qufe[database]    # Database operations
    pip install qufe[data]        # Pandas/NumPy data processing
    pip install qufe[web]         # Browser automation
    pip install qufe[vision]      # Screen capture and image processing
    pip install qufe[jupyter]     # Jupyter notebook integration
    pip install qufe[all]         # All optional dependencies

For detailed installation and usage instructions, see: https://qufe.readthedocs.io
"""

__version__ = "0.4.1"
__author__ = "Bongtae Jeon"
__email__ = "bongtae.jeon@gmail.com"

# Core modules (no external dependencies)
from . import base
from . import excludebracket
from . import texthandler
from . import filehandler

# Always available core functions
from .base import TS, diff_codes, import_script, flatten, flatten_gen
from .excludebracket import eb2, check_eb
from .texthandler import print_dict, print_in_columns, list_to_doku_wiki_table
from .filehandler import FileHandler, PathFinder

# Track available optional modules
_available_modules = {
    'base': True,
    'excludebracket': True,
    'texthandler': True,
    'filehandler': True,
    'dbhandler': False,
    'pdhandler': False,
    'wbhandler': False,
    'interactionhandler': False
}

# Optional modules with graceful fallback
try:
    from . import dbhandler
    from .dbhandler import PostgreSQLHandler
    _available_modules['dbhandler'] = True
except ImportError as e:
    dbhandler = None
    PostgreSQLHandler = None
    # Store import error for help() function
    _import_errors = getattr(globals(), '_import_errors', {})
    _import_errors['dbhandler'] = str(e)

try:
    from . import pdhandler
    _available_modules['pdhandler'] = True
except ImportError as e:
    pdhandler = None
    _import_errors = getattr(globals(), '_import_errors', {})
    _import_errors['pdhandler'] = str(e)

try:
    from . import wbhandler
    _available_modules['wbhandler'] = True
except ImportError as e:
    wbhandler = None
    _import_errors = getattr(globals(), '_import_errors', {})
    _import_errors['wbhandler'] = str(e)

try:
    from . import interactionhandler
    _available_modules['interactionhandler'] = True
except ImportError as e:
    interactionhandler = None
    _import_errors = getattr(globals(), '_import_errors', {})
    _import_errors['interactionhandler'] = str(e)


def help():
    """
    Display help information about qufe library and available modules.

    Shows which modules are available and provides installation instructions
    for missing optional dependencies.
    """
    print(f"qufe v{__version__} - Python Utility Library")
    print("=" * 50)
    print()

    print("AVAILABLE MODULES:")
    print("-" * 20)
    for module_name, is_available in _available_modules.items():
        status = "✓" if is_available else "✗"
        print(f"  {status} {module_name}")
    print()

    # Show unavailable modules with installation help
    unavailable = [name for name, available in _available_modules.items() if not available]
    if unavailable:
        print("MISSING OPTIONAL DEPENDENCIES:")
        print("-" * 35)

        install_suggestions = {
            'dbhandler': 'pip install qufe[database]',
            'pdhandler': 'pip install qufe[data]',
            'wbhandler': 'pip install qufe[web]',
            'interactionhandler': 'pip install qufe[vision]'
        }

        for module_name in unavailable:
            suggestion = install_suggestions.get(module_name, f'pip install qufe[all]')
            print(f"  • {module_name}: {suggestion}")
        print()

        print("To install all optional dependencies: pip install qufe[all]")
        print()

    print("CORE FUNCTIONALITY (always available):")
    print("-" * 40)
    print("  • base: Timestamp handling, code comparison, list flattening")
    print("  • texthandler: String processing, formatting, DokuWiki tables")
    print("  • filehandler: File operations, directory traversal, pickle support")
    print("  • excludebracket: Bracket content removal with validation")
    print()

    if _available_modules['dbhandler']:
        print("DATABASE OPERATIONS:")
        print("  • PostgreSQL connection and query management")
        print("  • Database and table exploration")
        print()

    if _available_modules['pdhandler']:
        print("DATA PROCESSING:")
        print("  • pandas DataFrame utilities and analysis")
        print("  • Missing data detection and validation")
        print()

    if _available_modules['wbhandler']:
        print("WEB AUTOMATION:")
        print("  • SeleniumBase browser automation")
        print("  • Network request monitoring and capture")
        print()

    if _available_modules['interactionhandler']:
        print("SCREEN AUTOMATION:")
        print("  • Screen capture and image processing")
        print("  • Mouse automation and color detection")
        print()

    print("For detailed documentation: https://qufe.readthedocs.io")
    print(f"Python {__import__('sys').version_info.major}.{__import__('sys').version_info.minor}+ required (current: {__import__('sys').version_info.major}.{__import__('sys').version_info.minor}.{__import__('sys').version_info.micro})")


def check_dependencies():
    """
    Check which optional dependencies are available and return status dict.

    Returns:
        dict: Dictionary mapping module names to availability status
    """
    return _available_modules.copy()


def get_missing_dependencies():
    """
    Get list of missing optional dependencies with installation suggestions.

    Returns:
        dict: Dictionary mapping missing module names to pip install commands
    """
    missing = {}
    install_map = {
        'dbhandler': 'pip install qufe[database]',
        'pdhandler': 'pip install qufe[data]',
        'wbhandler': 'pip install qufe[web]',
        'interactionhandler': 'pip install qufe[vision]'
    }

    for module_name, is_available in _available_modules.items():
        if not is_available and module_name in install_map:
            missing[module_name] = install_map[module_name]

    return missing


# Export list for explicit imports
__all__ = [
    # Always available
    '__version__',
    'help',
    'check_dependencies',
    'get_missing_dependencies',

    # Core modules
    'base',
    'excludebracket',
    'texthandler',
    'filehandler',

    # Core classes and functions
    'TS',
    'FileHandler',
    'PathFinder',
    'diff_codes',
    'import_script',
    'flatten',
    'flatten_gen',
    'print_dict',
    'print_in_columns',
    'list_to_doku_wiki_table',
    'eb2',
    'check_eb',
]

# Add optional exports if available
if _available_modules['dbhandler']:
    __all__.extend(['dbhandler', 'PostgreSQLHandler'])

if _available_modules['pdhandler']:
    __all__.append('pdhandler')

if _available_modules['wbhandler']:
    __all__.append('wbhandler')

if _available_modules['interactionhandler']:
    __all__.append('interactionhandler')


# Initialize with helpful message for first-time users
def _show_welcome():
    """Show welcome message on first import (only in interactive environments)."""
    try:
        # Only show in interactive environments like Jupyter
        if hasattr(__builtins__, '__IPYTHON__') or hasattr(__import__('sys'), 'ps1'):
            missing = get_missing_dependencies()
            if missing:
                print(f"qufe v{__version__} loaded! Some optional features require additional packages.")
                print("Run qufe.help() for installation instructions.")
    except:
        # Silently fail if we can't detect environment
        pass


_show_welcome()
