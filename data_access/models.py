from sqlalchemy import Table, Column, MetaData, Integer, String, DateTime

metadata = MetaData()

data = Table(
    "data",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('uuid', String),
    Column('name', String),
    Column('size', String),
    Column('format', String),
    Column('extension', String),
    Column('was_uploaded_on', DateTime)
)

def create_schema(engine):
    metadata.create_all(bind=engine)
