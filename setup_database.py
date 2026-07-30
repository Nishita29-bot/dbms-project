"""Create the Foodie Express database tables and load sample data.

Run this after MySQL/Docker is started:
    python setup_database.py
"""
from pathlib import Path
import mysql.connector
from mysql.connector import Error
from config import Config


PROJECT_FOLDER = Path(__file__).parent


def run_sql_file(connection, filename):
    """Run the simple SQL statements stored in one project SQL file."""
    sql_text = (PROJECT_FOLDER / 'database' / filename).read_text(encoding='utf-8')
    cursor = connection.cursor()

    # The supplied SQL files have simple statements with semicolon separators.
    for statement in sql_text.split(';'):
        if statement.strip():
            cursor.execute(statement)

    connection.commit()
    cursor.close()


def main():
    try:
        # Connect without selecting a database so schema.sql can create it if needed.
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        print('Connected to MySQL successfully.')
        run_sql_file(connection, 'schema.sql')

        cursor = connection.cursor()
        cursor.execute('USE food_delivery')
        cursor.execute('SELECT COUNT(*) FROM foods')
        food_count = cursor.fetchone()[0]
        cursor.close()

        # Keep the script repeatable: sample foods are only loaded into an empty menu.
        if food_count == 0:
            run_sql_file(connection, 'sample_data.sql')
            print('Sample users and food items loaded.')
        else:
            print('Existing menu found; sample data was not duplicated.')

        cursor = connection.cursor()
        cursor.execute('SHOW TABLES')
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        connection.close()

        print('Database setup complete.')
        print('Available tables:', ', '.join(tables))
    except Error as error:
        print(f'Database setup failed: {error}')
        print('Check that MySQL is running and that config.py has the correct host, port, user, and password.')


if __name__ == '__main__':
    main()
