from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField, DateTimeField, FloatField, URLField
from wtforms.validators import DataRequired, URL, EqualTo, Length, Regexp
# from flask_ckeditor import CKEditorField


class LoginUserForm(FlaskForm):
    email = EmailField("Enter Your Email", validators=[DataRequired()])
    password = PasswordField("Enter Your Password", validators=[DataRequired(),
                                                                Length(min=8,
                                                                       message="Password must be at least 8 characters"),
                                                                Regexp(r'^(?=.*?[A-Z])(?=.*?[^\w\s])',
                                                                       message="Password must contain at least one uppercase letter and one symbol")
                                                                ])
    submit = SubmitField("Login")

class RegisterUserForm(FlaskForm):
    email = EmailField("Enter Your Email", validators=[DataRequired()])
    password = PasswordField("Enter Your Password", validators=[DataRequired(),
                                                                EqualTo('confirm', message='Passwords must match'),
                                                                Length(min=8, message="Password must be at least 8 characters"),
                                                                Regexp(r'^(?=.*?[A-Z])(?=.*?[^\w\s])', message="Password must contain at least one uppercase letter and one symbol")
                                                                ])
    confirm = PasswordField('Repeat Password', validators=[DataRequired()])
    name = StringField("Enter Your Name", validators=[DataRequired()])
    submit = SubmitField("Create New User")


class AddProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    description = StringField("Product Description", validators=[DataRequired()])
    # upload_date = DateTimeField("Uploaded Date", validators=[DataRequired()])
    stock = IntegerField("How Many Stocks Does You Have ?", validators=[DataRequired()])
    price = FloatField("Product Price", validators=[DataRequired()])
    img_url = URLField("Image Link URL", validators=[DataRequired()])
    submit = SubmitField("Add New Product")