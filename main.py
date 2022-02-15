from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import _sqlite3

app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = "letbuildthisstuff"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#################################### Database schema ##########################################

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    Fname = db.Column(db.String(250), nullable=True)
    Lname = db.Column(db.String(250), nullable=True)
    country = db.Column(db.String(250), nullable=True)
    address = db.Column(db.String(250), nullable=True)
    city = db.Column(db.String(250), nullable=True)
    postcode = db.Column(db.String(250), nullable=True)
    phone = db.Column(db.String(250), nullable=True)
    email = db.Column(db.String(250), nullable=True, secondary_key=True)
    password = db.Column(db.String(250), nullable=True)
    cart = relationship("Cart", back_populates="user")
    wishlist = relationship("Wishlist", back_populates="added_by")


#

class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=True)
    price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(250), nullable=True)
    stock = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(250), nullable=True)
    size = db.Column(db.String(250), nullable=True)
    cart = relationship("Cart", back_populates="products")
    # number_of_products = db.Column(db.Float(3), nullable=False)
    wishlist = relationship("Wishlist", back_populates="products")
    product_category = relationship("Category", back_populates="products")


#
class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    name = db.Column(db.String(250), nullable=True)
    products = relationship("Products", back_populates="product_category")


#
#
class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    product = relationship("Products", back_populates="cart")
    user = relationship("User", back_populates="cart")
    number_of_products = db.Column(db.Float(3), nullable=False)


#
#
class Wishlist(db.Model):
    __tablename__ = "wishlists"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    products = relationship("Products", back_populates="wishlist")
    added_by = relationship("User", back_populates="wishlist")


db.create_all()


@app.route('/add', methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        stock = request.form["stock"]
        size = request.form["size"]
        description = request.form["desc"]
        img_url = request.files["img"]
        print(f"{name}\n{price}\n{stock}\n{size}\n{description}\n{img_url}")
        print(img_url.filename)

    return render_template("add.html")


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/shop')
def shop():
    return render_template("shop.html")


@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/account')
def account():
    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run(debug=True)
