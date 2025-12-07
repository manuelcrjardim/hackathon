import { ELEVENLABS_API_KEY, ELEVENLABS_AGENT_ID } from "@/app/secrets";

export async function POST(req: Request) {
  const { text } = await req.json();

  const response = await fetch(
    "https://api.elevenlabs.io/v1/conversational-ai/messages",
    {
      method: "POST",
      headers: {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        agent_id: ELEVENLABS_AGENT_ID,
        text,
        // ensure alignment is returned!
        output_format: "pcm_24000",
        enable_timestamps: true,
      }),
    }
  );

  if (!response.ok) {
    const err = await response.text();
    console.error("EL message error:", err);
    return new Response(JSON.stringify({ error: err }), { status: 500 });
  }

  const data = await response.json();

  return new Response(JSON.stringify({
    audio_base64: data.audio,
    alignment: data.alignment,
  }), { status: 200 });
}
