from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class FilterForm(FlaskForm):
    category = SelectField('Category', choices=[])
    min_price = DecimalField('Min Price', places=2)
    max_price = DecimalField('Max Price', places=2)
    submit = SubmitField('Filter')

class AddBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    quantity_in_stock = IntegerField('Quantity in Stock', validators=[DataRequired()])
    submit = SubmitField('Add Book')

class EditBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    quantity_in_stock = IntegerField('Quantity in Stock', validators=[DataRequired()])
    submit = SubmitField('Update Book')
