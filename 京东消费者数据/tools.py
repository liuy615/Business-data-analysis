# -*- coding: utf-8 -*
# @Time    : 2024/4/1 17:38
# @Author  : liuy
# @File    : tools.py
import csv
import datetime
from email.mime.image import MIMEImage
import numpy as np
import pymysql
import pandas as pd


# 连接数据库
def get_con():
    """
    获取MySql连接，return：mysql connection
    """
    return pymysql.connect(host="127.0.0.1",
                           user="root",
                           password="513921",
                           database="jd_data",
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)


# 进行数据查询
def get_query(sql):
    """
    根据SQL代码进行查询，并返回结果 paramater SQL
    return str
    """
    conn = get_con()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        return list(cursor.fetchall())
    finally:
        cursor.close()
        conn.close()


def get_one_query(sql, path_file):
    """
    用这个函数主要是因为数据量过大，导致内存溢出，所以我们将得到的数据一条一条读取并一条一条写入csv中。
    用fetchone()函数得到的数据是一个字典类型数据，包括查询的字段名和值。
    并且fetchone()函数是一个生成器，需要循环，每次只读一条数据。
    return str
    """
    conn = get_con()
    try:
        cursor = conn.cursor(cursor=pymysql.cursors.SSDictCursor)
        cursor.execute(sql)
        with open(path_file, "a+", encoding='utf-8', newline='') as file:
            data = cursor.fetchone()
            csv_writer = csv.writer(file)
            csv_writer.writerow(list(data.keys()))
            csv_writer.writerow(list(data.values()))
            i = 1
            while True:
                data = cursor.fetchone()
                if data == None:
                    break
                else:
                    data_values = list(data.values())
                    csv_writer.writerow(data_values)
                    i += 1
    finally:
        cursor.close()
        conn.close()


# 这是一个装饰器，用于计算函数所用的时间
def calculate_time(func):
    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        total_time = end_time - start_time
        print(f"函数 {func.__name__} 执行总共用时：{total_time}")
        return result
    return wrapper


def new_users_vip(flow_data):
    """
    新增用户的计算逻辑
        1. 我们得到的数据是2-1至4-15日用户浏览数据，和jdata_user会员表
        2. 我们将会员表中的用户看作老用户，不在表中的用户看作新用户
        3. 新用户在登录过一次之后，自动成为新增老用户，添加到new_user_data表中，以此类推
    此方法返回意义dataframe，包括每日新增用户和老用户
    """
    sql_vip_user_data = f'select user_id, 1 as vip from jdata_user'
    vip_user_data = pd.DataFrame(get_query(sql_vip_user_data))
    vip_user_data["user_id"] = vip_user_data["user_id"].astype(int)
    vip_user_data["vip"] = vip_user_data["vip"].astype("int8")
    print(f'原始会员人数{vip_user_data.shape[0]}')
    day_users_data = pd.DataFrame()
    for i in range(1, flow_data["day"].max()+1):
        user_data = pd.merge(flow_data[flow_data["day"] == i].drop_duplicates(subset="user_id"), vip_user_data, how="left", on="user_id").fillna(0)
        day_users_data = day_users_data.append(user_data)
        new_users = user_data[user_data["vip"] == 0].loc[:, ["user_id", "vip"]]
        new_users["vip"] = 1
        vip_user_data = vip_user_data.append(new_users)
        print(f'第{i}天,浏览人数{user_data.shape[0]},新增会员人数{user_data[user_data["vip"] == 0].shape[0]},老用户人数{user_data[user_data["vip"] == 1].shape[0]},会员人数{vip_user_data.shape[0]}')
    return day_users_data


def get_vip_user():
    sql_vip_user_data = f'select user_id, 1 as vip from jdata_user'
    vip_user_data = pd.DataFrame(get_query(sql_vip_user_data))
    vip_user_data["user_id"] = vip_user_data["user_id"].astype(int)
    vip_user_data["vip"] = vip_user_data["vip"].astype(np.int8)
    print(f'原始会员人数{vip_user_data.shape[0]}')
    return vip_user_data


def growth_rate(data, last_data):
    data_rate = pd.concat([data, last_data], axis=1, keys=["month", "last_month"])
    data_rate["growth_rate"] = round((data_rate["month"] - data_rate["last_month"])/data_rate["last_month"]*100, 2)
    return data_rate






if __name__ == '__main__':
    print("程序结束！")
