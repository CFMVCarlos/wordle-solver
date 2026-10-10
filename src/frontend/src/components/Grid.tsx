import { cn } from '@/lib/utils';
import { Attempt, LetterState } from '@/lib/types';

interface GridProps {
  attempts: Attempt[];
  currentAttemptIndex: number;
  currentCellIndex: number;
  onToggleState: (attemptIdx: number, cellIdx: number) => void;
}

const STATE_COLORS: Record<LetterState, string> = {
  'empty': 'bg-white border-zinc-200',
  'filled': 'bg-zinc-100 border-zinc-300 text-zinc-900',
  'B': 'bg-zinc-500 border-zinc-500 text-white',
  'Y': 'bg-yellow-500 border-yellow-500 text-white',
  'G': 'bg-green-500 border-green-500 text-white'
};

export function Grid({ attempts, currentAttemptIndex, currentCellIndex, onToggleState }: GridProps) {
  return (
    <div className="flex flex-col gap-2 mb-8">
      {attempts.map((attempt, aIdx) => (
        <div key={aIdx} className="flex gap-2 justify-center">
          {attempt.cells.map((cell, cIdx) => {
            const isActive = aIdx === currentAttemptIndex && cIdx === currentCellIndex;
            const isClickable = aIdx === currentAttemptIndex && cell.char !== '';
            
            return (
              <button
                key={cIdx}
                onClick={() => isClickable ? onToggleState(aIdx, cIdx) : null}
                disabled={!isClickable}
                className={cn(
                  "w-14 h-14 sm:w-16 sm:h-16 rounded-xl flex items-center justify-center text-2xl font-bold border-2 transition-all duration-200 select-none",
                  STATE_COLORS[cell.state],
                  isActive && "border-indigo-400 ring-4 ring-indigo-100 shadow-sm scale-[1.02]",
                  isClickable && "cursor-pointer hover:opacity-90 active:scale-95",
                  !isClickable && cell.char === '' && "cursor-default"
                )}
              >
                {cell.char}
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
}
