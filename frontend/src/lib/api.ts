// frontend/src/lib/api.ts
import { Repository, FileItem, ChatResponse } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function createRepository(url: string): Promise<Repository> {
  const normalizedApiBase = `${API_BASE.replace(/(\/api\/v1)+\/?$/, '')}/api/v1`;
  const res = await fetch(`${normalizedApiBase}/repositories`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || 'Failed to submit repository.');
  return data;
}

export async function getRepository(repoId: string): Promise<Repository> {
  const normalizedApiBase = `${API_BASE.replace(/(\/api\/v1)+\/?$/, '')}/api/v1`;
  const res = await fetch(`${normalizedApiBase}/repositories/${repoId}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || 'Repository not found.');
  return data;
}

export async function triggerIndexing(repoId: string): Promise<void> {
  const normalizedApiBase = `${API_BASE.replace(/(\/api\/v1)+\/?$/, '')}/api/v1`;
  const res = await fetch(`${normalizedApiBase}/repositories/${repoId}/index`, {
    method: 'POST',
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error?.message || 'Failed to trigger indexing.');
  }
}

export async function getRepositoryFiles(repoId: string): Promise<FileItem[]> {
  const normalizedApiBase = `${API_BASE.replace(/(\/api\/v1)+\/?$/, '')}/api/v1`;
  const res = await fetch(`${normalizedApiBase}/repositories/${repoId}/files`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || 'Failed to load file list.');
  return data.files || [];
}

export async function sendChatMessage(repoId: string, question: string): Promise<ChatResponse> {
  const normalizedApiBase = `${API_BASE.replace(/(\/api\/v1)+\/?$/, '')}/api/v1`;
  const res = await fetch(`${normalizedApiBase}/repositories/${repoId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: 6 }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || 'Failed to process question.');
  return data;
}