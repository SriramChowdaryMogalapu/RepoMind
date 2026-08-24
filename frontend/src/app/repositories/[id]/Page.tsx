// frontend/src/app/repositories/[id]/page.tsx
'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

import { Repository, FileItem } from '@/types';
import {
  getRepository,
  getRepositoryFiles,
  triggerIndexing,
} from '@/lib/api';

import { FileTree } from '@/components/FileTree';
import { ChatWindow } from '@/components/ChatWindow';

export default function RepositoryDashboardPage() {
  const params = useParams();
  const repoId = params.id as string;

  const [repo, setRepo] = useState<Repository | null>(null);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchState = useCallback(async () => {
    try {
      setError(null);

      const data = await getRepository(repoId);
      setRepo(data);

      if (data.status === 'READY') {
        const fileList = await getRepositoryFiles(repoId);
        setFiles(fileList);
      }
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to load repository.'
      );
    } finally {
      setLoading(false);
    }
  }, [repoId]);

  // Initial repository fetch
  useEffect(() => {
    fetchState();
  }, [fetchState]);

  // Poll status while indexing
  useEffect(() => {
    if (
      repo &&
      ['PENDING', 'CLONING', 'PARSING', 'EMBEDDING'].includes(repo.status)
    ) {
      const interval = setInterval(() => {
        fetchState();
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [repo, fetchState]);

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-zinc-950 text-zinc-400">
        Loading repository intelligence...
      </div>
    );
  }

  if (error || !repo) {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-zinc-950 text-red-400">
        <p>{error || 'Repository not found'}</p>

        <Link
          href="/"
          className="mt-4 text-sm text-zinc-400 hover:text-white transition"
        >
          ← Back to repositories
        </Link>
      </div>
    );
  }

  const handleStartIndexing = async () => {
    try {
      setError(null);

      await triggerIndexing(repo.id);
      await fetchState();
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to start indexing.'
      );
    }
  };

  return (
    <div className="flex flex-col h-screen bg-zinc-950 text-white font-sans">
      {/* Top Bar Header */}
      <header className="h-14 border-b border-zinc-800 px-4 flex items-center justify-between bg-zinc-900/40">
        <div className="flex items-center gap-3 min-w-0">
          {/* Home / Logo */}
          <Link
            href="/"
            className="font-bold text-lg tracking-tight hover:text-blue-400 transition shrink-0"
          >
            RepoMind
          </Link>

          <span className="text-zinc-600">/</span>

          {/* GitHub Repository */}
          <Link
            href={repo.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-mono text-zinc-300 hover:text-blue-400 flex items-center gap-1.5 min-w-0"
          >
            <span>📦</span>
            <span className="truncate">{repo.full_name}</span>
          </Link>

          {/* Default Branch */}
          <span className="text-xs px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 border border-zinc-700 shrink-0">
            {repo.default_branch}
          </span>
        </div>

        {/* Status / Actions */}
        <div className="flex items-center gap-4 text-xs shrink-0">
          <div className="flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${
                repo.status === 'READY'
                  ? 'bg-emerald-500'
                  : repo.status === 'FAILED'
                    ? 'bg-red-500'
                    : 'bg-amber-500 animate-pulse'
              }`}
            />

            <span className="text-zinc-400">{repo.status}</span>
          </div>

          {repo.status === 'PENDING' && (
            <button
              onClick={handleStartIndexing}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-500 rounded text-xs font-medium transition"
            >
              Start Indexing
            </button>
          )}
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: Repository Explorer & Stats */}
        <aside className="w-80 border-r border-zinc-800 flex flex-col bg-zinc-900/20">
          {/* Metadata Card */}
          <div className="p-4 border-b border-zinc-800 text-xs space-y-2">
            <div className="flex justify-between text-zinc-400">
              <span>Indexed Files:</span>

              <span className="font-mono text-white">
                {repo.file_count}
              </span>
            </div>

            <div className="flex justify-between text-zinc-400">
              <span>Code Chunks:</span>

              <span className="font-mono text-white">
                {repo.chunk_count}
              </span>
            </div>

            <div className="flex justify-between text-zinc-400">
              <span>Primary Language:</span>

              <span className="font-mono text-white">
                {repo.language || 'N/A'}
              </span>
            </div>
          </div>

          {/* File Explorer Tree */}
          <div className="flex-1 p-3 overflow-hidden flex flex-col">
            <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
              Repository Files
            </h4>

            <FileTree files={files} />
          </div>
        </aside>

        {/* Center / Right: Conversational RAG Assistant */}
        <main className="flex-1 p-4 overflow-hidden">
          <ChatWindow repoId={repo.id} />
        </main>
      </div>
    </div>
  );
}