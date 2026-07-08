import { describe, expect, it } from "vitest";
import { isLookKind, LOOK_KINDS } from "./schema";

describe("look schema", () => {
  it("lists kinds", () => {
    expect(LOOK_KINDS).toContain("signature");
    expect(LOOK_KINDS).toContain("grade");
    expect(LOOK_KINDS).toContain("enhance");
  });

  it("validates kind strings", () => {
    expect(isLookKind("grade")).toBe(true);
    expect(isLookKind("nope")).toBe(false);
  });
});
