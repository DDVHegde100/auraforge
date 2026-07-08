/** shared look types — keep in sync with engine schema.py */

export type LookKind = "signature" | "grade" | "enhance";

export interface Look {
  id: string;
  name: string;
  kind: LookKind;
  tags: string[];
  experimental?: boolean;
  skin_protect?: boolean;
  stack: Record<string, unknown>;
  notes?: string;
}

export const LOOK_KINDS: LookKind[] = ["signature", "grade", "enhance"];

export function isLookKind(value: string): value is LookKind {
  return (LOOK_KINDS as string[]).includes(value);
}
