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

### Database Setup

1. Download and extract the project files.

2. Open MySQL Workbench and import the SQL file:

   * `teamHATS_complete_database.sql`

3. Create the database with the following credentials:

   * **Database name:** `database_mgt`

   * **Password:** `password`

   > If you change these values, update them in `app.py` accordingly.

4. Verify the database was created successfully:

   ```sql
   USE database_mgt;
   SHOW TABLES;
   ```

5. Run the provided INSERT statements (from sampledata) to populate sample data.

### Running the Web Application (Optional)

1. Open a terminal or PowerShell window.
2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Start the application:

   ```bash
   python app.py
   ```
5. Open a browser and navigate to:

   ```
   http://localhost:5000
   ```

You should now be able to interact with the database through the web interface.

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
