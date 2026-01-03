'use client';
import { useState, useRef, useEffect } from 'react';
import { Send, Mic, Paperclip, StopCircle, Menu, X, Monitor, Image as ImageIcon, Search as SearchIcon, GraduationCap, Phone } from 'lucide-react';
import Sidebar from './components/Sidebar';

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

// Web Speech API types
declare global {
  interface Window {
    webkitSpeechRecognition: any;
  }
}

export default function Home() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [models, setModels] = useState<any[]>([]);
  const [currentModel, setCurrentModel] = useState('llama3.2:1b');
  const [isContinuousMode, setIsContinuousMode] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);

  // Ref to track continuous mode inside useEffect/callbacks
  const isContinuousModeRef = useRef(isContinuousMode);

  // Update ref when state changes
  useEffect(() => {
    isContinuousModeRef.current = isContinuousMode;
  }, [isContinuousMode]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Ref to hold utterance to prevent GC
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const isSpeakingRef = useRef(false);

  const speak = (text: string, onEnd?: () => void) => {
    if ('speechSynthesis' in window) {
      // 1. STOP LISTENING IMMEDIATELY to prevent Echo
      if (recognitionRef.current) {
        try { recognitionRef.current.abort(); } catch (e) { }
      }
      setIsListening(false);
      isSpeakingRef.current = true;

      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utteranceRef.current = utterance;

      // 2. FORCE ENGLISH VOICE (Fixes "Female/Another Language" bug)
      const voices = window.speechSynthesis.getVoices();
      // Priority: Google US English > Microsoft David > Any en-US > Any English > First
      const preferredVoice = voices.find(v => v.name === 'Google US English') ||
        voices.find(v => v.name.includes('Microsoft David')) ||
        voices.find(v => v.lang === 'en-US') ||
        voices.find(v => v.lang.startsWith('en')) ||
        voices[0];

      if (preferredVoice) {
        utterance.voice = preferredVoice;
        utterance.lang = 'en-US'; // Explicitly set lang
      }

      utterance.onend = () => {
        utteranceRef.current = null;
        isSpeakingRef.current = false;

        if (onEnd) onEnd();

        // 3. SAFETY DELAY (Fixes "Hearing own input")
        // Wait 800ms for system audio to clear before uncorking mic
      };

      window.speechSynthesis.speak(utterance);
    } else {
      if (onEnd) onEnd();
    }
  };

  // Background Audio Keep-Alive
  // Browsers often pause SpeechSynthesis when the tab is hidden. 
  // Calling resume() periodically helps prevent this.
  useEffect(() => {
    const interval = setInterval(() => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        if (window.speechSynthesis.paused || window.speechSynthesis.pending) {
          window.speechSynthesis.resume();
        }
      }
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize Speech Recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        // IGNORE if we are speaking (Double safety)
        if (isSpeakingRef.current) return;

        const transcript = event.results[0][0].transcript;
        // If continuous mode, we don't just set input, we submit!
        if (isContinuousModeRef.current) {
          // We pass the transcript directly to handleSubmit
          handleSubmit(undefined, transcript);
        } else {
          setInput(prev => prev + (prev ? ' ' : '') + transcript);
        }
        setIsListening(false);
      };

      recognition.onerror = (event: any) => {
        if (event.error === 'no-speech' && isContinuousModeRef.current && !isSpeakingRef.current) {
          setIsListening(false);
          return;
        }
        // Expected errors when we manually abort/stop, or network hiccups
        if (event.error === 'aborted' || event.error === 'not-allowed' || event.error === 'network') {
          setIsListening(false);
          return;
        }
        console.error('Speech recognition error', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
        // Restart loop ONLY if: Continuous Mode AND Not Speaking
        if (isContinuousModeRef.current && !isSpeakingRef.current) {
          setTimeout(() => {
            // Redundant check before starting
            if (!isSpeakingRef.current && recognitionRef.current) {
              try { recognitionRef.current.start(); setIsListening(true); } catch (e) { }
            }
          }, 500);
        }
      };

      recognitionRef.current = recognition;
    }

    // Dynamic API Base URL
    const getApiBaseUrl = () => {
      if (typeof window === 'undefined') return 'http://localhost:8000'; // Server side fallback
      return `http://${window.location.hostname}:8000`;
    };
    const API_BASE_URL = getApiBaseUrl();

    // Fetch Models
    fetch(`${API_BASE_URL}/models`)
      .then(res => res.json())
      .then(data => {
        if (data.models && data.models.length > 0) {
          setModels(data.models);
          // Default to lighter model if available, safely checking name (property is 'model' in Ollama API)
          const lightModel = data.models.find((m: any) => m?.model?.includes('1b'))?.model || data.models[0].model;
          setCurrentModel(lightModel);
        }
      })
      .catch(console.error);
  }, []);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  const handleSubmit = async (e?: React.FormEvent, overrideText?: string) => {
    if (e) e.preventDefault();

    // Use overrideText if provided, otherwise input
    const textToSend = overrideText !== undefined ? overrideText : input;

    if (!textToSend.trim() || isLoading) return;

    const userMsg = textToSend.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsLoading(true);

    try {
      console.log(`[Chat] Sending message: "${userMsg}" | UserID: ${currentUser?.userId}`);
      const getApiBaseUrl = () => {
        if (typeof window === 'undefined') return 'http://localhost:8000';
        return `http://${window.location.hostname}:8000`;
      };

      const response = await fetch(`${getApiBaseUrl()}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': currentUser?.userId?.toString() || ''
        },
        body: JSON.stringify({ message: userMsg, model: currentModel }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      // Fix for Double Icon: Stop showing "Thinking..." once we start receiving text
      setIsLoading(false);

      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = new TextDecoder().decode(value);
        fullResponse += text;

        setMessages(prev => {
          const newMessages = [...prev];
          // CRITICAL FIX: Create a shallow copy of the object to avoid mutating 'prev' state
          // This prevents double-rendering/duplication in React Strict Mode
          const lastMsgIndex = newMessages.length - 1;
          const lastMsg = { ...newMessages[lastMsgIndex] };
          lastMsg.content += text;
          newMessages[lastMsgIndex] = lastMsg;

          return newMessages;
        });
      }

      if (fullResponse.length < 500) {
        speak(fullResponse, () => {
          if (isContinuousModeRef.current) {
            // Increased delay to 1.5s to absolutely ensure no echo
            setTimeout(() => {
              if (recognitionRef.current) {
                try { recognitionRef.current.start(); setIsListening(true); } catch (e) { }
              }
            }, 1500);
          }
        });
      } else {
        if (isContinuousModeRef.current) {
          setTimeout(() => {
            if (recognitionRef.current) {
              try { recognitionRef.current.start(); setIsListening(true); } catch (e) { }
            }
          }, 2000);
        }
      }

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Is the backend running?' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Mock "Read file"
    const text = await file.text();
    setInput(prev => prev + `\n[Reference: ${file.name}]\n${text}\n`);
  };

  // Handle Enter key
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--background)] text-[var(--foreground)] font-sans">

      {/* Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        onNewChat={() => setMessages([])}
        activeUser={currentUser}
        onUserChange={setCurrentUser}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center relative h-full w-full">

        {/* Top Bar (Mobile/Desktop) */}
        <div className="w-full flex items-center justify-between p-2 md:hidden sticky top-0 z-10 bg-[var(--background)] border-b border-[var(--border-color)]">
          <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">
            <Menu size={20} />
          </button>
          <span className="font-semibold">Current Chat</span>
          <button onClick={() => setMessages([])} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">
            <PlusIcon size={20} />
          </button>
        </div>

        {/* Model Selector (Desktop) */}
        {!isSidebarOpen && (
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="absolute top-4 left-4 p-2 rounded-md hover:bg-[var(--sidebar-hover)] md:block hidden z-20 text-gray-500"
          >
            <Monitor size={20} />
          </button>
        )}

        <div className="w-full h-12 hidden md:flex items-center justify-center border-b border-transparent sticky top-0 z-10">
          <div className="flex items-center gap-2 px-3 py-1 rounded-lg hover:bg-[var(--sidebar-hover)] cursor-pointer transition-colors relative group">
            <select
              value={currentModel}
              onChange={(e) => setCurrentModel(e.target.value)}
              className="appearance-none bg-transparent border-none outline-none font-semibold text-lg cursor-pointer pr-4"
            >
              {models.length > 0 ? (
                models.map((m: any) => (
                  <option key={m.model} value={m.model} className="bg-[var(--background)] text-[var(--foreground)]">
                    {m.model}
                  </option>
                ))
              ) : (
                <option value={currentModel}>{currentModel}</option>
              )}
            </select>
            <div className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6" /></svg>
            </div>
            <span className="text-gray-400 text-sm ml-2">Local</span>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 w-full overflow-y-auto w-full relative scroll-smooth">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-4 pb-32">
              <div className="bg-white p-4 rounded-full mb-6 shadow-sm dark:bg-gray-700">
                <Monitor size={32} className="text-gray-400 dark:text-gray-200" />
              </div>
              <h2 className="text-2xl font-semibold mb-8">How can I help you today?</h2>

              <div className="grid grid-cols-2 gap-4 max-w-2xl w-full">
                <CapabilityCard icon={<ImageIcon size={20} className="text-purple-500" />} title="Create image" subtitle="Generate a painting" onClick={() => setInput("Create an image of ")} />
                <CapabilityCard icon={<GraduationCap size={20} className="text-orange-500" />} title="Study" subtitle="Prepare for exam" onClick={() => setInput("Help me study for ")} />
                <CapabilityCard icon={<SearchIcon size={20} className="text-blue-500" />} title="Search" subtitle="Latest news" onClick={() => setInput("Search for ")} />
                <CapabilityCard icon={<Monitor size={20} className="text-green-500" />} title="Coding" subtitle="Refactor code" onClick={() => setInput("Can you refactor this code? ")} />
              </div>
            </div>
          ) : (
            <div className="flex flex-col w-full pb-32">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`w-full py-6 px-4 flex justify-center ${msg.role === 'assistant'
                    ? 'bg-[var(--bot-msg-bg)] border-b border-black/5 dark:border-white/5'
                    : 'bg-[var(--background)]'
                    }`}
                >
                  <div className="w-full max-w-3xl flex gap-4 md:gap-6">
                    <div className="flex-shrink-0 flex flex-col relative items-end">
                      <div className={`w-8 h-8 rounded-sm flex items-center justify-center ${msg.role === 'assistant' ? 'bg-[#19c37d]' : 'bg-[#5436DA]'}`}>
                        {msg.role === 'assistant' ? <Monitor size={20} className="text-white" /> : <span className="text-white text-xs">U</span>}
                      </div>
                    </div>
                    <div className="relative flex-1 overflow-hidden">
                      <div className="prose dark:prose-invert max-w-full leading-7 text-sm md:text-base">
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="w-full py-6 px-4 flex justify-center bg-[var(--bot-msg-bg)]">
                  <div className="w-full max-w-3xl flex gap-4 md:gap-6">
                    <div className="w-8 h-8 rounded-sm bg-[#19c37d] flex items-center justify-center">
                      <Monitor size={20} className="text-white" />
                    </div>
                    <div className="flex items-center">
                      <span className="typing-cursor ml-2"></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} className="h-4" />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 w-full p-4 bg-gradient-to-t from-[var(--background)] via-[var(--background)] to-transparent pt-10">
          <div className="max-w-3xl mx-auto">
            <div className="relative flex items-end w-full p-3 bg-[var(--input-bg)] border border-[var(--border-color)] rounded-xl shadow-xs overflow-hidden ring-offset-2 focus-within:ring-2 ring-blue-500/50 transition-all">
              {/* Attach Button */}
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                onChange={handleFileChange}
                accept=".txt,.md,.py,.json"
              />
              <button
                onClick={handleAttachClick}
                className="p-2 mr-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
              >
                <Paperclip size={20} />
              </button>

              {/* Textarea */}
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message ChatGPT..."
                rows={1}
                className="w-full max-h-[200px] py-2 bg-transparent border-none outline-none resize-none text-base m-0 scrollbar-hide"
                style={{ minHeight: '24px' }}
              />

              {/* Right Actions */}
              <div className="flex items-center gap-2 ml-2">
                {/* Continuous Mode Toggle */}
                <button
                  onClick={() => {
                    const newMode = !isContinuousMode;
                    setIsContinuousMode(newMode);
                    if (newMode) {
                      // Turning ON
                      if (!isListening) {
                        recognitionRef.current?.start();
                        setIsListening(true);
                      }
                    } else {
                      // Turning OFF - STOP EVERYTHING
                      if ('speechSynthesis' in window) window.speechSynthesis.cancel();
                      recognitionRef.current?.stop();
                      setIsListening(false);
                    }
                  }}
                  className={`p-2 rounded-md transition-colors mr-1 ${isContinuousMode ? 'bg-green-100 text-green-600 dark:bg-green-900/30' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-200'}`}
                  title={isContinuousMode ? "Disable Continuous Voice" : "Enable Continuous Voice"}
                >
                  <Phone size={20} className={isContinuousMode ? "fill-current" : ""} />
                </button>

                {/* Voice Button */}
                <button
                  onClick={toggleListening}
                  className={`p-2 rounded-md transition-colors ${isListening ? 'bg-red-500 text-white animate-pulse' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-200'}`}
                >
                  {isListening ? <StopCircle size={20} /> : <Mic size={20} />}
                </button>

                {/* Send Button */}
                <button
                  onClick={() => handleSubmit()}
                  disabled={!input.trim() && !isLoading}
                  className={`p-2 rounded-md transition-all ${input.trim()
                    ? 'bg-[#19c37d] text-white shadow-md'
                    : 'bg-transparent text-gray-400 cursor-not-allowed'
                    }`}
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
            <div className="text-center text-xs text-gray-500 mt-2">
              ChatGPT can make mistakes. Consider checking important information.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PlusIcon({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
  )
}

function CapabilityCard({ icon, title, subtitle, onClick }: { icon: React.ReactNode, title: string, subtitle: string, onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-start p-4 border border-[var(--border-color)] rounded-xl hover:bg-[var(--sidebar-hover)] transition-colors text-left"
    >
      <div className="mb-2">{icon}</div>
      <div className="font-semibold text-sm">{title}</div>
      <div className="text-xs text-gray-500">{subtitle}</div>
    </button>
  )
}
