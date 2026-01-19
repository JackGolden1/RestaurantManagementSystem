
--Team HATS Restaurant Management System
-- Complete Database Schema and Data
-- Team Members: Joseph Walker, Alexa Corales, Giovanni Marroquin, Tommy Vives, Jack Golden
-- Course: BIT3524 - Database Management Systems

DROP DATABASE IF EXISTS database_mgt;
CREATE DATABASE IF NOT EXISTS database_mgt;
USE database_mgt;

-- Table Creation 
-- Customer Table --
CREATE TABLE Customer (
  CustomerID     INT PRIMARY KEY AUTO_INCREMENT,
  FirstName      VARCHAR(50)  NOT NULL,
  LastName       VARCHAR(50)  NOT NULL,
  Phone          VARCHAR(12),
  Email          VARCHAR(255) NOT NULL,
  CONSTRAINT uq_CustomerEmail UNIQUE (Email)
) ENGINE=InnoDB;

CREATE INDEX idx_CustomerName ON Customer (LastName, FirstName);

-- DiningTable Table
CREATE TABLE DiningTable (
  TableID     INT PRIMARY KEY AUTO_INCREMENT,
  TableNumber INT        NOT NULL,
  Capacity    INT        NOT NULL,
  Location    VARCHAR(100),
  IsActive    TINYINT(1) NOT NULL DEFAULT 1,
  CONSTRAINT chk_TableCapacity CHECK (Capacity > 0),
  CONSTRAINT uq_TableNumber UNIQUE (TableNumber)
) ENGINE=InnoDB;

CREATE INDEX idx_TableLocation ON DiningTable (Location);

-- Staff Table
CREATE TABLE Staff (
  StaffID     INT PRIMARY KEY AUTO_INCREMENT,
  FirstName   VARCHAR(50) NOT NULL,
  LastName    VARCHAR(50) NOT NULL,
  Role        VARCHAR(50) NOT NULL,
  ContactInfo VARCHAR(255),
  IsActive    TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE INDEX idx_StaffName ON Staff (LastName, FirstName);
CREATE INDEX idx_StaffRole ON Staff (Role);

-- MenuItem Table
CREATE TABLE MenuItem (
  ItemID      INT PRIMARY KEY AUTO_INCREMENT,
  Name        VARCHAR(150) NOT NULL,
  Category    VARCHAR(50)  NOT NULL,
  BasePrice   DECIMAL(10,2) NOT NULL,
  IsAvailable TINYINT(1) NOT NULL DEFAULT 1,
  CONSTRAINT chk_ItemPrice CHECK (BasePrice > 0)
) ENGINE=InnoDB;

CREATE UNIQUE INDEX uq_ItemName ON MenuItem (Name);
CREATE INDEX idx_ItemCategory ON MenuItem (Category);

-- Reservation Table
CREATE TABLE Reservation (
  ReservationID  INT PRIMARY KEY AUTO_INCREMENT,
  CustomerID     INT NOT NULL,
  TableID        INT NOT NULL,
  StartDateTime  DATETIME NOT NULL,
  EndDateTime    DATETIME NOT NULL,
  PartySize      INT NOT NULL,
  Status         VARCHAR(20) NOT NULL DEFAULT 'Booked',
  Notes          TEXT,
  CONSTRAINT fk_ResCustomer
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
  CONSTRAINT fk_ResTable
    FOREIGN KEY (TableID) REFERENCES DiningTable(TableID),
  CONSTRAINT chk_ResTimes CHECK (EndDateTime > StartDateTime),
  CONSTRAINT chk_ResParty CHECK (PartySize > 0),
  CONSTRAINT chk_ResStatus CHECK (Status IN ('Booked','Seated','Completed','Canceled'))
) ENGINE=InnoDB;

CREATE INDEX idx_ResTableTime ON Reservation (TableID, StartDateTime, EndDateTime);
CREATE INDEX idx_ResCustomer ON Reservation (CustomerID);

-- SalesOrder Table
CREATE TABLE SalesOrder (
  OrderID        INT PRIMARY KEY AUTO_INCREMENT,
  CustomerID     INT,
  ReservationID  INT,
  StaffID        INT,
  OrderDateTime  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Status         VARCHAR(20) NOT NULL DEFAULT 'Open',
  CreatedBy      VARCHAR(100),
  UpdatedAt      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_OrderCustomer
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
  CONSTRAINT fk_OrderReservation
    FOREIGN KEY (ReservationID) REFERENCES Reservation(ReservationID),
  CONSTRAINT fk_OrderStaff
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID),
  CONSTRAINT chk_OrderStatus
    CHECK (Status IN ('Open','Closed','Canceled'))
) ENGINE=InnoDB;

CREATE INDEX idx_OrderCustomer ON SalesOrder (CustomerID);
CREATE INDEX idx_OrderReservation ON SalesOrder (ReservationID);
CREATE INDEX idx_OrderStaff ON SalesOrder (StaffID);

-- OrderItem Table
CREATE TABLE OrderItem (
  OrderItemID         INT PRIMARY KEY AUTO_INCREMENT,
  OrderID             INT NOT NULL,
  ItemID              INT NOT NULL,
  Quantity            INT NOT NULL,
  UnitPriceAtOrder    DECIMAL(10,2) NOT NULL,
  SpecialInstructions TEXT,
  CONSTRAINT fk_OrderItem_Order
    FOREIGN KEY (OrderID) REFERENCES SalesOrder(OrderID)
    ON DELETE CASCADE,
  CONSTRAINT fk_OrderItem_Item
    FOREIGN KEY (ItemID) REFERENCES MenuItem(ItemID),
  CONSTRAINT chk_ItemQty CHECK (Quantity > 0),
  CONSTRAINT chk_ItemPriceAtOrder CHECK (UnitPriceAtOrder > 0)
) ENGINE=InnoDB;

CREATE INDEX idx_OrderItemOrder ON OrderItem (OrderID);
CREATE INDEX idx_OrderItemItem ON OrderItem (ItemID);

-- Payment Table
CREATE TABLE Payment (
  PaymentID       INT PRIMARY KEY AUTO_INCREMENT,
  OrderID         INT NOT NULL UNIQUE,
  Amount          DECIMAL(10,2) NOT NULL,
  PaymentMethod   VARCHAR(30) NOT NULL,
  PaymentDateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  AuthCode        VARCHAR(40),
  Status          VARCHAR(20) NOT NULL DEFAULT 'Captured',
  CONSTRAINT fk_PaymentOrder
    FOREIGN KEY (OrderID) REFERENCES SalesOrder(OrderID)
    ON DELETE CASCADE,
  CONSTRAINT chk_PaymentAmount CHECK (Amount > 0),
  CONSTRAINT chk_PaymentStatus CHECK (Status IN ('Authorized','Captured','Declined','Refunded'))
) ENGINE=InnoDB;

CREATE INDEX idx_PaymentMethod ON Payment (PaymentMethod);

-- MenuRotation Table (Optional Feature)
CREATE TABLE MenuRotation (
  RotationID INT PRIMARY KEY AUTO_INCREMENT,
  StartDate  DATE NOT NULL,
  EndDate    DATE NOT NULL,
  Label      VARCHAR(100) NOT NULL,
  CONSTRAINT chk_RotationDates CHECK (EndDate > StartDate)
) ENGINE=InnoDB;

-- MenuRotationItem Bridge Table
CREATE TABLE MenuRotationItem (
  RotationID INT NOT NULL,
  ItemID     INT NOT NULL,
  PRIMARY KEY (RotationID, ItemID),
  CONSTRAINT fk_MRI_Rotation
    FOREIGN KEY (RotationID) REFERENCES MenuRotation(RotationID)
    ON DELETE CASCADE,
  CONSTRAINT fk_MRI_Item
    FOREIGN KEY (ItemID) REFERENCES MenuItem(ItemID)
    ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_MRI_Item ON MenuRotationItem (ItemID);

-- Audit Tables
CREATE TABLE PriceAudit (
  AuditID        INT PRIMARY KEY AUTO_INCREMENT,
  ItemID         INT NOT NULL,
  OldPrice       DECIMAL(10,2) NOT NULL,
  NewPrice       DECIMAL(10,2) NOT NULL,
  ChangeDateTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ItemID) REFERENCES MenuItem(ItemID)
) ENGINE=InnoDB;

CREATE TABLE ReservationAudit (
  AuditID         INT PRIMARY KEY AUTO_INCREMENT,
  ReservationID   INT NOT NULL,
  Action          VARCHAR(50) NOT NULL,
  ActionTimeStamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ReservationID) REFERENCES Reservation(ReservationID)
) ENGINE=InnoDB;

--  SAMPLE DATA 

-- Insert Customers
INSERT INTO Customer (FirstName, LastName, Phone, Email) VALUES
('Alice', 'McCarthy', '274-375-2859', 'alice.mccarthy@email.com'),
('Brian', 'Lee', '684-325-1686', 'brian.lee@email.com'),
('Carla', 'Chadha', '432-126-1899', 'carla.chadha@email.com'),
('David', 'Miller', '111-222-3333', 'david.miller@email.com'),
('Ella', 'Hall', '333-444-5555', 'ella.hall@email.com'),
('Felix', 'Smith', '777-888-9999', 'felix.smith@email.com'),
('Grace', 'Brown', '012-468-9246', 'grace.brown@email.com'),
('Jack', 'Taylor', '124-256-7014', 'jack.taylor@email.com'),
('Henry', 'Wright', '563-673-2513', 'henry.wright@email.com'),
('JJ', 'Daniels', '983-091-9470', 'jj.daniels@email.com');

-- Insert Dining Tables
INSERT INTO DiningTable (TableNumber, Capacity, Location) VALUES
(1, 2, 'Front Window'),
(2, 4, 'Main Hall'),
(3, 4, 'Main Hall'),
(4, 6, 'Patio'),
(5, 2, 'Bar Area'),
(6, 4, 'Patio'),
(7, 6, 'VIP Room'),
(8, 4, 'Garden'),
(9, 2, 'Balcony'),
(10, 8, 'Main Hall');

-- Insert Staff
INSERT INTO Staff (FirstName, LastName, Role, ContactInfo) VALUES
('Tom', 'Evans', 'Manager', 'tom.evans@restaurant.com'),
('Judy', 'Martinez', 'Server', 'judy.martinez@restaurant.com'),
('Kyle', 'Brown', 'Chef', 'kyle.brown@restaurant.com'),
('Maria', 'Lopez', 'Server', 'maria.lopez@restaurant.com'),
('Jake', 'Turner', 'Busser', 'jake.turner@restaurant.com'),
('Sarah', 'Jackson', 'Server', 'sarah.jackson@restaurant.com'),
('Olivia', 'Davis', 'Chef', 'olivia.davis@restaurant.com'),
('Nathan', 'McGregor', 'Bartender', 'nathan.mcgregor@restaurant.com'),
('Leo', 'Johnson', 'Host', 'leo.johnson@restaurant.com'),
('Sophia', 'Alt', 'Server', 'sophia.alt@restaurant.com');

-- Insert Menu Items
INSERT INTO MenuItem (Name, Category, BasePrice) VALUES
('Supreme Pizza', 'Entree', 12.99),
('Caesar Salad', 'Appetizer', 8.50),
('Spaghetti Carbonara', 'Entree', 14.75),
('Tiramisu', 'Dessert', 7.00),
('Iced Tea', 'Beverage', 2.99),
('Garlic Bread', 'Appetizer', 5.50),
('Grilled Salmon', 'Entree', 18.25),
('Lemon Tart', 'Dessert', 6.75),
('Mojito', 'Beverage', 8.00),
('Bruschetta', 'Appetizer', 7.25),
('Chicken Parmesan', 'Entree', 16.50),
('French Onion Soup', 'Appetizer', 6.00),
('Chocolate Cake', 'Dessert', 7.50),
('Cappuccino', 'Beverage', 4.25),
('Ribeye Steak', 'Entree', 24.99);

-- Insert Reservations (Future dates)
INSERT INTO Reservation (CustomerID, TableID, StartDateTime, EndDateTime, PartySize, Status) VALUES
(1, 2, '2025-12-15 18:00:00', '2025-12-15 19:30:00', 4, 'Booked'),
(2, 3, '2025-12-15 19:00:00', '2025-12-15 20:30:00', 2, 'Booked'),
(3, 5, '2025-12-16 17:00:00', '2025-12-16 18:30:00', 2, 'Booked'),
(4, 4, '2025-12-16 19:00:00', '2025-12-16 21:00:00', 6, 'Booked'),
(5, 7, '2025-12-17 18:30:00', '2025-12-17 20:00:00', 5, 'Booked'),
(6, 6, '2025-12-17 20:00:00', '2025-12-17 21:30:00', 4, 'Booked'),
(7, 9, '2025-12-18 18:00:00', '2025-12-18 19:30:00', 2, 'Booked'),
(8, 1, '2025-12-18 19:00:00', '2025-12-18 20:00:00', 2, 'Booked'),
(9, 10, '2025-12-19 17:30:00', '2025-12-19 19:00:00', 8, 'Booked'),
(10, 8, '2025-12-19 19:30:00', '2025-12-19 21:00:00', 4, 'Booked');

-- Insert Sales Orders
INSERT INTO SalesOrder (CustomerID, ReservationID, StaffID, Status, CreatedBy) VALUES
(1, 1, 2, 'Closed', 'Tom Evans'),
(2, 2, 4, 'Open', 'Maria Lopez'),
(3, 3, 2, 'Closed', 'Judy Martinez'),
(4, 4, 6, 'Closed', 'Sarah Jackson'),
(5, 5, 4, 'Closed', 'Maria Lopez'),
(6, 6, 10, 'Closed', 'Sophia Alt'),
(7, 7, 2, 'Closed', 'Judy Martinez'),
(8, 8, 9, 'Closed', 'Leo Johnson'),
(9, 9, 1, 'Closed', 'Tom Evans'),
(10, 10, 10, 'Canceled', 'Sophia Alt');

-- Insert Order Items
INSERT INTO OrderItem (OrderID, ItemID, Quantity, UnitPriceAtOrder, SpecialInstructions) VALUES
(1, 1, 2, 12.99, 'Extra cheese'),
(1, 5, 2, 2.99, 'No ice'),
(2, 3, 1, 14.75, 'No bacon'),
(2, 4, 1, 7.00, 'Extra cocoa'),
(3, 6, 1, 5.50, 'To share'),
(3, 7, 1, 18.25, ''),
(4, 1, 1, 12.99, ''),
(4, 8, 1, 6.75, 'Extra lemon'),
(5, 9, 2, 8.00, ''),
(6, 2, 2, 8.50, 'Dressing on side'),
(7, 3, 1, 14.75, ''),
(8, 10, 2, 7.25, ''),
(9, 4, 3, 7.00, 'Extra cocoa'),
(10, 1, 2, 12.99, 'Extra Basil');

-- Insert Payments
INSERT INTO Payment (OrderID, Amount, PaymentMethod, AuthCode, Status) VALUES
(1, 31.96, 'Credit Card', 'AUTH001', 'Captured'),
(3, 23.75, 'Credit Card', 'AUTH002', 'Captured'),
(4, 19.74, 'Credit Card', 'AUTH003', 'Captured'),
(5, 16.00, 'Cash', NULL, 'Captured'),
(6, 17.00, 'Credit Card', 'AUTH004', 'Captured'),
(7, 14.75, 'Credit Card', 'AUTH005', 'Captured'),
(8, 14.50, 'Cash', NULL, 'Captured'),
(9, 21.00, 'Credit Card', 'AUTH006', 'Captured');

--  STORED PROCEDURES 

DELIMITER //

-- Procedure 1: PlaceOrder
CREATE PROCEDURE PlaceOrder(
    IN p_CustomerID INT,
    IN p_StaffID INT,
    IN p_ItemID INT,
    IN p_Quantity INT
)
BEGIN
    DECLARE v_UnitPrice DECIMAL(10,2);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Transaction rolled back';
    END;
    
    START TRANSACTION;
    
    IF NOT EXISTS (SELECT 1 FROM MenuItem WHERE ItemID = p_ItemID) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid Item ID';
    END IF;
    
    SELECT BasePrice INTO v_UnitPrice
    FROM MenuItem
    WHERE ItemID = p_ItemID;
    
    INSERT INTO SalesOrder (CustomerID, StaffID, OrderDateTime, Status)
    VALUES (p_CustomerID, p_StaffID, NOW(), 'Open');
    
    SET @orderID = LAST_INSERT_ID();
    
    INSERT INTO OrderItem (OrderID, ItemID, Quantity, UnitPriceAtOrder)
    VALUES (@orderID, p_ItemID, p_Quantity, v_UnitPrice);
    
    COMMIT;
END //

-- Procedure 2: UpdateMenuPrice
CREATE PROCEDURE UpdateMenuPrice(
    IN p_ItemID INT,
    IN p_Adjustment DECIMAL(10,2),
    IN p_IsPercentage BOOLEAN
)
BEGIN
    DECLARE v_OldPrice DECIMAL(10,2);
    DECLARE v_NewPrice DECIMAL(10,2);
    
    START TRANSACTION;
    
    SELECT BasePrice INTO v_OldPrice
    FROM MenuItem
    WHERE ItemID = p_ItemID;
    
    IF v_OldPrice IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid Item ID';
    END IF;
    
    IF p_IsPercentage THEN
        SET v_NewPrice = v_OldPrice * (1 + (p_Adjustment / 100));
    ELSE
        SET v_NewPrice = v_OldPrice + p_Adjustment;
    END IF;
    
    IF v_NewPrice <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: New price must be greater than zero';
    END IF;
    
    UPDATE MenuItem
    SET BasePrice = v_NewPrice
    WHERE ItemID = p_ItemID;
    
    COMMIT;
END //

-- Procedure 3: CancelReservation
CREATE PROCEDURE CancelReservation(
    IN p_ReservationID INT
)
BEGIN
    DECLARE v_Exists INT DEFAULT 0;
    
    START TRANSACTION;
    
    SELECT COUNT(*) INTO v_Exists
    FROM Reservation
    WHERE ReservationID = p_ReservationID;
    
    IF v_Exists > 0 THEN
        INSERT INTO ReservationAudit (ReservationID, Action, ActionTimeStamp)
        VALUES (p_ReservationID, 'Canceled', NOW());
        
        UPDATE Reservation
        SET Status = 'Canceled'
        WHERE ReservationID = p_ReservationID;
    ELSE
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Reservation not found';
    END IF;
    
    COMMIT;
END //

DELIMITER ;

-- Triggers 
DELIMITER //
-- Trigger #1: Prevent Customer Deletion with Orders
CREATE TRIGGER PreventCustomerDeletion
BEFORE DELETE ON Customer
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM SalesOrder WHERE CustomerID = OLD.CustomerID)
THEN 
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Customer cannot be deleted because of existing orders';
    END IF;
END //

-- Trigger 2: Log Menu Price Updates
CREATE TRIGGER LogMenuPriceUpdate
AFTER UPDATE ON MenuItem
FOR EACH ROW
BEGIN
    IF OLD.BasePrice <> NEW.BasePrice THEN
        INSERT INTO PriceAudit (ItemID, OldPrice, NewPrice, ChangeDateTime)
        VALUES (OLD.ItemID, OLD.BasePrice, NEW.BasePrice, NOW());
    END IF;
END //

DELIMITER ;

-- User Accounts and Permissions 
-- Create Application Users
CREATE USER IF NOT EXISTS 'server_app'@'%' IDENTIFIED BY 'server_pass';
CREATE USER IF NOT EXISTS 'manager_app'@'%' IDENTIFIED BY 'manager_pass';
CREATE USER IF NOT EXISTS 'accountant_app'@'%' IDENTIFIED BY 'accountant_pass';
CREATE USER IF NOT EXISTS 'reporting_readonly'@'%' IDENTIFIED BY 'report_pass';

-- Grant permissions to server_app
GRANT EXECUTE ON PROCEDURE database_mgt.PlaceOrder TO 'server_app'@'%';
GRANT SELECT ON database_mgt.Customer TO 'server_app'@'%';
GRANT SELECT ON database_mgt.MenuItem TO 'server_app'@'%';
GRANT SELECT, INSERT ON database_mgt.SalesOrder TO 'server_app'@'%';
GRANT SELECT, INSERT ON database_mgt.OrderItem TO 'server_app'@'%';

-- Grant permissions to manager_app
GRANT EXECUTE ON PROCEDURE database_mgt.UpdateMenuPrice TO 'manager_app'@'%';
GRANT EXECUTE ON PROCEDURE database_mgt.CancelReservation TO 'manager_app'@'%';
GRANT SELECT, UPDATE ON database_mgt.MenuItem TO 'manager_app'@'%';
GRANT SELECT, UPDATE ON database_mgt.Reservation TO 'manager_app'@'%';
GRANT SELECT ON database_mgt.PriceAudit TO 'manager_app'@'%';
GRANT SELECT ON database_mgt.ReservationAudit TO 'manager_app'@'%';

-- Grant permissions to accountant_app
GRANT SELECT ON database_mgt.Payment TO 'accountant_app'@'%';
GRANT SELECT ON database_mgt.SalesOrder TO 'accountant_app'@'%';
GRANT SELECT ON database_mgt.OrderItem TO 'accountant_app'@'%';

-- Grant permissions to reporting_readonly
GRANT SELECT ON database_mgt.Customer TO 'reporting_readonly'@'%';
GRANT SELECT ON database_mgt.Reservation TO 'reporting_readonly'@'%';
GRANT SELECT ON database_mgt.MenuItem TO 'reporting_readonly'@'%';
-- Verification Queries 
-- Verify table creation
SELECT 'Tables Created Successfully' AS Status;
SHOW TABLES;

-- Verify data insertion
SELECT 'Sample Data Inserted' AS Status;
SELECT COUNT(*) AS Customers FROM Customer;
SELECT COUNT(*) AS MenuItems FROM MenuItem;
SELECT COUNT(*) AS Reservations FROM Reservation;
SELECT COUNT(*) AS Orders FROM SalesOrder;

-- Verify stored procedures
SELECT 'Stored Procedures Created' AS Status;
SHOW PROCEDURE STATUS WHERE Db = 'database_mgt';

-- Verify triggers
SELECT 'Triggers Created' AS Status;
SHOW TRIGGERS FROM database_mgt;
