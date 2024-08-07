from sqlalchemy import insert, select, inspect
from sqlalchemy.orm import sessionmaker

from data_access.models import data, create_schema


# b'form-data; name="file"; filename="ghjunyhgfg87654kjngvd-bkmijrfd04532lkijtgr-hbedkuj73982jhbgvf-a-foto-naruto-uzumaki-3853528402.jpg"'
# b'image/jpeg'


class Repository:
    def __init__(self, connection) -> None:
        self.connection = connection
    
    def create_schema_if_not_exists(self):
        insp = inspect(self.connection)
        if not insp.has_table("test.db", schema="data"):
            create_schema(self.connection)

    def insert_new_metadata(self, metadata):
        with self.connection.connect() as conn:
            conn.execute(insert(data).values(
                uuid=metadata.uuid,
                name=metadata.filename,
                size=metadata.filesize,
                format=metadata.content_type,
                extension=metadata.extension,
                was_uploaded_on=metadata.was_uploaded_on,
            ))
            conn.commit()


    def get_metadata_by_uuid(self, uuid):
        with self.connection.connect() as conn:
            return conn.execute(select(data).where(data.c.uuid == uuid)).first()


    def get_all_metadata(self):
        with self.connection.connect() as conn:
            return conn.execute(select(data))


    def delete_old_records(self, timestamp):
        session = sessionmaker(bind=self.connection)()
        try:
            with session.begin():
                session.execute(data.delete().where(data.c.was_uploaded_on < timestamp))

            session.commit()
        
        except Exception as e:
            session.rollback()
            return e
