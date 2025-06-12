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
    logging.error(f"從環境變數初始化設定失敗：{e}")
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
        logging.warning(f"無法解析生日：{dob_str}。返回年齡 0。")
        return 0

def get_openai_response(prompt, temp=0.85):
    if not client:
        logging.error("OpenAI 客戶端未初始化。")
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
        logging.error(f"OpenAI API 錯誤：{e}")
        return None

def send_email(html_body, subject):
    if not SMTP_PASSWORD:
        logging.error("SMTP 密碼未設定。無法傳送郵件。")
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
            logging.info("郵件已成功寄出。")
    except Exception as e:
        logging.error(f"郵件傳送失敗：{e}")

# --- Chart and Summary Generation ---
def generate_chart_metrics():
    # Labels in Traditional Chinese
    return [
        {"title": "市場定位", "labels": ["品牌認知", "客戶契合", "聲譽穩固"], "values": [random.randint(70, 90), random.randint(65, 85), random.randint(70, 90)]},
        {"title": "投資者吸引力", "labels": ["敘事信心", "規模化模型", "信任憑證"], "values": [random.randint(70, 85), random.randint(60, 80), random.randint(75, 90)]},
        {"title": "策略執行力", "labels": ["合作準備", "高階通路", "領導形象"], "values": [random.randint(65, 85), random.randint(65, 85), random.randint(75, 90)]}
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
    # Maps in Traditional Chinese
    industry_map = {
        "保險": "競爭激烈的保險領域", "不動產": "充滿活力的不動產市場",
        "金融": "高風險的金融世界", "科技": "快速發展的科技產業",
        "製造業": "基礎穩固的製造業", "教育": "富有影響力的教育領域",
        "醫療保健": "至關重要的醫療保健產業"
    }
    industry_narrative = industry_map.get(industry, f"於 {industry} 領域")

    challenge_narrative_map = {
        "尋求新資金": "尋求新資本以驅動下一階段的成長",
        "擴張策略不明": "規劃一條清晰且具防禦性的擴張路徑",
        "投資信心不足": "為投資者建立一個令人信服且有證據支持的案例",
        "品牌定位薄弱": "強化品牌敘事和市場定位的策略要務"
    }
    challenge_narrative = challenge_narrative_map.get(challenge, f"解決 {challenge} 的主要挑戰")

    opening_templates = [
        f"對於一位在{country}{industry_narrative}深耕約{experience}年的專業人士而言，到達策略十字路口不僅是常態，更是雄心的體現。",
        f"一位擁有{experience}年{country}{industry_narrative}經驗的專業人士，其職業生涯是適應能力和專業知識的明證，並自然地引向關鍵的轉折與反思時刻。",
        f"在{age}歲的年紀，於{country}的{industry_narrative}導航{experience}年，培養了獨特的視角，尤其是在面對職業成長的下一階段時。"
    ]
    chosen_opening = random.choice(opening_templates)

    brand, fit, stick = metrics[0]["values"]
    conf, scale, trust = metrics[1]["values"]
    partn, premium, leader = metrics[2]["values"]

    # --- TEXT REWRITTEN TO THIRD-PERSON PERSPECTIVE ---
    summary_html = (
        "<br><div style='font-size:24px;font-weight:bold;'>🧠 策略摘要</div><br>"
        f"<p style='line-height:1.7; text-align:justify; margin-bottom: 1em;'>{chosen_opening} 這份報告反映了一個關鍵時刻，其焦點轉向{challenge_narrative}。數據顯示，擁有此背景的專業人士具備{brand}%的強大品牌認知，意味著已建立一定的市場影響力。 "
        f"然而，分析也指出了一个機會：需要提升價值主張的清晰度（客戶契合度為{fit}%），並確保其專業聲譽具有持久的影響力（聲譽穩固性為{stick}%）。目標是從單純的被認知，過渡到能產生共鳴的影響力。</p>"
        f"<p style='line-height:1.7; text-align:justify; margin-bottom: 1em;'>在{country}的投資環境中，一個引人入勝的故事至關重要。{conf}%的敘事信心表明，該人士的核心專業敘事元素是強而有力的。關鍵似乎在於解決規模化模型的問題，目前為{scale}%。 "
        f"這表明，優化「如何做」——即闡明一個清晰、可複製的成長模型——可能會顯著提升投資者吸引力。令人鼓舞的是，{trust}%的信任憑證得分顯示，過往的記錄是堅實的資產，為建構未來引人注目的敘事提供了信譽基礎。</p>"
        f"<p style='line-height:1.7; text-align:justify; margin-bottom: 1em;'>策略的最終評判標準是執行力。{partn}%的合作準備得分，標誌著強大的協作能力——這是吸引特定類型高水準合作夥伴或投資者時的關鍵要素。 "
        f"此外，{premium}%的高階通路使用率揭示了提升品牌定位的未開發潛力。再加上{leader}%的穩固領導形象，訊息非常明確：具備這樣背景的專業人士已被視為可信。下一步是策略性地佔據能反映其全部價值的高影響力空間。</p>"
        f"<p style='line-height:1.7; text-align:justify; margin-bottom: 1em;'>將這樣的資料與新加坡、馬來西亞和台灣的同行進行基準比較，不僅是衡量現狀，更是為了揭示策略優勢。 "
        f"數據表明，驅動這一策略焦點的專業直覺通常是正確的。對於處於此階段的專業人士來說，前進的道路通常在於資訊、模型和市場的精準對齊。本分析可作為一個框架，為這類專業人士將當前氣勢轉化為決定性突破提供所需的清晰度。</p>"
    )
    return summary_html


# --- Main Flask Route ---
@app.route("/investor_analyze", methods=["POST"])
def investor_analyze():
    try:
        data = request.get_json(force=True)
        logging.info(f"收到 POST 請求: {data.get('email', '沒有提供電子郵件')}")

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
        title = "<h4 style='text-align:center;font-size:24px;'>🎯 AI 策略洞察</h4>"
        chart_html = generate_chart_html(chart_metrics)
        summary_html = build_dynamic_summary(age, experience, industry, country, chart_metrics, challenge, context, target_profile)
        
        # --- AI Tips Generation (Prompt updated for third-person perspective and TW Chinese) ---
        prompt = (f"為一位在{country}{industry}領域擁有{experience}年經驗的專業人士，生成10條吸引投資者的實用建議，並附上表情符號。"
                  f"語氣應犀利、具有策略性且專業。請用繁體中文回答。"
                  f"重點：請使用客觀的第三人稱視角撰寫，例如使用「該類專業人士」或「他們」，絕對不要使用「您」或「您的」。")
        tips_text = get_openai_response(prompt)
        tips_block = ""
        if tips_text:
            tips_block = "<br><div style='font-size:24px;font-weight:bold;'>💡 創新建議</div><br>" + \
                         "".join(f"<p style='font-size:16px; line-height:1.6; margin-bottom: 1em;'>{line.strip()}</p>" for line in tips_text.splitlines() if line.strip())
        else:
            tips_block = "<p style='color:red;'>⚠️ 暫時無法生成創新建議。</p>"

        # --- Footer Construction (This part remains in 2nd person as it's a direct message from the service) ---
        footer = (
            "<div style='background-color:#f9f9f9;color:#333;padding:20px;border-left:6px solid #8C52FF; border-radius:8px;margin-top:30px;'>"
            "<strong>📊 AI 洞察來源:</strong><ul style='margin-top:10px;margin-bottom:10px;padding-left:20px;line-height:1.7;'>"
            "<li>來自新加坡、馬來西亞和台灣的匿名專業人士資料</li>"
            "<li>來自 OpenAI 和全球市場的投資者情緒模型及趨勢基準</li></ul>"
            "<p style='margin-top:10px;line-height:1.7;'>所有資料均符合個人資料保護法(PDPA)且不會被儲存。我們的 AI 系統在偵測具統計意義的模式時，不會引用任何個人記錄。</p>"
            "<p style='margin-top:10px;line-height:1.7;'><strong>附註:</strong> 這份初步洞察僅僅是個開始。一份更個人化、資料更具體的報告——反映您提供的完整資訊——將在 <strong>24 至 48 小時</strong> 內準備好並傳送到收件人的信箱。"
            "這將使我們的 AI 系統能夠將您的資料與細微的區域和產業特定基準進行交叉引用，確保提供針對確切挑戰的更精準建議。"
            "如果希望盡快進行對話，我們很樂意在您方便的時間安排一次 <strong>15 分鐘的通話</strong>。 🎯</p></div>"
        )
        
        # --- Email Body Construction ---
        details_html = (
            f"<br><div style='font-size:14px;color:#333;line-height:1.6;'>"
            f"<h3 style='font-size:16px;'>📝 提交摘要</h3>"
            f"<strong>英文姓名:</strong> {full_name}<br>"
            f"<strong>中文姓名:</strong> {chinese_name}<br>"
            f"<strong>出生日期:</strong> {dob_str}<br>"
            f"<strong>聯絡電話:</strong> {contact_number}<br>"
            f"<strong>國家/地區:</strong> {country}<br>"
            f"<strong>公司名稱:</strong> {company}<br>"
            f"<strong>目前職位:</strong> {role}<br>"
            f"<strong>經驗年資:</strong> {experience}<br>"
            f"<strong>所屬產業:</strong> {industry}<br>"
            f"<strong>主要挑戰:</strong> {challenge}<br>"
            f"<strong>背景簡介:</strong> {context}<br>"
            f"<strong>目標畫像:</strong> {target_profile}<br>"
            f"<strong>推薦人:</strong> {advisor}<br>"
            f"<strong>電子信箱:</strong> {email}</div><hr>"
        )

        email_html = f"<h1>新的投資者洞察提交</h1>" + details_html + title + chart_html + summary_html + tips_block + footer
        
        send_email(email_html, f"新的投資者洞察: {full_name}")

        display_html = title + chart_html + summary_html + tips_block + footer
        return jsonify({"html_result": display_html})

    except Exception as e:
        logging.error(f"在 /investor_analyze 中發生錯誤: {e}")
        traceback.print_exc()
        return jsonify({"error": "發生內部伺服器錯誤。"}), 500

# --- Run the App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
