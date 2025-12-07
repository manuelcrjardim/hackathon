export const API_KEY = process.env.DEMO_API_KEY ?? "5e4a40cc-d2d7-11f0-a99e-066a7fa2e369";
export const API_URL = process.env.DEMO_API_URL ?? "https://api.liveavatar.com";
export const AVATAR_ID = process.env.DEMO_AVATAR_ID ?? "dd73ea75-1218-4ef3-92ce-606d5f7fbc0a";

// FULL MODE Customizations
// Wayne's avatar voice and context
export const VOICE_ID = process.env.DEMO_VOICE_ID ?? "c2527536-6d1f-4412-a643-53a3497dada9";
export const CONTEXT_ID = process.env.DEMO_CONTEXT_ID ?? "5b9dba8a-aa31-11f0-a6ee-066a7fa2e369";
export const LANGUAGE = process.env.DEMO_LANGUAGE ?? "en";

// CUSTOM MODE Customizations
// Prefer environment variables for sensitive keys. If you run locally, put these in `apps/demo/.env.local`.
export const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY ?? "YOUR_ELEVENLABS_API_KEY";
export const ELEVENLABS_VOICE_ID = process.env.ELEVENLABS_VOICE_ID ?? "21m00Tcm4TlvDq8ikWAM";
export const OPENAI_API_KEY = process.env.OPENAI_API_KEY ?? "YOUR_OPENAI_API_KEY";
