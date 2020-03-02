# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class DjangoContentType(db.Model):
    __tablename__ = 'django_content_type'
    __table_args__ = (
        db.Index('django_content_type_app_label_model_76bd3d3b_uniq', 'app_label', 'model'),
    )

    id = db.Column(db.Integer, primary_key=True)
    app_label = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)



class DjangoMigration(db.Model):
    __tablename__ = 'django_migrations'

    id = db.Column(db.Integer, primary_key=True)
    app = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    applied = db.Column(db.DateTime, nullable=False)



class DjangoSession(db.Model):
    __tablename__ = 'django_session'

    session_key = db.Column(db.String(40), primary_key=True)
    session_data = db.Column(db.String, nullable=False)
    expire_date = db.Column(db.DateTime, nullable=False, index=True)



class TCaipu(db.Model):
    __tablename__ = 't_caipu'

    cpid = db.Column(db.Integer, primary_key=True)
    cp_title = db.Column(db.String(50), nullable=False)
    cpimg = db.Column(db.String(200), nullable=False)
    cp_info = db.Column(db.String(200))
    cp_url = db.Column(db.String(200), nullable=False)
    cp_cretime = db.Column(db.DateTime, nullable=False)
    flid = db.Column(db.ForeignKey('t_cpfenlei.flid'), index=True)
    uid = db.Column(db.ForeignKey('t_user.uid'), nullable=False, index=True)

    t_cpfenlei = db.relationship('TCpfenlei', primaryjoin='TCaipu.flid == TCpfenlei.flid', backref='t_caipus')
    t_user = db.relationship('TUser', primaryjoin='TCaipu.uid == TUser.uid', backref='t_caipus')



class TCpfenlei(db.Model):
    __tablename__ = 't_cpfenlei'

    flid = db.Column(db.Integer, primary_key=True)
    flname = db.Column(db.String(50), nullable=False)
    flnote = db.Column(db.String(200))



class TDianzan(db.Model):
    __tablename__ = 't_dianzan'

    dzid = db.Column(db.Integer, primary_key=True)
    cpid = db.Column(db.ForeignKey('t_caipu.cpid'), index=True)
    uid = db.Column(db.ForeignKey('t_user.uid'), index=True)

    t_caipu = db.relationship('TCaipu', primaryjoin='TDianzan.cpid == TCaipu.cpid', backref='t_dianzans')
    t_user = db.relationship('TUser', primaryjoin='TDianzan.uid == TUser.uid', backref='t_dianzans')



class TFeedback(db.Model):
    __tablename__ = 't_feedback'

    id = db.Column(db.Integer, primary_key=True)
    fkcontent = db.Column(db.String(200), nullable=False)
    fkcretime = db.Column(db.DateTime, nullable=False)
    uid = db.Column(db.ForeignKey('t_user.uid'), nullable=False, index=True)

    t_user = db.relationship('TUser', primaryjoin='TFeedback.uid == TUser.uid', backref='t_feedbacks')



class TGood(db.Model):
    __tablename__ = 't_goods'

    gid = db.Column(db.Integer, primary_key=True)
    gname = db.Column(db.String(50), nullable=False)
    gimg = db.Column(db.String(200), nullable=False)
    gpreprice = db.Column(db.Float(asdecimal=True), nullable=False)
    gprice = db.Column(db.Float(asdecimal=True), nullable=False)
    gnum = db.Column(db.Integer, nullable=False)
    gcretime = db.Column(db.DateTime, nullable=False)
    vid = db.Column(db.ForeignKey('t_vendor.vid'), index=True)

    t_vendor = db.relationship('TVendor', primaryjoin='TGood.vid == TVendor.vid', backref='t_goods')



class THistory(db.Model):
    __tablename__ = 't_history'

    hid = db.Column(db.Integer, primary_key=True)
    hcre_time = db.Column(db.DateTime, nullable=False)
    cpid = db.Column(db.ForeignKey('t_caipu.cpid'), index=True)
    uid = db.Column(db.ForeignKey('t_user.uid'), index=True)

    t_caipu = db.relationship('TCaipu', primaryjoin='THistory.cpid == TCaipu.cpid', backref='t_histories')
    t_user = db.relationship('TUser', primaryjoin='THistory.uid == TUser.uid', backref='t_histories')



class TMessage(db.Model):
    __tablename__ = 't_message'

    create_time = db.Column(db.DateTime, nullable=False)
    message_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.String)
    link_url = db.Column(db.String(100))
    note = db.Column(db.String)
    state = db.Column(db.Integer, nullable=False)



class TOrder(db.Model):
    __tablename__ = 't_order'

    oid = db.Column(db.Integer, primary_key=True)
    oprice = db.Column(db.Float(asdecimal=True), nullable=False)
    ocretime = db.Column(db.DateTime, nullable=False)
    ostate = db.Column(db.Integer, nullable=False)
    uid = db.Column(db.ForeignKey('t_user.uid'), nullable=False, index=True)

    t_user = db.relationship('TUser', primaryjoin='TOrder.uid == TUser.uid', backref='t_orders')



class TOrdergood(db.Model):
    __tablename__ = 't_ordergoods'

    ogid = db.Column(db.Integer, primary_key=True)
    ognum = db.Column(db.Integer, nullable=False)
    gid = db.Column(db.ForeignKey('t_goods.gid'), nullable=False, index=True)
    oid = db.Column(db.ForeignKey('t_order.oid'), nullable=False, index=True)

    t_good = db.relationship('TGood', primaryjoin='TOrdergood.gid == TGood.gid', backref='t_ordergoods')
    t_order = db.relationship('TOrder', primaryjoin='TOrdergood.oid == TOrder.oid', backref='t_ordergoods')



class TPinglun(db.Model):
    __tablename__ = 't_pinglun'

    plid = db.Column(db.Integer, primary_key=True)
    pl_text = db.Column(db.String(200))
    cpid = db.Column(db.ForeignKey('t_caipu.cpid'), index=True)
    uid = db.Column(db.ForeignKey('t_user.uid'), index=True)

    t_caipu = db.relationship('TCaipu', primaryjoin='TPinglun.cpid == TCaipu.cpid', backref='t_pingluns')
    t_user = db.relationship('TUser', primaryjoin='TPinglun.uid == TUser.uid', backref='t_pingluns')



class TRel(db.Model):
    __tablename__ = 't_rel'

    rel_id = db.Column(db.Integer, primary_key=True)
    fans_id = db.Column(db.Integer)
    followed_id = db.Column(db.Integer)



class TRenwu(db.Model):
    __tablename__ = 't_renwu'

    rwid = db.Column(db.Integer, primary_key=True)
    rwname = db.Column(db.Integer)
    rwexp = db.Column(db.Integer)
    note = db.Column(db.String(200))
    cpid = db.Column(db.ForeignKey('t_caipu.cpid'), index=True)

    t_caipu = db.relationship('TCaipu', primaryjoin='TRenwu.cpid == TCaipu.cpid', backref='t_renwus')



class TShoucang(db.Model):
    __tablename__ = 't_shoucang'

    scid = db.Column(db.Integer, primary_key=True)
    sccretime = db.Column(db.DateTime, nullable=False)
    cpid = db.Column(db.ForeignKey('t_caipu.cpid'), nullable=False, index=True)
    uid = db.Column(db.ForeignKey('t_user.uid'), nullable=False, index=True)

    t_caipu = db.relationship('TCaipu', primaryjoin='TShoucang.cpid == TCaipu.cpid', backref='t_shoucangs')
    t_user = db.relationship('TUser', primaryjoin='TShoucang.uid == TUser.uid', backref='t_shoucangs')



class TSysMenu(db.Model):
    __tablename__ = 't_sys_menu'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    parent_id = db.Column(db.Integer)
    ord = db.Column(db.Integer)
    url = db.Column(db.String(50))



class TSysRole(db.Model):
    __tablename__ = 't_sys_role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    code = db.Column(db.String(10), nullable=False, unique=True)



class TSysRoleMenu(db.Model):
    __tablename__ = 't_sys_role_menu'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer)
    menu_id = db.Column(db.Integer)



class TSysUser(db.Model):
    __tablename__ = 't_sys_user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    auth_string = db.Column(db.String(32), nullable=False)
    nick_name = db.Column(db.String(20))
    role_id = db.Column(db.Integer, nullable=False)



class TUser(db.Model):
    __tablename__ = 't_user'

    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(50))
    address = db.Column(db.String(100))
    head = db.Column(db.String(200))
    ucretime = db.Column(db.DateTime, nullable=False)
    note = db.Column(db.String(200))
    exp = db.Column(db.Integer)
    level = db.Column(db.Integer)



class TVendor(db.Model):
    __tablename__ = 't_vendor'

    vid = db.Column(db.Integer, primary_key=True)
    vname = db.Column(db.String(50))
    vpassword = db.Column(db.String(50))
    vphone = db.Column(db.String(50))
    vaddress = db.Column(db.String(100))
    v_cretime = db.Column(db.DateTime, nullable=False)



class TZhuanfa(db.Model):
    __tablename__ = 't_zhuanfa'

    zfid = db.Column(db.Integer, primary_key=True)
    zfurl = db.Column(db.String(200))
    cpid = db.Column(db.ForeignKey('t_caipu.cpid'), nullable=False, index=True)
    uid = db.Column(db.ForeignKey('t_user.uid'), nullable=False, index=True)

    t_caipu = db.relationship('TCaipu', primaryjoin='TZhuanfa.cpid == TCaipu.cpid', backref='t_zhuanfas')
    t_user = db.relationship('TUser', primaryjoin='TZhuanfa.uid == TUser.uid', backref='t_zhuanfas')
