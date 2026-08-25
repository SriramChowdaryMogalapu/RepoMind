// frontend/src/components/FileTree.tsx
'use client';

import React, { useState } from 'react';
import { ChevronRight, ChevronDown, FileCode2, Folder, FolderOpen, Tag } from 'lucide-react';

interface FileNode {
  path: string; // Full relative path: 'backend/app/main.py'
  name: string; // Short name: 'main.py'
  type: 'file' | 'dir';
  children?: FileNode[];
}

interface FileTreeProps {
  files: string[];
  activeFile?: string | null;
  onFileClick: (path: string) => void;
  onFileTag: (path: string) => void;
}

export const FileTree: React.FC<FileTreeProps> = ({ files, activeFile, onFileClick, onFileTag }) => {
  const buildTree = (paths: string[]): FileNode[] => {
    const root: { [key: string]: any } = {};

    paths.forEach((fullPath) => {
      const parts = fullPath.split('/');
      let current = root;
      parts.forEach((part, index) => {
        if (!current[part]) {
          current[part] = index === parts.length - 1 
            ? { __fullPath: fullPath, __type: 'file' } 
            : { __type: 'dir', __children: {} };
        }
        if (index < parts.length - 1) {
          current = current[part].__children;
        }
      });
    });

    const formatTree = (obj: any): FileNode[] => {
      return Object.keys(obj).map((key) => {
        if (obj[key].__type === 'file') {
          return {
            path: obj[key].__fullPath,
            name: key,
            type: 'file',
          };
        }
        return {
          path: key,
          name: key,
          type: 'dir',
          children: formatTree(obj[key].__children),
        };
      });
    };

    return formatTree(root);
  };

  const treeData = buildTree(files);

  return (
    <div className="flex h-full min-h-0 flex-col bg-zinc-950 border-r border-zinc-800 select-none text-xs">
      <div className="px-4 py-3 border-b border-zinc-800 flex items-center justify-between text-zinc-400 font-medium">
        <span>Files ({files.length})</span>
          <span className="text-[10px] text-zinc-500">{activeFile ? 'Viewing file' : 'Click a file to view'}</span>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto p-2 space-y-0.5">
        {treeData.map((node, i) => (
          <TreeNodeItem key={i} node={node} activeFile={activeFile} onFileClick={onFileClick} onFileTag={onFileTag} />
        ))}
      </div>
    </div>
  );
};

const TreeNodeItem: React.FC<{
  node: FileNode;
  activeFile?: string | null;
  onFileClick: (path: string) => void;
  onFileTag: (path: string) => void;
}> = ({ node, activeFile, onFileClick, onFileTag }) => {
  const [isOpen, setIsOpen] = useState(true);

  if (node.type === 'dir') {
    return (
      <div>
        <div
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-1.5 px-2 py-1.5 rounded-md hover:bg-zinc-900 cursor-pointer text-zinc-300 transition"
        >
          {isOpen ? <ChevronDown className="w-3.5 h-3.5 text-zinc-500" /> : <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />}
          {isOpen ? <FolderOpen className="w-3.5 h-3.5 text-blue-400" /> : <Folder className="w-3.5 h-3.5 text-blue-400" />}
          <span className="font-medium truncate">{node.name}</span>
        </div>
        {isOpen && node.children && (
          <div className="pl-3.5 border-l border-zinc-800/80 ml-3 space-y-0.5 mt-0.5">
            {node.children.map((child, idx) => (
              <TreeNodeItem key={idx} node={child} activeFile={activeFile} onFileClick={onFileClick} onFileTag={onFileTag} />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      draggable
      onDragStart={(e) => {
        e.dataTransfer.setData('text/plain', node.path);
        e.dataTransfer.effectAllowed = 'copy';
      }}
      onClick={() => {
        onFileClick(node.path);
      }}
      className={`group flex items-center justify-between rounded-md border px-2 py-1.5 transition cursor-pointer ${
        activeFile === node.path
          ? 'border-blue-500/30 bg-blue-500/10 text-blue-100'
          : 'border-transparent text-zinc-400 hover:bg-zinc-800/80 hover:text-zinc-100'
      }`}
      title={`Click to view ${node.path}`}
    >
      <div className="flex items-center gap-2 truncate">
        <FileCode2 className={`w-3.5 h-3.5 shrink-0 ${activeFile === node.path ? 'text-blue-400' : 'text-zinc-500 group-hover:text-blue-400'}`} />
        <span className="truncate font-mono text-[11px]">{node.name}</span>
      </div>
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          onFileTag(node.path);
        }}
        className="opacity-0 group-hover:opacity-100 hover:bg-blue-600/30 p-1 rounded text-blue-400 transition"
        title="Tag file in chat context"
      >
        <Tag className="w-3 h-3" />
      </button>
    </div>
  );
};