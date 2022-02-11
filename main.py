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


#################################### Database schema ##########################################

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = ""
    Fname = ""
    Lname = ""
    country = ""
    address = ""
    city = ""
    postcode = ""
    phone = ""
    email = ""
    password = ""
    cart = ""
    order = ""
    wishlist = ""


class Products(db.Model):
    __tablename__ = "products"
    id = ""
    name = ""
    price = ""
    image_url = ""
    stock = ""
    description = ""
    size = ""
    cart = ""
    number_of_products = db.Column(db.Float(3), nullable=False)
    wishlist = ""


class Cart(db.Model):
    __tablename__ = "cart"
    id = ""
    user_id = ""
    product_id = ""
    product = ""
    user = ""
    number_of_products = db.Column(db.Float(3), nullable=False)


class Category(db.Model):
    __tablename__ = "categories"
    id = ""
    product_id = ""
    name = ""
    products = ""
    pass


class Wishlist(db.Model):
    id = ""
    product_id = ""
    user_id = ""
    products = ""


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
