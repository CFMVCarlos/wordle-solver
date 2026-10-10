import { RefreshCw, Undo2 } from 'lucide-react';

interface HeaderProps {
  onUndo: () => void;
  onReset: () => void;
  canUndo: boolean;
}

export function Header({ onUndo, onReset, canUndo }: HeaderProps) {
  return (
    <div className="flex items-center justify-between mb-8">
      <h1 className="text-3xl font-extrabold tracking-tight text-zinc-900 flex items-center gap-2">
        <span className="text-indigo-600">Wordle</span> Solver
      </h1>
      <div className="flex gap-2">
        <button 
          onClick={onUndo} 
          disabled={!canUndo}
          className="p-2 text-zinc-500 hover:text-zinc-900 hover:bg-zinc-200 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Undo Last Attempt"
        >
          <Undo2 className="w-5 h-5" />
        </button>
        <button 
          onClick={onReset} 
          className="p-2 text-zinc-500 hover:text-zinc-900 hover:bg-zinc-200 rounded-full transition-colors"
          title="Reset Game"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
