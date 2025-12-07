// app/components/LiveAvatarSession.tsx
"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  LiveAvatarContextProvider,
  useSession,
  useTextChat,
  useVoiceChat,
} from "../liveavatar";
import { SessionState } from "@heygen/liveavatar-web-sdk";
import { useAvatarActions } from "../liveavatar/useAvatarActions";
import { useConversation } from "@elevenlabs/react"; // ElevenLabs React SDK

// Helper: convert base64 audio or (if needed) ensure audio buffer format
function base64ToUint8Array(base64: string) {
  const binary = atob(base64);
  const len = binary.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

const Button: React.FC<{
  onClick: () => void;
  disabled?: boolean;
  children: React.ReactNode;
}> = ({ onClick, disabled, children }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="bg-white text-black px-4 py-2 rounded-md"
    >
      {children}
    </button>
  );
};

const LiveAvatarSessionComponent: React.FC<{
  mode: "FULL" | "CUSTOM";
  onSessionStopped: () => void;
}> = ({ mode, onSessionStopped }) => {
  const [message, setMessage] = useState("");
  const sessionRef = useRef<any>(null); // we'll populate from global heygen session (see below)
  const {
    sessionState,
    isStreamReady,
    startSession,
    stopSession,
    connectionQuality,
    keepAlive,
    attachElement,
  } = useSession();
  const {
    isAvatarTalking,
    isUserTalking,
    isMuted,
    isActive,
    isLoading,
    start,
    stop,
    mute,
    unmute,
  } = useVoiceChat();

  const { interrupt, repeat, startListening, stopListening } =
    useAvatarActions(mode);

  const { sendMessage } = useTextChat(mode);
  const videoRef = useRef<HTMLVideoElement>(null);

  // ----------------------
  // ElevenLabs conversation hook
  // ----------------------
  const elevenLabsConversation = useConversation({
    // Ensure encoding lines up with HeyGen expectations:
    // Many ElevenLabs audio chunks are PCM; request 24000Hz if supported.
    audioEncoding: "pcm_24000",

    // Called when agent produces audio chunks (Uint8Array)
    onAudio: async (audioData: Uint8Array) => {
      console.log("ElevenLabs onAudio (chunk) length:", audioData?.length);
      if (sessionRef.current && mode === "CUSTOM") {
        try {
          // This streams whatever PCM bytes ElevenLabs sends directly into HeyGen
          await sessionRef.current.sendAudioChunk(audioData);
          // Debug:
          console.log("Forwarded audio chunk to HeyGen.");
        } catch (err) {
          console.error("Failed to forward audio chunk to HeyGen:", err);
        }
      }
    },

    // Mode changes (e.g., listening / speaking)
    onModeChange: async (modeChange) => {
      console.log("ElevenLabs onModeChange:", modeChange);
      // When ElevenLabs enters 'listening' it typically means audio finished
      if (modeChange?.mode === "listening" && sessionRef.current && mode === "CUSTOM") {
        try {
          await sessionRef.current.sendAudioEnded();
          console.log("Sent sendAudioEnded() to HeyGen.");
        } catch (err) {
          console.error("Failed to sendAudioEnded to HeyGen:", err);
        }
      }
    },

    onConnect: () => {
      console.log("ElevenLabs: connected");
    },
    onDisconnect: () => {
      console.log("ElevenLabs: disconnected");
    },
    onMessage: (m) => {
      console.log("ElevenLabs message:", m);
    },
    onError: (err) => {
      console.error("ElevenLabs error:", err);
    },
  });

  // When HeyGen stream becomes ready, capture its session object so we can call sendAudioChunk
  useEffect(() => {
    if (isStreamReady) {
      // The demo earlier placed the HeyGen session on window. Adjust if your SDK exposes differently.
      const heygenSession = (window as any).heygenSession;
      if (heygenSession) {
        sessionRef.current = heygenSession;
        console.log("Captured heygenSession on window -> sessionRef");
      } else {
        console.warn("heygenSession not found on window; ensure HeyGen SDK attaches it.");
      }
    }
  }, [isStreamReady]);

  useEffect(() => {
    if (sessionState === SessionState.DISCONNECTED) {
      onSessionStopped();
      // disconnect ElevenLabs if connected
      if (elevenLabsConversation.status === "connected") {
        elevenLabsConversation.endSession();
      }
    }
  }, [sessionState, onSessionStopped, elevenLabsConversation]);

  useEffect(() => {
    if (isStreamReady && videoRef.current) {
      attachElement(videoRef.current);
    }
  }, [attachElement, isStreamReady]);

  useEffect(() => {
    if (sessionState === SessionState.INACTIVE) {
      startSession();
    }
  }, [startSession, sessionState]);

  // Start ElevenLabs conversation using a signed URL returned by server (preferred).
  const startElevenLabsConversation = async () => {
    try {
      // Get signed url from your server (server will call ElevenLabs with your API Key)
      const res = await fetch("/api/elevenlabs-agent");
      if (!res.ok) {
        const body = await res.text();
        console.error("Failed to fetch signed-url:", res.status, body);
        alert("Failed to get ElevenLabs signed URL. See console.");
        return;
      }
      const { signed_url } = await res.json();
      console.log("Got signed_url:", signed_url);

      // Start conversation using signed url (preferred for private agents)
      if (signed_url) {
        await elevenLabsConversation.startSession({ signedUrl: signed_url });
      } else {
        // Fallback: start with agentId directly (public agents)
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        await elevenLabsConversation.startSession({ agentId: (window as any).ELEVENLABS_AGENT_ID });
      }

      console.log("ElevenLabs conversation started");
    } catch (err) {
      console.error("Failed to start ElevenLabs conversation:", err);
      alert("Failed to start ElevenLabs conversation (check console).");
    }
  };

  const stopElevenLabsConversation = async () => {
    try {
      if (elevenLabsConversation.status === "connected") {
        await elevenLabsConversation.endSession();
        console.log("Ended ElevenLabs conversation");
      }
    } catch (err) {
      console.error("Error ending ElevenLabs conversation:", err);
    }
  };

  return (
    <div className="w-[1080px] max-w-full h-full flex flex-col items-center justify-center gap-4 py-4">
      <div className="relative w-full aspect-video overflow-hidden flex flex-col items-center justify-center">
        <video ref={videoRef} autoPlay playsInline className="w-full h-full object-contain" />
        <button
          className="absolute bottom-4 right-4 bg-white text-black px-4 py-2 rounded-md"
          onClick={() => {
            stopSession();
            stopElevenLabsConversation();
          }}
        >
          Stop
        </button>
      </div>

      <div className="w-full h-full flex flex-col items-center justify-center gap-4">
        <p>Session state: {sessionState}</p>
        <p>Connection quality: {connectionQuality}</p>
        {mode === "FULL" && <p>User talking: {isUserTalking ? "true" : "false"}</p>}
        <p>Avatar talking: {isAvatarTalking ? "true" : "false"}</p>

        {mode === "CUSTOM" && (
          <>
            <p>ElevenLabs Status: {elevenLabsConversation.status || "disconnected"}</p>
            <p>ElevenLabs Speaking: {elevenLabsConversation.isSpeaking ? "true" : "false"}</p>

            <div className="flex gap-4">
              <Button
                onClick={() => {
                  if (elevenLabsConversation.status === "connected") {
                    stopElevenLabsConversation();
                  } else {
                    startElevenLabsConversation();
                  }
                }}
              >
                {elevenLabsConversation.status === "connected" ? "Stop ElevenLabs Agent" : "Start ElevenLabs Agent"}
              </Button>
            </div>
          </>
        )}

        <Button
          onClick={() => {
            keepAlive();
          }}
        >
          Keep Alive
        </Button>

        <div className="w-full h-full flex flex-row items-center justify-center gap-4">
          <Button onClick={() => startListening()}>Start Listening</Button>
          <Button onClick={() => stopListening()}>Stop Listening</Button>
          <Button onClick={() => interrupt()}>Interrupt</Button>
        </div>

        <div className="w-full h-full flex flex-row items-center justify-center gap-4">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-[400px] bg-white text-black px-4 py-2 rounded-md"
            placeholder={mode === "CUSTOM" ? "Type to send to AI (for testing)" : "Type message"}
          />
          <Button
            onClick={() => {
              if (mode === "CUSTOM" && elevenLabsConversation.status === "connected") {
                // Send as user message to ElevenLabs Agent (text)
                elevenLabsConversation.sendUserMessage(message);
              } else {
                sendMessage(message);
              }
              setMessage("");
            }}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};

export const LiveAvatarSession: React.FC<{
  mode: "FULL" | "CUSTOM";
  sessionAccessToken: string;
  onSessionStopped: () => void;
}> = ({ mode, sessionAccessToken, onSessionStopped }) => {
  return (
    <LiveAvatarContextProvider sessionAccessToken={sessionAccessToken}>
      <LiveAvatarSessionComponent mode={mode} onSessionStopped={onSessionStopped} />
    </LiveAvatarContextProvider>
  );
};
