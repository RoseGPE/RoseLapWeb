from setuptools import setup

setup(name="RoseLapWeb", version="6.0", description="Laptime Simulation Package", url="http://github.com/RoseGPE/RoseLapWeb", author="Thad Hughes et al", author_email="hughes.thad@gmail.com", license="", packages=[], 
	install_requires=[
		'ruamel.yaml',
		'web.py',
		'scipy',
		'matplotlib',
		'numpy',
		'sqlalchemy'
	])

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