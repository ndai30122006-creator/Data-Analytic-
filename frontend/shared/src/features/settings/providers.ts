export const PROVIDERS = ["openai", "gemini"] as const;
export type Provider = typeof PROVIDERS[number];
