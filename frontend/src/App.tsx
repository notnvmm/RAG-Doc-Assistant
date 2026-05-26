import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "http://localhost:8000";

interface Source {
  page: number | string;
  snippet: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setIsUploading(true);
    setUploadStatus("Processing document...");

    try {
      const res = await axios.post(`${API_BASE}/upload`, formData);
      setUploadStatus(
        `✅ ${res.data.message} (${res.data.chunks_created} chunks created)`
      );
    } catch (err: any) {
      setUploadStatus(`❌ Upload failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setIsLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/ask`, { question });
      const assistantMessage: Message = {
        role: "assistant",
        content: res.data.answer,
        sources: res.data.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${err.response?.data?.detail || "Something went wrong"}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>📄 Document Q&A</h1>
        <p>Upload a PDF and ask questions about it</p>
      </header>

      {/* Upload Section */}
      <div className="upload-section">
        <label className="upload-btn">
          {isUploading ? "Processing..." : "📎 Upload PDF"}
          <input
            type="file"
            accept=".pdf"
            onChange={handleUpload}
            disabled={isUploading}
            style={{ display: "none" }}
          />
        </label>
        {uploadStatus && <p className="upload-status">{uploadStatus}</p>}
      </div>

      {/* Chat Window */}
      <div className="chat-window">
        {messages.length === 0 && (
          <div className="placeholder">
            Upload a document, then ask anything about it!
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="bubble">{msg.content}</div>
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                <strong>Sources:</strong>
                {msg.sources.map((s, j) => (
                  <div key={j} className="source-item">
                    Page {s.page}: "{s.snippet}"
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="bubble loading">Thinking...</div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="input-row">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="Ask a question about your document..."
          disabled={isLoading}
        />
        <button onClick={handleAsk} disabled={isLoading || !question.trim()}>
          Ask
        </button>
      </div>
    </div>
  );
}

export default App;