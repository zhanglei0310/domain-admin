# -*- coding: utf-8 -*-
"""
domain_util.py
"""

import re

from typing import NamedTuple

import tldextract
from tldextract.remote import looks_like_ip
from tldextract.tldextract import ExtractResult

from domain_admin.log import logger
from domain_admin.utils import file_util
from domain_admin.utils.cert_util import cert_consts


class ParsedDomain(NamedTuple):
    """
    解析后的domain数据
    """
    domain: str
    root_domain: str
    group_name: str
    port: int
    alias: str


def parse_domain(domain):
    """
    解析域名信息
    :param domain:
    :return:
    """
    # print(domain)

    ret = re.match('((http(s)?:)?//)?(?P<domain>[\\w\\._:-]+)/?.*?', domain)
    if ret:
        # print(ret.groups())
        return ret.groupdict().get("domain")
    else:
        return None


def parse_domain_from_csv_file(filename) -> ParsedDomain:
    """
    读取csv文件 适合完整导入
    :param filename:
    :return:
    """
    with open(filename, 'r') as f:
        # 标题
        first_line = f.readline()
        keys = [filed.strip() for filed in first_line.split(',')]

        # 内容字段
        for line in f.readlines():
            values = [filed.strip() for filed in line.split(',')]
            item = dict(zip(keys, values))

            domain = parse_domain(item.get('域名', ''))
            if ':' in domain:
                domain, port = domain.split(":")

            alias = item.get('备注', '').strip(' -')
            group_name = item.get('分组', '').strip(' -')

            # SSL端口
            port = item.get('端口') or port or cert_consts.SSL_DEFAULT_PORT

            if domain:
                item = ParsedDomain(
                    domain=domain,
                    root_domain=get_root_domain(domain),
                    port=int(port),
                    alias=alias,
                    group_name=group_name
                )

                yield item


def parse_domain_from_txt_file(filename) -> ParsedDomain:
    """
    读取txt文件 适合快速导入
    :param filename:
    :return:
    """
    with open(filename, 'r') as f:
        for line in f.readlines():

            domain = parse_domain(line.strip())

            if ':' in domain:
                domain, port = domain.split(":")
            else:
                # SSL默认端口
                port = cert_consts.SSL_DEFAULT_PORT

            if domain:
                yield ParsedDomain(
                    domain=domain,
                    root_domain=get_root_domain(domain),
                    port=int(port),
                    alias='',
                    group_name=''
                )


def parse_domain_from_file(filename) -> ParsedDomain:
    """
    解析域名文件的工厂方法
    :param filename:
    :return:
    """
    file_type = file_util.get_filename_ext(filename)

    if file_type == 'csv':
        return parse_domain_from_csv_file(filename)
    else:
        return parse_domain_from_txt_file(filename)


def extract_domain(domain: str) -> ExtractResult:
    """
    解析域名
    :param domain:
    :return:
    """
    return tldextract.extract(domain)


def get_root_domain(domain: str) -> str:
    """
    解析出域名和顶级后缀
    :param domain:
    :return:
    """
    extract_result = extract_domain(domain)
    return extract_result.registered_domain
    # return '.'.join([extract_result.domain, extract_result.suffix])


def is_ipv4(ip) -> bool:
    """
    检测一个字符串是否是ipv4地址
    :param ip:
    :return:
    """
    return looks_like_ip(ip)

    # if re.match("(\d+\.){3}\d+", ip):
    #     return True
    # else:
    #     return False


def encode_hostname(hostname: str) -> str:
    """
    编码中文域名，英文域名原样返回
    :param hostname: 中文域名
    :return:
    """
    return hostname.encode('idna').decode('ascii')


def verify_cert_common_name(common_name, domain):
    """
    验证证书
    :param common_name:
    :param domain:
    :return:
    """
    logger.info("%s <=> %s", common_name, domain)

    if '*' in common_name:
        # 通配符 SSL 证书
        common_name_root_domain = get_root_domain(common_name)
        root_domain = get_root_domain(domain)
        return common_name_root_domain == root_domain
    else:
        # 普通证书
        return common_name == domain


if __name__ == '__main__':
    print(get_root_domain("*.juejin.cn"))
