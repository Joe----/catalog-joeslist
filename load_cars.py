from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, User, Item

engine = create_engine('sqlite:///joeslist.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# delete all data and reload
session.query(User).delete()
session.query(Category).delete()
session.query(Item).delete()

# Create user 1
User1 = User(name="Joe Burkhart", email="burkhart.joe@gmail.com",
             picture='')
session.add(User1)
session.commit()

# Create user 2
User2 = User(name="Some Guy", email="test@test.com",
             picture='')
session.add(User2)
session.commit()

# New Cat
category1 = Category(user_id=1, name="Junkers")
session.add(category1)
session.commit()

item = Item(user_id=1, year="1971", make="Ford", model="Pinto", miles="199000",
            description="Like new. Less than 200,000 miles. Never exploded.",
            price="500.00", category=category1)
session.add(item)
session.commit()

item = Item(user_id=2, year="1970", make="AMC", model="Gremlin", miles="13000",
            description="Ugly, but she runs! Must see this thing to believe.",
            price="800.00", category=category1)
session.add(item)
session.commit()

# New Cat
category2 = Category(user_id=1, name="Muscle Cars")
session.add(category2)
session.commit()

item = Item(user_id=1, year="1969", make="Chevrolet", model="Corvette",
            miles="2600", description="Cherry red, convertable chick magnet.",
            price="25000.00", category=category2)
session.add(item)
session.commit()

item = Item(user_id=2, year="1970", make="AMC", model="Rebel Machine",
            miles="1200", description="This thing rips! Really one of a kind.",
            price="25000.00", category=category2)
session.add(item)
session.commit()

# New Cat
category3 = Category(user_id=1, name="Classics")
session.add(category3)
session.commit()

item = Item(user_id=1, year="1969", make="Chevrolet", model="Corvette",
            miles="2600", description="Cherry red, amazing vette.",
            price="25000.00", category=category3)
session.add(item)
session.commit

item = Item(user_id=2, year="1967", make="Ford", model="Mustang", miles="4600",
            description="Beautiful, classic car. Mint condition. Drives fine.",
            price="25000.00", category=category3)
session.add(item)
session.commit()

# New Cat
category4 = Category(user_id=1, name="Plain Ole Cars")
session.add(category4)
session.commit()

item = Item(user_id=1, year="2015", make="Ford", model="Fusion", miles="44600",
            description="Great car. I think everyone has one of these.",
            price="22500.00", category=category4)
session.add(item)
session.commit()

item = Item(user_id=2, year="2015", make="Nissan", model="Maxima", miles="400",
            description="Must see this Maxima. Beautiful, and low miles.",
            price="37500.00", category=category4)
session.add(item)
session.commit()

# New Cat
category5 = Category(user_id=1, name="SUVs")
session.add(category5)
session.commit()

item = Item(user_id=1, year="2015", make="Chevrolet", model="Suburban",
            miles="26500", description="Fits a whole bascketball team.",
            price="25000.00", category=category5)
session.add(item)
session.commit()

item = Item(user_id=1, year="2016", make="Jeep", model="Cherokee",
            miles="36500", description="Reliable and just the right size.",
            price="19500.00", category=category5)
session.add(item)
session.commit()

# New Cat
category6 = Category(user_id=1, name="Pickups")
session.add(category6)
session.commit()

item = Item(user_id=1, year="2014", make="Chevrolet", model="Silverado",
            miles="38000", description="Great pickup. Haul your pigs around!",
            price="25000.00", category=category6)
session.add(item)
session.commit()

item = Item(user_id=1, year="2015", make="Ford", model="F150",
            miles="21000", description="Ford tough. Tow hitch, and all.",
            price="19200.00", category=category6)
session.add(item)
session.commit()

print("Added cars!")
