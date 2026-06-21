import { describe, expect, it } from "vitest";

import { dashboardUrl } from "./dashboard-state";
import {
  formatDate,
  formatInteger,
  formatNumber,
  formatPercent,
} from "./format";

describe("dashboard URL state", () => {
  it("sets a selected player and canonical view", () => {
    expect(
      dashboardUrl(new URLSearchParams("utm=test"), {
        playerId: 2544,
        view: "career",
        season: null,
      }),
    ).toBe("/?utm=test&playerId=2544&view=career");
  });

  it("clears dashboard state while retaining unrelated parameters", () => {
    expect(
      dashboardUrl(
        new URLSearchParams("playerId=2544&view=games&season=2025-26&utm=test"),
        { playerId: null },
      ),
    ).toBe("/?utm=test");
  });
});

describe("stat formatting", () => {
  it("renders missing values safely", () => {
    expect(formatNumber(null)).toBe("—");
    expect(formatInteger(null)).toBe("—");
    expect(formatPercent(null)).toBe("—");
    expect(formatDate(null)).toBe("—");
  });

  it("formats numbers and percentages consistently", () => {
    expect(formatNumber(27.456)).toBe("27.5");
    expect(formatInteger(27.6)).toBe("28");
    expect(formatPercent(0.5134)).toBe("51.3%");
    expect(formatDate("2026-01-05")).toBe("Jan 5");
  });
});
