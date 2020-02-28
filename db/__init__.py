from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import pymysql

Base = declarative_base()
metadata = Base.metadata

# yyserver1是在 {C:/windows/System32/drivers}/etc/hosts中配置域名
engine = create_engine('mysql+pymysql://root:073434@127.0.0.1:3306/chidiansha')
engine.connect()
Session = sessionmaker(bind=engine)
session = Session()

db_conn = pymysql.Connection(host='127.0.0.1',
                             port=3306,
                             user='root',
                             password='073434',
                             db='chidiansha',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
