# qufe

A comprehensive Python utility library for data processing, file handling, database management, and automation tasks.

Born from the need to streamline repetitive tasks in Jupyter Lab environments, qufe addresses common pain points encountered during interactive development and data exploration work.

**NEW in v0.4.0**: Modular architecture with optional dependencies - install only what you need!

## Python Version Requirement

**Important**: qufe requires **Python 3.10 or higher**.

This requirement exists because qufe uses modern Python features for better performance and code clarity:
- **zoneinfo module** (Python 3.9+): Standard library timezone support
- **Structural pattern matching** (Python 3.10+): match-case statements for cleaner logic
- **Union type operator** (Python 3.10+): `int | float` syntax for improved type hints

We made this decision to leverage modern Python capabilities that enhance the library's functionality and maintainability.

## Installation

### Quick Start (Core Features Only)
```bash
# Install core functionality with no external dependencies
pip install qufe
```

### Feature-Specific Installation
Install only the features you need:

```bash
# Database operations (PostgreSQL)
pip install qufe[database]

# Data processing with pandas/numpy  
pip install qufe[data]

# Web browser automation
pip install qufe[web]

# Screen capture and image processing
pip install qufe[vision]
```

## Features Overview

### Always Available (Core Features)

#### Base Utilities (`qufe.base`)
- **Timestamp handling**: Convert timestamps with timezone support
- **Code comparison**: Compare code snippets with multiple diff formats  
- **Dynamic imports**: Import Python modules from file paths
- **List flattening**: Flatten nested structures with configurable depth
- **Dictionary utilities**: Advanced nested dictionary operations

#### Text Processing (`qufe.texthandler`, `qufe.excludebracket`) 
- **Bracket content removal**: Validate and remove bracketed content
- **DokuWiki formatting**: Convert data to DokuWiki table format
- **String utilities**: Advanced search with context extraction
- **Pretty printing**: Format nested dictionaries and lists
- **Column display**: Multi-column text formatting with alignment

#### File Operations (`qufe.filehandler`)
- **Directory traversal**: Recursive file listing with Unicode normalization
- **Pattern matching**: Find latest files by datetime patterns
- **Pickle operations**: Simplified Python object persistence
- **Path utilities**: Safe filename generation and path management
- **Content extraction**: Text extraction from directory structures

### Optional Features (Require Additional Packages)

#### Database Management (`qufe.dbhandler`) - *[database]*
- **PostgreSQL integration**: Easy connections using SQLAlchemy
- **Database exploration**: List databases and tables with metadata
- **Connection management**: Automatic pooling and cleanup
- **Environment integration**: .env file and environment variable support

#### Data Analysis (`qufe.pdhandler`) - *[data]*
- **DataFrame utilities**: Type conversion and structure analysis
- **Column comparison**: Compare schemas across multiple DataFrames
- **Missing data detection**: Find NA values and empty strings
- **Data validation**: Comprehensive quality checks

#### Web Automation (`qufe.wbhandler`) - *[web]*
- **SeleniumBase integration**: Enhanced browser automation
- **Network monitoring**: Capture fetch/XHR requests
- **Element discovery**: Interactive element finding utilities  
- **URL parsing**: Extract and manipulate URL parameters
- **Multi-browser support**: Firefox implementation with profile detection

#### Screen Interaction (`qufe.interactionhandler`) - *[vision]*
- **Screen capture**: Full screen or region-specific screenshots
- **Image processing**: Color detection and comparison algorithms
- **Mouse automation**: Randomized clicking for natural automation
- **Progress tracking**: Real-time updates in Jupyter notebooks
- **Color analysis**: Extract and analyze color information

## Quick Start Guide

### 1. Check Installation Status
```python
import qufe

# See what's available
qufe.help()

# Check dependencies programmatically
status = qufe.check_dependencies()
print(status)

# Get installation commands for missing features
missing = qufe.get_missing_dependencies()
for module, command in missing.items():
    print(f"{module}: {command}")
```

### 2. Core Features (Always Available)
```python
from qufe import base, texthandler, filehandler

# Timestamp handling with timezone
ts = base.TS('Asia/Seoul')
formatted = ts.get_ts_formatted(1640995200)

# File operations
fh = filehandler.FileHandler()
files = fh.get_tree('/path/to/directory')

# Text processing
data = [['Name', 'Age'], ['Alice', '25'], ['Bob', '30']]
texthandler.list_to_doku_wiki_table(data)

# Directory exploration
pf = filehandler.PathFinder('/starting/path')
root, dirs, files = pf.get_one_depth()
```

### 3. Database Operations (Optional)
```bash
# Install database support first
pip install qufe[database]
```

#### Configuration Options

**Option 1: .env file (Recommended)**
```bash
# Create .env file in your project root
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_database
```

**Option 2: Environment variables**
```bash
export POSTGRES_USER=your_username
export POSTGRES_PASSWORD=your_password
# ... etc
```

**Option 3: Direct parameters**
```python
from qufe.dbhandler import PostgreSQLHandler

# Use .env or environment variables
db = PostgreSQLHandler()

# Or specify directly
db = PostgreSQLHandler(
    user='username',
    password='password', 
    host='localhost',
    port=5432,
    db_name='database'
)

# Usage
databases = db.get_database_list()
tables = db.get_table_list()
results = db.execute_query("SELECT * FROM users LIMIT 5")
```

### 4. Data Processing (Optional)
```bash
pip install qufe[data]
```

```python
from qufe.pdhandler import show_col_names, show_all_na
import pandas as pd

# Compare DataFrames
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df2 = pd.DataFrame({'B': [5, 6], 'C': [7, 8]})
col_dict, comparison = show_col_names([df1, df2])

# Find missing data
na_subset = show_all_na(df1)
```

### 5. Web Automation (Optional)
```bash
pip install qufe[web]
```

```python
from qufe.wbhandler import Firefox

# Start browser
browser = Firefox(private_mode=True)
browser.sb.open('https://example.com')

# Network monitoring
browser.inject_network_capture()
# ... perform actions ...
logs = browser.get_network_logs()

# Clean up
browser.quit_driver()
```

### 6. Screen Automation (Optional)
```bash
pip install qufe[vision]
```

```python
from qufe.interactionhandler import get_screenshot, display_image, get_color_boxes

# Capture screen
screenshot = get_screenshot(100, 100, 800, 600)
display_image(screenshot, is_bgra=True)

# Find colored regions
red_boxes = get_color_boxes(screenshot, (255, 0, 0), tolerance=0.1)
```

## Module-Specific Help

Each module provides detailed help information:

```python
# General help
import qufe
qufe.help()

# Module-specific help
from qufe import dbhandler, pdhandler, wbhandler, interactionhandler
dbhandler.help()      # Database operations guide
pdhandler.help()      # pandas utilities guide  
wbhandler.help()      # Browser automation guide
interactionhandler.help()  # Screen interaction guide
```

## Dependency Details

| Feature Group | Dependencies | Purpose |
|---------------|--------------|---------|
| `database` | sqlalchemy≥1.3.0, python-dotenv≥0.15.0 | PostgreSQL operations |
| `data` | pandas≥1.1.0, numpy≥1.17.0 | Data processing |
| `web` | seleniumbase≥3.0.0, selenium≥3.141.0 | Browser automation |
| `vision` | opencv-python≥4.1.0, matplotlib≥3.1.0, pyautogui≥0.9.48, mss≥4.0.0 | Screen interaction |
| `jupyter` | ipython≥6.0.0 | Notebook integration |

All versions are set to compatible minimums to avoid conflicts in existing environments.

## Configuration

### Database Setup

qufe supports multiple database configuration methods:

1. **`.env` file (Recommended)**: Works consistently across all environments
2. **Environment variables**: System-level configuration  
3. **Direct parameters**: Programmatic configuration

The `.env` approach is recommended because it:
- Works in Jupyter Lab, PyCharm, terminal, and other environments
- Keeps credentials separate from code
- Doesn't require system-level configuration
- Can be easily excluded from version control

### Web Automation Setup

Browser automation requires WebDriver installation:
- **Firefox**: Usually works out of the box (GeckoDriver auto-download)

## Migration from v0.3.0

If upgrading from previous versions:

1. **Check for import errors**:
   ```python
   import qufe
   qufe.help()  # See what's missing
   ```

2. **Install specific features**:
   ```bash
   pip install qufe[database,data]  # Only what you need
   ```

## Documentation
- **Online docs**: https://qufe.readthedocs.io
- **Local help**: Use `help()` functions in each module

## License

MIT License

## Security & Ethics Guidelines

### Database Security
- Store credentials in `.env` files, never in source code
- Add `.env` to `.gitignore` to prevent credential leaks
- Use environment variables in production environments
- Consider using database connection pooling for production

### Responsible Usage
When using automation and web interaction features, we encourage:
- Respecting website terms of service and limits
- Being mindful of server resources and privacy considerations
- Following ethical practices in data collection and automation

These are personal choices, but we believe technology works best when used responsibly.

## Support and Troubleshooting

### Common Issues

**ImportError on module load:**
```python
# Check what's available
import qufe
qufe.check_dependencies()

# Install missing features
pip install qufe[database]  # or other feature groups
```

**Database connection issues:**
```python
# Check configuration
from qufe.dbhandler import help
help()  # Shows configuration options
```

**Browser automation problems:**
```python
# Check WebDriver status
from qufe.wbhandler import help  
help()  # Shows WebDriver requirements
```

### Getting Help

1. **Check module help**: Call `help()` on any module
2. **GitHub Issues**: https://github.com/qufe/qufe/issues
3. **Documentation**: https://qufe.readthedocs.io

## Changelog

### v0.4.0 (Current)
- **Breaking Change**: Moved to optional dependencies architecture
- **Breaking Change**: Python 3.10+ requirement
- Added modular installation with feature groups
- Enhanced error messages with installation guidance  
- Added comprehensive help() functions
- Improved graceful degradation when dependencies missing

### v0.3.1 (Previous)
- All dependencies were required
- Python 3.8+ support
- Monolithic installation
