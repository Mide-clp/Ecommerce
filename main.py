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
    orders = relationship("Order", back_populates="users")


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


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=True)
    product = relationship("Products", back_populates="product_category")
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)


class Cart(db.Model):
    __tablename__ = "cart"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    product = relationship("Products", back_populates="cart")
    user = relationship("User", back_populates="cart")
    size = db.Column(db.String(250), nullable=True)
    qty = db.Column(db.Integer, nullable=True)
    total = db.Column(db.Integer, nullable=True)
    orders = relationship("Order", back_populates="cart")


#
#
class Wishlist(db.Model):
    __tablename__ = "wishlists"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    size = db.Column(db.String(250), nullable=True)
    qty = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    product = relationship("Products", back_populates="wishlist")
    added_by = relationship("User", back_populates="wishlist")


class Order(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    users = relationship("User", back_populates="orders")
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"))
    cart = relationship("Cart", back_populates="orders")


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


# This function return the total number of item a user cart
def get_total_cart(user_id):
    wish_list = Wishlist.query.filter_by(user_id=user_id).all()
    # print(len(wish_list))
    return len(wish_list)


@app.route('/')
def home():
    # total item in wishlist
    total_wish_item = 0
    try:
        total_wish_item = get_total_cart(current_user.id)
    except Exception:
        pass
    # print(total_cart_item)
    return render_template("index.html", user=current_user.is_authenticated, wishlist_total=total_wish_item)


@app.route('/add', methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        category = request.form["category"]
        rating = float(request.form["rating"])
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
    # total item in wishlist
    total_wish_item = 0
    try:
        total_wish_item = get_total_cart(current_user.id)
    except Exception:
        pass
    return render_template("add.html", user=current_user.is_authenticated, wishlist_total=total_wish_item)


@app.route('/preview-product')
def preview():
    data = Products.query.all()

    # total item in wishlist
    total_wish_item = 0
    try:
        total_wish_item = get_total_cart(current_user.id)
    except Exception:
        pass
    return render_template("preview.html", datas=data, user=current_user.is_authenticated,
                           wishlist_total=total_wish_item)


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

    # total item in wishlist
    total_wish_item = 0
    try:
        total_wish_item = get_total_cart(current_user.id)
    except Exception:
        pass
    return render_template("edit.html", product=update_product, user=current_user.is_authenticated,
                           wishlist_total=total_wish_item)


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
    return redirect(url_for("preview"))


@app.route('/product/<int:p_id>')
def view_product(p_id):
    product = Products.query.get(p_id)

    # get total item in a wishlist
    total_wish_item = 0
    try:
        total_wish_item = get_total_cart(current_user.id)
    except Exception:
        pass
    return render_template("product.html", product=product, user=current_user.is_authenticated,
                           wishlist_total=total_wish_item)


@app.route('/shop')
def shop():
    data = Products.query.all()

    # get total item in a wishlist
    total_wish_item = 0
    try:
        total_wish_item = get_total_cart(current_user.id)
    except Exception:
        pass
    return render_template("shop.html", datas=data, user=current_user.is_authenticated, wishlist_total=total_wish_item)


@app.route('/wishlist')
def wishlist():
    try:
        wish_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    except:
        flash("Login to view wishlist")
        return redirect(url_for('login'))

    # get total item in a wishlist
    total_wish_item = 0
    try:
        total_wish_item = get_total_cart(current_user.id)
    except Exception:
        pass
    return render_template('wishlist.html', user=current_user.is_authenticated,
                           user_wish=wish_items, wishlist_total=total_wish_item)


@app.route('/delete-wish/<int:wish_id>')
def delete_wishlist(wish_id):
    wish_item = Wishlist.query.get(wish_id)
    db.session.delete(wish_item)
    db.session.commit()

    return redirect(url_for('wishlist'))


@app.route('/checkout')
def checkout():
    # get total item in a wishlist
    total_wish_item = 0
    try:
        total_wish_item = get_total_cart(current_user.id)
    except Exception:
        pass
    return render_template('checkout.html', user=current_user.is_authenticated, wishlist_total=total_wish_item)


#  link to cart page
@app.route('/cart')
def cart():
    cart_items = ""
    total = 0
    try:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()

        for item in cart_items:
            total += item.total
        print(total)
    except Exception:
        pass

    # get total item in a wishlist
    total_wish_item = 0
    try:
        total_wish_item = get_total_cart(current_user.id)
    except Exception:
        pass
    return render_template('cart.html', user=current_user.is_authenticated, wishlist_total=total_wish_item,
                           cart_items=cart_items, cart_total=total)


# delete item from cart
@app.route('/delete-cart-item/<int:cart_id>')
def delete_cart_item(cart_id):
    cart_item = Cart.query.get(cart_id)
    db.session.delete(cart_item)
    db.session.commit()

    return redirect(url_for('cart'))


# Add new products
@app.route('/add-cart-or-prod/<int:add_id>')
def add_cart_or_product(add_id):
    product = Products.query.get(add_id)

    # add to cart
    if request.args.get('add') == "":
        # creating item
        add_cart = Cart()
        try:
            # adding to database
            # print(product.stock)
            if int(product.stock) > int(request.args.get('qty')):
                add_cart.user_id = current_user.id
                add_cart.product_id = add_id
                if request.args.get('size') == "#":
                    flash("choose a size")
                else:
                    add_cart.size = request.args.get('size')
                    add_cart.qty = request.args.get('qty')
                    add_cart.total = round(int(request.args.get('qty')) * float(product.price), 2)
                    db.session.add(add_cart)
                    db.session.commit()
            else:
                flash("Out of stock")
                # return redirect()

        except:
            flash("login to proceed")
            return redirect(url_for('login'))

        print(request.args.get('add'))

    # add to wishlist
    if request.args.get('wish') == "":
        print(request.args.get('wish'))
        # creating item
        add_wish_list = Wishlist()
        try:

            # adding to database
            if int(product.stock) > int(request.args.get('qty')):
                add_wish_list.product_id = add_id
                if request.args.get('size') == "#":
                    flash("choose a size")
                else:
                    add_wish_list.size = request.args.get('size')
                    add_wish_list.qty = request.args.get('qty')
                    add_wish_list.user_id = current_user.id
                    db.session.add(add_wish_list)
                    db.session.commit()
            else:
                flash("Out of stock")

        except:
            flash("login to proceed")
            return redirect(url_for('login'))

    return redirect(url_for('view_product', p_id=add_id))


@app.route('/add-cart/<int:add_id>', methods=["GET", "POST"])
def add_to_cart(add_id):
    new_cart = Cart()

    #  if user addcart from wishlist

    if request.method == "POST":

        wish_to_add = Wishlist.query.get(add_id)
        new_cart.product_id = wish_to_add.product_id
        new_cart.size = wish_to_add.size
        new_cart.qty = wish_to_add.qty
        new_cart.user_id = current_user.id
        new_cart.total = (int(wish_to_add.qty) * float(wish_to_add.product.price))
        db.session.add(new_cart)
        db.session.commit()
        return redirect(url_for('wishlist'))
        # print("hello")
    else:
        try:

            # adding to database

            new_cart.product_id = add_id
            new_cart.size = request.args.get('size')
            new_cart.qty = request.args.get('qty')
            new_cart.user_id = current_user.id
            new_cart.total = (int(request.args.get('qty')) * float(new_cart.product.price))

        except:
            flash("login to proceed")
            return redirect(url_for('login'))

        else:
            db.session.add(new_cart)
            db.session.commit()
    return redirect(url_for('shop'))


@app.route('/add-wishlist/<int:wish_id>')
def add_wish(wish_id):
    add_wish_list = Wishlist()
    try:

        # adding to database
        add_wish_list.product_id = wish_id
        add_wish_list.size = request.args.get('size')
        add_wish_list.qty = request.args.get('qty')
        add_wish_list.user_id = current_user.id

    except:
        flash("login to proceed")
        return redirect(url_for('login'))

    else:
        db.session.add(add_wish_list)
        db.session.commit()

    return redirect(url_for('shop'))


@app.route('/account', methods=["GET", "POST"])
def account():
    # getting user details by id
    user = ""
    try:
        user = User.query.get(current_user.id)
    except:
        flash("You need to login to use this page.")
        return redirect(url_for('login'))
    if request.method == "POST":

        # getting details from form
        first_name = request.form["fname"]
        last_name = request.form["lname"]
        email = request.form.get("email")
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        user.Fname = first_name
        user.Lname = last_name

        if check_password_hash(pwhash=user.password, password=old_password) and email == user.email and \
                new_password == confirm_password and request.form.get("new_password"):

            user.password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
            print(old_password)
            db.session.commit()

        elif email != user.email:
            flash("Incorrect Email")
            return redirect(url_for('account'))

        elif new_password != confirm_password:
            flash("password does not match")
            db.session.commit()
            return redirect(url_for('account'))

        elif not check_password_hash(pwhash=user.password, password=old_password):
            flash("Incorrect password")
            return redirect(url_for('account'))


        else:
            db.session.commit()

        # get total item in a wishlist
    total_wish_item = 0
    try:
        total_wish_item = get_total_cart(current_user.id)
    except Exception:
        pass
    return render_template('dashboard.html', user=current_user.is_authenticated, data=user,
                           wishlist_total=total_wish_item)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["singin-email"]).first()

        if not user:
            flash("This user does not exist")
            return redirect(url_for('login'))

        elif check_password_hash(user.password, password=request.form["singin-password"]):
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

    return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
