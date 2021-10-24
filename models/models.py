from logging import getLogger
from datetime import datetime
from backend import db

logger = getLogger()


class Address(db.Model):
    """
    Table to store the address info for each family / household.
    Each family may have multiple addresses.
    """

    # Set the name of this table
    __tablename__ = 'address'

    # Unique identifier is a simple auto-increment integer handled by the db
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    # Related family_id for this address record
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))

    # First line of the street address
    line_1 = db.Column(db.String)

    # Second line of the street address, typically used for apartment / unit number
    line_2 = db.Column(db.String)

    # Doesn't really need a comment, but it looks weird without one
    city = db.Column(db.String)

    # Defining these as `state` & `zip` effectively pigeonholes the app as US-only, but
    #  the holidays are coming soon and I need to solve for the 98% use case right now
    state = db.Column(db.String)
    zip = db.Column(db.String)

    # Storing the country enables us to create a simple, dirty workaround for non-US addresses...
    country = db.Column(db.String, default="United States")

    # ...the `full_address` field!  For non-US addresses, the front end will copy/pasta
    #  this multi-line text blob as the mailing address
    full_address = db.Column(db.BLOB)

    # Quick way to identify stale data
    is_current = db.Column(db.Integer, default=1)

    # All apartment addresses will default to 1 (True)
    is_likely_to_change = db.Column(db.Integer, default=0)

    # Storing some basic metadata is helpful
    created_date = db.Column(db.DateTime, index=True, nullable=False, default=datetime.utcnow())
    last_modified = db.Column(db.DateTime, index=True, nullable=False, default=datetime.utcnow())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ensure each record has created and last_modified dates
        if not self.created_date:
            now = datetime.utcnow()
            logger.debug(f"No created_date found for address_id={self.id}.  Setting to {now}.")
            self.created_date = now
            self.last_modified = now
            db.session.commit()

        if not self.last_modified:
            self.last_modified = datetime.utcnow()
            db.session.commit()

        # For apartment-dwellers, override the default value for is_likely_to_change
        if self.line_2 and "is_likely_to_change" not in kwargs.keys():
            self.is_likely_to_change = 1

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
            "full_address":        self.full_address if self.full_address else None,
            "is_current":          self.is_current,
            "is_likely_to_change": self.is_likely_to_change,
            "created_date":        self.created_date.strftime(
                "%Y-%m-%d %H:%M:%M.%f") if self.created_date else None,
            "last_modified":       self.last_modified.strftime(
                "%Y-%m-%d %H:%M:%M.%f") if self.last_modified else None
        }

    def __repr__(self):
        return f"Address(id={self.id}, fam={self.family_id}, L1={self.line_1}, L2={self.line_1}, " \
               f"city={self.city}, state={self.state}, zip={self.zip}, country={self.country}, " \
               f"full_addy={self.full_address}, is_current={self.is_current}"


class Family(db.Model):
    """
    Table to store data about each family (household?) in the database.
    This schema is almost certainly not optimally efficient, but even worrying
    about that is firmly out of scope.
    """

    # Set the name of this table
    __tablename__ = "family"

    # Unique identifier is a simple auto-increment integer handled by the db
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    # Human-friendly reference for a particular family
    nickname = db.Column(db.String, unique=True)

    # Primary surname for this family.  Households with multiple surnames will be challenging
    #  to implement; I'll need to find an elegant solution for this down the road.
    surname = db.Column(db.String)

    # When addressing a formal letter, how should this household be addressed?  Examples:
    #  Mr. & Mrs. John Doe
    #  Dr. Jane Doe & Mr. Nicholas Smith
    #  Dave & Pat Johnson
    formal_name = db.Column(db.String)

    # Family or Friends?
    relationship = db.Column(db.String)

    # List: Parents, Grandparents, Siblings, Aunts & Uncles, Cousins, Childhood friends,
    #  Family friends, Work friends, Colleagues, Neighbors, Acquaintances, etc.
    relationship_type = db.Column(db.String)

    # For family relationships, did these originate from mine or from my wife's side of the family?
    family_side = db.Column(db.String)

    # Easy SQLAlchemy backref for addresses which match this family.  Not a discrete data point.
    addresses = db.relationship("Address", backref="family", lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id":                self.id,
            "nickname":          self.nickname,
            "surname":           self.surname,
            "formal_name":       self.formal_name,
            "relationship":      self.relationship,
            "relationship_type": self.relationship_type,
            "family_side":       self.family_side
        }

    def __repr__(self):
        return f"Family(id={self.id}, nick={self.nickname}, surname={self.surname}, " \
               f"rel={self.relationship}, rel_type={self.relationship_type}, " \
               f"family_side={self.family_side}"


class Event(db.Model):
    # Set the name of this table
    __tablename__ = "event"

    # Unique identifier is a simple auto-increment integer handled by the db
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
    # Set the name of this table
    __tablename__ = "gift"

    # Unique identifier is a simple auto-increment integer handled by the db
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    description = db.Column(db.String)
    notes = db.Column(db.String)

    def to_dict(self):
        return {
            "id":          self.id,
            "event_id":    self.event_id,
            "address_id":  self.family_id,
            "description": self.description,
            "notes":       self.notes
        }

    def __repr__(self):
        return f"Gift(id={self.id}, event={self.event_id}, fam={self.family_id}, " \
               f"description={self.description}, notes={self.notes}"


class Card(db.Model):
    # Set the name of this table
    __tablename__ = "card"

    # Unique identifier is a simple auto-increment integer handled by the db
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
