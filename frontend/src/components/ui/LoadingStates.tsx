// frontend/src/components/ui/LoadingStates.tsx
import React, { useEffect, useState } from 'react';
import { Loader2, Sparkles, Layers } from 'lucide-react';

export const useRotatingMessage = (messages: string[], interval = 1800) => {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setMessageIndex((current) => (current + 1) % messages.length);
    }, interval);

    return () => window.clearInterval(timer);
  }, [messages.length, interval]);

  return messages[messageIndex];
};

export const IndexingLoader: React.FC = () => {
  const message = useRotatingMessage([
    'Reading repository structure...',
    'Parsing source files and symbols...',
    'Building searchable code context...',
    'Preparing grounded answers...',
  ]);

  return (
    <div className="flex flex-col items-center text-center">
      <div className="relative mb-5 flex h-16 w-16 items-center justify-center rounded-2xl border border-blue-400/30 bg-blue-500/10 text-blue-300 shadow-lg shadow-blue-950/40">
        <Layers className="h-8 w-8" />
        <span className="absolute inset-0 rounded-2xl border border-blue-400/30 animate-ping" />
      </div>
      <h3 className="text-lg font-bold text-white">Preparing your codebase</h3>
      <p className="mt-2 min-h-5 text-sm text-zinc-400" aria-live="polite">{message}</p>
      <div className="mt-6 flex gap-1.5" aria-hidden="true">
        {[0, 1, 2].map((dot) => <span key={dot} className="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-400" style={{ animationDelay: `${dot * 180}ms` }} />)}
      </div>
    </div>
  );
};

export const IndexingProgress: React.FC<{ status: string; fileCount: number; chunkCount: number }> = ({
  status,
  fileCount,
  chunkCount,
}) => {
  return (
    <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/50 backdrop-blur space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
          <div>
            <h4 className="text-sm font-semibold text-zinc-200">Repository Indexing in Progress</h4>
            <p className="text-xs text-zinc-400">Status: <span className="font-mono text-blue-400 uppercase">{status}</span></p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-zinc-400 font-mono">
          <span className="px-2 py-1 bg-zinc-800 rounded">{fileCount} files</span>
          <span className="px-2 py-1 bg-zinc-800 rounded">{chunkCount} chunks</span>
        </div>
      </div>
      
      {/* Animated Pulse Bar */}
      <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 via-indigo-500 to-blue-400 h-full w-full animate-pulse" />
      </div>
    </div>
  );
};

export const ChatSkeletonLoader: React.FC = () => {
  const message = useRotatingMessage([
    'Searching the codebase...',
    'Combining semantic and symbol matches...',
    'Checking the most relevant files...',
    'Writing a grounded response...',
  ], 1600);

  return (
    <div className="p-5 rounded-xl border border-zinc-800/80 bg-zinc-900/30 space-y-3 animate-pulse">
      <div className="flex items-center gap-2 text-xs text-blue-400">
        <Sparkles className="w-4 h-4" />
        <span aria-live="polite">{message}</span>
      </div>
      <div className="h-3 bg-zinc-800 rounded-md w-3/4" />
      <div className="h-3 bg-zinc-800 rounded-md w-full" />
      <div className="h-3 bg-zinc-800 rounded-md w-5/6" />
      <div className="pt-2 flex gap-2">
        <div className="h-6 w-28 bg-zinc-800/60 rounded" />
        <div className="h-6 w-36 bg-zinc-800/60 rounded" />
      </div>
    </div>
  );
};