from functools import wraps
import mysql.connector
from mysql.connector import Error
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


def db_connection():
    """Open one simple MySQL connection for a route."""
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'], port=app.config['MYSQL_PORT'],
        user=app.config['MYSQL_USER'], password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE']
)


def customer_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get('role') != 'customer':
            flash('Please log in as a customer first.', 'error')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Please log in as an admin first.', 'error')
            return redirect(url_for('admin_login'))
        return view(*args, **kwargs)
    return wrapped


def delivery_required(view):
    """Allow access only to logged-in delivery personnel."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get('role') != 'delivery_person':
            flash('Please log in as delivery personnel first.', 'error')
            return redirect(url_for('delivery_login'))
        return view(*args, **kwargs)
    return wrapped


def password_matches(stored_password, entered_password):
    """Verify stored hashes; supports the SHA-256 hashes in sample_data.sql."""
    if stored_password.startswith('sha256$'):
        return stored_password[7:] == hashlib.sha256(entered_password.encode()).hexdigest()
    return check_password_hash(stored_password, entered_password)


def query(sql, values=(), one=False):
    """Run a SELECT query and return dictionary rows."""
    conn = db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, values)
    result = cur.fetchone() if one else cur.fetchall()
    cur.close(); conn.close()
    return result


@app.route('/')
def index():
    foods = query('SELECT * FROM foods ORDER BY id DESC LIMIT 6')
    return render_template('index.html', foods=foods)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name, email = request.form.get('full_name', '').strip(), request.form.get('email', '').strip().lower()
        phone, password = request.form.get('phone', '').strip(), request.form.get('password', '')
        hashed_password = generate_password_hash(password)
        if not all([name, email, phone, password]):
            flash('Please complete every field.', 'error')
        else:
            try:
                conn = db_connection(); cur = conn.cursor()
                cur.execute('INSERT INTO users (full_name,email,phone,password) VALUES (%s,%s,%s,%s)', (name,email,phone,hashed_password))
                conn.commit(); cur.close(); conn.close()
                flash('Registration successful. Please log in.', 'success')
                return redirect(url_for('login'))
            except Error as err:
                flash('Email already exists or database error occurred.', 'error')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')
        user=query("SELECT * FROM users WHERE email=%s AND role='customer'",(email,),one=True)
        if user and password_matches(user['password'], password):
            session.update(user_id=user['id'], user_name=user['full_name'], role='customer')
            return redirect(url_for('dashboard'))
        flash('Invalid customer email or password.', 'error')
    return render_template('login.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')
        user=query("SELECT * FROM users WHERE email=%s AND role='admin'",(email,),one=True)
        if user and password_matches(user['password'], password):
            session.update(user_id=user['id'], user_name=user['full_name'], role='admin')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin email or password.', 'error')
    return render_template('admin_login.html')


@app.route('/delivery/login', methods=['GET', 'POST'])
def delivery_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password', '')
        user = query("SELECT * FROM users WHERE email=%s AND role='delivery_person'", (email,), one=True)
        if user and password_matches(user['password'], password):
            session.update(user_id=user['id'], user_name=user['full_name'], role='delivery_person')
            return redirect(url_for('delivery_dashboard'))
        flash('Invalid delivery personnel email or password.', 'error')
    return render_template('delivery_login.html')


@app.route('/logout')
def logout():
    session.clear(); flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
@customer_required
def dashboard():
    foods = query('SELECT * FROM foods ORDER BY id DESC LIMIT 4')
    order_count = query('SELECT COUNT(*) AS count FROM orders WHERE user_id=%s', (session['user_id'],), one=True)['count']
    return render_template('dashboard.html', foods=foods, order_count=order_count)


@app.route('/menu')
def menu():
    foods = query('SELECT * FROM foods ORDER BY category, name')
    return render_template('menu.html', foods=foods)


@app.route('/food/<int:food_id>')
def food_details(food_id):
    food = query('SELECT * FROM foods WHERE id=%s', (food_id,), one=True)
    if not food: return render_template('404.html'), 404
    return render_template('food_details.html', food=food)


@app.route('/cart/add/<int:food_id>', methods=['POST'])
@customer_required
def add_cart(food_id):
    try:
        conn=db_connection(); cur=conn.cursor()
        cur.execute('INSERT INTO cart (user_id, food_id, quantity) VALUES (%s,%s,1) ON DUPLICATE KEY UPDATE quantity=quantity+1', (session['user_id'], food_id))
        conn.commit(); cur.close(); conn.close(); flash('Item added to your cart.', 'success')
    except Error: flash('Could not add item to cart.', 'error')
    return redirect(request.referrer or url_for('menu'))


@app.route('/cart')
@customer_required
def cart():
    items = query('SELECT cart.*, foods.name, foods.price, foods.image FROM cart JOIN foods ON cart.food_id=foods.id WHERE user_id=%s', (session['user_id'],))
    total = sum(item['price'] * item['quantity'] for item in items)
    return render_template('cart.html', items=items, total=total)


@app.route('/cart/update/<int:cart_id>', methods=['POST'])
@customer_required
def update_cart(cart_id):
    quantity = max(1, int(request.form.get('quantity', 1)))
    conn=db_connection(); cur=conn.cursor(); cur.execute('UPDATE cart SET quantity=%s WHERE id=%s AND user_id=%s', (quantity,cart_id,session['user_id'])); conn.commit(); cur.close(); conn.close()
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:cart_id>', methods=['POST'])
@customer_required
def remove_cart(cart_id):
    conn=db_connection(); cur=conn.cursor(); cur.execute('DELETE FROM cart WHERE id=%s AND user_id=%s', (cart_id,session['user_id'])); conn.commit(); cur.close(); conn.close(); flash('Item removed.', 'success')
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
@customer_required
def checkout():
    items = query('SELECT cart.*, foods.name, foods.price FROM cart JOIN foods ON cart.food_id=foods.id WHERE user_id=%s', (session['user_id'],))
    total = sum(i['price'] * i['quantity'] for i in items)
    if not items:
        flash('Your cart is empty.', 'error'); return redirect(url_for('menu'))
    if request.method == 'POST':
        if not request.form.get('address', '').strip():
            flash('Please enter a delivery address.', 'error')
        else:
            conn=db_connection(); cur=conn.cursor()
            try:
                cur.execute('INSERT INTO orders (user_id,total_amount,status) VALUES (%s,%s,%s)', (session['user_id'], total, 'Pending'))
                order_id=cur.lastrowid
                for item in items:
                    cur.execute('INSERT INTO order_items (order_id,food_id,quantity,price) VALUES (%s,%s,%s,%s)', (order_id,item['food_id'],item['quantity'],item['price']))
                cur.execute('DELETE FROM cart WHERE user_id=%s', (session['user_id'],)); conn.commit()
                flash(f'Order #{order_id} placed successfully!', 'success'); return redirect(url_for('orders'))
            except Error:
                conn.rollback(); flash('Could not place your order.', 'error')
            finally: cur.close(); conn.close()
    return render_template('checkout.html', items=items, total=total)


@app.route('/orders')
@customer_required
def orders():
    orders_list = query('SELECT * FROM orders WHERE user_id=%s ORDER BY order_date DESC', (session['user_id'],))
    return render_template('orders.html', orders=orders_list)


@app.route('/profile', methods=['GET', 'POST'])
@customer_required
def profile():
    user = query('SELECT * FROM users WHERE id=%s', (session['user_id'],), one=True)
    if request.method == 'POST':
        name, phone = request.form.get('full_name','').strip(), request.form.get('phone','').strip()
        if name and phone:
            conn=db_connection(); cur=conn.cursor(); cur.execute('UPDATE users SET full_name=%s, phone=%s WHERE id=%s', (name,phone,session['user_id'])); conn.commit(); cur.close(); conn.close(); session['user_name']=name; flash('Profile updated.', 'success'); return redirect(url_for('profile'))
        flash('Name and phone are required.', 'error')
    return render_template('profile.html', user=user)


@app.route('/admin')
@admin_required
def admin_dashboard():
    counts = {key: query(sql, one=True)['count'] for key, sql in {'foods':'SELECT COUNT(*) count FROM foods','customers':"SELECT COUNT(*) count FROM users WHERE role='customer'",'orders':'SELECT COUNT(*) count FROM orders'}.items()}
    recent_orders = query('SELECT orders.*, users.full_name FROM orders JOIN users ON orders.user_id=users.id ORDER BY order_date DESC LIMIT 5')
    return render_template('admin/dashboard.html', counts=counts, orders=recent_orders)


@app.route('/admin/foods')
@admin_required
def admin_foods(): return render_template('admin/foods.html', foods=query('SELECT * FROM foods ORDER BY id DESC'))


def food_form(food=None):
    if request.method == 'POST':
        data = [request.form.get(k,'').strip() for k in ['name','description','category','price','image']]
        if not all(data[:4]): flash('Name, description, category, and price are required.', 'error')
        else:
            try:
                price=float(data[3]); conn=db_connection(); cur=conn.cursor()
                if food: cur.execute('UPDATE foods SET name=%s,description=%s,category=%s,price=%s,image=%s WHERE id=%s', (*data[:3],price,data[4],food['id']))
                else: cur.execute('INSERT INTO foods (name,description,category,price,image) VALUES (%s,%s,%s,%s,%s)', (*data[:3],price,data[4]))
                conn.commit(); cur.close(); conn.close(); flash('Food saved successfully.', 'success'); return redirect(url_for('admin_foods'))
            except (ValueError, Error): flash('Enter a valid price.', 'error')
    return render_template('admin/edit_food.html' if food else 'admin/add_food.html', food=food)


@app.route('/admin/foods/add', methods=['GET','POST'])
@admin_required
def add_food(): return food_form()


@app.route('/admin/foods/<int:food_id>/edit', methods=['GET','POST'])
@admin_required
def edit_food(food_id):
    food=query('SELECT * FROM foods WHERE id=%s',(food_id,),one=True)
    if not food: return render_template('404.html'),404
    return food_form(food)


@app.route('/admin/foods/<int:food_id>/delete', methods=['POST'])
@admin_required
def delete_food(food_id):
    try:
        conn=db_connection(); cur=conn.cursor(); cur.execute('DELETE FROM foods WHERE id=%s',(food_id,)); conn.commit(); cur.close(); conn.close(); flash('Food deleted.', 'success')
    except Error: flash('Food cannot be deleted because it belongs to an existing order.', 'error')
    return redirect(url_for('admin_foods'))


@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders_list = query('SELECT orders.*, users.full_name, users.phone, rider.full_name AS rider_name FROM orders JOIN users ON orders.user_id=users.id LEFT JOIN users AS rider ON orders.delivery_person_id=rider.id ORDER BY order_date DESC')
    riders = query("SELECT id, full_name, phone FROM users WHERE role='delivery_person' ORDER BY full_name")
    return render_template('admin/orders.html', orders=orders_list, riders=riders)


@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def order_status(order_id):
    status=request.form.get('status');
    if status in ['Pending','Preparing','Delivered']:
        conn=db_connection();cur=conn.cursor();cur.execute('UPDATE orders SET status=%s WHERE id=%s',(status,order_id));conn.commit();cur.close();conn.close();flash('Order status updated.','success')
    return redirect(url_for('admin_orders'))


@app.route('/admin/orders/<int:order_id>/assign', methods=['POST'])
@admin_required
def assign_delivery(order_id):
    rider_id = request.form.get('delivery_person_id', type=int)
    rider = query("SELECT id FROM users WHERE id=%s AND role='delivery_person'", (rider_id,), one=True) if rider_id else None
    if not rider:
        flash('Choose a valid delivery person.', 'error')
    else:
        conn = db_connection(); cur = conn.cursor()
        cur.execute("UPDATE orders SET delivery_person_id=%s, delivery_status='Assigned' WHERE id=%s", (rider_id, order_id))
        conn.commit(); cur.close(); conn.close()
        flash('Delivery person assigned successfully.', 'success')
    return redirect(url_for('admin_orders'))


@app.route('/delivery')
@delivery_required
def delivery_dashboard():
    assigned_orders = query('SELECT orders.*, users.full_name, users.phone FROM orders JOIN users ON orders.user_id=users.id WHERE orders.delivery_person_id=%s ORDER BY orders.order_date DESC', (session['user_id'],))
    return render_template('delivery_dashboard.html', orders=assigned_orders)


@app.route('/delivery/orders/<int:order_id>/status', methods=['POST'])
@delivery_required
def delivery_status(order_id):
    status = request.form.get('delivery_status')
    allowed_statuses = ['Assigned', 'Out for Delivery', 'Delivered']
    if status not in allowed_statuses:
        flash('Invalid delivery status.', 'error')
        return redirect(url_for('delivery_dashboard'))
    conn = db_connection(); cur = conn.cursor()
    if status == 'Delivered':
        cur.execute("UPDATE orders SET delivery_status=%s, status='Delivered' WHERE id=%s AND delivery_person_id=%s", (status, order_id, session['user_id']))
    else:
        cur.execute('UPDATE orders SET delivery_status=%s WHERE id=%s AND delivery_person_id=%s', (status, order_id, session['user_id']))
    conn.commit(); cur.close(); conn.close()
    flash('Delivery status updated.', 'success')
    return redirect(url_for('delivery_dashboard'))


@app.route('/admin/customers')
@admin_required
def customers(): return render_template('admin/customers.html', customers=query("SELECT id,full_name,email,phone,created_at FROM users WHERE role='customer' ORDER BY id DESC"))


@app.errorhandler(404)
def not_found(error): return render_template('404.html'), 404


@app.errorhandler(Error)
def database_error(error):
    """Show a friendly page when MySQL is unavailable or returns an error."""
    # Keep the browser message simple, but show the real MySQL error in Flask's terminal.
    app.logger.error('MySQL error: %s', error)
    return render_template('database_error.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
