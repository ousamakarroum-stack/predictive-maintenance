# 🔧 Predictive Maintenance Automation

نظام ذكي للكشف المبكر عن أعطاب المعدات باستخدام الذكاء الاصطناعي.

## 🎯 المشكلة التي يحلها
- الآلات كتعطل بدون سابق إنذار → خسارة في الوقت والمال
- صعب تتبع حالة المعدات بشكل لحظي

## 🏗️ معمارية المشروع

```
حساسات IoT → معالجة البيانات → نموذج ML → تنبيهات فورية
```

## 📁 هيكل المشروع

```
predictive-maintenance/
│
├── data/
│   ├── raw/              ← البيانات الخام من الحساسات
│   └── processed/        ← البيانات بعد التنظيف
│
├── src/
│   ├── sensors/          ← كود الحساسات وIoT
│   ├── ml/               ← نماذج الذكاء الاصطناعي
│   ├── dashboard/        ← واجهة المستخدم (Streamlit)
│   └── alerts/           ← نظام التنبيهات
│
├── models/               ← النماذج المحفوظة (.pkl)
├── notebooks/            ← Jupyter notebooks للتجارب
├── tests/                ← اختبارات الكود
└── docs/                 ← التوثيق
```

## 🚀 كيفية التشغيل

```bash
# 1. تنصيب المكتبات
pip install -r requirements.txt

# 2. تشغيل النموذج
python src/ml/train_model.py

# 3. تشغيل الداشبورد
streamlit run src/dashboard/app.py
```

## 🛠️ التقنيات المستخدمة

| الطبقة | التقنية |
|--------|---------|
| الحساسات | ESP32 + Python simulation |
| البروتوكول | MQTT |
| ML | Scikit-learn / Random Forest |
| Dashboard | Streamlit |
| قاعدة البيانات | TimescaleDB / SQLite |
| التنبيهات | Email / SMS |

## 📊 نتائج النموذج

- **الدقة:** 100% على بيانات الاختبار
- **الحساسات:** درجة الحرارة، الاهتزاز، الضغط، التيار، RPM، الزيت
- **أهم ميزة:** الاهتزاز (39%)

## 📅 خارطة الطريق

- [x] نموذج ML الأساسي (Random Forest)
- [ ] ESP32 Sensor Simulation
- [ ] MQTT Integration
- [ ] Streamlit Dashboard
- [ ] نظام التنبيهات
- [ ] نموذج LSTM (Deep Learning)
- [ ] Cloud Deployment

## 👤 المطور

Made with ❤️ — Predictive Maintenance Project
