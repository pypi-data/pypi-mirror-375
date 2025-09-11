import oracledb
import pandas as pd
import bcpy
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from numpy import int64
import sqlalchemy
import time
import csv
from io import StringIO

__all__ = ['DBHelper']

class DBHelper:
    def __init__(self, user, password, host, port, db_name, schema, db_type):
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self.db_name = db_name
        self.schema = schema
        self.db_type = db_type.lower()
        self.engine = self.__create_sql_engine()
        try:
            self.connection = self.engine.connect()
        except Exception as e:
            print(f"Error connecting to {self.db_type.capitalize()} Database: {e}")
            print("You might not access to the database. Please check your connection details.")
            pass
        self.sql_config = self.__initialize_sql_config()

    @property
    def user(self):
        raise AttributeError("Access to user attribute is not allowed")

    @property
    def password(self):
        raise AttributeError("Access to password attribute is not allowed")

    @property
    def host(self):
        raise AttributeError("Access to host attribute is not allowed")

    @property
    def port(self):
        raise AttributeError("Access to port attribute is not allowed")

    def __create_sql_engine(self):
        """
        Creates and returns a SQLAlchemy engine for the specified database type.
        
        Returns:
            A SQLAlchemy engine object.
        
        Raises:
            ValueError: If db_type is not one of the supported types.
            Exception: If there's an error establishing the connection.
        """
        try:
            if self.db_type == "oracle":
                self.__init_oracle_client()
                url = URL.create(
                    drivername='oracle+oracledb',
                    username=self._user,
                    password=self._password,
                    host=self._host,
                    port=self._port,
                    database=self.db_name
                )
                return create_engine(url)
            elif self.db_type == "sql_server":
                url = URL.create(
                    drivername='mssql+pyodbc',
                    username=self._user,
                    password=self._password,
                    host=self._host,
                    port=self._port,
                    database=self.db_name,
                    query={'driver': 'ODBC Driver 17 for SQL Server'}
                )
                return create_engine(url)
            elif self.db_type == "postgresql":
                url = URL.create(
                    drivername='postgresql',
                    username=self._user,
                    password=self._password,
                    host=self._host,
                    port=self._port,
                    database=self.db_name
                )
                return create_engine(url)
            else:
                raise ValueError("Unsupported database type. Please use 'oracle', 'sql_server', 'postgresql'")
        except Exception as e:
            print(f"Error connecting to {self.db_type.capitalize()} Database: {e}")
            raise

    @staticmethod
    def __init_oracle_client():
        """
        Initialize the Oracle client for thick mode.
        This function should be called before attempting to connect to an Oracle database.
        """
        try:
            oracledb.init_oracle_client()
            print("Oracle Client initialized successfully.")
        except Exception as e:
            print(f"Error initializing Oracle Client: {e}")
            pass

    def __initialize_sql_config(self):
        return {
            'server': self._host,
            'database': self.db_name,
            'username': self._user,
            'password': self._password
        }

    def __get_columns_types(self, table_name):
        """
        Get column types for a given table.
        
        Parameters:
        -----------
        table_name : str
            Name of the SQL table.
        
        Returns:
        --------
        dict
            A dictionary mapping column names to their types (datetime, float, int64, or str).
        """
        query = ""
        if self.db_type == "sql_server":
            query = f"""
            SELECT 
                c.name AS column_name,
                t.name AS data_type
            FROM 
                sys.columns c
            INNER JOIN 
                sys.types t ON c.user_type_id = t.user_type_id
            WHERE 
                c.object_id = OBJECT_ID('{table_name}')
            """
        elif self.db_type == "oracle":
            query = f"""
            SELECT 
                column_name,
                data_type
            FROM 
                all_tab_columns
            WHERE 
                table_name = '{table_name.upper()}'
            """
        elif self.db_type == "postgresql":
            query = f"""
            SELECT 
                column_name,
                data_type
            FROM 
                information_schema.columns
            WHERE 
                table_name = '{table_name}'
                and
                table_schema = '{self.schema}'
            """
        elif self.db_type == "sqlite":
            query = f"PRAGMA table_info('{table_name}')"
        
        df_types = {}
        with self.engine.connect() as connection:
            result = connection.execute(text(query))
            for row in result:
                column_name = row[0] if self.db_type != "sqlite" else row[1]
                data_type = row[1].lower() if self.db_type != "sqlite" else row[2].lower()
                
                if any(datetime_type in data_type for datetime_type in ['date', 'time', 'timestamp']):
                    df_types[column_name] = datetime
                elif any(float_type in data_type for float_type in ['float', 'double', 'decimal', 'numeric', 'real']):
                    df_types[column_name] = float
                elif any(int_type in data_type for int_type in ['int', 'bigint', 'smallint', 'tinyint']):
                    df_types[column_name] = int64
                else:
                    df_types[column_name] = str
        
        return df_types

    def __is_datetime(self, col):
        return pd.api.types.is_datetime64_any_dtype(col) or pd.api.types.is_datetime64_ns_dtype(col)

    def __check_data_to_table(self, df, table_name):
        # Get column types from the database
        db_types = self.__get_columns_types(table_name)
        # Create case-insensitive mappings
        df_columns_lower = {col.lower(): col for col in df.columns}
        db_columns_lower = {col.lower(): col for col in db_types.keys()}
     
        # Compare columns case-insensitively
        df_columns_set = set(df_columns_lower.keys())
        db_columns_set = set(db_columns_lower.keys())
        
        if df_columns_set != db_columns_set:
            print('Columns present in the uploaded file but not in the database:', [df_columns_lower[col] for col in df_columns_set - db_columns_set])
            print('Columns present in the database but not in the uploaded file:', [db_columns_lower[col] for col in db_columns_set - df_columns_set])
            raise ValueError("Column names do not match. Please recheck and try again")
        
        errors = []

        for col_lower in df_columns_set:
            df_col = df_columns_lower[col_lower]
            db_col = db_columns_lower[col_lower]
            expected_type = db_types[db_col]
            
            if expected_type == datetime:
                try:
                    df[df_col] = pd.to_datetime(df[df_col])
                except Exception as e:
                    errors.append({df_col:'datetime'})
            elif expected_type == float:
                try:
                    df[df_col] = df[df_col].astype(float)
                except Exception as e:
                    errors.append({df_col:'numeric'})
            elif expected_type == int64:
                try:
                    df[df_col] = df[df_col].astype(int64)
                except Exception as e:
                    errors.append({df_col:'integer'})
            else:
                try:
                    df[df_col] = df[df_col].astype(str).apply(lambda x: x.replace('"', "'").replace('\r', ' ').replace(',', ' '))
                except Exception as e:
                    errors.append({df_col:'string'})
        
        if errors:
            raise ValueError("Cannot convert columns: ", errors)
        
        return df


    def __psql_insert_copy(self, table, conn, keys, data_iter):
        """
        Execute SQL statement inserting data

        Parameters
        ----------
        table : pandas.io.sql.SQLTable
        conn : sqlalchemy.engine.Engine or sqlalchemy.engine.Connection
        keys : list of str
            Column names
        data_iter : Iterable that iterates the values to be inserted
        """
        # gets a DBAPI connection that can provide a cursor
        dbapi_conn = conn.connection
        with dbapi_conn.cursor() as cur:
            s_buf = StringIO()
            writer = csv.writer(s_buf)
            writer.writerows(data_iter)
            s_buf.seek(0)

            columns = ', '.join('"{}"'.format(k) for k in keys)
            if table.schema:
                table_name = '{}.{}'.format(table.schema, table.name)
            else:
                table_name = table.name

            sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
                table_name, columns)
            cur.copy_expert(sql=sql, file=s_buf)

    def __write_sql_table(self, df, tb_name, if_exists='append'):
        start_time = time.time()
        if self.db_type == 'sql_server':
            bdf = bcpy.DataFrame(df)
            sql_table = bcpy.SqlTable(self.sql_config, table=tb_name, use_existing_sql_table=(if_exists == 'append'))
            try:
                bdf.to_sql(sql_table, use_existing_sql_table=True)
            except Exception as e:
                print(f"Error writing to sql table")
                print(e)
        elif self.db_type == 'oracle':
            df.to_sql(name=tb_name, con=self.connection, if_exists=if_exists, index=False, dtype=self.dtyp, chunksize = 10000, schema = self.schema)
        elif self.db_type == 'postgresql':
            df.to_sql(name=tb_name, con=self.connection, if_exists=if_exists, index=False, method=self.__psql_insert_copy, schema=self.schema)
        else:
            try:
                df.to_sql(tb_name, con=self.connection, if_exists=if_exists, index=False, schema = self.schema)
            except Exception as e:
                print(f"Error writing to sql table")
                pass
        self.connection.commit()
        print(f"Time taken to write to {self.db_type} in seconds: {time.time() - start_time}")

    def __convert_dataframe_types(self, df):
        """
        Convert dataframe columns to datetime, float, int64, and str types.
        Boolean columns are converted to int64.
        
        Parameters:
        -----------
        df : DataFrame
            The DataFrame to be converted.
        
        Returns:
        --------
        DataFrame
            The converted DataFrame.
        """
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = pd.to_datetime(df[col])
            elif pd.api.types.is_float_dtype(df[col]):
                df[col] = df[col].astype(float)
            elif pd.api.types.is_integer_dtype(df[col]):
                df[col] = df[col].astype(int64)
            elif pd.api.types.is_bool_dtype(df[col]):
                df[col] = df[col].astype(int64)
            else:
                df[col] = df[col].astype(str)
        return df

    def drop_table_if_exists(self, table_name):
        """
        Drop the specified table if it exists in the database.

        Parameters:
        -----------
        table_name : str
            Name of the SQL table to drop.
        """
        if self.db_type == 'oracle':
            drop_query = f"""
            BEGIN
                EXECUTE IMMEDIATE 'DROP TABLE ' || UPPER('{table_name}');
            EXCEPTION
                WHEN OTHERS THEN
                    IF SQLCODE != -942 THEN
                        RAISE;
                    END IF;
            END;
            """
        elif self.db_type == 'sql_server':
            drop_query = f"""
            IF OBJECT_ID('{table_name}', 'U') IS NOT NULL
                DROP TABLE {table_name};
            """
        elif self.db_type == 'postgresql':
            drop_query = f"""
            DROP TABLE IF EXISTS {self.schema}.{table_name};
            """
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

        try:
            self.connection.execute(text(drop_query))
            self.connection.commit()
        except Exception as e:
            print(f"Error dropping table '{table_name}': {e}")

    def to_sql(self, df, table_name, if_exists='fail', index=False, **kwargs):
        """
        Write records stored in a DataFrame to a SQL database.
        
        Parameters:
        -----------
        df : DataFrame
            The DataFrame to be written to the database.
        table_name : str
            Name of the SQL table.
        if_exists : {'fail', 'replace', 'append'}, default 'fail'
            How to behave if the table already exists.
        index : bool, default False
            Write DataFrame index as a column.
        **kwargs : dict
            Additional keyword arguments to be passed to the underlying write_sql_table function.
        """
        if if_exists not in ('fail', 'replace', 'append'):
            raise ValueError("if_exists must be one of 'fail', 'replace', or 'append'")
        
        # Handle the 'replace' case for all supported database types
        if if_exists == 'replace':
            self.drop_table_if_exists(table_name)
            if_exists = 'append'

        # Convert dataframe types
        df = self.__convert_dataframe_types(df)
        self.dtyp = {}
        for column in df.columns:
            if df[column].dtype == 'object':
                self.dtyp[column] = sqlalchemy.types.VARCHAR(df[column].astype(str).str.len().max())
            elif df[column].dtype in ['float', 'float64']:
                self.dtyp[column] = sqlalchemy.FLOAT        
        # Write header of dataframe to sql table
        df.head(0).to_sql(table_name, con=self.engine, if_exists=if_exists, index=False, dtype = self.dtyp, schema = self.schema)

        # Check and prepare the data
        df = self.__check_data_to_table(df, table_name)
        #print(df.to_csv('check.csv'))
        #print("df after covert", df.dtypes)
        # Write to SQL table
        self.__write_sql_table(df, table_name, if_exists)

    def __del__(self):
        if hasattr(self, 'engine'):
            self.engine.dispose()
