#!/usr/bin/env python3
"""
Example usage of z007 as a package

LOCAL USAGE METHODS:
1. Copy z007 folder: cp -r z007 /path/to/your-project/
2. Add to Python path: See local_usage_example.py
3. Editable install: uv pip install -e . (from z007 directory)
"""

import asyncio
from z007 import Agent, create_calculator_tool


async def simple_example():
    """Simple question example"""
    print("=== Simple Example ===")
    # Use calculator tool even for simple example since AWS Bedrock requires tools
    calculator = create_calculator_tool()
    async with Agent(
        model_id="openai.gpt-oss-20b-1:0",
        tools=[calculator]
    ) as agent:
        response = await agent.run("Explain what LLM agents are in one sentence.")
    print(f"Response: {response}\n")


async def calculator_example():
    """Example with calculator tool"""
    print("=== Calculator Tool Example ===")
    calculator = create_calculator_tool()
    async with Agent(
        model_id="openai.gpt-oss-20b-1:0",
        tools=[calculator]
    ) as agent:
        response = await agent.run(
            "Calculate the result of (15 * 23) + (87 / 3) and explain the steps"
        )
    print(f"Response: {response}\n")


async def custom_tools_example():
    """Example with custom tools"""
    print("=== Custom Tools Example ===")
    
    def word_count_tool(text: str) -> str:
        """Count words in a text"""
        words = text.split()
        return f"Word count: {len(words)}"
    
    def reverse_text_tool(text: str) -> str:
        """Reverse the given text"""
        return text[::-1]
    
    async with Agent(
        model_id="openai.gpt-oss-20b-1:0",
        tools=[word_count_tool, reverse_text_tool]
    ) as agent:
        response = await agent.run(
            "Analyze this text: 'Hello world, this is a test message.' "
            "Count the words and show me the reversed version."
        )
    print(f"Response: {response}\n")


async def conversation_example():
    """Multi-turn conversation example"""
    print("=== Conversation Example ===")
    
    async with Agent(
        model_id="openai.gpt-oss-20b-1:0",
        system_prompt="You are a helpful programming tutor.",
    ) as agent:
        
        questions = [
            "What is a Python list?",
            "How do I add elements to it?", 
            "Show me a simple example"
        ]
        
        for i, question in enumerate(questions, 1):
            response = await agent.run(question)
            print(f"Q{i}: {question}")
            print(f"A{i}: {response}\n")


async def agent_context_example():
    """Example using Agent directly with context manager"""
    print("=== Agent Context Manager Example ===")
    
    def temperature_converter(celsius: float) -> str:
        """Convert Celsius to Fahrenheit"""
        fahrenheit = (celsius * 9/5) + 32
        return f"{celsius}°C = {fahrenheit}°F"
    
    async with Agent(
        model_id="openai.gpt-oss-20b-1:0",
        system_prompt="You are a helpful assistant with temperature conversion capabilities.",
        tools=[temperature_converter],
        max_turns=5
    ) as agent:
        response = await agent.run("Convert 25 degrees Celsius to Fahrenheit and explain the formula")
        print(f"Response: {response}\n")


async def main():
    """Run all examples"""
    print("z007 - Fast Micro Agent Examples\n")
    
    try:
        await simple_example()
        await calculator_example()
        await custom_tools_example()
        await conversation_example()
        await agent_context_example()
        
        print("=== All Examples Completed ===")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have LLM provider credentials configured.")


if __name__ == "__main__":
    asyncio.run(main())
