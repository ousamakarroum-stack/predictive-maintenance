"""
نظام التنبيهات التلقائية بالEmail
===================================
كيبعت email تلقائي لمسؤول الصيانة
عندما يتجاوز احتمال العطل الحد المحدد
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


# ─────────────────────────────────────────────
# إعدادات Email — غير هاد البيانات ديالك
# ─────────────────────────────────────────────

EMAIL_CONFIG = {
    'sender_email':    'ousamaka84@gmail.com',      # emailك
    'sender_password': 'dhrs ydza mcwk uzqe',          # App Password ديال Gmail
    'receiver_email':  'ousama.karroum@gmail.com', # email ديال المسؤول
    'smtp_server':     'smtp.gmail.com',
    'smtp_port':       587,
}

ALERT_THRESHOLD  = 0.75   # 75% — تحذير
DANGER_THRESHOLD = 0.90   # 90% — خطر عاجل


# ─────────────────────────────────────────────
# دالة بناء الرسالة
# ─────────────────────────────────────────────

def build_email(reading, risk_prob, machine_name="Machine A"):
    risk_pct = risk_prob * 100
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if risk_pct >= DANGER_THRESHOLD * 100:
        level = "🔴 DANGER — توقف فوري مطلوب"
        color = "#dc3545"
    else:
        level = "🟡 AVERTISSEMENT — مراقبة فورية"
        color = "#fd7e14"

    html = f"""
    <html><body style="font-family: Arial, sans-serif; direction: rtl;">
        <div style="max-width:600px; margin:auto; border:2px solid {color}; border-radius:10px; padding:20px;">

            <h2 style="color:{color}; text-align:center;">
                ⚠️ تنبيه صيانة تنبؤية
            </h2>

            <p style="font-size:18px; text-align:center;">
                <strong>{level}</strong>
            </p>

            <hr>

            <table style="width:100%; border-collapse:collapse;">
                <tr style="background:#f8f9fa;">
                    <td style="padding:10px; border:1px solid #dee2e6;"><strong>المعدة</strong></td>
                    <td style="padding:10px; border:1px solid #dee2e6;">{machine_name}</td>
                </tr>
                <tr>
                    <td style="padding:10px; border:1px solid #dee2e6;"><strong>الوقت</strong></td>
                    <td style="padding:10px; border:1px solid #dee2e6;">{timestamp}</td>
                </tr>
                <tr style="background:#f8f9fa;">
                    <td style="padding:10px; border:1px solid #dee2e6;"><strong>احتمال العطل</strong></td>
                    <td style="padding:10px; border:1px solid #dee2e6; color:{color}; font-size:20px;">
                        <strong>{risk_pct:.1f}%</strong>
                    </td>
                </tr>
            </table>

            <h3 style="margin-top:20px;">📊 قراءات الحساسات:</h3>
            <table style="width:100%; border-collapse:collapse;">
                <tr style="background:#343a40; color:white;">
                    <th style="padding:8px;">الحساس</th>
                    <th style="padding:8px;">القيمة</th>
                    <th style="padding:8px;">الحالة</th>
                </tr>
                <tr>
                    <td style="padding:8px; border:1px solid #dee2e6;">🌡️ الحرارة</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">{reading['temperature']}°C</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">
                        {"⚠️ مرتفع" if reading['temperature'] > 85 else "✅ طبيعي"}
                    </td>
                </tr>
                <tr style="background:#f8f9fa;">
                    <td style="padding:8px; border:1px solid #dee2e6;">📳 الاهتزاز</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">{reading['vibration']} mm/s</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">
                        {"⚠️ مرتفع" if reading['vibration'] > 1.2 else "✅ طبيعي"}
                    </td>
                </tr>
                <tr>
                    <td style="padding:8px; border:1px solid #dee2e6;">⚡ التيار</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">{reading['current']} A</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">
                        {"⚠️ مرتفع" if reading['current'] > 20 else "✅ طبيعي"}
                    </td>
                </tr>
                <tr style="background:#f8f9fa;">
                    <td style="padding:8px; border:1px solid #dee2e6;">💨 الضغط</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">{reading['pressure']} bar</td>
                    <td style="padding:8px; border:1px solid #dee2e6;">
                        {"⚠️ مرتفع" if reading['pressure'] > 120 else "✅ طبيعي"}
                    </td>
                </tr>
            </table>

            <div style="background:#fff3cd; border:1px solid #ffc107; border-radius:5px; padding:15px; margin-top:20px;">
                <strong>⚡ الإجراء المطلوب:</strong><br>
                {"توقف فوري للمعدة وإشعار فريق الصيانة!" if risk_pct >= 90 else "مراقبة المعدة وجدولة صيانة في أقرب وقت."}
            </div>

            <p style="text-align:center; color:#6c757d; margin-top:20px; font-size:12px;">
                تم الإرسال تلقائياً بواسطة نظام Predictive Maintenance<br>
                <a href="https://predictive-maintenancebysam.streamlit.app">عرض الداشبورد</a>
            </p>
        </div>
    </body></html>
    """
    return html


# ─────────────────────────────────────────────
# دالة إرسال Email
# ─────────────────────────────────────────────

def send_alert(reading, risk_prob, machine_name="Machine A"):
    """
    كتبعت email تنبيه لمسؤول الصيانة
    Returns: True إذا تم الإرسال، False إذا فشل
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"⚠️ تنبيه صيانة — {machine_name} — {risk_prob*100:.0f}% خطر"
        msg['From']    = EMAIL_CONFIG['sender_email']
        msg['To']      = EMAIL_CONFIG['receiver_email']

        html_content = build_email(reading, risk_prob, machine_name)
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.sendmail(
                EMAIL_CONFIG['sender_email'],
                EMAIL_CONFIG['receiver_email'],
                msg.as_string()
            )

        print(f"✅ Email تم الإرسال → {EMAIL_CONFIG['receiver_email']}")
        return True

    except Exception as e:
        print(f"❌ فشل الإرسال: {e}")
        return False


# ─────────────────────────────────────────────
# دالة التحقق من إرسال التنبيه
# (ما نبعتوش أكثر من مرة كل 10 دقائق)
# ─────────────────────────────────────────────

last_alert_time = {}

def should_send_alert(machine_name, cooldown_minutes=10):
    import time
    now = time.time()
    last = last_alert_time.get(machine_name, 0)
    if now - last > cooldown_minutes * 60:
        last_alert_time[machine_name] = now
        return True
    return False


def check_and_alert(reading, risk_prob, machine_name="Machine A"):
    """
    الدالة الرئيسية — كتستعملها مع الداشبورد
    """
    if risk_prob >= DANGER_THRESHOLD:
        if should_send_alert(machine_name):
            print(f"🔴 خطر عاجل! ({risk_prob*100:.0f}%) — جاري إرسال تنبيه...")
            send_alert(reading, risk_prob, machine_name)

    elif risk_prob >= ALERT_THRESHOLD:
        if should_send_alert(machine_name, cooldown_minutes=30):
            print(f"🟡 تحذير ({risk_prob*100:.0f}%) — جاري إرسال تنبيه...")
            send_alert(reading, risk_prob, machine_name)


# ─────────────────────────────────────────────
# اختبار
# ─────────────────────────────────────────────

if __name__ == "__main__":
    test_reading = {
        'temperature':   95.0,
        'vibration':     1.8,
        'pressure':      128.0,
        'current':       21.5,
        'rpm':           2600.0,
        'oil_viscosity': 39.0
    }

    print("=" * 50)
    print("  اختبار نظام التنبيهات")
    print("=" * 50)
    print("\n⚠️  قبل ما تشغل هاد الكود:")
    print("   1. بدل sender_email بـ Gmail ديالك")
    print("   2. فعل 2-Factor Authentication على Gmail")
    print("   3. دير App Password من myaccount.google.com")
    print("   4. حط App Password في sender_password\n")

    html = build_email(test_reading, 0.92, "Compresseur A")
    with open("test_email_preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ معاينة الEmail محفوظة في: test_email_preview.html")
    print("   افتحها في المتصفح باش تشوف كيفاش غادي تبان!")
