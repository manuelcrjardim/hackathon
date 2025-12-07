import { ELEVENLABS_API_KEY, ELEVENLABS_AGENT_ID } from "../secrets";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { text } = body;

    if (!text) {
      return new Response(JSON.stringify({ error: "text is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (!ELEVENLABS_API_KEY || !ELEVENLABS_AGENT_ID) {
      return new Response(
        JSON.stringify({ error: "ElevenLabs API key or agent not configured" }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    // Call ElevenLabs API using agent
    const res = await fetch(
      `https://api.elevenlabs.io/v1/text-to-speech/${ELEVENLABS_AGENT_ID}?output_format=pcm_24000`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "xi-api-key": ELEVENLABS_API_KEY,
        },
        body: JSON.stringify({ text }),
      }
    );

    if (!res.ok) {
      const errorData = await res.text();
      console.error("ElevenLabs agent API error:", errorData);
      return new Response(
        JSON.stringify({ error: "Failed to generate speech", details: errorData }),
        { status: res.status, headers: { "Content-Type": "application/json" } }
      );
    }

    const data = await res.json();
    const audio = data.audio_base64;

    return new Response(JSON.stringify({ audio }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error generating speech:", error);
    return new Response(
      JSON.stringify({ error: "Failed to generate speech" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
