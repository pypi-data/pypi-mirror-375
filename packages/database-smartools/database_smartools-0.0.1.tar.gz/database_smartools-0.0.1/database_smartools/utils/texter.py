# -*- coding: utf-8 -*-
"""
@项目名称 : python-main
@文件名称 : texter.py
@创建人   : zhongbinjie
@创建时间 : 2025/6/7 19:06
@文件说明 : 
@企业名称 : 深圳市赢和信息技术有限公司
@Copyright:2025-2035, 深圳市赢和信息技术有限公司. All rights Reserved.
"""

from datetime import datetime
import re
import uuid

def ljust(text, len):
    return text.ljust(len)

def get_uuid(is_hex):
    # 生成一个随机的 UUID
    unique_id = uuid.uuid4()
    # 使用 hex 属性获取不带 '-' 的 UUID
    if is_hex:
        unique_id = unique_id.hex

    return unique_id

def parse_jdbc_url(jdbc_url):
    # 定义正则表达式匹配不同数据库的JDBC URL
    patterns = {
        "mysql": r"jdbc:mysql://(?:\[([0-9a-fA-F:]+)\]|([^:/]+))(?::(\d+))?/([^?]+)",
        "postgresql": r"jdbc:postgresql://(?:\[([0-9a-fA-F:]+)\]|([^:/]+))(?::(\d+))?/([^?]+)",
        "oracle": r"jdbc:oracle:thin:@(?:\[([0-9a-fA-F:]+)\]|([^:/]+))(?::(\d+))?/(\w+)",
        "sqlserver": r"jdbc:sqlserver://(?:\[([0-9a-fA-F:]+)\]|([^:/;]+))(?::(\d+))?;database[Name=]*([^;]+)",
        "dameng": r"jdbc:dm://(?:\[([0-9a-fA-F:]+)\]|([^:/;]+))(?::(\d+))?/([^?]+)",
        "oceanbase": r"jdbc:oceanbase://(?:\[([0-9a-fA-F:]+)\]|([^:/;]+))(?::(\d+))?/([^?]+)"
    }

    # 尝试匹配不同数据库的URL
    for db_type, pattern in patterns.items():
        match = re.match(pattern, jdbc_url)
        if match:
            # 提取IPv6（带方括号）或IPv4/主机名
            host = match.group(1) or match.group(2)
            port = match.group(3)
            database = match.group(4)
            return {
                "type": db_type,
                "host": host,
                "port": port,
                "database": database
            }

    return None  # 未匹配到已知格式

def text2date(text):
    # 定义常见的日期格式列表
    date_formats = [
        "%Y%m%d", "%Y-%m-%d", "%Y/%m/%d", "%m-%d-%Y", "%m/%d/%Y",
        "%d-%m-%Y", "%d/%m/%Y", "%b %d, %Y",
        "%B %d, %Y", "%b %d %Y", "%B %d %Y", "%Y年%m月%d日"
    ]
    for fmt in date_formats:
        try:
            # 尝试使用当前格式解析日期字符串
            dt = datetime.strptime(text, fmt)
            return dt.date()
        except ValueError:
            continue
    return None  # 所有格式都尝试失败，返回 None

# 添加MB/GB/KB转字节的转换函数
def convert_to_bytes(size_str):
    """将带单位的大小字符串（如"50MB"）转换为字节数

    Args:
        size_str (str): 带单位的大小字符串，支持 B, KB, MB, GB (不区分大小写)

    Returns:
        int: 转换后的字节数

    Raises:
        ValueError: 当输入格式无效或单位不支持时触发
    """
    # 正则表达式匹配数值和单位（支持整数/小数和可选空格）
    match = re.match(r'^(\d+\.?\d*)\s*([A-Za-z]+)$', size_str.strip())
    if not match:
        raise ValueError(f"无效的大小格式: {size_str}，请使用类似'50MB'的格式")

    size = float(match.group(1))
    unit = match.group(2).upper()

    # 定义单位到字节的转换因子（1024进制）
    unit_factors = {
        'B': 1,  # 字节
        'KB': 1024,  # 千字节
        'MB': 1024 ** 2,  # 兆字节
        'GB': 1024 ** 3  # 吉字节
    }

    if unit not in unit_factors:
        supported_units = ', '.join(unit_factors.keys())
        raise ValueError(f"不支持的单位: {unit}，支持的单位有: {supported_units}")

    # 计算并返回字节数（转换为整数）
    return int(size * unit_factors[unit])


def extract_table_names(sql_query):
    """
    从 SQL 查询语句中提取表名和别名。
    返回格式: [{'table': '表名', 'alias': '别名'}, ...]
    """
    if not sql_query: return []
    sql_query = sql_query.replace('\n', ' ')
    # 增强正则表达式以匹配表名和可选别名
    table_pattern = re.compile(
        r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)\s*(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)?\b',
        re.IGNORECASE
    )
    matches = table_pattern.findall(sql_query)
    # 转换为字典列表，处理无别名情况
    result = []
    for table, alias in matches:
        result.append({
            'table': table,
            'alias': alias if alias else None
        })
    return result

def extract_columns(sql_query):
    # 匹配SELECT和FROM之间的内容（忽略大小写，支持多行）
    pattern = r'SELECT\s+(.*?)\s+FROM'
    flags = re.IGNORECASE | re.DOTALL

    # 提取内容
    match = re.search(pattern, sql_query, flags)
    select_content = None
    if match:
        select_content = match.group(1).strip()

    if not select_content:
        return []
    columns = [col.strip() for col in select_content.split(',')]

    # 解析每个列的源字段和别名
    parsed_columns = []
    for col in columns:
        # 支持带AS关键字和不带AS关键字的别名格式
        match = re.match(r'^(.+?)\s+(?:AS\s+)?([^\s]+)$', col, re.IGNORECASE)
        if match:
            source = match.group(1).strip()
            alias = match.group(2).strip()
            parsed_columns.append({"source": source, "alias": alias})
        else:
            parsed_columns.append({"source": col, "alias": None})

    return parsed_columns

def convert_to_oracle_datetime(input_str, type):
    """将'YYYY-MM-DD HH:MM:SS'格式字符串转换为Oracle兼容的'DD-Mon-YYYY HH:MM:SS'格式"""
    try:
        # 解析输入日期时间字符串
        dt = datetime.strptime(input_str, '%Y-%m-%d %H:%M:%S')
        # 格式化为目标格式并将月份缩写转为大写
        if type == 'DATE':
            dt = dt.strftime('%d-%b-%y').upper()
        elif type == 'TIMESTAMP':
            dt = dt.strftime('%d-%b-%y %H:%M:%S').upper()
        return dt
    except ValueError as e:
        raise ValueError(f"日期格式转换失败: {str(e)}")


if __name__ == '__main__':
    # url = "jdbc:oracle:thin:@192.168.74.26:1521/orcl"
    # url2 = "jdbc:mysql://192.168.74.26:3306/db"
    # url3 = "jdbc:dm://192.168.75.23:5236/UTMGR"
    # print(parse_jdbc_url(url3))
    # print(convert_to_kb("50MB"))
    # url3 = "jdbc:oceanbase://192.168.74.33:2883/fdc?autocommit=true"
    # print(parse_jdbc_url(url3))
    # 示例SQL
    # sql = "SELECT * FROM user_tab_columns WHERE table_name = 'T_CHECK_LOG_TEST'"
    # print(extract_columns(sql))
    None
