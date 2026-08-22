// frontend/src/components/Header.tsx
import React from 'react';
import Link from 'next/link';

export const Header: React.FC = () => {
  return (
    <header className="w-full border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 hover:opacity-90 transition">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white text-lg">
            🧠
          </div>
          <span className="font-bold text-lg text-white tracking-tight">RepoMind</span>
        </Link>

        <nav className="flex items-center gap-6 text-sm">
          <Link href="https://github.com" target="_blank" className="text-zinc-400 hover:text-white transition">
            GitHub
          </Link>
          <Link
            href="/docs"
            className="px-3 py-1.5 rounded-md border border-zinc-700 hover:bg-zinc-800 text-zinc-300 text-xs font-medium transition"
          >
            Documentation
          </Link>
        </nav>
      </div>
    </header>
  );
};