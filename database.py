import os
import pandas as pd
from supabase import create_client, Client

# البيانات الخاصة بمشروعك
URL = "https://zhfyxolklugpiemhrlpz.supabase.co"
KEY = "sb_publishable_1B5zvn8xjA-H6wPDsuydcg_X-uG0dTj"

print("جاري الاتصال بقاعدة البيانات...")
supabase: Client = create_client(URL, KEY)

def save_score(student_name: str, score: int, subject: str = "General"):
    try:
        data = {
            "Student_Name": student_name,
            "Score": score,
            "Subject": subject
        }
        response = supabase.table("Students Scores").insert(data).execute()
        return True, "تم حفظ النتيجة بنجاح!"
    except Exception as e:
        return False, f"خطأ في الحفظ: {str(e)}"

def get_leaderboard(limit: int = 10):
    try:
        response = (
            supabase.table("Students Scores")
            .select("Student_Name, Score, Subject")
            .order("Score", desc=True)
            .limit(limit)
            .execute()
        )
        df = pd.DataFrame(response.data)
        if not df.empty:
            df.columns = ["اسم الطالب", "النقاط", "المادة"]
        return df
    except Exception as e:
        print(f"خطأ في الجلب: {e}")
        return pd.DataFrame()

# === تجربة الكود عند التشغيل ===
if __name__ == "__main__":
    print("1. جاري تجربة إرسال نتيجة جديدة...")
    status, msg = save_score("محمد صالح", 100, "Cybersecurity")
    print("النتيجة:", msg)

    print("\n2. جاري جلب لوحة الأوائل من السحابة...")
    df = get_leaderboard()
    print(df)