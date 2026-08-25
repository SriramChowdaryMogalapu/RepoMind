// frontend/src/components/ChatPanel.tsx
'use client';

import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, Sparkles, ExternalLink, Bot, User, Tag, X, FileCode, 
  Layers, Play
} from 'lucide-react';
import { ChatSkeletonLoader, IndexingLoader } from './ui/LoadingStates';

interface Source {
  file_path: string;
  start_line: number;
  end_line: number;
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
  status: 'PENDING' | 'INDEXING' | 'COMPLETED' | 'FAILED';
  availableFiles: string[];
  taggedFiles: string[];
  onAddTag: (path: string) => void;
  onRemoveTag: (path: string) => void;
  onOpenFileModal: (path: string, githubUrl?: string) => void;
  onTriggerIndex: () => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  repositoryId,
  status,
  availableFiles,
  taggedFiles,
  onAddTag,
  onRemoveTag,
  onOpenFileModal,
  onTriggerIndex,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  // Autocomplete state
  const [showDropdown, setShowDropdown] = useState(false);
  const [filterQuery, setFilterQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  // Filtered files for autocomplete
  const filteredFiles = availableFiles.filter((f) =>
    f.toLowerCase().includes(filterQuery.toLowerCase())
  );

  const updateMentionState = (value: string, cursorPosition: number) => {
    const textBeforeCursor = value.slice(0, cursorPosition);
    const mentionMatch = textBeforeCursor.match(/(?:^|\s)@([^\s]*)$/);

    if (mentionMatch) {
      setFilterQuery(mentionMatch[1]);
      setSelectedIndex(0);
      setShowDropdown(true);
      return;
    }

    setShowDropdown(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setInput(val);
    updateMentionState(val, e.target.selectionStart ?? val.length);
  };

  const handleSelectFile = (filePath: string) => {
    onAddTag(filePath);

    if (inputRef.current) {
      const cursorPos = inputRef.current.selectionStart ?? input.length;
      const textBeforeCursor = input.slice(0, cursorPos);
      const textAfterCursor = input.slice(cursorPos);
      const mentionMatch = textBeforeCursor.match(/(?:^|\s)@([^\s]*)$/);

      if (mentionMatch && mentionMatch.index !== undefined) {
        const mentionStart = mentionMatch.index + (textBeforeCursor[mentionMatch.index] === ' ' ? 1 : 0);
        const updated = textBeforeCursor.slice(0, mentionStart) + textAfterCursor;
        setInput(updated ? `${updated.trimEnd()} ` : '');
      }
    }

    setShowDropdown(false);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showDropdown || filteredFiles.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % Math.min(filteredFiles.length, 6));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + Math.min(filteredFiles.length, 6)) % Math.min(filteredFiles.length, 6));
    } else if (e.key === 'Enter' && showDropdown) {
      e.preventDefault();
      handleSelectFile(filteredFiles[selectedIndex]);
    } else if (e.key === 'Escape') {
      setShowDropdown(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const droppedPath = e.dataTransfer.getData('text/plain');
    if (droppedPath && availableFiles.includes(droppedPath)) {
      onAddTag(droppedPath);
    }
  };

  const openTaggedFile = (file: string) => {
    onOpenFileModal(file);
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
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer || 'No answer returned.',
          sources: data.sources || [],
          model: data.model_name,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Error connecting to the AI backend.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      className={`relative flex flex-col h-full bg-zinc-900/40 overflow-hidden transition ${
        isDragOver ? 'ring-2 ring-blue-500 bg-blue-950/20' : ''
      }`}
    >
      {/* Indexing Banner */}
      {status === 'PENDING' && (
        <div className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-zinc-950/90 p-6 text-center backdrop-blur-md">
          <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl border border-blue-400/30 bg-blue-500/10 text-blue-300 shadow-lg shadow-blue-950/40">
            <Layers className="h-8 w-8" />
          </div>
          <h3 className="text-lg font-bold text-white">Ready to index repository</h3>
          <p className="mt-2 max-w-md text-sm leading-relaxed text-zinc-400">
            Give RepoMind permission to index this repository for file-grounded Q&amp;A.
          </p>
          <button
            onClick={onTriggerIndex}
            className="mt-6 flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-zinc-950"
          >
            <Play className="h-4 w-4 fill-white" />
            <span>Allow and index repository</span>
          </button>
        </div>
      )}

      {status === 'INDEXING' && (
        <div className="absolute inset-0 z-30 flex items-center justify-center bg-zinc-950/90 p-6 text-center backdrop-blur-md">
          <IndexingLoader />
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-5 space-y-6">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center text-zinc-500 py-12">
            <div className="w-12 h-12 rounded-2xl bg-zinc-800/80 border border-zinc-700/60 flex items-center justify-center mb-3">
              <Sparkles className="w-6 h-6 text-blue-400" />
            </div>
            <h4 className="text-sm font-semibold text-zinc-200">RepoMind Intelligence Chat</h4>
            <p className="text-xs text-zinc-400 mt-1 max-w-sm">
              Type <code className="text-blue-400 bg-zinc-800 px-1 py-0.5 rounded">@</code> to auto-complete and pin files directly to context.
            </p>
          </div>
        )}

        {messages.map((m, idx) => (
          <div key={idx} className={`flex gap-3.5 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.role === 'assistant' && (
              <div className="w-8 h-8 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-blue-400" />
              </div>
            )}

            <div className={`space-y-2 max-w-[80%] ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className="flex items-center gap-2 text-[11px] text-zinc-500 px-1">
                <span className="font-medium text-zinc-300">{m.role === 'user' ? 'You' : 'RepoMind AI'}</span>
                {m.model && <span className="text-[10px] text-zinc-500 font-mono">({m.model})</span>}
              </div>

              {m.tagged_files && m.tagged_files.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {m.tagged_files.map((file, fIdx) => (
                    <button
                      key={fIdx}
                      onClick={() => openTaggedFile(file)}
                      className="inline-flex items-center gap-1.5 text-[11px] px-2.5 py-1 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400 hover:bg-blue-500/20 transition font-mono"
                    >
                      <Tag className="w-3 h-3" />
                      <span>{file}</span>
                    </button>
                  ))}
                </div>
              )}

              <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                m.role === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-none'
                  : 'bg-zinc-800/80 border border-zinc-700/60 text-zinc-200 rounded-tl-none'
              }`}>
                <p className="whitespace-pre-wrap">{m.content}</p>
              </div>

              {m.sources && m.sources.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-1">
                  {m.sources.map((src, sIdx) => (
                    <button
                      key={sIdx}
                      onClick={() => onOpenFileModal(src.file_path, src.github_url)}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-zinc-950 border border-zinc-800 hover:border-zinc-700 text-zinc-400 hover:text-zinc-200 text-xs transition font-mono"
                    >
                      <FileCode className="w-3.5 h-3.5 text-blue-400" />
                      <span>{src.file_path}:{src.start_line}-{src.end_line}</span>
                      <ExternalLink className="w-3 h-3 text-zinc-600" />
                    </button>
                  ))}
                </div>
              )}
            </div>

            {m.role === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 border border-blue-400/40 flex items-center justify-center shrink-0">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        ))}

        {isLoading && <ChatSkeletonLoader />}
      </div>

      {/* Input Form */}
      <div className="p-4 border-t border-zinc-800 bg-zinc-950/80 relative">
        {/* Modern @ Autocomplete Dropdown */}
        {showDropdown && filteredFiles.length > 0 && (
          <div className="absolute bottom-full left-4 right-4 mb-2 max-h-56 overflow-y-auto rounded-xl border border-zinc-700 bg-zinc-900 shadow-2xl z-50">
            <div className="px-3 py-2 text-[10px] text-zinc-400 font-semibold uppercase border-b border-zinc-800 flex justify-between">
              <span>Matching Files</span>
              <span>Use ↑ ↓ to navigate, Enter to pin</span>
            </div>
            {filteredFiles.slice(0, 6).map((file, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleSelectFile(file)}
                className={`w-full text-left px-3 py-2.5 text-xs flex items-center justify-between transition ${
                  selectedIndex === i
                    ? 'bg-blue-600 text-white'
                    : 'text-zinc-300 hover:bg-zinc-800/80'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <FileCode className="w-3.5 h-3.5 shrink-0" />
                  <span className="font-mono truncate">{file}</span>
                </div>
                <span className="text-[10px] opacity-70">Pin</span>
              </button>
            ))}
          </div>
        )}

        {/* Tagged Pills */}
        {taggedFiles.length > 0 && (
          <div className="mb-3 rounded-xl border border-blue-500/20 bg-blue-500/[0.06] p-2.5">
            <div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-wider text-blue-300">
              <Tag className="h-3.5 w-3.5" />
              <span>Files in context</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
            {taggedFiles.map((file, idx) => (
              <div 
                key={idx} 
                className="inline-flex max-w-full items-center gap-1.5 rounded-lg border border-blue-400/30 bg-blue-500/15 px-2.5 py-1.5 text-xs text-blue-200 shadow-sm shadow-blue-950/30"
              >
                <FileCode className="h-3.5 w-3.5 shrink-0 text-blue-300" />
                <button
                  type="button"
                  onClick={() => openTaggedFile(file)}
                  title={`Open ${file}`}
                  className="truncate font-mono hover:text-white hover:underline"
                >
                  {file}
                </button>
                <button
                  type="button"
                  onClick={() => onRemoveTag(file)}
                  aria-label={`Remove ${file} from context`}
                  title="Remove from context"
                  className="hover:text-red-400 transition"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
            </div>
          </div>
        )}

        <form onSubmit={handleSend} className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={handleInputChange}
            onClick={(e) => updateMentionState(e.currentTarget.value, e.currentTarget.selectionStart ?? e.currentTarget.value.length)}
            onKeyUp={(e) => updateMentionState(e.currentTarget.value, e.currentTarget.selectionStart ?? e.currentTarget.value.length)}
            onKeyDown={handleKeyDown}
            disabled={status !== 'COMPLETED'}
            placeholder={
              status === 'COMPLETED'
                ? 'Ask a question, or type @ to pin files into context...'
                : 'Repository must be indexed before chatting.'
            }
            className="flex-1 px-4 py-3 bg-zinc-900/90 border border-zinc-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-xl text-sm text-white placeholder-zinc-500 outline-none transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading || status !== 'COMPLETED'}
            className="px-5 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-xl text-sm font-medium flex items-center gap-2 transition shadow-lg shadow-blue-600/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};