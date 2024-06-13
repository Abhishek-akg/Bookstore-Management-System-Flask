from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db, bcrypt
from app.forms import LoginForm, RegistrationForm, SearchForm, FilterForm, AddBookForm, EditBookForm
from app.models import User, Book, Cart, CartItem, Order, OrderItem
import re

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/browse_books', methods=['GET', 'POST'])
def browse_books():
    search_form = SearchForm()
    filter_form = FilterForm()
    filter_form.category.choices = [(c.category, c.category) for c in Book.query.distinct(Book.category)]
    books = Book.query.all()
    
    if search_form.validate_on_submit():
        search_term = search_form.search.data
        regex = re.compile(f".*{re.escape(search_term)}.*", re.IGNORECASE)
        books = Book.query.filter(
            (Book.title.op('REGEXP')(regex.pattern)) | 
            (Book.author.op('REGEXP')(regex.pattern)) | 
            (Book.category.op('REGEXP')(regex.pattern))
        ).all()
    
    if filter_form.validate_on_submit():
        min_price = filter_form.min_price.data
        max_price = filter_form.max_price.data
        category = filter_form.category.data
        books = Book.query
        if category:
            books = books.filter_by(category=category)
        if min_price is not None:
            books = books.filter(Book.price >= min_price)
        if max_price is not None:
            books = books.filter(Book.price <= max_price)
        books = books.all()
    
    return render_template('browse_books.html', books=books, search_form=search_form, filter_form=filter_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Register', form=form)

@app.route('/cart')
@login_required
def view_cart():
    cart = current_user.cart
    items = cart.items if cart else []
    return render_template('view_cart.html', items=items)

@app.route('/add_to_cart/<int:book_id>')
@login_required
def add_to_cart(book_id):
    cart = current_user.cart
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    cart_item = CartItem.query.filter_by(cart_id=cart.id, book_id=book_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(cart_id=cart.id, book_id=book_id, quantity=1)
        db.session.add(cart_item)
    db.session.commit()
    flash('Book added to cart')
    return redirect(url_for('browse_books'))

@app.route('/checkout')
@login_required
def checkout():
    cart = current_user.cart
    if not cart or not cart.items:
        flash('Your cart is empty')
        return redirect(url_for('browse_books'))
    total_price = sum(item.book.price * item.quantity for item in cart.items)
    order = Order(user_id=current_user.id, total_price=total_price)
    db.session.add(order)
    db.session.commit()
    for item in cart.items:
        order_item = OrderItem(order_id=order.id, book_id=item.book_id, quantity=item.quantity)
        item.book.quantity_in_stock -= item.quantity
        db.session.add(order_item)
        db.session.delete(item)
    db.session.commit()
    flash('Order placed successfully')
    return redirect(url_for('home'))

@app.route('/admin/manage_inventory', methods=['GET', 'POST'])
@login_required
def manage_inventory():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('home'))
    add_book_form = AddBookForm()
    if add_book_form.validate_on_submit():
        book = Book(title=add_book_form.title.data, author=add_book_form.author.data,
                    category=add_book_form.category.data, price=add_book_form.price.data,
                    quantity_in_stock=add_book_form.quantity_in_stock.data)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully')
        return redirect(url_for('manage_inventory'))
    books = Book.query.all()
    return render_template('manage_inventory.html', books=books, add_book_form=add_book_form)

@app.route('/admin/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('home'))
    book = Book.query.get_or_404(book_id)
    form = EditBookForm(obj=book)
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.category = form.category.data
        book.price = form.price.data
        book.quantity_in_stock = form.quantity_in_stock.data
        db.session.commit()
        flash('Book updated successfully')
        return redirect(url_for('manage_inventory'))
    return render_template('edit_book.html', form=form, book=book)

@app.route('/admin/delete_book/<int:book_id>')
@login_required
def delete_book(book_id):
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('home'))
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully')
    return redirect(url_for('manage_inventory'))

@app.route('/admin/sales_report')
@login_required
def sales_report():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('home'))
    orders = Order.query.all()
    return render_template('sales_report.html', orders=orders)

@app.route('/admin/inventory_report')
@login_required
def inventory_report():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('home'))
    books = Book.query.all()
    return render_template('inventory_report.html', books=books)

@app.route('/admin/user_activity_report')
@login_required
def user_activity_report():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('user_activity_report.html', users=users)
