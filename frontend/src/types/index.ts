// frontend/src/types/index.ts
export type RepositoryStatus = 'PENDING' | 'CLONING' | 'PARSING' | 'EMBEDDING' | 'READY' | 'FAILED';

export interface Repository {
  id: string;
  owner: string;
  name: string;
  full_name: string;
  url: string;
  default_branch: string;
  description?: string;
  language?: string;
  stars: number;
  forks: number;
  status: RepositoryStatus;
  error_message?: string;
  file_count: number;
  chunk_count: number;
  indexed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface FileItem {
  id: string;
  path: string;
  language?: string;
  size_bytes: number;
}

export interface SourceCitation {
  file_path: string;
  start_line: number;
  end_line: number;
  symbol_name?: string;
  language?: string;
  github_url: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceCitation[];
  confidence?: string;
  timestamp: string;
}

export interface ChatResponse {
  repository_id: string;
  question: string;
  answer: string;
  sources: SourceCitation[];
  confidence: string;
  model_name: string;
}