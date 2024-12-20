# ====================================
# Flask E-Commerce Application
# ====================================

# Import necessary libraries
from flask import Flask, render_template, url_for, request, session, redirect, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
import random

# ====================================
# Application Configuration
# ====================================

# Initialize Flask application
app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database and migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Session configuration
app.secret_key = os.urandom(24)

# File upload configuration
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ====================================
# Database Models
# ====================================

class User(db.Model):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.username}>"

class Item(db.Model):
    """Item model for product management"""
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(80), nullable=False, unique=True)
    item_price = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(255))
    item_type = db.Column(db.String(100))
    item_gender = db.Column(db.String(100))
    description = db.Column(db.Text())

    def to_dict(self):
        """Convert item to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.item_name,
            'gender': self.item_gender,
            'price': self.item_price,
            'image_path': self.image_path,
            'type': self.item_type,
            'description': self.description
        }

    def __repr__(self):
        return f"<item {self.item_name}>"

class CartItem(db.Model):
    """Cart item model for shopping cart management"""
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    item_id = db.Column(db.Integer)

    def __repr__(self):
        return f"<CartItem {self.id}>"

class Order(db.Model):
    """Order model for order processing"""
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    total_price = db.Column(db.Float)
    order_number = db.Column(db.Integer)
    user_address = db.Column(db.String(100))
    user_city = db.Column(db.String(100))
    user_country = db.Column(db.String(100))
    user_mobile_number = db.Column(db.String(100))

    def __repr__(self):
        return f"<Order {self.id}>"

# Create database tables
with app.app_context():
    db.create_all()

# ====================================
# Product Management Routes
# ====================================

@app.route("/additem", methods=["POST", "GET"])
def add_item():
    """Handle adding new items to the store (admin only)"""
    if not session.get("is_admin"):
        return redirect("/signin")

    if request.method == "POST":
        # Extract form data
        item_name = request.form.get("item_name")
        item_price = request.form.get("item_price")
        item_description = request.form.get("item_description")
        item_image = request.files.get("item_image")
        item_type = request.form.get("type")
        item_gender = request.form.get("gender")

        # Validate form data
        if not all([item_image, item_price, item_name, item_type, item_gender, item_description]):
            return render_template("additem.html", 
                                username=session["username"], 
                                error="All fields are required")

        # Process image and save item
        if item_image.filename:
            filename = secure_filename(item_image.filename)
            item_image.save(os.path.join(UPLOAD_FOLDER, filename))

            item = Item(
                item_name=item_name,
                item_price=item_price,
                image_path=f"../static/uploads/{filename}",
                item_type=item_type,
                item_gender=item_gender,
                description=item_description
            )
            db.session.add(item)
            db.session.commit()
            return redirect("/additem")

        return render_template("additem.html", 
                            username=session["username"], 
                            error="something wrong happened")

    return render_template("additem.html", username=session["username"])

# ====================================
# API Routes
# ====================================

@app.route("/getitems/<string:gender>")
def getItems(gender):
    """API endpoint to get items by gender"""
    requested_items = Item.query.filter_by(item_gender=gender)
    if requested_items:
        items_list = [item.to_dict() for item in requested_items]
        return jsonify(items_list)
    return jsonify(error="No items found for the specified gender"), 404

# ====================================
# Shopping Cart Routes
# ====================================

@app.route("/item/<int:item_id>")
def item(item_id):
    """Display individual item details"""
    item_data = Item.query.filter_by(id=item_id).first()
    if not item_data:
        return "Item Not Found"
    
    return render_template("item.html", 
                         item=item_data, 
                         username=session.get("username"), 
                         user_id=session.get("user_id"))

@app.route("/addtocart/<int:item_id>")
def add_to_cart(item_id):
    """Add item to shopping cart"""
    item_to_add = Item.query.filter_by(id=item_id).first()
    if not item_id:
        return "item not found"

    user_id = session.get("user_id")
    if not user_id:
        return jsonify([{"error": "please sign in first"}])

    # Check if item already in cart
    existing_item = CartItem.query.filter_by(item_id=item_id, user_id=user_id).first()
    if existing_item:
        return jsonify([{"error": "item already there"}])

    # Add item to cart
    cart_adder = CartItem(user_id=user_id, item_id=item_id)
    db.session.add(cart_adder)
    db.session.commit()

    return jsonify([{"success": True, "fail": False}])

@app.route("/shoppingcart/<int:user_id>")
def shopping_cart(user_id):
    """Display shopping cart contents"""
    if session.get("user_id") != user_id:
        return redirect("/signin")

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    items_in_cart = []
    for cart_item in cart_items:
        item = Item.query.get(cart_item.item_id)
        if item:
            items_in_cart.append(item)

    if not items_in_cart:
        return render_template("shoppingcart.html")

    return render_template("shoppingcart.html", 
                         cart_items=items_in_cart, 
                         user_id=user_id, 
                         username=session.get("username"))

@app.route("/removefromcart/<int:item_id>")
def remove_from_cart(item_id):
    """Remove item from shopping cart"""
    item_to_remove = Item.query.filter_by(id=item_id).first()
    if not item_id:
        return "item not found"

    user_id = session.get("user_id")
    if not user_id:
        return jsonify([{"error": "please sign in first"}])

    cart_item = CartItem.query.filter_by(item_id=item_id, user_id=user_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify([{"success": True, "fail": False}])

    return jsonify([{"error": "item not in cart"}])

# ====================================
# Checkout and Order Routes
# ====================================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    """Handle order checkout process"""
    user_id = session.get("user_id")
    if not user_id:
        return redirect("signin")

    cart_items = CartItem.query.filter_by(user_id=user_id)
    if not cart_items.first():
        return redirect("/")

    # Get items and calculate total
    items_in_cart = []
    total_price = 0
    for cart_item in cart_items:
        item = Item.query.get(cart_item.item_id)
        if item:
            items_in_cart.append(item)
            total_price += float(item.item_price)

    shipping = 35.0
    total_price += shipping
    username = session.get("username")

    if request.method == "POST":
        # Process order
        address = request.form.get("address")
        city = request.form.get("city")
        country = request.form.get("country")
        phone_number = request.form.get("number")

        # Validate order data
        if not all([address, city, country, phone_number]):
            return render_template("checkout.html", 
                                items_in_cart=items_in_cart, 
                                total_price=total_price,
                                error="All fields are required",
                                username=username,
                                user_id=user_id,
                                shipping=shipping)

        # Create order
        order_number = random.randint(100000, 999999)
        order = Order(
            user_id=user_id,
            total_price=total_price,
            user_address=address,
            user_city=city,
            user_country=country,
            user_mobile_number=phone_number,
            order_number=order_number
        )
        db.session.add(order)

        # Clear cart
        for item in cart_items:
            db.session.delete(item)

        db.session.commit()
        return redirect("/")

    return render_template("checkout.html", 
                         items_in_cart=items_in_cart,
                         total_price=total_price,
                         shipping=shipping,
                         username=username,
                         user_id=user_id)

@app.route("/user/<int:user_id>")
def user(user_id):
    """Display user profile and orders"""
    if not session.get("user_id") or session.get("user_id") != user_id:
        return redirect("/signin")

    user_orders = Order.query.filter_by(user_id=user_id).all()
    return render_template("user.html", 
                         username=session.get("username"),
                         user_id=user_id,
                         user_orders=user_orders)

# ====================================
# Authentication Routes
# ====================================

@app.route("/")
def main():
    """Main page route"""
    return render_template("index.html", 
                         username=session.get('username'),
                         user_id=session.get("user_id"))

@app.route("/signin", methods=["GET", "POST"])
def signin():
    """Handle user sign in"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter(User.username == username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session["is_admin"] = user.is_admin
            return redirect("/")
        
        return render_template("signin.html", error="wrong password/username")

    return render_template("signin.html", signin=True)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user registration"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("password")

        # Validate registration data
        if User.query.filter(User.username == username).first():
            return render_template("signup.html", error="user already exists")
        
        if password != password_confirmation:
            return render_template("signup.html", error="passwords don't match")
        
        if len(password) < 8:
            return render_template("signup.html", error="password's length should be longer than 8")

        # Create new user
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/signin")

    return render_template("signup.html")

@app.route("/logout")
def logout():
    """Handle user logout"""
    session.clear()
    return redirect("/")

# ====================================
# Application Entry Point
# ====================================

if __name__ == '__main__':
    app.run(debug=True)