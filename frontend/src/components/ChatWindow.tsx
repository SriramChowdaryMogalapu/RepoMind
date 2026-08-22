// frontend/src/components/ChatWindow.tsx
'use client';

import React, { useState } from 'react';
import { ChatMessage } from '@/types';
import { sendChatMessage } from '@/lib/api';
import { SourceCitationList } from './SourceCitation';

interface Props {
  repoId: string;
}

const SAMPLE_QUESTIONS = [
  'How does authentication work?',
  'Where is the main entry point of this application?',
  'What are the core database models and relationships?',
  'How does the codebase handle errors and logging?',
];

export const ChatWindow: React.FC<Props> = ({ repoId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: textToSend,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const resp = await sendChatMessage(repoId, textToSend);
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: resp.answer,
        sources: resp.sources,
        confidence: resp.confidence,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${err.message || 'Unable to retrieve answer.'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-zinc-950 rounded-lg border border-zinc-800">
      {/* Message History */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
            <h3 className="text-lg font-medium text-zinc-300">Ask anything about this repository</h3>
            <p className="text-xs text-zinc-500 max-w-md">
              Answers are grounded strictly in the indexed source code and include line citations.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg mt-2">
              {SAMPLE_QUESTIONS.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(q)}
                  className="p-2.5 text-left text-xs bg-zinc-900 hover:bg-zinc-800/80 border border-zinc-800 hover:border-zinc-700 rounded-md text-zinc-400 hover:text-zinc-200 transition"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m) => (
            <div
              key={m.id}
              className={`p-4 rounded-lg text-sm ${
                m.role === 'user'
                  ? 'bg-blue-600/10 border border-blue-900/50 text-blue-100 ml-8'
                  : 'bg-zinc-900/90 border border-zinc-800 text-zinc-200 mr-8'
              }`}
            >
              <div className="font-semibold text-xs text-zinc-400 mb-1">
                {m.role === 'user' ? 'You' : 'RepoMind Assistant'}
              </div>
              <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>
              {m.sources && <SourceCitationList citations={m.sources} />}
            </div>
          ))
        )}
        {loading && (
          <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-lg mr-8 animate-pulse text-xs text-zinc-400 flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-blue-500 animate-ping"></span>
            Searching repository and analyzing code...
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="p-3 border-t border-zinc-800 bg-zinc-900/50">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about the repository..."
            disabled={loading}
            className="flex-1 px-3 py-2 bg-zinc-900 border border-zinc-700 rounded-md text-sm text-white placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-500 text-white text-sm font-medium rounded-md transition"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};