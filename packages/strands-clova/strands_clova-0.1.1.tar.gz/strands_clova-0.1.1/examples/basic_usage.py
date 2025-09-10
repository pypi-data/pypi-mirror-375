#!/usr/bin/env python
"""Basic usage example of strands-clova."""

import asyncio
import os
from dotenv import load_dotenv

from strands_clova import ClovaModel
from strands import Agent


async def main():
    """Run basic example."""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv("CLOVA_API_KEY"):
        print("Error: CLOVA_API_KEY not found in environment variables.")
        print("Please set: export CLOVA_API_KEY='your-api-key'")
        return
    
    print("=== Basic CLOVA Example ===\n")
    
    # Initialize model
    model = ClovaModel(
        model="HCX-005",
        temperature=0.7,
        max_tokens=1024
    )
    
    # Create agent
    agent = Agent(model=model)
    
    # Simple conversation
    print("Question: 안녕하세요! 오늘 날씨가 어떤가요?")
    response = await agent.invoke_async("안녕하세요! 오늘 날씨가 어떤가요?")
    print(f"Response: {response.message}\n")
    
    # English conversation
    print("Question: What are the benefits of using AI?")
    response = await agent.invoke_async("What are the benefits of using AI?")
    print(f"Response: {response.message}\n")


if __name__ == "__main__":
    asyncio.run(main())