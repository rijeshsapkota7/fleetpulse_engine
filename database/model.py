from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey,Float

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String , nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)

class Deliveries(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rider_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    pickup_address = Column(String, nullable=False)
    dropoff_address = Column(String, nullable=False)
    status = Column(String, nullable=False)

class RiderLocation(Base):
    __tablename__ = "rider_locations"
    id = Column(Integer, primary_key=True)
    rider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(String, nullable=False)

