# -*- coding: utf-8 -*
# @Time    : 2024/4/9 10:53
# @Author  : liuy
# @File    : user_prifile.py
from pyecharts.charts import Line, Bar, Page, Funnel, Pie, Grid
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
        self.view_user_data_path = f'data/{self.month}月数据/{self.month}月view_user_data.csv'
        self.buy_user_data_path = f'data/{self.month}月数据/{self.month}月buy_user_data.csv'

    # 从mysql读取会员用户数据并保存
    def read_vip_data(self):
        sql_vip_user_data = f'select user_id, age, sex, user_reg_tm, user_lv_cd, city_level from jdata_user'
        get_one_query(sql_vip_user_data, self.vip_data_path)
        vip_user_data = pd.read_csv(self.vip_data_path)
        vip_user_data = vip_user_data.dropna(how="any")
        vip_user_data["user_id"] = vip_user_data["user_id"].astype(np.int32)
        vip_user_data["user_reg_tm"] = pd.to_datetime(vip_user_data["user_reg_tm"])
        vip_user_data[["age", "sex", "user_lv_cd", "city_level"]] = vip_user_data[["age", "sex", "user_lv_cd", "city_level"]].astype(np.int8)
        vip_user_data.to_csv(self.vip_data_path, index=False)

    # 数据清洗(本月浏览过的用户)
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
        month_user_data = pd.merge(flow_data, vip_user_data, on="user_id", how="left")
        month_user_data.to_csv(self.view_user_data_path)

    # 数据清洗(本月购买过的用户)
    def save_month_buy_user(self):
        month_active_data = pd.read_csv(f"data/{self.month}月数据/{self.month}月flow原始数据.csv", encoding='gbk', chunksize=3000000)
        flow_data = pd.DataFrame()
        for chunk in month_active_data:
            chunk = chunk[chunk["type"] == 4]
            chunk["user_id"] = chunk["user_id"].astype(np.int32)
            chunk[["hour", "week", "day", "type"]] = chunk[["hour", "week", "day", "type"]].astype(np.int8)
            chunks = chunk.loc[:, ["user_id", "day"]]
            flow_data = flow_data.append(chunks)
        # 会员数据
        vip_user_data = pd.read_csv(self.vip_data_path)
        month_user_data = pd.merge(flow_data, vip_user_data, on="user_id", how="left")
        month_user_data.to_csv(self.buy_user_data_path)

    def month_view_profile(self):
        month_user_data = pd.read_csv(self.view_user_data_path)
        regular_users = month_user_data["age"].isnull().sum()
        vip_users = month_user_data["age"].notnull().sum()
        print("本月浏览普通用户：{}，会员用户：{}".format(regular_users, vip_users))

"""
1. 平台全体用户画像
2. 本月浏览用户画像
3. 本月购买用户画像
"""


# 下面根据vip_user_data数据进行作图
class DrawUserProfile:
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.month_view_user_data = pd.read_csv(f'data/{self.month}月数据/{self.month}月view_user_data.csv', index_col=0)
        self.month_buy_user_data = pd.read_csv(f'data/{self.month}月数据/{self.month}月buy_user_data.csv', index_col=0)

    # 统计每个月浏览网站的人群中会员和非会员人数
    def month_view_vip_user(self):
        regular_users = self.month_view_user_data["age"].isnull().sum()  # 非会员人数
        vip_users = self.month_view_user_data["age"].notnull().sum()  # 会员人数
        return [int(regular_users), int(vip_users)]

    # 统计每个月浏览网站的购买人群中会员和非会员人数
    def month_buy_vip_user(self):
        vip_user_buy_data = self.month_buy_user_data.drop_duplicates("user_id", keep="last")
        regular_users = vip_user_buy_data["age"].isnull().sum()  # 非会员人数
        vip_users = vip_user_buy_data["age"].notnull().sum()  # 会员人数
        return [int(regular_users), int(vip_users)]

    # 定义饼图模型
    @staticmethod
    def draw_nested_pie(inner_data_pair, outer_data_pair, center, title, series_name1, series_name2):
        pos_center = f'{center - 10}%'
        pie_center = f'{center}%'
        pie = (
            Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width="800px", height="600px"))
            .add(
                series_name=series_name1,
                data_pair=inner_data_pair,
                radius=[0, "30%"],
                center=[pie_center, "50%"],
                label_opts=opts.LabelOpts(
                    position="inside",
                    formatter="{b}: {d}%",
                ),
            )
            .add(
                series_name=series_name2,
                radius=["40%", "55%"],
                center=[pie_center, "50%"],
                data_pair=outer_data_pair,
                label_opts=opts.LabelOpts(
                    position="outside",
                    formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}",
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
                legend_opts=opts.LegendOpts(is_show=False),
                title_opts=opts.TitleOpts(title=title, pos_top="top", pos_left=pos_center)
            )
        )
        return pie

    # 本月访问过的会员性别分布饼图
    def draw_user_pie(self):
        # 本月浏览过的会员性别分布饼图
        vip_user_data = self.month_view_user_data.dropna()
        vip_user_sex = vip_user_data.value_counts("sex").sort_index()
        list_inner = self.month_view_vip_user()
        attr_inner = ["非会员", "会员"]
        list_sex = vip_user_sex.values.tolist()
        attr_sex = ["未知", "女", "男"]
        inner_data_pair_sex = [list(z) for z in zip(attr_inner, list_inner)]
        outer_data_pair_sex = [list(z) for z in zip(attr_sex, list_sex)]
        user_sex_pie = self.draw_nested_pie(inner_data_pair_sex, outer_data_pair_sex, 20, "本月访问用户会员占比及会员性别分布", "会员占比", "会员性别占比")

        # 本月浏览过的会员年龄分布饼图
        vip_user_age = vip_user_data.value_counts("age").sort_values(ascending=False)
        list_age = vip_user_age.values.tolist()
        attr_age = [str(int(i)) + "阶" for i in vip_user_age.index]
        inner_data_pair_age = [list(z) for z in zip(attr_inner, list_inner)]
        outer_data_pair_age = [list(z) for z in zip(attr_age, list_age)]
        user_age_pie = self.draw_nested_pie(inner_data_pair_age, outer_data_pair_age, 20, "本月访问用户会员占比及会员年龄分布", "会员占比", "会员年龄占比")

        # 本月浏览过的会员等级分布饼图
        vip_user_lv = vip_user_data.value_counts("user_lv_cd").sort_values(ascending=False)
        list_lv = vip_user_lv.values.tolist()
        attr_lv = [str(int(i)) + "级" for i in vip_user_lv.index]
        inner_data_pair_lv = [list(z) for z in zip(attr_inner, list_inner)]
        outer_data_pair_lv = [list(z) for z in zip(attr_lv, list_lv)]
        user_lv_pie = self.draw_nested_pie(inner_data_pair_lv, outer_data_pair_lv, 20, "本月访问用户会员占比及会员等级分布", "会员占比", "会员等级占比")

        # 本月浏览过的会员城市等级分布饼图
        vip_user_city = vip_user_data.value_counts("city_level").sort_values(ascending=False)
        list_city = vip_user_city.values.tolist()
        attr_city = [str(int(i)) + "线城市" for i in vip_user_city.index]
        inner_data_pair_city = [list(z) for z in zip(attr_inner, list_inner)]
        outer_data_pair_city = [list(z) for z in zip(attr_city, list_city)]
        city_lv_pie = self.draw_nested_pie(inner_data_pair_city, outer_data_pair_city, 20, "本月访问用户会员占比及城市等级分布", "会员占比", "城市等级占比")
        return user_sex_pie, user_age_pie, user_lv_pie, city_lv_pie

    # 本月购买过的会员性别分布饼图
    def draw_user_buy_pie(self):
        # 对会员性别进行分组
        vip_user_buy_data = self.month_buy_user_data.dropna().drop_duplicates("user_id", keep="last")
        list1 = self.month_buy_vip_user()
        attr1 = ["非会员", "会员"]
        vip_user_buy_sex = vip_user_buy_data.value_counts("sex").sort_index()
        list_buy_sex = vip_user_buy_sex.values.tolist()
        attr_buy_sex = ["未知", "女", "男"]
        inner_data_pair_sex = [list(z) for z in zip(attr1, list1)]
        outer_data_pair_sex = [list(z) for z in zip(attr_buy_sex, list_buy_sex)]
        user_buy_sex_pie = self.draw_nested_pie(inner_data_pair_sex, outer_data_pair_sex, 50, "本月购买用户会员占比及会员性别分布", "会员占比", "会员性别占比")

        vip_user_buy_age = vip_user_buy_data.value_counts("age").sort_index()
        list_buy_age = vip_user_buy_age.values.tolist()
        attr_buy_age = [str(int(i)) + "阶" for i in vip_user_buy_age.index]
        inner_data_pair_age = [list(z) for z in zip(attr1, list1)]
        outer_data_pair_age = [list(z) for z in zip(attr_buy_age, list_buy_age)]
        user_buy_age_pie = self.draw_nested_pie(inner_data_pair_age, outer_data_pair_age, 50, "本月购买用户会员占比及会员年龄分布", "会员占比", "会员年龄占比")

        vip_user_buy_lv = vip_user_buy_data.value_counts("user_lv_cd").sort_index()
        list_lv = vip_user_buy_lv.values.tolist()
        attr_lv = [str(int(i)) + "级" for i in vip_user_buy_lv.index]
        inner_data_pair_lv = [list(z) for z in zip(attr1, list1)]
        outer_data_pair_lv = [list(z) for z in zip(attr_lv, list_lv)]
        user_buy_lv_pie = self.draw_nested_pie(inner_data_pair_lv, outer_data_pair_lv, 50, "本月购买用户会员占比及会员等级分布", "会员占比", "会员等级占比")

        vip_user_buy_city = vip_user_buy_data.value_counts("city_level").sort_index()
        list_city = vip_user_buy_city.values.tolist()
        attr_city = [str(int(i)) + "线城市" for i in vip_user_buy_city.index]
        inner_data_pair_city = [list(z) for z in zip(attr1, list1)]
        outer_data_pair_city = [list(z) for z in zip(attr_city, list_city)]
        user_buy_city_pie = self.draw_nested_pie(inner_data_pair_city, outer_data_pair_city, 50, "本月购买用户会员占比及会员城市等级分布", "会员占比", "会员城市等级占比")
        return user_buy_sex_pie, user_buy_age_pie, user_buy_lv_pie, user_buy_city_pie

    # 本月访问和购买过的会员性别分布饼图
    def draw_view_buy_pie(self):
        # 本月浏览用户和购买用户性别分布
        month_view_user = self.month_view_user_data.dropna().drop_duplicates("user_id", keep="last")
        month_buy_user = self.month_buy_user_data.dropna().drop_duplicates("user_id", keep="last")
        month_view_user_sex = month_view_user.value_counts("sex").sort_index()
        list_view_sex = month_view_user_sex.values.tolist()
        month_buy_user_sex = month_buy_user.value_counts("sex").sort_index()
        list_buy_sex = month_buy_user_sex.values.tolist()
        index_sex = ["未知", "女", "男"]
        inner_data_pair_sex = [list(z) for z in zip(index_sex, list_view_sex)]
        outer_data_pair_sex = [list(z) for z in zip(index_sex, list_buy_sex)]
        view_buy_sex_pie = self.draw_nested_pie(inner_data_pair_sex, outer_data_pair_sex, 80, "本月浏览用户和购买用户性别分布", "浏览会员占比", "购买会员占比")

        # 本月浏览用户和购买用户年龄分布
        month_view_user_age = month_view_user.value_counts("age").sort_index()
        list_view_age = month_view_user_age.values.tolist()
        month_buy_user_age = month_buy_user.value_counts("age").sort_index()
        list_buy_age = month_buy_user_age.values.tolist()
        index_age = [str(int(i)) + "阶" for i in month_buy_user_age.index]
        inner_data_pair_age = [list(z) for z in zip(index_age, list_view_age)]
        outer_data_pair_age = [list(z) for z in zip(index_age, list_buy_age)]
        view_buy_age_pie = self.draw_nested_pie(inner_data_pair_age, outer_data_pair_age, 80, "本月浏览用户和购买用户年龄分布", "浏览会员占比", "购买会员占比")

        # 本月浏览用户和购买用户等级分布
        month_view_user_lv = month_view_user.value_counts("user_lv_cd").sort_index()
        list_view_lv = month_view_user_lv.values.tolist()
        month_buy_user_lv = month_buy_user.value_counts("user_lv_cd").sort_index()
        list_buy_lv = month_buy_user_lv.values.tolist()
        index_lv = [str(int(i)) + "级" for i in month_buy_user_lv.index]
        inner_data_pair_lv = [list(z) for z in zip(index_lv, list_view_lv)]
        outer_data_pair_lv = [list(z) for z in zip(index_lv, list_buy_lv)]
        view_buy_lv_pie = self.draw_nested_pie(inner_data_pair_lv, outer_data_pair_lv, 80, "本月浏览用户和购买用户等级分布", "浏览会员占比", "购买会员占比")

        # 本月浏览用户和购买用户城市等级分布
        month_view_user_city = month_view_user.value_counts("user_lv_cd").sort_index()
        list_view_city = month_view_user_city.values.tolist()
        month_buy_user_city = month_buy_user.value_counts("user_lv_cd").sort_index()
        list_buy_city = month_buy_user_city.values.tolist()
        index_city = [str(int(i)) + "级" for i in month_buy_user_city.index]
        inner_data_pair_city = [list(z) for z in zip(index_city, list_view_city)]
        outer_data_pair_city = [list(z) for z in zip(index_city, list_buy_city)]
        view_buy_city_pie = self.draw_nested_pie(inner_data_pair_city, outer_data_pair_city, 80, "本月浏览用户和购买用户城市等级分布", "浏览会员占比", "购买会员占比")
        return view_buy_sex_pie, view_buy_age_pie, view_buy_lv_pie, view_buy_city_pie

    # 本月sex饼图合并
    def draw_user_page(self):
        user_sex_pie, user_age_pie, user_lv_pie, city_lv_pie = self.draw_user_pie()
        user_buy_sex_pie, user_buy_age_pie, user_buy_lv_pie, user_buy_city_pie = self.draw_user_buy_pie()
        view_buy_sex_pie, view_buy_age_pie, view_buy_lv_pie, view_buy_city_pie = self.draw_view_buy_pie()

        # 本月sex饼图合并
        sex_page = (
            Grid(init_opts=opts.InitOpts(theme=ThemeType.ROMA, width='1600px'))
            .add(user_sex_pie, grid_opts=opts.GridOpts(pos_left="55%"))
            .add(user_buy_sex_pie, grid_opts=opts.GridOpts(pos_right="55%"))
            .add(view_buy_sex_pie, grid_opts=opts.GridOpts(pos_right="55%"))
        )

        # 本月age饼图合并
        age_page = (
            Grid(init_opts=opts.InitOpts(theme=ThemeType.ROMA, width='1600px'))
            .add(user_age_pie, grid_opts=opts.GridOpts(pos_left="55%"))
            .add(user_buy_age_pie, grid_opts=opts.GridOpts(pos_right="55%"))
            .add(view_buy_age_pie, grid_opts=opts.GridOpts(pos_right="55%"))
        )

        # 本月user_lv饼图合并
        user_lv_page = (
            Grid(init_opts=opts.InitOpts(theme=ThemeType.ROMA, width='1600px'))
            .add(user_lv_pie, grid_opts=opts.GridOpts(pos_left="55%"))
            .add(user_buy_lv_pie, grid_opts=opts.GridOpts(pos_right="55%"))
            .add(view_buy_lv_pie, grid_opts=opts.GridOpts(pos_right="55%"))
        )

        # 本月city_lv饼图合并
        city_lv_page = (
            Grid(init_opts=opts.InitOpts(theme=ThemeType.ROMA, width='1600px'))
            .add(city_lv_pie, grid_opts=opts.GridOpts(pos_left="55%"))
            .add(user_buy_city_pie, grid_opts=opts.GridOpts(pos_right="55%"))
            .add(view_buy_city_pie, grid_opts=opts.GridOpts(pos_right="55%"))
        )
        return sex_page, age_page, user_lv_page, city_lv_page

    def create_images(self):
        # 生成每个月用户性别图片
        sex_page, age_page, user_lv_page, city_lv_page = self.draw_user_page()
        make_snapshot(driver, sex_page.render(), f"data/email_file/img_file/{self.month}月user_sex_pie_chart.png")
        make_snapshot(driver, age_page.render(), f"data/email_file/img_file/{self.month}月user_age_pie_chart.png")
        make_snapshot(driver, user_lv_page.render(), f"data/email_file/img_file/{self.month}月user_lv_pie_chart.png")
        make_snapshot(driver, city_lv_page.render(), f"data/email_file/img_file/{self.month}月user_city_pie_chart.png")


def main():
    print("这是程序的入口")
    # 接下来是用户画像数据
    # user_profile = UserProfile(2018, 3)
    # user_profile.read_vip_data()
    # user_profile.save_month_view_user()
    # user_profile.save_month_buy_user()

    # 会员用户画像作图
    # draw_user_profile = DrawUserProfile(2018, 3)
    # draw_user_profile.create_images()

    def generate_nested_pie_chart(data, save_path):
        # 构建嵌套饼图
        c = (
            Pie()
            .add("", data, radius=["30%", "75%"])
            .set_global_opts(title_opts=opts.TitleOpts(title="嵌套饼图"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )
        # 保存为 PNG 图片
        c.render(save_path)

    # 示例数据
    data = [
        {"value": 10,
         "name": "类别1",},
        {"value": 20, "name": "类别2"}
    ]

    # 生成嵌套饼图并保存为 PNG 图片
    generate_nested_pie_chart(data, "nested_pie_chart.png")


if __name__ == '__main__':
    main()
    print("程序结束！")
