# 🛏️ **E-Commerce Platform Documentation**  

## 📚 **Table of Contents**
1.  [Project Overview](#project-overview)  
2.  [Features Implemented](#features-implemented)  
3.  [Technical Stack](#technical-stack)  
4.  [Folder Structure](#folder-structure)  
5.  [Installation and Setup](#installation-and-setup)  
6.  [App Overview](#app-overview)  
7.  [Models and Database Structure](#models-and-database-structure)  
8.  [API and URL Endpoints](#api-and-url-endpoints)  
9.  [Authentication and Authorization](#authentication-and-authorization)  
10. [Payment Integration](#payment-integration)  
11. [Testing](#testing)  
12. [To-Do and Future Enhancements](#to-do-and-future-enhancements)  

---

## 💄 **1. Project Overview**

The **E-Commerce Platform** is a web application built using Django to facilitate the sale of travel-related items. Users can browse products, add them to the cart, apply coupons, and place orders with Razorpay payment integration. The project includes a user interface for customers and an admin panel for managing products, orders, users, and offers.

---

## 🎯 **2. Features Implemented**

### ✅ **User Side**
- User Registration with Email OTP Verification  
- User Login/Logout with Session Management  
- Profile and Address Management  
- Wishlist (Add/Remove Items)  
- Add/Remove Items to/from Cart  
- Apply/Remove Coupons  
- Checkout and Order Placement  
- Order History and Order Status Updates  
- Payment Integration with Razorpay  
- Return and Cancel Orders  
- Wallet for Refunds on Canceled Orders 
- Search , category filtering
- added blogs to enhance user experience and engagement 

### ✅ **Admin Panel**
- Manage Users, Products, Categories, and Brands  
- Add/Edit/Delete Product Variants  
- Coupon Management  
- Offer Module (Category/Product/Referral Offers)  
- View and Filter Orders  

---

## 🛠️ **3. Technical Stack**

### 📚 **Backend**
- Python 3.11  
- Django 4.x    
- Razorpay for Payment Gateway  

### 🎨 **Frontend**
- HTML5, CSS3, JavaScript  
- Bootstrap (for UI enhancements)  

### 📉 **Database**
- PostgreSQL

---

## 📂 **4. Folder Structure**

```
/ecommerce_project/
├── /accounts/                  # User authentication and profile management
├── /admin_panel/               # Admin functionalities and management
├── /cart/                      # Cart and wishlist functionality
├── /coupons/                   # Coupons and discount module
├── /orders/                    # Order management and Razorpay integration
├── /store/                     # Product listing, category, and search
├── /templates/                 # HTML templates for user/admin interfaces
├── /static/                    # CSS, JS, and images
├── /media/                     # Uploaded product images
├── /ecommerce_project/         # Core settings and URLs
└── manage.py                   # Django project management script
```

---

## 🚀 **5. Installation and Setup**

### 👥 **Step 1: Clone the Repository**
```bash
git clone https://github.com/username/ecommerce_project.git
cd ecommerce_project
```

---

### ⚙️ **Step 2: Create and Activate Virtual Environment**
```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# On Windows
env\Scripts\activate

# On Linux/Mac
source env/bin/activate
```

---

### 🛆 **Step 3: Install Required Packages**
```bash
pip install -r requirements.txt
```

---

### 🛄 **Step 4: Configure Database**
- Open `ecommerce_project/settings.py` and update the database settings as needed.  
- Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 👤 **Step 5: Create Superuser for Admin Panel**
```bash
python manage.py createsuperuser
```

---

### ▶️ **Step 6: Run the Development Server**
```bash
python manage.py runserver
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to access the application.

---

## 📺 **6. App Overview**

### 📌 **1. `accounts` App**
- User registration with OTP verification  
- Login/Logout functionality  
- Address and profile management  

---

### 📌 **2. `admin_panel` App**
- Admin management of users, products, and orders  
- Coupon and offer management  

---

### 📌 **3. `store` App**
- Product listing, category filtering, and search  
- Product detail view  

---

### 📌 **4. `cart` App**
- Add, update, and remove items from the cart  
- Wishlist management  

---

### 📌 **5. `orders` App**
- Order placement and tracking  
- Razorpay payment gateway integration  
- Return and cancel order options  

---

### 📌 **6. `coupons` App**
- Coupon management and application  
- Discount handling during checkout  

---

## 📊 **7. Models and Database Structure**

Here’s a high-level overview of the core models:

- **User:** Stores user details and related info.  
- **Product, Category, Brand:** Manages product listings and attributes.  
- **Cart and CartItem:** Handles items added to the cart.  
- **Order and OrderItem:** Stores order details and payment status.  
- **Coupon and CouponUsage:** Manages coupons and discounts.  
- **Wishlist and WishlistItem:** Keeps track of users’ favorite products.
- **Blog and Bloglist:**  Listing and viewing blogs realted to travel.

---

## 🌐 **8. API and URL Endpoints**

### ✅ **User Side URLs**
- `/` – Homepage  
- `/accounts/register/` – User registration  
- `/accounts/login/` – User login  
- `/store/` – Product listing  
- `/cart/` – View and update cart  
- `/checkout/` – Checkout page  

---

### ✅ **Admin URLs**
- `/admin/` – Admin login  
- `/admin_panel/dashboard/` – Admin dashboard  
- `/admin_panel/orders/` – Manage orders  
- `/admin_panel/products/` – Manage products  

---

## 🔒 **9. Authentication and Authorization**

- **Authentication:** Handled via Django’s built-in `auth` system.  
- **Authorization:** Restricted views for admin and user-specific pages.  

---

## 💳 **10. Payment Integration**

### ✅ **Razorpay Integration**
- Razorpay payment gateway integrated for secure payments.  
- Webhook to update payment status after successful/failed transactions.  

---


## 🎮 **11. To-Do and Future Enhancements**

- ⏳ Invoice PDF download after order completion  
- ⏳ Add Celery for background tasks and notifications  
- ⏳ Implement Product Reviews and Ratings  
- ⏳ Deployment on Heroku or AWS  

---
