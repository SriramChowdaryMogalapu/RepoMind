// frontend/src/app/page.tsx
import React from 'react';
import { Header } from '@/components/Header';
import { RepositoryInput } from '@/components/RepositoryInput';
import { Search, ShieldCheck, FileCode2, Sparkles } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col bg-zinc-950 text-white">
      <Header />

      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16 text-center max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-xs font-medium mb-6">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Grounded Code Intelligence & Hybrid RAG</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight mb-6 bg-gradient-to-r from-white via-zinc-200 to-zinc-400 bg-clip-text text-transparent">
          Understand any public GitHub repository using AI
        </h1>

        <p className="text-base sm:text-lg text-zinc-400 max-w-2xl mb-10 leading-relaxed">
          Index source files, explore structural chunks, and ask natural-language questions.
          Every answer is strictly grounded in the codebase with clickable line citations.
        </p>

        <div className="w-full mb-12">
          <RepositoryInput />
        </div>

        {/* Feature Highlights with Lucide Icons */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full text-left mt-8">
          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-3">
              <Search className="w-4 h-4" />
            </div>
            <h3 className="font-semibold text-sm text-zinc-200 mb-1">Hybrid Retrieval</h3>
            <p className="text-xs text-zinc-500 leading-relaxed">
              Combines semantic vector embeddings with exact symbol matching via Reciprocal Rank Fusion.
            </p>
          </div>

          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-3">
              <FileCode2 className="w-4 h-4" />
            </div>
            <h3 className="font-semibold text-sm text-zinc-200 mb-1">Verified Citations</h3>
            <p className="text-xs text-zinc-500 leading-relaxed">
              Direct source links pointing directly to the exact file line ranges on GitHub.
            </p>
          </div>

          <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40">
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 mb-3">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <h3 className="font-semibold text-sm text-zinc-200 mb-1">Anti-Injection Guardrails</h3>
            <p className="text-xs text-zinc-500 leading-relaxed">
              Treats repository code as unprivileged data to protect against prompt injection attempts.
            </p>
          </div>
        </div>
      </main>

      <footer className="py-6 border-t border-zinc-900 text-center text-xs text-zinc-600">
        RepoMind — AI Codebase Intelligence & RAG Platform
      </footer>
    </div>
  );
}