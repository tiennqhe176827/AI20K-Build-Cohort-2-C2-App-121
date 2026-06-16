#!/usr/bin/env python3
"""
Tạo database clinical_scribe.db theo sơ đồ ER:

    Doctor ──1:N──> Encounter <──N:1── Patient
                       │
           ┌───────────┼───────────┐
           ▼           ▼           ▼
       Recording   Transcript  SOAP_Note
                                  │
                ┌─────────────────┼─────────────────┐
                ▼                 ▼                 ▼
        SOAP_Subjective   SOAP_Objective   SOAP_Assessment
                                                      │
                                                      ▼
                                              SOAP_Diagnosis
                                                      │
                                                      ▼
                                                  SOAP_Plan

Cách chạy:
    python src/api/create_db.py

Sinh ra file:
    data/clinical_scribe.db
"""

import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DB_DIR / "clinical_scribe.db"
VN_TZ = timezone(timedelta(hours=7))
NOW = datetime.now(VN_TZ).isoformat()


def hash_pw(pw: str) -> str:
    """Hash password bằng bcrypt (giống security.py)."""
    import bcrypt
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_tables(conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    c.executescript("""
        PRAGMA foreign_keys = ON;

        -- Xóa bảng cũ (theo thứ tự FK)
        DROP TABLE IF EXISTS clinical_notes;
        DROP TABLE IF EXISTS soap_plan;
        DROP TABLE IF EXISTS soap_diagnosis;
        DROP TABLE IF EXISTS soap_assessment;
        DROP TABLE IF EXISTS soap_objective;
        DROP TABLE IF EXISTS soap_subjective;
        DROP TABLE IF EXISTS soap_notes;
        DROP TABLE IF EXISTS transcripts;
        DROP TABLE IF EXISTS recordings;
        DROP TABLE IF EXISTS encounters;
        DROP TABLE IF EXISTS shifts;
        DROP TABLE IF EXISTS patients;
        DROP TABLE IF EXISTS doctors;
        DROP TABLE IF EXISTS users;

        -- =============================================
        -- 0. users (cho Auth - JWT login)
        -- =============================================
        CREATE TABLE users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            email           TEXT    NOT NULL UNIQUE,
            full_name       TEXT    NOT NULL,
            hashed_password TEXT    NOT NULL,
            role            TEXT    NOT NULL DEFAULT 'user',
            is_active       INTEGER NOT NULL DEFAULT 1,
            created_at      TEXT    NOT NULL,
            updated_at      TEXT    NOT NULL
        );

        CREATE INDEX idx_users_email ON users(email);
        CREATE INDEX idx_users_role  ON users(role);

        -- =============================================
        -- 0b. clinical_notes (cho SOAP note history)
        -- =============================================
        CREATE TABLE clinical_notes (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id              INTEGER NOT NULL,
            transcript           TEXT    NOT NULL,
            corrected_transcript TEXT    NOT NULL DEFAULT '',
            soap_note            TEXT    NOT NULL,
            audio_filename       TEXT,
            created_at           TEXT    NOT NULL,
            updated_at           TEXT    NOT NULL,

            FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );

        CREATE INDEX idx_clinical_notes_user ON clinical_notes(user_id);

        -- =============================================
        -- 1. doctors
        -- =============================================
        CREATE TABLE doctors (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name       TEXT    NOT NULL,
            specialization  TEXT    NOT NULL DEFAULT '',
            email           TEXT    UNIQUE,
            phone           TEXT,
            is_active       INTEGER NOT NULL DEFAULT 1,
            created_at      TEXT    NOT NULL,
            updated_at      TEXT    NOT NULL
        );

        -- =============================================
        -- 2. shifts
        -- =============================================
        CREATE TABLE shifts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id   INTEGER NOT NULL,
            shift_date  TEXT    NOT NULL,
            start_time  TEXT    NOT NULL,
            end_time    TEXT    NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'scheduled',
            created_at  TEXT    NOT NULL,

            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );

        CREATE INDEX idx_shifts_doctor ON shifts(doctor_id);
        CREATE INDEX idx_shifts_date   ON shifts(shift_date);

        -- =============================================
        -- 3. patients
        -- =============================================
        CREATE TABLE patients (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name       TEXT    NOT NULL,
            date_of_birth   TEXT,
            gender          TEXT    CHECK(gender IN ('male','female','other')),
            phone           TEXT,
            email           TEXT,
            address         TEXT,
            medical_record_no TEXT  UNIQUE,
            created_at      TEXT    NOT NULL,
            updated_at      TEXT    NOT NULL
        );

        -- =============================================
        -- 4. encounters
        -- =============================================
        CREATE TABLE encounters (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id       INTEGER NOT NULL,
            patient_id      INTEGER NOT NULL,
            encounter_date  TEXT    NOT NULL,
            chief_complaint TEXT    NOT NULL DEFAULT '',
            status          TEXT    NOT NULL DEFAULT 'in_progress',
            created_at      TEXT    NOT NULL,
            updated_at      TEXT    NOT NULL,

            FOREIGN KEY (doctor_id)  REFERENCES doctors(id)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );

        CREATE INDEX idx_encounters_doctor  ON encounters(doctor_id);
        CREATE INDEX idx_encounters_patient ON encounters(patient_id);
        CREATE INDEX idx_encounters_date    ON encounters(encounter_date);

        -- =============================================
        -- 5. recordings
        -- =============================================
        CREATE TABLE recordings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id    INTEGER NOT NULL,
            file_path       TEXT    NOT NULL,
            file_name       TEXT    NOT NULL,
            duration_sec    INTEGER,
            file_size_bytes INTEGER,
            created_at      TEXT    NOT NULL,

            FOREIGN KEY (encounter_id) REFERENCES encounters(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );

        CREATE INDEX idx_recordings_encounter ON recordings(encounter_id);

        -- =============================================
        -- 6. transcripts
        -- =============================================
        CREATE TABLE transcripts (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id        INTEGER NOT NULL,
            raw_transcript      TEXT    NOT NULL DEFAULT '',
            corrected_transcript TEXT   NOT NULL DEFAULT '',
            language            TEXT    NOT NULL DEFAULT 'vi',
            created_at          TEXT    NOT NULL,
            updated_at          TEXT    NOT NULL,

            FOREIGN KEY (encounter_id) REFERENCES encounters(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );

        CREATE INDEX idx_transcripts_encounter ON transcripts(encounter_id);

        -- =============================================
        -- 7. soap_notes
        -- =============================================
        CREATE TABLE soap_notes (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id    INTEGER NOT NULL,
            note_type       TEXT    NOT NULL DEFAULT 'initial',
            created_at      TEXT    NOT NULL,
            updated_at      TEXT    NOT NULL,

            FOREIGN KEY (encounter_id) REFERENCES encounters(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );

        CREATE INDEX idx_soap_notes_encounter ON soap_notes(encounter_id);

        -- =============================================
        -- 8. soap_subjective
        -- =============================================
        CREATE TABLE soap_subjective (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            soap_note_id    INTEGER NOT NULL UNIQUE,
            chief_complaint TEXT    NOT NULL DEFAULT '',
            history         TEXT    NOT NULL DEFAULT '',
            review_of_systems TEXT  NOT NULL DEFAULT '',
            created_at      TEXT    NOT NULL,

            FOREIGN KEY (soap_note_id) REFERENCES soap_notes(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );

        -- =============================================
        -- 9. soap_objective
        -- =============================================
        CREATE TABLE soap_objective (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            soap_note_id    INTEGER NOT NULL UNIQUE,
            vital_signs     TEXT    NOT NULL DEFAULT '',
            physical_exam   TEXT    NOT NULL DEFAULT '',
            lab_results     TEXT    NOT NULL DEFAULT '',
            created_at      TEXT    NOT NULL,

            FOREIGN KEY (soap_note_id) REFERENCES soap_notes(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );

        -- =============================================
        -- 10. soap_assessment
        -- =============================================
        CREATE TABLE soap_assessment (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            soap_note_id    INTEGER NOT NULL UNIQUE,
            diagnosis       TEXT    NOT NULL DEFAULT '',
            severity        TEXT    NOT NULL DEFAULT '',
            notes           TEXT    NOT NULL DEFAULT '',
            created_at      TEXT    NOT NULL,

            FOREIGN KEY (soap_note_id) REFERENCES soap_notes(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );

        -- =============================================
        -- 11. soap_diagnosis
        -- =============================================
        CREATE TABLE soap_diagnosis (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            soap_assessment_id  INTEGER NOT NULL UNIQUE,
            primary_diagnosis   TEXT    NOT NULL DEFAULT '',
            differential_diagnoses TEXT NOT NULL DEFAULT '',
            icd_code            TEXT,
            created_at          TEXT    NOT NULL,

            FOREIGN KEY (soap_assessment_id) REFERENCES soap_assessment(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );

        -- =============================================
        -- 12. soap_plan
        -- =============================================
        CREATE TABLE soap_plan (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            soap_diagnosis_id   INTEGER NOT NULL UNIQUE,
            treatment           TEXT    NOT NULL DEFAULT '',
            medications         TEXT    NOT NULL DEFAULT '',
            follow_up           TEXT    NOT NULL DEFAULT '',
            patient_education   TEXT    NOT NULL DEFAULT '',
            created_at          TEXT    NOT NULL,

            FOREIGN KEY (soap_diagnosis_id) REFERENCES soap_diagnosis(id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
    """)
    conn.commit()
    print("[OK] Da tao 14 bang (users + clinical_notes + 12 ER bang)")


def seed_data(conn: sqlite3.Connection) -> None:
    c = conn.cursor()

    # ========== users (cho Auth) ==========
    users = [
        ("admin@vinuni.edu.vn", "Admin System", hash_pw("admin123"), "admin", 1, NOW, NOW),
        ("nguyenquoctien0000@gmail.com", "Nguyen Quoc Tien", hash_pw("user123"), "user", 1, NOW, NOW),
        ("bs.nguyen@hospital.vn", "BS. Nguyen Van A", hash_pw("doctor123"), "doctor", 1, NOW, NOW),
        ("bs.tran@hospital.vn", "BS. Tran Thi B", hash_pw("doctor123"), "doctor", 1, NOW, NOW),
        ("inactive@vinuni.edu.vn", "Inactive User", hash_pw("inactive123"), "user", 0, NOW, NOW),
    ]
    c.executemany(
        "INSERT INTO users (email, full_name, hashed_password, role, is_active, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        users,
    )

    # ========== clinical_notes ==========
    clinical_notes = [
        (2, "Benh nhan nam 45 tuoi, met keo dai", "Bệnh nhân nam 45 tuổi, mệt kéo dài",
         "S: Met keo dai 2 tuan\nO: BMI 18.5, WBC 3.2\nA: Suy giam mien dich\nP: Xet nghiem chuyen sau",
         "consultation_001.wav", NOW, NOW),
        (3, "Tre em 8 tuoi, sot cao 39 do", "Trẻ em 8 tuổi, sốt cao 39 độ",
         "S: Sot cao 39.5, dau hong\nO: Amidan sưng đỏ 2+\nA: Viem amidan cap\nP: Paracetamol + Penicillin",
         None, NOW, NOW),
        (3, "Nam 62 tuoi, kham dinh ky", "Nam 62 tuổi, khám định kỳ",
         "S: DT2 5 nam, HAP 3 nam\nO: HbA1c 7.2%, HA 135/85\nA: DT2 chua dat muc tieu\nP: Tang Metformin + Ramipril",
         None, NOW, NOW),
    ]
    c.executemany(
        "INSERT INTO clinical_notes (user_id, transcript, corrected_transcript, soap_note, audio_filename, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        clinical_notes,
    )

    # ========== doctors ==========
    doctors = [
        ("BS. Nguyen Van A", "Noi tong hop", "bs.nguyen@hospital.vn", "0901234567", 1, NOW, NOW),
        ("BS. Tran Thi B", "San phu khoa", "bs.tran@hospital.vn", "0912345678", 1, NOW, NOW),
        ("BS. Le Van C", "Nhi khoa", "bs.le@hospital.vn", "0923456789", 1, NOW, NOW),
    ]
    c.executemany(
        "INSERT INTO doctors (full_name, specialization, email, phone, is_active, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        doctors,
    )

    # ========== patients ==========
    patients = [
        ("Pham Van D", "1980-05-15", "male", "0934567890", "pham.d@gmail.com", "Ha Noi", "MRN-001", NOW, NOW),
        ("Hoang Thi E", "1995-08-20", "female", "0945678901", "hoang.e@gmail.com", "Hai Phong", "MRN-002", NOW, NOW),
        ("Vo Van F", "1962-12-01", "male", "0956789012", "vo.f@gmail.com", "TP HCM", "MRN-003", NOW, NOW),
        ("Nguyen Thi G", "1998-03-10", "female", "0967890123", "nguyen.g@gmail.com", "Da Nang", "MRN-004", NOW, NOW),
        ("Tran Van H", "2018-07-25", "male", "0978901234", None, "Ha Noi", "MRN-005", NOW, NOW),
    ]
    c.executemany(
        "INSERT INTO patients (full_name, date_of_birth, gender, phone, email, address, medical_record_no, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
        patients,
    )

    # ========== shifts ==========
    shifts = [
        (1, "2026-06-16", "07:00", "12:00", "completed", NOW),
        (1, "2026-06-16", "13:00", "17:00", "in_progress", NOW),
        (2, "2026-06-16", "08:00", "16:00", "in_progress", NOW),
        (3, "2026-06-16", "07:00", "12:00", "scheduled", NOW),
    ]
    c.executemany(
        "INSERT INTO shifts (doctor_id, shift_date, start_time, end_time, status, created_at) VALUES (?,?,?,?,?,?)",
        shifts,
    )

    # ========== encounters ==========
    encounters = [
        (1, 1, "2026-06-16 08:30:00", "Met kéo dài 2 tuần, mệt mỏi", "completed", NOW, NOW),
        (3, 5, "2026-06-16 09:15:00", "Sốt cao 39.5°C, đau họng", "completed", NOW, NOW),
        (1, 3, "2026-06-16 10:00:00", "Khám định kỳ - đái tháo đường", "completed", NOW, NOW),
        (2, 4, "2026-06-16 10:30:00", "Mang thai 12 tuần, ra máu nhẹ", "in_progress", NOW, NOW),
    ]
    c.executemany(
        "INSERT INTO encounters (doctor_id, patient_id, encounter_date, chief_complaint, status, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        encounters,
    )

    # ========== recordings ==========
    recordings = [
        (1, "uploads/enc_001.wav", "enc_001.wav", 180, 1440000, NOW),
        (2, "uploads/enc_002.wav", "enc_002.wav", 240, 1920000, NOW),
        (3, "uploads/enc_003.wav", "enc_003.wav", 300, 2400000, NOW),
        (4, "uploads/enc_004.wav", "enc_004.wav", 210, 1680000, NOW),
    ]
    c.executemany(
        "INSERT INTO recordings (encounter_id, file_path, file_name, duration_sec, file_size_bytes, created_at) VALUES (?,?,?,?,?,?)",
        recordings,
    )

    # ========== transcripts ==========
    transcripts = [
        (1,
         "Benh nhan nam 46 tuoi, met keo dai 2 tuan, khong sot, khong ho",
         "Bệnh nhân nam 46 tuổi, mệt kéo dài 2 tuần, không sốt, không ho",
         "vi", NOW, NOW),
        (2,
         "Tre em 8 tuoi, sot cao 39 do 5, dau hong, nuot kho, chay mui trong",
         "Trẻ em 8 tuổi, sốt cao 39.5 độ, đau họng, nuốt khó, chảy mũi trong",
         "vi", NOW, NOW),
        (3,
         "Nam 62 tuoi, kham dinh ky, tieu duong type 2, huyet ap cao",
         "Nam 62 tuổi, khám định kỳ, đái tháo đường type 2, huyết áp cao",
         "vi", NOW, NOW),
        (4,
         "Nu 28 tuoi, mang thai 12 tuan, dau bung duoi, ra mau nhe",
         "Nữ 28 tuổi, mang thai 12 tuần, đau bụng dưới, ra máu nhẹ",
         "vi", NOW, NOW),
    ]
    c.executemany(
        "INSERT INTO transcripts (encounter_id, raw_transcript, corrected_transcript, language, created_at, updated_at) VALUES (?,?,?,?,?,?)",
        transcripts,
    )

    # ========== soap_notes ==========
    soap_notes = [
        (1, "initial", NOW, NOW),
        (2, "initial", NOW, NOW),
        (3, "initial", NOW, NOW),
        (4, "initial", NOW, NOW),
    ]
    c.executemany(
        "INSERT INTO soap_notes (encounter_id, note_type, created_at, updated_at) VALUES (?,?,?,?)",
        soap_notes,
    )

    # ========== soap_subjective ==========
    c.executemany(
        "INSERT INTO soap_subjective (soap_note_id, chief_complaint, history, review_of_systems, created_at) VALUES (?,?,?,?,?)",
        [
            (1,
             "Mệt mỏi kéo dài 2 tuần",
             "Không sốt, không ho, không khó thở. Ngủ ít, ăn kém.",
             "- Tiêu hóa: bình thường\n- Hô hấp: bình thường\n- Thần kinh: mệt mỏi",
             NOW),
            (2,
             "Sốt cao 39.5°C, đau họng",
             "Mẹ kể trẻ sốt từ sáng, không dùng thuốc hạ sốt. Đau họng, nuốt đau.",
             "- Tai Mũi Họng: đau họng, chảy mũi\n- hô hấp: bình thường",
             NOW),
            (3,
             "Khám định kỳ",
             "Tiểu đường type 2 5 năm. Huyết áp cao 3 năm. Dùng Metformin + Amlodipine.",
             "- Nội tiết: ổn định\n- Tim mạch: hơi cao HA",
             NOW),
            (4,
             "Ra máu nhẹ khi mang thai",
             "Thai 12 tuần. Ra máu màu nâu, lượng ít. Không đau dữ dội.",
             "- Sản khoa: ra máu âm đạo\n- Tổng trạng: bình thường",
             NOW),
        ],
    )

    # ========== soap_objective ==========
    c.executemany(
        "INSERT INTO soap_objective (soap_note_id, vital_signs, physical_exam, lab_results, created_at) VALUES (?,?,?,?,?)",
        [
            (1,
             "HA 120/80, Mạch 78, Nhiệt 36.8°C, SpO2 98%",
             "Gầy, BMI 18.5. Da xanh, niêm mạc nhợt. Tim phổi bình thường.",
             "WBC 3.2 (giảm), Lymphocyte 18%, Hb 11.8",
             NOW),
            (2,
             "Nhiệt 39.5°C, Mạch 110, HA 100/60, SpO2 99%",
             "Amidan sưng đỏ 2+, có giả mạc trắng. Hạch góc hàm sưng 1cm.",
             "CRP 45 (tăng), WBC 14.2",
             NOW),
            (3,
             "HA 135/85, Mạch 72, Nhiệt 36.6°C, BMI 26.8",
             "Béo nhẹ. Tim đều, phổi trong. Bụng mềm, không đau.",
             "HbA1c 7.2%, Đường huyết đói 145, LDL 140, Cholesterol 220",
             NOW),
            (4,
             "HA 110/70, Mạch 88, Nhiệt 36.9°C",
             "Thai 12 tuần, tử cung sized phù hợp. Cổ tử cung đóng.",
             "Hb 11.2. Siêu âm: Thai 12+3 ngày, tim thai+, nhau bám thấp",
             NOW),
        ],
    )

    # ========== soap_assessment ==========
    c.executemany(
        "INSERT INTO soap_assessment (soap_note_id, diagnosis, severity, notes, created_at) VALUES (?,?,?,?,?)",
        [
            (1, "Suy giảm miễn dịch thứ phát", "medium", "Cần loại trừ HIV, tuyến giáp, tự miễn", NOW),
            (2, "Viêm amidan cấp (Cobbs grade 2)", "mild", "Chưa loại trừ liên cầu khuẩn group A", NOW),
            (3, "Đái tháo đường type 2 - kiểm soát chưa đạt mục tiêu", "medium", "HbA1c >7%, HA >130/80", NOW),
            (4, "Dọa sảy thai (threatened abortion)", "high", "Nhau bám thấp loại II", NOW),
        ],
    )

    # ========== soap_diagnosis ==========
    c.executemany(
        "INSERT INTO soap_diagnosis (soap_assessment_id, primary_diagnosis, differential_diagnoses, icd_code, created_at) VALUES (?,?,?,?,?)",
        [
            (1, "Suy giảm miễn dịch thứ phát", "HIV; Lupus; Suy tuyến giáp", "D84.9", NOW),
            (2, "Viêm amidan cấp", "Viêm họng liên cầu; Viêm amidan virus", "J03.9", NOW),
            (3, "Đái tháo đường type 2", "", "E11.9", NOW),
            (4, "Dọa sảy thai", "Mang thai ngoài tử cung; Polyp cổ tử cung", "O20.0", NOW),
        ],
    )

    # ========== soap_plan ==========
    c.executemany(
        "INSERT INTO soap_plan (soap_diagnosis_id, treatment, medications, follow_up, patient_education, created_at) VALUES (?,?,?,?,?,?)",
        [
            (1,
             "Xét nghiệm chuyên sâu",
             "Chưa có thuốc",
             "Tái khám sau 1 tuần",
             "Nghỉ ngơi, dinh dưỡng đầy đủ",
             NOW),
            (2,
             "Kháng sinh nếu xét nghiệm (+)",
             "Paracetamol 15mg/kg x4; Penicillin V nếu (+)",
             "Tái khám sau 3 ngày",
             "Uống nhiều nước, nghỉ ngơi",
             NOW),
            (3,
             "Điều chỉnh thuốc",
             "Metformin 850mg x2; Ramipril 5mg; Atorvastatin 20mg",
             "Tái khám 1 tháng, xét nghiệm HbA1c",
             "Kiêng đường, tập thể dục 30 phút/ngày",
             NOW),
            (4,
             "Nghỉ ngơi tuyệt đối",
             "Duphaston 20mg x2",
             "Tái khám 1 tuần, siêu âm lại",
             "Không QHTD, đến viện nếu ra máu nhiều",
             NOW),
        ],
    )

    conn.commit()

    counts = {}
    for table in ["doctors", "patients", "shifts", "encounters", "recordings",
                   "transcripts", "soap_notes", "soap_subjective", "soap_objective",
                   "soap_assessment", "soap_diagnosis", "soap_plan"]:
        counts[table] = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    parts = ", ".join(f"{v} {k}" for k, v in counts.items() if v > 0)
    print(f"[OK] Da them du lieu mau: {parts}")


def verify(conn: sqlite3.Connection) -> None:
    c = conn.cursor()

    print(f"\n===== DATABASE: {DB_PATH.name} =====")
    print(f"  Kich thuoc: {DB_PATH.stat().st_size / 1024:.1f} KB")

    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
    print(f"  So bang: {len(tables)}")
    for t in tables:
        count = c.execute(f"SELECT COUNT(*) FROM [{t[0]}]").fetchone()[0]
        print(f"    {t[0]}: {count} dong")

    # FK check
    print("\n  Khoa ngoai:")
    for t_name in [row[0] for row in tables]:
        fks = c.execute(f"PRAGMA foreign_key_list([{t_name}])").fetchall()
        for fk in fks:
            print(f"    {t_name}.{fk[3]} -> {fk[2]}(id)")

    print("\n[OK] Verify thanh cong!")


def main() -> None:
    print("=" * 55)
    print("  CREATE DATABASE: clinical_scribe.db")
    print("  So do: Doctor/Patient -> Encounter -> SOAP components")
    print("=" * 55)

    DB_DIR.mkdir(parents=True, exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"[INFO] Da xoa database cu")

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        create_tables(conn)
        seed_data(conn)
        verify(conn)
    finally:
        conn.close()

    print(f"\nFile: {DB_PATH}")


if __name__ == "__main__":
    main()
