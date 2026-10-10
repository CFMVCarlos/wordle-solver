import { useState, useEffect, useCallback } from 'react';
import { AlertCircle } from 'lucide-react';

import { Attempt, LetterState, Suggestion } from '@/lib/types';
import { fetchSolveSuggestion } from '@/lib/api';
import { Header } from '@/components/Header';
import { InfoPanel } from '@/components/InfoPanel';
import { Grid } from '@/components/Grid';

const WORD_LENGTH = 5;
const MAX_ATTEMPTS = 6;

const NEXT_STATE: Record<LetterState, LetterState> = {
  'empty': 'empty',
  'filled': 'Y',
  'B': 'Y',
  'Y': 'G',
  'G': 'B'
};

const createEmptyAttempts = (): Attempt[] => Array.from({ length: MAX_ATTEMPTS }, () => ({
  cells: Array.from({ length: WORD_LENGTH }, () => ({ char: '', state: 'empty' as LetterState })),
  isSubmitted: false
}));

export default function App() {
  const [attempts, setAttempts] = useState<Attempt[]>(createEmptyAttempts());
  
  const [currentAttemptIndex, setCurrentAttemptIndex] = useState(0);
  const [currentCellIndex, setCurrentCellIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [suggestion, setSuggestion] = useState<Suggestion | null>(null);

  useEffect(() => {
    loadSuggestion([]);
  }, []);

  const loadSuggestion = async (submittedAttempts: Attempt[]) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchSolveSuggestion(submittedAttempts);
      setSuggestion({
        word: data.optimal_guess || '',
        count: data.remaining_words_count
      });
      
      if (data.remaining_words_count === 1 && currentAttemptIndex > 0) {
        setSuccess(`You found it! The word is ${data.remaining_words[0].toUpperCase()}`);
      } else if (data.remaining_words_count === 0) {
         setError("No words left! Check your constraints.");
      }
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const submitAttempt = () => {
    if (currentCellIndex < WORD_LENGTH) {
      setError("Not enough letters");
      return;
    }
    
    setAttempts(prev => {
      const nextAttempts = prev.map((attempt, aIdx) => {
        if (aIdx === currentAttemptIndex) {
           return {
             ...attempt,
             isSubmitted: true,
             cells: attempt.cells.map(c => ({ ...c, state: (c.state === 'filled' || c.state === 'empty') ? 'B' : c.state }))
           };
        }
        return attempt;
      });
      
      const submittedAttempts = nextAttempts.slice(0, currentAttemptIndex + 1);
      setCurrentAttemptIndex(prevIdx => prevIdx + 1);
      setCurrentCellIndex(0);
      
      // Fire and forget, we don't await in setState
      loadSuggestion(submittedAttempts);
      
      return nextAttempts;
    });
  };

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (success || currentAttemptIndex >= MAX_ATTEMPTS) return;
    if (loading) return;
    
    if (e.key === 'Backspace') {
      if (currentCellIndex > 0) {
        setAttempts(prev => prev.map((attempt, idx) => 
          idx === currentAttemptIndex 
            ? { ...attempt, cells: attempt.cells.map((cell, cIdx) => cIdx === currentCellIndex - 1 ? { char: '', state: 'empty' } : cell) }
            : attempt
        ));
        setCurrentCellIndex(prev => prev - 1);
        setError(null);
      }
    } else if (e.key === 'Enter') {
      submitAttempt();
    } else if (/^[a-zA-Z]$/.test(e.key)) {
      if (currentCellIndex < WORD_LENGTH) {
        setAttempts(prev => prev.map((attempt, idx) => 
          idx === currentAttemptIndex
            ? { ...attempt, cells: attempt.cells.map((cell, cIdx) => cIdx === currentCellIndex ? { char: e.key.toUpperCase(), state: 'B' } : cell) }
            : attempt
        ));
        setCurrentCellIndex(prev => prev + 1);
        setError(null);
      }
    }
  }, [currentAttemptIndex, currentCellIndex, loading, success]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const toggleState = (attemptIdx: number, cellIdx: number) => {
    if (attemptIdx !== currentAttemptIndex) return;
    
    setAttempts(prev => prev.map((attempt, aIdx) => 
      aIdx === attemptIdx
        ? { ...attempt, cells: attempt.cells.map((cell, cIdx) => cIdx === cellIdx && cell.char !== '' ? { ...cell, state: NEXT_STATE[cell.state] } : cell) }
        : attempt
    ));
  };

  const handleUndo = () => {
    if (currentAttemptIndex === 0 || loading || success) return;
    
    setAttempts(prev => prev.map((attempt, idx) => {
      if (idx === currentAttemptIndex - 1 || idx === currentAttemptIndex) {
        return {
          cells: Array.from({ length: WORD_LENGTH }, () => ({ char: '', state: 'empty' as LetterState })),
          isSubmitted: false
        };
      }
      return attempt;
    }));
    
    const prevIdx = currentAttemptIndex - 1;
    setCurrentAttemptIndex(prevIdx);
    setCurrentCellIndex(0);
    setError(null);
    setSuccess(null);
    
    const prevAttempts = attempts.slice(0, prevIdx);
    loadSuggestion(prevAttempts);
  };

  const handleReset = () => {
    setAttempts(createEmptyAttempts());
    setCurrentAttemptIndex(0);
    setCurrentCellIndex(0);
    setError(null);
    setSuccess(null);
    loadSuggestion([]);
  };

  return (
    <div className="min-h-screen bg-zinc-50 flex flex-col items-center py-12 px-4 selection:bg-indigo-100">
      <div className="w-full max-w-md">
        
        <Header 
          onUndo={handleUndo} 
          onReset={handleReset} 
          canUndo={currentAttemptIndex > 0 && !loading && !success} 
        />

        <InfoPanel 
          loading={loading} 
          success={success} 
          suggestion={suggestion} 
        />

        <Grid 
          attempts={attempts} 
          currentAttemptIndex={currentAttemptIndex} 
          currentCellIndex={currentCellIndex} 
          onToggleState={toggleState} 
        />

        {/* Actions / Errors */}
        <div className="flex flex-col items-center gap-4 h-16">
          {error && (
            <div className="flex items-center gap-2 text-red-600 bg-red-50 px-4 py-2 rounded-lg font-medium border border-red-100">
              <AlertCircle className="w-5 h-5" />
              {error}
            </div>
          )}
          
          {currentAttemptIndex < MAX_ATTEMPTS && !success && !error && currentCellIndex === WORD_LENGTH && (
             <p className="text-zinc-500 font-medium animate-pulse text-sm">
               Press <kbd className="px-2 py-1 bg-zinc-200 border border-zinc-300 rounded text-zinc-700 mx-1 font-mono text-xs shadow-sm">Enter</kbd> to submit or click letters to change colors
             </p>
          )}
        </div>

      </div>
    </div>
  );
}
