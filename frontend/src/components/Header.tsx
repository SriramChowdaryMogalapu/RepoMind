// frontend/src/components/Header.tsx
import React from 'react';
import Link from 'next/link';
import { Cpu, BookOpen } from 'lucide-react';
import { FaGithub } from 'react-icons/fa6';

export const Header: React.FC = () => {
  return (
    <header className="w-full border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 hover:opacity-90 transition">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-blue-600/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-lg text-white tracking-tight">RepoMind</span>
        </Link>

        <nav className="flex items-center gap-4 text-sm">
          <Link
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-zinc-400 hover:text-white transition px-2.5 py-1.5 rounded-md hover:bg-zinc-900"
          >
            <FaGithub className="w-4 h-4" />
            <span>GitHub</span>
          </Link>
          <Link
            href="/docs"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-zinc-700 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 text-xs font-medium transition"
          >
            <BookOpen className="w-3.5 h-3.5 text-blue-400" />
            <span>Documentation</span>
          </Link>
        </nav>
      </div>
    </header>
  );
};