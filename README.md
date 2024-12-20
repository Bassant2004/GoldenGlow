# GOLDEN GLOW
This is an e-commerce web application built with Flask, featuring user authentication, product management, shopping cart functionality, and order processing. The project is designed with a modular architecture allowing for clear separation of concerns among team members.
### Installation
#### 1. create a virtual invironment
- on windows :

    ``` 
    python -m venv myvenv

    venv\Scripts\activate
    ```

- on mac :

    ``` 
    python -m venv myvenv

    source venv/bin/activate
    ```





#### 2. install the requirements.txt  
- on windows :

    ```bash 
    pip install requirements.txt
    ```

- on mac :

    ```bash 
    pip3 install requirements.txt
    ```

#### 3. create the db
open your vscode terminal and run 
```
flask shell
```

```
from app import db
db.create_all()
```
this will create the instance folder with `database.db`

#### 4. run the app
open your terminal and run this code
```
python app.py
```
or on mac
```
python3 app.py
```
you should see a link copy it and paste on the browser and you should be ready

# E-Commerce Web Application

A modern e-commerce platform built with Flask, featuring user authentication, product management, shopping cart functionality, and order processing.

## Project Overview

This application provides a complete e-commerce solution with features including:
- User authentication and authorization
- Product catalog with category filtering
- Shopping cart management
- Secure checkout process
- Order tracking
- Admin dashboard for product management

## Contributors and Responsibilities

### Bassant Khaled 
- Product catalog implementation
- Main page layout and design
- Category filtering system
- Product sorting functionality
- Files: index.html, catalog components in main.js

### Sarah Mohamed
- User authentication system
- Login/Register functionality
- Session management
- Security implementation
- Files: signin.html, signup.html, authentication routes in app.py

### Rony Sherief
- Shopping cart functionality
- Cart management
- Recently viewed items feature
- Local storage implementation
- Files: shoppingcart.html, cart-related functions in main.js

### Malak Ayman
- Checkout process
- Order management
- Payment integration
- Order confirmation system
- Files: checkout.html, order routes in app.py

### Mary Sobhi 
- Admin dashboard
- Product management interface
- Image upload functionality
- Inventory management
- Files: additem.html, product management routes in app.py


## Shahd Elshokaly

- Backend: Flask (Python)
- Database: SQLite with SQLAlchemy ORM
- Frontend: JavaScript, HTML, CSS
- File Storage: Local file system for product images
- Authentication: Session-based with password hashing


