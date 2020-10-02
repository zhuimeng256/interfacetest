import requests


class RequestUtil:
    def __init__(self):
        pass

    def request(self, url, method, params=None, headers=None, content_type=None):
        try:
            if method == "get":
                res = requests.get(url=url, params=params, headers=headers).json()
                return res
            elif method == "post":
                if content_type == "application/json":
                    res = requests.post(url=url, json=params, headers=headers).json()
                    return res
                else:
                    res = requests.post(url=url, data=params, headers=headers).json()
                    return res
            else:
                print("request is not allow")

        except Exception as e:
            print("http请求报错:{0}".format(e))


if __name__ == '__main__':
    # url = "https://api.xdclass.net/pub/api/v1/web/all_category"
    # r = RequestUtil()
    # result = r.request(url, 'get')
    # print(result)

    url = "https://api.xdclass.net/pub/api/v1/web/web_login"
    r = RequestUtil()
    data = {"phone": "13113777555", "pwd": "1234567890"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    result = r.request(url, 'post', params=data, headers=headers)
    print(result)