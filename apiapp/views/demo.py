import db
from db import session
from apiapp.models import *

# cp=session.query(TCaipu).filter(TCaipu.uid=="1").all()
# print(cp)
#
# data=[{'cpid': k.cpid,
#     'cp_title': k.cp_title,
#     'cpimg': k.cpimg,
#     'cp_info': k.cp_info,
#     'cp_url': k.cp_url,
#     'cp_cretime': k.cp_cretime}
#       for k in cp]
# print(data)

# query = session.query(TUser).filter(
#     TUser.name=='李少鹏',
#     TUser.phone == '15191292433'
# )
#
# ifexists = session.query(
#     query.exists()
# ).scalar()
# print(ifexists)

# caipu=session.query(TCaipu).filter(TCaipu.uid == "1",TCaipu.cp_title=="一品豆腐").first()
# print(caipu)

# user = session.query(TCaipu).filter(TCaipu.uid == 1).first()
# print(user)

# goods = session.query(TGood).filter(TGood.vid == 1).all()
# print(goods[0].gprice)

# s=session.query(TDianzan).filter(TDianzan.cpid == 1).count()
# print(s)

# print(session.query(TCaipu).get(1).cp_url)

# fans=session.query(TRel).filter(TRel.followed_id == 2).all()
# if fans:
#     fansinfo=[]
#     for f in fans:
#         user=session.query(TUser).filter(TUser.uid == f.fans_id)
#         fansinfo.append({'uid':user.uid,'uname':user.name})

# cpid = list(set([cp.cpid for cp in session.query(TDianzan).all()]))
# topdit = [{"cpid": k, "voted": session.query(TDianzan).filter(TDianzan.cpid == k).count()} for k in cpid]
# topdit=sorted(topdit, reverse=True, key=lambda x: x['voted'])
# print(topdit)

cpid = list(set([cp.cpid for cp in session.query(TDianzan).all()]))
topdit = [{"cpname": session.query(TCaipu).filter(TCaipu.cpid==k).first().cp_title, "voted": session.query(TDianzan).filter(TDianzan.cpid == k).count()} for k in cpid]
topdit=sorted(topdit, reverse=True, key=lambda x: x['voted'])
print(topdit)