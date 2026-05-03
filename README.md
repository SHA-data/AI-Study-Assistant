# 🎓 My Study Buddy — AI-Powered Learning Assistant

![Project Banner](https://img.shields.io/badge/AI-Study--Assistant-blueviolet?style=for-the-badge&logo=openai)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?style=for-the-badge&logo=flask)
![ChromaDB](https://img.shields.io/badge/Vector--DB-ChromaDB-orange?style=for-the-badge)

**My Study Buddy** is a sophisticated, full-stack AI application designed to help students and researchers manage their knowledge base, chat with their documents, and verify claims using state-of-the-art Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG).

---

## 🚀 Key Features

- **🧠 Contextual Chat**: Engage in deep conversations with your study materials. The AI retrieves relevant context from your uploaded documents to provide accurate, grounded answers.
- **📄 Multi-Format Ingestion**: Support for PDF, Plain Text, URLs, and PPTX files.
- **🔍 Claim Verification**: Automatically extract and verify claims from documents, categorizing them as supported, unverified, or active.
- **📚 Knowledge Library**: A centralized hub to manage your uploaded resources, organized by subject and metadata.
- **⚡ High Performance**: Powered by **Groq (Llama 3.3)** for lightning-fast inference and **Google Gemini** for high-quality embeddings.
- **🎨 Premium UI**: A clean, modern, and responsive interface with smooth micro-animations and intuitive navigation.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask
- **LLM**: Llama 3.3 70B (via Groq)
- **Embeddings**: Gemini Embedding 001 (via Google GenAI)
- **Orchestration**: LangChain
- **Vector Store**: ChromaDB
- **Database**: SQLite (SQLAlchemy)
- **Document Processing**: PyPDF, python-pptx, BeautifulSoup4

### Frontend
- **Framework**: Flask (Template Engine)
- **Styling**: Vanilla CSS (Modern design system, glassmorphism)
- **Logic**: Vanilla JavaScript (Async API calls, dynamic UI updates)

---

## 📁 Project Structure

```text
AI_Project/
├── backend/                # Flask API Server
│   ├── routes/             # API Endpoints (Chat, Library, Ingest, Claims)
│   ├── services/           # Business Logic (RAG, Vector Store, LLM)
│   ├── chroma_store/       # Vector Database Persistence
│   ├── uploads/            # Temporary file storage
│   ├── models.py           # Database Schemas
│   └── run.py              # Backend Entry Point
├── frontend/               # UI Server
│   ├── static/             # CSS, JS, Images
│   ├── templates/          # Jinja2 HTML Templates
│   └── app.py              # Frontend Entry Point
├── pyproject.toml          # uv/Python project configuration
└── README.md               # You are here!
```

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.10+
- [Groq API Key](https://console.groq.com/)
- [Google AI API Key](https://aistudio.google.com/)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd AI_Project
   ```

2. **Set up using `uv` (Recommended)**:
   ```bash
   # This will install all dependencies and set up the environment
   uv sync
   ```

3. **Alternative: Manual setup**:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the `backend/` directory:
   ```env
   GROQ_API_KEY=your_groq_key_here
   GOOGLE_API_KEY=your_google_key_here
   CHROMA_PERSIST_DIR=./chroma_store
   UPLOAD_DIR=./uploads
   DATABASE_URL=sqlite:///./study_assistant.db
   FLASK_PORT=5001
   ```

### Running the Application

1. **Start the Backend**:
   ```bash
   cd backend
   python run.py
   ```

2. **Start the Frontend**:
   ```bash
   cd frontend
   python app.py
   ```

3. **Access the App**:
   Open your browser and navigate to `http://localhost:5000` (or the port specified in your frontend config).

---

## 📖 Usage

1. **Upload Documents**: Go to the "Resource Center" to upload PDFs or paste URLs.
2. **Wait for Indexing**: The backend will process the documents and store them in the vector database.
3. **Start Chatting**: Navigate to the Chat screen and ask questions about your documents.
4. **Verify Claims**: Use the Claims module to analyze specific statements within your study materials.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
