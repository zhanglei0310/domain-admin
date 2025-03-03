# -*- coding: utf-8 -*-
"""
@File    : icp_util.py
@Date    : 2023-06-30
"""

import requests


def get_icp(domain: str):
    """
    查询域名备案信息
    doc: https://api.vvhan.com/beian.html

    其他方式：
        - https://github.com/1in9e/icp-domains
        - https://github.com/wongzeon/ICP-Checker

    :param domain:
    :return:
    """
    url = 'https://api.vvhan.com/api/icp'
    params = {
        'url': domain
    }
    res = requests.get(url, params)
    return res.json()


if __name__ == '__main__':
    print(get_icp('baidu.com'))
