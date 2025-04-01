from env import Env
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from report.misc.google import GoogleConn, Scope

env = Env()

sql_engine = create_engine(env.NETFLOW_POSTGRES_URL)
sql_Base = declarative_base()
sql_SessionLocal = sessionmaker(bind=sql_engine)

default_google_conn = GoogleConn(
    credentials_path=env.GOOGLE_CREDENTIALS_FILE,
    scopes=[Scope.GoogleDrive, Scope.GoogleSheets],
)
