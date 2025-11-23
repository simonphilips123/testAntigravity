import streamlit as st
from utils.data import init_session_state, add_to_cart, get_cart_total, login_user_mock, logout_user, remove_from_cart
from utils.auth import GoogleAuth
import os

# Page Config
st.set_page_config(page_title="Adams Inners", layout="wide", page_icon="🛍️")


import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .torn-paper-top {
        width: 100%;
        height: 50px;
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        margin-bottom: -10px;
        z-index: 10;
        position: relative;
    }

    .torn-paper-bottom {
        width: 100%;
        height: 50px;
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        margin-top: -10px;
        z-index: 10;
        position: relative;
    }
    </style>
    ''' % (get_base64_of_bin_file("assets/torn_paper_top.png"), get_base64_of_bin_file("assets/torn_paper_bottom.png"))
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amazon+Ember:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Arial', sans-serif; /* Fallback to Arial as Amazon does */
    }

    .stApp {
        background-color: #EAEDED;
    }

    /* Header */
    .amazon-header {
        background-color: #131921;
        color: white;
        padding: 10px 20px;
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }

    .amazon-logo {
        font-size: 24px;
        font-weight: bold;
        margin-right: 30px;
    }

    /* Search Bar */
    .search-container {
        flex-grow: 1;
        display: flex;
        margin: 0 20px;
    }

    .search-input {
        width: 100%;
        padding: 10px;
        border-radius: 4px 0 0 4px;
        border: none;
    }

    .search-btn {
        background-color: #febd69;
        border: none;
        padding: 10px 20px;
        border-radius: 0 4px 4px 0;
        cursor: pointer;
    }

    /* Product Card */
    .product-card {
        background: white;
        border: 1px solid #ddd;
        padding: 20px;
        height: 100%;
        display: flex;
        flex-direction: column;
    }

    .product-title {
        font-size: 16px;
        font-weight: 500;
        color: #0F1111;
        line-height: 1.3em;
        max-height: 2.6em;
        overflow: hidden;
        margin-bottom: 5px;
    }

    .product-price {
        font-size: 28px;
        color: #0F1111;
        font-weight: 500;
    }

    .product-price sup {
        font-size: 13px;
        top: -0.75em;
    }

    .prime-badge {
        color: #00a8e1;
        font-weight: bold;
        font-style: italic;
        margin-bottom: 10px;
    }

    .add-to-cart-btn {
        background-color: #FFD814;
        border: 1px solid #FCD200;
        border-radius: 20px;
        padding: 8px 20px;
        width: 100%;
        cursor: pointer;
        font-size: 13px;
        margin-top: auto;
    }

    .add-to-cart-btn:hover {
        background-color: #F7CA00;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# Initialize State
init_session_state()

# Handle Mock Login Callback
if "mock_login" in st.query_params:
    with st.spinner("Connecting to Google..."):
        import time
        time.sleep(1.0)
        login_user_mock()
        st.query_params.clear()
        st.session_state.page = "Home"
        st.rerun()

# Handle Navigation Callback
if "nav" in st.query_params:
    page = st.query_params["nav"]
    if page == "account":
        st.session_state.page = "Account"
    st.query_params.clear()
    st.rerun()

# Handle OAuth Callback
if "code" in st.query_params:
    google_auth = GoogleAuth()
    code = st.query_params["code"]
    user_info = google_auth.get_user_info(code)
    if user_info:
        st.session_state.user = user_info
        st.query_params.clear() # Clear code from URL
        st.session_state.page = "Home"
        st.rerun()

# Helper for base64 images
def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        print(f"Error loading image {file_path}: {e}")
        return ""

# Amazon Header (Interactive)
# Logo at the top, full width
st.markdown(f"""
    <a href="?nav=Home" target="_self">
        <img src="data:image/jpeg;base64,{get_img_as_base64('assets/products/logo.jpg')}" style="width: 100%; object-fit: cover;">
    </a>
    """, unsafe_allow_html=True)

# Header columns (Search, Account, Returns, Cart) - Removed the first column for logo
header_cols = st.columns([4, 1.5, 1.2, 0.8, 1])

with header_cols[0]:
    st.text_input("Search", label_visibility="collapsed", placeholder="Search Adams Inners")

with header_cols[1]:
    if st.session_state.user:
        user_name = st.session_state.user['name'].split()[0]
        btn_text = f"Hello, {user_name}\nAccount & Lists"
        if st.button(btn_text, key="nav_account"):
            st.session_state.page = "Account" # New Account page
            st.rerun()
    else:
        if st.button("Hello, Sign in\nAccount & Lists", key="nav_account"):
            st.session_state.page = "Login"
            st.rerun()

with header_cols[2]:
    if st.button("Returns\n& Orders", key="nav_orders"):
        st.info("Orders feature coming soon!")

with header_cols[3]:
    # Google Sign In (Icon only or small button)
    if not st.session_state.user:
        google_auth = GoogleAuth()
        auth_url = google_auth.get_auth_url()

        # Use mock if no auth_url (secrets missing)
        if not auth_url:
            target_url = "?mock_login=true"
            tooltip = "Sign in with Google (Mock)"
        else:
            target_url = auth_url
            tooltip = "Sign in with Google"

        st.markdown(f'''
            <a href="{target_url}" target="_self" style="text-decoration: none;">
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; padding-top: 5px;">
                    <img src="https://www.svgrepo.com/show/475656/google-color.svg" style="width: 30px; height: 30px; cursor: pointer;" title="{tooltip}">
                </div>
            </a>
        ''', unsafe_allow_html=True)
    else:
         # Show a small avatar or placeholder if logged in
         # We use a query param 'nav=account' to trigger navigation
         st.markdown(f'''
            <a href="?nav=account" target="_self" style="text-decoration: none;">
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; padding-top: 5px;">
                    <div style="width: 30px; height: 30px; background-color: #00a8e1; border-radius: 50%; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; cursor: pointer;" title="Go to Account">
                        {st.session_state.user['name'][0]}
                    </div>
                </div>
            </a>
        ''', unsafe_allow_html=True)

with header_cols[4]:
    cart_count = sum(item['quantity'] for item in st.session_state.cart.values())
    if st.button(f"🛒 Cart ({cart_count})", key="nav_cart"):
        st.session_state.page = "Cart"
        st.rerun()

st.markdown("""
<style>
    /* Style the header buttons to look like the dark navbar */
    div[data-testid="column"]:has(button[key^="nav_"]) button {
        background-color: #131921;
        color: white;
        border: none;
        height: 100%;
        width: 100%;
        text-align: left;
        padding: 10px;
    }

    div[data-testid="column"]:has(button[key^="nav_"]) button:hover {
        background-color: #232f3e;
        color: #febd69;
        border: 1px solid white;
    }

    /* Adjust the search bar alignment */
    div[data-testid="column"] .stTextInput {
        margin-top: 5px;
    }

    /* Hide the default Streamlit header decoration if possible or blend it */
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Ensure page defaults to Home if not set
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = "All"

# Category Navigation Menu
categories = ["All", "Briefs", "Boxers", "Trunks", "Vests"]
cat_cols = st.columns(len(categories))
for idx, category in enumerate(categories):
    with cat_cols[idx]:
        if st.button(category, key=f"cat_{category}", use_container_width=True):
            st.session_state.selected_category = category
            st.rerun()

st.markdown("""
<style>
    div[data-testid="column"]:has(button[key^="cat_"]) button {
        background-color: #232f3e;
        color: white;
        border: 1px solid #3a4553;
        padding: 10px;
        font-weight: 500;
    }
    div[data-testid="column"]:has(button[key^="cat_"]) button:hover {
        background-color: #374151;
        border-color: #febd69;
    }
</style>
""", unsafe_allow_html=True)

# Navigation (Sidebar)
with st.sidebar:
    st.title("Departments")
    # Sync radio with session state
    pages = ["Home", "Shop", "Cart", "Wishlist", "Comparison", "Admin"]
    page = st.radio("Navigate", pages, index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)

    # Update session state if radio changes
    if page != st.session_state.page:
        st.session_state.page = page
        st.rerun()

    st.markdown("---")
    st.markdown("### Filter by Price")
    max_price = st.slider("Max Price", 0, 10000, 10000)

if st.session_state.page == "Home" or st.session_state.page == "Shop":
    # Promotional Banner (using torn paper asset as a stylistic choice)
    st.image("assets/torn_paper_top.png", use_column_width=True)

    st.markdown("## Recommended for you")

    # Filter by category and price
    products = [p for p in st.session_state.products if p.price <= max_price]
    if st.session_state.selected_category != "All":
        products = [p for p in products if p.category == st.session_state.selected_category]

    # Grid Layout
    cols = st.columns(4)
    for idx, product in enumerate(products):
        with cols[idx % 4]:
            # Load image as base64
            if product.image.startswith("http"):
                img_src = product.image
            else:
                img_b64 = get_img_as_base64(product.image)
                img_src = f"data:image/png;base64,{img_b64}"

            # Price formatting
            price_whole = int(product.price)
            price_fraction = int((product.price - price_whole) * 100)

            # Original price if discount exists
            original_price_html = ""
            discount_badge = ""
            if product.discount > 0:
                orig_whole = int(product.original_price)
                orig_fraction = int((product.original_price - orig_whole) * 100)
                original_price_html = f'<div style="font-size: 12px; color: #565959; text-decoration: line-through;">₹{orig_whole}.{orig_fraction:02d}</div>'
                discount_badge = f'<div style="background-color: #CC0C39; color: white; padding: 2px 6px; display: inline-block; font-size: 11px; font-weight: bold; margin-bottom: 5px;">{int(product.discount*100)}% OFF</div>'

            # Star rating
            stars = "★" * int(product.rating) + "☆" * (5 - int(product.rating))
            rating_html = f'<div style="color: #FFA41C; font-size: 14px; margin-bottom: 3px;">{stars} <span style="color: #007185; font-size: 12px;">({product.review_count})</span></div>'

            # Stock indicator
            stock_html = ""
            if product.stock < 20:
                stock_html = f'<div style="font-size: 12px; color: #B12704; margin-bottom: 5px;">Only {product.stock} left in stock</div>'
            else:
                stock_html = '<div style="font-size: 12px; color: #007600; margin-bottom: 5px;">In Stock</div>'

            # Wishlist heart icon
            in_wishlist = product.id in st.session_state.wishlist
            heart_icon = "❤️" if in_wishlist else "🤍"

            st.markdown(f"""
            <div class="product-card">
                <div style="text-align: right; margin-bottom: -20px; font-size: 20px; cursor: pointer;" id="wishlist_{product.id}">
                    {heart_icon}
                </div>
                <div style="text-align: center; margin-bottom: 10px;">
                    <img src="{img_src}" style="max-width: 100%; max-height: 200px;">
                </div>
                {discount_badge}
                <div class="product-title">{product.name}</div>
                <div style="font-size: 12px; color: #565959; margin-bottom: 5px;">{product.category}</div>
                {rating_html}
                <div class="product-price">
                    <span style="font-size: 13px; vertical-align: top;">₹</span>{price_whole}<sup style="font-size: 13px;">{price_fraction:02d}</sup>
                </div>
                {original_price_html}
                <div class="prime-badge">✓prime</div>
                {stock_html}
                <p style="font-size: 12px; color: #565959; line-height: 1.2em; height: 2.4em; overflow: hidden;">{product.description}</p>
            </div>
            """, unsafe_allow_html=True)

            # Buttons row
            btn_cols = st.columns([3, 1])
            with btn_cols[0]:
                # Check if product is in cart and show quantity
                cart_qty = st.session_state.cart.get(product.id, {}).get('quantity', 0)
                button_text = f"Add to Cart ({cart_qty})" if cart_qty > 0 else "Add to Cart"
                if st.button(button_text, key=product.id):
                    add_to_cart(product)
            with btn_cols[1]:
                if st.button(heart_icon, key=f"wish_{product.id}"):
                    if product.id in st.session_state.wishlist:
                        del st.session_state.wishlist[product.id]
                    else:
                        st.session_state.wishlist[product.id] = product
                    st.rerun()


elif st.session_state.page == "Wishlist":
    st.title("My Wishlist")

    if not st.session_state.wishlist:
        st.info("Your wishlist is empty. Start adding items you love!")
    else:
        st.markdown(f"### {len(st.session_state.wishlist)} items in your wishlist")

        cols = st.columns(4)
        for idx, (product_id, product) in enumerate(st.session_state.wishlist.items()):
            with cols[idx % 4]:
                if product.image.startswith("http"):
                    img_src = product.image
                else:
                    img_b64 = get_img_as_base64(product.image)
                    img_src = f"data:image/png;base64,{img_b64}"

                st.markdown(f"""
                <div class="product-card">
                    <div style="text-align: center; margin-bottom: 10px;">
                        <img src="{img_src}" style="max-width: 100%; max-height: 150px;">
                    </div>
                    <div class="product-title">{product.name}</div>
                    <div class="product-price">₹{product.price:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

                btn_cols = st.columns(2)
                with btn_cols[0]:
                    if st.button("Add to Cart", key=f"wish_cart_{product.id}"):
                        add_to_cart(product)
                with btn_cols[1]:
                    if st.button("Remove", key=f"wish_remove_{product.id}"):
                        del st.session_state.wishlist[product.id]
                        st.rerun()

elif st.session_state.page == "Comparison":
    st.title("Product Comparison")

    if len(st.session_state.comparison) < 2:
        st.info("Add at least 2 products to compare. Use the comparison checkbox on product cards.")
    else:
        st.markdown(f"### Comparing {len(st.session_state.comparison)} products")

        # Create comparison table
        comparison_data = {
            "Product": [],
            "Price": [],
            "Rating": [],
            "Reviews": [],
            "Stock": [],
            "Discount": []
        }

        for product_id in st.session_state.comparison:
            product = next((p for p in st.session_state.products if p.id == product_id), None)
            if product:
                comparison_data["Product"].append(product.name)
                comparison_data["Price"].append(f"₹{product.price:.2f}")
                comparison_data["Rating"].append(f"{product.rating}★")
                comparison_data["Reviews"].append(product.review_count)
                comparison_data["Stock"].append(product.stock)
                comparison_data["Discount"].append(f"{int(product.discount*100)}%" if product.discount > 0 else "No discount")

        st.table(comparison_data)

        if st.button("Clear Comparison"):
            st.session_state.comparison = []
            st.rerun()

elif st.session_state.page == "Cart":
    st.title("Shopping Cart")

    if not st.session_state.cart:
        st.info("Your cart is empty.")
    else:
        # Cart items
        for product_id, item in st.session_state.cart.items():
            product = item['product']
            quantity = item['quantity']

            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    if product.image.startswith("http"):
                        st.image(product.image, width=100)
                    else:
                        img_b64 = get_img_as_base64(product.image)
                        st.markdown(f'<img src="data:image/png;base64,{img_b64}" width="100">', unsafe_allow_html=True)
                with col2:
                    st.subheader(product.name)
                    st.write(f"In Stock - {product.stock} available")
                    st.write("Eligible for FREE Shipping & FREE Returns")
                    st.markdown(f"**₹{product.price:.2f}**")
                    st.write(f"**Quantity: {quantity}**")

                    if st.button("Delete", key=f"del_{product.id}"):
                        remove_from_cart(product.id)
                st.markdown("---")

        # Checkout Section
        st.markdown("## Checkout")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Shipping Address
            st.markdown("### Shipping Address")
            if st.session_state.shipping_addresses:
                address_options = [f"{addr['name']} - {addr['address']}" for addr in st.session_state.shipping_addresses]
                selected_addr = st.selectbox("Select Address", address_options)
                st.session_state.selected_address = selected_addr
            else:
                st.info("No saved addresses. Add one below:")

            with st.expander("Add New Address"):
                new_name = st.text_input("Name")
                new_address = st.text_area("Address")
                new_city = st.text_input("City")
                new_pin = st.text_input("PIN Code")
                if st.button("Save Address"):
                    st.session_state.shipping_addresses.append({
                        "name": new_name,
                        "address": f"{new_address}, {new_city} - {new_pin}"
                    })
                    st.success("Address saved!")
                    st.rerun()

            # Payment Method
            st.markdown("### Payment Method")
            payment_options = [f"{pm['type']} - {pm['details']}" for pm in st.session_state.payment_methods]
            selected_payment = st.selectbox("Select Payment Method", payment_options)
            st.session_state.selected_payment = selected_payment

        with col2:
            # Order Summary
            st.markdown("### Order Summary")

            subtotal = get_cart_total()
            tax = subtotal * 0.18  # 18% GST
            shipping = 0 if subtotal > 500 else 40  # Free shipping over ₹500
            total = subtotal + tax + shipping

            st.markdown(f"""
            <div style="background-color: white; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span>Subtotal:</span>
                    <span>₹{subtotal:.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span>Tax (18% GST):</span>
                    <span>₹{tax:.2f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span>Shipping:</span>
                    <span>{"FREE" if shipping == 0 else f"₹{shipping:.2f}"}</span>
                </div>
                <hr>
                <div style="display: flex; justify-content: space-between; font-size: 18px; font-weight: bold;">
                    <span>Total:</span>
                    <span>₹{total:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Estimated Delivery
            from datetime import datetime, timedelta
            delivery_date = (datetime.now() + timedelta(days=5)).strftime("%B %d, %Y")
            st.markdown(f"**Estimated Delivery:** {delivery_date}")
            st.markdown("*(3-5 business days)*")

            st.markdown("---")

            if st.button("Proceed to Checkout", use_container_width=True, type="primary"):
                if not st.session_state.selected_address:
                    st.error("Please select a shipping address")
                elif not st.session_state.selected_payment:
                    st.error("Please select a payment method")
                else:
                    st.success("Order placed successfully! 🎉")
                    st.balloons()
                    # Clear cart after order
                    # st.session_state.cart = {}
                    # st.rerun()

elif st.session_state.page == "Admin":
    st.title("Seller Central")
    st.dataframe(pd.DataFrame([vars(p) for p in st.session_state.products]))

elif st.session_state.page == "Login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background-color: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;">
            <h2 style="margin-bottom: 20px;">Sign in</h2>
            <p style="margin-bottom: 30px;">to continue to Adams Inners</p>
        </div>
        """, unsafe_allow_html=True)

        # Real Google Auth
        google_auth = GoogleAuth()
        auth_url = google_auth.get_auth_url()

        # Button Style
        google_btn_style = """
        width: 100%;
        background-color: white;
        color: #444;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-family: Roboto, sans-serif;
        font-weight: 500;
        """

        if auth_url:
            # Real Auth Button
            st.markdown(f'''
                <a href="{auth_url}" target="_self" style="text-decoration: none;">
                    <button style="{google_btn_style}">
                        <img src="https://www.svgrepo.com/show/475656/google-color.svg" style="width: 20px; margin-right: 10px;">
                        Sign in with Google
                    </button>
                </a>
            ''', unsafe_allow_html=True)
        else:
            # Mock Auth Button (looks the same)
            st.markdown(f'''
                <a href="?mock_login=true" target="_self" style="text-decoration: none;">
                    <button style="{google_btn_style}">
                        <img src="https://www.svgrepo.com/show/475656/google-color.svg" style="width: 20px; margin-right: 10px;">
                        Sign in with Google
                    </button>
                </a>
            ''', unsafe_allow_html=True)
            if not auth_url:
                st.info("⚠️ Running in Mock Mode (No secrets found)")

elif st.session_state.page == "Account":
    st.title("Your Account")
    if st.session_state.user:
        st.write(f"**Name:** {st.session_state.user['name']}")
        st.write(f"**Email:** {st.session_state.user['email']}")

        if st.button("Sign Out"):
            logout_user()
            st.session_state.page = "Home"
            st.rerun()
    else:
        st.error("You are not signed in.")

# Footer
st.markdown("""
<div style="background-color: #232F3E; color: white; padding: 40px; text-align: center; margin-top: 50px;">
    <div style="margin-bottom: 20px;">Back to top</div>
    <div style="font-size: 12px;">© 1996-2025, Adams Inners, Inc. or its affiliates</div>
</div>
""", unsafe_allow_html=True)
