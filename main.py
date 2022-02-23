from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from functools import wraps
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import _sqlite3
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
Bootstrap(app)
SAVE_PATH = "static/products/uploads/"
UPLOAD_FOLDER = "products/uploads/"
app.config['SECRET_KEY'] = "letbuildthisstuff"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config["SAVE_PATH"] = SAVE_PATH
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


# creating login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403, "Access denied")
        return f(*args, **kwargs)

    return decorated_function


# check for file type

def allowed_file(filename):
    if filename.split(".")[1] in ALLOWED_EXTENSIONS:
        return True
    else:
        return False


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
    email = db.Column(db.String(250), nullable=True, unique=True)
    password = db.Column(db.String(250), nullable=True)
    cart = relationship("Cart", back_populates="user")
    wishlist = relationship("Wishlist", back_populates="added_by")


#

class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=True)
    price = db.Column(db.Float, nullable=True)
    stock = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(250), nullable=True)
    cart = relationship("Cart", back_populates="product")
    # number_of_products = db.Column(db.Float(3), nullable=False)
    wishlist = relationship("Wishlist", back_populates="product")
    product_category = relationship("Category", back_populates="product")
    prod_image = relationship("Image", back_populates="product")
    prod_size = relationship("Size", back_populates="product")
    rating = relationship("Rating", back_populates="product_rating")


#
class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=True)
    product = relationship("Products", back_populates="product_category")
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)


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
    product = relationship("Products", back_populates="wishlist")
    added_by = relationship("User", back_populates="wishlist")


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(250), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    product = relationship("Products", back_populates="prod_image")


class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sizes = db.Column(db.String(250), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    product = relationship("Products", back_populates="prod_size")


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    product_rating = relationship("Products", back_populates="rating")
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))


db.create_all()


@app.route('/')
def home():
    return render_template("index.html", user=current_user.is_authenticated)


@app.route('/add', methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        category = request.form["category"]
        rating = int(request.form["rating"])
        # size = request.form["size"]
        description = request.form["desc"]
        image1 = request.files["img1"]
        image2 = request.files["img2"]
        image3 = request.files["img3"]
        images = [image1, image2, image3]
        # print(f"{name}\n{price}\n{stock}\n{size}\n{description}\n{images}\n{category}")/

        #  checking if the file type is allowed
        if allowed_file(images[0].filename) and allowed_file(images[1].filename) and allowed_file(images[2].filename):
            # saving product data
            new_product = Products(name=name,
                                   price=price,
                                   stock=stock,
                                   description=description,
                                   # size=size,
                                   )
            db.session.add(new_product)
            db.session.commit()

            product_all = Products.query.filter_by(name=name).all()
            product = product_all[-1]
            # Adding category to category table
            add_category = Category(name=category,
                                    product_id=product.id, )
            db.session.add(add_category)
            db.session.commit()

            new_rating = Rating(number=rating,
                                product_id=product.id,

                                )
            db.session.add(new_rating)
            db.session.commit()

            #  size data and saving it to the database
            if "small" in request.form:
                new_size = Size(product_id=product.id,
                                sizes="small",
                                )
                db.session.add(new_size)

            if "medium" in request.form:
                new_size = Size(product_id=product.id,
                                sizes="medium",
                                )
                db.session.add(new_size)

            if "large" in request.form:
                new_size = Size(product_id=product.id,
                                sizes="large",
                                )
                db.session.add(new_size)

            if "xl" in request.form:
                new_size = Size(product_id=product.id,
                                sizes="xl",
                                )
                db.session.add(new_size)

            if "xxl" in request.form:
                new_size = Size(product_id=product.id,
                                sizes="xxl",
                                )
                db.session.add(new_size)

            db.session.commit()

            for image in images:
                file_name = secure_filename(image.name)

                # saving file to file path
                image.save(os.path.join(SAVE_PATH, file_name))
                os.rename(SAVE_PATH + file_name, SAVE_PATH + image.filename)
                image_loc = UPLOAD_FOLDER + image.filename

                # adding path to database
                new_image = Image(product_id=product.id,
                                  path=image_loc, )
                db.session.add(new_image)
                db.session.commit()
            return redirect(url_for("preview"))
            # print(image_loc)

        else:
            flash("You uploaded an incorrect file")
            return redirect(url_for("add_product"))

    return render_template("add.html", user=current_user.is_authenticated)


@app.route('/preview-product')
def preview():
    data = Products.query.all()
    return render_template("preview.html", datas=data, user=current_user.is_authenticated)


@app.route('/edit-product/<product_id>', methods=["POST", "GET"])
def edit_product(product_id):
    # getting post details by id passed to route
    product = Products.query.get(product_id)
    print(product.description)

    # creating s dictionary to pass the html document
    update_product = {"id": product.id, "name": product.name, "price": product.price,
                      "rating": product.rating[0].number,
                      "category": product.product_category[0].name, "description": product.description,
                      "stock": product.stock, }
    print(update_product["rating"])

    # checking if form is being filled and updating database details with the information
    if request.method == "POST":
        print(request.form["name"])
        product.name = request.form["name"]
        product.price = float(request.form["price"])
        product.rating[0].number = int(request.form["rating"])
        product.stock = int(request.form["stock"])
        product.description = request.form["desc"]
        product.product_category[0].name = request.form["category"]
        db.session.commit()
        return redirect(url_for("preview"))
    # print(request.form["name"])
    return render_template("edit.html", product=update_product, user=current_user.is_authenticated)


@app.route('/delete/<product_id>')
def delete_product(product_id):
    # get products to deelete
    product = Products.query.get(product_id)
    category = Category.query.filter_by(product_id=product_id).first()
    carts = Cart.query.filter_by(product_id=product_id).first()
    image = Image.query.filter_by(product_id=product_id).first()
    rating = Rating.query.filter_by(product_id=product_id).first()
    size = Size.query.filter_by(product_id=product_id).first()
    wishlists = Wishlist.query.filter_by(product_id=product_id).first()

    # deleting product from all table
    db.session.delete(product)
    db.session.delete(category)
    db.session.delete(carts)
    db.session.delete(image)
    db.session.delete(rating)
    db.session.delete(size)
    db.session.delete(wishlists)

    # committing changes to database
    db.session.commit()
    return redirect(url_for("preview"), user=current_user.is_authenticated)


@app.route('/product/<int:p_id>')
def view_product(p_id):
    product = Products.query.get(p_id)
    return render_template("product.html", product=product, user=current_user.is_authenticated)


@app.route('/shop')
def shop():
    data = Products.query.all()

    return render_template("shop.html", datas=data, user=current_user.is_authenticated)


@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html', user=current_user.is_authenticated)


@app.route('/checkout')
def checkout():
    return render_template('checkout.html', user=current_user.is_authenticated)


@app.route('/cart')
def cart():
    return render_template('cart.html', user=current_user.is_authenticated)


@app.route('/account')
def account():
    return render_template('dashboard.html', user=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["login-email"]).first()
        print(request.form["login-email"])
        print(user)
        if not user:
            flash("This user does not exist")
            return redirect(url_for('login'))

        elif check_password_hash(user.password, password=request.form["login-password"]):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("You entered an incorrect password")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        exist_user = User.query.filter_by(email=request.form["register-email"]).first()

        # checking if user already exist
        if exist_user:
            flash("This user already exist")
            return redirect(url_for('register'))

        if len(request.form["register-password"]) < 8:
            flash("Password too short")
            return redirect(request.url)

        email = request.form["register-email"]
        password = generate_password_hash(request.form["register-password"], method='pbkdf2:sha256', salt_length=8)
        user = User()
        user.email = email
        user.password = password

        # committing change to database
        db.session.add(user)
        db.session.commit()

        # logining in user and redirecting to account page
        login_user(user)
        return redirect(url_for('account'))

    return render_template("register.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
