# MovieX - Server

MovieX là hệ thống đặt vé xem phim trực tuyến, được xây dựng với mục tiêu cung cấp trải nghiệm đặt vé tiện lợi, nhanh chóng và an toàn cho người dùng.

## Tính năng chính

- Quản lý rạp chiếu phim, phòng chiếu, ghế ngồi
- Quản lý phim, lịch chiếu, suất chiếu
- Đặt vé và thanh toán
- Quản lý người dùng và phân quyền (Admin, Khách hàng)
- Tìm kiếm, lọc phim và suất chiếu
- API RESTful phục vụ cho frontend

## Công nghệ sử dụng

- **Backend framework**: Django
- **Cơ sở dữ liệu**: SQLite
- **Authentication**: JWT (JSON Web Token)
- **Quản lý dữ liệu**: Django Admin
- **API documentation**: Swagger

## Hướng dẫn chạy dự án

### 1. Clone repo

```bash
git clone https://github.com/limbanga/moviex-server.git
cd moviex-server
```

### 2. Cài đặt dependencies

```bash
# tạo virtualenv
python -m venv venv

# kích hoạt virtualenv
.\venv\Scripts\activate

# với linux
source venv/bin/activate
```

```bash
# cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### 3. Tạo file `.env`

```bash
cp .env.example .env
```

Điền cái config của bạn

### 4. Chạy server

```bash
.\run_dev.bat # window
# hoặc
.\run_dev.sh # linux
```

<!-- ### 5. (Tuỳ chọn) Dùng Docker

```bash
docker-compose up --build
``` -->

## Ghi chú

* Frontend của hệ thống được phát triển riêng ở repo `moviex-client`.

* Có thể mở rộng hệ thống với thanh toán qua cổng như Momo, ZaloPay,...



