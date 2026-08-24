// frontend/src/components/ui/LoadingStates.tsx
import React from 'react';
import { Loader2, Sparkles, FileCode, CheckCircle2 } from 'lucide-react';

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
  return (
    <div className="p-5 rounded-xl border border-zinc-800/80 bg-zinc-900/30 space-y-3 animate-pulse">
      <div className="flex items-center gap-2 text-xs text-blue-400">
        <Sparkles className="w-4 h-4 animate-spin" />
        <span>Searching AST embeddings & grounding response...</span>
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