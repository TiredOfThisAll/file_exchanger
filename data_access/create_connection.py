import sqlalchemy


def create_connection(connection_str):
    engine = sqlalchemy.create_engine(
        connection_str
    )
    return engine
