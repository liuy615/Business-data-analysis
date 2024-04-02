# -*- coding: utf-8 -*
# @Time    : 2023/4/25 17:26
# @Author  : liuy
# @File    : data_analysis.py
import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.set_option('display.width', 1000)
# pd.set_option('display.max_columns', 100)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
plt.rcParams['font.sans-serif'] = ['SimHei']


# 4. 数据清洗
def main():
    print("这是程序的入口")


def run_time(fnc):
    time_start = datetime.datetime.now()
    fnc()
    time_end = datetime.datetime.now()
    print(f"此项目运行的时间为：{time_end - time_start}")


def clean_data_user():
    #    4.1 数据导入
    data_user = pd.read_csv("data/old date/jdata_user.csv")
    # data_shop = pd.read_csv("data/old date/jdata_shop.csv")
    # data_product = pd.read_csv("data/old date/jdata_product.csv")
    # data_comment = pd.read_csv("data/old date/jdata_comment.csv")
    # data_action = pd.read_csv("data/jdata_action.csv")

    #    4.2 缺失值处理及数据类型确定
    #       4.2.1 查看缺失值
    print(data_user.isnull().sum())
    #       4.2.2 填充缺失值，及数据类型确定
    data_user["age"] = data_user["age"].fillna(-1).astype("int64")
    data_user["sex"] = data_user["sex"].fillna(-1).astype("int64")
    data_user["user_reg_tm"] = pd.to_datetime(data_user["user_reg_tm"])
    data_user["city_level"] = data_user["city_level"].fillna(-1).astype("int64")
    data_user["province"] = data_user["province"].fillna(-1).astype("int64")
    data_user["city"] = data_user["city"].fillna(-1).astype("int64")
    data_user["county"] = data_user["county"].fillna(-1).astype("int64")
    print(data_user.info())

    #    4.4 异常值处理
    print(data_user.describe())  # 通过观察，并未发现有异常值的出现

    #    4.5 重复值处理
    print(data_user[data_user.duplicated()])  # 通过观察，并未发现有异常值的出现

    #    4.6 辅助列处理
    #    4.7 保存清洗后的数据
    data_user.to_csv("data/new data/data_user.csv")


def clean_data_shop():
    """
    商家表中只有cate列和注册时间列有空值，
    cate列是商家主营类目，如果有空值，暂时用未知填充, -1代表未知
    注册时间列是商家注册的时间，如果有空值，暂时用未知填充，并将时间列改为datatime类型数据
    :return:
    """
    #    4.1 数据导入
    data_shop = pd.read_csv("data/old date/jdata_shop.csv")

    #    4.2 缺失值处理及数据类型确定
    #           4.2.1 查看缺失值
    print(data_shop.isnull().sum())
    #           4.2.2 填充缺失值，及数据类型确定
    data_shop["cate"] = data_shop["cate"].fillna(-1).astype("int64")
    data_shop["shop_reg_tm"] = pd.to_datetime(data_shop["shop_reg_tm"].fillna(method="bfill"))
    print(data_shop.info())

    #    4.4 异常值处理
    print(data_shop.describe())  # 通过观察，并未发现有异常值的出现

    #    4.5 重复值处理
    print(data_shop[data_shop.duplicated()])  # 通过观察，并未发现有异常值的出现

    #    4.6 辅助列处理
    #    4.7 保存清洗后的数据
    data_shop.to_csv("data/new data/data_shop.csv")


def clean_data_product():
    """
    商品表中没有缺失值
    商品上市时间列改为datatime类型数据
    :return:
    """
    #    4.1 数据导入
    data_product = pd.read_csv("data/old date/jdata_product.csv")

    #    4.2 缺失值处理及数据类型确定
    #           4.2.1 查看缺失值
    print(data_product.isnull().sum())  # 通过观察，并未发现有缺失值的出现
    data_product["market_time"] = pd.to_datetime(data_product["market_time"])
    print(data_product.info())

    #    4.4 异常值处理
    print(data_product.describe())  # 通过观察，并未发现有异常值的出现

    #    4.5 重复值处理
    print(data_product[data_product.duplicated()])  # 通过观察，并未发现有异常值的出现

    #    4.6 辅助列处理
    #    4.7 保存清洗后的数据
    data_product.to_csv("data/new data/data_product.csv")


def clean_data_comment():
    """
    评论表中没有缺失值
    评论时间列改为datatime类型数据
    :return:
    """
    #    4.1 数据导入
    data_comment = pd.read_csv("data/old date/jdata_comment.csv")

    #    4.2 缺失值处理及数据类型确定
    #           4.2.1 查看缺失值
    print(data_comment.isnull().sum())
    #           4.2.2 填充缺失值，及数据类型确定
    data_comment["dt"] = pd.to_datetime(data_comment["dt"])
    print(data_comment.info())

    #    4.4 异常值处理
    print(data_comment.describe())  # 通过观察，并未发现有异常值的出现

    #    4.5 重复值处理
    print(data_comment[data_comment.duplicated()])  # 通过观察，并未发现有异常值的出现

    #    4.6 辅助列处理
    #    4.7 保存清洗后的数据
    data_comment.to_csv("data/new data/data_comment.csv")


def clean_data_action():
    """
    评论表中没有缺失值
    评论时间列改为datatime类型数据
    :return:
    """
    #    4.1 数据导入
    data_action = pd.read_pickle("data/old date/data_action.pkl")

    #    4.2 缺失值处理及数据类型确定
    #           4.2.1 查看缺失值
    print(data_action.isnull().sum())
    #           4.2.2 填充缺失值，及数据类型确定
    data_action["user_id"] = data_action["user_id"].astype("int32")
    data_action["sku_id"] = data_action["sku_id"].astype("int32")
    data_action["action_time"] = pd.to_datetime(data_action["action_time"])
    data_action["module_id"] = data_action["module_id"].astype("int32")
    data_action["type"] = data_action["type"].astype("int8")
    print(data_action.info())

    #    4.4 异常值处理
    print(data_action.describe())  # 通过观察，并未发现有异常值的出现

    #    4.5 重复值处理
    print(data_action[data_action.duplicated()])  # 通过观察，即使精确到秒，也有可能会出现同一个用户出现两次浏览行为，所以不做处理

    #    4.6 辅助列处理
    data_action["date"] = pd.to_datetime(data_action["action_time"].dt.date)
    print(data_action.info())
    #    4.7 保存清洗后的数据
    data_action.to_pickle("data/new data/data_action.pkl")

    # 对消费的数据进行消费金额的随机赋值，以便后续的分析
    data_consumption = data_action[data_action["type"] == 2][["user_id", "sku_id", "action_time", "module_id"]]
    data = pd.DataFrame(data_consumption["sku_id"].drop_duplicates(keep="first"), columns=["sku_id"]).reset_index()
    data["money"] = pd.DataFrame(np.random.randint(10, 3000, size=(len(data), 1)), columns=['money'])
    data_consumption = pd.merge(data_consumption, data, how="inner", on="sku_id").drop("index", axis=1)
    print(data_consumption)
    data_consumption.to_pickle("data/new data/data_consumption.pkl")


# 5. 用户相关数据分析
def analysis_data_user():
    data_consumption = pd.read_pickle("data/new data/data_consumption.pkl")
    data_consumption_group = data_consumption.groupby("user_id")
    #   5.1 用户购买量与消费金额分析
    user_amount = data_consumption_group.agg(购买量=("money", "count"), 消费金额=("money", "sum")).reset_index()
    #       5.1.1 绘制每个用户产品购买量与消费金额散点图
    plt.figure(figsize=(12, 8))
    grid = plt.GridSpec(2, 2, wspace=0.5, hspace=0.5)
    plt.subplot(grid[0:1, 0:2])
    plt.scatter(user_amount["购买量"], user_amount["消费金额"])
    plt.xlabel("用户购买量", fontsize=12)
    plt.ylabel("用户消费总金额", fontsize=12)
    plt.title("用户产品购买量与消费金额散点图", fontsize=12)
    #       5.1.2 绘制用户购买数量分布直方图
    plt.subplot(grid[1:2, 0:1])
    plt.hist(user_amount["购买量"], bins=200)
    plt.xlabel("用户购买量", fontsize=12)
    plt.ylabel("用户数量", fontsize=12)
    plt.title("用户产品购买量分布直方图", fontsize=12)
    #       5.1.3 绘制用户消费金额分布直方图
    plt.subplot(grid[1:2, 1:2])
    plt.hist(user_amount["消费金额"], bins=200)
    plt.xlabel("消费金额", fontsize=12)
    plt.ylabel("用户数量", fontsize=12)
    plt.title("用户产品消费金额分布直方图", fontsize=12)
    print(user_amount.describe())
    #       5.1.4 总结
    """
    经过以上分析，我们可以得到如下结论：
        1. 今年在我们平台上消费过的用户一共有1608707位用户，同比增加xx%，环比增长xx%。
        2. 在所有购买的用户用，平均每位用户购买数量为1.36件，平均每位用户消费金额2019元。相比我们预计目标有很大的提升。
        3. 结合用户购买量与消费金额分布图分析，我们可以看到，大多数（超过90%）用户仅仅购买过1件商品，如何提升复购率将是我们接下来的工作重点。
        4. 有一半用户消费金额不超过1750，75%用户消费金额不超过2586元，从图中可以看出仅仅很小的一部分用户消费金额超过50000元。
    """
    #   5.2 用户累积消费金额占比分析
    user_cumsun = data_consumption_group.agg(消费金额=("money", "sum")).sort_values(by="消费金额", ascending=False).reset_index()
    user_cumsun["消费金额"] = pd.DataFrame(user_cumsun["消费金额"], dtype='int64')
    user_cumsun["累积消费金额"] = user_cumsun["消费金额"].cumsum()
    user_cumsun["累积消费人数"] = user_cumsun["消费金额"].rank(ascending=False).astype("int64")
    user_cumsun["累积消费金额占比"] = user_cumsun["累积消费金额"]/user_cumsun["累积消费金额"].max()*100
    user_cumsun["累积消费人数占比"] = user_cumsun["累积消费人数"]/user_cumsun["累积消费人数"].max()*100
    plt.figure(figsize=(12, 8))
    plt.plot(user_cumsun["累积消费人数占比"], user_cumsun["累积消费金额占比"])
    plt.title("用户累积消费金额折线图")
    plt.xlabel("累积消费人数占比", fontsize=12)
    plt.ylabel("累积消费金额占比", fontsize=12)
    user_cumsun_2_8 = user_cumsun[user_cumsun["累积消费金额占比"] < 80]
    print(f'前{round(user_cumsun_2_8["累积消费人数占比"].max(), 2)}%的用户贡献了80%的销售额，共{user_cumsun_2_8.shape[0]}人')
    #   5.2 总结
    """
        通过对累积消费金额的数据分析，我们得到如下信息
        1. 前52.27%的用户贡献了80%的销售额，共840934人。如果需要，可以输出这些用户的user_id做精细化运营。
        2. 由于销售额数据是根据随机数据生成的，所以事实与二八定律有所差别。
    """
    #   5.3 用户消费时间分析
    #       5.3.1 首购时间折线图
    user_buy_time = data_consumption_group.agg(首购时间=("action_time", "min"), 最后一次购买时间=("action_time", "max")).reset_index()
    user_buy_time["first_day"] = user_buy_time["首购时间"].dt.date
    user_buy_time["last_day"] = user_buy_time["最后一次购买时间"].dt.date
    plt.figure(figsize=(12, 8))
    user_buy_time.value_counts("first_day").plot(kind="line", legend="首购时间")
    user_buy_time.value_counts("last_day").plot(kind="line", legend="最后一次购买时间")
    plt.legend()
    plt.title("首购/最后一次购买时间折线图")
    plt.xlabel("时间", fontsize=12)
    plt.ylabel("人数", fontsize=12)
    #       5.3.2 消费时间偏好图
    data_consumption_time = data_consumption[["user_id", "action_time"]]
    data_consumption_time = data_consumption_time.copy()
    data_consumption_time["date"] = data_consumption_time["action_time"].dt.date
    data_consumption_time["month"] = data_consumption_time["action_time"].dt.month
    data_consumption_time["day"] = data_consumption_time["action_time"].dt.day
    data_consumption_time["week"] = data_consumption_time["action_time"].dt.day_name()
    data_consumption_time["hour"] = data_consumption_time["action_time"].dt.hour
    plt.figure(figsize=(12, 8))
    plt.subplots_adjust(hspace=0.3)
    plt.subplot(2, 2, 1)
    data_consumption_time.groupby("month").agg("count")["user_id"].plot(kind="bar")
    plt.plot(kind="line")
    plt.title("月消费偏好柱状图")
    plt.xlabel("月份", fontsize=12)
    plt.ylabel("人数", fontsize=12)
    plt.subplot(2, 2, 2)
    data_consumption_time.groupby("day").agg("count")["user_id"].plot(kind="line")
    plt.plot(kind="line")
    plt.title("日期消费偏好折线图")
    plt.xlabel("日期", fontsize=12)
    plt.subplot(2, 2, 3)
    data_consumption_time.groupby("week").agg("count")["user_id"].plot(kind="bar")
    plt.plot(kind="line")
    plt.title("星期消费偏好柱状图")
    plt.xlabel("星期", fontsize=12)
    plt.ylabel("人数", fontsize=12)
    plt.xticks(rotation=45)
    plt.subplot(2, 2, 4)
    data_consumption_time.groupby("hour").agg("count")["user_id"].plot(kind="line")
    plt.plot(kind="line")
    plt.title("小时消费偏好折线图")
    plt.xlabel("小时", fontsize=12)
    #       5.3.3 总结
    """
        通过对用户消费时间的数据分析，我们得到如下信息：
        1. 通过对首购/最后一次购买时间分析可得，
        2. 从月消费柱状图来看，用户在3月份购买的人数最多，在4月份大幅度下降，有可能是4月数据不完善
        3. 从日期消费折线图来看，用户在月初的时候购买人数最多，然后逐渐下降，直到月中，然后有所回升
            随后到月末直线下降，用户在月初的时候发工资有更强的购买力，应该在月初的时候做更多的活动吸引用户
        4. 从星期消费偏好图来看，用户没有明显的购买时间偏好。为了避免大多数公司在周末做活动，
            建议我们可以重心放在周内，可以避免很多竞争。
        5. 从小时消费偏好来看，用户在早上10-11点购买意愿最强，在晚上9-10点购买意愿也很强。
    """
    #   5.4 RFM模型
    user_rfm_data = data_consumption_group.agg(R=("action_time", "max"), F=("user_id", "count"), M=("money", "sum"))
    user_rfm_data["R"] = (user_rfm_data["R"].max() - user_rfm_data["R"]).dt.days
    """
    处理rfm模型不能仅仅单纯的用平均值比较大小判断，我这里的处理方式是：
        观察RFM各列的值，再对每列进行分箱，然后取平均值进行判断。
    """
    print(user_rfm_data.describe())
    """
    通过观察RFM模型的数据，我们可以看到，r列的数据分布比较平均，[0-25%]的用户为4，以此类推
    F列数据比较难处理，超过75%的用户仅仅购买一次，所以这里F=1的值为1，F=2的值为2，F=3-10的值为3，F=10-max为4
    M列的值也比较平均，直接采用4分位分箱法就可以
    """
    user_rfm_data["cut_r"] = pd.cut(user_rfm_data["R"], [0, 16, 33, 50, 74], labels=[4, 3, 2, 1], right=False).astype("int8")
    user_rfm_data["cut_f"] = pd.cut(user_rfm_data["F"], [0, 1, 2, 10, 237], labels=[1, 2, 3, 4]).astype("int8")
    user_rfm_data["cut_m"] = pd.cut(user_rfm_data["M"], [0, 881, 1751, 2586, 356569], labels=[1, 2, 3, 4]).astype("int8")
    # 打分并输出结果

    def rfm_score(col):
        level = col.apply(lambda x: "1" if x >= 0 else "0")
        label = level["cut_r"] + level["cut_f"] + level["cut_m"]
        dic = {
            "111": "重要价值客户",
            "011": "重要保持客户",
            "101": "重要发展客户",
            "001": "重要挽留客户",
            "110": "一般价值客户",
            "010": "一般保持客户",
            "100": "一般发展客户",
            "000": "一般挽留客户"

        }
        result = dic[label]
        return result
    user_rfm_data["level"] = user_rfm_data[["cut_r", "cut_f", "cut_m"]].apply(lambda x: x - x.mean()).apply(rfm_score, axis=1)
    print(user_rfm_data.head())


# 6. 流量相关数据分析
def analysis_data_flow():
    data = pd.read_pickle("data/new data/data_consumption.pkl")



if __name__ == '__main__':
    # run_time(clean_data_action)  # 数据清洗，并将清洗好的数据保存
    # run_time(analysis_data_user)
    # run_time(analysis_data_flow)
    print("程序结束！")
