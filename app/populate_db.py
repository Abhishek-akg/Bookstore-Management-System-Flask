import os
import sys
from datetime import datetime

# Adding the project directory to the sys.path to ensure correct module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Book, Cart, CartItem, Order, OrderItem, Post

app = create_app()

def populate_db():
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()

        # Create some users
        user1 = User(username='admin', email='admin@example.com', is_admin=True)
        user1.set_password('adminpassword')
        
        user2 = User(username='user1', email='user1@example.com')
        user2.set_password('user1password')
        
        user3 = User(username='user2', email='user2@example.com')
        user3.set_password('user2password')
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)

        # Commit the users to ensure they are assigned IDs
        db.session.commit()

        # Create some books
        book1 = Book(title='Flask Web Development', author='Miguel Grinberg', category='Programming', price=29.99, quantity_in_stock=10)
        book2 = Book(title='Python Crash Course', author='Eric Matthes', category='Programming', price=39.99, quantity_in_stock=5)
        book3 = Book(title='The Pragmatic Programmer', author='Andrew Hunt', category='Programming', price=49.99, quantity_in_stock=8)
        
        db.session.add(book1)
        db.session.add(book2)
        db.session.add(book3)

        # Create some carts
        cart1 = Cart(owner=user2)
        cart2 = Cart(owner=user3)
        
        db.session.add(cart1)
        db.session.add(cart2)

        # Create some cart items
        cart_item1 = CartItem(cart=cart1, book=book1, quantity=1)
        cart_item2 = CartItem(cart=cart1, book=book2, quantity=2)
        cart_item3 = CartItem(cart=cart2, book=book3, quantity=1)
        
        db.session.add(cart_item1)
        db.session.add(cart_item2)
        db.session.add(cart_item3)

        # Create some orders
        order1 = Order(customer=user2, total_price=69.98)
        order2 = Order(customer=user3, total_price=49.99)
        
        db.session.add(order1)
        db.session.add(order2)

        # Create some order items
        order_item1 = OrderItem(order=order1, book=book1, quantity=1)
        order_item2 = OrderItem(order=order1, book=book2, quantity=2)
        order_item3 = OrderItem(order=order2, book=book3, quantity=1)
        
        db.session.add(order_item1)
        db.session.add(order_item2)
        db.session.add(order_item3)

        # Create some posts
        post1 = Post(title='Welcome to the Bookstore', content='This is the first post in the bookstore application.', user_id=user1.id)
        post2 = Post(title='Flask Tips and Tricks', content='Here are some useful tips and tricks for using Flask.', user_id=user2.id)

        db.session.add(post1)
        db.session.add(post2)

        # Commit the changes
        db.session.commit()
        print("Database populated with initial data.")

if __name__ == "__main__":
    populate_db()
