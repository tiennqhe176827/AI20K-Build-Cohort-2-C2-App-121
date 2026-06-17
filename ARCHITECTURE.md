# Architecture Document — AI Clinical Scribe

## System Overview

**AI Clinical Scribe** là hệ thống trợ lý ghi chép y khoa tự động. Khi bác sĩ kết thúc buổi khám, hệ thống nhận file âm thanh cuộc hội thoại, tự động chuyển tiếng nói thành văn bản tiếng Việt, hiệu đính chính tả y khoa, và xuất ra SOAP Note chuẩn y tế — giúp bác sĩ tiết kiệm 15–30 phút ghi chép mỗi ca.

Kiến trúc gồm 2 tiến trình (process) phối hợp qua MCP Protocol:
- **FastAPI Backend (port 8000):** Tiếp nhận request, xác thực JWT, lưu kết quả vào DB.
- **FastMCP Server (port 8001):** Thực thi các tác vụ AI nặng (ASR + LLM) một cách độc lập.

## Architecture Diagram

```mermaid
graph TB
    subgraph Client ["🌐 Client"]
        Doctor["🩺 Bác sĩ"] --> FE["Frontend\n(React/Next.js)"]
    end

    subgraph Backend ["⚡ FastAPI Backend · Port 8000"]
        Auth["JWT Auth\nMiddleware"]
        API["POST /clinical/soap-note\nGET  /clinical/history"]
        DB[("SQLite / PostgreSQL\nusers · clinical_notes")]
    end

    subgraph Agent ["🧠 LangGraph Agent"]
        N1["transcribe_node"]
        N2["fix_spelling_node"]
        N3["soap_node"]
        State[("ClinicalState")]
    end

    subgraph MCP ["🔧 FastMCP Server · Port 8001"]
        T1["transcribe_audio\n→ PhoWhisper-small"]
        T2["fix_spelling\n→ Gemini 2.0 Flash"]
        T3["convert_to_soap_note\n→ Gemini 2.0 Flash"]
    end

    FE -->|"POST /api/v1/clinical/soap-note"| Auth
    Auth -->|"JWT hợp lệ"| API
    API -->|"ainvoke(audio_path)"| N1
    N1 --> N2 --> N3
    N1 & N2 & N3 <-->|"đọc/ghi"| State
    N1 -->|"Streamable HTTP"| T1
    N2 -->|"Streamable HTTP"| T2
    N3 -->|"Streamable HTTP"| T3
    API -->|"save_note()"| DB
    API -->|"SOAP Note JSON"| FE
```

## Components

### 1. Frontend (React/Next.js)
- **Purpose:** Giao diện upload file âm thanh và hiển thị SOAP Note cho bác sĩ.
- **State Management:** Local state (React hooks).

### 2. Backend (FastAPI)
- **Purpose:** REST API server, xử lý xác thực và điều phối luồng dữ liệu.
- **API Design:** RESTful — prefix `/api/v1`.
- **Authentication:** JWT (Access Token + Refresh Token), mật khẩu mã hóa bằng bcrypt.

### 3. AI Agent (LangGraph)
- **Agent Type:** Sequential Pipeline (không có vòng lặp, không có tool-calling agent).
- **State Schema:** `ClinicalState` — `TypedDict` với 5 trường: `audio_path`, `transcript`, `corrected_transcript`, `soap_note`, `error`.
- **Nodes:** `transcribe_node` → `fix_spelling_node` → `soap_node`.
- **Error Routing:** Conditional edges sau mỗi node — kết thúc ngay nếu có lỗi.
- **Tool Execution:** Không gọi tool trực tiếp mà ủy quyền cho **MCP Server** qua HTTP.

### 4. MCP Server (FastMCP)
- **Purpose:** Đóng gói các tác vụ AI/ML nặng thành microservice độc lập.
- **Tools:** `transcribe_audio` (PhoWhisper), `fix_spelling` (Gemini), `convert_to_soap_note` (Gemini).
- **Transport:** Streamable HTTP (`http://localhost:8001/mcp`).

### 5. Database
- **Type:** SQLite (development) / PostgreSQL (production).
- **Tables:** `users` (tài khoản bác sĩ), `clinical_notes` (lịch sử SOAP note).
- **ORM:** SQLAlchemy v2 với `DeclarativeBase`.

## Data Flow

1. Bác sĩ upload file âm thanh qua Frontend.
2. FastAPI xác thực JWT Bearer Token.
3. `Clinical Service` ghi file vào thư mục temp, gọi `clinical_agent.ainvoke()`.
4. LangGraph `transcribe_node` → MCP `transcribe_audio` → **PhoWhisper** → trả về transcript.
5. LangGraph `fix_spelling_node` → MCP `fix_spelling` → **Gemini** → trả về corrected transcript.
6. LangGraph `soap_node` → MCP `convert_to_soap_note` → **Gemini** → trả về SOAP Note.
7. Kết quả (`transcript`, `corrected_transcript`, `soap_note`) được lưu vào Database.
8. API trả JSON response về Frontend để hiển thị.

## Deployment Architecture

```mermaid
graph LR
    subgraph Docker ["Docker Compose"]
        FE_C["Frontend Container\n(Next.js · Port 3000)"]
        BE_C["Backend Container\n(FastAPI · Port 8000)"]
        MCP_C["MCP Container\n(FastMCP · Port 8001)"]
        DB_C["Database Container\n(PostgreSQL · Port 5432)"]
    end

    FE_C --> BE_C --> MCP_C
    BE_C --> DB_C
```

## Security

- API keys lưu trong `.env` — **không commit lên Git**.
- Input validation qua Pydantic v2.
- File upload giới hạn định dạng: `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.webm`.
- CORS được cấu hình cho frontend domain.
- File âm thanh tạm thời bị xóa ngay sau khi xử lý xong.

## Design Decisions

| Quyết định | Lựa chọn | Lý do |
|---|---|---|
| **Agent Framework** | LangGraph | Quản lý State rõ ràng, dễ thêm/bớt node, hỗ trợ conditional routing |
| **Tool Execution** | FastMCP (riêng biệt) | Tách process nặng ra khỏi API server, load model một lần, dễ scale |
| **ASR Model** | vinai/PhoWhisper-small | Tối ưu riêng cho tiếng Việt, chạy offline, không tốn API call |
| **LLM** | Google Gemini 2.0 Flash | Chi phí thấp, tốc độ nhanh, chất lượng tốt với tiếng Việt y khoa |
| **Backend** | FastAPI | Async native, tự động sinh Swagger docs, type-safe với Pydantic |
| **Database** | SQLite / PostgreSQL | SQLite cho dev nhanh gọn, PostgreSQL cho production scale |

📄 **Tài liệu chi tiết hơn (với đầy đủ 3 sơ đồ):** [`docs/architecture_diagram.md`](docs/architecture_diagram.md)
