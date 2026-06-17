# Architecture Diagram — AI Clinical Scribe

## 1. End-to-End System Flow

Luồng toàn cảnh từ lúc bác sĩ upload file âm thanh đến khi nhận SOAP Note hoàn chỉnh.

```mermaid
sequenceDiagram
    actor Doctor as 🩺 Bác sĩ
    participant FE as Frontend<br/>(React/Next.js)
    participant API as FastAPI Backend<br/>(Port 8000)
    participant Auth as JWT Auth<br/>Middleware
    participant DB as SQLite / PostgreSQL
    participant Agent as LangGraph Agent
    participant MCP as FastMCP Server<br/>(Port 8001)

    Doctor->>FE: Upload file âm thanh (.wav, .mp3, ...)
    FE->>API: POST /api/v1/clinical/soap-note<br/>Authorization: Bearer <token>
    API->>Auth: Xác thực JWT Token
    Auth-->>API: ✅ User hợp lệ

    API->>Agent: ainvoke({audio_path})

    Note over Agent,MCP: LangGraph điều phối qua 3 Node tuần tự

    Agent->>MCP: call_tool("transcribe_audio", {audio_path})
    MCP-->>Agent: transcript (text tiếng Việt thô)

    Agent->>MCP: call_tool("fix_spelling", {transcript})
    MCP-->>Agent: corrected_transcript (text đã hiệu đính)

    Agent->>MCP: call_tool("convert_to_soap_note", {corrected_transcript})
    MCP-->>Agent: soap_note (định dạng SOAP chuẩn y khoa)

    Agent-->>API: {transcript, corrected_transcript, soap_note}

    API->>DB: save_note(user_id, transcript, corrected_transcript, soap_note)
    DB-->>API: ✅ Đã lưu

    API-->>FE: ClinicalSoapResponse (JSON)
    FE-->>Doctor: Hiển thị SOAP Note
```

---

## 2. LangGraph + MCP Component Architecture

Kiến trúc nội bộ của Agent, thể hiện rõ vai trò từng thành phần.

```mermaid
graph TB
    subgraph Client ["🌐 Client Layer"]
        FE["Frontend (React/Next.js)"]
    end

    subgraph Backend ["⚡ FastAPI Backend (Port 8000)"]
        Router["Router: /api/v1/clinical"]
        AuthDep["Dependency: get_current_user\n(JWT Bearer Token)"]
        Service["Clinical Service\nprocess_audio_upload()"]
        Repo["Repository\nsave_note() / get_notes_by_user()"]
        DB[("SQLite / PostgreSQL\nusers + clinical_notes")]
    end

    subgraph AgentLayer ["🧠 LangGraph Agent"]
        Graph["StateGraph\nbuild_graph()"]
        State[("ClinicalState\naudio_path\ntranscript\ncorrected_transcript\nsoap_note\nerror")]
        N1["transcribe_node"]
        N2["fix_spelling_node"]
        N3["soap_node"]
        MCPClient["MultiServerMCPClient\n(Streamable HTTP)"]
    end

    subgraph MCPServer ["🔧 FastMCP Server (Port 8001)"]
        T1["Tool: transcribe_audio"]
        T2["Tool: fix_spelling"]
        T3["Tool: convert_to_soap_note"]
    end

    subgraph AIModels ["🤖 AI Models"]
        PhoWhisper["vinai/PhoWhisper-small\n(HuggingFace Transformers)\nASR — Tiếng Việt"]
        Gemini["Google Gemini 2.0 Flash\n(google-genai SDK)\nNLP — Tiếng Việt y khoa"]
    end

    FE -->|"POST /soap-note\nmultipart/form-data"| Router
    Router --> AuthDep
    Router --> Service
    Service -->|"ainvoke()"| Graph
    Graph <-->|"đọc / ghi"| State
    State --> N1 & N2 & N3
    N1 & N2 & N3 -->|"call_clinical_tool()"| MCPClient
    MCPClient -->|"Streamable HTTP"| MCPServer

    T1 --> PhoWhisper
    T2 --> Gemini
    T3 --> Gemini

    Service -->|"kết quả"| Repo
    Repo --> DB
```

---

## 3. Agent Data Flow — Biến đổi ClinicalState

Theo dõi cách `ClinicalState` được cập nhật qua từng Node trong LangGraph graph.

```mermaid
flowchart TD
    START(["▶ START\nainvoke({audio_path})"]) --> TN

    TN["🎙️ transcribe_node\nGọi MCP: transcribe_audio(audio_path)"]
    TN -->|"✅ Thành công"| TN_OK{"route_after_transcribe()"}
    TN -->|"❌ Lỗi"| END_ERR1(["⏹ END\nState: {error}"])

    TN_OK -->|"Không có lỗi"| FN
    TN_OK -->|"Có lỗi"| END_ERR1

    FN["✏️ fix_spelling_node\nGọi MCP: fix_spelling(transcript)"]
    FN -->|"✅ Thành công"| FN_OK{"route_after_fix_spelling()"}
    FN -->|"❌ Lỗi"| END_ERR2(["⏹ END\nState: {error}"])

    FN_OK -->|"Không có lỗi"| SN
    FN_OK -->|"Có lỗi"| END_ERR2

    SN["📋 soap_node\nGọi MCP: convert_to_soap_note(corrected_transcript)"]
    SN --> END_OK(["⏹ END\nState: {transcript, corrected_transcript, soap_note}"])

    style START fill:#4CAF50,color:#fff
    style END_OK fill:#2196F3,color:#fff
    style END_ERR1 fill:#f44336,color:#fff
    style END_ERR2 fill:#f44336,color:#fff
    style TN fill:#FFF9C4
    style FN fill:#FFF9C4
    style SN fill:#FFF9C4
```

---

## 4. Component Details

| Component | Technology | Vai trò |
|---|---|---|
| **Frontend** | React / Next.js | Giao diện người dùng — upload âm thanh, hiển thị SOAP note |
| **Backend** | FastAPI + Uvicorn | API server, xác thực JWT, định tuyến request |
| **Auth** | JWT (python-jose) + bcrypt | Đăng ký / đăng nhập / bảo vệ endpoint |
| **LangGraph Agent** | LangGraph | Điều phối luồng xử lý qua StateGraph |
| **MCP Server** | FastMCP | Đóng gói tools AI thành microservice độc lập |
| **ASR Engine** | `vinai/PhoWhisper-small` | Nhận diện giọng nói tiếng Việt y khoa |
| **LLM** | Google Gemini 2.0 Flash | Hiệu đính chính tả và tạo SOAP Note |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Lưu trữ hồ sơ bệnh nhân và lịch sử SOAP note |
| **ORM** | SQLAlchemy v2 | Quản lý model và session database |

---

## 5. Lý do thiết kế MCP (Design Rationale)

Hệ thống tách biệt **LangGraph Agent** và **FastMCP Server** thành 2 process riêng biệt vì:

- **Tách trách nhiệm rõ ràng:** LangGraph chỉ làm nhiệm vụ *điều phối (orchestration)*, không thực thi logic nặng.
- **Tránh nghẽn cổ chai:** Mô hình `PhoWhisper-small` (~240MB) được load một lần duy nhất khi MCP Server khởi động, không tốn thời gian khởi tạo lại mỗi request.
- **Dễ mở rộng (Scalable):** Có thể scale MCP Server độc lập với Backend nếu lưu lượng tăng cao.
- **Dễ kiểm thử:** Từng Tool trong MCP Server có thể được test độc lập mà không cần chạy cả pipeline.
