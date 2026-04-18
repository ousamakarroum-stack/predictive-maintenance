"""
Predictive Maintenance — ML Model (مرحلة أولى)
================================================
1. توليد بيانات مسيملة (حساسات)
2. تدريب Random Forest
3. تقييم النموذج
4. حفظ النموذج للاستخدام لاحقاً
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# 1. توليد البيانات المسيملة
# ─────────────────────────────────────────────

np.random.seed(42)
N_SAMPLES = 5000  # عدد القراءات

def simulate_sensor_data(n=N_SAMPLES):
    """
    نسيميليو بيانات حساسات لمعدة صناعية.
    كل صف = قراءة واحدة في لحظة معينة.
    """

    # ---- معدات سليمة (80% من البيانات) ----
    n_normal = int(n * 0.80)
    normal = pd.DataFrame({
        'temperature':    np.random.normal(70, 5, n_normal),   # درجة حرارة طبيعية ~70°C
        'vibration':      np.random.normal(0.5, 0.1, n_normal),# اهتزاز طبيعي ~0.5 mm/s
        'pressure':       np.random.normal(100, 8, n_normal),  # ضغط طبيعي ~100 bar
        'current':        np.random.normal(15, 1.5, n_normal), # تيار كهربائي ~15A
        'rpm':            np.random.normal(3000, 100, n_normal),# سرعة دوران ~3000 rpm
        'oil_viscosity':  np.random.normal(46, 3, n_normal),   # لزوجة الزيت
        'label': 0  # 0 = سليم
    })

    # ---- معدات على وشك العطل (20% من البيانات) ----
    n_fault = n - n_normal
    fault = pd.DataFrame({
        'temperature':    np.random.normal(95, 10, n_fault),   # حرارة مرتفعة ⚠️
        'vibration':      np.random.normal(1.8, 0.4, n_fault), # اهتزاز قوي ⚠️
        'pressure':       np.random.normal(130, 15, n_fault),  # ضغط زائد ⚠️
        'current':        np.random.normal(22, 3, n_fault),    # تيار مرتفع ⚠️
        'rpm':            np.random.normal(2600, 200, n_fault),# سرعة غير منتظمة ⚠️
        'oil_viscosity':  np.random.normal(38, 5, n_fault),    # زيت متدهور ⚠️
        'label': 1  # 1 = خطر عطل
    })

    df = pd.concat([normal, fault], ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # خلط البيانات
    return df


# ─────────────────────────────────────────────
# 2. تحضير البيانات
# ─────────────────────────────────────────────

print("=" * 55)
print("  Predictive Maintenance — ML Pipeline")
print("=" * 55)

df = simulate_sensor_data()
print(f"\n✅ البيانات جاهزة: {len(df)} قراءة")
print(f"   سليم:     {(df['label']==0).sum()} ({(df['label']==0).mean()*100:.0f}%)")
print(f"   خطر عطل: {(df['label']==1).sum()} ({(df['label']==1).mean()*100:.0f}%)")

# الميزات والهدف
FEATURES = ['temperature', 'vibration', 'pressure', 'current', 'rpm', 'oil_viscosity']
X = df[FEATURES]
y = df['label']

# تقسيم البيانات
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# تطبيع البيانات
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

print(f"\n📊 تقسيم البيانات:")
print(f"   تدريب: {len(X_train)} قراءة")
print(f"   اختبار: {len(X_test)} قراءة")


# ─────────────────────────────────────────────
# 3. تدريب النموذج
# ─────────────────────────────────────────────

print("\n🤖 جاري تدريب النموذج...")

model = RandomForestClassifier(
    n_estimators=100,    # عدد الأشجار
    max_depth=10,        # عمق كل شجرة
    random_state=42,
    n_jobs=-1            # استخدام كل المعالجات
)

model.fit(X_train_scaled, y_train)
print("✅ تم التدريب بنجاح!")


# ─────────────────────────────────────────────
# 4. تقييم النموذج
# ─────────────────────────────────────────────

y_pred = model.predict(X_test_scaled)
y_proba = model.predict_proba(X_test_scaled)[:, 1]

print("\n" + "=" * 55)
print("  نتائج التقييم")
print("=" * 55)
print(classification_report(y_test, y_pred,
      target_names=['سليم', 'خطر عطل'], digits=3))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(f"  TP={cm[1,1]}  FP={cm[0,1]}")
print(f"  FN={cm[1,0]}  TN={cm[0,0]}")


# ─────────────────────────────────────────────
# 5. أهمية الميزات
# ─────────────────────────────────────────────

importance = pd.Series(model.feature_importances_, index=FEATURES)
importance = importance.sort_values(ascending=False)

print("\n📌 أهمية كل حساس في القرار:")
for feat, imp in importance.items():
    bar = "█" * int(imp * 40)
    print(f"  {feat:<15} {bar} {imp:.3f}")


# ─────────────────────────────────────────────
# 6. اختبار على قراءة جديدة (Inference)
# ─────────────────────────────────────────────

print("\n" + "=" * 55)
print("  اختبار على قراءة حقيقية جديدة")
print("=" * 55)

new_reading = pd.DataFrame([{
    'temperature': 98.0,   # حرارة مرتفعة
    'vibration':   2.1,    # اهتزاز قوي
    'pressure':    135.0,  # ضغط زائد
    'current':     23.5,   # تيار مرتفع
    'rpm':         2550.0, # سرعة منخفضة
    'oil_viscosity': 37.0  # زيت متدهور
}])

new_scaled = scaler.transform(new_reading)
pred = model.predict(new_scaled)[0]
prob = model.predict_proba(new_scaled)[0][1]

print(f"\n  درجة الحرارة:  {new_reading['temperature'].values[0]}°C")
print(f"  الاهتزاز:      {new_reading['vibration'].values[0]} mm/s")
print(f"  الضغط:         {new_reading['pressure'].values[0]} bar")
print(f"\n  ➤ التشخيص:    {'⚠️  خطر عطل!' if pred == 1 else '✅ المعدة سليمة'}")
print(f"  ➤ احتمال العطل: {prob*100:.1f}%")

if prob > 0.8:
    print("\n  🔴 تنبيه عاجل: يجب إجراء صيانة فورية!")
elif prob > 0.5:
    print("\n  🟡 تحذير: جدول صيانة في أقرب وقت.")
else:
    print("\n  🟢 المعدة في حالة جيدة.")


# ─────────────────────────────────────────────
# 7. حفظ النموذج
# ─────────────────────────────────────────────

joblib.dump(model,  '/mnt/user-data/outputs/maintenance_model.pkl')
joblib.dump(scaler, '/mnt/user-data/outputs/maintenance_scaler.pkl')

print("\n" + "=" * 55)
print("  ✅ النموذج محفوظ!")
print("     maintenance_model.pkl")
print("     maintenance_scaler.pkl")
print("=" * 55)
print("\n  المرحلة التالية: Dashboard لحظي + تنبيهات SMS 🚀")
