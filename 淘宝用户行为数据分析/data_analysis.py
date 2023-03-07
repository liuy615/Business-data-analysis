# -*- coding: utf-8 -*
# @Time    : 2023/3/1 11:13
# @Author  : liuy
# @File    : data_analysis.py
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pyecharts.charts import Bar, Line, Scatter, Grid, Pie
from  pyecharts import options as opts
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.width', 100)
# 设置绘图风格
plt.style.use("seaborn")
# 设置中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
# 坐标轴负号的处理
plt.rcParams['axes.unicode_minus'] = False


def main():
    print("这是程序的入口")
# 4. 数据清洗
#  4.1 数据读取
data_analysis = pd.read_csv("data/taobao_user_behavior_cut.csv", index_col=0)
#  4.2 缺失值处理
# print(data_analysis.info())
# print(data_analysis.head())
#  4.3 重复值处理
# print(sum(data_analysis.duplicated()))
# print(sum(data_analysis[data_analysis["behavior_type"] == 1].duplicated()))
# print(sum(data_analysis[data_analysis["behavior_type"] == 2].duplicated()))
# print(sum(data_analysis[data_analysis["behavior_type"] == 3].duplicated()))
# print(sum(data_analysis[data_analysis["behavior_type"] == 4].duplicated()))
#  4.4 异常值处理
# print(data_analysis.describe())
#  4.5 文本类数值的处理
behavior_type = ["click", "collect", "cart", "buy"]
data_analysis["behavior_type"] = data_analysis["behavior_type"].map(lambda x: behavior_type[x-1])
#  4.6 时间序列处理
data_analysis["time"] = pd.to_datetime(data_analysis["time"])
data_analysis["date"] = pd.to_datetime(data_analysis["time"].dt.date)
data_analysis["day"] = data_analysis["time"].dt.day
data_analysis["hour"] = data_analysis["time"].dt.hour
#  4.7 确定各类数据类型
data_analysis.drop(["time", "user_geohash"], axis=1, inplace=True)
print(data_analysis.info())

# 5. 数据分析
#  5.1 流量维度
#     5.1.1 总体流量分析 PV/UV


def overall_flow_analysis():
    """
    PV:访问次数
    UV:独立访问人数
    人均访问次数：PV/UV
    日均访问次数：PV/时间段
    用户行为数据PV：点击、收藏、加购、购买的次数
    用户行为数据UV：点击、收藏、加购、购买的人数
    购买用户数量: 购买过商品的用户去重之后的数量
    人均购买次数: 购买商品行为数量/UV
    购买用户人均购买次数: 购买商品行为数量/购买用户次数
    购买率: 购买用户人数/总用户人数
    复购率: 购买两次及两次以上的用户人数/购买用户人数
    :return:
    """
    # PV: 访问次数
    PV = data_analysis["user_id"].count()
    # UV: 独立访问人数
    UV = data_analysis["user_id"].nunique()
    # 人均访问次数：PV\UV
    per_capita_visits = round(PV/UV)
    # 日均访问次数：PV/时间段
    average_daily_visits = round(PV/(data_analysis["day"].nunique()+1))
    # 用户行为数据PV：点击、收藏、加购、购买的次数
    PV_action = data_analysis["behavior_type"].value_counts().sort_values(ascending=False)
    # 用户行为数据UV：点击、收藏、加购、购买的人数
    UV_action = data_analysis.groupby("behavior_type")["user_id"].nunique().sort_values(ascending=False)
    # 购买用户数量: 购买过商品的用户去重之后的数量
    num_buy = UV_action["buy"]
    # 人均购买次数: 购买商品行为数量/UV
    per_num_buy = round(PV_action["buy"]/UV, 2)
    # 购买用户人均购买次数: 购买商品行为数量/购买用户次数
    per_num_buy_num_buy = round(PV_action["buy"]/num_buy, 2)
    # 购买率: 购买用户人数/总用户人数
    purchase_rate = round(num_buy/UV, 4)*100
    # 复购率: 购买两次及两次以上的用户人数/购买用户人数
    repurchase_num = data_analysis[data_analysis["behavior_type"] == "buy"].groupby("user_id")["behavior_type"].count()
    repurchase_rate = round(repurchase_num[repurchase_num.values >= 2].count()/num_buy, 4)*100
    print(f"总访问量PV:{PV} \n"
          f"总访问量UV:{UV}\n"
          f"人均访问次数：{per_capita_visits}\n"
          f"日均访问次数：{average_daily_visits} \n"
          f"购买用户数量：{num_buy}\n"
          f"人均购买次数：{per_num_buy}\n"
          f"购买用户人均购买次数：{per_num_buy_num_buy}\n"
          f"购买率：{purchase_rate}"+"% \n"
          f"复购率：{repurchase_rate}"+"%\n"
          f"用户行为数据PV：\n {PV_action}\n"
          f"用户行为数据UV：\n {UV_action}")
#     5.1.2 日均流量分析 PV/UV


def daily_average_flow_analysis():
    daily_flow_pv = data_analysis["day"].value_counts().sort_index()
    daily_flow_pv_click = data_analysis[data_analysis["behavior_type"] == "click"].groupby("day")["user_id"].count()
    daily_flow_pv_collect = data_analysis[data_analysis["behavior_type"] == "collect"].groupby("day")["user_id"].count()
    daily_flow_pv_cart = data_analysis[data_analysis["behavior_type"] == "cart"].groupby("day")["user_id"].count()
    daily_flow_pv_buy = data_analysis[data_analysis["behavior_type"] == "buy"].groupby("day")["user_id"].count()
    daily_flow_uv = data_analysis.groupby("day")["user_id"].nunique()
    daily_flow_uv_click = data_analysis[data_analysis["behavior_type"] == "click"].groupby("day")["user_id"].nunique()
    daily_flow_uv_collect = data_analysis[data_analysis["behavior_type"] == "collect"].groupby("day")["user_id"].nunique()
    daily_flow_uv_cart = data_analysis[data_analysis["behavior_type"] == "cart"].groupby("day")["user_id"].nunique()
    daily_flow_uv_buy = data_analysis[data_analysis["behavior_type"] == "buy"].groupby("day")["user_id"].nunique()
    # 画图
    plt.figure(figsize=(12, 8))
    grid = plt.GridSpec(3, 2, wspace=0.1, hspace=0.4)
    plt.subplot(grid[0, 0:2])
    plt.plot(daily_flow_pv.index, daily_flow_pv.values, label="PV")
    plt.plot(daily_flow_uv.index, daily_flow_uv.values, label="UV")
    plt.legend()
    plt.title("12月PV/UV关系图")
    plt.xticks(daily_flow_pv.index)

    plt.subplot(grid[1, 0])
    plt.plot(daily_flow_pv.index, daily_flow_pv.values, label="PV")
    plt.plot(daily_flow_pv.index, daily_flow_pv_click.values,  label="click")
    plt.legend()
    plt.title("12月访问量和点击量折线图")

    plt.subplot(grid[2, 0])
    plt.plot(daily_flow_pv.index, daily_flow_pv_collect.values, label="collect")
    plt.plot(daily_flow_pv.index, daily_flow_pv_cart.values, label="cart")
    plt.plot(daily_flow_pv.index, daily_flow_pv_buy.values, label="buy")
    plt.legend()
    plt.title("12月收藏/加购/支付次数折线图")
    plt.xticks(daily_flow_pv.index)

    plt.subplot(grid[1, 1])
    plt.plot(daily_flow_pv.index, daily_flow_uv.values, label="UV")
    plt.plot(daily_flow_pv.index, daily_flow_uv_click.values, label="click")
    plt.legend()
    plt.title("12月访问人数和点击人数折线图")

    plt.subplot(grid[2, 1])
    plt.plot(daily_flow_pv.index, daily_flow_uv_collect.values, label="collect")
    plt.plot(daily_flow_pv.index, daily_flow_uv_cart.values, label="cart")
    plt.plot(daily_flow_pv.index, daily_flow_uv_buy.values, label="buy")
    plt.legend()
    plt.title("12月收藏/加购/支付人数折线图")
    plt.xticks(daily_flow_pv.index)
    plt.show()
#     5.1.3 时均流量分析 PV/UV


def time_average_flow_analysis():
    plt.figure(figsize=(12, 8))
    time_average_flow_pv = data_analysis.groupby("hour")["user_id"].count()
    time_average_flow_uv = data_analysis.groupby("hour")["user_id"].nunique()
    plt.plot(time_average_flow_pv.index, time_average_flow_pv.values, label="pv")
    plt.plot(time_average_flow_uv.index, time_average_flow_uv.values, label="uv")
    plt.legend()
    plt.title("时均流量pv/uv的变化情况")
    plt.xticks(time_average_flow_uv.index)
    plt.yticks(np.linspace(0, 100000, 51)[::2])
    plt.xlabel("小时")
    plt.ylabel("流量")
    plt.show()

    plt.figure(figsize=(12, 8))
    time_average_flow_uv_click = data_analysis[data_analysis["behavior_type"] == "click"].groupby("hour")["user_id"].nunique()
    time_average_flow_uv_collect = data_analysis[data_analysis["behavior_type"] == "collect"].groupby("hour")["user_id"].nunique()
    time_average_flow_uv_cart = data_analysis[data_analysis["behavior_type"] == "cart"].groupby("hour")["user_id"].nunique()
    time_average_flow_uv_buy = data_analysis[data_analysis["behavior_type"] == "buy"].groupby("hour")["user_id"].nunique()
    plt.plot(time_average_flow_uv_click.index, time_average_flow_uv_click.values, label="click")
    plt.plot(time_average_flow_uv_collect.index, time_average_flow_uv_collect, label="collect")
    plt.plot(time_average_flow_uv_cart.index, time_average_flow_uv_cart, label="cart")
    plt.plot(time_average_flow_uv_buy.index, time_average_flow_uv_buy.values, label="buy")
    plt.legend()
    plt.title("时均流量的变化情况")
    plt.xticks(time_average_flow_uv.index)
    plt.xlabel("小时")
    plt.ylabel("用户数")
    plt.show()
    time_average_flow_uv_buy_w = data_analysis[(data_analysis["hour"] == 4) & (data_analysis["behavior_type"] == "buy")]
    print(time_average_flow_uv_buy_w)
#     5.1.4 用户流量漏斗分析


def user_flow_funnel_analysis():
    user_flow = data_analysis["behavior_type"].value_counts()
    user_flow["pv"] = data_analysis["user_id"].count()
    user_flow = pd.DataFrame(user_flow)
    change_rate = {"点击转化率": round(user_flow.loc["click"]/user_flow.loc["pv"], 4),
                   "点击/收藏转化率": round(user_flow.loc["collect"]/user_flow.loc["click"], 4),
                   "点击/加购转化率": round(user_flow.loc["cart"]/user_flow.loc["click"], 4),
                   "点击/购买转化率": round(user_flow.loc["buy"]/user_flow.loc["click"], 4),
                   "加购/购买转化率": round(user_flow.loc["buy"]/user_flow.loc["cart"], 4),
                   "收藏/购买转化率": round(user_flow.loc["buy"]/user_flow.loc["collect"], 4),
                   }
    change_rate = pd.DataFrame(change_rate,).T
    change_rate["转化率"] = change_rate["behavior_type"].apply(lambda x: format(x, '.2%'))
    change_rate = change_rate.drop(columns="behavior_type")
    print(change_rate)

#     5.1.5 跳出率


def jump_rate():
    user_bouncenum=data_analysis.groupby("user_id").filter(
        lambda x: x["behavior_type"].count() == 1 and (x["behavior_type"] == "click").all())["user_id"].count()
    user_num = data_analysis["user_id"].nunique()
    user_bouncerate = user_bouncenum/user_num
    print("总用户数：" + str(user_num))
    print("跳出用户数：" + str(user_bouncenum))
    print("跳出率：%.2f%%" % (round(user_bouncerate, 4)*100))
#  5.2 用户维度
#     5.2.1 用户购买量


def user_purchases():
    # 购买次数前十客户
    user_purchases = data_analysis[data_analysis["behavior_type"] == "buy"]["user_id"].value_counts().sort_values(ascending=False)
    print(user_purchases[0:10])
    # 购买频次直方图
    plt.figure(figsize=(12, 8))
    sns.displot(user_purchases.values, bins=70, kde=True, label='人数')
    plt.title("购买次数直方图")
    plt.xlabel('次数')
    plt.ylabel('人数')
    plt.legend()
    plt.show()
#     5.2.2 用户留存率分析


def retention(user_new, date_frame, cloumn, date, n):
    """
    计算n日留存率
    :param user_new: 新增用户的用户id集
    :param date_frame:数据集
    :param cloumn:数据集中日期列的列名
    :param date: 循环变量，日期
    :param n: 计算n日留存
    :return:返回一个Series类型的数据，数据为第n日的留存率
    """
    date_max = pd.Series(date_frame[cloumn].unique()).max()  # 计算出日期最大的日期
    retention_action_user = date_frame[date_frame[cloumn] == date+pd.to_timedelta(n, unit='D')]["user_id"].unique()  # 次日登录的用户id
    retention_action_user_num = set()  # 次日登录的用户并且在当日登陆过的用户id
    for x in retention_action_user:
        if x in user_new:
            retention_action_user_num.add(x)
    retention_rate = len(retention_action_user_num)/len(user_new) if date+pd.to_timedelta(n, unit='D') <= date_max else 0
    return retention_rate


def user_preserve():
    """
    计算用户留存率的矩阵
    :return:
    """
    # 由于只有这一个月的用户数据，并不能判断用户是否是新增用户，所以我们将这个月第一次登录的用户看作新增用户
    # 新增用户数 = 这个月第一次登录的用户
    data_retain = pd.DataFrame(columns=["日期", "新增用户数", "次日留存率", "3日留存率", "7日留存率", "14日留存率", "30日留存率"])
    data_retain_base = set()  # 总用户id集合
    for date in data_analysis["date"].unique():
        data_retain_new = data_analysis[data_analysis["date"] == date]["user_id"].unique()
        user_new = set()  # 新增用户的用户id集
        for x in data_retain_new:
            if x not in data_retain_base:
                user_new.add(x)
        data_retain_base.update(user_new)
        user_new_num = len(user_new)  # 新增用户数
        # 次日留存 = 次日还活跃的用户/当日新增用户数
        next_day_rate = retention(user_new, data_analysis, "date", date, 1)
        three_day_rate = retention(user_new, data_analysis, "date", date, 2)
        seven_day_rate = retention(user_new, data_analysis, "date", date, 6)
        two_week_day_rate = retention(user_new, data_analysis, "date", date, 13)
        thriy_day_rate = retention(user_new, data_analysis, "date", date, 29)
        data_retain_item = {"日期": [date], "新增用户数": [user_new_num], "次日留存率": [round(next_day_rate, 4)], "3日留存率": [round(three_day_rate, 4)],
                            "7日留存率": [round(seven_day_rate, 4)], "14日留存率": [round(two_week_day_rate, 4)], "30日留存率": [round(thriy_day_rate, 4)]}
        data_retain_item = pd.DataFrame(data_retain_item)
        data_retain = pd.concat([data_retain, data_retain_item], axis=0, join="inner")
        data_retain.index = range(0, data_retain.shape[0])
    # 留存率折线图
    line_retain = Line()
    line_retain.add_xaxis(data_retain["日期"].dt.date.tolist())
    line_retain.add_yaxis("次日留存率", data_retain["次日留存率"].tolist())
    line_retain.add_yaxis("3日留存率", data_retain["3日留存率"].tolist())
    line_retain.add_yaxis("7日留存率", data_retain["7日留存率"].tolist())
    line_retain.add_yaxis("14日留存率", data_retain["14日留存率"].tolist())
    line_retain.add_yaxis("30日留存率", data_retain["30日留存率"].tolist())
    line_retain.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line_retain.set_global_opts(title_opts=opts.TitleOpts(title="留存率随日期变动"),
                                xaxis_opts=opts.AxisOpts(name='日期'),
                                yaxis_opts=opts.AxisOpts(name='留存率'))
    line_retain.render("data/template/retention_line.html")
    print(data_retain)
    print("平均次日留存率: "+str(round(data_retain[data_retain["次日留存率"] != 0]["次日留存率"].mean(), 4)))
    print("平均3日留存率: "+str(round(data_retain[data_retain["3日留存率"] != 0]["3日留存率"].mean(), 4)))
    print("平均7日留存率: "+str(round(data_retain[data_retain["7日留存率"] != 0]["7日留存率"].mean(), 4)))
    print("平均14日留存率: "+str(round(data_retain[data_retain["14日留存率"] != 0]["14日留存率"].mean(), 4)))
    print("平均30日留存率: "+str(round(data_retain[data_retain["30日留存率"] != 0]["30日留存率"].mean(), 4)))
#     5.2.3 用户购买路径偏好分析


def user_path():
    """
    电商平台用户的路径主要有，直接购买，点击-购买，点击-加购-购买，点击-收藏-购买，点击-收藏&加购-购买
    :return:
    """
    # 如何判断用户直接购买
    # 拿到所有支付过的用户的id，然后判断这个id是否有click行为
    user_click_num = data_analysis[data_analysis["behavior_type"] == "click"]["user_id"].unique()
    user_collect_num = data_analysis[data_analysis["behavior_type"] == "collect"]["user_id"].unique()
    user_cart_num = data_analysis[data_analysis["behavior_type"] == "cart"]["user_id"].unique()
    user_buy_num = data_analysis[data_analysis["behavior_type"] == "buy"]["user_id"].unique()


#     5.2.4 用户价值RFM模型分析
#  5.3 商品维度
#     5.3.1 商品数量与商品类别
#     5.3.2 top10商品分析
#            5.3.2.1 点击量top10商品
#            5.3.2.2 购买量top10商品
#     5.3.3 top10商品类别分析
#     5.3.4 帕累托分析


if __name__ == '__main__':
    # overall_flow_analysis()
    # daily_average_flow_analysis()
    # time_average_flow_analysis()
    # user_flow_funnel_analysis()
    # jump_rate()
    # user_purchases()
    # user_preserve()
    user_path()
    print("程序结束！")