from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import pymysql

Base = declarative_base()
metadata = Base.metadata

# yyserver1是在 {C:/windows/System32/drivers}/etc/hosts中配置域名
engine = create_engine('mysql+pymysql://root:root@139.129.93.165:3307/chidiansha')
engine.connect()
Session = sessionmaker(bind=engine)
session = Session()

db_conn = pymysql.Connection(host='139.129.93.165',
                             port=3307,
                             user='root',
                             password='root',
                             db='chidiansha',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
