from logging import getLogger
from datetime import datetime
from backend import db
from distutils.util import strtobool

logger = getLogger()


class Address(db.Model):
    """
    Table to store the mailing address for a specified household.
    Each household may have multiple addresses.
    """

    # Set the name of this table
    __tablename__ = 'address'

    # Unique identifier is a simple auto-increment integer handled by the db
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    # Related household_id for this address record
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'))

    # First line of the street address
    line_1 = db.Column(db.String)

    # Second line of the street address, typically used for apartment / unit number
    line_2 = db.Column(db.String)

    # Doesn't really need a comment, but it looks weird without one
    city = db.Column(db.String)

    # Defining these as `state` & `zip` effectively pigeonholes the app as US-only, but
    # the holidays are coming soon and I need to solve for the 98% use case right now
    state = db.Column(db.String)
    zip = db.Column(db.String)

    # Storing the country enables us to create a simple, dirty workaround for non-US addresses...
    country = db.Column(db.String, default="United States")

    # ...the `full_address` field!  For non-US addresses, the front end will copy/pasta
    # this multi-line text blob as the mailing address
    full_address = db.Column(db.String)

    # Quick way to flag stale data, or for friends who move to a temporary spot
    is_current = db.Column(db.Integer, default=1)

    # All apartment addresses will default to 1 (True)
    is_likely_to_change = db.Column(db.Integer, default=0)

    # Storing basic metadata is helpful
    created_date = db.Column(db.DateTime, index=True, nullable=False, default=datetime.utcnow())
    last_modified = db.Column(db.DateTime, index=True, nullable=False, default=datetime.utcnow())

    def to_dict(self):
        return {
            "id":                  self.id,
            "household_id":        self.household_id,
            "line_1":              self.line_1,
            "line_2":              self.line_2,
            "city":                self.city,
            "state":               self.state,
            "zip":                 self.zip,
            "country":             self.country,
            "full_address":        self.full_address,
            "is_current":          self.is_current,
            "is_likely_to_change": self.is_likely_to_change,
            "created_date":        self.created_date.strftime(
                "%Y-%m-%d %H:%M:%M.%f") if self.created_date else datetime.utcnow(),
            "last_modified":       self.last_modified.strftime(
                "%Y-%m-%d %H:%M:%M.%f") if self.last_modified else datetime.utcnow()
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ensure each record has created and last_modified dates
        if not self.created_date:
            now = datetime.utcnow()
            logger.debug(f"No created_date found for address_id={self.id}.  Setting to {now}.")
            self.created_date = now
            self.last_modified = now

        # For apartment-dwellers, override the default value for is_likely_to_change
        if self.line_2 and "is_likely_to_change" not in kwargs.keys():
            self.is_likely_to_change = 1

        # Ensure is_current has a binary `int` value
        if self.is_current:
            if self.is_current not in (0, 1):
                self.is_current = strtobool(str(self.is_current))
        else:
            self.is_current = 1

        # Ensure is_likely_to_change has a binary `int` value
        if self.is_likely_to_change:
            if self.is_likely_to_change not in (0, 1):
                self.is_likely_to_change = strtobool(str(self.is_likely_to_change))
        else:
            self.is_likely_to_change = 0

    def __repr__(self):
        return f"Addy(id={self.id}, hh={self.household_id}, L1={self.line_1}, L2={self.line_1}, " \
               f"city={self.city}, state={self.state}, zip={self.zip}, country={self.country}, " \
               f"full_addy={self.full_address}, is_current={self.is_current})"


class Household(db.Model):
    """
    Table to store data about each household.
    This schema is certainly not optimally designed, but even the act of worrying
    about that is firmly out of scope at this time.
    """

    # Set the name of this table
    __tablename__ = "household"

    # Unique identifier is a simple auto-increment integer
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    # Human-friendly reference for a particular household
    nickname = db.Column(db.String, unique=True)

    # First names of the heads of household
    first_names = db.Column(db.String)

    # Primary surname for this household.  Households with multiple surnames will be challenging
    # to implement; I'll find a better solution for this down the road.
    surname = db.Column(db.String)

    # When addressing a formal letter, how should this household be addressed?  Examples:
    #  Mr. & Mrs. John Doe
    #  Dr. Jane Doe & Mr. Nicholas Smith
    #  Dave & Pat Johnson
    formal_name = db.Column(db.String)

    # How do we know these people?  Immediate Household, Grandparents, Aunts & Uncles, Cousins,
    # Childhood friends, Family friends, Work friends, Colleagues, Neighbors, Acquaintances, etc.
    relationship = db.Column(db.String)

    # Defines this household as either Friends or Family
    relationship_type = db.Column(db.String)

    # For family relationships, did these originate from mine or from my spouse's side?
    family_side = db.Column(db.String)

    # Names of children living in this household
    # Good candidate for being broken out into its own table later, if the need arises
    kids = db.Column(db.String)

    # Pets are important household members too!
    pets = db.Column(db.String)

    # Do we want this household on our holiday/Christmas card list?  0 = False, 1 = True
    should_receive_holiday_card = db.Column(db.Integer, default=0)

    # Additional notes about this household
    notes = db.Column(db.String)

    # Easy SQLAlchemy backref for addresses which match this household
    addresses = db.relationship("Address", backref="household", lazy=True)

    def to_dict(self):
        return {
            "id":                          self.id,
            "nickname":                    self.nickname,
            "first_names":                 self.first_names,
            "surname":                     self.surname,
            "formal_name":                 self.formal_name,
            "relationship":                self.relationship,
            "relationship_type":           self.relationship_type,
            "family_side":                 self.family_side,
            "kids":                        self.kids,
            "pets":                        self.pets,
            "should_receive_holiday_card": self.should_receive_holiday_card,
            "notes":                       self.notes
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ensure should_receive_holiday_card has a binary `int` value
        if self.should_receive_holiday_card:
            if self.should_receive_holiday_card not in (0, 1):
                self.should_receive_holiday_card = strtobool(str(self.should_receive_holiday_card))
        else:
            self.should_receive_holiday_card = 0

    def __repr__(self):
        return f"Household(id={self.id}, nick={self.nickname}, first={self.first_names}, " \
               f"surname={self.surname}, rel={self.relationship}, " \
               f"rel_type={self.relationship_type}, family_side={self.family_side}, " \
               f"kids={self.kids}, pets={self.pets}, notes={self.notes}, " \
               f"should_receive_card={self.should_receive_holiday_card})"


class Event(db.Model):
    """
    Table to store data about events that we'll want to send greeting (or thank you) cards for.
    """

    # Set the name of this table
    __tablename__ = "event"

    # Unique identifier is a simple auto-increment integer
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    # Descriptive name of the event
    name = db.Column(db.String)

    # Date of the event, if applicable
    date = db.Column(db.Date)

    # For annual events like holiday cards, it makes more sense to only capture the event's year
    year = db.Column(db.Integer, default=datetime.utcnow().year)

    # Events get archived once all greeting (or thank-you) cards are sent
    is_archived = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id":          self.id,
            "name":        self.name,
            "date":        self.date.strftime("%Y-%m-%d") if self.date else None,
            "year":        self.year,
            "is_archived": self.is_archived
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ensure is_archived has a binary `int` value
        if self.is_archived:
            if self.is_archived not in (0, 1):
                self.is_archived = strtobool(str(self.is_archived))
        else:
            self.is_archived = 0

    def __repr__(self):
        return f"Event(id={self.id}, name={self.name}, date={self.date}, year={self.year}, " \
               f"is_archived={self.is_archived})"


class Gift(db.Model):
    """
    Table to store data about gifts received from a particular event.
    """

    # Set the name of this table
    __tablename__ = "gift"

    # Unique identifier is a simple auto-increment integer
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    # Event that the gift was from
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

    # List of households who contributed to this gift
    # households = db.Column(db.ARRAY)
    households = db.Column(db.Integer)

    # Description of the item(s).  You'll send one thank-you card for each gift record.
    description = db.Column(db.String)

    # Basic category for this gift, i.e.: Book, Clothing, Toy
    type = db.Column(db.String)

    # Where the gift originated from (store where it was purchased, homemade, etc.), if known
    # We collected this data but probably don't care about it; will likely remove in the future
    origin = db.Column(db.String)

    # Date the gift was received
    # Another data point we collected but probably won't keep long-term
    date = db.Column(db.Date, index=True)

    # Some friends & family ask you not to send a thank-you card
    # TODO: Update all boolean db values to string?
    should_a_card_be_sent = db.Column(db.Integer, default=1)

    # Other notes
    notes = db.Column(db.String)

    def to_dict(self):
        return {
            "id":                    self.id,
            "event_id":              self.event_id,
            "households":            self.households,
            "description":           self.description,
            "type":                  self.type,
            "origin":                self.origin,
            "date":                  self.date.strftime("%Y-%m-%d") if self.date else None,
            "should_a_card_be_sent": self.should_a_card_be_sent,
            "notes":                 self.notes
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ensure should_a_card_be_sent has a binary `int` value
        if self.should_a_card_be_sent:
            if self.should_a_card_be_sent not in (0, 1):
                self.should_a_card_be_sent = strtobool(str(self.should_a_card_be_sent))
        else:
            self.should_a_card_be_sent = 1

    def __repr__(self):
        return f"Gift(id={self.id}, event={self.event_id}, hhs={self.households}, " \
               f"description={self.description}, origin={self.origin}, type={self.type}, " \
               f"date={self.date}, card?={self.should_a_card_be_sent}, notes={self.notes})"


class Card(db.Model):
    """
    Table which stores relational data about cards sent for each event (and/or gift).
    """

    # Set the name of this table
    __tablename__ = "card"

    # Unique identifier is a simple auto-increment integer
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    # What type of card is this?  Options: Thank You, Holiday, Greeting, Other
    type = db.Column(db.String)

    # Defines the lifecycle status of this card: New --> Written --> Addressed --> Sent.
    status = db.Column(db.String, default="New", nullable=False)

    # If this is a thank-you card, which gift is this card for?
    # TODO: Must change to a 1-to-many relationship
    gift_id = db.Column(db.Integer, db.ForeignKey('gift.id'))

    # Storing the hh_id for clarity, despite being able to reference it using the `gift_id` above
    # Another reminder that getting to 1NF isn't important for this project :)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'))

    # Indicates which address the card was intended for
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))

    # Stores the date
    date_sent = db.Column(db.Date, index=True)

    def to_dict(self):
        return {
            "id":           self.id,
            "type":         self.type,
            "status":       self.status,
            "event_id":     self.event_id,
            "gift_id":      self.gift_id,
            "household_id": self.household_id,
            "address_id":   self.address_id,
            "date_sent":    self.date_sent.strftime("%Y-%m-%d") if self.date_sent else None
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"Card(id={self.id}, type={self.type}, status={self.status}, " \
               f"event={self.event_id}, gift={self.gift_id}, hh={self.household_id}, " \
               f"address={self.address_id}, " \
               f"date_sent={self.date_sent.strftime('%Y-%m-%d') if self.date_sent else None})"
