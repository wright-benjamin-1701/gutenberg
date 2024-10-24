import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

database_url = "sqlite:///gutenberg.db"

engine = create_engine(database_url)

Base = declarative_base()
class Asset(Base):
    __tablename__ = "assets"
    url = Column("url", String(), index=True, primary_key=True)
    name = Column("name", String())

class DownloadsData(Base):
    __tablename__ = "downloadsdata"
    retrieved = Column("retrieved", Float(), primary_key=True)
    count = Column("count", Integer())
    bucket = Column("bucket", String(), primary_key=True)
    asset = Column("asset", ForeignKey(Asset.url), primary_key=True)

class SiteContent(Base):
    __tablename__ = "sitecontents"
    retrieved = Column("retrieved", Float(), primary_key=True)
    url = Column("url", String())
    content = Column("content", Text())

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

session.close()