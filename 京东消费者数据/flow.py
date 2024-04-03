# -*- coding: utf-8 -*
# @Time    : 2024/4/1 16:49
# @Author  : liuy
# @File    : flow.py
import pandas as pd
from pyecharts.charts import Line, Bar, Page, Funnel
from pyecharts import options as opts
from bs4 import BeautifulSoup
from tools import *


class MonthFlow:
    def __init__(self, year, month):
        self.month = month
        self.year = year
        self.last_month = self.month - 1
        self.flow_active_data = self.type_conversion(self.month)
        self.last_flow_active_data = pd.read_csv(f"data/{self.month - 1}月数据/{self.month - 1}月flow原始数据.csv", encoding='gbk')

    def read_month_action_data(self):
        query = f'select user_id, type, day(action_time)  day, hour(action_time) hour, weekday(action_time) week from jdata_action where (year(action_time) = {self.year}) and (month(action_time) = {self.month});'
        get_one_query(query, f"data/{self.month}月数据/{self.month}月flow原始数据.csv")

    def type_conversion(self, month):
        """
        将读取的数据进行数据类型精确，并返回dataframe
        """
        month_active_data = pd.read_csv(f"data/{month}月数据/{month}月flow原始数据.csv", encoding='gbk', chunksize=5000000)
        flow_data = pd.DataFrame()
        for chunk in month_active_data:
            chunk["user_id"] = chunk["user_id"].astype(np.int32)
            chunk[["hour", "day", "week", "type"]] = chunk[["hour", "day", "week", "type"]].astype(np.int8)
            flow_data = flow_data.append(chunk)
        return flow_data

    def get_pv_count(self, data):
        # pv计算
        pv_day_flow = data["day"].value_counts().sort_index()   # 获取到pv的日流量分布
        pv_hour_flow = data["hour"].value_counts().sort_index()    # 获取到pv的时流量分布
        pv_week_flow = data.groupby("week").agg(weeks=("user_id", "count")).reset_index()   # 获取到pv的周流量分布
        day_week = data.drop_duplicates(subset="day", keep="first")["week"].value_counts().reset_index()  # 获取这个月有几个星期一
        pv_week_flow = pd.merge(pv_week_flow, day_week, how="inner", left_on="week", right_on="index").set_index("week_x")
        pv_week_flow["week"] = round(pv_week_flow["weeks"]/pv_week_flow["week_y"]).astype(int)
        pv_week_flow = pv_week_flow["week"]

        return pv_day_flow, pv_hour_flow, pv_week_flow

    def get_uv_count(self, data):
        # uv计算：在一个时间周期内，访问页面的人数之和
        uv_day_user = data.groupby("day").agg(day_user=("user_id", "nunique")).reset_index()
        uv_hour_user = data.groupby("hour").agg(hour_user=("user_id", "nunique")).reset_index()
        uv_week_user = data.groupby("week").agg(week_users=("user_id", "nunique")).reset_index()
        day_week = data.drop_duplicates(subset="day", keep="first")["week"].value_counts().reset_index()  # 获取这个月有几个星期一
        uv_week_user = pd.merge(uv_week_user, day_week, how="inner", left_on="week", right_on="index").set_index("week_x")
        uv_week_user["week_user"] = round(uv_week_user["week_users"]/uv_week_user["week_y"]).astype(int)
        uv_day_user = uv_day_user["day_user"]
        uv_hour_user = uv_hour_user["hour_user"]
        uv_week_user = uv_week_user["week_user"]

        return uv_day_user, uv_hour_user, uv_week_user

    def get_flow_count(self):
        active_data = self.flow_active_data
        last_active_data = self.last_flow_active_data
        pv_day_flow, pv_hour_flow, pv_week_flow = self.get_pv_count(active_data)
        last_pv_day_flow, last_pv_hour_flow, last_pv_week_flow = self.get_pv_count(last_active_data)
        pv_day_data = growth_rate(pv_day_flow, last_pv_day_flow)
        pv_hour_data = growth_rate(pv_hour_flow, last_pv_hour_flow)
        pv_week_data = growth_rate(pv_week_flow, last_pv_week_flow)
        uv_day_flow, uv_hour_flow, uv_week_flow = self.get_uv_count(active_data)
        last_uv_day_flow, last_uv_hour_flow, last_uv_week_flow = self.get_uv_count(last_active_data)
        uv_day_data = growth_rate(uv_day_flow, last_uv_day_flow)
        uv_hour_data = growth_rate(uv_hour_flow, last_uv_hour_flow)
        uv_week_data = growth_rate(uv_week_flow, last_uv_week_flow)

        return pv_day_data, pv_hour_data, pv_week_data, uv_day_data, uv_hour_data, uv_week_data

    def save_flow_count(self):
        pv_day_data, pv_hour_data, pv_week_data, uv_day_data, uv_hour_data, uv_week_data = self.get_flow_count()
        with pd.ExcelWriter(f"data/{self.month}月数据/flow_pv_data.xlsx") as writer:
            pv_day_data.to_excel(writer, sheet_name="pv_day_data")
            pv_hour_data.to_excel(writer, sheet_name="pv_hour_data")
            pv_week_data.to_excel(writer, sheet_name="pv_week_data")
            uv_day_data.to_excel(writer, sheet_name="uv_day_data")
            uv_hour_data.to_excel(writer, sheet_name="uv_hour_data")
            uv_week_data.to_excel(writer, sheet_name="uv_week_data")

    # 下面计算下单的用户
    def get_buy_count(self):
        type_buy_data = self.flow_active_data[self.flow_active_data["type"] == 4]
        last_type_buy_data = self.last_flow_active_data[self.last_flow_active_data["type"] == 4]
        pv_buy_day_flow, pv_buy_hour_flow, pv_buy_week_flow = self.get_pv_count(type_buy_data)
        last_buy_pv_day_flow, last_buy_pv_hour_flow, last_buy_pv_week_flow = self.get_pv_count(last_type_buy_data)
        pv_buy_day_data = growth_rate(pv_buy_day_flow, last_buy_pv_day_flow)
        pv_buy_hour_data = growth_rate(pv_buy_hour_flow, last_buy_pv_hour_flow)
        pv_buy_week_data = growth_rate(pv_buy_week_flow, last_buy_pv_week_flow)
        uv_buy_day_flow, uv_buy_hour_flow, uv_buy_week_flow = self.get_uv_count(type_buy_data)
        last_buy_uv_day_flow, last_buy_uv_hour_flow, last_buy_uv_week_flow = self.get_uv_count(last_type_buy_data)
        uv_buy_day_data = growth_rate(uv_buy_day_flow, last_buy_uv_day_flow)
        uv_buy_hour_data = growth_rate(uv_buy_hour_flow, last_buy_uv_hour_flow)
        uv_buy_week_data = growth_rate(uv_buy_week_flow, last_buy_uv_week_flow)

        return pv_buy_day_data, pv_buy_hour_data, pv_buy_week_data, uv_buy_day_data, uv_buy_hour_data, uv_buy_week_data

    def save_buy_count(self):
        pv_buy_day_data, pv_buy_hour_data, pv_buy_week_data, uv_buy_day_data, uv_buy_hour_data, uv_buy_week_data = self.get_buy_count()
        with pd.ExcelWriter(f"data/{self.month}月数据/flow_buy_data.xlsx") as writer:
            pv_buy_day_data.to_excel(writer, sheet_name="pv_buy_day_data")
            pv_buy_hour_data.to_excel(writer, sheet_name="pv_buy_hour_data")
            pv_buy_week_data.to_excel(writer, sheet_name="pv_buy_week_data")
            uv_buy_day_data.to_excel(writer, sheet_name="uv_buy_day_data")
            uv_buy_hour_data.to_excel(writer, sheet_name="uv_buy_hour_data")
            uv_buy_week_data.to_excel(writer, sheet_name="uv_buy_week_data")

        # 下面对流量数据分类统计，计算转化率
    def get_type_count(self):
        active_data = self.flow_active_data
        last_active_data = self.last_flow_active_data
        pv_type_data = active_data["type"].value_counts().sort_index()
        last_pv_type_data = last_active_data["type"].value_counts().sort_index()
        pv_type_count = growth_rate(pv_type_data, last_pv_type_data)
        uv_type_data = active_data.groupby("type").agg(data_type=("user_id", "nunique")).sort_index()
        last_uv_type_data = last_active_data.groupby("type").agg(data_type=("user_id", "nunique")).sort_index()
        uv_type_data = uv_type_data["data_type"]
        last_uv_type_data = last_uv_type_data["data_type"]
        uv_type_count = growth_rate(uv_type_data, last_uv_type_data).reset_index()

        return pv_type_count, uv_type_count

    def save_type_count(self):
        pv_type_count, uv_type_count = self.get_type_count()
        with pd.ExcelWriter(f"data/{self.month}月数据/flow_type_data.xlsx") as writer:
            pv_type_count.to_excel(writer, sheet_name="pv_type_count")
            uv_type_count.to_excel(writer, sheet_name="uv_type_count")


class DramFlow(MonthFlow):
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.flow_view_path = f"data/{self.month}月数据/flow_pv_data.xlsx"
        self.flow_buy_path = f"data/{self.month}月数据/flow_buy_data.xlsx"
        self.flow_type_path = f"data/{self.month}月数据/flow_type_data.xlsx"
        self.save_view_path = f"data/{self.month}月数据/draw_view.html"
        self.save_buy_view_path = f"data/{self.month}月数据/draw_buy_view.html"

    # 绘制本月全体用户的pv数据
    def draw_pv_chart(self):
        """
        此方法用于将月流量pv数据转化为可视化的图形
        """
        # PV日流量折线图
        pv_day_data = pd.read_excel(self.flow_view_path, sheet_name="pv_day_data")  # 获取本月及上月的日pv数据
        pv_day_x = [str(i + 1)+"日" for i in pv_day_data.index]  # 横坐标数据，以这个月的日期为准
        last_pv_day_y = pv_day_data["last_month"].tolist()
        pv_day_y = pv_day_data["month"].tolist()
        pv_day_bar = (
            Bar()
                .add_xaxis(pv_day_x)
                .add_yaxis("上月", last_pv_day_y, label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", pv_day_y, label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("PV日流量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=50,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        pv_day_rate = pv_day_data["growth_rate"].tolist()
        pv_day_line = (
            Line()
                .add_xaxis(pv_day_x)
                .add_yaxis("增长率", pv_day_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        pv_day_bar.overlap(pv_day_line)

        # PV周流量柱状图
        pv_week_data = pd.read_excel(self.flow_view_path, sheet_name="pv_week_data")  # 获取本月及上月的周pv数据
        pv_week_x = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        last_pv_week_y = pv_week_data["last_month"].tolist()
        pv_week_y = pv_week_data["month"].tolist()
        pv_week_bar = (
            Bar()
                .add_xaxis(pv_week_x)
                .add_yaxis("上月", last_pv_week_y, yaxis_index=0, category_gap="50%", label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", pv_week_y, yaxis_index=0, category_gap="50%", label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("PV周流量"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=10,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        pv_week_rate = pv_week_data["growth_rate"].tolist()
        pv_week_line = (
            Line()
                .add_xaxis(pv_week_x)
                .add_yaxis("增长率", pv_week_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        pv_week_bar.overlap(pv_week_line)

        # PV时流量柱状图
        pv_hour_data = pd.read_excel(self.flow_view_path, sheet_name="pv_hour_data")
        pv_hour_x = [str(i)+"时" for i in range(0, 24)]
        last_pv_hour_y = pv_hour_data["last_month"].tolist()
        pv_hour_y = pv_hour_data["month"].tolist()
        pv_hour_bar = (
            Bar()
                .add_xaxis(pv_hour_x)
                .add_yaxis("上月", last_pv_hour_y, category_gap="50%", gap="0%", label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", pv_hour_y, category_gap="50%", gap="0%", label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("PV时流量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=10,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        pv_hour_rate = pv_hour_data["growth_rate"].tolist()
        pv_hour_line = (
            Line()
                .add_xaxis(pv_hour_x)
                .add_yaxis("增长率", pv_hour_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        pv_hour_bar.overlap(pv_hour_line)

        return pv_day_bar, pv_week_bar, pv_hour_bar

    # 绘制本月全体用户的uv数据
    def draw_uv_chart(self):
        """
        此方法用于将月流量uv数据转化为可视化的图形
        """
        # UV日流量折线图
        uv_day_data = pd.read_excel(self.flow_view_path, sheet_name="uv_day_data")  # 获取本月及上月的日pv数据
        uv_day_x = [str(i + 1)+"日" for i in uv_day_data.index]  # 横坐标数据，以这个月的日期为准
        last_uv_day_y = uv_day_data["last_month"].tolist()
        uv_day_y = uv_day_data["month"].tolist()
        uv_day_bar = (
            Bar()
                .add_xaxis(uv_day_x)
                .add_yaxis("上月", last_uv_day_y, label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", uv_day_y, label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("UV日流量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=50,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        uv_day_rate = uv_day_data["growth_rate"].tolist()
        uv_day_line = (
            Line()
                .add_xaxis(uv_day_x)
                .add_yaxis("增长率", uv_day_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        uv_day_bar.overlap(uv_day_line)

        # UV周流量柱状图
        uv_week_data = pd.read_excel(self.flow_view_path, sheet_name="uv_week_data")  # 获取本月及上月的周pv数据
        uv_week_x = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        last_uv_week_y = uv_week_data["last_month"].tolist()
        uv_week_y = uv_week_data["month"].tolist()
        uv_week_bar = (
            Bar()
                .add_xaxis(uv_week_x)
                .add_yaxis("上月", last_uv_week_y, yaxis_index=0, category_gap="50%", label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", uv_week_y, yaxis_index=0, category_gap="50%", label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("UV周流量"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=10,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        uv_week_rate = uv_week_data["growth_rate"].tolist()
        uv_week_line = (
            Line()
                .add_xaxis(uv_week_x)
                .add_yaxis("增长率", uv_week_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        uv_week_bar.overlap(uv_week_line)

        # PV时流量柱状图
        uv_hour_data = pd.read_excel(self.flow_view_path, sheet_name="uv_hour_data")
        uv_hour_x = [str(i)+"时" for i in range(0, 24)]
        last_uv_hour_y = uv_hour_data["last_month"].tolist()
        uv_hour_y = uv_hour_data["month"].tolist()
        uv_hour_bar = (
            Bar()
                .add_xaxis(uv_hour_x)
                .add_yaxis("上月", last_uv_hour_y, category_gap="50%", gap="0%", label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", uv_hour_y, category_gap="50%", gap="0%", label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("UV时流量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=10,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        uv_hour_rate = uv_hour_data["growth_rate"].tolist()
        uv_hour_line = (
            Line()
                .add_xaxis(uv_hour_x)
                .add_yaxis("增长率", uv_hour_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        uv_hour_bar.overlap(uv_hour_line)

        return uv_day_bar, uv_week_bar, uv_hour_bar

    # 人均访问量（全体pv/uv）折线图
    def draw_avg_pv_chart(self):
        """
        1. 获取pv、uv数据
        2. 用这个月的pv除以这个月的uv，得到人均pv
        :return:
        """
        pv_day_data = pd.read_excel(self.flow_view_path, sheet_name="pv_day_data")  # 获取本月及上月的日pv数据
        uv_day_data = pd.read_excel(self.flow_view_path, sheet_name="uv_day_data")  # 获取本月及上月的日uv数据
        x_index = [str(i + 1)+"日" for i in pv_day_data.index]
        y_data_day_1 = [round(i / j, 2) for i, j in zip(pv_day_data["month"], uv_day_data["month"])]
        y_data_day_2 = [round(i / j, 2) for i, j in zip(pv_day_data["last_month"], uv_day_data["last_month"])]
        day_avg_line = (
            Line()
                .add_xaxis(x_index)
                .add_yaxis("本月", y_data_day_1, label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("上月", y_data_day_2, label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("日人均访问量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="占比",
                    type_="value",
                    interval=1,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )

        pv_week_data = pd.read_excel(self.flow_view_path, sheet_name="pv_week_data")  # 获取本月及上月的日pv数据
        uv_week_data = pd.read_excel(self.flow_view_path, sheet_name="uv_week_data")  # 获取本月及上月的日uv数据
        x_index = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        y_data_week_1 = [round(i / j, 2) for i, j in zip(pv_week_data["month"], uv_week_data["month"])]
        y_data_week_2 = [round(i / j, 2) for i, j in zip(pv_week_data["last_month"], uv_week_data["last_month"])]
        week_avg_line = (
            Line()
                .add_xaxis(x_index)
                .add_yaxis("本月", y_data_week_1, label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("上月", y_data_week_2, label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("周人均访问量"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="占比",
                    type_="value",
                    interval=1,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )

        pv_hour_data = pd.read_excel(self.flow_view_path, sheet_name="pv_hour_data")  # 获取本月及上月的日pv数据
        uv_hour_data = pd.read_excel(self.flow_view_path, sheet_name="uv_hour_data")  # 获取本月及上月的日uv数据
        x_index = [str(i)+"时" for i in pv_hour_data.index]
        y_data_hour_1 = [round(i / j, 2) for i, j in zip(pv_hour_data["month"], uv_hour_data["month"])]
        y_data_hour_2 = [round(i / j, 2) for i, j in zip(pv_hour_data["last_month"], uv_hour_data["last_month"])]
        hour_avg_line = (
            Line()
                .add_xaxis(x_index)
                .add_yaxis("本月", y_data_day_1, label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("上月", y_data_day_2, label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("时人均访问量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="占比",
                    type_="value",
                    interval=1,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        return day_avg_line, week_avg_line, hour_avg_line

    # 合并
    def draw_pv_page(self):
        pv_day_bar, pv_week_bar, pv_hour_bar = self.draw_pv_chart()
        uv_day_bar, uv_week_bar, uv_hour_bar = self.draw_uv_chart()
        day_avg_line, week_avg_line, hour_avg_line = self.draw_avg_pv_chart()
        pv_page = (
            Page()
                .add(pv_day_bar)
                .add(uv_day_bar)
                .add(day_avg_line)
                .add(pv_week_bar)
                .add(uv_week_bar)
                .add(week_avg_line)
                .add(pv_hour_bar)
                .add(uv_hour_bar)
                .add(hour_avg_line)
        )
        pv_page.render(self.save_view_path)
        with open(self.save_view_path, "r+", encoding='utf-8') as html:
            html_bf = BeautifulSoup(html, 'lxml')
            divs = html_bf.select('.chart-container')
            divs[0]["style"] = "width:33%;height:33%;position:absolute;top:0;left:1%;"
            divs[1]["style"] = "width:33%;height:33%;position:absolute;top:0%;left:34%;"
            divs[2]["style"] = "width:33%;height:33%;position:absolute;top:0%;left:67%;"
            divs[3]["style"] = "width:33%;height:33%;position:absolute;top:50%;left:1%;"
            divs[4]["style"] = "width:33%;height:33%;position:absolute;top:50%;left:34%;"
            divs[5]["style"] = "width:33%;height:33%;position:absolute;top:50%;left:67%;"
            divs[6]["style"] = "width:33%;height:33%;position:absolute;top:100%;left:1%;"
            divs[7]["style"] = "width:33%;height:33%;position:absolute;top:100%;left:34%;"
            divs[8]["style"] = "width:33%;height:33%;position:absolute;top:100%;left:67%;"
            html_new = str(html_bf)
            html.seek(0, 0)
            html.truncate()
            html.write(html_new)
            html.close()

    # 绘制有购买行为的用户的pv数据
    def draw_buy_pv_chart(self):
        """
        此方法用于将月流量pv数据转化为可视化的图形
        """
        # PV日流量折线图
        pv_buy_day_data = pd.read_excel(self.flow_buy_path, sheet_name="pv_buy_day_data")  # 获取本月及上月的日pv数据
        pv_day_x = [str(i + 1)+"日" for i in pv_buy_day_data.index]  # 横坐标数据，以这个月的日期为准
        last_pv_day_y = pv_buy_day_data["last_month"].tolist()
        pv_day_y = pv_buy_day_data["month"].tolist()
        pv_buy_day_bar = (
            Bar()
                .add_xaxis(pv_day_x)
                .add_yaxis("上月", last_pv_day_y, label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", pv_day_y, label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("购买人群PV日流量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=50,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        pv_day_rate = pv_buy_day_data["growth_rate"].tolist()
        pv_buy_day_line = (
            Line()
                .add_xaxis(pv_day_x)
                .add_yaxis("增长率", pv_day_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        pv_buy_day_bar.overlap(pv_buy_day_line)

        # PV周流量柱状图
        pv_buy_week_data = pd.read_excel(self.flow_buy_path, sheet_name="pv_buy_week_data")  # 获取本月及上月的周pv数据
        pv_week_x = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        last_pv_week_y = pv_buy_week_data["last_month"].tolist()
        pv_week_y = pv_buy_week_data["month"].tolist()
        pv_buy_week_bar = (
            Bar()
                .add_xaxis(pv_week_x)
                .add_yaxis("上月", last_pv_week_y, yaxis_index=0, category_gap="50%", label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", pv_week_y, yaxis_index=0, category_gap="50%", label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("购买人群PV周流量"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=10,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        pv_week_rate = pv_buy_week_data["growth_rate"].tolist()
        pv_buy_week_line = (
            Line()
                .add_xaxis(pv_week_x)
                .add_yaxis("增长率", pv_week_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        pv_buy_week_bar.overlap(pv_buy_week_line)

        # PV时流量柱状图
        pv_buy_hour_data = pd.read_excel(self.flow_buy_path, sheet_name="pv_buy_hour_data")
        pv_hour_x = [str(i)+"时" for i in range(0, 24)]
        last_pv_hour_y = pv_buy_hour_data["last_month"].tolist()
        pv_hour_y = pv_buy_hour_data["month"].tolist()
        pv_buy_hour_bar = (
            Bar()
                .add_xaxis(pv_hour_x)
                .add_yaxis("上月", last_pv_hour_y, category_gap="50%", gap="0%", label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", pv_hour_y, category_gap="50%", gap="0%", label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("购买人群PV时流量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=10,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        pv_hour_rate = pv_buy_hour_data["growth_rate"].tolist()
        pv_buy_hour_line = (
            Line()
                .add_xaxis(pv_hour_x)
                .add_yaxis("增长率", pv_hour_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        pv_buy_hour_bar.overlap(pv_buy_hour_line)

        return pv_buy_day_bar, pv_buy_week_bar, pv_buy_hour_bar

    # 绘制有购买行为的用户的uv数据
    def draw_buy_uv_chart(self):
        """
        此方法用于将月流量uv数据转化为可视化的图形
        """
        # PV日流量折线图
        uv_buy_day_data = pd.read_excel(self.flow_buy_path, sheet_name="uv_buy_day_data")  # 获取本月及上月的日pv数据
        uv_day_x = [str(i + 1)+"日" for i in uv_buy_day_data.index]  # 横坐标数据，以这个月的日期为准
        last_uv_day_y = uv_buy_day_data["last_month"].tolist()
        uv_day_y = uv_buy_day_data["month"].tolist()
        uv_buy_day_bar = (
            Bar()
                .add_xaxis(uv_day_x)
                .add_yaxis("上月", last_uv_day_y, label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", uv_day_y, label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("购买人群UV日流量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=50,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        uv_day_rate = uv_buy_day_data["growth_rate"].tolist()
        uv_buy_day_line = (
            Line()
                .add_xaxis(uv_day_x)
                .add_yaxis("增长率", uv_day_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        uv_buy_day_bar.overlap(uv_buy_day_line)

        # PV周流量柱状图
        uv_buy_week_data = pd.read_excel(self.flow_buy_path, sheet_name="uv_buy_week_data")  # 获取本月及上月的周pv数据
        uv_week_x = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        last_uv_week_y = uv_buy_week_data["last_month"].tolist()
        uv_week_y = uv_buy_week_data["month"].tolist()
        uv_buy_week_bar = (
            Bar()
                .add_xaxis(uv_week_x)
                .add_yaxis("上月", last_uv_week_y, yaxis_index=0, category_gap="50%", label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", uv_week_y, yaxis_index=0, category_gap="50%", label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("购买人群UV周流量"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=10,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        uv_week_rate = uv_buy_week_data["growth_rate"].tolist()
        uv_buy_week_line = (
            Line()
                .add_xaxis(uv_week_x)
                .add_yaxis("增长率", uv_week_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        uv_buy_week_bar.overlap(uv_buy_week_line)

        # PV时流量柱状图
        uv_buy_hour_data = pd.read_excel(self.flow_buy_path, sheet_name="uv_buy_hour_data")
        uv_hour_x = [str(i)+"时" for i in range(0, 24)]
        last_uv_hour_y = uv_buy_hour_data["last_month"].tolist()
        uv_hour_y = uv_buy_hour_data["month"].tolist()
        uv_buy_hour_bar = (
            Bar()
                .add_xaxis(uv_hour_x)
                .add_yaxis("上月", last_uv_hour_y, category_gap="50%", gap="0%", label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("本月", uv_hour_y, category_gap="50%", gap="0%", label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("购买人群UV时流量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            )
                .extend_axis(   # 第二坐标轴
                yaxis=opts.AxisOpts(
                    name="增长率",
                    type_="value",
                    interval=10,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        uv_hour_rate = uv_buy_hour_data["growth_rate"].tolist()
        uv_buy_hour_line = (
            Line()
                .add_xaxis(uv_hour_x)
                .add_yaxis("增长率", uv_hour_rate, yaxis_index=1, label_opts=opts.LabelOpts(is_show=False))
        )
        uv_buy_hour_bar.overlap(uv_buy_hour_line)

        return uv_buy_day_bar, uv_buy_week_bar, uv_buy_hour_bar

    # 绘制购买人群的人均访问量（全体pv/uv）折线图
    def draw_avg_buy_chart(self):
        """
        1. 获取pv、uv数据
        2. 用这个月的pv除以这个月的uv，得到人均pv
        :return:
        """
        pv_day_data = pd.read_excel(self.flow_buy_path, sheet_name="pv_buy_day_data")  # 获取本月及上月的日pv数据
        uv_day_data = pd.read_excel(self.flow_buy_path, sheet_name="uv_buy_day_data")  # 获取本月及上月的日uv数据
        x_index = [str(i + 1)+"日" for i in pv_day_data.index]
        y_data_day_1 = [round(i / j, 2) for i, j in zip(pv_day_data["month"], uv_day_data["month"])]
        y_data_day_2 = [round(i / j, 2) for i, j in zip(pv_day_data["last_month"], uv_day_data["last_month"])]
        day_avg_line = (
            Line()
                .add_xaxis(x_index)
                .add_yaxis("本月", y_data_day_1, label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("上月", y_data_day_2, label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("日人均访问量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="占比",
                    type_="value",
                    interval=1,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )

        pv_week_data = pd.read_excel(self.flow_buy_path, sheet_name="pv_buy_week_data")  # 获取本月及上月的日pv数据
        uv_week_data = pd.read_excel(self.flow_buy_path, sheet_name="uv_buy_week_data")  # 获取本月及上月的日uv数据
        x_index = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        y_data_week_1 = [round(i / j, 2) for i, j in zip(pv_week_data["month"], uv_week_data["month"])]
        y_data_week_2 = [round(i / j, 2) for i, j in zip(pv_week_data["last_month"], uv_week_data["last_month"])]
        week_avg_line = (
            Line()
                .add_xaxis(x_index)
                .add_yaxis("本月", y_data_week_1, label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("上月", y_data_week_2, label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("周人均访问量"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="占比",
                    type_="value",
                    interval=1,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )

        pv_hour_data = pd.read_excel(self.flow_buy_path, sheet_name="pv_buy_hour_data")  # 获取本月及上月的日pv数据
        uv_hour_data = pd.read_excel(self.flow_buy_path, sheet_name="uv_buy_hour_data")  # 获取本月及上月的日uv数据
        x_index = [str(i)+"时" for i in pv_hour_data.index]
        y_data_hour_1 = [round(i / j, 2) for i, j in zip(pv_hour_data["month"], uv_hour_data["month"])]
        y_data_hour_2 = [round(i / j, 2) for i, j in zip(pv_hour_data["last_month"], uv_hour_data["last_month"])]
        hour_avg_line = (
            Line()
                .add_xaxis(x_index)
                .add_yaxis("本月", y_data_day_1, label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis("上月", y_data_day_2, label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts("时人均访问量"),
                datazoom_opts=opts.DataZoomOpts(is_show=True),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                yaxis_opts=opts.AxisOpts(
                    name="占比",
                    type_="value",
                    interval=1,
                    axislabel_opts=opts.LabelOpts(formatter="{value} %")  # 设置坐标轴格式
                )
            )
        )
        return day_avg_line, week_avg_line, hour_avg_line

    # 合并
    def draw_buy_pv_page(self):
        pv_buy_day_bar, pv_buy_week_bar, pv_buy_hour_bar = self.draw_buy_pv_chart()
        uv_buy_day_bar, uv_buy_week_bar, uv_buy_hour_bar = self.draw_buy_uv_chart()
        day_buy_avg_line, week_buy_avg_line, hour_buy_avg_line = self.draw_avg_buy_chart()
        pv_page = (
            Page()
                .add(pv_buy_day_bar)
                .add(uv_buy_day_bar)
                .add(day_buy_avg_line)
                .add(pv_buy_week_bar)
                .add(uv_buy_week_bar)
                .add(week_buy_avg_line)
                .add(pv_buy_hour_bar)
                .add(uv_buy_hour_bar)
                .add(hour_buy_avg_line)
        )
        pv_page.render(self.save_buy_view_path)
        with open(self.save_buy_view_path, "r+", encoding='utf-8') as html:
            html_bf = BeautifulSoup(html, 'lxml')
            divs = html_bf.select('.chart-container')
            divs[0]["style"] = "width:33%;height:33%;position:absolute;top:0;left:1%;"
            divs[1]["style"] = "width:33%;height:33%;position:absolute;top:0%;left:34%;"
            divs[2]["style"] = "width:33%;height:33%;position:absolute;top:0%;left:67%;"
            divs[3]["style"] = "width:33%;height:33%;position:absolute;top:50%;left:1%;"
            divs[4]["style"] = "width:33%;height:33%;position:absolute;top:50%;left:34%;"
            divs[5]["style"] = "width:33%;height:33%;position:absolute;top:50%;left:67%;"
            divs[6]["style"] = "width:33%;height:33%;position:absolute;top:100%;left:1%;"
            divs[7]["style"] = "width:33%;height:33%;position:absolute;top:100%;left:34%;"
            divs[8]["style"] = "width:33%;height:33%;position:absolute;top:100%;left:67%;"
            html_new = str(html_bf)
            html.seek(0, 0)
            html.truncate()
            html.write(html_new)
            html.close()

















def main():
    print("这是程序的入口")
    # month_flow = MonthFlow(2018, 3)
    # month_flow.read_month_action_data()
    # month_flow.save_flow_count()
    # month_flow.save_buy_count()
    # month_flow.save_type_count()

    # 接下来是画图
    draw_flow = DramFlow(2018, 3)
    draw_flow.draw_pv_page()
    draw_flow.draw_buy_pv_page()

if __name__ == '__main__':
    main()
    print("程序结束！")
