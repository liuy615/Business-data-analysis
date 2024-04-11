# -*- coding: utf-8 -*
# @Time    : 2024/4/9 10:53
# @Author  : liuy
# @File    : user_prifile.py
from pyecharts.charts import Line, Bar, Page, Funnel, Pie
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from tools import *
import pandas as pd
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot as driver


class UserProfile:
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.vip_data_path = "data/vip_user_data.csv"
        self.month_vip_path = f"data/{self.month}月数据/{self.month}月vip用户数据.csv"

    def read_vip_data(self):
        sql_vip_user_data = f'select user_id, age, sex, user_reg_tm, user_lv_cd, city_level from jdata_user'
        get_one_query(sql_vip_user_data, self.vip_data_path)

    def save_month_view_user(self):
        month_active_data = pd.read_csv(f"data/{self.month}月数据/{self.month}月flow原始数据.csv", encoding='gbk', chunksize=3000000)
        flow_data = pd.DataFrame()
        for chunk in month_active_data:
            chunk["user_id"] = chunk["user_id"].astype(np.int32)
            chunk[["hour", "week", "day", "type"]] = chunk[["hour", "week", "day", "type"]].astype(np.int8)
            chunks = chunk.loc[:, ["user_id"]]
            flow_data = flow_data.append(chunks)
        flow_data = flow_data.drop_duplicates(subset="user_id", keep="first")
        # 会员数据
        vip_user_data = pd.read_csv(self.vip_data_path)
        vip_user_data = vip_user_data.dropna(how="any")
        vip_user_data["user_id"] = vip_user_data["user_id"].astype(np.int32)
        vip_user_data["user_reg_tm"] = pd.to_datetime(vip_user_data["user_reg_tm"])
        vip_user_data[["age", "sex", "user_lv_cd", "city_level"]] = vip_user_data[["age", "sex", "user_lv_cd", "city_level"]].astype(np.int8)
        month_user_data = pd.merge(flow_data, vip_user_data, on="user_id", how="left")
        month_user_data.to_csv(self.vip_data_path)

    def month_view_profile(self):
        month_user_data = pd.read_csv(self.vip_data_path)
        regular_users = month_user_data["age"].isnull().sum()
        vip_users = month_user_data["age"].notnull().sum()
        print("本月浏览普通用户：{}，会员用户：{}".format(regular_users, vip_users))

    def draw_age_pie(self):
        month_user_data = pd.read_csv(self.vip_data_path, index_col=0)
        regular_users = month_user_data["age"].isnull().sum()  # 非会员人数
        vip_users = month_user_data["age"].notnull().sum()  # 会员人数

        # 对会员性别进行分组
        vip_user_data = month_user_data.dropna()
        vip_user_sex = vip_user_data.value_counts("sex").sort_index()
        list1 = [int(regular_users), int(vip_users)]
        attr1 = ["非会员", "会员"]
        list2 = vip_user_sex.values.tolist()
        attr2 = ["未知", "女", "男"]

        inner_data_pair = [list(z) for z in zip(attr1, list1)]
        outer_data_pair = [list(z) for z in zip(attr2, list2)]
        age_pie = (
            Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="800px", height="600px"))
            .add(
                series_name="会员占比",
                data_pair=inner_data_pair,
                radius=[0, "30%"],
                label_opts=opts.LabelOpts(
                    position="inside",
                    formatter="{b}: {d}%",
                ),
            )
            .add(
                series_name="会员性别分布",
                radius=["40%", "55%"],
                data_pair=outer_data_pair,
                label_opts=opts.LabelOpts(
                    position="outside",
                    formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
                    background_color="#eee",
                    border_color="#aaa",
                    border_width=1,
                    border_radius=4,
                    rich={
                        "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                        "abg": {
                            "backgroundColor": "#e3e3e3",
                            "width": "100%",
                            "align": "right",
                            "height": 22,
                            "borderRadius": [4, 4, 0, 0],
                        },
                        "hr": {
                            "borderColor": "#aaa",
                            "width": "100%",
                            "borderWidth": 0.5,
                            "height": 0,
                        },
                        "b": {"fontSize": 16, "lineHeight": 33},
                        "per": {
                            "color": "#eee",
                            "backgroundColor": "#334455",
                            "padding": [2, 4],
                            "borderRadius": 2,
                        },
                    },
                ),
            )
            .set_global_opts(
                legend_opts=opts.LegendOpts(pos_left="left", pos_bottom="center", orient="vertical"),
                title_opts=opts.TitleOpts(title="本月访问用户会员占比及会员性别分布", pos_top="top", pos_left="center")
            )
        )
        return age_pie





"""
1. 平台全体用户画像
2. 本月浏览用户画像
3. 本月购买用户画像
"""





def main():
    print("这是程序的入口")
    # 接下来是用户画像数据
    user_profile = UserProfile(2018, 3)
    # user_profile.read_vip_data()
    # user_profile.save_month_view_user()
    # user_profile.month_view_profile()
    # user_profile.draw_age_pie()
    make_snapshot(driver, user_profile.draw_age_pie().render(), "data/email_file/img_file/user_sex_pie_chart.png")


if __name__ == '__main__':
    main()
    print("程序结束！")
