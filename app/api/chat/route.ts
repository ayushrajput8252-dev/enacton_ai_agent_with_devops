/**
 * Next.js Chat API Route
 * Acts as a proxy to the FastAPI backend for chat requests
 * Supports both streaming and non-streaming responses
 */

export async function POST(req: Request) {
  try {
    const { message } = await req.json();

    if (!message || typeof message !== 'string') {
      return new Response(
        JSON.stringify({ error: 'Invalid message format' }),
        {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        }
      );
    }

    // Get FastAPI URL from environment or use default
    const fastApiUrl = process.env.FASTAPI_URL || 'http://localhost:8000';
    
    // Try streaming endpoint first, fallback to non-streaming
    try {
      const streamResponse = await fetch(`${fastApiUrl}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: `web-${Date.now()}`,
        }),
      });

      if (!streamResponse.ok) {
        throw new Error(`FastAPI error: ${streamResponse.status}`);
      }

      // Return the streaming response directly
      return new Response(streamResponse.body, {
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
          'Transfer-Encoding': 'chunked',
          'Cache-Control': 'no-cache',
        },
      });
    } catch (streamError) {
      console.warn('Streaming endpoint failed, trying non-streaming:', streamError);

      // Fallback to non-streaming endpoint
      const response = await fetch(`${fastApiUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: `web-${Date.now()}`,
        }),
      });

      if (!response.ok) {
        throw new Error(`FastAPI error: ${response.status}`);
      }

      const data = await response.json();

      // Simulate streaming response by splitting words
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        async start(controller) {
          const words = data.response.split(' ');
          for (const word of words) {
            controller.enqueue(encoder.encode(word + ' '));
            await new Promise((resolve) => setTimeout(resolve, 10));
          }
          controller.close();
        },
      });

      return new Response(stream, {
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
          'Transfer-Encoding': 'chunked',
        },
      });
    }
  } catch (error) {
    console.error('Chat API Error:', error);
    
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    return new Response(JSON.stringify({ 
      error: 'Failed to process message',
      details: errorMessage 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
