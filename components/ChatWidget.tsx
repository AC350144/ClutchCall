import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';

type Message = {
  id: string;
  sender: 'user' | 'bot';
  text: string;
};

function formatBotMessage(text: string) {
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
  
  const withBreaks = escaped
    .replace(/&lt;br\s*\/?&gt;/gi, '\n')
    .replace(/&lt;b&gt;(.*?)&lt;\/b&gt;/gi, '**$1**');
  
  return withBreaks.split('\n').map((line, i) => (
    <span key={i}>
      {line.includes('**') 
        ? line.split(/\*\*(.*?)\*\*/).map((part, j) => 
            j % 2 === 1 ? <strong key={j} className="text-green-400">{part}</strong> : part
          )
        : line}
      {i < withBreaks.split('\n').length - 1 && <br />}
    </span>
  ));
}

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'bot',
      text: "Hey there! I'm your AI Financial Assistant. Type help to see what I can do."
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: input.trim()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input.trim() })
      });
      const data = await res.json();

      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: data.response || 'No response received.'
      }]);
    } catch {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: 'Sorry, something went wrong. Try again.'
      }]);
    } finally {
      setLoading(false);
    }
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-full shadow-lg hover:shadow-xl hover:scale-105 transition-all flex items-center justify-center z-50"
      >
        <MessageCircle className="w-6 h-6 text-white" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-[380px] h-[520px] bg-gradient-to-b from-slate-800 to-slate-900 rounded-2xl shadow-2xl border border-slate-700 flex flex-col overflow-hidden z-50">
      <div className="flex items-center gap-3 p-4 border-b border-slate-700 bg-gradient-to-r from-slate-800 to-slate-900">
        <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center">
          <MessageCircle className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-white font-semibold flex items-center gap-2">
            ClutchCall
            <span className="text-[10px] bg-gradient-to-r from-purple-500 to-violet-600 px-1.5 py-0.5 rounded font-semibold">AI</span>
          </h3>
          <p className="text-slate-400 text-xs">Financial Assistant</p>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="w-8 h-8 rounded-lg hover:bg-slate-700 flex items-center justify-center transition-colors"
        >
          <X className="w-4 h-4 text-slate-400" />
        </button>
      </div>

      {/*messages */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`max-w-[85%] p-3 rounded-xl text-sm leading-relaxed ${
              msg.sender === 'user'
                ? 'ml-auto bg-gradient-to-br from-green-500 to-green-600 text-white rounded-br-sm'
                : 'bg-slate-700 text-slate-200 border border-slate-600 rounded-bl-sm'
            }`}
          >
            {msg.sender === 'user' ? msg.text : formatBotMessage(msg.text)}
          </div>
        ))}
        {loading && (
          <div className="bg-slate-700 border border-slate-600 rounded-xl rounded-bl-sm p-3 max-w-[60px]">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/*input box */}
      <div className="p-4 border-t border-slate-700 bg-slate-900 flex gap-3">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Ask me anything..."
          className="flex-1 bg-slate-800 border border-slate-600 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-green-500 focus:ring-1 focus:ring-green-500/20 transition-all"
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl px-4 py-3 font-semibold text-sm hover:shadow-lg hover:shadow-green-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          Send
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
