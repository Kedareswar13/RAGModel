# AI Booking Assistant

A Streamlit‑based chat application with RAG over uploaded PDFs, conversational booking flow, SQLite persistence, email confirmations, and an admin dashboard.

---

## 🚀 Features

- **Chat & RAG**
  - Upload one or more PDFs.
  - Ask questions answered using retrieved chunks + LLM.
  - Falls back to direct LLM chat when no PDFs are uploaded.

- **Conversational Booking**
  - Detects booking intent (`book`, `appointment`, `reservation`).
  - Multi‑turn slot filling via UI:
    - name, email, phone, booking_type, date (YYYY‑MM‑DD), time (HH:MM)
  - Summarizes details and asks for explicit confirmation.
  - Saves to SQLite and sends confirmation email.

- **Admin Dashboard**
  - View all bookings with customer info.
  - Filter by name, email, or date.

- **Tools**
  - RAG Tool: query → retrieved answer.
  - Booking Persistence Tool: structured payload → DB insert.
  - Email Tool: SMTP confirmation (graceful failure handling).

- **Short‑term Memory**
  - Last ~25 chat messages retained in `st.session_state`.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: Google Gemini (`langchain-google-genai`)
- **Embeddings**: `sentence-transformers` (all-MiniLM-L6-v2)
- **Vector Store**: FAISS (in‑memory)
- **PDF Parsing**: `pypdf`
- **Database**: SQLite (`customers`, `bookings`)
- **Email**: SMTP (configurable via env/secrets)

---

## 📦 Installation

1. Clone or download this folder.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` (optional for local runs) with:

   ```env
   GEMINI_API_KEY="your_gemini_api_key_here"
   GEMINI_MODEL="gemini-1.5-flash"
   SMTP_HOST="smtp.gmail.com"
   SMTP_PORT="587"
   SMTP_USER="your_email@example.com"
   SMTP_PASS="your_app_password_here"
   ```

4. Run:

   ```bash
   streamlit run app.py
   ```

---

## 🧭 Usage

### 1. Chat & Booking

- Open `http://localhost:8501` (or the URL shown in terminal).
- **Ask questions**:
  - If PDFs are uploaded → RAG answers.
  - Otherwise → direct Gemini chat.
- **Start a booking**:
  - Type anything containing `book`, `appointment`, or `reservation`.
  - Fill the booking form.
  - Click **✅ Confirm Booking**.
  - You’ll see:
    - Booking ID.
    - Success message.
    - Optional email warning if SMTP isn’t configured.

### 2. Admin Dashboard

- From the sidebar, go to **Admin Dashboard**.
- View all bookings and use filters.
- No edit/delete in this minimal version (can be added later).

---

## 🌐 Deployment (Streamlit Cloud)

1. Push this repo to GitHub.
2. On Streamlit Cloud:
   - Connect the repo.
   - In **Secrets**, add:
     - `GEMINI_API_KEY`
     - `GEMINI_MODEL` (optional)
     - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`
3. Deploy.
4. Your app will be publicly accessible.

---

## 📂 Project Structure

```
AI_UseCase/
├─ app.py                 # Streamlit entry
├─ app/
│  ├─ config.py          # Environment variables
│  ├─ rag_pipeline.py     # PDF → embeddings → FAISS → RAG
│  ├─ tools.py           # RAG / DB / Email tools
│  ├─ booking_flow.py    # Booking state & validation
│  └─ admin_dashboard.py # Admin UI
├─ db/
│  ├─ database.py         # SQLite init & connection
│  └─ models.py          # CRUD helpers
├─ models/
│  ├─ llm.py            # Gemini model factory
│  └─ embeddings.py     # Sentence‑transformers embeddings
├─ requirements.txt
├─ .env (local only, git‑ignored)
└─ README.md
```

---

## 🧩 Troubleshooting

- **LLM not available**: Ensure `GEMINI_API_KEY` is set in `.env` or Streamlit secrets.
- **RAG does not work**: Upload at least one PDF; check `pypdf` extraction.
- **Email not sent**: Verify SMTP credentials; check Gmail app password settings.
- **Import errors**: Run `pip install -r requirements.txt` again after any changes.

---

## 📄 License

MIT License — feel free to use and modify.

---

## 🤝 Contributing

1. Fork the repo.
2. Create a feature branch.
3. Open a pull request.

---

## 📬 Contact

For questions or issues, open an issue on the repository.

---
