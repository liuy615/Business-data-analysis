# -*- coding: utf-8 -*
# @Time    : 2023/2/23 16:48
# @Author  : liuy
# @File    : 商城超市销售数据分析.py
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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


"""
1. 明确目的
2. 数据提取
3. 数据清洗
4. 建立指标体系
5. 多维度分析
6. 撰写报告
"""
# 2. 数据提取
#   2.1 数据读取
# analysis_date1 = pd.read_excel("data/商城详细销售数据.xls", sheet_name='订单')
# analysis_date2 = pd.read_excel("data/商城详细销售数据.xls", sheet_name='退货')
# analysis_date3 = pd.read_excel("data/商城详细销售数据.xls", sheet_name='销售人员')
#   2.2 合并数据
# analysis_date = pd.merge(analysis_date1, analysis_date2, how='left', left_on='订单 ID', right_on='订单 ID')
# analysis_date = pd.merge(analysis_date, analysis_date3, how='left', left_on='地区', right_on='地区')
#   2.3 保存数据为csv
# analysis_date.to_csv('data/商城详细销售数据.csv')

analysis_date = pd.read_csv("data/商城详细销售数据.csv", index_col=0)
# 3. 数据清洗
#   3.1 观察数据
# print(analysis_date.head(5))
# print(analysis_date.info())
# 通过观察，我们发现产品ID列和产品名称列数据比较混乱，需要处理
#   3.2 处理混乱数据
analysis_date["产品 ID"] = analysis_date["产品 ID"].apply(lambda x: re.search(r'\d+', x).group())
analysis_date[["产品名称", "产品介绍"]] = analysis_date["产品名称"].str.split(",", expand=True)
# print(analysis_date.head())
#   3.3 查看是否有缺失值
# print(analysis_date.isnull().any())
#   3.4 查看是否有异常值
# print(analysis_date.describe())
#   3.5 确定每个字段的数据类型
"""
从data.info 中我们可以看到float类型有3列数据，int类型有2列数据，其余都是object数据，
我们想要发货日期和订单日期为date类型的数据，
退回列为int类型数据，把nan值填充为0，其他为1
"""
analysis_date["订单日期"] = pd.to_datetime(analysis_date["订单日期"])
analysis_date["发货日期"] = pd.to_datetime(analysis_date["发货日期"])
analysis_date["退回"] = analysis_date["退回"].str.replace("是", "1", regex=True).fillna(0).astype(int)
# 4. 建立指标体系


# 5. 多维度分析
#   5.1 销售额分析
#       5.1.1 销售额年变化情况
def sales_year_analysis():
    sales_year = pd.DataFrame(round(analysis_date.groupby(by=analysis_date["订单日期"].dt.year)["销售额"].sum(), 2))
    sales_year["年增长额"] = sales_year.diff()
    sales_year["年增长率"] = round(sales_year["销售额"].pct_change(), 4)
    print(sales_year)
    # 画图----年销售额柱状图+年变化率折线图
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.bar(sales_year.index, sales_year["销售额"])
    ax2.plot(sales_year.index, sales_year["年增长率"], "c.-", label="年增长率")
    plt.legend()
    plt.xticks(sales_year.index, labels=['2015年', '2016年', '2017年', '2018年'])
    plt.title("年销售额变化情况")
    plt.show()


#       5.1.2 销售额季度变化情况
def sales_quarter_analysis():
    """
    1. 今年各季度销售额情况
    2。销售额同比、环比变化率
    3. 各季度销售额对比柱状图
    4. 各基地销售额同比增长率折线图
    """
    sales_quarter = pd.DataFrame(round(analysis_date.groupby(by=[analysis_date["订单日期"].dt.year, analysis_date["订单日期"].dt.quarter])["销售额"].sum(), 2))
    sales_quarter["同比增长率"] = round(sales_quarter["销售额"].pct_change(periods=4), 4)
    sales_quarter["环比增长率"] = round(sales_quarter["销售额"].pct_change(periods=1), 4)
    print(sales_quarter)
    # 画图，各年季度销售额柱状图
    fig, ax1 = plt.subplots(figsize=(12, 8))
    ax2 = ax1.twinx()
    index_quarter = [str(i[0]) + "年Q" + str(i[1]) for i in sales_quarter.index]
    ax1.bar(index_quarter, sales_quarter["销售额"])
    ax2.plot(index_quarter, sales_quarter["同比增长率"], 'b.:', label='同比增长率')
    ax2.plot(index_quarter, sales_quarter["环比增长率"], 'r.:', label='环比增长率')
    plt.gcf().autofmt_xdate()
    plt.title("2015-2018年各季度同比环比增长率变化情况")
    ax1.set_xlabel("季度")
    ax1.set_ylabel("销售额")
    ax2.set_ylabel("变化率")
    plt.show()
    # 各年各季度销售额对比柱状图
    index_2 = [1, 2, 3, 4]
    index_1 = [i-0.2 for i in index_2]
    index_3 = [i+0.2 for i in index_2]
    index_4 = [i+0.2 for i in index_3]
    plt.bar(index_1, sales_quarter.loc[2015, "销售额"], width=0.2, label="2015")
    plt.bar(index_2, sales_quarter.loc[2016, "销售额"], width=0.2, label="2016")
    plt.bar(index_3, sales_quarter.loc[2017, "销售额"], width=0.2, label="2017")
    plt.bar(index_4, sales_quarter.loc[2018, "销售额"], width=0.2, label="2018")
    plt.legend()
    plt.xticks(index_2)
    plt.title("2015-2018年各季度销量情况")
    plt.xlabel("季度")
    plt.ylabel("销售额")
    plt.show()


#       5.1.3 销售额月变化情况
def sales_month_analysis():
    sales_month = pd.DataFrame(round(analysis_date.groupby(by=[analysis_date["订单日期"].dt.year, analysis_date["订单日期"].dt.month])["销售额"].sum(), 2))
    sales_month["同比增长额"] = round(sales_month["销售额"].diff(periods=12), 4)
    sales_month["同比增长率"] = round(sales_month["销售额"].pct_change(periods=12), 4)
    sales_month["环比增长额"] = round(sales_month["销售额"].diff(periods=1), 4)
    sales_month["环比增长率"] = round(sales_month["销售额"].pct_change(periods=1), 4)
    # 画图 2018年各月同比环比销售额增长率
    fig, ax1 = plt.subplots(figsize=(12, 8))
    ax2 = ax1.twinx()
    sales_month_2018 = sales_month.loc[2018]
    ax1.bar(sales_month_2018.index, sales_month_2018["销售额"])
    ax2.plot(sales_month_2018.index, sales_month_2018["同比增长率"], 'b.-', label='同比增长率')
    ax2.plot(sales_month_2018.index, sales_month_2018["环比增长率"], 'r.--', label='环比增长率')
    plt.legend()
    plt.title("2018年各月同比环比销售额增长率")
    ax1.set_xlabel("月份")
    ax1.set_ylabel("销售额")
    ax1.set_xticks(sales_month_2018.index)
    ax2.set_ylabel("变化率")
    plt.show()
    print(sales_month)
    """
    发现问题：
        1. 通过2018年各月销售额统计，我们可以发现4月销售额同比环比都下跌非常严重，
        2. 8月销售额虽然环比有所增加，但是同比却下滑严重。
        3. 从7月份销售额增长率达到高点后，接下来4个月的增长率一直下降，11月增长率甚至为负数。
    提出假设：
        1.对于4月份的销售额下跌，在与今年3月份数据相比的情况下，下跌很大，但是与2月份相比相差不多
        是否是因为3月份做了促销活动，使得销售额大幅度增加？
        2.在与去年4月份相比的情况下，上升趋势放缓，是否是因为去年提升过大，导致总体体量扩大，增长率体现不明显？
        3.从环比和销售额著柱状图的角度看，8-11月的销售额略微下降，但是同比下降严重，导致今年整体下降是因为公司达到瓶颈还是竞争对手掠夺？
    """
    # 看一下去年4月份的销售额以及每年各月份的销售额
    sales_month_2017_index = range(1, 13)
    sales_month_2016_index = [i-0.2 for i in sales_month_2017_index]
    sales_month_2015_index = [i-0.2 for i in sales_month_2016_index]
    sales_month_2018_index = [i+0.2 for i in sales_month_2017_index]
    plt.bar(sales_month_2018_index, sales_month.loc[2018]["销售额"], width=0.2, label="2018")
    plt.bar(sales_month_2017_index, sales_month.loc[2017]["销售额"], width=0.2, label="2017")
    plt.bar(sales_month_2016_index, sales_month.loc[2016]["销售额"], width=0.2, label="2016")
    plt.bar(sales_month_2015_index, sales_month.loc[2015]["销售额"], width=0.2, label="2015")
    plt.legend()
    plt.show()
    """
        1. 通过对各年每月的销售额分析，我们可以得到4月在各年的销售额相比其他月份都相对降低，
        所以我们可以初步判断4月由于产品性质的关系是本公司的销售淡季，由此我们可以看一下我们公司产品的具体销量
        2. 因为去年4月份销售额大幅增加，但是销售额提升163848.74，相比前年销售额183424.58几乎提高一倍，导致体量扩大
        而今年销售额提升140544.69，相比去年销售额下降23304.05，但总量却提升了一倍，所以增长率变缓。
        3.对于8月份的同比增长率下降的原因也是因为2017年增长过多，导致体量增大，所以8月份的增长率趋于正常。
    """

#       5.1.4 不同省销售额贡献情况
def sales_province_analysis():
    """
    1. 总销售贡献度
    2. 销售额top5地区
    """
    print(analysis_date.head())
    sales_province = round(analysis_date.groupby(by=analysis_date["省/自治区"])["销售额"].sum().sort_values(ascending=False), 2)
    plt.legend()
    plt.title("不同品类对销售额贡献度")
    print(sales_province)
    # 画图----销售额条形图和top5销售额饼图
    plt.figure(figsize=(12, 8))
    plt.subplot(211)
    for i in range(len(sales_province)):
        plt.bar(sales_province.index[i], sales_province.values[i])
    plt.xticks(rotation=45)
    plt.title("销量分析")
    plt.xlabel("地区")
    plt.ylabel("销售额")
    # 画饼图，数据简单处理
    plt.subplot(212)
    data_pie = sales_province[0:5]
    data_pie.loc["其他"] = sales_province[5:].sum()
    plt.pie(data_pie.values, labels=data_pie.index, autopct='%1.1f%%', explode=[0.1, 0, 0, 0, 0, 0])
    plt.show()


#       5.1.5 不同品类对销售额的贡献度
def sales_category_analysis():
    sales_category_subcat = analysis_date.groupby(by=[analysis_date["类别"], analysis_date["子类别"]])["销售额"].agg(["sum", "count"])
    sales_category = round(analysis_date.groupby(by=analysis_date["类别"])["销售额"].sum(), 2)
    # 画图--- 不同品类贡献度饼图
    plt.figure(figsize=(12, 8))
    grid = plt.GridSpec(6, 2, wspace=0.5, hspace=0.5)
    plt.subplot(grid[0:3, 0])
    plt.pie(sales_category.values, labels=sales_category.index, autopct='%1.2f%%')
    plt.title("不同品类销售额贡献度")

    plt.subplot(grid[3:6, 0])
    sales_category_top5 = sales_category_subcat.sort_values(by="sum", ascending=False)["sum"][0:5]
    sales_category_top5["其他"] = round(sales_category_subcat.sort_values(by="sum", ascending=False)["sum"][5:].sum(), 2)
    sales_category_top5_index = [str(x[0]) + "/" + str(x[1]) for x in sales_category_top5.index]
    plt.pie(sales_category_top5, labels=sales_category_top5_index, autopct='%1.2f%%')
    plt.title("销售额贡献度top5品类")

    plt.subplot(grid[0:2, 1])
    plt.pie(sales_category_subcat.loc["家具"]["sum"], labels=sales_category_subcat.loc["家具"].index, autopct='%1.2f%%')
    plt.title("家具品类销售额贡献度")

    plt.subplot(grid[2:4, 1])
    sales_category_subcat_ban = sales_category_subcat.loc["办公用品"].sort_values(by="sum", ascending=False)["sum"]
    sales_category_subcat_bangong = sales_category_subcat_ban[0:4]
    sales_category_subcat_bangong.loc["其他"] = round(sales_category_subcat_ban[4:].sum(), 2)
    plt.pie(sales_category_subcat_bangong, labels=sales_category_subcat_bangong.index, autopct='%1.2f%%')
    plt.title("办公用品类销售额贡献度")

    plt.subplot(grid[4:6, 1])
    plt.pie(sales_category_subcat.loc["技术"]["sum"], labels=sales_category_subcat.loc["技术"].index, autopct='%1.2f%%')
    plt.title("技术品类销售额贡献度")
    plt.show()


#       5.1.6 不同地区销售额贡献度
def sales_area_analysis():
    sales_area = round(analysis_date.groupby(by=analysis_date["地区"])["销售额"].sum().sort_values(ascending=False), 2)
    # 画图 ----不同地区销售额贡献度
    plt.figure(figsize=(12, 8))
    grid = plt.GridSpec(1, 3, wspace=0.3, hspace=0.3)
    plt.subplot(grid[0, 0:2])
    for i in range(len(sales_area)):
        plt.bar(sales_area.index[i], sales_area.values[i])
    plt.title("不同地区销售额贡献度")
    plt.xlabel("地区")
    plt.ylabel("销售额")
    for a, b in zip(sales_area.index, sales_area.values):  # 添加数据标签
        plt.text(a, b+0.05, '%.2f' % b, ha='center', va='bottom', fontsize=10)
    plt.subplot(grid[0, 2])
    plt.pie(sales_area.values, labels=sales_area.index, autopct='%1.2f%%')
    plt.title("不同地区销售额贡献度占比")
    plt.show()


#       5.1.7 不同地区经理销售额贡献度
def sales_manager_analysis():
    sales_manager = round(analysis_date.groupby(by=analysis_date["地区经理"])["销售额"].sum().sort_values(ascending=False), 2)
    # 画图 ----不同地区经理销售额贡献度
    plt.figure(figsize=(12, 8))
    grid = plt.GridSpec(3, 3, wspace=0.3, hspace=0.3)
    plt.subplot(grid[0, 0:2])
    for i in range(len(sales_manager)):
        plt.bar(sales_manager.index[i], sales_manager.values[i])
    plt.title("不同地区销售额贡献度")
    plt.xlabel("地区")
    plt.ylabel("销售额")
    for a, b in zip(sales_manager.index, sales_manager.values):  # 添加数据标签
        plt.text(a, b+0.05, '%.2f' % b, ha='center', va='bottom', fontsize=10)
    plt.subplot(grid[0, 2])
    plt.pie(sales_manager.values, labels=sales_manager.index, autopct='%1.2f%%')
    plt.title("不同地区销售额贡献度占比")
    plt.show()


#       5.1.8 不同类型消费者对产品销售额贡献度
def sales_consumer_analysis():
    print(analysis_date.head())
    sales_consumer = round(analysis_date.groupby(by=analysis_date["细分"])["销售额"].sum().sort_values(ascending=False), 2)
    print(sales_consumer)
    sales_consumer_category = round(analysis_date[analysis_date["细分"] == "消费者"].groupby(by=["类别", "子类别"])["销售额"].sum().sort_values(), 2)
    sales_company_category = round(analysis_date[analysis_date["细分"] == "公司"].groupby(by=["类别", "子类别"])["销售额"].sum().sort_values(), 2)
    sales_business_category = round(analysis_date[analysis_date["细分"] == "小型企业"].groupby(by=["类别", "子类别"])["销售额"].sum().sort_values(), 2)
    plt.figure(figsize=(12, 8))
    grid = plt.GridSpec(3, 3, wspace=0.5, hspace=0.5)
    plt.subplot(grid[0:2, 0])
    sales_consumer_category_index = [str(x[0]) + "/" + str(x[1]) for x in sales_consumer_category.index]
    plt.barh(sales_consumer_category_index, sales_consumer_category.values)
    plt.title("消费者兴趣偏好")
    plt.xlabel("销售额")
    plt.ylabel("类别")

    plt.subplot(grid[0:2, 1])
    sales_company_category_index = [str(x[0]) + "/" + str(x[1]) for x in sales_company_category.index]
    plt.barh(sales_company_category_index, sales_company_category.values)
    plt.title("公司兴趣偏好")
    plt.xlabel("销售额")

    plt.subplot(grid[0:2, 2])
    sales_business_category_index = [str(x[0]) + "/" + str(x[1]) for x in sales_business_category.index]
    plt.barh(sales_business_category_index, sales_business_category.values)
    plt.title("小型企业兴趣偏好")
    plt.xlabel("销售额")

    plt.subplot(grid[2, 1])
    plt.pie(sales_consumer.values, labels=sales_consumer.index, autopct="%1.2f%%")
    plt.title("不同类型消费者对产品销售额贡献度")
    plt.show()

# 5.2   利润分析
"""

"""
#       5.2.1 销售额与利润的关系
def profit_sales():
    pass
if __name__ == '__main__':
    # sales_year_analysis()
    # sales_quarter_analysis()
    # sales_month_analysis()
    # sales_province_analysis()
    # sales_category_analysis()
    # sales_area_analysis()
    # sales_manager_analysis()
    # sales_consumer_analysis()
    profit_sales()
    print("程序结束！")
