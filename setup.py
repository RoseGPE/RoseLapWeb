from database import *

Base.metadata.create_all(engine) # create all tables

db_session = scoped_session(sessionmaker(bind=engine))

print("Input username.\n>", end="")
name = input()
print("Input password.\n>", end="")
password = input()

user = User(name, password)

db_session.add(user)
db_session.commit()
db_session.close()