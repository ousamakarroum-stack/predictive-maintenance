"""
ESP32 Sensor Simulation
=======================
كنسيميليو ESP32 كيبعت بيانات حساسات كل ثانية
النموذج كيقرأها ويعطي تشخيص فوري
"""

import numpy as np
import time
import joblib
import os
from datetime import datetime

# ─────────────────────────────────────────────
# تحميل النموذج
# ─────────────────────────────────────────────

MODEL_PATH  = "maintenance_model.pkl"
SCALER_PATH = "maintenance_scaler.pkl"

if os.path.exists(MODEL_PATH):
    model  = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("✅ النموذج محمل — جاهز للتشخيص\n")
else:
    model  = None
    scaler = None
    print("⚠️  النموذج مو موجود — كنشغلو بدون تشخيص\n")


# ─────────────────────────────────────────────
# كلاس الحساس المسيمل
# ─────────────────────────────────────────────

class ESP32Simulator:
    """
    كيسيميليو ESP32 مع 6 حساسات.
    mode = 'normal'  → معدة سليمة
    mode = 'fault'   → معدة على وشك العطل
    mode = 'gradual' → تدهور تدريجي (الأواقعي)
    """

    def __init__(self, mode='normal'):
        self.mode = mode
        self.step = 0  # عداد للتدهور التدريجي

    def read(self):
        self.step += 1
        t = self.step

        if self.mode == 'normal':
            return {
                'temperature':   round(np.random.normal(70, 3), 2),
                'vibration':     round(np.random.normal(0.5, 0.05), 3),
                'pressure':      round(np.random.normal(100, 5), 2),
                'current':       round(np.random.normal(15, 1), 2),
                'rpm':           round(np.random.normal(3000, 80), 1),
                'oil_viscosity': round(np.random.normal(46, 2), 2),
            }

        elif self.mode == 'fault':
            return {
                'temperature':   round(np.random.normal(98, 5), 2),
                'vibration':     round(np.random.normal(2.0, 0.3), 3),
                'pressure':      round(np.random.normal(135, 10), 2),
                'current':       round(np.random.normal(23, 2), 2),
                'rpm':           round(np.random.normal(2500, 150), 1),
                'oil_viscosity': round(np.random.normal(37, 3), 2),
            }

        elif self.mode == 'gradual':
            # تدهور تدريجي — الأواقعي بزاف
            progress = min(t / 30, 1.0)  # 30 قراءة للوصول للعطل
            return {
                'temperature':   round(70  + progress * 28  + np.random.normal(0, 2), 2),
                'vibration':     round(0.5 + progress * 1.5 + np.random.normal(0, 0.05), 3),
                'pressure':      round(100 + progress * 35  + np.random.normal(0, 4), 2),
                'current':       round(15  + progress * 8   + np.random.normal(0, 0.8), 2),
                'rpm':           round(3000 - progress * 500 + np.random.normal(0, 60), 1),
                'oil_viscosity': round(46  - progress * 9   + np.random.normal(0, 1), 2),
            }


# ─────────────────────────────────────────────
# دالة التشخيص
# ─────────────────────────────────────────────

def diagnose(reading):
    if model is None:
        return None, None

    import pandas as pd
    features = ['temperature','vibration','pressure','current','rpm','oil_viscosity']
    df = pd.DataFrame([reading])[features]
    scaled = scaler.transform(df)
    pred = model.predict(scaled)[0]
    prob = model.predict_proba(scaled)[0][1]
    return pred, prob


def status_icon(prob):
    if prob is None:   return "⚪"
    if prob < 0.3:     return "🟢"
    if prob < 0.6:     return "🟡"
    if prob < 0.85:    return "🟠"
    return "🔴"


def alert_message(prob):
    if prob is None:   return ""
    if prob < 0.3:     return "المعدة سليمة"
    if prob < 0.6:     return "تحذير — راقب المعدة"
    if prob < 0.85:    return "⚠️  جدول صيانة!"
    return "🚨 توقف فوري — خطر عطل!"


# ─────────────────────────────────────────────
# تشغيل الSimulation
# ─────────────────────────────────────────────

def run_simulation(mode='gradual', n_readings=20, interval=1.0):
    sensor = ESP32Simulator(mode=mode)

    print("=" * 60)
    print(f"  ESP32 Simulation — Mode: {mode.upper()}")
    print(f"  {n_readings} قراءة كل {interval} ثانية")
    print("=" * 60)
    print(f"{'الوقت':<10} {'🌡️ °C':<8} {'📳 mm/s':<9} {'⚡ A':<7} {'احتمال العطل':<15} {'الحالة'}")
    print("-" * 60)

    for i in range(n_readings):
        reading = sensor.read()
        pred, prob = diagnose(reading)

        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = status_icon(prob)
        alert = alert_message(prob)
        prob_str = f"{prob*100:.1f}%" if prob is not None else "N/A"

        print(
            f"{timestamp:<10} "
            f"{reading['temperature']:<8} "
            f"{reading['vibration']:<9} "
            f"{reading['current']:<7} "
            f"{prob_str:<15} "
            f"{icon} {alert}"
        )

        # تنبيه عاجل
        if prob is not None and prob >= 0.85:
            print("\n" + "🚨" * 20)
            print("  تنبيه عاجل! المعدة على وشك العطل!")
            print("  → أوقف المعدة وادعو فريق الصيانة")
            print("🚨" * 20 + "\n")

        time.sleep(interval)

    print("\n✅ انتهت الSimulation")


# ─────────────────────────────────────────────
# تشغيل
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("اختار النوع:")
    print("  1 → normal  (معدة سليمة)")
    print("  2 → fault   (معدة معطوبة)")
    print("  3 → gradual (تدهور تدريجي — الأواقعي)\n")

    choice = input("اختارك (1/2/3): ").strip()
    modes = {'1': 'normal', '2': 'fault', '3': 'gradual'}
    mode  = modes.get(choice, 'gradual')

    run_simulation(mode=mode, n_readings=20, interval=0.8)
