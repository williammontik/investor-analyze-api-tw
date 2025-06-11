# -*- coding: utf-8 -*-
import os
import logging
import smtplib
import traceback
import random
from datetime import datetime
from dateutil import parser
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

# --- Initialization ---
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

# --- Configuration ---
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
except Exception as e:
    logging.error(f"Failed to initialize configuration from environment variables: {e}")
    client = None
    SMTP_PASSWORD = None

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"

# --- Helper Functions ---
def compute_age(dob_str):
    try:
        birth_date = parser.parse(dob_str)
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except (ValueError, TypeError):
        logging.warning(f"Could not parse DOB: {dob_str}. Returning age 0.")
        return 0

def get_openai_response(prompt, temp=0.85):
    if not client:
        logging.error("OpenAI client not initialized.")
        return None
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return None

def send_email(html_body, subject):
    if not SMTP_PASSWORD:
        logging.error("SMTP password not configured. Cannot send email.")
        return
    msg = MIMEText(html_body, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = SMTP_USERNAME
    msg['To'] = SMTP_USERNAME
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Email sending failed: {e}")

# --- Chart and Summary Generation ---
def generate_chart_metrics():
    # Labels in Simplified Chinese
    return [
        {"title": "市场定位", "labels": ["品牌认知", "客户契合", "声誉稳固"], "values": [random.randint(70, 90), random.randint(65, 85), random.randint(70, 90)]},
        {"title": "投资者吸引力", "labels": ["叙事信心", "规模化模型", "信任凭证"], "values": [random.randint(70, 85), random.randint(60, 80), random.randint(75, 90)]},
        {"title": "战略执行力", "labels": ["合作准备", "高端渠道", "领导形象"], "values": [random.randint(65, 85), random.randint(65, 85), random.randint(75, 90)]}
    ]

def generate_chart_html(metrics):
    colors = ["#8C52FF", "#5E9CA0", "#F2A900"]
    html = ""
    for metric in metrics:
        html += f"<strong style='font-size:18px;color:#333;'>{metric['title']}</strong><br>"
        for j, (label, val) in enumerate(zip(metric['labels'], metric['values'])):
            html += (
                f"<div style='display:flex;align-items:center;margin-bottom:8px;'>"
                f"<span style='width:120px; font-size: 15px;'>{label}</span>"
                f"<div style='flex:1;background:#eee;border-radius:5px;overflow:hidden;'>"
                f"<div style='width:{val}%;height:14px;background:{colors[j % len(colors)]};'></div></div>"
                f"<span style='margin-left:10px; font-size: 15px;'>{val}%</span></div>"
            )
        html += "<br>"
    return html

def build_dynamic_summary(age, experience, industry, country, metrics, challenge, context, target_profile):
    # Maps in Simplified Chinese
    industry_map = {
        "保险": "竞争激烈的保险领域", "房地产": "充满活力的房地产市场",
        "金融": "高风险的金融世界", "科技": "快速发展的科技行业",
        "制造业": "基础稳固的制造业", "教育": "富有影响力的教育领域",
        "医疗保健": "至关重要的医疗保健行业"
    }
    industry_narrative = industry_map.get(industry, f"于 {industry} 领域")

    challenge_narrative_map = {
        "寻求新资金": "寻求新资本以驱动下一阶段的增长",
        "扩张策略不明": "规划一条清晰且具防御性的扩张路径",
        "投资信心不足": "为投资者建立一个令人信服且有证据支持的案例",
        "品牌定位薄弱": "强化品牌叙事和市场定位的战略要务"
    }
    challenge_narrative = challenge_narrative_map.get(challenge, f"解决 {challenge} 的主要挑战")

    opening_templates = [
        f"对于一位在{country}{industry_narrative}深耕约{experience}年的专业人士而言，到达战略十字路口不仅是常态，更是雄心的体现。",
        f"一位拥有{experience}年{country}{industry_narrative}经验的专业人士，其职业生涯是适应能力和专业知识的明证，并自然地引向关键的转折与反思时刻。",
        f"在{age}岁的年纪，于{country}的{industry_narrative}导航{experience}年，培养了独特的视角，尤其是在面对职业成长的下一阶段时。"
    ]
    chosen_opening = random.choice(opening_templates)

    brand, fit, stick = metrics[0]["values"]
    conf, scale, trust = metrics[1]["values"]
    partn, premium, leader = metrics[2]["values"]

    # --- TEXT REWRITTEN TO THIRD-PERSON PERSPECTIVE ---
    summary_html = (
        "<br><div style='font-size:24px;font-weight:bold;'>🧠 战略摘要</div><br>"
        f"<p style='line-height:1.7; text-align:justify; margin-bottom: 1em;'>{chosen_opening} 这份报告反映了一个关键时刻，其焦点转向{challenge_narrative}。数据显示，拥有此背景的专业人士具备{brand}%的强大品牌认知，意味着已建立一定的市场影响力。 "
        f"然而，分析也指出了一个机会：需要提升价值主张的清晰度（客户契合度为{fit}%），并确保其专业声誉具有持久的影响力（声誉稳固性为{stick}%）。目标是从简单的被认知，过渡到能产生共鸣的影响力。</p>"
        f"<p style='line-height:1.7; text-align:justify; margin-bottom: 1em;'>在{country}的投资环境中，一个引人入胜的故事至关重要。{conf}%的叙事信心表明，该人士的核心专业叙事元素是强有力的。关键似乎在于解决规模化模型的问题，目前为{scale}%。 "
        f"这表明，优化“如何做”——即阐明一个清晰、可复制的增长模型——可能会显著提升投资者吸引力。令人鼓舞的是，{trust}%的信任凭证得分显示，过往的记录是坚实的资产，为构建未来引人注目的叙事提供了信誉基础。</p>"
        f"<p style='line-height:1.7; text-align:justify; margin-bottom: 1em;'>战略的最终评判标准是执行力。{partn}%的合作准备得分，标志着强大的协作能力——这是吸引特定类型高水平合作伙伴或投资者时的关键要素。 "
        f"此外，{premium}%的高端渠道使用率揭示了提升品牌定位的未开发潜力。再加上{leader}%的稳固领导形象，信息非常明确：具备这样背景的专业人士已被视为可信。下一步是战略性地占据能反映其全部价值的高影响力空间。</p>"
        f"<p style='line-height:1.7; text-align:justify; margin-bottom: 1em;'>将这样的资料与新加坡、马来西亚和台湾的同行进行基准比较，不仅是衡量现状，更是为了揭示战略优势。 "
        f"数据表明，驱动这一战略焦点的专业直觉通常是正确的。对于处于此阶段的专业人士来说，前进的道路通常在于信息、模型和市场的精准对齐。本分析可作为一个框架，为这类专业人士将当前势头转化为决定性突破提供所需的清晰度。</p>"
    )
    return summary_html


# --- Main Flask Route ---
@app.route("/investor_analyze", methods=["POST"])
def investor_analyze():
    try:
        data = request.get_json(force=True)
        logging.info(f"Received POST request: {data.get('email', 'No email provided')}")

        # --- Data Extraction ---
        full_name = data.get("fullName", "N/A")
        chinese_name = data.get("chineseName", "N/A")
        dob_str = data.get("dob", "N/A")
        contact_number = data.get("contactNumber", "N/A")
        company = data.get("company", "N/A")
        role = data.get("role", "N/A")
        country = data.get("country", "N/A")
        experience = data.get("experience", "N/A")
        industry = data.get("industry", "N/A")
        challenge = data.get("challenge", "N/A")
        context = data.get("context", "N/A")
        target_profile = data.get("targetProfile", "N/A")
        advisor = data.get("advisor", "N/A")
        email = data.get("email", "N/A")
        
        # --- Data Processing ---
        age = compute_age(dob_str)
        chart_metrics = generate_chart_metrics()
        
        # --- HTML Generation ---
        title = "<h4 style='text-align:center;font-size:24px;'>🎯 AI 战略洞察</h4>"
        chart_html = generate_chart_html(chart_metrics)
        summary_html = build_dynamic_summary(age, experience, industry, country, chart_metrics, challenge, context, target_profile)
        
        # --- AI Tips Generation (Prompt updated for third-person perspective) ---
        prompt = (f"为一位在{country}{industry}领域拥有{experience}年经验的专业人士，生成10条吸引投资者的实用建议，并附上表情符号。"
                  f"语气应犀利、具有战略性且专业。请用简体中文回答。"
                  f"重点：请使用客观的第三人称视角撰写，例如使用“该类专业人士”或“他们”，绝对不要使用“您”或“您的”。")
        tips_text = get_openai_response(prompt)
        tips_block = ""
        if tips_text:
            tips_block = "<br><div style='font-size:24px;font-weight:bold;'>💡 创新建议</div><br>" + \
                         "".join(f"<p style='font-size:16px; line-height:1.6; margin-bottom: 1em;'>{line.strip()}</p>" for line in tips_text.splitlines() if line.strip())
        else:
            tips_block = "<p style='color:red;'>⚠️ 暂时无法生成创新建议。</p>"

        # --- Footer Construction (This part remains in 2nd person as it's a direct message from the service) ---
        footer = (
            "<div style='background-color:#f9f9f9;color:#333;padding:20px;border-left:6px solid #8C52FF; border-radius:8px;margin-top:30px;'>"
            "<strong>📊 AI 洞察来源:</strong><ul style='margin-top:10px;margin-bottom:10px;padding-left:20px;line-height:1.7;'>"
            "<li>来自新加坡、马来西亚和台湾的匿名专业人士数据</li>"
            "<li>来自 OpenAI 和全球市场的投资者情绪模型及趋势基准</li></ul>"
            "<p style='margin-top:10px;line-height:1.7;'>所有数据均符合个人数据保护法(PDPA)且不会被储存。我们的 AI 系统在检测具统计意义的模式时，不会引用任何个人记录。</p>"
            "<p style='margin-top:10px;line-height:1.7;'><strong>附言:</strong> 这份初步洞察仅仅是个开始。一份更个性化、数据更具体的报告——反映您提供的完整信息——将在 <strong>24 至 48 小时</strong> 内准备并发送到收件人的邮箱。"
            "这将使我们的 AI 系统能够将您的资料与细微的区域和行业特定基准进行交叉引用，确保提供针对确切挑战的更精准建议。"
            "如果希望尽快进行对话，我们很乐意在您方便的时间安排一次 <strong>15 分钟的通话</strong>。 🎯</p></div>"
        )
        
        # --- Email Body Construction ---
        details_html = (
            f"<br><div style='font-size:14px;color:#333;line-height:1.6;'>"
            f"<h3 style='font-size:16px;'>📝 提交摘要</h3>"
            f"<strong>英文姓名:</strong> {full_name}<br>"
            f"<strong>中文姓名:</strong> {chinese_name}<br>"
            f"<strong>出生日期:</strong> {dob_str}<br>"
            f"<strong>联系电话:</strong> {contact_number}<br>"
            f"<strong>国家/地区:</strong> {country}<br>"
            f"<strong>公司名称:</strong> {company}<br>"
            f"<strong>当前职位:</strong> {role}<br>"
            f"<strong>经验年限:</strong> {experience}<br>"
            f"<strong>所属行业:</strong> {industry}<br>"
            f"<strong>主要挑战:</strong> {challenge}<br>"
            f"<strong>背景简介:</strong> {context}<br>"
            f"<strong>目标画像:</strong> {target_profile}<br>"
            f"<strong>推荐人:</strong> {advisor}<br>"
            f"<strong>电子邮箱:</strong> {email}</div><hr>"
        )

        email_html = f"<h1>新的投资者洞察提交</h1>" + details_html + title + chart_html + summary_html + tips_block + footer
        
        send_email(email_html, f"新的投资者洞察: {full_name}")

        display_html = title + chart_html + summary_html + tips_block + footer
        return jsonify({"html_result": display_html})

    except Exception as e:
        logging.error(f"An error occurred in /investor_analyze: {e}")
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred."}), 500

# --- Run the App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
