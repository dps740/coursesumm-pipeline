"""LLM integration utilities."""

import json
from typing import Any, Dict, Optional
import openai
import anthropic

from coursumm.config import get_config


async def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    json_response: bool = False,
    temperature: float = 0.3,
) -> str:
    """
    Call the configured LLM.
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        json_response: If True, request JSON output
        temperature: Sampling temperature
        
    Returns:
        LLM response text
    """
    config = get_config()
    
    if config.llm_provider == "openai":
        return await _call_openai(prompt, system_prompt, json_response, temperature)
    elif config.llm_provider == "anthropic":
        return await _call_anthropic(prompt, system_prompt, json_response, temperature)
    else:
        raise ValueError(f"Unknown LLM provider: {config.llm_provider}")


async def _call_openai(
    prompt: str,
    system_prompt: Optional[str],
    json_response: bool,
    temperature: float,
) -> str:
    """Call OpenAI API."""
    config = get_config()
    
    if not config.openai_api_key:
        raise ValueError("OPENAI_API_KEY not configured")
    
    client = openai.AsyncOpenAI(api_key=config.openai_api_key)
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    kwargs = {
        "model": config.llm_model,
        "messages": messages,
        "temperature": temperature,
    }
    
    if json_response:
        kwargs["response_format"] = {"type": "json_object"}
    
    response = await client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


async def _call_anthropic(
    prompt: str,
    system_prompt: Optional[str],
    json_response: bool,
    temperature: float,
) -> str:
    """Call Anthropic API."""
    config = get_config()
    
    if not config.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY not configured")
    
    client = anthropic.AsyncAnthropic(api_key=config.anthropic_api_key)
    
    kwargs = {
        "model": config.llm_model,
        "max_tokens": 4096,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    
    if system_prompt:
        kwargs["system"] = system_prompt
    
    response = await client.messages.create(**kwargs)
    content = response.content[0].text
    
    # Extract JSON if requested and Claude wrapped it in code blocks
    if json_response:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
    
    return content.strip()


def parse_json_response(response: str) -> Any:
    """
    Parse JSON from LLM response, handling various formats.
    """
    # Try direct parse first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Try extracting from code blocks
    if "```json" in response:
        try:
            json_str = response.split("```json")[1].split("```")[0]
            return json.loads(json_str.strip())
        except:
            pass
    
    if "```" in response:
        try:
            json_str = response.split("```")[1].split("```")[0]
            return json.loads(json_str.strip())
        except:
            pass
    
    raise ValueError(f"Could not parse JSON from response: {response[:200]}...")
