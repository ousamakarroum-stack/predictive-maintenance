"""
Predictive Maintenance — Streamlit Dashboard
=============================================
تشغيل: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import joblib
import os
import time
from datetime import datetime

# ─────────────────────────────────────────────
# إعداد الصفحة
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Predictive Maintenance",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Predictive Maintenance Dashboard")
st.markdown("نظام مراقبة المعدات في الوقت الحقيقي")
st.divider()

# ─────────────────────────────────────────────
# تحميل النموذج
# ─────────────────────────────────────────────

@st.cache_resource
def load_model():
    if os.path.exists("maintenance_model.pkl"):
        model  = joblib.load("maintenance_model.pkl")
        scaler = joblib.load("maintenance_scaler.pkl")
        return model, scaler
    return None, None

model, scaler = load_model()

# ─────────────────────────────────────────────
# Sidebar — إعدادات
# ─────────────────────────────────────────────

st.sidebar.header("⚙️ إعدادات المحاكاة")

mode = st.sidebar.selectbox(
    "نوع المحاكاة",
    ["gradual", "normal", "fault"],
    format_func=lambda x: {
        "normal":  "🟢 معدة سليمة",
        "fault":   "🔴 معدة معطوبة",
        "gradual": "🟡 تدهور تدريجي"
    }[x]
)

speed = st.sidebar.slider("سرعة التحديث (ثانية)", 0.5, 3.0, 1.0, 0.5)
n_points = st.sidebar.slider("عدد النقاط في الرسم", 20, 100, 40)

st.sidebar.divider()
st.sidebar.markdown("**حدود التنبيه**")
warn_threshold  = st.sidebar.slider("🟡 تحذير %",  20, 60, 40)
alert_threshold = st.sidebar.slider("🔴 خطر %",    60, 95, 75)

# ─────────────────────────────────────────────
# دالة توليد البيانات
# ─────────────────────────────────────────────

def generate_reading(mode, step):
    progress = min(step / 30, 1.0)
    if mode == "normal":
        return {
            'temperature':   round(np.random.normal(70, 3), 2),
            'vibration':     round(np.random.normal(0.5, 0.05), 3),
            'pressure':      round(np.random.normal(100, 5), 2),
            'current':       round(np.random.normal(15, 1), 2),
            'rpm':           round(np.random.normal(3000, 80), 1),
            'oil_viscosity': round(np.random.normal(46, 2), 2),
        }
    elif mode == "fault":
        return {
            'temperature':   round(np.random.normal(98, 5), 2),
            'vibration':     round(np.random.normal(2.0, 0.3), 3),
            'pressure':      round(np.random.normal(135, 10), 2),
            'current':       round(np.random.normal(23, 2), 2),
            'rpm':           round(np.random.normal(2500, 150), 1),
            'oil_viscosity': round(np.random.normal(37, 3), 2),
        }
    else:  # gradual
        return {
            'temperature':   round(70  + progress * 28  + np.random.normal(0, 2), 2),
            'vibration':     round(0.5 + progress * 1.5 + np.random.normal(0, 0.05), 3),
            'pressure':      round(100 + progress * 35  + np.random.normal(0, 4), 2),
            'current':       round(15  + progress * 8   + np.random.normal(0, 0.8), 2),
            'rpm':           round(3000 - progress * 500 + np.random.normal(0, 60), 1),
            'oil_viscosity': round(46  - progress * 9   + np.random.normal(0, 1), 2),
        }

def get_risk(reading):
    if model is None:
        return np.random.uniform(0, 1)
    features = ['temperature','vibration','pressure','current','rpm','oil_viscosity']
    df = pd.DataFrame([reading])[features]
    scaled = scaler.transform(df)
    return model.predict_proba(scaled)[0][1]

# ─────────────────────────────────────────────
# Session State
# ─────────────────────────────────────────────

if 'history' not in st.session_state:
    st.session_state.history = []
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'running' not in st.session_state:
    st.session_state.running = False

# ─────────────────────────────────────────────
# أزرار التحكم
# ─────────────────────────────────────────────

col1, col2, col3 = st.columns([1, 1, 4])

with col1:
    if st.button("▶️ تشغيل", use_container_width=True):
        st.session_state.running = True

with col2:
    if st.button("⏹️ إيقاف", use_container_width=True):
        st.session_state.running = False
        st.session_state.history = []
        st.session_state.step = 0

# ─────────────────────────────────────────────
# Dashboard الرئيسي
# ─────────────────────────────────────────────

placeholder = st.empty()

if st.session_state.running:
    while st.session_state.running:
        st.session_state.step += 1
        reading = generate_reading(mode, st.session_state.step)
        risk = get_risk(reading)
        reading['risk'] = risk
        reading['time'] = datetime.now().strftime("%H:%M:%S")
        st.session_state.history.append(reading)

        # نحافظو على آخر n_points قراءة فقط
        history = st.session_state.history[-n_points:]
        df = pd.DataFrame(history)

        with placeholder.container():

            # ── KPIs ──
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("🌡️ الحرارة",   f"{reading['temperature']}°C",
                      delta=f"{reading['temperature']-70:.1f}")
            k2.metric("📳 الاهتزاز",  f"{reading['vibration']} mm/s",
                      delta=f"{reading['vibration']-0.5:.3f}")
            k3.metric("⚡ التيار",    f"{reading['current']} A",
                      delta=f"{reading['current']-15:.1f}")
            k4.metric("🔄 RPM",       f"{reading['rpm']:.0f}",
                      delta=f"{reading['rpm']-3000:.0f}")

            st.divider()

            # ── مؤشر الخطر ──
            risk_pct = risk * 100
            if risk_pct < warn_threshold:
                color = "green"
                status = "✅ المعدة سليمة"
            elif risk_pct < alert_threshold:
                color = "orange"
                status = "⚠️ تحذير — راقب المعدة"
            else:
                color = "red"
                status = "🚨 خطر عطل — توقف فوري!"

            st.markdown(f"### {status}")

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_pct,
                number={'suffix': '%', 'font': {'size': 40}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, warn_threshold],  'color': '#e8f5e9'},
                        {'range': [warn_threshold, alert_threshold], 'color': '#fff3e0'},
                        {'range': [alert_threshold, 100], 'color': '#ffebee'},
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 3},
                        'thickness': 0.75,
                        'value': alert_threshold
                    }
                },
                title={'text': "احتمال العطل", 'font': {'size': 20}}
            ))
            fig_gauge.update_layout(height=250, margin=dict(t=40, b=0))
            st.plotly_chart(fig_gauge, use_container_width=True)

            st.divider()

            # ── الرسوم البيانية ──
            c1, c2 = st.columns(2)

            with c1:
                fig1 = px.line(df, x='time', y='temperature',
                               title="🌡️ درجة الحرارة",
                               color_discrete_sequence=['#ef5350'])
                fig1.update_layout(height=220, margin=dict(t=40,b=20))
                st.plotly_chart(fig1, use_container_width=True)

                fig2 = px.line(df, x='time', y='pressure',
                               title="💨 الضغط",
                               color_discrete_sequence=['#42a5f5'])
                fig2.update_layout(height=220, margin=dict(t=40,b=20))
                st.plotly_chart(fig2, use_container_width=True)

            with c2:
                fig3 = px.line(df, x='time', y='vibration',
                               title="📳 الاهتزاز",
                               color_discrete_sequence=['#ab47bc'])
                fig3.update_layout(height=220, margin=dict(t=40,b=20))
                st.plotly_chart(fig3, use_container_width=True)

                fig4 = px.line(df, x='time', y='risk',
                               title="⚠️ احتمال العطل",
                               color_discrete_sequence=['#ff7043'])
                fig4.add_hline(y=alert_threshold/100, line_dash="dash",
                               line_color="red", annotation_text="حد الخطر")
                fig4.update_layout(height=220, margin=dict(t=40,b=20))
                st.plotly_chart(fig4, use_container_width=True)

            # ── آخر القراءات ──
            st.divider()
            st.markdown("**آخر القراءات:**")
            display_df = df[['time','temperature','vibration','pressure','current','rpm']].tail(8)
            display_df.columns = ['الوقت','الحرارة°C','الاهتزاز','الضغط','التيار A','RPM']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        time.sleep(speed)

else:
    st.info("👆 اضغط **تشغيل** باش تبدا المراقبة")
    st.markdown("""
    **شنو كيدير هاد الداشبورد:**
    - 📡 كيقرا بيانات الحساسات كل ثانية
    - 🤖 كيمر البيانات على النموذج ديال ML
    - 📊 كيرسم الرسوم البيانية في الوقت الحقيقي
    - 🚨 كيطلع تنبيه لو احتمال العطل على الحد
    """)
