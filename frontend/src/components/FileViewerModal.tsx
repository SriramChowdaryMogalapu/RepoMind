// frontend/src/components/FileViewerModal.tsx
'use client';

import React, { useEffect, useState } from 'react';
import { X, FileCode, Copy, Check, ExternalLink, Loader2 } from 'lucide-react';
import { useRotatingMessage } from './ui/LoadingStates';

interface FileViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  filePath: string | null;
  repositoryId: string;
  githubUrl?: string;
}

export const FileViewerModal: React.FC<FileViewerModalProps> = ({
  isOpen,
  onClose,
  filePath,
  repositoryId,
  githubUrl,
}) => {
  const [content, setContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const loadingMessage = useRotatingMessage([
    'Opening file...',
    'Loading source content...',
    'Formatting code for preview...',
  ], 1400);

  useEffect(() => {
    if (isOpen && filePath && repositoryId) {
      fetchFileContent(filePath);
    } else {
      setContent('');
    }
  }, [isOpen, filePath, repositoryId]);

  const fetchFileContent = async (path: string) => {
    setIsLoading(true);
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const cleanPath = path.replace(/^\/+/, ''); // Trim leading slashes
      const res = await fetch(
        `${baseUrl}/repositories/${repositoryId}/files/content?path=${encodeURIComponent(cleanPath)}`
      );
      if (res.ok) {
        const data = await res.json();
        setContent(data.content || '// Empty file');
      } else {
        setContent(`// Unable to preview file: ${path}\n// Chunks for this file were not found in the database.`);
      }
    } catch (err) {
      setContent(`// Failed to load file: ${path}\n// Error contacting backend server.`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (!content) return;
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen || !filePath) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <div 
        className="w-full max-w-4xl h-[85vh] bg-zinc-950 border border-zinc-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-800 bg-zinc-900/70">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <FileCode className="w-4 h-4" />
            </div>
            <span className="text-sm font-mono font-medium text-zinc-200 truncate">{filePath}</span>
          </div>

          <div className="flex items-center gap-2">
            {githubUrl && (
              <a
                href={githubUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition text-xs flex items-center gap-1"
                title="View on GitHub"
              >
                <ExternalLink className="w-4 h-4" />
              </a>
            )}
            <button
              onClick={handleCopy}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
              title="Copy"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-zinc-400" />}
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800 transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Code Content */}
        <div className="flex-1 overflow-auto p-4 bg-zinc-950 font-mono text-xs text-zinc-300 leading-relaxed select-text">
          {isLoading ? (
            <div className="h-full flex flex-col items-center justify-center gap-3 text-zinc-500">
              <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
              <span aria-live="polite">{loadingMessage}</span>
            </div>
          ) : (
            <pre className="whitespace-pre">
              {content.split('\n').map((line, idx) => (
                <div key={idx} className="table-row hover:bg-zinc-900/50">
                  <span className="table-cell pr-4 text-right select-none text-zinc-600 w-10 text-[11px]">
                    {idx + 1}
                  </span>
                  <span className="table-cell">{line || ' '}</span>
                </div>
              ))}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};