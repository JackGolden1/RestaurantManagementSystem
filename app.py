from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from decimal import Decimal
import os

app = Flask(__name__)
app.secret_key = "your_secret_key" 

# MySQL Configuration - Use environment variables for Docker
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'database_mgt')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Helper Functions
def login_required(f):
    """Decorator to ensure user is logged in"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to ensure user is admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    """Decorator to ensure user is staff or admin"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] not in ['admin', 'staff']:
            flash('Staff access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home Page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'customer')

        cursor = mysql.connection.cursor()

        if user_type == 'customer':
            cursor.execute("SELECT * FROM Customer WHERE Email=%s", (email,))
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user['CustomerID']
                session['user_name'] = f"{user['FirstName']} {user['LastName']}"
                session['user_role'] = 'customer'
                flash(f"Welcome back, {user['FirstName']}!", 'success')
                cursor.close()
                return redirect(url_for('customer_dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        else:
            # Staff/Admin Login (ContactInfo contains email addresses)
            cursor.execute("SELECT * FROM Staff WHERE ContactInfo=%s", (email,))
            staff = cursor.fetchone()
            
            if staff:
                session['user_id'] = staff['StaffID']
                session['user_name'] = f"{staff['FirstName']} {staff['LastName']}"
                session['user_role'] = 'admin' if staff['Role'] == 'Manager' else 'staff'
                flash(f"Welcome back, {staff['FirstName']}!", 'success')
                cursor.close()
                return redirect(url_for('admin_dashboard') if session['user_role'] == 'admin' else url_for('staff_dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        
        cursor.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Customer Registration Page"""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone', '')

        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO Customer (FirstName, LastName, Email, Phone) VALUES (%s, %s, %s, %s)",
                           (first_name, last_name, email, phone))
            mysql.connection.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            flash('Error during registration. Please try again.', 'danger')
        finally:
            cursor.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout User"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

#  CUSTOMER ROUTES

@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    """Customer Dashboard"""
    if session.get('user_role') != 'customer':
        return redirect(url_for('index'))
    
    cursor = mysql.connection.cursor()

    # Get upcoming reservations
    cursor.execute("""              
        SELECT r.ReservationID, d.TableNumber, d.Location, r.StartDateTime, r.PartySize AS NumberOfGuests
        FROM Reservation r
        JOIN DiningTable d ON r.TableID = d.TableID
        WHERE r.CustomerID = %s AND r.Status = 'Booked' AND r.StartDateTime >= NOW()
        ORDER BY r.StartDateTime ASC
    """, (session['user_id'],))
    reservations = cursor.fetchall()

    # Get recent orders
    cursor.execute("""
        SELECT o.OrderID, o.OrderDateTime, o.Status, COALESCE(p.Amount, 0) AS Amount
        FROM SalesOrder o
        LEFT JOIN Payment p ON o.OrderID = p.OrderID
        WHERE o.CustomerID = %s
        ORDER BY o.OrderDateTime DESC
        LIMIT 5
    """, (session['user_id'],))
    orders = cursor.fetchall()
    cursor.close()
    
    return render_template('customer/dashboard.html', reservations=reservations, orders=orders)

@app.route('/customer/reservations')
@login_required
def customer_reservations():
    """Customer Reservations Page"""
    if session.get('user_role') != 'customer':
        return redirect(url_for('index'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT r.ReservationID, d.TableNumber, d.Location, d.Capacity, r.StartDateTime, r.PartySize AS NumberOfGuests, r.Status
        FROM Reservation r
        JOIN DiningTable d ON r.TableID = d.TableID
        WHERE r.CustomerID = %s
        ORDER BY r.StartDateTime DESC
    """, (session['user_id'],))
    reservations = cursor.fetchall()
    cursor.close()

    return render_template('customer/reservations.html', reservations=reservations)

@app.route('/customer/make_reservation', methods=['GET', 'POST'])
@login_required
def make_reservation():
    """Make a Reservation"""
    if session.get('user_role') != 'customer':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        table_id = request.form.get('table_id')
        date = request.form.get('date')
        time = request.form.get('time')
        party_size = request.form.get('party_size')
        notes = request.form.get('notes', '')

        # Combine date and time
        start_datetime_str = f"{date} {time}:00"
        # End time is 2 hours later
        end_datetime_str = (datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S') + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor = mysql.connection.cursor()
        try:
            # Check if table is available
            cursor.execute("""
                SELECT COUNT(*) AS count FROM Reservation
                WHERE TableID = %s AND Status = 'Booked' AND (
                    (StartDateTime <= %s AND EndDateTime > %s) OR
                    (StartDateTime < %s AND EndDateTime >= %s)
                )
            """, (table_id, start_datetime_str, start_datetime_str, end_datetime_str, end_datetime_str))
            conflict = cursor.fetchone()

            if conflict['count'] > 0:
                flash('Selected table is not available at the chosen time. Please select a different time or table.', 'danger')
                return redirect(url_for('make_reservation'))
            
            cursor.execute("""
                INSERT INTO Reservation (CustomerID, TableID, StartDateTime, EndDateTime, PartySize, Notes, Status)
                VALUES (%s, %s, %s, %s, %s, %s, 'Booked')
            """, (session['user_id'], table_id, start_datetime_str, end_datetime_str, party_size, notes))
            mysql.connection.commit()
            flash('Reservation made successfully!', 'success')
            return redirect(url_for('customer_reservations'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error making reservation: {str(e)}', 'danger')
        finally:
            cursor.close()

    # Get available tables
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT TableID, TableNumber, Capacity FROM DiningTable ORDER BY TableNumber")
    tables = cursor.fetchall()  
    cursor.close()
    
    # Get today's date for the date input min attribute
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('customer/make_reservation.html', tables=tables, today=today)

@app.route('/customer/menu')
@login_required
def customer_menu():
    """Customer Menu Page"""
    if session.get('user_role') != 'customer':
        return redirect(url_for('index'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM MenuItem WHERE IsAvailable = 1 ORDER BY Category, Name")
    menu_items = cursor.fetchall()
    cursor.close()
    
    # Group menu items by category
    categorized_menu = {}
    for item in menu_items:
        category = item['Category']
        if category not in categorized_menu:
            categorized_menu[category] = []
        categorized_menu[category].append(item)
    
    return render_template('customer/menu.html', categorized_menu=categorized_menu)

@app.route('/customer/orders', methods=['POST'])    
@login_required
def place_order():
    """Place an Order"""
    if session.get('user_role') != 'customer':
        return redirect(url_for('index'))
    
    # Accept both JSON requests (API-style) and form submissions (from the menu page)
    order_items = []
    if request.is_json:
        order_items = request.json.get('order_items', [])
    else:
        # Build items from form fields
        form_item_ids = request.form.getlist('items[]')
        form_quantities = request.form.getlist('quantities[]')
        for item_id, qty in zip(form_item_ids, form_quantities):
            try:
                qty_int = int(qty)
            except (TypeError, ValueError):
                qty_int = 0
            if qty_int > 0:
                order_items.append({'item_id': int(item_id), 'quantity': qty_int})
    
    if not order_items:
        if request.is_json:
            return jsonify({'status': 'error', 'message': 'No items in order.'}), 400
        flash('Please select at least one item with quantity greater than 0.', 'warning')
        return redirect(url_for('customer_menu'))

    cursor = mysql.connection.cursor()
    try:
        # Create new order
        cursor.execute("INSERT INTO SalesOrder (CustomerID, OrderDateTime, Status) VALUES (%s, NOW(), 'Open')",
                       (session['user_id'],))
        order_id = cursor.lastrowid

        # Insert order items
        for item in order_items:
            item_id = item['item_id']
            quantity = item['quantity']
            
            if int(quantity) > 0:
                # Get current price
                cursor.execute("SELECT BasePrice FROM MenuItem WHERE ItemID = %s", (item_id,))
                menu_item = cursor.fetchone()
                
                if menu_item:
                    cursor.execute("""
                        INSERT INTO OrderItem (OrderID, ItemID, Quantity, UnitPriceAtOrder)
                        VALUES (%s, %s, %s, %s)
                    """, (order_id, item_id, quantity, menu_item['BasePrice']))

        mysql.connection.commit()
        if request.is_json:
            return jsonify({'status': 'success', 'order_id': order_id, 'message': f'Order #{order_id} placed successfully!'}), 200
        flash(f'Order #{order_id} placed successfully!', 'success')
        return redirect(url_for('view_order', order_id=order_id))
    except Exception as e:
        mysql.connection.rollback()
        if request.is_json:
            return jsonify({'status': 'error', 'message': f'Error placing order: {str(e)}'}), 500
        flash(f'Error placing order: {str(e)}', 'danger')
        return redirect(url_for('customer_menu'))
    finally:
        cursor.close()

@app.route('/customer/order/<int:order_id>')
@login_required
def view_order(order_id):
    """View order details"""
    cursor = mysql.connection.cursor()
    
    # Get order
    cursor.execute("""
        SELECT o.*, CONCAT(c.FirstName, ' ', c.LastName) as CustomerName
        FROM SalesOrder o
        JOIN Customer c ON o.CustomerID = c.CustomerID
        WHERE o.OrderID = %s
    """, (order_id,))
    order = cursor.fetchone()
    
    if not order:
        cursor.close()
        flash('Order not found.', 'danger')
        return redirect(url_for('customer_dashboard'))
    
    # Get order items
    cursor.execute("""
        SELECT oi.*, m.Name, m.Category
        FROM OrderItem oi
        JOIN MenuItem m ON oi.ItemID = m.ItemID
        WHERE oi.OrderID = %s
    """, (order_id,))
    items = cursor.fetchall()
    
    # Get payment if exists
    cursor.execute("SELECT * FROM Payment WHERE OrderID = %s", (order_id,))
    payment = cursor.fetchone()
    
    cursor.close()
    
    # Calculate total
    total = sum(float(item['Quantity']) * float(item['UnitPriceAtOrder']) for item in items)
    
    return render_template('view_order.html', order=order, items=items, payment=payment, total=total)

# STAFF ROUTES

@app.route('/staff/dashboard')
@login_required
@staff_required
def staff_dashboard():
    """Staff dashboard"""
    cursor = mysql.connection.cursor()
    
    # Get today's reservations
    cursor.execute("""
        SELECT r.*, c.FirstName, c.LastName, c.Phone, d.TableNumber
        FROM Reservation r
        JOIN Customer c ON r.CustomerID = c.CustomerID
        JOIN DiningTable d ON r.TableID = d.TableID
        WHERE DATE(r.StartDateTime) = CURDATE()
        AND r.Status IN ('Booked', 'Seated')
        ORDER BY r.StartDateTime
    """)
    reservations = cursor.fetchall()
    
    # Get open orders
    cursor.execute("""
        SELECT o.*, c.FirstName, c.LastName
        FROM SalesOrder o
        JOIN Customer c ON o.CustomerID = c.CustomerID
        WHERE o.Status = 'Open'
        ORDER BY o.OrderDateTime
    """)
    orders = cursor.fetchall()
    
    cursor.close()
    
    return render_template('staff_dashboard.html', 
                         reservations=reservations, 
                         orders=orders)

@app.route('/staff/reservations')
@login_required
@staff_required
def staff_reservations():
    """Manage all reservations"""
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT r.*, c.FirstName, c.LastName, c.Phone, c.Email,
               d.TableNumber, d.Location
        FROM Reservation r
        JOIN Customer c ON r.CustomerID = c.CustomerID
        JOIN DiningTable d ON r.TableID = d.TableID
        WHERE r.StartDateTime >= CURDATE()
        ORDER BY r.StartDateTime
    """)
    reservations = cursor.fetchall()
    cursor.close()
    
    return render_template('staff_reservations.html', reservations=reservations)

@app.route('/staff/update-reservation/<int:reservation_id>', methods=['POST'])
@login_required
@staff_required
def update_reservation_status(reservation_id):
    """Update reservation status"""
    status = request.form.get('status')
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            UPDATE Reservation 
            SET Status = %s 
            WHERE ReservationID = %s
        """, (status, reservation_id))
        mysql.connection.commit()
        flash(f'Reservation status updated to {status}.', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error updating reservation: {str(e)}', 'danger')
    finally:
        cursor.close()
    
    return redirect(url_for('staff_reservations'))

@app.route('/staff/orders')
@login_required
@staff_required
def staff_orders():
    """View and manage orders"""
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT o.*, c.FirstName, c.LastName,
               COALESCE(p.Amount, 0) as PaymentAmount,
               p.Status as PaymentStatus
        FROM SalesOrder o
        JOIN Customer c ON o.CustomerID = c.CustomerID
        LEFT JOIN Payment p ON o.OrderID = p.OrderID
        ORDER BY o.OrderDateTime DESC
    """)
    orders = cursor.fetchall()
    cursor.close()
    
    return render_template('staff_orders.html', orders=orders)

@app.route('/staff/order/<int:order_id>')
@login_required
@staff_required
def staff_view_order(order_id):
    """View order details for staff"""
    cursor = mysql.connection.cursor()
    
    # Get order
    cursor.execute("""
        SELECT o.*, CONCAT(c.FirstName, ' ', c.LastName) as CustomerName,
               c.Phone, c.Email
        FROM SalesOrder o
        JOIN Customer c ON o.CustomerID = c.CustomerID
        WHERE o.OrderID = %s
    """, (order_id,))
    order = cursor.fetchone()
    
    # Get order items
    cursor.execute("""
        SELECT oi.*, m.Name, m.Category
        FROM OrderItem oi
        JOIN MenuItem m ON oi.ItemID = m.ItemID
        WHERE oi.OrderID = %s
    """, (order_id,))
    items = cursor.fetchall()
    
    # Get payment
    cursor.execute("SELECT * FROM Payment WHERE OrderID = %s", (order_id,))
    payment = cursor.fetchone()
    
    cursor.close()
    
    total = sum(float(item['Quantity']) * float(item['UnitPriceAtOrder']) for item in items)
    
    return render_template('staff_view_order.html', 
                         order=order, items=items, 
                         payment=payment, total=total)

@app.route('/staff/process-payment/<int:order_id>', methods=['POST'])
@login_required
@staff_required
def process_payment(order_id):
    """Process payment for an order"""
    amount = float(request.form.get('amount'))
    payment_method = request.form.get('payment_method')
    
    cursor = mysql.connection.cursor()
    try:
        # Insert payment
        cursor.execute("""
            INSERT INTO Payment (OrderID, Amount, PaymentMethod, PaymentDateTime, Status)
            VALUES (%s, %s, %s, NOW(), 'Captured')
        """, (order_id, amount, payment_method))
        
        # Update order status
        cursor.execute("""
            UPDATE SalesOrder 
            SET Status = 'Closed' 
            WHERE OrderID = %s
        """, (order_id,))
        
        mysql.connection.commit()
        flash('Payment processed successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error processing payment: {str(e)}', 'danger')
    finally:
        cursor.close()
    
    return redirect(url_for('staff_view_order', order_id=order_id))

# ADMIN ROUTES 

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard with reports"""
    cursor = mysql.connection.cursor()
    
    # Today's stats
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM Reservation 
        WHERE DATE(StartDateTime) = CURDATE()
    """)
    today_reservations = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM SalesOrder 
        WHERE DATE(OrderDateTime) = CURDATE()
    """)
    today_orders = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT COALESCE(SUM(Amount), 0) as revenue 
        FROM Payment 
        WHERE DATE(PaymentDateTime) = CURDATE()
        AND Status = 'Captured'
    """)
    today_revenue = cursor.fetchone()['revenue']
    
    # Top menu items
    cursor.execute("""
        SELECT m.Name, SUM(oi.Quantity) as TotalSold
        FROM OrderItem oi
        JOIN MenuItem m ON oi.ItemID = m.ItemID
        GROUP BY m.ItemID, m.Name
        ORDER BY TotalSold DESC
        LIMIT 5
    """)
    top_items = cursor.fetchall()
    
    cursor.close()
    
    return render_template('admin_dashboard.html',
                         today_reservations=today_reservations,
                         today_orders=today_orders,
                         today_revenue=today_revenue,
                         top_items=top_items)

@app.route('/admin/menu')
@login_required
@admin_required
def admin_menu():
    """Manage menu items"""
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM MenuItem ORDER BY Category, Name")
    menu_items = cursor.fetchall()
    cursor.close()
    
    return render_template('admin_menu.html', menu_items=menu_items)

@app.route('/admin/menu/add', methods=['POST'])
@login_required
@admin_required
def add_menu_item():
    """Add new menu item"""
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price')
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO MenuItem (Name, Category, BasePrice, IsAvailable)
            VALUES (%s, %s, %s, 1)
        """, (name, category, price))
        mysql.connection.commit()
        flash('Menu item added successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error adding menu item: {str(e)}', 'danger')
    finally:
        cursor.close()
    
    return redirect(url_for('admin_menu'))

@app.route('/admin/menu/update/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def update_menu_item(item_id):
    """Update menu item"""
    price = request.form.get('price')
    available = request.form.get('available', '0')
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("""
            UPDATE MenuItem 
            SET BasePrice = %s, IsAvailable = %s 
            WHERE ItemID = %s
        """, (price, available, item_id))
        mysql.connection.commit()
        flash('Menu item updated successfully!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error updating menu item: {str(e)}', 'danger')
    finally:
        cursor.close()
    
    return redirect(url_for('admin_menu'))

@app.route('/admin/staff')
@login_required
@admin_required
def admin_staff():
    """Manage staff"""
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Staff ORDER BY LastName, FirstName")
    staff_members = cursor.fetchall()
    cursor.close()
    
    return render_template('admin_staff.html', staff_members=staff_members)

@app.route('/admin/reports')
@login_required
@admin_required
def admin_reports():
    """View reports"""
    cursor = mysql.connection.cursor()
    
    # Daily revenue report
    cursor.execute("""
        SELECT DATE(p.PaymentDateTime) as Date,
               COUNT(DISTINCT o.OrderID) as Orders,
               SUM(p.Amount) as Revenue
        FROM Payment p
        JOIN SalesOrder o ON p.OrderID = o.OrderID
        WHERE p.Status = 'Captured'
        GROUP BY DATE(p.PaymentDateTime)
        ORDER BY Date DESC
        LIMIT 30
    """)
    daily_revenue = cursor.fetchall()
    
    # Staff performance
    cursor.execute("""
        SELECT CONCAT(s.FirstName, ' ', s.LastName) as StaffName,
               COUNT(DISTINCT o.OrderID) as OrdersHandled,
               COALESCE(SUM(oi.Quantity * oi.UnitPriceAtOrder), 0) as TotalSales
        FROM Staff s
        LEFT JOIN SalesOrder o ON o.StaffID = s.StaffID
        LEFT JOIN OrderItem oi ON oi.OrderID = o.OrderID
        GROUP BY s.StaffID, s.FirstName, s.LastName
        ORDER BY TotalSales DESC
    """)
    staff_performance = cursor.fetchall()
    
    cursor.close()
    
    return render_template('admin_reports.html',
                         daily_revenue=daily_revenue,
                         staff_performance=staff_performance)

#  ERROR HANDLERS 

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# RUN APP

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)