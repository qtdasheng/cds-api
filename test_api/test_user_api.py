import requests

from unittest import TestCase

HOST = '139.129.93.165'
PORT = 5001

# HOST = 'localhost'
# PORT = 5000

base_url = f'http://{HOST}:{PORT}'

data = {
    'phone': '15191292433',
    'token': '8896e19de5232acf8ae368a01e9b085a'
}


class TestUserApi(TestCase):
    def test_a_send_code(self):
        url = base_url + f'/api/code/?phone={data["phone"]}'
        resp = requests.get(url)
        print(resp.json())

    def test_b_regist(self):
        url = base_url + '/api/regist/'
        resp = requests.post(url, json={
            'name': '李少鹏',
            'phone': data['phone'],
            'code': '1480',
            'password': 'admin'  # 密文要求（前端）：需要使用hash算法
        })
        print(resp.json())

    def test_c_login(self):
        url = base_url + '/api/login/'
        resp = requests.post(url, json={
            'phone': data['phone'],
            'password': 'admin'
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
        url = base_url+"/api/upload_head/"
        resp = requests.post(url, files={
            'head': ('mm6.jpg', open('mm6.jpg', 'rb'), 'image/jpeg')
        }, cookies={'token': data['token']})
        print(resp.json())
