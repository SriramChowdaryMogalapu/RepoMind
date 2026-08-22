// frontend/src/types/repository.ts
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