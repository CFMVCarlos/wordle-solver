import { Loader2, Check } from 'lucide-react';
import { Suggestion } from '@/lib/types';

interface InfoPanelProps {
  loading: boolean;
  success: string | null;
  suggestion: Suggestion | null;
}

export function InfoPanel({ loading, success, suggestion }: InfoPanelProps) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-zinc-200 mb-8 transition-all">
      {loading ? (
        <div className="flex items-center justify-center gap-2 text-zinc-500 h-[60px]">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span className="font-medium">Calculating...</span>
        </div>
      ) : success ? (
        <div className="flex items-center justify-center gap-3 text-green-600 h-[60px]">
          <Check className="w-6 h-6" />
          <span className="font-bold text-lg">{success}</span>
        </div>
      ) : (
        <div className="text-center h-[60px] flex flex-col justify-center">
          {suggestion && suggestion.count > 0 ? (
            <>
              <p className="text-sm font-medium text-zinc-500 mb-1">
                {suggestion.count} {suggestion.count === 1 ? 'word' : 'words'} remaining
              </p>
              <p className="text-lg font-semibold text-zinc-900">
                Try guessing <span className="text-indigo-600 font-bold uppercase tracking-wider bg-indigo-50 px-2 py-0.5 rounded">{suggestion.word}</span>
              </p>
            </>
          ) : (
            <p className="text-zinc-500 font-medium">No suggestions available</p>
          )}
        </div>
      )}
    </div>
  );
}
