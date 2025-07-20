import { useEffect, useState, useRef } from "react";
import { Sheet, SheetTrigger, SheetContent } from "@/components/ui/sheet";
import { Settings2, Sun, Moon, Clipboard, FileDown } from "lucide-react";
import axios from "axios";
import { TypeAnimation } from "react-type-animation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [theme, setTheme] = useState("light");
  const [isTyping, setIsTyping] = useState(false);
  const [typingContent, setTypingContent] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("chatHistory");
    const storedTheme = localStorage.getItem("theme");
    if (saved) setMessages(JSON.parse(saved));
    if (storedTheme) setTheme(storedTheme);
  }, []);

  useEffect(() => {
    localStorage.setItem("chatHistory", JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("theme", theme);
  }, [theme]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setIsTyping(true);
    setTypingContent("🤖 Qwen is thinking");

    try {
      const res = await axios.post("http://localhost:8000/chat", {
        prompt: {
          model: "Qwen2.5-3B-Instruct",
          temperature: 0,
          max_tokens: 100,
          messages: [
            {
              role: "system",
              content:
                "Bạn là hệ thống phân loại yêu cầu người dùng trong ứng dụng xem nội dung.\n\nNhiệm vụ:\n- Dựa trên câu lệnh người dùng, chọn **DUY NHẤT MỘT nhóm hành động** phù hợp nhất.\n- Trả về đúng định dạng JSON: {\"group\": \"Tên nhóm\"}\n- KHÔNG trả thêm nội dung nào khác.\n\nDanh sách nhóm:\n\n- \"media_control\": Điều khiển phát lại, âm lượng, tua, tạm dừng, tiếp tục, bật/tắt thiết bị.\n- \"content_open\": Mở hoặc hỏi về nội dung: phim, chương trình, video, lịch chiếu.\n- \"query_info\": Câu hỏi thông tin, phản ánh, tìm kiếm, hỏi về phim, gói cước, thời tiết, vàng.\n- \"app_ui\": Điều hướng giao diện ứng dụng, mở YouTube, quay lại trang trước, tắt màn hình.\n\nVí dụ:\n- \"Tăng âm lượng lên\" → {\"group\": \"media_control\"}\n- \"Xem phim Avatar\" → {\"group\": \"content_open\"}\n- \"Không thấy phim yêu thích\" → {\"group\": \"query_info\"}\n- \"Về trang chủ giúp tôi\" → {\"group\": \"app_ui\"}"
            },
            {
              role: "user",
              content: input
            }
          ]
        }
      });
      const output = (res?.data?.response ?? '').trim();
      setTimeout(() => {
        setTypingContent(output);
        setMessages((prev) => [...prev, { role: "assistant", content: output }]);
        setIsTyping(false);
      }, 500);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "⚠️ Lỗi khi gọi API." }
      ]);
      setIsTyping(false);
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1000);
  };

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(messages, null, 2)], {
      type: "application/json"
    });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "chat_history.json";
    link.click();
  };

  return (
    <div className="h-screen w-screen bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 transition-colors flex flex-col">
      <header className="flex justify-between items-center px-4 py-3 shadow dark:shadow-none border-b border-zinc-200 dark:border-zinc-800">
        <h1 className="text-xl font-semibold">Qwen Intent Classifier</h1>
        <div className="flex items-center gap-3">
          <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>{theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}</button>
          <Sheet>
            <SheetTrigger>
              <Settings2 size={18} />
            </SheetTrigger>
            <SheetContent side="right" className="w-72">
              <h2 className="text-lg font-semibold mb-4">⚙️ Settings</h2>
              <div className="space-y-2">
                <button onClick={() => { setMessages([]); localStorage.removeItem("chatHistory"); }} className="w-full bg-zinc-200 dark:bg-zinc-700 py-1 px-2 rounded text-sm">
                  🗑️ Clear Chat
                </button>
                <button onClick={handleExport} className="w-full bg-zinc-200 dark:bg-zinc-700 py-1 px-2 rounded text-sm flex items-center gap-2">
                  <FileDown size={16} /> Export History
                </button>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="space-y-4 mb-6">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] p-3 rounded-lg text-sm whitespace-pre-wrap relative ${m.role === "user" ? "bg-blue-500 text-white" : "bg-zinc-100 dark:bg-zinc-800"}`}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                {m.role === "assistant" && (
                  <button onClick={() => handleCopy(m.content)} className="absolute top-1 right-1 text-xs text-gray-400 hover:text-gray-600">
                    <Clipboard size={14} />
                  </button>
                )}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex justify-start">
              <div className="max-w-[80%] p-3 rounded-lg text-sm whitespace-pre-wrap bg-zinc-100 dark:bg-zinc-800">
                <TypeAnimation
                  sequence={[typingContent + " .", typingContent + " ..", typingContent + " ..."]}
                  wrapper="span"
                  speed={200}
                  repeat={Infinity}
                  cursor={false}
                />
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            className="flex-1 border border-zinc-300 dark:border-zinc-700 bg-transparent rounded px-3 py-2 text-sm outline-none"
            placeholder="Nhập yêu cầu của bạn..."
          />
          <button onClick={sendMessage} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm">
            Send
          </button>
        </div>
      </main>
    </div>
  );
}
