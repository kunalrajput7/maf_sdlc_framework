"""
APEX — AI-Powered Engineering eXperience

Run this to start the interactive 3-phase SDLC flow:
    python main.py

Make sure you have:
  1. Installed dependencies: pip install -e .
  2. Created a .env file from .env.example with your Azure AI Foundry credentials
"""

import asyncio
from src.orchestrator import Orchestrator


async def main():
    orchestrator = Orchestrator()
    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())
