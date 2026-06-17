# 🤖 AI Clinical Scribe - Trợ lý Tạo SOAP Note Y Khoa Tự Động

> **AI Clinical Scribe** là trợ lý trí tuệ nhân tạo thông minh dành cho bác sĩ. Ứng dụng nhận file âm thanh cuộc đối thoại khám bệnh giữa bác sĩ và bệnh nhân, tự động chuyển đổi thành văn bản tiếng Việt chính xác cao, hiệu chỉnh lỗi chính tả y khoa, và cấu trúc thành SOAP Note chuẩn y học.

---

## 🎯 Tính năng chính

- **Nhận dạng giọng nói (ASR):** Sử dụng mô hình `vinai/PhoWhisper-small` tối ưu riêng cho tiếng Việt để chuyển giọng nói y khoa thành văn bản.
- **Hiệu đính chính tả y tế:** Dùng Gemini 2.0 Flash thông qua SDK mới `google-genai` để sửa lỗi phát âm, dấu câu, và chuẩn hóa các danh từ riêng/thuật ngữ tiếng Anh chuyên ngành mà không dịch nghĩa.
- **Tự động hóa SOAP Note:** Trích xuất thông tin lâm sàng từ transcript thành 4 phần chuẩn: **Subjective** (Chủ quan), **Objective** (Khách quan), **Assessment** (Đánh giá), và **Plan** (Kế hoạch).
- **Hệ thống API đầy đủ:** Hỗ trợ Đăng ký, Đăng nhập (JWT auth) và tra cứu lịch sử hồ sơ bệnh án.
- **Tích hợp MCP (Model Context Protocol):** Đóng gói và tách biệt các tác vụ AI/ASR nặng thành một MCP Server riêng biệt.

---

## 🛠 Tech Stack

- **AI Agent Workflow:** LangGraph
- **LLM Engine:** Google Gemini 2.0 Flash (sử dụng SDK `google-genai`)
- **ASR Engine:** HuggingFace Transformers (`vinai/PhoWhisper-small`)
- **API Backend:** FastAPI, Uvicorn, Pydantic v2
- **Database Layer:** SQLite (Development) / PostgreSQL (Production) + SQLAlchemy ORM

---

## 📋 Yêu cầu hệ thống & Biến môi trường

Ứng dụng đọc cấu hình từ file `.env`. Hãy tạo file `.env` từ file mẫu `.env.example`:

```bash
cp .env.example .env
```

Các biến môi trường cần thiết cấu hình trong `.env`:

| Biến môi trường | Loại | Giá trị mặc định / Ví dụ | Mô tả |
| :--- | :--- | :--- | :--- |
| **`GOOGLE_API_KEY`** | Bắt buộc | `AIzaSy...` | API Key của Google Gemini dùng để hiệu đính và tạo SOAP note. |
| **`GEMINI_MODEL_NAME`** | Tùy chọn | `gemini-2.0-flash` | Model Gemini được sử dụng bởi hệ thống. |
| **`LLM_PROVIDER`** | Tùy chọn | `gemini` | Chọn `gemini` hoặc `openai`. |
| **`DATABASE_URL`** | Tùy chọn | `sqlite:///./data/app.db` | Đường dẫn kết nối Database. Mặc định dùng SQLite cục bộ. |
| **`APP_HOST`** | Tùy chọn | `0.0.0.0` | IP Host để lắng nghe các kết nối đến. |
| **`APP_PORT`** | Tùy chọn | `8000` | Port chạy ứng dụng FastAPI Backend. |
| **`LOG_LEVEL`** | Tùy chọn | `INFO` | Mức độ ghi nhận log hệ thống (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| **`AI_LOG_API_KEY`** | Bắt buộc | Key được BTC cấp | Mã API Key để gửi nhật ký sử dụng AI (Grading Server AI20K). |

---

## 🚀 Hướng dẫn cài đặt & Chạy ứng dụng

### Bước 1: Clone dự án và di chuyển vào thư mục
```bash
git clone https://github.com/AI20K-Build-Cohort-2/C2-App-121.git
cd C2-App-121
```

### Bước 2: Khởi tạo và kích hoạt môi trường ảo (Virtual Env)
- **Trên Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
- **Trên Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Bước 3: Cài đặt các gói thư viện phụ thuộc
```bash
pip install -e ".[dev]"
```

### Bước 4: Thiết lập AI Hooks Logging (Bắt buộc cho AI20K Cohort 2)
Cài đặt pre-push hook để tự động nộp log tương tác AI:
- **Trên Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts/setup_hooks.ps1
  ```
- **Trên Linux / macOS / Git Bash:**
  ```bash
  bash scripts/setup_hooks.sh
  ```

### Bước 5: Khởi chạy MCP Clinical Server (Cổng 8001)
Chạy server phụ trách công cụ AI (Chuyển giọng nói & xử lý ngôn ngữ y tế):
```bash
python src/agents/mcp/server.py
```

### Bước 6: Khởi chạy FastAPI Backend (Cổng 8000)
Mở một terminal mới (nhớ kích hoạt `.venv` trước) và chạy:
```bash
uvicorn src.main:app --reload --port 8000
```
Sau khi chạy thành công, giao diện tài liệu API tự động (Swagger UI) sẽ mở tại: [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🧪 Các câu lệnh mẫu để chạy thử (Sample Queries)

Bạn có thể chạy thử trực tiếp qua giao diện Swagger UI hoặc dùng công cụ terminal (`curl` hoặc `PowerShell`).

Dưới đây là kịch bản chạy thử từ lúc **Đăng ký tài khoản** đến **Tạo SOAP Note từ file ghi âm**:

### 1. Đăng ký tài khoản Bác sĩ mới (Register)

- **Sử dụng `curl` (Linux/Git Bash):**
  ```bash
  curl -X POST "http://localhost:8000/api/v1/auth/register" \
       -H "Content-Type: application/json" \
       -d '{
         "email": "doctor.test@example.com",
         "password": "SecurePassword123",
         "full_name": "Nguyễn Văn A"
       }'
  ```

- **Sử dụng `PowerShell` (Windows):**
  ```powershell
  $body = @{
      email = "doctor.test@example.com"
      password = "SecurePassword123"
      full_name = "Nguyễn Văn A"
  } | ConvertTo-Json
  Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method Post -Body $body -ContentType "application/json"
  ```

*Kết quả trả về sẽ có dạng:*
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```
> **Lưu ý:** Hãy sao chép chuỗi `access_token` để điền vào phần `<YOUR_ACCESS_TOKEN>` trong các câu lệnh tiếp theo.

---

### 2. Đăng nhập để lấy Token (Login)

Nếu đã có tài khoản, sử dụng endpoint này để nhận Access Token mới:

- **Sử dụng `curl`:**
  ```bash
  curl -X POST "http://localhost:8000/api/v1/auth/login" \
       -H "Content-Type: application/json" \
       -d '{
         "email": "doctor.test@example.com",
         "password": "SecurePassword123"
       }'
  ```

- **Sử dụng `PowerShell`:**
  ```powershell
  $body = @{
      email = "doctor.test@example.com"
      password = "SecurePassword123"
  } | ConvertTo-Json
  Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $body -ContentType "application/json"
  ```

---

### 3. Gửi file âm thanh khám bệnh để tạo SOAP Note

Gửi file âm thanh hội thoại lâm sàng (`.mp3`, `.wav`, `.m4a`, `.ogg`, v.v.) qua request `multipart/form-data`. Yêu cầu truyền kèm token xác thực Bearer trong Header.

- **Sử dụng `curl`:**
  *(Hãy chuẩn bị một file âm thanh ví dụ như `audio_record.wav` ở thư mục hiện hành)*
  ```bash
  curl -X POST "http://localhost:8000/api/v1/clinical/soap-note" \
       -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
       -F "file=@audio_record.wav"
  ```

- **Sử dụng `PowerShell`:**
  ```powershell
  $headers = @{
      Authorization = "Bearer <YOUR_ACCESS_TOKEN>"
  }
  $filePath = "audio_record.wav"
  Invoke-RestMethod -Uri "http://localhost:8000/api/v1/clinical/soap-note" -Method Post -Headers $headers -Form @{ file = Get-Item $filePath }
  ```

*Kết quả trả về mẫu:*
```json
{
  "transcript": "bệnh nhân nam 45 tuổi khai đau ngực trái âm ỉ hai ngày nay...",
  "corrected_transcript": "Bệnh nhân nam, 45 tuổi, khai đau ngực trái âm ỉ hai ngày nay...",
  "soap_note": "# S - Subjective\n- Bệnh nhân nam 45 tuổi, phàn nàn đau ngực trái âm ỉ 2 ngày nay.\n\n# O - Objective\n- Chưa ghi nhận chỉ số khám thực thể.\n\n# A - Assessment\n- Đau ngực trái chưa rõ nguyên nhân.\n\n# P - Plan\n- Đề nghị đo điện tâm đồ (ECG) và siêu âm tim."
}
```

---

### 4. Truy vấn lịch sử SOAP Note của bạn (History)

- **Sử dụng `curl`:**
  ```bash
  curl -X GET "http://localhost:8000/api/v1/clinical/history?skip=0&limit=10" \
       -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
  ```

- **Sử dụng `PowerShell`:**
  ```powershell
  $headers = @{
      Authorization = "Bearer <YOUR_ACCESS_TOKEN>"
  }
  Invoke-RestMethod -Uri "http://localhost:8000/api/v1/clinical/history?skip=0&limit=10" -Method Get -Headers $headers
  ```

---

## 📁 Cấu trúc Dự Án chính

- `src/agents/` — Chứa định nghĩa đồ thị LangGraph Agent (`graph.py`, `state.py`, các node xử lý).
- `src/agents/mcp/` — Client và Server của Model Context Protocol.
- `src/api/` — Chứa định nghĩa các endpoints FastAPI y tế và xác thực người dùng.
- `src/models/` — Pydantic schemas và SQLAlchemy models của Database.
- `src/services/` — Kết nối các SDK bên ngoài (Gemini client, local storage).
- `tests/` — Bộ kiểm thử tự động pytest.

---

## 📄 License

Dự án phát triển dưới giấy phép MIT. Sử dụng tự do cho các mục đích học tập và phát triển lâm sàng phi lợi nhuận.
