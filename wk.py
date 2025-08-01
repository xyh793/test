# -*-coding:utf-8-*-
import calendar
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
# 设置页面标题

# 注入自定义 CSS 隐藏 "Hosted with Streamlit" 徽标
st.markdown("""
    <style>
        /* 隐藏 footer 标签中的内容 */
        footer {
            visibility: hidden !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("每月随机工时生成")

# 获取当前日期
current_date = datetime.now()

# 获取当前年份和月份
current_year = current_date.year
current_month = current_date.month

# 用户输入年份和月份
year = st.number_input("请输入年份", min_value=1900, max_value=2100, value=current_year )
month = st.number_input("请输入月份", min_value=1, max_value=12, value=current_month-1 )

# 获取该月的天数和第一天是星期几
first_weekday, last_day = calendar.monthrange(year, month)

# 初始化变量
days = []
weekdays = []
non_working_days = []

# 定义星期字典
weekday_dict = {0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四', 4: '星期五', 5: '星期六', 6: '星期日'}

# 计算每一天的日期和对应的星期几，并标记非工作日（周六和周日）
current_weekday = first_weekday
for i in range(last_day):
    days.append(str(i + 1))  # 日期
    if current_weekday == 5 or current_weekday == 6:  # 周六或周日
        non_working_days.append(i)
    weekdays.append(weekday_dict[current_weekday])  # 星期几
    current_weekday = (current_weekday + 1) % 7  # 逐天递增

# 用户输入项目数量
number_of_projects = st.number_input("请输入项目数量", min_value=1, max_value=10, value=5)

# 随机生成每天的项目数据，确保总和为 8
def generate_daily_data():
    while True:
        n = np.random.choice(range(0, 9), size=number_of_projects)
        if sum(n) == 8:
            return n

# 生成整个月的数据
month_data = np.array([generate_daily_data() for _ in range(last_day)])
month_data = np.transpose(month_data)  # 转置为 (number_of_projects, last_day)

# 将非工作日的数据置为 0
for day_index in non_working_days:
    if day_index >= last_day:
        raise ValueError(f"Invalid day_index: {day_index}")
    month_data[:, day_index] = 0

# 创建一个 Pandas DataFrame 来存储数据
df = pd.DataFrame(month_data, columns=days)
df.insert(0, "项目", [f"项目 {i+1}" for i in range(number_of_projects)])  # 添加项目列

# 将 weekdays 作为新的一行添加到顶部
weekdays_row = pd.DataFrame([["星期"] + weekdays], columns=df.columns)
df = pd.concat([weekdays_row, df], ignore_index=True)

# 显示结果
st.subheader("生成的日历数据")
st.write(f"年份：{year}，月份：{month}")

# 使用 st.dataframe 或 st.table 显示表格
st.dataframe(df)  # 动态表格，支持排序和筛选

# 下载按钮
csv_content = df.to_csv(index=False, encoding='utf-8-sig')  # 导出为 CSV 文件
st.download_button(
    label="下载 CSV 文件",
    data=csv_content.encode('utf-8-sig'),
    file_name=f"{year}_{month}_calendar_data.csv",
    mime="text/csv"
)
