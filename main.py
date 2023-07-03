from flask import Flask, render_template, redirect, url_for, flash, abort
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
    # author = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)
    upload_date = db.Column(db.String(250), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('shop_products', lazy=True))
    # author_id = db.Column(db.Integer, ForeignKey('user.id'))
    # author = relationship("User", back_populates="blogpost")
    # comments = relationship("Comment", back_populates="post_comment")


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    name = db.Column(db.String(1000))
    # cart = relationship("ShopProduct", backref=backref("user", lazy=True))
    # products = relationship("ShopProduct", backref=backref("user", lazy=True))
    # comments = relationship("Comment", back_populates="comment_author")

def get_id(self):
    return str(self.id)

#Line below only required once, when creating DB.
# with app.app_context():
#     sql_text = text('ALTER TABLE "ShopProducts" ADD COLUMN user_id INTEGER')
#     db.session.execute(sql_text)
#     db.session.commit()
# #     db.create_all()
#     db.session.commit()



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
    print(all_product)
    return render_template("index.html", products=all_product)

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



if __name__ == "__main__":
    app.run(debug=True)