#!/usr/bin/env python
"""Streaming example for strands-clova."""

import asyncio
import os
from dotenv import load_dotenv

from strands_clova import ClovaModel


async def stream_korean():
    """Stream Korean response."""
    print("Korean Streaming Example")
    print("Prompt: 한국의 전통 음식 3가지를 소개해주세요")
    print("Response: ", end="")
    
    model = ClovaModel(temperature=0.7, max_tokens=512)
    
    async for event in model.stream("한국의 전통 음식 3가지를 소개해주세요"):
        if isinstance(event, dict) and event.get("type") == "text":
            print(event["text"], end="", flush=True)
    print("\n")


async def stream_with_system_prompt():
    """Stream with system prompt."""
    print("System Prompt Example")
    print("System: You are a helpful coding assistant.")
    print("Prompt: Explain Python list comprehension")
    print("Response: ", end="")
    
    model = ClovaModel(temperature=0.5)
    
    async for event in model.stream(
        "Explain Python list comprehension",
        system_prompt="You are a helpful coding assistant. Be concise."
    ):
        if isinstance(event, dict) and event.get("type") == "text":
            print(event["text"], end="", flush=True)
    print("\n")


async def main():
    """Run streaming examples."""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv("CLOVA_API_KEY"):
        print("Error: CLOVA_API_KEY not found.")
        print("Please set: export CLOVA_API_KEY='your-api-key'")
        return
    
    print("=== CLOVA Streaming Examples ===\n")
    
    # Run examples
    await stream_korean()
    await stream_with_system_prompt()
    
    print("=== Examples completed ===")


if __name__ == "__main__":
    asyncio.run(main())