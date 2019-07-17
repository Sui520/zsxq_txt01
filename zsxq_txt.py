import requests
from urllib import parse
import json
from PyPDF2 import  PdfFileWriter, PdfFileReader
from pdfkit import pdfkit
import os


class zsxq_work(object):

    def __init__(self):
        self.zsxq_group_id = []
        self.zsxq_group_name = []
        self.end_time = 0 # 翻页的时间戳
        self.position = 0
        # 登陆一次更新一次cookie
        self.my_cookie = '_uab_collina=156318392161342136317032; upload_channel=qiniu; ws_address=wss%3A//ws.zsxq.com/ws%3Fversion%3Dv1.10%26access_token%3D02E872BE-8FAC-4B92-DC3E-2C6CF88B94FA; user_id=15488518558112; name=%u7A57%uD83D%uDC44; avatar_url=https%3A//images.zsxq.com/FkOzB4usE_reu_52chWzbsvflZaZ%3Fe%3D1906272000%26token%3DkIxbL07-8jAj8w1n4s9zv64FuZZNEATmlU_Vm6zD%3ATfB2jf-n7Y3VK6wydY_deCSTftI%3D; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216bf530766d354-0b3f7ac28636e8-e343166-1327104-16bf530766e39b%22%2C%22%24device_id%22%3A%2216bf530766d354-0b3f7ac28636e8-e343166-1327104-16bf530766e39b%22%2C%22props%22%3A%7B%7D%7D; UM_distinctid=16bf54cd5e21ac-0f04b4d5fb1969-e343166-144000-16bf54cd5e444; zsxq_access_token=02E872BE-8FAC-4B92-DC3E-2C6CF88B94FA'
        self.headers_group = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Cookie': self.my_cookie,
                'Host': 'api.zsxq.com',
                'Origin': 'https://wx.zsxq.com',
                'Referer': 'https://wx.zsxq.com/dweb/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        }

    def get_zsxq_group(self):
        """
        获取知识星球的星球id与名称
        """
        try:
            url_groups = 'https://api.zsxq.com/v1.10/groups'
            response = requests.get(url=url_groups, headers=self.headers_group)
            if response.status_code == 200:
                # 把unicode 编码改成中文
                datas = json.loads(response.text, encoding="utf-8").get('resp_data').get('groups')
                for data in datas:
                    self.zsxq_group_id.append(data.get('group_id'))
                    self.zsxq_group_name.append(data.get('name'))
        except Exception as e:
            print(e.args)

    def get_zsxq_essence_content(self, group_id, group_name):
        """
        只看精华帖
        :param group_id:
        :param group_name:
        :return:
        """
        while True:
            url_content = 'https://api.zsxq.com/v1.10/groups/{}/topics?scope=digests&count=20&end_time={}'.format(
                group_id, self.end_time)
            print(url_content)
            response = requests.get(url=url_content, headers=self.headers_group)
            if response.status_code == 200:  # 注意：这里一定要做200判断，
                topics = json.loads(response.text, encoding="utf-8").get("resp_data").get(
                    "topics")  # 把unicode 编码成 utf-8
                print(topics)
                if not topics:  # 如果没有主题就退出
                    print('空的')
                    if len(self.zsxq_group_name) > self.position:
                        self.position += 1
                        self.end_time = 0
                        self.get_zsxq_essence_content(xq.zsxq_group_id[xq.position],
                                                      xq.zsxq_group_name[xq.position])
                    break

                end_time = topics[-1].get('create_time')
                self.get_end_time(end_time)

                for topic in topics:
                    try:
                        if topic.get('type') == 'talk' and topic.get('talk'):  # 会话模式的
                            text = topic.get('talk').get('text').replace('\n', '')  # 获取正文内容
                            title = text[0:10] if len(text) > 10 else text
                            author = topic.get('talk').get('owner').get('name')  # 获取作者名称
                            create_time = topic.get('create_time')[:10]  # 获取最后更新时间
                            # images = topic.get('talk').get('images')  # 获取图片列表
                            self.save_zsxq_txt(group_name, title, author.strip(), create_time, text)
                            # if images is not None:
                            #     for image in images:
                            #         imgUrl = image.get('large').get('url')
                            #         print(imgUrl)
                            # else:
                            #     print('没有图片')
                            # print(author, text, modify_time)
                        elif topic.get('type') == 'q&a' and topic.get('question'):
                            author_question = topic.get('question').get('owner').get('name')  # 获取提问者的名称
                            author_answer = topic.get('answer').get('owner').get('name')  # 获取回答者的名称
                            text_question = topic.get('question').get('text').replace('\n', '')  # 获取提问正文
                            text_answer = topic.get('answer').get('text').replace('\n', '')  # 获取回答正文内容
                            title = text_question[0:10] if len(text_question) > 10 else text_question  # 标题
                            text = '{}的提问:{}\n\n{}的回答:{}'.format(author_question, text_question, author_answer,
                                                                 text_answer)  # 获取正文内容
                            author = author_question + '&' + author_answer
                            create_time = topic.get('create_time')[:10]  # 获取最后更新时间
                            # images = topic.get('question').get('images')  # 获取图片列表
                            self.save_zsxq_txt(group_name, title, author.strip(), create_time, text)
                            # if images is not None:
                            #     for image in images:
                            #         imgUrl = image.get('large').get('url')
                            #         print(imgUrl)
                            # else:
                            #     print('没有图片')
                            # print(author, text, modify_time)
                    except Exception as e:
                        print(e.args)

    def get_end_time(self, create_time):
        """
        获取翻页的时间戳
        :param create_time:
        :return:
        """
        first_time = create_time[:10]  # 前一部分时间
        middle_time = create_time[10:-4]  # 中间一部分时间
        last_time = create_time[-4:]  # 最后一部分时间
        # 1. 网页列表的时间戳，发现规律，时间戳倒数第5位会比前面最后一页的时间戳少1 2. zfill方法可以在左边补0 凑成3位
        change_middle_time = middle_time.replace(middle_time[-4:-1], str(int(middle_time[-4:-1]) - 1).zfill(3))
        self.end_time = first_time + parse.quote(change_middle_time) + last_time
        print(self.end_time)

    def save_zsxq_txt(self, group_name, title, author, create_time, content):
        try:
            txt_path = u'H:/pycharmPro/zsxq/zsxq/txt'
            txt_name = u'{}.txt'.format(group_name)
            # 写入txt文本
            with open(txt_path + '/' + txt_name, 'a', encoding='utf-8') as f:
                msg = '标题：{}\n作者：{}\n创建时间:{}\n\n{}\n\n\n\n\n'.format(title, author, create_time, content)
                f.write(msg)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    xq = zsxq_work()
    xq.get_zsxq_group()
    print(xq.zsxq_group_name)
    xq.get_zsxq_essence_content(xq.zsxq_group_id[xq.position], xq.zsxq_group_name[xq.position])


