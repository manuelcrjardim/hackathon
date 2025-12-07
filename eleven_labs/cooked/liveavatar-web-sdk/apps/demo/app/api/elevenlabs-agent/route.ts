// app/api/elevenlabs/signed-url/route.ts
import { NextResponse } from "next/server";
import { ELEVENLABS_API_KEY, ELEVENLABS_AGENT_ID } from "../secrets";

/**
 * GET /api/elevenlabs/signed-url
 * Returns JSON: { signed_url: string } or 400/500 on error.
 */
export async function GET() {
  if (!ELEVENLABS_API_KEY || !ELEVENLABS_AGENT_ID) {
    return NextResponse.json(
      { error: "ELEVENLABS_API_KEY or ELEVENLABS_AGENT_ID not configured" },
      { status: 500 }
    );
  }

  try {
    const url = `https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?agent_id=${encodeURIComponent(
      ELEVENLABS_AGENT_ID
    )}`;

    const resp = await fetch(url, {
      method: "GET",
      headers: {
        "xi-api-key": ELEVENLABS_API_KEY,
      },
    });

    const body = await resp.json();

    if (!resp.ok) {
      console.error("Signed URL fetch failed:", resp.status, body);
      return NextResponse.json(
        { error: "Failed to get signed URL", details: body },
        { status: resp.status }
      );
    }

    // body should contain { signed_url: "wss://..." }
    return NextResponse.json({ signed_url: body.signed_url });
  } catch (err) {
    console.error("Error getting signed URL:", err);
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}
