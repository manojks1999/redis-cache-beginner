import re
import ast
import string

from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, Sequence, Date, VARCHAR, BIGINT


from api import Base

from datetime import datetime, timedelta, timezone
import uuid

# env
from dotenv import load_dotenv
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    DateTime,
    BigInteger,
    Float,
    JSON,
    ForeignKey,
    TIMESTAMP,
)
import os

# env
from dotenv import load_dotenv

# load environment variables
load_dotenv()
# get environment
ENVIRONMENT = os.environ.get("ENVIRONMENT")


# python classes that connect with the central
# db and provide classes to connect with tables
class DeviceLocations(Base):
    __tablename__ = "device_locations"
    __table_args__ = {"extend_existing": True}
    device_fk_id = Column(BIGINT)
    latitude = Column(VARCHAR)
    longitude = Column(VARCHAR)
    time_stamp = Column(TIMESTAMP)
    sts = Column(TIMESTAMP)
    speed = Column(Integer)
    id = Column(VARCHAR, primary_key=True)

    def __init__(
        self,
        device_fk_id,
        latitude,
        longitude,
        timestamp,
        sts,
        speed,
    ):
        """
        Create object
        """
        self.id = str(uuid.uuid4())
        self.device_fk_id = device_fk_id
        self.latitude = latitude
        self.longitude = longitude
        self.time_stamp = timestamp
        self.sts = sts
        self.speed = speed

    def to_dict(self):
        locations_data = {
            "device_fk_id": self.device_fk_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.time_stamp,
            "sts": self.sts,
            "speed": self.speed,
        }
        return locations_data
