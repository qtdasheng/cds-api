from redis import Redis

rd = Redis('127.0.0.1', port=6379, db=0, decode_responses=True)

if __name__ == '__main__':
    print(rd.keys('*'))