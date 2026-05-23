export async function POST(req: Request) {
  try {
    const { message } = await req.json();

    // Simulate streaming response with mock AI assistant
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      async start(controller) {
        // Simulate typing delay
        const responses: string[] = [
          'That\'s a great question about AI implementation. ',
          'At EnactOn, we specialize in helping enterprises adopt AI strategically. ',
          'First, we assess your current infrastructure and business goals. ',
          'Then we design a customized roadmap that minimizes risk and maximizes ROI. ',
          'Our team handles everything from data preparation to deployment and monitoring. ',
          'Would you like to know more about our specific services or get started with a consultation?',
        ];

        for (const chunk of responses) {
          // Simulate word-by-word streaming
          const words = chunk.split(' ');
          for (const word of words) {
            controller.enqueue(encoder.encode(word + ' '));
            await new Promise((resolve) => setTimeout(resolve, 30));
          }
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
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Failed to process message' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
