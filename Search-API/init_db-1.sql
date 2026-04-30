-- =========================================================================
-- TRAVEL BOOKING SYSTEM INITIALIZATION SCRIPT
-- Purpose: Build optimized schema and seed with realistic test data.
-- =========================================================================

-- Step 1: Clean up existing tables (important for repeated testing)
-- DROP in reverse order of relationships to respect constraints.
DROP TABLE IF EXISTS Activity_Reservations;
DROP TABLE IF EXISTS Flight_Reservations;
DROP TABLE IF EXISTS Hotel_Reservations;
DROP TABLE IF EXISTS Bookings;
DROP TABLE IF EXISTS Airport_Master;
DROP TABLE IF EXISTS Airline_Master;
DROP TABLE IF EXISTS Hotel_Master;
DROP TABLE IF EXISTS Agents;
DROP TABLE IF EXISTS Users;

-- =========================================================================
-- Part 1: CREATE REFERENCE TABLES (MASTER DATA)
-- Zone 1 of the ERD
-- =========================================================================

-- 1. Users Table
CREATE TABLE Users (
    User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    First_Name TEXT NOT NULL,
    Last_Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL, -- Critically important constraint
    Phone_Number TEXT
);

-- 2. Agents Table
CREATE TABLE Agents (
    Agent_Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL, -- Ensures agent emails are unique
    Phone TEXT
);

-- 3. Hotel_Master (Optimized static hotel data)
CREATE TABLE Hotel_Master (
    Hotel_Code INTEGER PRIMARY KEY AUTOINCREMENT, -- Used as the FK ID
    Hotel_Name TEXT NOT NULL,
    Address TEXT,
    City TEXT NOT NULL,
    Zip_Code TEXT,
    Country TEXT NOT NULL,
    Email TEXT,
    Phone_Number TEXT,
    -- Prevent duplicate entries of the same hotel
    UNIQUE(Hotel_Name, City, Country) 
);

-- 4. Airline_Master (Static airline data)
CREATE TABLE Airline_Master (
    Airline_Code TEXT PRIMARY KEY, -- Standard IATA code, e.g., 'AA', 'DL', 'BA'
    Airline_Name TEXT NOT NULL
);

-- 5. Airport_Master (Static airport data)
CREATE TABLE Airport_Master (
    Airport_Code TEXT PRIMARY KEY, -- Standard IATA code, e.g., 'LHR', 'JFK', 'LAX'
    Airport_Name TEXT NOT NULL,
    City TEXT NOT NULL,
    Country TEXT NOT NULL
);


-- =========================================================================
-- Part 2: CREATE MAIN TRANSACTION TABLE
-- Zone 2 of the ERD
-- =========================================================================

-- 6. Bookings (Central "Bucket" table)
CREATE TABLE Bookings (
    Booking_Id INTEGER PRIMARY KEY AUTOINCREMENT,
    User_Id INTEGER NOT NULL,
    Agent_Id INTEGER, -- Can be NULL if booked directly by the user
    Start_Date TEXT NOT NULL, -- ISO 8601 (YYYY-MM-DD)
    End_Date TEXT NOT NULL,   -- ISO 8601 (YYYY-MM-DD)
    
    -- Mandatory Constraints
    FOREIGN KEY (User_Id) REFERENCES Users(User_Id),
    FOREIGN KEY (Agent_Id) REFERENCES Agents(Agent_Id)
);


-- =========================================================================
-- Part 3: CREATE CHILD TRANSACTION TABLES (SUB-RESERVATIONS)
-- Zone 3 of the ERD
-- =========================================================================

-- 7. Hotel_Reservations (Links a Booking to a specific stay)
CREATE TABLE Hotel_Reservations (
    Reservation_No INTEGER PRIMARY KEY AUTOINCREMENT,
    Booking_Id INTEGER NOT NULL,
    Hotel_Code INTEGER NOT NULL, -- REFERENCE TO MASTER DATA
    Check_In_Date TEXT NOT NULL,
    Check_In_Time TEXT, -- Often useful to track
    Check_Out_Date TEXT NOT NULL,
    Check_Out_Time TEXT,
    Rate REAL, -- Crucially, the rate charged for THIS specific stay

    FOREIGN KEY (Booking_Id) REFERENCES Bookings(Booking_Id),
    FOREIGN KEY (Hotel_Code) REFERENCES Hotel_Master(Hotel_Code)
);

-- 8. Flight_Reservations (Links a Booking to a complex travel route)
CREATE TABLE Flight_Reservations (
    Reservation_No INTEGER PRIMARY KEY AUTOINCREMENT,
    Booking_Id INTEGER NOT NULL,
    Airline_Code TEXT NOT NULL, -- REFERENCE TO AIRLINE MASTER
    Flight_Number TEXT NOT NULL, -- e.g., '101'
    Departure_Date TEXT NOT NULL,
    Departure_Time TEXT NOT NULL, -- 24-hour format suggested (e.g., '14:30')
    Arrive_Date TEXT NOT NULL,
    Arrive_Time TEXT NOT NULL,
    Rate REAL, -- Specific rate for THIS flight booking
    Origin_Airport_Code TEXT NOT NULL, -- REFERENCE TO AIRPORT MASTER
    Destination_Airport_Code TEXT NOT NULL, -- REFERENCE TO AIRPORT MASTER

    -- Foreign Key constraints ensure all codes are valid master data
    FOREIGN KEY (Booking_Id) REFERENCES Bookings(Booking_Id),
    FOREIGN KEY (Airline_Code) REFERENCES Airline_Master(Airline_Code),
    FOREIGN KEY (Origin_Airport_Code) REFERENCES Airport_Master(Airport_Code),
    FOREIGN KEY (Destination_Airport_Code) REFERENCES Airport_Master(Airport_Code)
);

-- 9. Activity_Reservations (Links activities directly to the Booking)
CREATE TABLE Activity_Reservations (
    Activity_Reservation_Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Booking_Id INTEGER NOT NULL, -- Linked to the Booking trip
    Activity_Name TEXT NOT NULL, -- Specific name: 'Eiffel Tower Access'
    Location TEXT,
    Activity_Date TEXT NOT NULL,
    Price REAL,

    FOREIGN KEY (Booking_Id) REFERENCES Bookings(Booking_Id)
);

-- =========================================================================
-- End of CREATE statements
-- =========================================================================


-- =========================================================================
-- Part 4: SEED DATA FOR TESTING
-- Inserting sample data that follows all relationships.
-- =========================================================================

-- 1. Seed Users
INSERT INTO Users (First_Name, Last_Name, Email, Phone_Number) VALUES
('John', 'Doe', 'john.doe@example.com', '555-123-4567'),
('Jane', 'Smith', 'jane.smith@email.co.uk', '44-20-7946-0958'),
('Kazan', 'Gonsalves', 'kazangonsalves@example.com', '650-248-0747');
--3. My User

-- 2. Seed Agents
INSERT INTO Agents (Name, Email, Phone) VALUES
('Global Travel Solutions', 'support@gtstravel.com', '1-800-555-0199'),
('Independent Agent Bob', 'bob@bobsbookings.biz', '555-987-6543');

-- 3. Seed Hotel_Master (Master Hotel data)
-- Let's define some famous places.
INSERT INTO Hotel_Master (Hotel_Name, Address, City, Zip_Code, Country, Email) VALUES
('The Plaza', '768 5th Ave', 'New York', '10019', 'USA', 'reservations@theplazany.com'),
('The Savoy', 'Strand', 'London', 'WC2R 0EU', 'UK', 'savoy.reservations@fairmont.com'),
('Hotel California', '123 Sunset Blvd', 'Los Angeles', '90210', 'USA', 'youcanneverleave@hc.com'),
('HI New York City Hostel', '891 Amsterdam Avenue', 'New York', '10025', 'USA', 'hinych@newyork.com');
-- 4.My hotel info

-- 4. Seed Airline_Master (Major Carriers)
INSERT INTO Airline_Master (Airline_Code, Airline_Name) VALUES
('AA', 'American Airlines'),
('BA', 'British Airways'),
('DL', 'Delta Air Lines'),
('VS', 'Virgin Atlantic'),
('AL', 'Alaska Airlines');
--5. My Airlines

-- 5. Seed Airport_Master (Major Hubs)
INSERT INTO Airport_Master (Airport_Code, Airport_Name, City, Country) VALUES
('JFK', 'John F. Kennedy International', 'New York', 'USA'),
('SFO', 'San Francisco International', 'San Francisco', 'USA'),
('LHR', 'London Heathrow', 'London', 'UK'),
('LAX', 'Los Angeles International', 'Los Angeles', 'USA'),
('CDG', 'Charles de Gaulle Airport', 'Paris', 'France');

-- SEED MAIN TRANSACTIONS 
-- Crucial: We must generate the Bookings first to get the Booking_Ids needed
-- for all child reservation tables.

-- 6. Seed Bookings
-- John Doe (User 1) booked directly a New York to London Trip (3 weeks).
INSERT INTO Bookings (User_Id, Agent_Id, Start_Date, End_Date) VALUES
(1, NULL, '2024-06-01', '2024-06-21'); -- Returns Booking_Id 1

-- Jane Smith (User 2) booked a trip through Global Travel (Agent 1) to LA (10 days).
INSERT INTO Bookings (User_Id, Agent_Id, Start_Date, End_Date) VALUES
(2, 1, '2024-08-15', '2024-08-25'); -- Returns Booking_Id 2


-- SEED SUB-RESERVATIONS (LINKED TO BOOKINGS) 

-- 7. Seed Hotel_Reservations
-- Booking 1 (John in London) staying at The Savoy (Hotel_Code 2).
INSERT INTO Hotel_Reservations (Booking_Id, Hotel_Code, Check_In_Date, Check_In_Time, Check_Out_Date, Rate) VALUES
(1, 2, '2024-06-02', '14:00', '2024-06-19', 450.00);

-- Booking 2 (Jane in LA) staying at Hotel California (Hotel_Code 3).
INSERT INTO Hotel_Reservations (Booking_Id, Hotel_Code, Check_In_Date, Check_Out_Date, Rate) VALUES
(2, 3, '2024-08-15', '2024-08-25', 298.80);


-- 8. Seed Flight_Reservations
-- Booking 1 (John NY to London). Round trip.
INSERT INTO Flight_Reservations (Booking_Id, Airline_Code, Flight_Number, Departure_Date, Departure_Time, Arrive_Date, Arrive_Time, Rate, Origin_Airport_Code, Destination_Airport_Code) VALUES
(1, 'BA', '112', '2024-06-01', '18:30', '2024-06-02', '06:30', 850.00, 'JFK', 'LHR'), -- Outbound
(1, 'BA', '113', '2024-06-21', '10:15', '2024-06-21', '13:10', 850.00, 'LHR', 'JFK'); -- Inbound (Rate is often for the whole trip, but this table tracks specific leg costs/rates).

-- Booking 2 (Jane NY to LA). One way Delta flight.
INSERT INTO Flight_Reservations (Booking_Id, Airline_Code, Flight_Number, Departure_Date, Departure_Time, Arrive_Date, Arrive_Time, Rate, Origin_Airport_Code, Destination_Airport_Code) VALUES
(2, 'DL', '45', '2024-08-15', '07:00', '2024-08-15', '10:05', 315.50, 'JFK', 'LAX');


-- 9. Seed Activity_Reservations
-- Booking 1 (John in London) did a Thames Cruise.
INSERT INTO Activity_Reservations (Booking_Id, Activity_Name, Location, Activity_Date, Price) VALUES
(1, 'Thames River Sunset Cruise', 'Tower Pier, London', '2024-06-05', 75.00);

-- Booking 2 (Jane in LA) booked a studio tour.
INSERT INTO Activity_Reservations (Booking_Id, Activity_Name, Location, Activity_Date, Price) VALUES
(2, 'Warner Bros Studio Tour', 'Burbank, CA', '2024-08-18', 69.00),
(2, 'Santa Monica Pier Bike Rental', 'Santa Monica', '2024-08-20', 25.00); -- Two activities on one trip

-- =========================================================================
-- Complete: 9 tables built, populated with related test data.
-- =========================================================================

