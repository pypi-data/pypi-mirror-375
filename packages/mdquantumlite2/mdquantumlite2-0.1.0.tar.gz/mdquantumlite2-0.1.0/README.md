# MDQuantumLite

A lightweight machine learning library for regression tasks, enhanced with optional quantum features using Pennylane. Based on LightGBM with GOSS sampling and target encoding.

## Installation
```bash
pip install mdquantumlite

MDQuantumLite/  # فولدر اصلی پروژه (می‌تونی این رو به MD_library تغییر بدی اگر بخشی از ریپو بزرگتر باشه)
├── mdquantumlite/  # فولدر پکیج (اینجا کد اصلی می‌ره)
│   ├── __init__.py  # برای ایمپورت: from mdquantumlite import MDQuantumLite
│   ├── mdquantum_lite.py  # کد اصلی کلاس‌ها (از APP1.PY منتقل شده، بدون تابع تست)
│   └── quantum_feature.py  # کلاس QuantumFeature رو جدا کردم برای تمیزتر شدن
├── tests/  # فولدر تست‌ها
│   └── test_mdquantum_lite.py  # تابع تست از APP1.PY
├── setup.py  # فایل نصب (مهم‌ترین فایل برای PyPI)
├── README.md  # توضیح پروژه
├── LICENSE  # لایسنس (مثلاً MIT)
├── MANIFEST.in  # برای شامل کردن فایل‌های غیرپایتون (اختیاری)
├── requirements.txt  # لیست dependencies برای توسعه (اختیاری، اما خوب است)
└── .gitignore  # برای نادیده گرفتن فایل‌های موقتی مثل __pycache__


from mdquantumlite import MDQuantumLite

model = MDQuantumLite(use_quantum_features=True)
model.fit(X, y)
predictions = model.predict(X_test)