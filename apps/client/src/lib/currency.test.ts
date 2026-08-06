import { describe, expect, it } from "vitest";
import {
  CURRENCIES,
  DEFAULT_CURRENCY,
  formatCurrency,
  formatCurrencyShort,
} from "./currency";

/**
 * Removes currency symbols, separators and spaces, preserving only digits.
 *
 * This keeps the tests independent from the machine locale:
 * - en-US may format 1234 as "1,234"
 * - pt-BR may format 1234 as "1.234"
 */
function onlyDigits(value: string): string {
  return value.replace(/\D/g, "");
}

describe("formatCurrency", () => {
  it("formats whole amounts with no minor units", () => {
    const out = formatCurrency(1234, "USD");

    expect(onlyDigits(out)).toBe("1234");
    expect(out).not.toMatch(/[.,]00(?:\D|$)/);
  });

  it("defaults to USD when no currency is given", () => {
    expect(formatCurrency(10)).toBe(
      formatCurrency(10, DEFAULT_CURRENCY),
    );
  });

  it("treats an empty-string currency as the default", () => {
    expect(formatCurrency(10, "")).toBe(
      formatCurrency(10, DEFAULT_CURRENCY),
    );
  });

  it("coerces non-finite values to 0", () => {
    const out = formatCurrency(Number.NaN, "USD");

    expect(onlyDigits(out)).toBe("0");
  });

  it("renders a well-formed but unknown ISO code without throwing", () => {
    // Intl is lenient with structurally valid unknown currency codes
    // and normally renders the code itself as the symbol.
    const out = formatCurrency(1234, "ZZZ");

    expect(out).toContain("ZZZ");
    expect(onlyDigits(out)).toBe("1234");
  });

  it("never throws on a structurally invalid code", () => {
    const invalidCodes = [
      "United States",
      "US",
      "USDD",
      "12",
      "u$d",
    ];

    for (const code of invalidCodes) {
      const format = () => formatCurrency(1234, code);

      expect(format).not.toThrow();
      expect(onlyDigits(format()).endsWith("1234")).toBe(true);
    }
  });

  it("formats every offered currency without throwing", () => {
    for (const currency of CURRENCIES) {
      expect(() =>
        formatCurrency(1000, currency.code),
      ).not.toThrow();
    }
  });
});

describe("formatCurrencyShort", () => {
  it("abbreviates millions and thousands with the currency symbol", () => {
    expect(formatCurrencyShort(2_500_000, "USD")).toBe("$2.5M");
    expect(formatCurrencyShort(3_400, "USD")).toBe("$3.4k");
    expect(formatCurrencyShort(900, "USD")).toBe("$900");
  });

  it("uses the matching symbol for non-USD currencies", () => {
    expect(formatCurrencyShort(1_000, "EUR")).toBe("€1.0k");
    expect(formatCurrencyShort(1_000, "INR")).toBe("₹1.0k");
  });

  it("falls back to the code prefix for unknown currencies", () => {
    expect(formatCurrencyShort(1_000, "ZZZ")).toBe("ZZZ 1.0k");
  });
});