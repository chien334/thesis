# FastAPI with Gemini AI and Image Detection

## Cài đặt

1. Đảm bảo bạn đã cài đặt Python 3.8 trở lên
2. Chạy file `install.cmd` để cài đặt môi trường ảo và các dependencies:
```bash
install.cmd
```

## Cấu hình

1. Tạo file `.env` trong thư mục gốc với nội dung sau:
```
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///thesis.db
PORT=8000
GEMINI_API_KEY=your-gemini-api-key-here
```

2. Thay thế các giá trị trong file `.env` với các giá trị thực tế của bạn

## Chạy ứng dụng

Chạy file `run.cmd` để khởi động server:
```bash
run.cmd
```

Server sẽ chạy tại `http://localhost:8000`

## API Documentation

Bạn có thể truy cập tài liệu API tại:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- POST `/api/users/register` - Đăng ký người dùng mới
- POST `/api/users/token` - Đăng nhập và lấy token

### User Management
- GET `/api/users/me` - Lấy thông tin người dùng hiện tại
- GET `/api/users/admin/list` - Danh sách người dùng (admin only)
- PUT `/api/users/admin/<user_id>` - Cập nhật thông tin người dùng (admin only)
- DELETE `/api/users/admin/<user_id>` - Xóa người dùng (admin only)

### Chat Management
- POST `/api/chats` - Tạo cuộc trò chuyện mới
- GET `/api/chats` - Lấy danh sách các cuộc trò chuyện
- GET `/api/chats/<chat_id>` - Lấy thông tin chi tiết của một cuộc trò chuyện
- POST `/api/chats/<chat_id>/messages` - Thêm tin nhắn mới vào cuộc trò chuyện
- PUT `/api/chats/<chat_id>` - Cập nhật thông tin cuộc trò chuyện
- DELETE `/api/chats/<chat_id>` - Xóa cuộc trò chuyện

### Image Detection
- GET `/api/detection/history` - Lấy lịch sử phát hiện hình ảnh
- POST `/api/detection/detect` - Phát hiện đối tượng trong hình ảnh
- GET `/api/detection/history/<history_id>` - Lấy chi tiết một lần phát hiện
- DELETE `/api/detection/history/<history_id>` - Xóa một lần phát hiện khỏi lịch sử

## Lưu ý
- Tất cả các API endpoints (trừ đăng ký và đăng nhập) đều yêu cầu JWT token trong header:
```
Authorization: Bearer <your-token>
```
- Đảm bảo thư mục `uploads` tồn tại để lưu trữ hình ảnh
- Kiểm tra logs trong console để debug nếu có lỗi 