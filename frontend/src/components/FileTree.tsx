// frontend/src/components/FileTree.tsx
'use client';

import React, { useState } from 'react';
import { FileItem } from '@/types';

interface TreeNode {
  name: string;
  path: string;
  isFile: boolean;
  children: { [key: string]: TreeNode };
  fileData?: FileItem;
}

export const FileTree: React.FC<{ files: FileItem[]; onSelectFile?: (file: FileItem) => void }> = ({
  files,
  onSelectFile,
}) => {
  // Build nested folder structure
  const root: TreeNode = { name: '', path: '', isFile: false, children: {} };

  files.forEach((f) => {
    const parts = f.path.split('/');
    let current = root;
    parts.forEach((part, i) => {
      const isFile = i === parts.length - 1;
      if (!current.children[part]) {
        current.children[part] = {
          name: part,
          path: parts.slice(0, i + 1).join('/'),
          isFile,
          children: {},
          fileData: isFile ? f : undefined,
        };
      }
      current = current.children[part];
    });
  });

  const renderNode = (node: TreeNode, depth: number = 0) => {
    const [open, setOpen] = useState(true);

    if (node.isFile) {
      return (
        <div
          key={node.path}
          style={{ paddingLeft: `${depth * 14}px` }}
          onClick={() => node.fileData && onSelectFile?.(node.fileData)}
          className="flex items-center gap-2 py-1 px-2 hover:bg-zinc-800/60 rounded cursor-pointer text-xs font-mono text-zinc-300 transition"
        >
          <span className="text-zinc-500">📄</span>
          <span className="truncate">{node.name}</span>
        </div>
      );
    }

    const childKeys = Object.keys(node.children).sort();

    return (
      <div key={node.path || 'root'} className="select-none">
        {node.name && (
          <div
            style={{ paddingLeft: `${depth * 14}px` }}
            onClick={() => setOpen(!open)}
            className="flex items-center gap-1.5 py-1 px-2 hover:bg-zinc-800/60 rounded cursor-pointer text-xs font-medium text-zinc-400 transition"
          >
            <span>{open ? '📂' : '📁'}</span>
            <span>{node.name}</span>
          </div>
        )}
        {open && childKeys.map((k) => renderNode(node.children[k], node.name ? depth + 1 : depth))}
      </div>
    );
  };

  return (
    <div className="h-full overflow-y-auto pr-1">
      {files.length === 0 ? (
        <p className="text-xs text-zinc-500 p-2">No files indexed.</p>
      ) : (
        renderNode(root)
      )}
    </div>
  );
};