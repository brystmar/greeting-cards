from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True, autoincrement=True)
    family_id = Column(Integer, ForeignKey('family.id'))
    line_1 = Column(String)
    line_2 = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String, default="United States")
    is_current = Column(Integer, default=1)
    is_likely_to_change = Column(Integer, default=0)

    def __repr__(self):
        return f"Address(id={self.id}, family_id={self.family_id}, city={self.city}, " \
               f"state={self.state}, is_current={self.is_current}"


class Family(Base):
    __tablename__ = "family"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    formal_name = Column(String)
    relationship = Column(String)
    primary_address_id = Column(Integer)

    def __repr__(self):
        return f"Family(id={self.id}, name={self.name}, primary_address={self.primary_address_id}"


class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    date = Column(String)
    year = Column(Integer, default=datetime.now().year)
    is_archived = Column(Integer, default=0)

    def __repr__(self):
        return f"Event(id={self.id}, name={self.name}, date={self.date}, year={self.year}, " \
               f"is_archived={self.is_archived}"


class Gift(Base):
    __tablename__ = "gift"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey('event.id'))
    family_id = Column(Integer, ForeignKey('family.id'))
    description = Column(String)
    notes = Column(String)

    def __repr__(self):
        return f"Gift(id={self.id}, event={self.event_id}, family={self.family_id}, " \
               f"description={self.description}, notes={self.notes}"


class Card(Base):
    __tablename__ = "card"

    id = Column(Integer, primary_key=True, autoincrement=True)
    was_card_sent = Column(Integer, default=0)
    event_id = Column(Integer, ForeignKey('event.id'))
    gift_id = Column(Integer, ForeignKey('gift.id'))
    family_id = Column(Integer, ForeignKey('family.id'))
    address_id = Column(Integer, ForeignKey('address.id'))

    def __repr__(self):
        return f"Card(id={self.id}, was_card_sent={self.was_card_sent}, event={self.event_id}, " \
               f"gift={self.gift_id}, family={self.family_id}, address={self.address_id}"
