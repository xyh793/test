import streamlit as st
import json
import os

# 定义数据存储路径
DATA_FILE = "scores.json"

# 初始化 session_state 和加载数据
if 'scores' not in st.session_state:
    if os.path.exists(DATA_FILE):
        # 如果文件存在，加载数据
        with open(DATA_FILE, "r") as f:
            st.session_state.scores = json.load(f)
    else:
        # 如果文件不存在，初始化为空字典
        st.session_state.scores = {}

# 用于存储最近一次提交的分数
if 'last_score' not in st.session_state:
    st.session_state.last_score = None

# 保存数据到文件
def save_scores_to_file():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.scores, f)

# 登录页面
def login_page():
    st.title("登录")
    password = st.text_input("请输入管理员密码", type="password")

    if st.button("登录"):
        # 验证密码
        if password == st.secrets["admin_password"]:
            st.success("登录成功！")
            st.session_state.logged_in = True
            st.rerun()  # 刷新页面以跳转到后台
        else:
            st.error("密码错误，请重试。")

# 后台管理页面
def admin_dashboard():
    st.title("后台管理 - 打分情况")
    
    if not st.session_state.scores:
        st.info("目前还没有任何打分记录。")
    else:
        # 显示每个人的打分情况
        st.write("打分记录：")
        for person, score in st.session_state.scores.items():
            st.write(f"{person}: {score}")

    # 注销按钮
    if st.button("注销"):
        st.session_state.logged_in = False
        st.rerun()  # 刷新页面以跳转到登录页

# 前端打分页面
def scoring_page():
    st.title("打分系统")

    # 输入框：选择人名和分数
    person = st.text_input("请输入要打分的人名")
    score = st.number_input("请输入分数（0-100）", min_value=0, max_value=100, value=0)  # 默认值为 0

    if st.button("提交打分"):
        if person.strip() == "":
            st.error("请输入有效的人名！")
        elif score == 0:
            st.warning("分数为 0，确认是否继续？")
        else:
            # 更新打分记录
            st.session_state.scores[person] = score
            st.session_state.last_score = (person, score)  # 存储最近一次的打分
            save_scores_to_file()  # 将数据保存到文件
            st.success(f"已为 {person} 提交分数：{score}")
            st.write("谢谢打分！")  # 显示感谢信息

    # 显示当前打分记录（仅限最近一次）
    if st.session_state.last_score:
        person, score = st.session_state.last_score
        st.write(f"当前打分：{person}: {score}")

# 主程序逻辑
def main():
    # 检查是否已登录
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        # 如果已登录，显示后台管理页面
        admin_dashboard()
    else:
        # 如果未登录，显示登录页面或打分页面
        page = st.sidebar.radio("导航", ["打分系统", "后台管理"])

        if page == "打分系统":
            scoring_page()
        elif page == "后台管理":
            login_page()

# 运行主程序
if __name__ == "__main__":
    main()
