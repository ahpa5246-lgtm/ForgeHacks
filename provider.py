"""Server-side AI provider selection for job-offer extraction and comparison.

Google AI Studio and Groq both expose OpenAI-compatible chat completion
endpoints. Prefer Gemini when configured. Never return or log the API key.
"""
import os


def configured_provider():
    """Return public metadata only: whether any usable key is present."""
    if (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("google")):
        return "gemini"
    if os.environ.get("GROQ_API_KEY"):
        return "groq"
    return None


def provider_connection():
    """Private connection fields for use only in server-side request builders."""
    gemini_key = (os.environ.get("GEMINI_API_KEY")
                  or os.environ.get("GOOGLE_API_KEY")
                  or os.environ.get("google"))
    if gemini_key:
        return {
            "provider": "gemini",
            "key": gemini_key,
            "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            "model": os.environ.get("GEMINI_MODEL", "gemini-3.8-flash"),
        }
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        return {
            "provider": "groq",
            "key": groq_key,
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "model": os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b"),
        }
    return None


def prepare_json_request(payload, config):
    """Provider-safe JSON-object completion payload, without changing prompts."""
    payload["model"] = config["model"]
    if config["provider"] == "groq" and config["model"] == "qwen/qwen3.8-27b":
        payload.update({"temperature": 0.7, "reasoning_effort": "none",
                        "reasoning_format": "hidden"})
    else:
        payload.pop("reasoning_effort", None)
        payload.pop("reasoning_format", None)
    return payload
