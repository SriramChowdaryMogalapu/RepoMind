// frontend/src/lib/api.ts
import { Repository, FileItem, ChatResponse } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function createRepository(url: string): Promise<Repository> {
  const res = await fetch(`${API_BASE}/repositories`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || 'Failed to submit repository.');
  return data;
}

export async function getRepository(repoId: string): Promise<Repository> {
  const res = await fetch(`${API_BASE}/repositories/${repoId}`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || 'Repository not found.');
  return data;
}

export async function triggerIndexing(repoId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/index`, {
    method: 'POST',
  });
  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error?.message || 'Failed to trigger indexing.');
  }
}

export async function getRepositoryFiles(repoId: string): Promise<FileItem[]> {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/files`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || 'Failed to load file list.');
  return data.files || [];
}

export async function sendChatMessage(repoId: string, question: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: 6 }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error?.message || 'Failed to process question.');
  return data;
}