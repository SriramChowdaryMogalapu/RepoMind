// frontend/src/app/docs/page.tsx
import React from 'react';
import Link from 'next/link';
import { Header } from '@/components/Header';

export default function DocsPage() {
  return (
    <div className="min-h-screen flex flex-col bg-zinc-950 text-white">
      <Header />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-12">
        <div className="mb-8">
          <Link href="/" className="text-xs text-blue-400 hover:text-blue-300 transition inline-flex items-center gap-1 mb-4">
            ← Back to App
          </Link>
          <h1 className="text-3xl font-extrabold tracking-tight mb-2">RepoMind Documentation</h1>
          <p className="text-zinc-400 text-sm">
            Architecture, API reference, and technical workflows for codebase intelligence.
          </p>
        </div>

        <div className="space-y-10 text-sm leading-relaxed text-zinc-300">
          {/* Architecture Overview */}
          <section className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/40">
            <h2 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
              <span>🏗️</span> System Architecture
            </h2>
            <p className="mb-4 text-zinc-400">
              RepoMind ingests public GitHub repositories, builds code-aware vector representations using AST-based chunking, and provides grounded conversational Q&A with direct source file line citations.
            </p>
            <div className="p-4 rounded-lg bg-zinc-950 font-mono text-xs border border-zinc-800 text-zinc-300">
              GitHub Repo → AST / Structural Chunking → Batch Embeddings → pgvector (HNSW) + Keyword Match → Grounded RAG Chat
            </div>
          </section>

          {/* REST API Reference */}
          <section className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/40">
            <h2 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
              <span>📡</span> Core API Endpoints
            </h2>
            <div className="space-y-4">
              <div>
                <div className="flex items-center gap-2 font-mono text-xs mb-1">
                  <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 font-bold">POST</span>
                  <span className="text-white">/api/v1/repositories</span>
                </div>
                <p className="text-xs text-zinc-400">Register a public GitHub repository for indexing.</p>
              </div>

              <div>
                <div className="flex items-center gap-2 font-mono text-xs mb-1">
                  <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold">POST</span>
                  <span className="text-white">/api/v1/repositories/:id/index</span>
                </div>
                <p className="text-xs text-zinc-400">Trigger the background ingestion, chunking, and embedding pipeline.</p>
              </div>

              <div>
                <div className="flex items-center gap-2 font-mono text-xs mb-1">
                  <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 font-bold">POST</span>
                  <span className="text-white">/api/v1/repositories/:id/chat</span>
                </div>
                <p className="text-xs text-zinc-400">Ask a question and receive a grounded answer with line citations.</p>
              </div>
            </div>
          </section>

          {/* Security & Multi-Tier Fallback */}
          <section className="p-6 rounded-xl border border-zinc-800 bg-zinc-900/40">
            <h2 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
              <span>🛡️</span> Security & Multi-Tier Fallback
            </h2>
            <ul className="list-disc list-inside space-y-2 text-xs text-zinc-400">
              <li><strong className="text-zinc-200">No Code Execution:</strong> Repositories are statically parsed via AST; no untrusted code is executed.</li>
              <li><strong className="text-zinc-200">Prompt Injection Defenses:</strong> Code context is encapsulated inside isolated XML boundary tags.</li>
              <li><strong className="text-zinc-200">Multi-Tier AI Resilience:</strong> Transparent fallback routes from Gemini to OpenAI/Groq or offline extraction if API rate limits (HTTP 429) or timeouts occur.</li>
            </ul>
          </section>
        </div>
      </main>

      <footer className="py-6 border-t border-zinc-900 text-center text-xs text-zinc-600">
        RepoMind — AI Codebase Intelligence & RAG Platform
      </footer>
    </div>
  );
}