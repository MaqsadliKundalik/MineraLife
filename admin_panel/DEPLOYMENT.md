# PythonAnywhere'da Django loyihasini deploy qilish yo'riqnomasi

## 1. PythonAnywhere'da Bash Console ochish
- Dashboard -> Consoles -> Bash

## 2. Loyihani klonlash (GitHub orqali)
```bash
cd ~
git clone https://github.com/your-username/MineraLife.git
cd MineraLife/admin_panel
```

Yoki zip fayl orqali yuklash:
- Files sahifasida Upload qiling va unzip qiling

## 3. Virtual environment yaratish
```bash
mkvirtualenv --python=/usr/bin/python3.10 mineralife-env
workon mineralife-env
```

## 4. Dependency'larni o'rnatish
```bash
cd ~/MineraLife/admin_panel
pip install -r requirements.txt
```

## 5. .env faylini sozlash
```bash
cd ~/MineraLife/admin_panel
nano .env
```

.env.production faylidan nusxalab, quyidagi qiymatlarni kiriting:
```
USE_MYSQL=true
MYSQL_HOST=mineralife.mysql.pythonanywhere-services.com
MYSQL_PORT=3306
MYSQL_USER=mineralife
MYSQL_PASSWORD=wwwMiner123
MYSQL_DBNAME=mineralife$default
DEBUG=False
SECRET_KEY=yangi-secret-key-yarating
ALLOWED_HOSTS=mineralife.pythonanywhere.com
YANDEX_MAPS_API_KEY=551c0bcb-107f-46e8-a984-fa0de3388168
```

SECRET_KEY yaratish:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 6. MySQL bazasini utf8mb4 ga o'zgartirish (emoji uchun)
```bash
mysql -u mineralife -p -h mineralife.mysql.pythonanywhere-services.com
# Parol: wwwMiner123
```

MySQL consoleda:
```sql
USE mineralife$default;
ALTER DATABASE `mineralife$default` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE clients_client CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE orders_order CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE products_product CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE clients_clientphonenumber CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

## 7. Migrationlarni bajarish
```bash
cd ~/MineraLife/admin_panel
python manage.py migrate
```

## 7. Static fayllarni to'plash
```bash
python manage.py collectstatic --noinput
```

## 8. Superuser yaratish
```bash
python manage.py createsuperuser
```

## 9. Web App sozlash
Dashboard -> Web -> Add a new web app

**Manual configuration** tanlang:
- Python version: Python 3.10
- Path to virtualenv: /home/mineralife/.virtualenvs/mineralife-env

**WSGI configuration file:**
- Click on WSGI configuration file link
- Barcha kodni o'chiring va quyidagini kiriting:

```python
import os
import sys

# Loyiha yo'lini qo'shish
project_home = '/home/mineralife/MineraLife/admin_panel'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'admin_panel.settings'

# WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 10. Static va Media files sozlash
Web tab'da:

**Static files:**
- URL: `/static/`
- Directory: `/home/mineralife/MineraLife/admin_panel/static/`

**Media files:**
- URL: `/media/`
- Directory: `/home/mineralife/MineraLife/admin_panel/media/`

## 11. Reload web app
Web tab'da "Reload" tugmasini bosing

## 12. Saytni tekshirish
https://mineralife.pythonanywhere.com

---

## Xatolarni ko'rish:
- Web tab -> Log files -> Error log
- Server log

## settings.py'ga qo'shimcha sozlamalar kerak bo'lishi mumkin:

```python
# Static files collection
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# CSRF trusted origins for forms
CSRF_TRUSTED_ORIGINS = [
    'https://mineralife.pythonanywhere.com',
]
```

## Kod yangilanganida:
```bash
workon mineralife-env
cd ~/MineraLife/admin_panel
git pull  # Agar git ishlatgan bo'lsangiz
python manage.py migrate  # Agar yangi migrationlar bo'lsa
python manage.py collectstatic --noinput  # Agar static fayllar o'zgargan bo'lsa
```

Keyin Web tab'da "Reload" tugmasini bosing.
