# Bizflow DB Helper

A comprehensive database helper library for Oracle, SQL Server, and PostgreSQL with support for data import/export operations using pandas DataFrames.

## Features

- **Multi-database support**: Oracle, SQL Server, and PostgreSQL
- **Pandas integration**: Easy data import/export with pandas DataFrames
- **Secure connections**: Proper URL encoding for passwords with special characters
- **Type handling**: Automatic data type conversion and validation
- **Bulk operations**: Efficient data loading with chunking support
- **Schema support**: Full schema-aware operations

## Installation

```bash
pip install bizflow-db-helper
```

## Quick Start

```python
from bizflow_db_helper import DBHelper

# Initialize database connection
db = DBHelper(
    user="your_username",
    password="your_password@with_special_chars",  # Now handles special characters!
    host="localhost",
    port=1521,
    db_name="your_database",
    schema="your_schema",
    db_type="oracle"  # or "sql_server" or "postgresql"
)

# Write DataFrame to database
import pandas as pd
df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
db.to_sql(df, 'your_table', if_exists='replace')

# Read data (using standard pandas/SQLAlchemy)
df_result = pd.read_sql("SELECT * FROM your_table", db.engine)
```

## Supported Database Types

- **Oracle**: Uses `oracledb` driver with thick client support
- **SQL Server**: Uses `pyodbc` with ODBC Driver 17
- **PostgreSQL**: Uses standard PostgreSQL driver

## What's New in v2.0.0

- **Fixed password encoding**: Passwords containing '@' and other special characters now work correctly
- **Improved URL handling**: Uses SQLAlchemy's `URL.create()` for robust connection string generation
- **Enhanced security**: Better handling of credentials in connection URLs

## Requirements

- Python >=3.8
- pandas >=1.3.0
- sqlalchemy >=1.4.0
- oracledb >=1.0.0
- numpy >=1.20.0
- bcpy >=0.1.0 (for SQL Server bulk operations)

## License

MIT License

## Contributing

Issues and pull requests are welcome on [GitHub](https://github.com/littlekeixi/dbhelper).
