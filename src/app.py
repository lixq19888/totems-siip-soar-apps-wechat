# -*- encoding:utf-8 -*-
# abtnetworks.com
#
import os
from SoarAction import SoarAction
from SoarUtils import output_handler
import requests
import json


LogFile = "wechat.log"
APP_NAME = "WeChat"
ACTION_LIST = ["TEXT"]

class WeChatApp(SoarAction):
    __version__ = "1.0.0"

    def __init__(self, app_name, action_list, input_data, action_select):
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LogFile)
        super(WeChatApp, self).__init__(app_name, log_path, action_list, input_data, action_select)

    def get_access_token(self):
        """
        获取微信公众号的access_token值
        """
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format( self.setting_param_dict["appID"],self.setting_param_dict["appsecret"] )
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36'
        }
        response = requests.get(url, headers=headers).json()
        access_token = response.get('access_token')
        return access_token

    def get_openid(self):
        """
        获取所有粉丝的openid
        """
        next_openid = ''
        url_openid = 'https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s&next_openid=%s' % (self.get_access_token(), next_openid)
        ans = requests.get(url_openid)
        open_ids = json.loads(ans.content)['data']['openid']
        return open_ids

    @output_handler
    def TEXT(self):
        """
        给所有粉丝发送文本消息
        """
        url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={}".format(self.get_access_token())

        try:
            openids = self.get_openid()
            if openids != '':
                for open_id in openids:
                    body = {
                        "touser": open_id,
                        "msgtype":"text",
                        "text":
                        {
                            "content": self.params['content']
                        }
                    }
                    data = bytes(json.dumps(body, ensure_ascii=False).encode('utf-8'))
                    response = requests.post(url, data=data)
                    # 这里可根据回执code进行判定是否发送成功(也可以根据code根据错误信息)
                    result = response.json()
                    print(result)
                    return self.get_response_json('send success')
            else:
                return self.get_error_response('当前没有用户关注该公众号')
        except Exception as e:
            print('error', e)
            return self.get_error_response('send fail')

    def sendAllmsg(self):
        """
        认证号给所有粉丝发送文本消息
        """
        url = "https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={}".format(self.access_token)
        a= {
            "filter": {
                "is_to_all": True
            },
            "text": {
                "content": "CONTENT"
            },
            "msgtype": "text"
        }
        resp = requests.post(url=url, headers={'Content-Type': 'application/json'}, json=a)
        print( resp.content )

    def sendAllmsgPre(self):
        """
        预览-给所有粉丝发送文本消息
        """
        url = "https://api.weixin.qq.com/cgi-bin/message/mass/preview?access_token={}".format(self.access_token)
        a= {
                    "touser": "o7reb6Usq2DEsWj2PeH60SRt0yec",
                    "msgtype":"text",
                    "text":
                    {
                        "content": "safdsafdsaf大苏打撒撒反对撒发射点"
                    }
                }
        resp = requests.post(url=url, headers={'Content-Type': 'application/json'}, json=a)
        print( resp.content )


    def upload_media(self, media_type, media_path):
        """
        上传临时文件到微信服务器，并获取该文件到meida_id
        """
        url = 'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={}&type={}'.format(self.access_token, media_type)
        meida = {
            'media': open(media_path, 'rb')
        }
        rsponse = requests.post(url, files=meida)
        parse_json = json.loads(rsponse.content.decode())
        return parse_json.get('media_id')

    def send_media_to_user(self, media_type, media_path):
        """
        给所有粉丝发送媒体文件，媒体文件以meida_id表示
        """
        media_id = self.upload_media(media_type, media_path)
        url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={}'.format(self.access_token)
        if self.opend_ids != '':
            for open_id in self.opend_ids:
                if media_type == "image":
                    body = {
                        "touser": open_id,
                        "msgtype": "image",
                        "image":
                            {
                                "media_id": media_id
                            }
                    }
                if media_type == "voice":
                    body = {
                        "touser": open_id,
                        "msgtype": "voice",
                        "voice":
                            {
                                "media_id": media_id
                            }
                    }
                data = bytes(json.dumps(body, ensure_ascii=False).encode('utf-8'))
                print(data)
                response = requests.post(url, data=data)
                # 这里可根据回执code进行判定是否发送成功(也可以根据code根据错误信息)
                result = response.json()
                print(result)
        else:
            print("当前没有用户关注该公众号！")


if __name__ == "__main__":
    input_data = None
    action = None
    # input_data = r'%7B%22languageType%22%3A%22PYTHON3%22%2C%22playBookVersion%22%3A%221.0.0%22%2C%22appId%22%3A%22f14ebb301580404aa7e6733379043700%22%2C%22appVersion%22%3A%221.0.0%22%2C%22appName%22%3A%22WECHAT%22%2C%22description%22%3A%22%E5%BE%AE%E4%BF%A1%E5%85%AC%E4%BC%97%E5%8F%B7%E6%8E%A8%E9%80%81%E6%B6%88%E6%81%AF%22%2C%22brief%22%3A%22%E4%B8%BA%E6%99%BA%E8%83%BD%E7%BB%88%E7%AB%AF%E6%8F%90%E4%BE%9B%E5%8D%B3%E6%97%B6%E9%80%9A%E8%AE%AF%E6%9C%8D%E5%8A%A1%E7%9A%84%E5%85%8D%E8%B4%B9%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F%22%2C%22tags%22%3A%5B%22WECHAT%22%5D%2C%22categories%22%3A%7B%22name%22%3A%22%E6%B6%88%E6%81%AF%E9%80%9A%E7%9F%A5%22%2C%22parent%22%3A%22%E9%BB%98%E8%AE%A4%E5%88%86%E7%B1%BB%22%7D%2C%22contactInfo%22%3A%7B%22name%22%3A%22ABT%20%E5%AE%89%E5%8D%9A%E9%80%9A%22%2C%22url%22%3A%22http%3A%2F%2Fwww.abtnetworks.com%2Fwelcome.html%22%2C%22email%22%3A%22XXX%40sapling.com.cn%22%2C%22phone%22%3A%22XXXXX%22%2C%22description%22%3A%22XXXXXXXXXXXX%22%7D%2C%22licenseInfo%22%3A%7B%22name%22%3A%22%E6%8E%88%E6%9D%83%E4%BF%A1%E6%81%AF%22%2C%22url%22%3A%22https%3A%2F%2FXXXXX%2FLICENSE.md%22%7D%2C%22setting%22%3A%7B%22parameters%22%3A%5B%7B%22name%22%3A%22appID%22%2C%22description%22%3A%22%E7%AC%AC%E4%B8%89%E6%96%B9%E7%94%A8%E6%88%B7%E5%94%AF%E4%B8%80%E5%87%AD%E8%AF%81%22%2C%22example%22%3A%22wx3a3c7192476752f8%22%2C%22value%22%3A%22wx3a3c7192476752f8%22%2C%22required%22%3Atrue%2C%22schema%22%3A%7B%22type%22%3A%22STRING%22%7D%2C%22ui%22%3A%7B%22type%22%3A%22text%22%2C%22uiName%22%3A%22%E7%AC%AC%E4%B8%89%E6%96%B9%E7%94%A8%E6%88%B7%E5%94%AF%E4%B8%80%E5%87%AD%E8%AF%81%22%7D%7D%2C%7B%22name%22%3A%22appsecret%22%2C%22description%22%3A%22%E7%AC%AC%E4%B8%89%E6%96%B9%E7%94%A8%E6%88%B7%E5%94%AF%E4%B8%80%E5%87%AD%E8%AF%81%E5%AF%86%E9%92%A5%22%2C%22example%22%3A%2220e73b13b5393bbe7cbd5302f024c0e9%22%2C%22value%22%3A%2220e73b13b5393bbe7cbd5302f024c0e9%22%2C%22required%22%3Atrue%2C%22schema%22%3A%7B%22type%22%3A%22STRING%22%7D%2C%22ui%22%3A%7B%22type%22%3A%22text%22%2C%22uiName%22%3A%22%E7%AC%AC%E4%B8%89%E6%96%B9%E7%94%A8%E6%88%B7%E5%94%AF%E4%B8%80%E5%87%AD%E8%AF%81%E5%AF%86%E9%92%A5%22%7D%7D%5D%7D%2C%22actions%22%3A%5B%7B%22name%22%3A%22TEXT%22%2C%22description%22%3A%22send%20text%20to%20wechat%22%2C%22parameters%22%3A%5B%7B%22name%22%3A%22content%22%2C%22value%22%3A%22%E8%BF%99%E9%87%8C%E6%98%AF%E6%B5%8B%E8%AF%95%E5%86%85%E5%AE%B9%22%2C%22description%22%3A%22%E5%8F%91%E9%80%81%E6%B6%88%E6%81%AF%E7%9A%84%E5%86%85%E5%AE%B9%22%2C%22example%22%3A%22%E5%86%85%E5%AE%B9%22%2C%22required%22%3Atrue%2C%22schema%22%3A%7B%22type%22%3A%22STRING%22%7D%2C%22ui%22%3A%7B%22type%22%3A%22textarea%22%2C%22uiName%22%3A%22%E6%B6%88%E6%81%AF%E5%86%85%E5%AE%B9%22%7D%7D%2C%7B%22name%22%3A%22msgtype%22%2C%22value%22%3A%22text%22%2C%22description%22%3A%22%E6%B6%88%E6%81%AF%E7%B1%BB%E5%9E%8B%2C%E6%AD%A4%E6%97%B6%E5%9B%BA%E5%AE%9Atext%22%2C%22example%22%3A%22text%22%2C%22required%22%3Atrue%2C%22schema%22%3A%7B%22type%22%3A%22STRING%22%7D%2C%22ui%22%3A%7B%22type%22%3A%22text%22%2C%22uiName%22%3A%22%E6%B6%88%E6%81%AF%E7%B1%BB%E5%9E%8B%22%7D%7D%5D%2C%22returns%22%3A%7B%22schema%22%3A%7B%22type%22%3A%22STRING%22%7D%2C%22example%22%3A%22%7B%5C%22status%5C%22%3A%20%5C%22Success%5C%22%2C%20%5C%22data%5C%22%3A%20%5C%22send%20success%5C%22%2C%20%5C%22schema%5C%22%3A%20%7B%5C%22type%5C%22%3A%20%5C%22STRING%5C%22%7D%7D%22%2C%22description%22%3A%22dingtail%20send%20result%22%7D%7D%5D%2C%22image%22%3A%7B%22smallIcon%22%3Anull%2C%22largeImage%22%3A%22data%3Aimage%2Fjpg%3Bbase64%2C%2F9j%2F4AAQSkZJRgABAQEAkACQAAD%2F4QBORXhpZgAATU0AKgAAAAgAAgESAAMAAAABAAEAAIdpAAQAAAABAAAAJgAAAAAAAqACAAQAAAABAAACTqADAAQAAAABAAACTgAAAAAAAP%2FtACxQaG90b3Nob3AgMy4wADhCSU0EJQAAAAAAENQdjNmPALIE6YAJmOz4Qn7%2F2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz%2F2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz%2FwAARCABQAFADASIAAhEBAxEB%2F8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL%2F8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4%2BTl5ufo6erx8vP09fb3%2BPn6%2F8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL%2F8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3%2BPn6%2F9oADAMBAAIRAxEAPwD9D%2F8AgpP%2FAMFJ9W%2BGniu7%2BHnw8vI7PVLNQus6yiiSS0dgD9ngyCocKRvfBKltq4dSV%2FPjxN4u1jxrqb3utatqms3khy9xfXclzKx92ckn86PF3ia68a%2BLtW1q%2BZpLzWL2a%2FuHPVpJZGkY%2FizGs%2BvhcVi515uUnp0XY%2Fzd4444zDiPMKmJxNR%2Byu%2BSF3yxjfTTa9t3u35WSKKKK5T4kKKKKACiiigDQ8NeLtY8Famt7ourapo15GcrcWF3JbSqfZkII%2FOv0H%2F4Jsf8FJ9W%2BJfiyz%2BHnxDu47zVLxSujayyiN7t1BP2efAClyoOx%2BCxXa2XYFvzorQ8I%2BJrrwV4u0nWrJjHeaPew39u46rJFIsin8GUV1YXFzoTUovTqu59twPxxmHDmY08Thqj9ldc8LvllG%2Bum17bPdPyunn0UUVynxIjNtFer%2FCP9hz4sfHHSotQ8PeC9Sk0yYBo728eOxt5UPIeNpmTzFPrGGFfT3%2FBJ39hbR%2FG2hL8UvGNhDqkDTvF4fsLhQ9vmNij3cidHYSKyIrcKUZsElGX6i1b9vLwjov7XUHwdmsta%2FtyYpEb4RIbSOeS3FwkZ%2BbfzGy%2FMFIDMAeNzL7GFy2DhGriJcqk7Jd77fefv3Bfg%2FgsRl9DNuJsS6FPESjGlGNlKTn8F5NNLmtdKz93VtH53eI%2F%2BCV%2Fxw8O2RuF8J2%2BpKoLMtlqls8igf7LOpb6KCfavCPE3hfVPBOvXGl61puoaPqdqQJrS9t3t54sjI3I4BGRyOORX7UftYftT6H%2ByJ8MofE2uWepahDeX8em21vZKpklmdJJBksQFUJE5JJ7AYJNcx8V%2Fgn4F%2F4KM%2Fs56TqkltJaPrFgt%2FoeqyW6rf6S7rkKwB%2BZd3EkW4o%2BMg5COOitlFJtwoy95K9mfU8R%2BA%2BTznUwXD%2BLl9bpxU3SqNO8XotVGPLd7N3V7Xsnc%2FHCitTxx4M1H4b%2BNNW8PaxCtvqmh3ktjdIDuUSRsVbae6kjIPcEHvWXXz7utGfy5WpTpTdKorSi2mnumtGn6BRRRQZhQ3IoooA%2FaL%2Fgn9qdjqv7F%2Fw5k04xtAmjRQPs6edGWjm%2FHzVkz75r0Sb4W%2BGbnx7D4qk8P6LJ4mt4jBFqzWUZvY4yCpUTY3gYLDGejEdCa%2FNL%2FgmF%2B3dL8BvEUHgDxBDdX3hjxFqCLYyQgyS6XdzMsfC9WidipKryrZYAlmz%2BpdfaZfiIVqMbbxtfya%2FrQ%2F0O8M%2BJsv4gyDDyppOdGMIzi18M4pJNX6O14tdNN0zyn9qrxpolp4f0zwreeEbH4ga74snaPSPDl3HG8N00QDPPM0issUMIKs0hBILKFBZgKzvDP7NPibW9Gs18YfEDWrdbeJI49E8HEeH9H09AqqIYmiH2plTGAzTAEdEToJvhZpn9u%2Ftf%2FFLWr5UkvNFs9K0HTSyjdBZtAbuTaeuJJ5ju9fs6f3ai8Y%2Fsif8ACW%2FtheHPix%2FwlmrWv%2FCP2DWX9jomYZsiQcPu%2BVD5mWTadxUHIq3GUnz2vra17aJ2bffvb7tbt%2BhWoVcbN472PtU6nsuRSUEqcJuEpzf%2FAC8s1KSg7q1lFKXM3xHxe%2F4JO%2FDH4s3d1qD3Xi7T9cuvmk1E61NfzTOFCqZTdGUuAAoxkHAwCK%2FPr9r%2FAPYn8Vfsd%2BJbeLVXj1bw%2FqbMunazbxlIp2XkxyISTFLt%2BbYSQRkqzbW2%2Fp5%2B1H%2ByL%2Fw0r408A6x%2FwlmseHP%2BEH1I3%2Fk2S5%2B15aNuG3Dy5B5eFkw2A7Dac03%2FAIKF%2BBNP8e%2FsbePodQjj%2FwCJbpUuq20jAbop7YechU9iSuzjqrsOhNcWMy%2BnOM5Rjytaprrpd3X9dz884%2B8LMtzPCY3EUMHHD1aK5qdSLVqvu80lKC0jreN3rf3k7XT%2FABjooByKK%2BVP4kCiiigDU8DeMr74deNtI8QaZ5H9paHeRX1oZohIiSxsHRip4OGAP1ArY1z49%2BOfEnj6bxVeeMPEjeI5sg6jFqEkE8ak52I0ZXy0BPCJhR2Ark6KpTklZM7KOYYqlS9jSqSjG%2FNZNpc2ylZdUtnuj6a%2FYZ%2F4KC6t8Dvjlcah481rXvEWgeJLaGw1K8vLmW%2BurERM7QTKXLOyRmWUMinO2VmAZlCt%2Bq3g7xppHxC8N2usaHqVjrGl3q74LqzmWaGUdDhlJHB4I6gjB5r8D62fBPxH8R%2FDO7luPDfiHXPDs0%2BPNk0y%2FltGlx%2FeMbDd%2BNepgc2nQXJNcy%2FE%2FZvDvxtxvD9B4DH03Xo3bT5rTi3q9XdSTd3Z2abbv0P3rr4J%2FwCCtn7b1lBoWpfCDw600upXDxf8JFd7WSO0iG2VbZDxud%2F3bOwyoQ7fmZmCfEusftKfEjxDdWs998QPG11NZSCW3eTW7km3cdHT5%2Flb3HNZfxQ%2BKOufGbxrceIvEl4uoa1eRwxXN15KRNceVGsSMwUAFtiKCcc4rbGZx7Wk4U1a%2FwCXU%2Bi448e1m%2BT1cuyylKjKo1Ft2d6bT50rP3W3ZbSvFy1Tsc%2FRRRXhn81mh4u8M3Xgrxfq2i3qmO80e9msLhT1WSKRo2H4MprPr9F%2F%2BCk%2F%2FBNjVviX4svPiH8PLOO81S8UNrOjKwje7dQB9ogyQpcqBvTgsV3Ll2Ib8%2BPEvhHWPBWptZa1pOqaNeRnDW9%2FaSW0qn3VwCPyrqxWFnQm4yWnR9z7bjjgfMOHMwqYbE037K75J2fLKN9Ndr23W6flZvPooorlPiQooooAKKKKACtDwj4aufG3i%2FSdFslMl7rF7DYW6Dq8ksixqPxZhR4a8I6x421NbHRdJ1TWL2Q4S3sLSS5lY%2ByoCT%2BVfoP%2FAME2P%2BCbGrfDTxXZ%2FEP4iWkdnqlmpbRtGdhI9o7Aj7RPglQ4UnYmSVLbjh1AXqwmFnXmoxWnV9j7bgfgfMeI8xp4bDU37K6552fLGN9ddr22W7fldr%2F%2F2Q%3D%3D%22%7D%7D'
    # action = "TEXT"

    app = WeChatApp(APP_NAME, ACTION_LIST, input_data, action)
    app.do_action()
