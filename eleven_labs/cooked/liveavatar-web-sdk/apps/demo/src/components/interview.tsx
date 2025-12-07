'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useConversation } from '@elevenlabs/react';

interface HeyGenSession {
  sendAudioChunk: (chunk: Uint8Array) => Promise<void>;
  sendAudioEnded: () => Promise<void>;
  attachElement: (element: HTMLVideoElement) => void;
  stopSession: () => Promise<void>;
}

function base64ToUint8Array(base64: string) {
  const binary = atob(base64);
  const len = binary.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

export function HeyGenElevenLabsInterview() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [heyGenSession, setHeyGenSession] = useState<HeyGenSession | null>(null);
  const [isHeyGenReady, setIsHeyGenReady] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  // ElevenLabs Conversation Hook
  const conversation = useConversation({
    // Called when AI speaks - we need to send this audio to HeyGen
    onAudio: async (audioData: Uint8Array) => {
      if (heyGenSession && isHeyGenReady) {
        try {
          // Send audio chunk to HeyGen for lip-sync
          await heyGenSession.sendAudioChunk(audioData);
        } catch (error) {
          console.error('Failed to send audio to HeyGen:', error);
        }
      }
    },
    
    // Called when AI finishes speaking
    onModeChange: async (mode: { mode: string }) => {
      if (mode.mode === 'listening' && heyGenSession && isHeyGenReady) {
        try {
          // Tell HeyGen that audio has ended
          await heyGenSession.sendAudioEnded();
        } catch (error) {
          console.error('Failed to end audio in HeyGen:', error);
        }
      }
    },

    onConnect: () => {
      console.log('Connected to ElevenLabs Agent');
      setIsConnecting(false);
    },

    onDisconnect: () => {
      console.log('Disconnected from ElevenLabs');
    },

    onMessage: (message) => {
      console.log('Message:', message);
    },

    onError: (error) => {
      console.error('ElevenLabs Error:', error);
      setIsConnecting(false);
    },
  });

  // Initialize HeyGen Avatar
  const startHeyGenAvatar = async () => {
    try {
      console.log('Initializing HeyGen avatar...');
      
      // Get session token from your API
      const response = await fetch('/api/heygen/token', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to get HeyGen session');
      }

      const { session_token } = await response.json();
      
      // Import and initialize HeyGen SDK
      const { LiveAvatar } = await import('@heygen/liveavatar-web-sdk');
      
      const session = new LiveAvatar({
        sessionToken: session_token,
      });

      // Connect to HeyGen
      await session.connect();
      
      // Attach video element
      if (videoRef.current) {
        await session.attachElement(videoRef.current);
      }

      setHeyGenSession(session);
      setIsHeyGenReady(true);
      console.log('HeyGen avatar ready');
      
      return session;
    } catch (error) {
      console.error('Failed to start HeyGen avatar:', error);
      throw error;
    }
  };

  // Start the interview
  const handleStartInterview = async () => {
    if (!process.env.NEXT_PUBLIC_ELEVENLABS_AGENT_ID) {
      alert('Please set NEXT_PUBLIC_ELEVENLABS_AGENT_ID in .env.local');
      return;
    }

    setIsConnecting(true);
    
    try {
      // 1. Start HeyGen avatar first
      await startHeyGenAvatar();
      
      // 2. Start ElevenLabs conversation
      await conversation.startSession({
        agentId: process.env.NEXT_PUBLIC_ELEVENLABS_AGENT_ID,
        connectionType: 'webrtc', // Use WebRTC for better audio streaming
      });
      
      console.log('Interview started successfully');
    } catch (error) {
      console.error('Failed to start interview:', error);
      setIsConnecting(false);
      alert('Failed to start interview. Check console for details.');
    }
  };

  // End the interview
  const handleEndInterview = async () => {
    if (confirm('Are you sure you want to end the interview?')) {
      try {
        await conversation.endSession();
        
        if (heyGenSession) {
          await heyGenSession.stopSession();
          setHeyGenSession(null);
          setIsHeyGenReady(false);
        }
      } catch (error) {
        console.error('Error ending interview:', error);
      }
    }
  };

  const isConnected = conversation.status === 'connected';
  const isSpeaking = conversation.isSpeaking;

  return (
    <div className="w-full h-full flex flex-col items-center justify-center gap-6 p-6">
      {/* Video Avatar */}
      <div className="relative w-full max-w-4xl aspect-video bg-gradient-to-br from-purple-900 to-pink-900 rounded-2xl overflow-hidden shadow-2xl">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-full h-full object-cover"
        />
        
        {/* Status Overlay */}
        <div className="absolute top-4 left-4 flex items-center gap-2 bg-black/60 backdrop-blur-sm px-4 py-2 rounded-lg">
          <div className={`w-3 h-3 rounded-full ${
            isConnected ? 'bg-green-400 animate-pulse' : 'bg-gray-400'
          }`} />
          <span className="text-sm text-white font-medium">
            {isConnected ? (isSpeaking ? '🗣️ AI Speaking' : '👂 Listening') : '○ Disconnected'}
          </span>
        </div>

        {/* Speaking Wave Indicator */}
        {isSpeaking && (
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex gap-1.5">
            {[...Array(7)].map((_, i) => (
              <div
                key={i}
                className="w-1.5 h-12 bg-white/70 rounded-full animate-wave"
                style={{ 
                  animationDelay: `${i * 0.1}s`,
                  animationDuration: '0.8s'
                }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Status Info */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-2">
          {isConnecting ? 'Connecting...' : isConnected ? 'Interview Active' : 'Ready to Start'}
        </h2>
        <p className="text-purple-200">
          {isConnecting 
            ? 'Establishing connection with AI interviewer...' 
            : isConnected 
            ? 'Speak naturally - the AI is listening' 
            : 'Click start to begin your voice interview'}
        </p>
      </div>

      {/* Volume Indicator */}
      {isConnected && (
        <div className="w-full max-w-md">
          <div className="flex items-center justify-between text-xs text-purple-200 mb-2">
            <span>Your Voice Level</span>
            <span>{Math.round((conversation.getInputVolume?.() || 0) * 100)}%</span>
          </div>
          <div className="bg-purple-900/30 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-purple-400 to-pink-400 h-full transition-all duration-100"
              style={{ width: `${(conversation.getInputVolume?.() || 0) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex gap-4">
        {!isConnected ? (
          <button
            onClick={handleStartInterview}
            disabled={isConnecting}
            className="px-10 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-xl text-white font-bold text-lg shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3"
          >
            {isConnecting ? (
              <>
                <div className="w-6 h-6 border-3 border-white border-t-transparent rounded-full animate-spin" />
                Connecting...
              </>
            ) : (
              <>
                🎙️ Start Interview
              </>
            )}
          </button>
        ) : (
          <>
            <button
              onClick={() => conversation.setVolume({ volume: conversation.getOutputVolume?.() > 0 ? 0 : 0.8 })}
              className="px-8 py-3 bg-purple-700/50 hover:bg-purple-700 rounded-lg transition-all duration-300 text-white font-semibold"
            >
              {(conversation.getOutputVolume?.() || 0) > 0 ? '🔊 Mute AI' : '🔇 Unmute AI'}
            </button>
            <button
              onClick={handleEndInterview}
              className="px-8 py-3 bg-red-700/50 hover:bg-red-700 rounded-lg transition-all duration-300 text-white font-semibold"
            >
              📞 End Interview
            </button>
          </>
        )}
      </div>

      {/* Powered By */}
      <div className="flex items-center gap-4 text-sm text-purple-300">
        <span>🤖 Voice AI: ElevenLabs</span>
        <span>•</span>
        <span>🎭 Avatar: HeyGen</span>
      </div>
    </div>
  );
}