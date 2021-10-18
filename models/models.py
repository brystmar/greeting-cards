from logging import getLogger
from datetime import datetime
from backend import db

logger = getLogger()


class Address(db.Model):
    __tablename__ = 'address'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    line_1 = db.Column(db.String)
    line_2 = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    zip = db.Column(db.String)
    country = db.Column(db.String, default="United States")
    is_current = db.Column(db.Integer, default=1)
    is_likely_to_change = db.Column(db.Integer, default=0)
    created_date = db.Column(db.DateTime, index=True, nullable=False, default=datetime.utcnow())
    last_modified = db.Column(db.DateTime, index=True, nullable=False, default=datetime.utcnow())

    def __init__(self):
        # Ensure each record has created and last_modified dates
        logger.debug(f"id: {self.id}, created: {self.created_date}")
        print(f"id: {self.id}, created: {self.created_date}")
        if not self.created_date:
            self.created_date = datetime.utcnow()
            db.session.commit()

        if self.last_modified is None:
            self.last_modified = datetime.utcnow()
            db.session.commit()

    def to_dict(self):
        return {
            "id":                  self.id,
            "family_id":           self.family_id,
            "line_1":              self.line_1,
            "line_2":              self.line_2 if self.line_2 else None,
            "city":                self.city,
            "state":               self.state,
            "zip":                 self.zip,
            "country":             self.country,
            "is_current":          self.is_current,
            "is_likely_to_change": self.is_likely_to_change,
            "created_date":        self.created_date.strftime(
                "%Y-%m-%d %H:%M:%M.%f") if self.created_date else None,
            "last_modified":       self.last_modified.strftime(
                "%Y-%m-%d %H:%M:%M.%f") if self.last_modified else None
        }

    def __repr__(self):
        return f"Address(id={self.id}, fam={self.family_id}, L1={self.line_1}, L2={self.line_1}, " \
               f"city={self.city}, state={self.state}, zip={self.zip}, is_current={self.is_current}"


class Family(db.Model):
    __tablename__ = "family"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    nickname = db.Column(db.String)
    surname = db.Column(db.String)
    formal_name = db.Column(db.String)
    relationship = db.Column(db.String)
    relationship_type = db.Column(db.String)
    addresses = db.relationship("Address", backref="family", lazy=True)

    def to_dict(self):
        return {
            "id":                self.id,
            "nickname":          self.nickname,
            "surname":           self.surname,
            "formal_name":       self.formal_name,
            "relationship":      self.relationship,
            "relationship_type": self.relationship_type
        }

    def __repr__(self):
        return f"Family(id={self.id}, nick={self.nickname}, surname={self.surname}, " \
               f"rel={self.relationship}, primary_address={self.primary_address_id}"


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    name = db.Column(db.String)
    date = db.Column(db.DateTime)
    year = db.Column(db.Integer, default=datetime.now().year)
    is_archived = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id":          self.id,
            "name":        self.name,
            "date":        self.date.strftime("%Y-%m-%d") if self.date else None,
            "year":        self.year,
            "is_archived": self.is_archived
        }

    def __repr__(self):
        return f"Event(id={self.id}, name={self.name}, date={self.date}, year={self.year}, " \
               f"is_archived={self.is_archived}"


class Gift(db.Model):
    __tablename__ = "gift"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    description = db.Column(db.String)
    notes = db.Column(db.String)

    def to_dict(self):
        return {
            "id":          self.id,
            "event_id":    self.event_id,
            "family_id":   self.family_id,
            "description": self.description,
            "notes":       self.notes
        }

    def __repr__(self):
        return f"Gift(id={self.id}, event={self.event_id}, fam={self.family_id}, " \
               f"description={self.description}, notes={self.notes}"


class Card(db.Model):
    __tablename__ = "card"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    was_card_sent = db.Column(db.Integer, default=0)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    gift_id = db.Column(db.Integer, db.ForeignKey('gift.id'))
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))

    def to_dict(self):
        return {
            "id":            self.id,
            "was_card_sent": self.was_card_sent,
            "event_id":      self.event_id,
            "gift_id":       self.gift_id,
            "family_id":     self.family_id,
            "address_id":    self.address_id
        }

    def __repr__(self):
        return f"Card(id={self.id}, was_card_sent={self.was_card_sent}, event={self.event_id}, " \
               f"gift={self.gift_id}, fam={self.family_id}, address={self.address_id}"
