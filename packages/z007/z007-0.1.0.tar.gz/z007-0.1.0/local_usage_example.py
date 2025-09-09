#!/usr/bin/env python3
"""
How to use z007 locally without PyPI installation

This file demonstrates different methods to use z007 in other projects
before it's published to PyPI.
"""

import sys
import os

# Setup path before importing z007 (this would go at top of your target file)
sys.path.insert(0, os.path.dirname(__file__))

from z007 import Agent, create_calculator_tool


# METHOD 1: Copy z007 folder to your target project
# This is useful if you want to include the code directly in your project

# Step 1: Copy the z007 directory to your project
# cp -r /path/to/aws-bedrock-gpt-oss-tester/z007 /path/to/your-project/

# Step 2: Import directly in your project
# from z007 import Agent

# METHOD 2: Add z007's parent directory to Python path (shown above)
# This is useful for development/testing

# METHOD 3: Install in development mode
# This creates a symlink so changes to the source are reflected immediately

# From the z007 project directory, run:
# pip install -e .
# OR with uv:
# uv pip install -e .
# Then you can import normally:
# from z007 import Agent

import sys
import asyncio
from pathlib import Path

# Setup path before importing zappy (this would go at top of your target file)
sys.path.insert(0, str(Path(__file__).parent))

from z007 import Agent, create_calculator_tool

# ============================================================================
# METHOD 1: Copy zappy folder to your target project
# ============================================================================
# 
# Step 1: Copy the zappy directory to your project
# cp -r /path/to/aws-bedrock-gpt-oss-tester/zappy /path/to/your-project/
# 
# Step 2: Import normally
# from zappy import Agent

# ============================================================================
# METHOD 2: Add zappy's parent directory to Python path (shown above)
# ============================================================================

# ============================================================================
# METHOD 3: Editable install (best for development)
# ============================================================================
#
# From the zappy project directory, run:
# uv pip install -e .
# 
# Then you can import from anywhere:
# from zappy import Agent

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def demo_local_usage():
    """Demo using zappy locally"""
    print("Testing local zappy usage...")
    
    # Quick ask example
    try:
        async with Agent(model_id="openai.gpt-oss-20b-1:0", tools=[create_calculator_tool()]) as agent:
            result = await agent.run("What is 5 + 3?")
        print(f"Quick ask result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Agent example
    try:
        async with Agent(model_id="openai.gpt-oss-20b-1:0") as agent:
            response = await agent.run("Hello! Can you calculate 10 * 7?")
            print(f"Agent response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("=== Local zappy Usage Demo ===")
    print("Current directory:", Path(__file__).parent)
    print()
    
    asyncio.run(demo_local_usage())
