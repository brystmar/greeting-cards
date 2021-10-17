from logging import getLogger
from datetime import datetime
from backend import db
# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import declarative_base

logger = getLogger()


class Address(db.Model):
    __tablename__ = 'address'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    line_1 = db.Column(db.String)
    line_2 = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    zip = db.Column(db.String)
    country = db.Column(db.String, default="United States")
    is_current = db.Column(db.Integer, default=1)
    is_likely_to_change = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Address(id={self.id}, fam={self.family_id}, city={self.city}, " \
               f"state={self.state}, is_current={self.is_current}"


class Family(db.Model):
    __tablename__ = "family"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String)
    surname = db.Column(db.String)
    formal_name = db.Column(db.String)
    relationship = db.Column(db.String)
    relationship_type = db.Column(db.String)
    primary_address_id = db.Column(db.Integer)

    def __repr__(self):
        return f"Family(id={self.id}, nick={self.nickname}, surname={self.surname}, " \
               f"rel={self.relationship}, primary_address={self.primary_address_id}"


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    date = db.Column(db.String)
    year = db.Column(db.Integer, default=datetime.now().year)
    is_archived = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Event(id={self.id}, name={self.name}, date={self.date}, year={self.year}, " \
               f"is_archived={self.is_archived}"


class Gift(db.Model):
    __tablename__ = "gift"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    description = db.Column(db.String)
    notes = db.Column(db.String)

    def __repr__(self):
        return f"Gift(id={self.id}, event={self.event_id}, fam={self.family_id}, " \
               f"description={self.description}, notes={self.notes}"


class Card(db.Model):
    __tablename__ = "card"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    was_card_sent = db.Column(db.Integer, default=0)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    gift_id = db.Column(db.Integer, db.ForeignKey('gift.id'))
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))

    def __repr__(self):
        return f"Card(id={self.id}, was_card_sent={self.was_card_sent}, event={self.event_id}, " \
               f"gift={self.gift_id}, fam={self.family_id}, address={self.address_id}"
