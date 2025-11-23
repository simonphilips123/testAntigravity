import streamlit as st
import pandas as pd
import uuid

class Product:
    def __init__(self, name, price, image, description, category,
                 rating=4.5, review_count=0, reviews=None,
                 variants=None, stock=50, discount=0,
                 recommendations=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.price = price
        self.original_price = price / (1 - discount) if discount > 0 else price
        self.discount = discount
        self.image = image
        self.description = description
        self.category = category
        self.rating = rating
        self.review_count = review_count
        self.reviews = reviews or []
        self.variants = variants or {"sizes": ["S", "M", "L", "XL"], "colors": ["White", "Black", "Grey"]}
        self.stock = stock
        self.recommendations = recommendations or []

def get_products():
    products = [
        Product("Men's Cotton Brief - White", 1999.00, "assets/products/1.png",
                "Premium cotton brief with elastic waistband. Comfortable all-day wear.", "Briefs",
                rating=4.5, review_count=234, stock=45, discount=0.1,
                reviews=[
                    {"user": "Raj K.", "rating": 5, "comment": "Perfect fit and great quality!"},
                    {"user": "Priya S.", "rating": 4, "comment": "Good product, value for money."}
                ]),
        Product("Men's Boxer Shorts - Multicolor", 1199.00, "assets/products/2.png",
                "Breathable fabric boxer shorts for daily wear. Pack of 3.", "Boxers",
                rating=4.7, review_count=456, stock=12, discount=0.15,
                reviews=[
                    {"user": "Amit P.", "rating": 5, "comment": "Most comfortable boxers ever!"},
                    {"user": "Vikram M.", "rating": 5, "comment": "Highly recommended!"}
                ]),
        Product("Men's Trunk Underwear - Black", 2499.00, "assets/products/3.png",
                "Premium trunk style underwear with superior fit and comfort.", "Trunks",
                rating=4.8, review_count=189, stock=8, discount=0.2,
                reviews=[
                    {"user": "Neha R.", "rating": 5, "comment": "Excellent quality!"},
                    {"user": "Karan J.", "rating": 4, "comment": "Worth the price."}
                ]),
        Product("Men's Athletic Briefs - Grey", 1499.00, "assets/products/4.png",
                "High performance moisture wicking athletic briefs for sports.", "Briefs",
                rating=4.6, review_count=312, stock=25, discount=0,
                reviews=[
                    {"user": "Rohit S.", "rating": 5, "comment": "Great for workouts!"},
                    {"user": "Arjun K.", "rating": 4, "comment": "Good quality material."}
                ]),
        Product("Men's Cotton Vests - White (Pack of 3)", 999.00, "assets/products/5.png",
                "Soft cotton vests for everyday comfort. Pack of 3.", "Vests",
                rating=4.4, review_count=567, stock=100, discount=0.05,
                reviews=[
                    {"user": "Sneha D.", "rating": 4, "comment": "Very comfortable!"},
                    {"user": "Rahul T.", "rating": 5, "comment": "Great value pack!"}
                ]),
    ]

    # Set up recommendations (circular references)
    products[0].recommendations = [products[1].id, products[3].id, products[4].id]
    products[1].recommendations = [products[0].id, products[3].id, products[4].id]
    products[2].recommendations = [products[0].id, products[1].id, products[4].id]
    products[3].recommendations = [products[0].id, products[1].id, products[4].id]
    products[4].recommendations = [products[0].id, products[1].id, products[3].id]

    return products

def init_session_state():
    if 'cart' not in st.session_state or isinstance(st.session_state.cart, list):
        st.session_state.cart = {} # Initialize as dict or reset if list
    if 'products' not in st.session_state:
        st.session_state.products = get_products()
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'wishlist' not in st.session_state:
        st.session_state.wishlist = {}
    if 'recently_viewed' not in st.session_state:
        st.session_state.recently_viewed = []
    if 'comparison' not in st.session_state:
        st.session_state.comparison = []
    if 'shipping_addresses' not in st.session_state:
        st.session_state.shipping_addresses = []
    if 'payment_methods' not in st.session_state:
        st.session_state.payment_methods = [
            {"type": "Credit Card", "details": "****1234"},
            {"type": "UPI", "details": "user@upi"},
            {"type": "Cash on Delivery", "details": "Pay when you receive"}
        ]
    if 'selected_address' not in st.session_state:
        st.session_state.selected_address = None
    if 'selected_payment' not in st.session_state:
        st.session_state.selected_payment = None

def login_user_mock():
    st.session_state.user = {"name": "Simon P.", "email": "simon@gmail.com"}

def logout_user():
    st.session_state.user = None

def add_to_cart(product):
    if product.id in st.session_state.cart:
        st.session_state.cart[product.id]['quantity'] += 1
    else:
        st.session_state.cart[product.id] = {'product': product, 'quantity': 1}

def remove_from_cart(product_id):
    if product_id in st.session_state.cart:
        del st.session_state.cart[product_id]
        st.rerun()

def get_cart_total():
    return sum(item['product'].price * item['quantity'] for item in st.session_state.cart.values())
