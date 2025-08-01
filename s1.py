import streamlit as st
import pandas as pd
import os
import hashlib

# -----------------------------
# 配置
# -----------------------------

# 参赛者列表
participants = [
    {"编号": 1, "姓名": "张罡铭"},
    {"编号": 2, "姓名": "王小波"},
    {"编号": 3, "姓名": "胡梅"},
    {"编号": 4, "姓名": "陈宇"},
    {"编号": 5, "姓名": "谌淼"},
    {"编号": 6, "姓名": "杨强"},
    {"编号": 7, "姓名": "古棋元"},
    {"编号": 8, "姓名": "陈鑫"},
    {"编号": 9, "姓名": "朱虹润"},
    {"编号": 10, "姓名": "文钰"},
    {"编号": 11, "姓名": "李俊橙"},
    {"编号": 12, "姓名": "董余"},
    {"编号": 13, "姓名": "付勇"},
    {"编号": 14, "姓名": "胡佳佳"},
    {"编号": 15, "姓名": "黄荆荣"},
    {"编号": 16, "姓名": "李治兴"},
]

# 评分权重
weights = {
    "内容契合度": 25,
    "语言表达": 20,
    "情感表现": 20,
    "朗诵技巧": 15,
    "台风形象": 10,
    "原创/创意": 10,
}

# 总分满分
MAX_TOTAL = sum(weights.values())  # 100 分

# 评分数据文件
SCORES_FILE = "scores.csv"

# 发布者密码
PUBLISHER_PASSWORD = "admin123"  # ← 修改为你的密码

# -----------------------------
# 工具函数
# -----------------------------

def hash_password(password):
    """使用 SHA-256 哈希加密密码"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_scores():
    """加载评分数据，确保包含必要列"""
    if os.path.exists(SCORES_FILE):
        df = pd.read_csv(SCORES_FILE)
        # 确保包含 device_id 列
        if "device_id" not in df.columns:
            df["device_id"] = ""  # 新增列，默认为空
        return df
    else:
        # 初始化空 DataFrame
        columns = ["评委ID", "device_id", "编号", "姓名"] + list(weights.keys()) + ["总分"]
        return pd.DataFrame(columns=columns)

def save_scores(df):
    """保存评分数据到 CSV 文件"""
    df.to_csv(SCORES_FILE, index=False)

def clear_scores():
    """清除评分数据文件"""
    if os.path.exists(SCORES_FILE):
        os.remove(SCORES_FILE)
        st.cache_data.clear()  # 清除缓存

def get_device_id():
    """生成设备指纹（基于 IP 和 User-Agent）"""
    try:
        ip = st.context.request.headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0].strip()
    except:
        ip = "127.0.0.1"

    try:
        user_agent = st.context.request.headers.get("User-Agent", "")
    except:
        user_agent = ""

    device_str = f"{ip}-{user_agent}"
    return hashlib.md5(device_str.encode()).hexdigest()

def has_submitted(device_id):
    """检查设备是否已提交评分"""
    if os.path.exists(SCORES_FILE):
        df = load_scores()
        if "device_id" in df.columns:
            return device_id in df["device_id"].dropna().values
    return False

# -----------------------------
# 初始化状态
# -----------------------------

# 获取设备 ID
device_id = get_device_id()

# 检查是否已提交
if "has_submitted" not in st.session_state:
    st.session_state.has_submitted = has_submitted(device_id)

# 生成唯一的评委 ID
if "judge_id" not in st.session_state:
    existing_judges = load_scores()["评委ID"].unique()
    st.session_state.judge_id = f"J{len(existing_judges) + 1:03d}"

# 加载评分数据
all_scores = load_scores()

# -----------------------------
# 页面主函数
# -----------------------------

def main():
    st.title("🎙️ 技术党支部朗诵活动打分表（匿名在线评分）")

    # ========== 显示打分状态（顶部提示）==========
    if st.session_state.has_submitted:
        st.success("✅ 感谢您的评分！您已成功提交，每个设备仅可提交一次。")

    # ========== 显示打分表单（仅未提交时）==========
    if not st.session_state.has_submitted:
        show_scoring_form()

    # ========== 管理区：发布者登录 ==========
    st.sidebar.title("🔐 发布者管理")
    pwd = st.sidebar.text_input("请输入发布者密码", type="password")

    if st.sidebar.button("登录"):
        if hash_password(pwd) == hash_password(PUBLISHER_PASSWORD):
            st.session_state.publisher_logged_in = True
            st.sidebar.success("登录成功！")
        else:
            st.sidebar.error("密码错误")

    # ========== 发布者功能（仅登录后可见）==========
    if st.session_state.get("publisher_logged_in", False):
        display_publisher_dashboard()

# -----------------------------
# 评委打分表单
# -----------------------------

def show_scoring_form():
    """显示评分表单"""
    st.subheader("📝 请为每位参赛者打分（满分100分）")
    st.markdown("📌 **评分标准**：")
    for category, max_score in weights.items():
        st.markdown(f"- **{category}**：满分 {max_score} 分")

    new_scores = []

    with st.form(key="scoring_form"):
        for participant in participants:
            with st.expander(f"🎤 {participant['姓名']} (编号: {participant['编号']})", expanded=True):
                score_row = {
                    "评委ID": st.session_state.judge_id,
                    "device_id": device_id,
                    "编号": participant["编号"],
                    "姓名": participant["姓名"],
                }

                total = 0
                cols = st.columns(len(weights))
                for i, (category, max_score) in enumerate(weights.items()):
                    with cols[i]:
                        score = st.number_input(
                            f"{category} (0~{max_score})",
                            min_value=0,
                            max_value=max_score,
                            step=1,
                            key=f"{participant['编号']}_{category}",
                            help=f"本项满分 {max_score} 分"
                        )
                        score_row[category] = score
                        total += score

                score_row["总分"] = total
            st.caption(f"✅ {participant['姓名']} 当前总分：{total} / {MAX_TOTAL}")
            new_scores.append(score_row)

        submitted = st.form_submit_button("📤 提交所有评分")

        if submitted:
            # 校验分数范围
            for row in new_scores:
                for category, max_score in weights.items():
                    if not (0 <= row[category] <= max_score):
                        st.error(f"❌ {category} 分数超出范围（应为 0~{max_score}）")
                        return

            # 再次检查是否已提交
            if has_submitted(device_id):
                st.error("⚠️ 您的设备已提交过评分，不可重复提交。")
                st.session_state.has_submitted = True
                return

            # 保存评分
            new_df = pd.DataFrame(new_scores)
            global all_scores
            all_scores = pd.concat([all_scores, new_df], ignore_index=True)
            save_scores(all_scores)

            st.session_state.has_submitted = True
            st.success("🎉 感谢您的评分！数据已提交。每个设备仅可提交一次。")

# -----------------------------
# 发布者功能面板
# -----------------------------

def display_publisher_dashboard():
    """显示发布者管理面板"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 管理功能")

    # 安全获取已提交设备数
    if "device_id" in all_scores.columns:
        submitted_devices = all_scores[all_scores["device_id"] != ""]["device_id"].nunique()
    else:
        submitted_devices = 0

    st.sidebar.write(f"✅ 已收到 {submitted_devices} 份评分")
    st.sidebar.write(f"🎯 共 {len(participants)} 位参赛者")

    # 一键清除
    if st.sidebar.button("🗑️ 一键清除所有评分"):
        clear_scores()
        st.session_state.clear()
        st.experimental_rerun()

    # 显示最终得分
    display_final_scores_publisher()

def display_final_scores_publisher():
    """显示最终得分（仅发布者可见）"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 最终得分（仅发布者可见）")

    if all_scores.empty or all_scores["总分"].sum() == 0:
        st.sidebar.info("
