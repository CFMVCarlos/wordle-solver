import { z } from "zod";
import { Attempt } from "./types";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const SolveResponseSchema = z.object({
  status: z.string(),
  message: z.string().nullable().optional(),
  remaining_words_count: z.number(),
  optimal_guess: z.string().nullable().optional(),
  remaining_words: z.array(z.string()),
});
export type SolveResponse = z.infer<typeof SolveResponseSchema>;

export async function fetchSolveSuggestion(submittedAttempts: Attempt[]): Promise<SolveResponse> {
  const payload = submittedAttempts.map(a => ({
    word: a.cells.map(c => c.char).join(''),
    feedback: a.cells.map(c => c.state).join('')
  }));
  
  const res = await fetch(`${API_URL}/api/solve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ attempts: payload })
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || 'Failed to fetch suggestion');
  }
  
  const data = await res.json();
  return SolveResponseSchema.parse(data);
}
