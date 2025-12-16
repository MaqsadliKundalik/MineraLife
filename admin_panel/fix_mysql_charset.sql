-- MySQL bazasini utf8mb4 ga o'zgartirish

-- PythonAnywhere Bash Console'da MySQL ga kirish:
-- mysql -u mineralife -p -h mineralife.mysql.pythonanywhere-services.com

-- Parolni kiriting: wwwMiner123

-- Keyin quyidagi buyruqlarni bajaring:

USE mineralife$default;

-- Barcha jadvallarni utf8mb4 ga o'zgartirish
ALTER DATABASE `mineralife$default` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Clients jadvali
ALTER TABLE clients_client CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Orders jadvali
ALTER TABLE orders_order CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Products jadvali
ALTER TABLE products_product CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Couriers jadvali (agar mavjud bo'lsa)
ALTER TABLE couriers_courier CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ClientPhoneNumber jadvali
ALTER TABLE clients_clientphonenumber CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Barcha jadvallarni ko'rish
SHOW TABLES;

-- Jadval charset'ini tekshirish
SHOW CREATE TABLE clients_client;

-- Chiqish
exit;
