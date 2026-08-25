// frontend/src/app/repositories/[id]/page.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Header } from '@/components/Header';
import { FileTree } from '@/components/FileTree';
import { ChatPanel } from '@/components/ChatPanel';
import { FileViewerModal } from '@/components/FileViewerModal';
import { FaGithub } from 'react-icons/fa6';
import { GitBranch, Layers, FileText, CheckCircle2, AlertCircle } from 'lucide-react';

export default function RepositoryDetailPage() {
  const { id } = useParams<{ id: string }>();

  const [repo, setRepo] = useState<any>(null);
  const [files, setFiles] = useState<string[]>([]);
  const [taggedFiles, setTaggedFiles] = useState<string[]>([]);
  const [isLoadingRepo, setIsLoadingRepo] = useState(true);
  const [isLoadingFiles, setIsLoadingFiles] = useState(true);
  
  // Modal state
  const [modalFile, setModalFile] = useState<string | null>(null);
  const [modalGithubUrl, setModalGithubUrl] = useState<string | undefined>(undefined);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    if (id) {
      loadRepoDetails();
      loadRepoFiles();
    }
  }, [id]);

  const loadRepoDetails = async () => {
    setIsLoadingRepo(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/repositories/${id}`);
      if (res.ok) {
        const data = await res.json();
        setRepo(data);
      }
    } catch {
      setRepo(null);
    } finally {
      setIsLoadingRepo(false);
    }
  };

  const loadRepoFiles = async () => {
    setIsLoadingFiles(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/repositories/${id}/files`);
      if (res.ok) {
        const data = await res.json();
        const paths = Array.isArray(data.files)
          ? data.files
              .map((file: unknown) => {
                if (typeof file === 'string') return file;
                if (file && typeof file === 'object' && 'path' in file && typeof file.path === 'string') {
                  return file.path;
                }
                return null;
              })
              .filter((path: string | null): path is string => Boolean(path))
          : [];
        setFiles(paths);
      }
    } catch {
      setFiles([]);
    } finally {
      setIsLoadingFiles(false);
    }
  };

  const handleTriggerIndex = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/repositories/${id}/index`, {
        method: 'POST',
      });
      if (!res.ok) return;

      const initialStatus = await res.json();
      setRepo((currentRepo: any) => ({ ...currentRepo, ...initialStatus }));

      let status = initialStatus.status;
      while (status !== 'READY' && status !== 'FAILED') {
        await new Promise((resolve) => setTimeout(resolve, 7000)); // Poll every 7 seconds
        const statusRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/repositories/${id}/status`);
        if (!statusRes.ok) return;

        const statusData = await statusRes.json();
        status = statusData.status;
        setRepo((currentRepo: any) => ({ ...currentRepo, ...statusData }));
      }

      if (status === 'READY') {
        await loadRepoDetails();
        await loadRepoFiles();
      }
    } catch {}
  };

  const handleOpenFileModal = (path: string, githubUrl?: string) => {
    setModalFile(path);
    setModalGithubUrl(githubUrl);
    setIsModalOpen(true);
  };

  const handleAddTag = (path: string) => {
    if (!taggedFiles.includes(path)) {
      setTaggedFiles([...taggedFiles, path]);
    }
  };

  const handleRemoveTag = (path: string) => {
    setTaggedFiles(taggedFiles.filter((f) => f !== path));
  };

  const isRepositoryReady = repo?.status === 'READY';
  const isLoadingRepositoryContent = isLoadingRepo || (isRepositoryReady && isLoadingFiles);
  const chatStatus = isLoadingRepositoryContent ? 'EMBEDDING' : (repo?.status || 'PENDING');

  return (
    <div className="min-h-screen flex flex-col bg-zinc-950 text-white">
      <Header />

      {/* Repo Top Bar */}
      <div className="border-b border-zinc-800 bg-zinc-900/40 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-zinc-800 text-zinc-300">
            <FaGithub className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-sm text-white tracking-tight">{repo?.name || 'Repository'}</h1>
            <div className="flex items-center gap-3 text-xs text-zinc-400 font-mono mt-0.5">
              <span className="flex items-center gap-1">
                <GitBranch className="w-3 h-3 text-blue-400" />
                {repo?.default_branch || 'main'}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <FileText className="w-3 h-3 text-emerald-400" />
                {repo?.file_count ?? files.length} files
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className={`px-2.5 py-1 rounded-full font-mono text-[11px] border ${
            repo?.status === 'READY'
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
              : 'bg-amber-500/10 border-amber-500/20 text-amber-400'
          }`}>
            {repo?.status || 'PENDING'}
          </span>
        </div>
      </div>

      {/* Main 2-Column Layout */}
      <div className="flex-1 grid h-[calc(100vh-120px)] min-h-0 grid-cols-1 grid-rows-[14rem_minmax(0,1fr)] overflow-hidden md:grid-cols-4 md:grid-rows-1">
        {/* Left Column: File Tree */}
        <div className="min-h-0 overflow-hidden md:col-span-1 md:h-full">
          <FileTree
            files={files}
            activeFile={modalFile}
            onFileClick={(path) => handleOpenFileModal(path)}
            onFileTag={handleAddTag}
          />
        </div>

        {/* Right Column: Chat & Index Action */}
        <div className="md:col-span-3 h-full overflow-hidden">
          <ChatPanel
            repositoryId={id}
            status={chatStatus}
            availableFiles={files}
            taggedFiles={taggedFiles}
            onAddTag={handleAddTag}
            onRemoveTag={handleRemoveTag}
            onOpenFileModal={handleOpenFileModal}
            onTriggerIndex={handleTriggerIndex}
          />
        </div>
      </div>

      {/* Code Viewer Modal */}
      <FileViewerModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        filePath={modalFile}
        repositoryId={id}
        githubUrl={modalGithubUrl}
      />
    </div>
  );
}