import streamlit as st
import pandas as pd
import sqlite3

# 设置页面标题
st.set_page_config(page_title="在线文档", page_icon="📝")

# 标题
st.title("在线文档 📝")
st.subheader("在这里填写你的姓名和年龄，其他人也可以看到！")

# 初始化 SQLite 数据库
def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    # 创建表格（如果不存在）
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# 插入新记录
def add_user(name, age):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
    conn.commit()
    conn.close()

# 获取所有记录
def get_all_users():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT id, name, age FROM users")  # 返回 ID、姓名和年龄
    users = c.fetchall()
    conn.close()
    return users

# 删除指定记录
def delete_user(user_id):
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# 重新排列 ID
def reset_ids():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    # 1. 创建临时表并复制数据
    c.execute("CREATE TEMPORARY TABLE temp_users AS SELECT name, age FROM users")

    # 2. 删除原表
    c.execute("DROP TABLE users")

    # 3. 重新创建原表
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    """)

    # 4. 将数据重新插入原表
    c.execute("INSERT INTO users (name, age) SELECT name, age FROM temp_users")

    # 5. 删除临时表
    c.execute("DROP TABLE temp_users")

    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# 用户输入部分
with st.form(key="user_form"):
    st.write("请输入你的信息：")
    user_name = st.text_input("姓名：")
    user_age = st.number_input("年龄：", min_value=0, step=1)
    submit_button = st.form_submit_button(label="提交")

    if submit_button:
        if user_name.strip() != "":
            add_user(user_name, user_age)
            st.success(f"已添加：{user_name}，年龄：{user_age}")
        else:
            st.error("姓名不能为空，请重新输入！")

# 显示所有用户
st.subheader("所有已填写的信息：")
users = get_all_users()
if users:
    df = pd.DataFrame(users, columns=["ID", "姓名", "年龄"])
    st.table(df)
else:
    st.info("目前还没有人填写信息。")

# 删除功能
st.subheader("删除记录")
delete_id = st.number_input("请输入要删除的记录的 ID：", min_value=1, step=1)
if st.button("删除"):
    delete_user(delete_id)
    st.success(f"已删除 ID 为 {delete_id} 的记录！")
    reset_ids()  # 删除后重新排列 ID
    st.rerun()

# 刷新按钮
if st.button("刷新页面"):
    st.rerun()