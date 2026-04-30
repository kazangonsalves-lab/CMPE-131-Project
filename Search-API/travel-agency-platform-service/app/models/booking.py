# ==========================================
# SQLALCHEMY MODELS (Zone 2 of ERD)
# ==========================================
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from app.core.database import Base  # Import Base from your core config


class Agent(Base):
    __tablename__ = "Agents"

    Agent_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Name = Column(String, nullable=False)
    Email = Column(String, unique=True, nullable=False)
    Phone = Column(String)

    bookings = relationship("Booking", back_populates="agent")


class HotelMaster(Base):
    __tablename__ = "Hotel_Master"

    Hotel_Code = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Hotel_Name = Column(String, nullable=False)
    Address = Column(String)
    City = Column(String, nullable=False)
    Zip_Code = Column(String)
    Country = Column(String, nullable=False)
    Email = Column(String)
    Phone_Number = Column(String)


class AirlineMaster(Base):
    __tablename__ = "Airline_Master"

    Airline_Code = Column(String, primary_key=True)
    Airline_Name = Column(String, nullable=False)


class AirportMaster(Base):
    __tablename__ = "Airport_Master"

    Airport_Code = Column(String, primary_key=True)
    Airport_Name = Column(String, nullable=False)
    City = Column(String, nullable=False)
    Country = Column(String, nullable=False)


class User(Base):
    __tablename__ = "Users"  # Fixed: matches CREATE TABLE Users

    User_ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    First_Name = Column(String, nullable=False)
    Last_Name = Column(String, nullable=False)
    Email = Column(String, unique=True, nullable=False, index=True)
    Phone_Number = Column(String)

    # Relationship back to Bookings
    bookings = relationship("Booking", back_populates="user")


class Booking(Base):
    __tablename__ = "Bookings"  # Fixed: matches CREATE TABLE Bookings

    Booking_Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    User_Id = Column(Integer, ForeignKey("Users.User_ID"), nullable=False)  # Fixed FK reference
    Agent_Id = Column(Integer, ForeignKey("Agents.Agent_Id"), nullable=True)
    Start_Date = Column(Date, nullable=False)
    End_Date = Column(Date, nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookings")
    agent = relationship("Agent", back_populates="bookings")
    hotel_reservations = relationship("HotelReservation", back_populates="booking", cascade="all, delete-orphan")
    flight_reservations = relationship("FlightReservation", back_populates="booking", cascade="all, delete-orphan")


class HotelReservation(Base):
    __tablename__ = "Hotel_Reservations"  # Fixed: matches CREATE TABLE Hotel_Reservations

    Reservation_No = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Booking_Id = Column(Integer, ForeignKey("Bookings.Booking_Id"), nullable=False)  # Fixed FK reference
    Hotel_Code = Column(Integer, ForeignKey("Hotel_Master.Hotel_Code"), nullable=False)  # Fixed FK reference
    Check_In_Date = Column(Date, nullable=False)
    Check_In_Time = Column(String, nullable=True)
    Check_Out_Date = Column(Date, nullable=False)
    Check_Out_Time = Column(String, nullable=True)
    Rate = Column(Float, nullable=True)

    booking = relationship("Booking", back_populates="hotel_reservations")


class FlightReservation(Base):
    __tablename__ = "Flight_Reservations"  # Fixed: matches CREATE TABLE Flight_Reservations

    Reservation_No = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Booking_Id = Column(Integer, ForeignKey("Bookings.Booking_Id"), nullable=False)  # Fixed FK reference
    Airline_Code = Column(String, ForeignKey("Airline_Master.Airline_Code"), nullable=False)  # Fixed FK reference
    Flight_Number = Column(String, nullable=False)
    Departure_Date = Column(Date, nullable=False)
    Departure_Time = Column(String, nullable=False)
    Arrive_Date = Column(Date, nullable=False)
    Arrive_Time = Column(String, nullable=False)
    Rate = Column(Float, nullable=True)
    Origin_Airport_Code = Column(String, ForeignKey("Airport_Master.Airport_Code"), nullable=False)  # Fixed FK reference
    Destination_Airport_Code = Column(String, ForeignKey("Airport_Master.Airport_Code"), nullable=False)  # Fixed FK reference

    booking = relationship("Booking", back_populates="flight_reservations")
