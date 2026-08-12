"""Create the Foodie Express database tables and load sample data.

Run this after MySQL/Docker is started:
    python setup_database.py
"""
from pathlib import Path
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
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


def migrate_existing_database(connection):
    """Add delivery columns and hash old plain-text passwords for existing projects."""
    cursor = connection.cursor(dictionary=True)
    cursor.execute("ALTER TABLE users MODIFY role ENUM('customer', 'admin', 'delivery_person') NOT NULL DEFAULT 'customer'")
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='food_delivery' AND TABLE_NAME='orders'")
    columns = {row['COLUMN_NAME'] for row in cursor.fetchall()}
    if 'delivery_person_id' not in columns:
        cursor.execute('ALTER TABLE orders ADD COLUMN delivery_person_id INT NULL')
    if 'delivery_status' not in columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN delivery_status ENUM('Not Assigned', 'Assigned', 'Out for Delivery', 'Delivered') NOT NULL DEFAULT 'Not Assigned'")

    cursor.execute("SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA='food_delivery' AND TABLE_NAME='orders' AND CONSTRAINT_NAME='fk_orders_delivery_person'")
    if not cursor.fetchone():
        cursor.execute('ALTER TABLE orders ADD CONSTRAINT fk_orders_delivery_person FOREIGN KEY (delivery_person_id) REFERENCES users(id) ON DELETE SET NULL')

    cursor.execute('SELECT id, password FROM users')
    users = cursor.fetchall()
    for user in users:
        value = user['password']
        if not value.startswith(('scrypt:', 'pbkdf2:', 'sha256$')):
            cursor.execute('UPDATE users SET password=%s WHERE id=%s', (generate_password_hash(value), user['id']))

    cursor.execute("SELECT id FROM users WHERE email='rider@example.com'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (full_name, email, phone, password, role) VALUES (%s, %s, %s, %s, 'delivery_person')", ('Sample Rider', 'rider@example.com', '9822222222', generate_password_hash('rider123')))
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
        migrate_existing_database(connection)

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
