#!/usr/bin/python3
# coding: utf-8
import hashlib
import os
import uuid
from datetime import datetime

from flask import Blueprint, Response
from flask import request, jsonify
from sqlalchemy import or_, and_, not_

import settings
from db import session
from apiapp.models import *
from common import code_, cache_, token_, oss_
from . import validate_json, validate_params

blue = Blueprint('user_api', __name__)


@blue.route('/code/', methods=['GET'])
def get_code():
    phone = request.args.get('phone')
    if phone:
        code_.send_code(phone)
        return jsonify({
            'state': 0,
            'msg': '验证码已发送'
        })

    return jsonify({
        'state': 1,
        'msg': '手机号不能为空'
    })


@blue.route('/regist/', methods=['POST'])
def regist():
    # 要求JSON数据格式：
    valid_fields = {"name", "phone", "code", "password"}
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    # 验证参数的完整性
    if set(data.keys()) == valid_fields:
        # 验证输入的验证码是否正确
        if not code_.valid_code(data['phone'], data['code']):
            return jsonify({
                'state': 2,
                'msg': '验证码输入错误，请确认输入的验证码'
            })

        nameexists = session.query(session.query(TUser).filter(TUser.name == data['name']).exists()).scalar()
        phoneexists = session.query(session.query(TUser).filter(TUser.phone == data['phone']).exists()).scalar()
        if nameexists:
            return jsonify({
                'state': 6,
                'msg': '用户名已被使用，请重新输入'
            })
        if phoneexists:
            return jsonify({
                'state': 6,
                'msg': '手机号已被使用，请重新输入'
            })
        user = TUser()
        user.name = data.get('name')
        user.phone = data.get('phone')
        user.password = data.get('password')
        user.level = 0
        user.exp = 0
        user.ucretime = datetime.now()

        session.add(user)
        session.commit()

        # 向前端返回信息中，包含一个与用户匹配的token(有效时间为一周)
        # 1. 基于uuid+user_id生成token
        # 2. 将token和user_id保存到缓存（cache_.save_token(token, user_id)）
        # JWT 单点授权登录
        token = token_.gen_token(user.uid)
        cache_.add_token(token, user.uid)
    else:
        return jsonify({
            'state': 1,
            'msg': '参数不完速，详情请查看接口文档'
        })

    return jsonify({
        'state': 0,
        'msg': '注册并登录成功',
        'token': token
    })


@blue.route('/login/', methods=['POST'])
def login():
    resp = validate_json()
    if resp: return resp

    resp = validate_params('phone', 'password')
    if resp: return resp

    data = request.get_json()
    try:
        user = session.query(TUser).filter(or_(TUser.phone == data['phone'],
                                               TUser.name == data['phone']),
                                           TUser.password == data['password']).one()

        token = token_.gen_token(user.uid)
        cache_.add_token(token, user.uid)

        resp: Response = jsonify({
            'state': 0,
            'msg': '登录成功',
            'token': token
        })

        # 设置响应对象的cookie，向客户端响应cookie
        resp.set_cookie('token', token)
        return resp
    except:
        pass

    return jsonify({
        'state': 4,
        'msg': '用户名或口令输入错误',
    })


@blue.route('/modify_auth/', methods=['POST'])
def modify_auth():
    resp = validate_json()
    if resp: return resp

    resp = validate_params('new_password', 'password', 'token')
    if resp: return resp

    data = request.get_json()

    try:
        user_id = cache_.get_user_id(data['token'])
        if not user_id:
            jsonify({
                'state': 3,
                'msg': '登录已期，需要重新登录并获取新的token',
            })

        user = session.query(TUser).get(int(user_id))
        if user.password == data['password']:
            user.password = data['new_password']
            session.add(user)
            session.commit()

            return jsonify({
                'state': 0,
                'msg': '修改成功'
            })
        return jsonify({
            'state': 4,
            'msg': '原口令不正确'
        })
    except:
        pass

    return jsonify({
        'state': 3,
        'msg': 'token已无效，尝试重新登录',
    })


@blue.route('/upload_head/', methods=["POST"])
def upload_head():
    # 前端上传图片的两种方式（文件对象上传， base64字符串上传）
    # FileStorage:  'content_length', 'content_type', 'filename', 'headers', 'mimetype', 'save',
    upload_file = request.files.get('head')
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取

    print(upload_file.filename, upload_file.content_type, upload_file.mimetype)

    user_id = cache_.get_user_id(token)
    file_name = upload_file.filename

    save_file_path = os.path.join(settings.TEMP_DIR, file_name)
    # 保存上传的文件到临时的目录中
    upload_file.save(save_file_path)

    # 将临时的文件上传到oss服务器中， 并获取到缩小后的图片URL
    head_url = oss_.upload_head(user_id, file_name, save_file_path)

    # 将head_url保存到用户的表中
    user = session.query(TUser).get(user_id)
    user.head = f'{user_id}-{file_name}'  # 存储oss上的key对象
    session.add(user)
    session.commit()

    # 将头像的URL 存到 redis中
    cache_.save_head_url(user.head, head_url)

    # 删除临时的文件
    os.remove(save_file_path)

    return jsonify({
        'state': 0,
        'msg': '上传成功',
        'head': head_url
    })


@blue.route('/head/', methods=["GET"])
def get_head():
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)
    user = session.query(TUser).get(user_id)
    head_url = cache_.get_head_url(user.head)
    if not head_url:
        head_url = oss_.get_oss_img_url(user.head)
        cache_.save_head_url(user.head, head_url)

    return jsonify({
        'state': 0,
        'head': head_url
    })


# 用户更新个人资料

@blue.route('/userinfo/', methods=["PUT"])
def updateinfo():
    # 要求JSON数据格式：
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)
    user = session.query(TUser).filter(TUser.uid == user_id).first()

    user.email = data.get('email', user.email)
    user.address = data.get('address', user.address)
    user.note = data.get('note', user.note)

    session.commit()
    return jsonify({
        'state': 0,
        'msg': '个人信息修改成功！'
    })


# 用户上传菜谱
@blue.route('/addcaipu/', methods=["POST"])
def addcaipu():
    # 要求JSON数据格式：
    valid_fields = {"cp_title", "cpimg", "cp_info", "cp_url", "flid"}
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    # 验证参数的完整性
    if not set(data.keys()) == valid_fields:
        return jsonify({
            'state': 1,
            'msg': '参数不完速，详情请查看接口文档'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)
    caipuexists = session.query(
        session.query(TUser).filter(TCaipu.uid == user_id, TCaipu.cp_title == data['cp_title']).exists()).scalar()
    if caipuexists:
        return jsonify({
            'state': -1,
            'msg': '你已经添加过该菜谱了！'
        })
    else:
        caipu = TCaipu()
        caipu.cp_title = data.get('cp_title')
        caipu.cpimg = data.get('cpimg')
        caipu.cp_info = data.get('cp_info')
        caipu.cp_url = data.get('cp_url')
        caipu.flid = data.get('flid')
        caipu.uid = user_id
        caipu.cp_cretime = datetime.now()

        session.add(caipu)
        session.commit()
        return jsonify({
            'state': 0,
            'msg': '上传成功'
        })


# 用户查找自己上传的菜谱
@blue.route('/querycaipu/', methods=["GET"])
def querycaipu():
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)
    caipu = session.query(TCaipu).filter(TCaipu.uid == user_id).all()
    if caipu:
        data = [{'cpid': k.cpid,
                 'cp_title': k.cp_title,
                 'cpimg': k.cpimg,
                 'cp_info': k.cp_info,
                 'cp_url': k.cp_url,
                 'cp_cretime': k.cp_cretime}
                for k in caipu]
        return jsonify({
            'state': 0,
            'msg': '获取成功',
            "data": data
        })
    else:
        return jsonify({
            'state': -1,
            'msg': "你还未上传菜单!"
        })


# 用户删除自己上传的菜谱
@blue.route('/delcaipu/', methods=["DELETE"])
def delcaipu():
    # 要求JSON数据格式：
    valid_fields = {"cp_title"}
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    # 验证参数的完整性
    if not set(data.keys()) == valid_fields:
        return jsonify({
            'state': 1,
            'msg': '参数不完速，详情请查看接口文档'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)

    caipuexists = session.query(
        session.query(TUser).filter(TCaipu.uid == user_id, TCaipu.cp_title == data['cp_title']).exists()).scalar()
    if caipuexists:
        session.query(TCaipu).filter(TCaipu.uid == user_id, TCaipu.cp_title == data['cp_title']).delete()
        session.commit()
        return jsonify({
            'state': 0,
            'msg': '菜谱删除成功！'
        })
    else:
        return jsonify({
            'state': -1,
            'msg': '删除失败，该菜谱不存在！'
        })


# 用户修改自己上传的菜谱
@blue.route('/updatecaipu/', methods=["PUT"])
def updatecaipu():
    # 要求JSON数据格式：
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)
    caipu = session.query(TCaipu).filter(TCaipu.uid == user_id, TCaipu.cp_title == data['old_cp_title']).first()

    caipu.cp_title = data.get('cp_title', caipu.cp_title)
    caipu.cpimg = data.get('cpimg', caipu.cpimg)
    caipu.cp_info = data.get('cp_info', caipu.cp_info)
    caipu.cp_url = data.get('cp_url', caipu.cp_url)
    caipu.flid = data.get('flid', caipu.flid)

    session.commit()
    return jsonify({
        'state': 0,
        'msg': '菜谱修改成功'
    })


# 商户注册
@blue.route('/vendorregist/', methods=['POST'])
def vendorregist():
    # 要求JSON数据格式：
    valid_fields = {"vname", "vphone", "vcode", "vpassword", "vaddress"}
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    # 验证参数的完整性
    if set(data.keys()) == valid_fields:
        # 验证输入的验证码是否正确
        if not code_.valid_code(data['vphone'], data['vcode']):
            return jsonify({
                'state': 2,
                'msg': '验证码输入错误，请确认输入的验证码'
            })

        nameexists = session.query(session.query(TVendor).filter(TVendor.vname == data['vname']).exists()).scalar()
        phoneexists = session.query(session.query(TVendor).filter(TVendor.vphone == data['vphone']).exists()).scalar()
        if nameexists:
            return jsonify({
                'state': 6,
                'msg': '商户名已被使用，请重新输入'
            })
        if phoneexists:
            return jsonify({
                'state': 6,
                'msg': '手机号已被使用，请重新输入'
            })
        vendor = TVendor()
        vendor.vname = data.get('vname')
        vendor.vphone = data.get('vphone')
        vendor.vpassword = data.get('vpassword')
        vendor.vaddress = data.get('vaddress')
        vendor.v_cretime = datetime.now()

        session.add(vendor)
        session.commit()

        # 向前端返回信息中，包含一个与用户匹配的token(有效时间为一周)
        # 1. 基于uuid+user_id生成token
        # 2. 将token和user_id保存到缓存（cache_.save_token(token, user_id)）
        # JWT 单点授权登录
        token = token_.gen_token(vendor.vid)
        cache_.add_token(token, vendor.vid)
    else:
        return jsonify({
            'state': 1,
            'msg': '参数不完速，详情请查看接口文档'
        })

    return jsonify({
        'state': 0,
        'msg': '注册并登录成功',
        'token': token
    })


# 商户登录
@blue.route('/vendorlogin/', methods=['POST'])
def vendorlogin():
    resp = validate_json()
    if resp: return resp

    resp = validate_params('vphone', 'vpassword')
    if resp: return resp

    data = request.get_json()
    try:
        vendor = session.query(TVendor).filter(or_(TVendor.vphone == data['vphone'],
                                                   TVendor.vname == data['vphone']),
                                               TVendor.vpassword == data['vpassword']).one()

        token = token_.gen_token(vendor.vid)
        cache_.add_token(token, vendor.vid)

        resp: Response = jsonify({
            'state': 0,
            'msg': '登录成功',
            'token': token
        })

        # 设置响应对象的cookie，向客户端响应cookie
        resp.set_cookie('token', token)
        return resp
    except:
        pass

    return jsonify({
        'state': 4,
        'msg': '用户名或口令输入错误',
    })


# 商户添加商品
@blue.route('/addgoods/', methods=['POST'])
def addgoods():
    # 要求JSON数据格式：
    valid_fields = {"gname", "gimg", "gpreprice", "gprice", "gnum"}
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    # 验证参数的完整性
    if not set(data.keys()) == valid_fields:
        return jsonify({
            'state': 1,
            'msg': '参数不完速，详情请查看接口文档'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    vid = cache_.get_user_id(token)
    caipuexists = session.query(
        session.query(TVendor).filter(TVendor.vid == vid, TGood.gname == data['gname']).exists()).scalar()
    if caipuexists:
        return jsonify({
            'state': -1,
            'msg': '你已经添加过该物品了！'
        })
    else:
        goods = TGood()
        goods.gname = data.get('gname')
        goods.gimg = data.get('gimg')
        goods.gpreprice = data.get('gpreprice')
        goods.gprice = data.get('gprice')
        goods.gnum = data.get('gnum')
        goods.vid = vid
        goods.gcretime = datetime.now()

        session.add(goods)
        session.commit()
        return jsonify({
            'state': 0,
            'msg': '商品添加成功'
        })


# 商户查询添加的商品
@blue.route('/querygoods/', methods=["GET"])
def querygoods():
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    vid = cache_.get_user_id(token)
    goods = session.query(TGood).filter(TGood.vid == vid).all()
    if goods:
        data = [{'gid': k.gid,
                 'gname': k.gname,
                 'gimg': k.gimg,
                 'gpreprice': float(k.gpreprice),
                 'gprice': float(k.gprice),
                 'gnum': k.gnum,
                 'gcretime': k.gcretime}
                for k in goods]
        return jsonify({
            'state': 0,
            'msg': '获取成功',
            "data": data
        })
    else:
        return jsonify({
            'state': -1,
            'msg': "你还未添加商品!"
        })


# 商户删除商品
@blue.route('/delgoods/', methods=["DELETE"])
def delgoods():
    # 要求JSON数据格式：
    valid_fields = {"gname"}
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    # 验证参数的完整性
    if not set(data.keys()) == valid_fields:
        return jsonify({
            'state': 1,
            'msg': '参数不完速，详情请查看接口文档'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    vid = cache_.get_user_id(token)

    goodsexists = session.query(
        session.query(TGood).filter(TGood.vid == vid, TGood.gname == data['gname']).exists()).scalar()
    if goodsexists:
        session.query(TGood).filter(TGood.vid == vid, TGood.gname == data['gname']).delete()
        session.commit()
        return jsonify({
            'state': 0,
            'msg': '商品删除成功！'
        })
    else:
        return jsonify({
            'state': -1,
            'msg': '删除失败，该商品不存在！'
        })


# 商户修改商品
@blue.route('/updategoods/', methods=["PUT"])
def updategoods():
    # 要求JSON数据格式：
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    vid = cache_.get_user_id(token)
    goods = session.query(TGood).filter(TGood.vid == vid, TGood.gname == data['old_gname']).first()

    goods.gname = data.get('gname', goods.gname)
    goods.gimg = data.get('gimg', goods.gimg)
    goods.gpreprice = data.get('gpreprice', goods.gpreprice)
    goods.gprice = data.get('gprice', goods.gprice)
    goods.gnum = data.get('gnum', goods.gnum)

    session.commit()
    return jsonify({
        'state': 0,
        'msg': '商品修改成功'
    })


# 用户对菜谱点赞/取消赞
@blue.route('/dianzan/', methods=['POST'])
def dianzan():
    # 要求JSON数据格式：
    valid_fields = {"cpid"}
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    # 验证参数的完整性
    if not set(data.keys()) == valid_fields:
        return jsonify({
            'state': 1,
            'msg': '参数不完速，详情请查看接口文档'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)
    zanexists = session.query(
        session.query(TDianzan).filter(TDianzan.uid == user_id, TDianzan.cpid == data['cpid']).exists()).scalar()
    if zanexists:
        session.query(TDianzan).filter(TDianzan.uid == user_id, TDianzan.cpid == data['cpid']).delete()
        session.commit()
        return jsonify({
            'state': 0,
            'msg': '取消了赞！'
        })
    else:
        dz = TDianzan()
        dz.cpid = data.get('cpid')
        dz.uid = user_id

        session.add(dz)
        session.commit()
        return jsonify({
            'state': 0,
            'msg': '点赞成功！'
        })


# 获取菜谱被赞次数
@blue.route('/sumdianzan/', methods=['GET'])
def sumdianzan():
    cpid = request.args.get('cpid')
    s = session.query(TDianzan).filter(TDianzan.cpid == cpid).count()
    return jsonify({
        'state': 0,
        'msg': '查询成功！',
        'count': s
    })


# 用户评论菜谱
@blue.route('/pinglun/', methods=['POST'])
def pinglun():
    # 要求JSON数据格式：
    valid_fields = {"cpid", "pl_text"}
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    # 验证参数的完整性
    if not set(data.keys()) == valid_fields:
        return jsonify({
            'state': 1,
            'msg': '参数不完速，详情请查看接口文档'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)

    pl = TPinglun()
    pl.pl_text = data.get('pl_text')
    pl.uid = user_id
    pl.cpid = data.get('cpid')

    session.add(pl)
    session.commit()
    return jsonify({
        'state': 0,
        'msg': '评论成功！'
    })


# 用户删除评论
@blue.route('/delpinglun/', methods=['POST'])
def delpinglun():
    # 要求JSON数据格式：
    valid_fields = {"cpid"}
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    # 验证参数的完整性
    if not set(data.keys()) == valid_fields:
        return jsonify({
            'state': 1,
            'msg': '参数不完速，详情请查看接口文档'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)
    pinglunexists = session.query(
        session.query(TPinglun).filter(TPinglun.uid == user_id, TPinglun.cpid == data['cpid']).exists()).scalar()
    if pinglunexists:
        session.query(TPinglun).filter(TPinglun.uid == user_id, TPinglun.cpid == data['cpid']).delete()
        session.commit()
        return jsonify({
            'state': 0,
            'msg': '你删除了对该菜谱的评论！'
        })
    else:
        return jsonify({
            'state': 0,
            'msg': '你还未对该菜谱进行评论！'
        })


@blue.route('/sumpinglun/', methods=['GET'])
def sumpinglun():
    cpid = request.args.get('cpid')
    s = session.query(TPinglun).filter(TPinglun.cpid == cpid).count()
    return jsonify({
        'state': 0,
        'msg': '查询成功！',
        'count': s
    })


# 用户转发菜谱
@blue.route('/zhuanfa/', methods=['POST'])
def zhuanfa():
    # 要求JSON数据格式：
    valid_fields = {"cpid"}
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    # 验证参数的完整性
    if not set(data.keys()) == valid_fields:
        return jsonify({
            'state': 1,
            'msg': '参数不完速，详情请查看接口文档'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)

    zf = TZhuanfa()
    zf.cpid = data.get('cpid')
    zf.zfurl = session.query(TCaipu).get(data.get('cpid')).cp_url
    zf.uid = user_id

    session.add(zf)
    session.commit()
    return jsonify({
        'state': 0,
        'msg': '转发成功！'
    })


# 获取菜谱转发次数
@blue.route('/sumzhuanfa/', methods=['GET'])
def sumzhuanfa():
    cpid = request.args.get('cpid')
    s = session.query(TZhuanfa).filter(TZhuanfa.cpid == cpid).count()
    return jsonify({
        'state': 0,
        'msg': '查询成功！',
        'count': s
    })


# 用户下订单
@blue.route('/order/', methods=['POST'])
def order():
    # 要求JSON数据格式：
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)
    total = 0.0
    for g in data['goods']:
        total += float(session.query(TGood).get(g['gid']).gprice) * g['gnum']
    o = TOrder()
    o.ocretime = datetime.now()
    o.uid = user_id
    o.ostate = 0
    o.oprice = total

    session.add(o)
    session.commit()

    for g in data['goods']:
        og = TOrdergood()
        og.gid = session.query(TGood).get(g['gid']).gid
        og.ognum = g['gnum']
        og.oid = o.oid
        session.add(og)
        session.commit()

    return jsonify({
        'state': 0,
        'msg': '下单成功'
    })


# 用户关注
@blue.route('/guanzhu/', methods=['POST'])
def guanzhu():
    # 要求JSON数据格式：
    valid_fields = {"followed_id"}
    data = request.get_json()  # 获取上传的json数据
    if data is None:
        return jsonify({
            'state': 4,
            'msg': '必须提供json格式的参数'
        })

    # 验证参数的完整性
    if not set(data.keys()) == valid_fields:
        return jsonify({
            'state': 1,
            'msg': '参数不完速，详情请查看接口文档'
        })
    token = request.cookies.get('token')  # 1. 从请求参数中获取  2. 从请求头的Cookie中获取
    user_id = cache_.get_user_id(token)

    relexists = session.query(
        session.query(TRel).filter(TRel.fans_id == user_id, TRel.followed_id == data['followed_id']).exists()).scalar()
    if relexists:
        session.query(TRel).filter(TRel.fans_id == user_id, TRel.followed_id == data['followed_id']).delete()
        session.commit()
        return jsonify({
            'state': 1,
            'msg': '取关成功！'
        })
    else:
        rel = TRel()
        rel.followed_id = data.get('followed_id')
        rel.fans_id = user_id

        session.add(rel)
        session.commit()
        return jsonify({
            'state': 0,
            'msg': '关注成功！'
        })


# 获取用户被关注人数
@blue.route('/sumguanzhu/', methods=['GET'])
def sumguanzhu():
    followed_id = request.args.get('followed_id')
    s = session.query(TRel).filter(TRel.followed_id == followed_id).count()
    return jsonify({
        'state': 0,
        'msg': '查询成功！',
        'count': s
    })


# 获取粉丝信息
@blue.route('/allfans/', methods=['GET'])
def allfans():
    followed_id = request.args.get('followed_id')
    fans = session.query(TRel).filter(TRel.followed_id == followed_id).all()
    if fans:
        fansinfo = []
        for f in fans:
            user = session.query(TUser).filter(TUser.uid == f.fans_id).first()
            fansinfo.append({'uid': user.uid, 'name': user.name})
        return jsonify({
            'state': 0,
            'msg': '获取成功！',
            "data": fansinfo
        })
    else:
        return jsonify({
            'state': -1,
            'msg': '该用户没有粉丝！',
        })


# 搜索菜谱
@blue.route('/searchcaipu/', methods=['GET'])
def searchcaipu():
    cpname = request.args.get('cpname')
    caipu = session.query(TCaipu).filter(TCaipu.cp_title == cpname).all()
    if caipu:
        data = [{'cpid': k.cpid,
                 'cp_title': k.cp_title,
                 'cpimg': k.cpimg,
                 'cp_info': k.cp_info,
                 'cp_url': k.cp_url,
                 'cp_cretime': k.cp_cretime}
                for k in caipu]
        return jsonify({
            'state': 0,
            'msg': '获取成功',
            "data": data
        })
    else:
        return jsonify({
            'state': -1,
            'msg': "抱歉，未找到该菜谱！"
        })


# 最受欢迎菜谱排名
@blue.route('/topcaipu/', methods=['GET'])
def topcaipu():
    cpid = list(set([cp.cpid for cp in session.query(TDianzan).all()]))
    topdit = [{"cp_title": session.query(TCaipu).filter(TCaipu.cpid == k).first().cp_title,
               "voted": session.query(TDianzan).filter(TDianzan.cpid == k).count()} for k in cpid]
    topdit = sorted(topdit, reverse=True, key=lambda x: x['voted'])
    return jsonify({
        'state': 0,
        'msg': "查询成功！",
        'data': topdit
    })
