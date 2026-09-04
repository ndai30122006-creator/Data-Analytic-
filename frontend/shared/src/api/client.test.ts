import { describe, it, expect, vi } from "vitest";
import { request, setToken } from "./client";

describe("client", () => {
  it("adds Bearer header", async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ ok: true }) } as Response)
    );
    setToken("test123");
    const res = await request<{ ok: boolean }>("/health");
    expect(res.ok).toBe(true);
    expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining("/health"), expect.objectContaining({ headers: expect.objectContaining({ Authorization: "Bearer test123" }) }));
    setToken(null);
  });
});
