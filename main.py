from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate
from forms import LoginUserForm, RegisterUserForm, AddProductForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Configure Table of Database
class ShopProduct(db.Model):
    __tablename__ = "ShopProducts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)
    upload_date = db.Column(db.String(250), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('shop_products', lazy=True))


class ShoppingCart(db.Model):
    __tablename__ = "ShoppingCart"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('shopping_cart', uselist=False)) #uselist=False, it indicates a one-to-one relationship or a many-to-one relationship, where the relationship attribute represents a single object. In your case, user in the ShoppingCart model is associated with a single User object, indicating that each shopping cart is associated with a specific user.
    product_id = db.Column(db.Integer, db.ForeignKey('ShopProducts.id'), nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)
    products = db.relationship('ShopProduct', backref=db.backref("shopping_cart"))


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    name = db.Column(db.String(1000))
    carts = db.relationship('ShopProduct', secondary=ShoppingCart.__table__, backref='user_carts')
    # cart = relationship("ShopProduct", backref=backref("user", lazy=True))
    # products = relationship("ShopProduct", backref=backref("user", lazy=True))
    # comments = relationship("Comment", back_populates="comment_author")

def get_id(self):
    return str(self.id)

#Line below only required once, when creating DB.
with app.app_context():
#     sql_text = text('ALTER TABLE "ShopProducts" ADD COLUMN user_id INTEGER')
#     db.session.execute(sql_text)
#     db.session.commit()
    db.create_all()
    db.session.commit()



# Create FLaskLogin
login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'login'  # Replace 'login' with the appropriate endpoint

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    all_product = ShopProduct.query.all()
    my_cart = None
    if current_user.is_authenticated:
        my_cart = ShoppingCart.query.filter_by(user_id=current_user.id).all()
    # products = ShopProduct.query.all()

    print(all_product)
    return render_template("index.html", products=all_product, my_cart=my_cart)

@app.route('/login', methods=["POST","GET"])
def login():
    form = LoginUserForm()
    if form.validate_on_submit():
        check_user_existed = User.query.filter_by(email=form.email.data).first()
        matching_password = check_password_hash(check_user_existed.password, form.password.data)
        if check_user_existed and matching_password:
            login_user(check_user_existed)
            flash("You Have Successfully Login")
            return redirect(url_for("home"))
        else:
            flash("Invalid Email/Credentials")
    return render_template("login.html", form=form)

@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterUserForm()
    if form.validate_on_submit():
        user_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8)
        new_user = User(
            email= form.email.data,
            password = user_password,
            name = form.name.data
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("register.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/add-product", methods=["POST","GET"])
@login_required
def add_new_product():
    form = AddProductForm()
    if form.validate_on_submit():
        new_product = ShopProduct(
            name=form.name.data,
            description=form.description.data,
            upload_date=datetime.now(),
            stock=form.stock.data,
            price=form.price.data,
            img_url=form.img_url.data,
            user_id=current_user.id
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_product.html", form=form, current_user=current_user)

# @app.route('/add_cart/<int:product_id>', methods=["POST", "GET"])
# @login_required
# def add_cart(product_id):
#     all_cart = ShoppingCart.query.all()
#     product_increase = 1
#     for cart in all_cart :
#         if (cart.user_id == current_user.id) and (cart.product_id == product_id):
#             product_increase = cart.product_quantity + 1
#             break
#
#     add_cart = ShoppingCart(
#         user_id=current_user.id,
#         product_id=product_id,
#         product_quantity= product_increase,
#     )
#     db.session.add(add_cart)
#     db.session.commit()
#     return redirect(url_for("home"))

@app.route('/add_cart/<int:product_id>', methods=["POST", "GET"])
@login_required
def add_cart(product_id):
    cart = ShoppingCart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart:
        cart.product_quantity += 1
    else:
        cart = ShoppingCart(
            user_id=current_user.id,
            product_id=product_id,
            product_quantity=1,
        )
        db.session.add(cart)
    db.session.commit()
    return redirect(request.referrer or url_for("home"))

@app.route('/delete_cart/<int:product_id>', methods=["POST", "GET"])
@login_required
def delete_cart(product_id):
    cart = ShoppingCart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart.product_quantity > 1:
        cart.product_quantity -= 1
    else:
        # cart = ShoppingCart(
        #     user_id=current_user.id,
        #     product_id=product_id,
        #     product_quantity=1,
        # )
        db.session.delete(cart)
    db.session.commit()
    return redirect(request.referrer or url_for("home"))


@app.route('/cart', methods=["POST", "GET"])
@login_required
def show_cart():
    my_cart = ShoppingCart.query.filter_by(user_id=current_user.id).all()
    products = ShopProduct.query.all()
    total_price = 0
    for cart in my_cart:
        for product in products:
            if product.id == cart.product_id:
                total_price += (cart.product_quantity * product.price)
    print(total_price)
    return render_template("cart.html", my_cart=my_cart, products=products, total=total_price)



if __name__ == "__main__":
    app.run(debug=True)
