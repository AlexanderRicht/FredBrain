import mysql.connector
import pandas as pd
from mysql.connector import Error
import time


class MySQLBrain:
    def __init__(self, host, user, passwd, db_name=None, ssl_verify_identity=None, ssl_ca=None):
        """
        Initializes a new instance of the SQLBrain class.

        Parameters:
        - host (str): The hostname or IP address of the MySQL server.
        - user (str): The username used to authenticate with the MySQL server.
        - passwd (str): The password used to authenticate with the MySQL server.
        - db_name (str, optional): The name of the database to connect to. If not specified,
          the connection will be established without selecting a database. From there, you can
          use the create or view database functions

        The constructor establishes a connection to the MySQL server and initializes a cursor
        for executing database operations. If a database name is provided, the connection
        will be set to use that specific database.
        """
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db_name = db_name
        self.ssl_verify_identity = ssl_verify_identity
        self.ssl_ca = ssl_ca
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """
        Establishes a connection to the MySQL database server and initializes a cursor.

        This method attempts to connect to the MySQL server using the credentials and
        details provided during class initialization. If a database name was specified,
        the connection will automatically select that database. On successful connection,
        a cursor object is created for executing SQL commands.

        Raises:
        - Prints an error message if the connection to the MySQL server fails.
        """
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                database=self.db_name,
                ssl_verify_identity=self.ssl_verify_identity,
                ssl_ca=self.ssl_ca
            )
            if self.conn.is_connected():
                self.cursor = self.conn.cursor()
                print("MySQL database connection successful.")
        except Error as e:
            print(f"Database connection failed: {e}")

    def list_databases(self):
        """
          Retrieves and prints a list of all databases available on the connected MySQL server.

          This method executes the "SHOW DATABASES" SQL command to fetch a list of all databases
          from the MySQL server. Each database name is then printed to the console. This function
          can be used to verify the available databases and ensure that the required database
          exists on the server before attempting operations like table creation or data insertion.

          Usage:
          After creating an instance of the SQLBrain class and establishing a connection to the
          MySQL server, call this method to list all databases.

              db_manager = SQLBrain(host="localhost", user="your_username", passwd="your_password")
              db_manager.list_databases()

          Output:
          The method prints the names of all databases on the MySQL server, one per line, prefixed
          with "List of databases:".

          Error Handling:
          - If there's an issue executing the "SHOW DATABASES" command, such as a connection error
            or if the cursor is not initialized, an error message is printed detailing the failure.
          - The method catches and handles exceptions of type `mysql.connector.Error`, which are
            raised for errors related to MySQL operations.

          Note:
          This method does not return any value. It directly prints the database names to the console.
          For applications requiring programmatic access to the list of databases, you may consider
          modifying this method to return the list of database names instead of printing them.
          """
        try:
            self.cursor.execute("SHOW DATABASES")
            databases = self.cursor.fetchall()
            print("List of databases:")
            for db in databases:
                print(db[0])
        except Error as e:
            print(f"Failed to list databases: {e}")

    def check_create_database(self, db_name):
        """
        Checks if a specified database exists in the MySQL server, and creates it if it does not exist.

        Parameters:
        - db_name (str): The name of the database to check for existence and possibly create.

        This method first checks if the specified database exists by executing the "SHOW DATABASES LIKE"
        SQL command. If the database does not exist, it then creates the database using the "CREATE DATABASE"
        SQL command.

        Outputs:
        - Prints a message indicating whether the database already exists or has been created successfully.

        Exceptions:
        - Catches and prints any MySQL-related errors that occur during the execution of the method.

        Usage Example:
        db_manager.check_create_database('example_database')
        """
        try:
            self.cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
            result = self.cursor.fetchone()
            if result:
                print(f"Database already exists: {db_name}")
            else:
                self.cursor.execute(f"CREATE DATABASE {db_name}")
                print("Database created successfully.")
        except Error as e:
            print(f"Failed to check or create database: {e}")

    def list_tables(self):
        """
        Lists all tables in the currently selected database on the MySQL server.

        This method retrieves and prints the names of all tables within the currently selected database
        by executing the "SHOW TABLES" SQL command.

        Outputs:
        - Prints the list of table names, each on a new line, prefixed with "List of tables:".

        Exceptions:
        - Catches and prints any MySQL-related errors encountered while attempting to list the tables.

        Usage Example:
        db_manager.list_tables()
        """
        try:
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall(dictionary=True)
            print("List of tables:")
            for db in tables:
                print(db[0])
        except Error as e:
            print(f"Failed to list tables: {e}")

    def check_table_exists(self, table_name):
        """
        Checks if a specified table exists in the currently selected database.

        Parameters:
        - table_name (str): The name of the table to check for existence.

        Returns:
        - True if the table exists, False otherwise.

        This method executes the "SHOW TABLES LIKE" SQL command to check for the existence of a specific
        table. It returns a boolean value indicating the presence of the table.

        Outputs:
        - Prints a message indicating whether the table already exists or does not exist.

        Exceptions:
        - Catches and prints any MySQL-related errors encountered during the execution of the method.

        Usage Example:
        exists = db_manager.check_table_exists('example_table')
        """
        try:
            self.cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            result = self.cursor.fetchone()
            if result is not None:  # If result is not None (i.e., the table exists)
                print(f"Table already exists: {table_name}")
                return True
            else:
                print(f"Table does not exist: {table_name}")
                return False
        except Error as e:
            print(f"Failed to check table existence: {e}")
            return False

    def fred_insert_into_table(self, table_name, df):
        """
        Constructs and executes an INSERT INTO statement to batch insert data from a pandas DataFrame into
        a specified table.

        Parameters:
        - table_name (str): The name of the table into which the data will be inserted.
        - df (pandas.DataFrame): The DataFrame containing the data to insert.

        This method prepares an INSERT INTO SQL statement with placeholders for data values. It then
        executes this statement in batch mode for all rows in the provided DataFrame, inserting the data
        into the specified table.

        Outputs:
        - Prints a message indicating successful data insertion.

        Exceptions:
        - Catches and prints any MySQL-related errors encountered during data insertion, including issues
          with data types and SQL syntax.

        Usage Example:
        db_manager.fred_insert_into_table('example_table', dataframe)
        """
        # Convert DataFrame columns to a list of column names, wrapped in backticks
        column_names = ', '.join([f"`{column}`" for column in df.columns])
        # Create placeholders for the values
        placeholders = ', '.join(['%s' for _ in df.columns])
        sql_insert_statement = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"
        # Prepare data for insertion
        data_to_insert = [tuple(row) for row in df.values]
        try:
            # Use executemany to insert data in batches
            self.cursor.executemany(sql_insert_statement, data_to_insert)
            self.conn.commit()  # Commit the transaction
            print(f"Data inserted successfully into '{table_name}'.")
        except Error as e:
            print(f"Failed to insert data into table '{table_name}': {e}")

    def fred_create_table_sql(self, df, table_name):
        """
           Constructs and executes a CREATE TABLE SQL statement based on a pandas DataFrame structure and
           specified table name, then inserts the DataFrame data into the newly created table using the
           fred_insert_into_table method.

           Parameters:
           - df (pandas.DataFrame): The DataFrame based on which the table structure is determined.
           - table_name (str): The name of the table to create.

           This method first analyzes the data types of the DataFrame's columns to construct a corresponding
           CREATE TABLE SQL statement. It then attempts to create the table in the currently selected database
           if it does not already exist. If the table creation is successful or if the table already exists, it
           proceeds to insert the DataFrame data into the table using the fred_insert_into_table method.

           Outputs:
           - Prints the SQL data types determined for each column and a message indicating whether the table
             was created successfully or already exists.
           - If the table is created successfully or already exists, it attempts to insert the DataFrame data
             into the table and prints a message indicating the success or failure of data insertion.

           Exceptions:
           - Catches and prints any MySQL-related errors encountered during the table creation or data insertion
             process, including issues with SQL syntax or data types compatibility.

           Usage Example:
           db_manager.fred_create_table_sql(dataframe, 'example_table')

           Note:
           This method combines table creation and data insertion into a single operation. If the table
           does not exist, it will be created based on the structure of the provided DataFrame, and then
           the data from the DataFrame will be inserted into the new table. This ensures that the database
           schema matches the structure of the DataFrame, facilitating seamless data storage.
        """
        df_datatype = df.dtypes
        columns_with_types = [
            "`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY",
            "`sql_upload_datetime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
        ]
        columns_with_headers = []
        for index, value in df_datatype.items():
            if str(value).startswith('int'):
                sqldtype = 'INT'
            elif str(value).startswith('float'):
                sqldtype = 'FLOAT'
            elif str(value).startswith('bool'):
                sqldtype = 'BOOLEAN'
            elif str(value).startswith('datetime'):
                sqldtype = 'DATETIME'
            elif str(value).startswith('date'):
                sqldtype = 'DATE'
            else:
                sqldtype = 'VARCHAR(250)'
            columns_with_types.append(f"`{index}` {sqldtype}")
            columns_with_headers.append(f"{index}")
        columns_type_sql = ', '.join(columns_with_types)
        if self.check_table_exists(table_name) is False:
            print(f"SQL Statement:\nCREATE TABLE IF NOT EXISTS `{table_name}` ({columns_type_sql})")
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns_type_sql})")
            print(f"Table '{table_name}' created successfully.")
            self.fred_insert_into_table(table_name, df)
        else:
            print(f"Table '{table_name}' already exists.")

    def insert_new_rows(self, df, table_name):
        """
          Inserts new rows into a specified table in the MySQL database, avoiding duplicates.

          This method performs an incremental load by appending new rows from the provided pandas DataFrame to the
          specified table. It first retrieves existing data from the table to identify rows in the DataFrame that are
          not already present. Only unique new rows, identified by a 'hash_key' column in the DataFrame, are
          inserted into the table, ensuring no duplicates are added.

          Parameters:
          - table_name (str): The name of the table into which the new rows will be inserted.
          - df (pandas.DataFrame): A DataFrame containing the new rows to insert. The DataFrame must include a 'hash_key'
            column, which serves as a unique identifier for each row. This 'hash_key' should be generated using a
            consistent hashing method to ensure uniqueness.

          Outputs:
          - Console output indicating the success of the operation, including the number of rows inserted.

          Exceptions:
          - Prints any MySQL-related errors encountered during the operation.

          Usage Example:
          - db_manager.insert_new_rows('example_table', new_rows_dataframe)

          Note:
          - The 'hash_key' column in the DataFrame is crucial for identifying unique rows. This unique identifier should
            be generated using the method described in 'transform_series', combining specific row data into a SHA-256 hash.
            The presence of this column ensures that the method can effectively prevent duplicate entries in the database
            by performing an incremental load.
          """
        column_names = ', '.join([f"`{column}`" for column in df.columns])
        existing_data_query = f"SELECT {column_names} FROM `{table_name}`"
        print(f"SQL Statement - Retrieve Existing Data:\n{existing_data_query}")
        self.cursor.execute(existing_data_query)
        existing_rows = self.cursor.fetchall()
        existing_df = pd.DataFrame(existing_rows, columns=df.columns.to_list())
        print(existing_df)
        time.sleep(5)
        unique_to_insert = (
            df
            .merge(existing_df[['Unique Key']], on="Unique Key", how='left', indicator=True)
            .loc[lambda x: x['_merge'] == 'left_only']
        )
        unique_to_insert = unique_to_insert.drop(columns=['_merge'])

        column_names = ', '.join([f"`{column}`" for column in unique_to_insert.columns])
        placeholders = ', '.join(['%s' for _ in unique_to_insert.columns])
        sql_insert_statement = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"
        print(f"SQL Statement - Insert New Rows:\n{sql_insert_statement}")
        if not unique_to_insert.empty:
            data_to_insert = [tuple(row) for row in unique_to_insert.values]
            row_count = len(data_to_insert)
            self.cursor.executemany(sql_insert_statement, data_to_insert)
            self.conn.commit()
            print(f"{row_count} rows inserted successfully into '{table_name}'.")
        else:
            print("No new unique rows to insert.")

    def close_connection(self):
        """
        Closes the connection to the MySQL server.

        This method closes the cursor and connection to the MySQL server, releasing any resources
        associated with the connection. It should be called when the database operations are complete
        to ensure that the connection is properly closed.

        Usage Example:
        db_manager.close_connection()
        """
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("MySQL database connection closed.")
        else:
            print("No active MySQL database connection to close.")
