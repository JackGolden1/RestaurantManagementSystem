# Restaurant Management Database System

## Description

This project is a comprehensive, normalized database system designed to support daily operations of a local restaurant. It centralizes reservations, orders, menu management, staff assignments, and payments to improve efficiency, reduce redundancy, and enhance data accuracy.

## Key Features

* Customer reservations and walk-in order support
* Order placement with preparation and status tracking
* Dynamic weekly menu rotation
* Payment processing and validation
* Staff assignment and performance tracking
* Administrative reporting and overrides

## Database Design

The database is built using a relational model and normalized to Third Normal Form (3NF).

### Core Entities

* Customer
* Reservation
* DiningTable
* MenuItem
* SalesOrder
* OrderItem
* Staff
* Payment

### Relationships

* One customer can have many reservations and orders
* Each order is assigned to one staff member and one payment
* Orders contain one or more menu items via OrderItem
* Reservations are linked to a single customer and table

## Business Rules & Integrity

* Enforced using primary keys, foreign keys, constraints, triggers, and stored procedures
* Prevents duplicate reservations, invalid payments, and inconsistent data
* Ensures all completed orders have exactly one payment

## Technologies Used

* MySQL
* SQL (DDL, DML, complex queries)
* Stored Procedures & Triggers
* MySQL Workbench
* Python (for application testing)

## Installation & Setup

Follow the steps below to install and run the database and optional web application locally.

### Prerequisites

* MySQL Server
* MySQL Workbench
* Python 3.x
* Git

### 1. Initial Setup

Download and Extract: Download the Final GroupDeliverable.zip file and extract its contents onto your computer.


Verify Files: Ensure the following files are present in the extracted folder: app.py, config.py, docker-compose.yaml, Dockerfile, requirements.txt, and TeamHATS_Complete_Database.sql.





2. Database Configuration
Before running the application, you must set up the MySQL database.


Import Database: Open MySQL Workbench and import the TeamHATS_Complete_Database.sql file.

Database Credentials:


Name: database_mgt.



Password: password.



Custom Configuration: If you use a different name or password, you must open app.py in an IDE (like VS Code) and update the following lines to match your credentials:


Python

app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'your_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'your_database_name')

Populate Data: Copy and run the INSERT statements from Deliverables 3 & 4 in MySQL Workbench to populate the tables for customers, staff, menu items, etc.


Verify Tables: Run the following commands in MySQL Workbench to confirm the setup:

SQL

USE database_mgt;
SHOW TABLES;
3. Running the Application
Use Windows PowerShell to initialize and launch the web application.

Create Virtual Environment:

PowerShell

python -m venv venv
[cite_start]``` [cite: 58]
Install Dependencies:

PowerShell

pip install -r requirements.txt
[cite_start]``` [cite: 59]
[cite_start]*(Note: If this fails, use the full file path for `requirements.txt`)[cite: 60].*
Launch App:

PowerShell

python app.py
[cite_start]``` [cite: 61]
[cite_start]*(Note: If this fails, use the full file path for `app.py`)[cite: 61].*

4. Accessing the Website
Once the server is running (indicated by a "Running on http://127.0.0.1:5000" message in the terminal):

Open your web browser.

Navigate to: http://localhost:5000.

You can now interact with the website and test the database functionality.

Would you like me to help you draft a "Troubleshooting" section based on common Python or MySQL errors?

## Usage

This database can be used directly through SQL queries or via the optional Python web application.

### Using SQL

* Run SELECT queries to view reservations, orders, payments, and reports
* Use provided INSERT, UPDATE, and DELETE queries to manage customers, reservations, menu items, and orders
* Execute stored procedures to place orders, update menu prices, or cancel reservations

### Using the Web Application (Optional)

* Start the Python application using `python app.py`
* Access the application at `http://localhost:5000`
* Use the interface to create reservations, place orders, and test database functionality

The system enforces business rules and data integrity automatically through constraints, triggers, and procedures.

## Future Improvements

* Role-based access expansion
* Advanced analytics and dashboards
* Online ordering integration
* Mobile-friendly frontend

## Authors

Joseph Walker, Alexa Corales, Giovanni Marroquin, Tommy Vives, Jack Golden

## License

This project was created for educational purposes.
