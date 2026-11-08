# جزء المحتوى والأنيميشن (العضو الثاني - أمين)

نظام مواد متعددة: كل **مادة** مجلد، وكل **ملزمة** ملف JSON داخلها. الصور تُولَّد تلقائياً.

## التشغيل

```bash
pip install -r requirements.txt
streamlit run app.py
```

(`app.py` هنا نسخة تجريبية لاختبار جزئك. صفحة العضو الأول تحتاج فقط 3 أسطر، انظر آخر الملف.)

## هيكل المشروع

```
content/
  python_security/            <- مادة
    subject.json              <- اسم المادة وأيقونتها
    lec1_intro_python.json    <- ملزمة
    lec2_security_automation.json
    lec3_python_libraries.json
  _template/                  <- المجلدات التي تبدأ بـ _ يتجاهلها الموقع
sources/python_security/      <- ملفات الـ PDF الأصلية (للرجوع فقط)
assets/animations/...         <- الصور المولَّدة (تلقائي، لا تعدّلها يدوياً)
content_manager/              <- الكود (loader / renderer / viewer / validate)
manage.py                     <- أوامر الإدارة
```

## إضافة ملزمة جديدة لمادة موجودة

```bash
python manage.py new-lecture python_security lec4_my_topic --title "المحاضرة 4: ..." --title-en "Lecture 4: ..."
```

يُنشئ ملف JSON فيه مشهدين نموذجيين. عدّله، ثم:

```bash
python manage.py validate   # يتأكد من الملف ويتحقق أن الناتج المكتوب هو ناتج الكود الحقيقي
python manage.py build      # (اختياري) يولّد الصور الآن
```

لا حاجة لتعديل أي كود: الملزمة تظهر في القائمة الجانبية تلقائياً، وإذا غيّرت ملف JSON تُعاد الصور تلقائياً.
تقدر أيضاً ترفع الملزمة الجديدة (PDF) لـ Claude ويحوّلها لملف JSON بنفس الصيغة.

## إضافة مادة جديدة

```bash
python manage.py new-subject networking --title "الشبكات" --title-en "Networking" --icon "🌐" --order 2
python manage.py new-lecture networking lec1_basics --title "..." --title-en "..."
```

استخدم في الـ id أحرفاً إنجليزية صغيرة وأرقاماً و `_` فقط.

## صيغة ملف الملزمة

```json
{
  "title": "عنوان الملزمة (عربي، يظهر في الموقع)",
  "title_en": "English title (يظهر داخل الصور)",
  "order": 1,
  "summary": "وصف قصير",
  "scenes": [ ... ]
}
```

كل مشهد له `title` (إنجليزي، يظهر في الصورة) و `text` (شرح عربي قصير يظهر تحت الصورة)، ونوع واحد من:

| النوع | الحقول | الناتج |
|---|---|---|
| قائمة نقاط | `"bullets": ["a", "b"]` | صورة واحدة |
| جدول | `"table": {"headers": [...], "rows": [[...]], "mono_cols": [0]}` | صورة واحدة |
| مخطط خطوات | `"flow": ["Step 1", "Step 2"]` و اختياري `"branches": [{"label":"Yes","text":"Alert","kind":"bad"}, {"label":"No","text":"Normal","kind":"good"}]` | صورة لكل خطوة |
| كود | `"code": "..."` و اختياري `"output": "..."` | إطاران: الكود، ثم الكود مع ناتجه |
| صورة جاهزة | `"image": "assets/custom/x.png"` | تستخدم صورتك بدل المولَّدة |

حقول اختيارية للكود: `"output_label"` (مثل "Possible output")، `"code_label"` (مثل "Terminal")،
`"error": true` (الناتج بالأحمر)، `"verify": true` (يتحقق `validate` أن الناتج صحيح بتشغيل الكود فعلاً؛ لا تستعمله مع input أو شبكة أو ملفات).

الكلام داخل الصور بالإنجليزية فقط (الكود والعناوين)، والعربي كله في `text`.

## ربط باقي الفريق

```python
from content_manager import loader
from content_manager.viewer import render_lesson_viewer

loader.list_subjects()                       # للقائمة الجانبية (العضو 1)
loader.list_lectures("python_security")      # ملازم المادة
render_lesson_viewer("python_security", "lec1_intro_python")   # عارض الأنيميشن

loader.get_lecture_data("python_security", "lec1_intro_python")
# {"title", "summary", "scenes": [{"title", "text", "images": [مسارات الصور]}]}
```

ملف الملزمة يقبل حقولاً إضافية (مثل `exercises` للعضو 3) ويتجاهلها العارض، فيمكن للجميع استعمال نفس الملف.
