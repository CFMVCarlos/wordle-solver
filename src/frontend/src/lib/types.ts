import { z } from "zod";

export const LetterStateEnum = z.enum(["empty", "filled", "B", "Y", "G"]);
export type LetterState = z.infer<typeof LetterStateEnum>;

export const LetterCellSchema = z.object({
  char: z.string().max(1),
  state: LetterStateEnum,
});
export type LetterCell = z.infer<typeof LetterCellSchema>;

export const AttemptSchema = z.object({
  cells: z.array(LetterCellSchema).length(5),
  isSubmitted: z.boolean(),
});
export type Attempt = z.infer<typeof AttemptSchema>;

export const SuggestionSchema = z.object({
  word: z.string(),
  count: z.number().int().nonnegative(),
});
export type Suggestion = z.infer<typeof SuggestionSchema>;
