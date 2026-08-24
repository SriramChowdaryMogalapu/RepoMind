// frontend/src/components/ChatPanel.tsx
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Send, FileText, X, Sparkles, ExternalLink, Bot, User, Check, Tag } from 'lucide-react';
import { ChatSkeletonLoader } from './ui/LoadingStates';

interface Source {
  file_path: string;
  start_line: int;
  end_line: int;
  symbol_name?: string;
  github_url: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  model?: string;
  tagged_files?: string[];
}

interface ChatPanelProps {
  repositoryId: string;
  availableFiles: string[];
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ repositoryId, availableFiles }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [taggedFiles, setTaggedFiles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Autocomplete dropdown state
  const [showDropdown, setShowDropdown] = useState(false);
  const [filterText, setFilterText] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setInput(val);

    const lastWord = val.split(' ').pop() || '';
    if (lastWord.startsWith('@')) {
      setShowDropdown(true);
      setFilterText(lastWord.slice(1).toLowerCase());
    } else {
      setShowDropdown(false);
    }
  };

  const handleSelectFile = (file: string) => {
    if (!taggedFiles.includes(file)) {
      setTaggedFiles([...taggedFiles, file]);
    }
    // Remove the trailing @searchword
    const words = input.split(' ');
    words.pop();
    setInput(words.join(' ') + (words.length > 0 ? ' ' : ''));
    setShowDropdown(false);
    inputRef.current?.focus();
  };

  const removeTaggedFile = (file: string) => {
    setTaggedFiles(taggedFiles.filter((f) => f !== file));
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      tagged_files: taggedFiles.length > 0 ? [...taggedFiles] : undefined,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/repositories/${repositoryId}/chat`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question: userMessage.content,
            tagged_files: userMessage.tagged_files,
            top_k: 6,
          }),
        }
      );

      const data = await res.json();
      const botMessage: Message = {
        role: 'assistant',
        content: data.answer || 'No response returned.',
        sources: data.sources || [],
        model: data.model_name,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'An error occurred while communicating with the backend.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredFileList = availableFiles.filter((f) =>
    f.toLowerCase().includes(filterText)
  );

  return (
    <div className="flex flex-col h-[650px] rounded-xl border border-zinc-800 bg-zinc-900/40 overflow-hidden">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center text-zinc-500">
            <Bot className="w-10 h-10 mb-2 text-zinc-600" />
            <p className="text-sm font-medium text-zinc-400">Ask any question about this codebase</p>
            <p className="text-xs text-zinc-500 mt-1 max-w-sm">
              Type <code className="text-blue-400 bg-zinc-800 px-1 py-0.5 rounded">@</code> to pin specific files into the context window.
            </p>
          </div>
        )}

        {messages.map((m, idx) => (
          <div key={idx} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.role === 'assistant' && (
              <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-blue-400" />
              </div>
            )}

            <div className={`space-y-2 max-w-[85%] ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
              {/* Tagged files badge */}
              {m.tagged_files && m.tagged_files.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-1">
                  {m.tagged_files.map((file, fIdx) => (
                    <span key={fIdx} className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400">
                      <Tag className="w-2.5 h-2.5" />
                      {file}
                    </span>
                  ))}
                </div>
              )}

              <div className={`p-3.5 rounded-xl text-sm leading-relaxed ${
                m.role === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none'
                  : 'bg-zinc-800/80 border border-zinc-700/60 text-zinc-200 rounded-tl-none'
              }`}>
                <p className="whitespace-pre-wrap">{m.content}</p>
              </div>

              {/* Source citations */}
              {m.sources && m.sources.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {m.sources.map((src, sIdx) => (
                    <a
                      key={sIdx}
                      href={src.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-zinc-950/80 border border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200 text-xs transition"
                    >
                      <FileText className="w-3 h-3 text-blue-400" />
                      <span>{src.file_path}:{src.start_line}-{src.end_line}</span>
                      <ExternalLink className="w-2.5 h-2.5 text-zinc-500" />
                    </a>
                  ))}
                </div>
              )}
            </div>

            {m.role === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-zinc-800 border border-zinc-700 flex items-center justify-center shrink-0">
                <User className="w-4 h-4 text-zinc-400" />
              </div>
            )}
          </div>
        ))}

        {isLoading && <ChatSkeletonLoader />}
      </div>

      {/* Input Bar & File Tags */}
      <div className="p-3 border-t border-zinc-800 bg-zinc-950/60 relative">
        {/* File Autocomplete Suggestions */}
        {showDropdown && filteredFileList.length > 0 && (
          <div className="absolute bottom-full left-3 right-3 mb-2 max-h-48 overflow-y-auto rounded-lg border border-zinc-700 bg-zinc-900 shadow-xl z-50">
            <div className="p-1.5 text-[10px] text-zinc-500 uppercase font-semibold border-b border-zinc-800">
              Pin File into Prompt Context
            </div>
            {filteredFileList.slice(0, 8).map((file, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleSelectFile(file)}
                className="w-full text-left px-3 py-2 text-xs text-zinc-300 hover:bg-blue-600 hover:text-white flex items-center gap-2 transition"
              >
                <FileText className="w-3.5 h-3.5 shrink-0" />
                <span className="truncate">{file}</span>
              </button>
            ))}
          </div>
        )}

        {/* Selected File Chips */}
        {taggedFiles.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-2 px-1">
            {taggedFiles.map((file, idx) => (
              <span key={idx} className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-zinc-800 border border-zinc-700 text-xs text-zinc-200">
                <Tag className="w-3 h-3 text-blue-400" />
                <span className="truncate max-w-[180px]">{file}</span>
                <button
                  type="button"
                  onClick={() => removeTaggedFile(file)}
                  className="hover:text-red-400 transition"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}

        <form onSubmit={handleSend} className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={handleInputChange}
            placeholder="Ask a question or type @ to pin a file..."
            className="flex-1 px-3.5 py-2.5 bg-zinc-900 border border-zinc-700 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-lg text-sm text-white placeholder-zinc-500 outline-none transition"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg text-sm font-medium flex items-center gap-1.5 transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};