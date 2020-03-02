import requests

from unittest import TestCase

HOST = '127.0.0.1'
PORT = 5000

# HOST = 'localhost'
# PORT = 5000

base_url = f'http://{HOST}:{PORT}'

data = {
    'phone': '15191292433',
    'token': 'fac806dc6501fae31a93ccb15619ccf4'
}

vdata = {
    'vphone': '15191292433',
    'vtoken': '861b652042aa28d9e20c1f59c0d61278'
}


class TestUserApi(TestCase):
    def test_a_send_code(self):
        url = base_url + f'/api/code/?phone={data["phone"]}'
        resp = requests.get(url)
        print(resp.json())

    def test_b_regist(self):
        url = base_url + '/api/regist/'
        resp = requests.post(url, json={
            'name': 'admin',
            'phone': data['phone'],
            'code': '0819',
            'password': 'admin'  # 密文要求（前端）：需要使用hash算法
        })
        print(resp.json())

    def test_c_login(self):
        url = base_url + '/api/login/'
        resp = requests.post(url, json={
            'phone': data['phone'],
            'password': '123456'
        })
        resp_data = resp.json()
        print(resp_data)
        if resp_data['state'] == 0:
            data['token'] = resp_data['token']

    def test_d_login(self):
        url = base_url + '/api/modify_auth/'
        resp = requests.post(url, json={
            'token': data['token'],
            'password': 'admin',
            'new_password': '123456',
        })
        resp_data = resp.json()
        print(resp_data)

    def test_e_upload_head(self):
        url = base_url + "/api/upload_head/"
        resp = requests.post(url, files={
            'head': ('mm6.jpg', open('mm6.jpg', 'rb'), 'image/jpeg')
        }, cookies={'token': data['token']})
        print(resp.json())

    # @blue.route('/userinfo/', methods=["PUT"])
    def test_f_update_userinfo(self):
        url = base_url + "/api/userinfo/"
        resp = requests.put(url, json={
            'email': "1593073434@qq.com",
            'address': "陕西西安",
            'note': '这个人很懒，什么也没有留下！'},
                            cookies={'token': data['token']})
        print(resp.json())

    def test_g_set_usercaipu(self):
        url = base_url + "/api/addcaipu/"
        resp = requests.post(url, json={
            'cp_title': "一品豆腐",
            'cpimg': 'https://bkimg.cdn.bcebos.com/pic/1ad5ad6eddc451dac80ab698b6fd5266d11632c0?x-bce-process=image/resize,m_lfit,w_268,limit_1/format,f_jpg',
            'cp_info': '一品豆腐，是一道经典的特色名菜，属于孔府菜。此菜白细鲜嫩，营养丰富而为人所喜食。冯骥才先生曾说过养育龙种，豆腐有功。',
            'cp_url': 'http://www.xiachufang.com/recipe/104202592/',
            'flid': '2'}, cookies={'token': data['token']})
        print(resp.json())

    def test_h_get_usercaipu(self):
        url = base_url + "/api/querycaipu/"
        resp = requests.get(url, cookies={'token': data['token']})
        print(resp.json())

    def test_i_del_usercaipu(self):
        url = base_url + "/api/delcaipu/"
        resp = requests.delete(url, json={
            'cp_title': "一品豆腐"
        }, cookies={'token': data['token']})
        print(resp.json())

    def test_j_update_usercaipu(self):
        url = base_url + "/api/updatecaipu/"
        resp = requests.put(url, json={
            'old_cp_title': "一品豆腐",
            'cp_title': "二品豆腐",
            'flid': '2'}, cookies={'token': data['token']})
        print(resp.json())

    def test_k_vendorregist(self):
        url = base_url + "/api/vendorregist/"
        resp = requests.post(url, json={
            'vname': '佳佳乐超市',
            'vphone': vdata['vphone'],
            'vcode': '2508',
            'vaddress': '陕西西安科技路',
            'vpassword': '123456'  # 密文要求（前端）：需要使用hash算法
        })
        print(resp.json())

    def test_l_vendorlogin(self):
        url = base_url + "/api/vendorlogin/"
        resp = requests.post(url, json={
            'vphone': vdata['vphone'],
            'vpassword': '123456'
        })
        resp_data = resp.json()
        print(resp_data)
        if resp_data['state'] == 0:
            vdata['vtoken'] = resp_data['token']

    def test_m_addgoods(self):
        # "gname", "gimg", "gpreprice", "gprice", "gnum"
        url = base_url + '/api/addgoods/'
        resp = requests.post(url, json={
            'gname': "豆角",
            'gimg': "https://imgsa.baidu.com/baike/pic/item/c9fcc3cec3fdfc0372a50bc8db3f8794a5c226e5.jpg",
            'gpreprice': '3.0',
            'gprice': "3.5",
            'gnum': "1000"}, cookies={'token': vdata['vtoken']})
        print(resp.json())

    def test_n_querygoods(self):
        url = base_url + "/api/querygoods/"
        resp = requests.get(url, cookies={'token': vdata['vtoken']})
        print(resp.json())

    def test_o_delgoods(self):
        url = base_url + "/api/delgoods/"
        resp = requests.delete(url, json={
            'gname': "豆角"
        }, cookies={'token': vdata['vtoken']})
        print(resp.json())

    def test_p_updategoods(self):
        url = base_url + "/api/updategoods/"
        resp = requests.put(url, json={
            'old_gname': "豆角",
            'gname': "豇豆",
            'flid': '2'}, cookies={'token': vdata['vtoken']})
        print(resp.json())

    def test_q_dianzan(self):
        url = base_url + "/api/dianzan/"
        resp = requests.post(url, json={
            'cpid': "1"}, cookies={'token': data['token']})
        print(resp.json())

    def test_r_sumdianzan(self):
        url = base_url + '/api/sumdianzan/?cpid=1'
        resp = requests.get(url)
        print(resp.json())

    def test_s_pinglun(self):
        url = base_url + "/api/pinglun/"
        resp = requests.post(url, json={
            'cpid': "1",
            'pl_text': "这道菜看着很有食欲,爷i了！"
        }, cookies={'token': data['token']})
        print(resp.json())

    def test_t_delpinglun(self):
        url = base_url + "/api/delpinglun/"
        resp = requests.post(url, json={
            'cpid': "1"
        }, cookies={'token': data['token']})
        print(resp.json())

    def test_u_sumpinglun(self):
        url = base_url + '/api/sumpinglun/?cpid=1'
        resp = requests.get(url)
        print(resp.json())

    def test_v_zhuanfa(self):
        url = base_url + "/api/zhuanfa/"
        resp = requests.post(url, json={
            'cpid': "1"
        }, cookies={'token': data['token']})
        print(resp.json())

    def test_w_sumzhuanfa(self):
        url = base_url + '/api/sumzhuanfa/?cpid=1'
        resp = requests.get(url)
        print(resp.json())

    def test_x_order(self):
        url = base_url + '/api/order/'
        resp = requests.post(url,
                             json={
                                 'goods': [{'gid': '1', 'gnum': 5},
                                           {'gid': '2', 'gnum': 5}]
                             }, cookies={'token': data['token']})
        print(resp.json())

    def test_y_guanzhu(self):
        url = base_url + "/api/guanzhu/"
        resp = requests.post(url, json={
            'followed_id': "2"}, cookies={'token': data['token']})
        print(resp.json())

    def test_z_sumfollowed(self):
        url = base_url + '/api/sumguanzhu/?followed_id=1'
        resp = requests.get(url)
        print(resp.json())

    def test_1_allfans(self):
        url = base_url + '/api/allfans/?followed_id=2'
        resp = requests.get(url)
        print(resp.json())

    def test_2_searchcaipu(self):
        url = base_url + '/api/searchcaipu/?cpname=西红柿炒鸡蛋'
        resp = requests.get(url)
        print(resp.json())

    def test_3_topcaipu(self):
        url = base_url + '/api/topcaipu/'
        resp = requests.get(url)
        print(resp.json())
