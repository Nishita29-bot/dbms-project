# Foodie Express — Online Food Delivery

A simple, beginner-friendly online food delivery application for a college DBMS mini project. It models one restaurant where customers browse food, use a cart, and place orders; an administrator manages foods and order status.

## Objectives

- Demonstrate Python Flask with MySQL using raw SQL queries.
- Practice database relationships, CRUD, sessions, forms, and Jinja templates.
- Keep the code readable and easy to run locally.

## Features

**Customer:** registration, login/logout, menu search, food details, cart quantity updates, checkout, order history, and profile update.

**Admin:** separate login, dashboard, food CRUD, customer list, order list, and status updates (Pending, Preparing, Delivered).

## Technology Stack

- Python 3, Flask, Jinja2
- MySQL 8 and mysql-connector-python
- HTML5, CSS3, vanilla JavaScript
- Docker Compose (for MySQL only)

## Software Requirements

Python 3.10+, Docker Desktop (recommended), and a browser. MySQL can be installed locally instead of Docker.

## Installation and Database Setup

1. Open a terminal in this project folder.
2. Start MySQL and let it import the SQL files automatically:

   ```bash
   docker compose up -d
   ```

   The first start creates `food_delivery`, its tables, two users, and 10 foods. To re-import after changing SQL, run `docker compose down -v` then start again. This removes only the Docker database volume.

3. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

4. Install dependencies and run the app:

   ```bash
   pip install -r requirements.txt
   python setup_database.py
   python app.py
   ```

5. Visit `http://127.0.0.1:5000`.

`python setup_database.py` is safe to run whenever the tables are missing. It tests the MySQL connection, creates the database/tables if needed, loads the sample data, and prints the tables it finds. For a locally installed MySQL server, set `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE` environment variables if they differ from the defaults. Defaults are `localhost`, `3306`, `root`, `root`, and `food_delivery`.

## Sample Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@example.com | admin123 |
| Customer | customer@example.com | customer123 |

## Folder Structure

```text
app.py                 Flask routes and SQL queries
config.py              Database configuration
database/              schema.sql and sample_data.sql
templates/             Public/customer Jinja pages
templates/admin/       Admin Jinja pages
static/css/style.css   Responsive styling
static/js/script.js    Search, navigation, confirmations
docker-compose.yml     MySQL container setup
```

## ER Diagram

```text
USERS (1) ──< CART >── (1) FOODS
  |
  └──< ORDERS (1) ──< ORDER_ITEMS >── (1) FOODS
```

## Database Schema

`users(id, full_name, email, phone, password, role)`

`foods(id, name, description, category, price, image)`

`cart(id, user_id, food_id, quantity)`

`orders(id, user_id, total_amount, order_date, status)`

`order_items(id, order_id, food_id, quantity, price)`

Foreign keys connect cart items to users/foods, orders to users, and order items to orders/foods. See `database/schema.sql` for the complete definitions.

## Application Workflow

1. Customer registers or logs in.
2. Customer searches the menu and adds food to the cart.
3. At checkout, the app creates an order and order-item records, then clears the cart.
4. Admin views orders and changes the status.
5. Customer views the updated status in My Orders.

## Screenshots

Add screenshots here after running the application:

- Home page
- Menu and cart
- Checkout/order history
- Admin dashboard

## Future Improvements

- Hash passwords before saving them.
- Add image uploads and payment integration.
- Add order detail pages, delivery addresses, and pagination.
- Add server-side CSRF protection.

## Troubleshooting

- **Cannot connect to MySQL:** ensure Docker is running and wait a few seconds after `docker compose up -d`.
- **Access denied:** check the password in `config.py` matches `docker-compose.yml`.
- **Port 3306 already used:** change `3306:3306` in `docker-compose.yml` (for example `3307:3306`) and set `MYSQL_PORT=3307` before running Flask.
- **Tables missing:** run the schema and sample SQL files manually, or recreate the Docker database volume as described above.

## License

For educational use as a college mini project.

## Author

Your Name Here

## References

- Flask documentation: https://flask.palletsprojects.com/
- MySQL documentation: https://dev.mysql.com/doc/
- mysql-connector-python documentation: https://dev.mysql.com/doc/connector-python/en/
