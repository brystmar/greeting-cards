"""
Define the data model for each database table.
"""

from logging import getLogger
from datetime import datetime, timezone
from backend import db
from helpers.helpers import convert_to_bool

logger = getLogger()


class Address(db.Model):
    """
    Stores the mailing address(es) for a given household.
    Note: Each household may have multiple addresses.
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

    # Doesn't really need a comment, but this looks weird without one
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
    is_current = db.Column(db.String, default="True")

    # All apartment addresses will default to True
    is_likely_to_change = db.Column(db.String, default="False")

    # When a household has more than 1 address, which one should the card be mailed to?
    mail_the_card_to_this_address = db.Column(db.String, default="True")

    # Storing basic metadata is helpful
    created_date = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now(timezone.utc))
    last_modified = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now(timezone.utc))

    # Additional context about this particular address
    notes = db.Column(db.String)

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
            "is_current":          convert_to_bool(self.is_current),
            "is_likely_to_change": convert_to_bool(self.is_likely_to_change),
            "mail_the_card_to_this_address": convert_to_bool(self.mail_the_card_to_this_address),
            "created_date":        self.created_date.strftime(
                "%Y-%m-%d %H:%M:%S%z") if self.created_date else datetime.now(timezone.utc),
            "last_modified":       self.last_modified.strftime(
                "%Y-%m-%d %H:%M:%S%z") if self.last_modified else datetime.now(timezone.utc),
            "notes":               self.notes
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ensure each record has created and last_modified dates
        if not self.created_date:
            now = datetime.now(timezone.utc)
            logger.debug(f"No created_date found for address_id={self.id}.  Setting to {now}.")
            self.created_date = now
            self.last_modified = now

        # For apartment-dwellers, override the default value for is_likely_to_change
        # if self.line_2 and "is_likely_to_change" not in kwargs.keys():
        #     self.is_likely_to_change = True

        # Convert the provided values for checkbox fields to boolean
        self.is_current = convert_to_bool(self.is_current)
        self.is_likely_to_change = convert_to_bool(self.is_likely_to_change)
        self.mail_the_card_to_this_address = convert_to_bool(self.mail_the_card_to_this_address)

    def __repr__(self):
        return f"Addy(id={self.id}, hh={self.household_id}, L1={self.line_1}, L2={self.line_1}, " \
               f"city={self.city}, state={self.state}, zip={self.zip}, country={self.country}, " \
               f"full_addy={self.full_address}, is_current={self.is_current}, " \
               f"is_likely_to_change={self.is_likely_to_change}, " \
               f"mail_the_card_to_this_address={self.mail_the_card_to_this_address}, " \
               f"created_date={self.created_date}, last_modified={self.last_modified})"


class Household(db.Model):
    """
    Store data about each household, which is defined as a group of people living together.
    This schema is certainly not optimally designed, but even the act of worrying
    about that is firmly out of scope at this time.
    """

    # Set the name of this table
    __tablename__ = "household"

    # Unique identifier is a simple auto-increment integer
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    # Human-friendly reference for a particular household
    #  Setting a default helps for debugging since uniqueness is enforced
    nickname = db.Column(db.String, unique=True, nullable=False, index=True,
                         default=f"An unknown {datetime.now(timezone.utc)}")

    # First names of the heads of household
    first_names = db.Column(db.String)

    # Primary surname for this household.  Households with multiple surnames will be challenging
    # to implement; I'll find a better solution for this down the road.
    surname = db.Column(db.String)

    # To whom should letters be addressed for this household?
    address_to = db.Column(db.String)

    # For fancypants formal letters, how should this household be addressed?  Examples:
    #  Mr. & Mrs. John Doe
    #  Dr. Jane Doe & Mr. Nicholas Smith
    #  Dave & Pat Johnson
    formal_name = db.Column(db.String)

    # Where do we know these people from?
    known_from = db.Column(db.String)

    # How do we know these people?  Immediate Household, Grandparents, Aunts & Uncles, Cousins,
    # Childhood friends, Family friends, Work friends, Colleagues, Neighbors, Acquaintances, etc.
    relationship = db.Column(db.String)

    # Defines this household as Family, Friends, or Acquaintances
    relationship_type = db.Column(db.String)

    # For family relationships, did these originate from mine or from my spouse's side?
    family_side = db.Column(db.String)

    # Names of children living in this household
    # Good candidate for being broken out into its own table later, if the need arises
    kids = db.Column(db.String)

    # Pets are important household members too!
    pets = db.Column(db.String)

    # Do we want this household on our holiday/Christmas card list?  0 = False, 1 = True
    should_receive_holiday_card = db.Column(db.String, default="False")

    # Are these people still relevant to us?
    is_relevant = db.Column(db.String, default="True")

    # Storing basic metadata is helpful
    created_date = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now(timezone.utc))
    last_modified = db.Column(db.DateTime, index=True, nullable=False, default=datetime.now(timezone.utc))

    # Additional context about this household
    notes = db.Column(db.String)

    # Easy SQLAlchemy backref for addresses which match this household
    addresses = db.relationship("Address", backref="household", lazy=True)

    def to_dict(self):
        return {
            "id":                          self.id,
            "nickname":                    self.nickname,
            "first_names":                 self.first_names,
            "surname":                     self.surname,
            "address_to":                  self.address_to,
            "formal_name":                 self.formal_name,
            "known_from":                  self.known_from,
            "relationship":                self.relationship,
            "relationship_type":           self.relationship_type,
            "family_side":                 self.family_side,
            "kids":                        self.kids,
            "pets":                        self.pets,
            "should_receive_holiday_card": convert_to_bool(self.should_receive_holiday_card),
            "is_relevant":                 convert_to_bool(self.is_relevant),
            "created_date":                self.created_date.strftime(
                "%Y-%m-%d %H:%M:%S%z") if self.created_date else datetime.now(timezone.utc),
            "last_modified":               self.last_modified.strftime(
                "%Y-%m-%d %H:%M:%S%z") if self.last_modified else datetime.now(timezone.utc),
            "notes":                       self.notes
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Ensure each record has created and last_modified dates
        if not self.created_date:
            now = datetime.now(timezone.utc)
            logger.debug(f"No created_date found for hh_id={self.id}.  Setting to {now}.")
            self.created_date = now
            self.last_modified = now

        # Convert the provided value for should_receive_holiday_card to boolean
        self.should_receive_holiday_card = convert_to_bool(self.should_receive_holiday_card)

    def __repr__(self):
        return f"Household(id={self.id}, nick={self.nickname}, first={self.first_names}, " \
               f"surname={self.surname}, rel={self.relationship}, addr_to={self.address_to}" \
               f"known_from={self.known_from}, " \
               f"rel_type={self.relationship_type}, family_side={self.family_side}, " \
               f"kids={self.kids}, pets={self.pets}, notes={self.notes}, " \
               f"should_receive_card={self.should_receive_holiday_card}, relevant={self.is_relevant}, " \
               f"created_date={self.created_date}, last_modified={self.last_modified})"


class Event(db.Model):
    """
    Store data about events that we'll want to send greeting (or thank you) cards for.
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
    year = db.Column(db.Integer, default=datetime.now(timezone.utc).year)

    # Events get archived once all greeting (or thank-you) cards are sent
    is_archived = db.Column(db.String, default="False")

    # Additional context about this event
    notes = db.Column(db.String)

    def to_dict(self):
        return {
            "id":          self.id,
            "name":        self.name,
            "date":        self.date.strftime("%Y-%m-%d") if self.date else None,
            "year":        self.year,
            "is_archived": convert_to_bool(self.is_archived),
            "notes":       self.notes
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Convert the provided value for is_archived to boolean
        self.is_archived = convert_to_bool(self.is_archived)

    def __repr__(self):
        return f"Event(id={self.id}, name={self.name}, date={self.date}, year={self.year}, " \
               f"is_archived={self.is_archived}, notes={self.notes})"


class Gift(db.Model):
    """
    Store data about gifts received from a particular event.
    """

    # Set the name of this table
    __tablename__ = "gift"

    # Unique identifier is a simple auto-increment integer
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    # Event that the gift was from
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

    # Household who gifted the item
    household_id = db.Column(db.Integer)

    # List of households who contributed to this gift
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
    should_a_card_be_sent = db.Column(db.String, default="True")

    # Additional context about this gift
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
            "should_a_card_be_sent": convert_to_bool(self.should_a_card_be_sent),
            "notes":                 self.notes
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Convert the provided value for should_a_card_be_sent to boolean
        self.should_a_card_be_sent = convert_to_bool(self.should_a_card_be_sent)

    def __repr__(self):
        return f"Gift(id={self.id}, event={self.event_id}, hhs={self.households}, " \
               f"description={self.description}, origin={self.origin}, type={self.type}, " \
               f"date={self.date}, card?={self.should_a_card_be_sent}, notes={self.notes})"


class Card(db.Model):
    """
    Stores relational data about cards sent for each event (and/or gift).
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
    gift_id = db.Column(db.Integer, db.ForeignKey('gift.id'))

    # Which event is this for?
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

    # Storing the hh_id for clarity, despite being able to reference it using the `gift_id` above
    # Another reminder that getting to 1NF isn't important for this project :)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'))

    # Indicates which address the card was intended for
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))

    # Stores the date
    date_sent = db.Column(db.Date, index=True)

    # Additional context about this card
    notes = db.Column(db.String)

    def to_dict(self):
        return {
            "id":           self.id,
            "type":         self.type,
            "status":       self.status,
            "gift_id":      self.gift_id,
            "event_id":     self.event_id,
            "household_id": self.household_id,
            "address_id":   self.address_id,
            "date_sent":    self.date_sent.strftime("%Y-%m-%d") if self.date_sent else None,
            "notes":        self.notes
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"Card(id={self.id}, type={self.type}, status={self.status}, " \
               f"event={self.event_id}, gift={self.gift_id}, hh={self.household_id}, " \
               f"address={self.address_id}, " \
               f"date_sent={self.date_sent.strftime('%Y-%m-%d') if self.date_sent else None}, " \
               f"notes={self.notes})"


class Picklists(db.Model):
    """
    Stores a comma-separated list of picklist values for fields shown as picklists in the UI.
    Probably not an optimal way of storing these data.  However, since not all options may have an
    associated record, this is the quick & dirty solution we'll use.
    """
    # Set the name of this table
    __tablename__ = "picklist_values"

    # Version is the primary key
    version = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    # Household picklists
    household_relationship = db.Column(db.String)
    household_relationship_type = db.Column(db.String)
    household_family_side = db.Column(db.String)

    # Card picklists
    card_type = db.Column(db.String)
    card_status = db.Column(db.String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Convert the provided value for is_default to boolean
        self.is_default = convert_to_bool(self.is_default)

    def to_dict(self):
        return {
            "version":                     self.version,
            "household_relationship":      self.household_relationship.split(","),
            "household_relationship_type": self.household_relationship_type.split(","),
            "household_family_side":       self.household_family_side.split(","),
            "card_type":                   self.card_type.split(","),
            "card_status":                 self.card_status.split(",")
        }

    def __repr__(self):
        return f"PicklistValues(version: {self.version} \n" \
               f"\thh_relationship: {self.household_relationship} \n" \
               f"\thh_relationship_type: {self.household_relationship_type} \n" \
               f"\thh_family_side: {self.household_family_side} \n" \
               f"\tcard_type: {self.card_type} \n" \
               f"\tcard_status: {self.card_status})"
