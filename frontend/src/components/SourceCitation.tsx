// frontend/src/components/SourceCitation.tsx
'use client';

import React from 'react';
import { SourceCitation as CitationType } from '@/types';

interface Props {
  citations: CitationType[];
}

export const SourceCitationList: React.FC<Props> = ({ citations }) => {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-zinc-800 text-xs">
      <p className="font-semibold text-zinc-400 mb-2 uppercase tracking-wider text-[11px]">
        Referenced Code Sources ({citations.length})
      </p>
      <div className="flex flex-wrap gap-2">
        {citations.map((c, idx) => (
          <a
            key={idx}
            href={c.github_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-2.5 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 hover:border-zinc-600 rounded text-blue-400 hover:text-blue-300 font-mono transition"
          >
            <span>📄</span>
            <span className="truncate max-w-[200px]">{c.file_path}</span>
            <span className="text-zinc-500">
              L{c.start_line}{c.start_line !== c.end_line ? `-L${c.end_line}` : ''}
            </span>
          </a>
        ))}
      </div>
    </div>
  );
};