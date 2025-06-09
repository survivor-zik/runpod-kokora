import runpod
import random
import asyncio
import runpod
import asyncio
import requests
import base64

request_rate = 0

async def process_request(job):
    """
    Streams TTS audio response from localhost and yields it back as base64 chunks.
    """
    job_input = job["input"]
    text = job_input.get("text", "Hello world!")
    voice = job_input.get("voice", "af_bella")

    try:
        response = requests.post(
            "http://localhost:8880/v1/audio/speech",
            json={
                "input": text,
                "voice": voice,
                "response_format": "pcm"
            },
            stream=True,
            timeout=60
        )
    except Exception as e:
        yield {"error": f"Failed to connect to TTS server: {str(e)}"}
        return

    if response.status_code != 200:
        yield {"error": f"TTS server returned {response.status_code}"}
        return

    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            # Send base64 encoded PCM chunk
            yield {"audio_chunk": base64.b64encode(chunk).decode("utf-8")}

    yield {"status": "done"}


def adjust_concurrency(current_concurrency):
    # Dynamically adjust the worker's concurrency level based on request load.
    #
    # Args:
    #     current_concurrency (int): The current concurrency level
    #
    # Returns:
    #     int: The new concurrency level

    global request_rate
    
    # In production, this would use real metrics
    update_request_rate()
    
    max_concurrency = 10  # Maximum allowable concurrency
    min_concurrency = 1   # Minimum concurrency to maintain
    high_request_rate_threshold = 50  # Threshold for high request volume
    
    # Increase concurrency if under max limit and request rate is high
    if (request_rate > high_request_rate_threshold and 
        current_concurrency < max_concurrency):
        return current_concurrency + 1
    # Decrease concurrency if above min limit and request rate is low
    elif (request_rate <= high_request_rate_threshold and 
          current_concurrency > min_concurrency):
        return current_concurrency - 1
    
    return current_concurrency


def update_request_rate():
    """Simulates changes in the request rate to mimic real-world scenarios."""
    global request_rate
    request_rate = random.randint(20, 100)

# Start the Serverless function when the script is run
if __name__ == "__main__":
    runpod.serverless.start({
        "handler": process_request,
        "concurrency_modifier": adjust_concurrency
    })
