# -*- coding: utf-8 -*-
# author:Tiper(邱鹏)
# 文件所属项目:QDC SMS SDK
# 文件描述:QuanmSMS SDK (泉鸣开放平台sms接口SDK)，包含执行短信业务所需的方法
# Python版本要求：Python3及以上（可自行修改兼容Python2）
# 官网：dev.quanmwl.com
# 发布日期:2023-3-6【⭐重要更新-新增自动节点功能】

import random
import hashlib
import requests


class SDK:
    def __init__(self):
        # 请开发者修改下列三行配置信息
        self.open_id = '389'   # 开发者ID
        self.api_key = '8e548d54091511eeb5200242ac110004'   # 能力列表的apiKey
        self.def_model_id = 0    # 默认情况下使用的模板ID

        # 因备用通道现仅在特殊情况开放【默认关闭】
        # 故自动节点功能默认关闭，不建议普通用户或在未和平台确认的情况下开启自动节点功能
        self.use_auto_server_node = False  # 【⭐自动节点】是否使用自动节点功能（在主节点不能访问或提供服务时，自动启用备用节点并在主节点恢复后重新回到主节点）
        self.api_http = 'http'  # 【默认，api支持https，如有需要请修改,如开启自动节点，该值将会自动更换为https】
        self.api_host = 'dev.quanmwl.com'  # Api Host【默认,非必要无需修改】
        self.api_gateway = self.api_http + '://' + self.api_host  # 【默认,非必要无需修改】

        self.try_next = 0  # 失败容错及刷间隔【默认，非必要无需修改】
        self.standby_number = 0  # 备用线路计数器

        self.state_code = {
            '200': '短信发送成功',
            '201': '表单信息或接口信息有误',
            '202': '信息重复',
            '203': '服务器异常，请稍后重试',
            '204': '找不到数据',
            '205': '本次请求不安全',
            '206': '接口版本过低',
            '207': '余额不足',
            '208': '验签失败',
            '209': '功能被禁用',
            '210': '账户被禁用',
            '211': '参数过长',
            '212': '权限不足',
            '213': '参数调用状态异常',
            '214': '版本过高',
            '215': '内容受限',
            '216': '内容违规',
            '???': '严重未知错误，请联系服务提供商'
        }
        # 更多状态：https://quanmwl.yuque.com/docs/share/9fbd5429-6575-403d-8a3d-7081b2977eda?#8sz4 《平台状态码处理指引》

        self.auto_server_node()

    def up_api_gateway(self, api_http=None, api_host=None):
        if api_http:
            self.api_http = api_http
        if api_host:
            self.api_host = api_host
        self.api_gateway = self.api_http + '://' + self.api_host

    def auto_server_node(self):
        """
        自动节点机制，允许外部调用，外部调用即刷新
        PS:单个IP每一秒仅能向一个节点请求一次【！】
        :return:
        """
        if self.use_auto_server_node:
            # 更新设定初始值
            self.up_api_gateway('https', 'dev.quanmwl.com')
            # 访问状态检测接口
            tf, _code = self.try_url(self.api_gateway + '/v1/node_status')
            if tf:
                # 访问成功
                print("[AutoServerNode][Info]Main server node ready")
                # 结束
                return
            elif _code == 301:
                # 失败但是301状态码（cors）
                # 尝试http访问
                self.up_api_gateway('http')
                tf, _code = self.try_url(self.api_gateway + '/v1/node_status')
                if tf:
                    print("[AutoServerNode][Warning]Main server node ready,but ssl is not enabled")
                    return
            else:
                # 其他状态码
                # 备用线路检测
                self.up_api_gateway('http', 'testdev.quanmwl.com')
                tf, _code = self.try_url(self.api_gateway + '/v1/node_status')
                if tf:
                    print("[AutoServerNode][Warning]Main serve node down, Standby server node ready,"
                          "but ssl is not enabled")
                    return
            # 如果全部无法访问，则切换回主节点使用http（因为这将是第一时间恢复的节点）
            self.up_api_gateway('http', 'dev.quanmwl.com')
            print("[AutoServerNode][Error]All server node can't link,now set gateway:%s" % self.api_gateway)

    def try_url(self, url):
        """
        检查链接的访问状态
        :param url:
        :return:
        """
        print("[AutoServerNode]try:%s" % url)
        response = requests.get(url)
        # H5标准
        if response is None or '<!DOCTYPE html>' in response.text:
            print("Requests Fail")
            return False, None
        else:
            http_state = response.status_code
            if http_state != 200:
                return False, http_state
            return True, http_state

    def sign(self, _tel, model_id, model_args):
        # type:(str, str, str) -> str
        """
        签名方法
        :param _tel: 接收者手机号
        :param model_id: 短信模板ID
        :param model_args: 短信模板变量参数字典
        :return:
        """
        hl = hashlib.md5()
        server_sign_data = f"{self.open_id}{self.api_key}{_tel}{model_id}{model_args}"
        hl.update(server_sign_data.encode("utf-8"))
        return hl.hexdigest()

    def send(self, tel, model_id, model_args):
        # type:(str, int, dict) -> tuple[bool, str]
        """
        发送短信
        :param tel: 接收者手机号
        :param model_id: 短信模板ID
        :param model_args: 短信模板变量参数字典
        :return:
        """
        headers = {
            'User-Agent': 'QuanmOpenApi_Python_SDK-Sms_0.1.0',  # 非必要，但推荐传入用于兼容性统计
        }

        data = {
            'openID': self.open_id,
            'tel': tel,
            'sign': self.sign(tel, str(model_id), str(model_args).replace(' ', '')),
            'model_id': model_id,
            'model_args': f'{model_args}'
        }
        try:
            response = requests.post(f'{self.api_gateway}/v1/sms', headers=headers, data=data)
            # http_status = response.status_code  几乎可以不依赖http状态码，如有需要请自行修改
        except:
            return False, 'Server Error'
        _mess = 'Not Find'
        if response is None or '<!DOCTYPE html>' in response.text:
            print("Requests Fail")
            # auto server node
            if self.try_next == 0:
                self.try_next = 64
                self.auto_server_node()
                # [重试]
                self.send(tel, model_id, model_args)
            else:
                self.try_next -= 1

            return False, _mess
        else:
            redata = eval(response.text)

            http_state = response.status_code
            if http_state != 200 and 'state' not in redata:
                # auto server node
                if self.try_next == 0:
                    self.try_next = 64
                    self.auto_server_node()
                    # [重试]
                    self.send(tel, model_id, model_args)
                else:
                    self.try_next -= 1

                return False, _mess

            api_state = redata['state']
            if api_state in self.state_code:
                _mess = self.state_code[api_state]

            # auto server node
            """
            这一步用于在使用备用线路时，有规律的去检查主线路状态
            这里按请求次数重试，直到主线路恢复
            """
            if self.api_host != 'dev.quanmwl.com':
                self.standby_number += 1
                if self.standby_number >= 3000:
                    self.standby_number = 0
                if self.standby_number % 9 == 0:
                    self.auto_server_node()
                    # [重试]
                    self.send(tel, model_id, model_args)

            if api_state == '200':
                return True, _mess
            else:
                return True, _mess


if __name__ == '__main__':
    sms = SDK()  # 实例化SDK【提示：该操作仅需进行一次！】
    # 这里演示了一个简单的验证码功能
    check_code = random.randint(100000, 999999)  # 生成验证码
    results, info = sms.send('接受者的手机号', sms.def_model_id, {'code': check_code})  # 发送
    print(info)
