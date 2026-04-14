"""
Centralized LLM Model Provider
Supports: Google Gemini (with API key), Ollama (local fallback), OpenAI, Anthropic

Configuration via .env:
  LLM_PROVIDER  = auto | google | openai | anthropic | ollama
  GOOGLE_API_KEY / GEMINI_API_KEY, GOOGLE_MODEL
  OPENAI_API_KEY, OPENAI_MODEL
  ANTHROPIC_API_KEY, ANTHROPIC_MODEL
  OLLAMA_BASE_URL, OLLAMA_MODEL
"""
import os
import logging
from typing import Optional

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Default models per provider
_DEFAULT_MODELS = {
    'google': 'gemini-2.5-flash',
    'openai': 'gpt-4o-mini',
    'anthropic': 'claude-3-5-haiku-20241022',
    'ollama': 'llama3.2',
}


def get_llm(provider: Optional[str] = None,
            model: Optional[str] = None,
            temperature: float = 0.7,
            max_tokens: Optional[int] = None,
            **kwargs):
    """
    Create and return an LLM instance based on available configuration.
    
    Resolution order for provider:
      1. Explicit `provider` argument
      2. LLM_PROVIDER env var
      3. Auto-detect by checking API keys (Google > OpenAI > Anthropic > Ollama)

    Resolution order for model:
      1. Explicit `model` argument
      2. <PROVIDER>_MODEL env var (e.g. GOOGLE_MODEL, OPENAI_MODEL)
      3. Built-in default for the provider
    """
    # --- Resolve provider ---
    if not provider or provider == 'auto':
        provider = os.getenv('LLM_PROVIDER', '').strip().lower()

    if not provider or provider == 'auto':
        # Auto-detect from available keys
        if os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY') or \
           os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '').lower() in ('true', '1', 'yes'):
            provider = 'google'
        elif os.getenv('OPENAI_API_KEY'):
            provider = 'openai'
        elif os.getenv('ANTHROPIC_API_KEY'):
            provider = 'anthropic'
        else:
            provider = 'ollama'

    provider = provider.lower().strip()

    # --- Common params ---
    params = {'temperature': temperature}
    if max_tokens:
        params['max_tokens'] = max_tokens
    params.update(kwargs)

    # --- Build LLM ---
    if provider == 'google':
        return _create_google(model, params)
    elif provider == 'openai':
        return _create_openai(model, params)
    elif provider == 'anthropic':
        return _create_anthropic(model, params)
    elif provider == 'ollama':
        model = model or os.getenv('OLLAMA_MODEL') or _DEFAULT_MODELS['ollama']
        return _create_ollama(model, params)
    else:
        logger.warning(f"Unknown provider '{provider}', falling back to Ollama")
        model = model or os.getenv('OLLAMA_MODEL') or _DEFAULT_MODELS['ollama']
        return _create_ollama(model, params)


def _create_google(model: Optional[str], params: dict):
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    use_vertex = os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '').lower() in ('true', '1', 'yes')

    if not api_key and not use_vertex:
        logger.warning("No GOOGLE_API_KEY found, falling back to Ollama")
        return _create_ollama(
            os.getenv('OLLAMA_MODEL') or _DEFAULT_MODELS['ollama'], params
        )

    from langchain_google_genai import ChatGoogleGenerativeAI
    model_name = model or os.getenv('GOOGLE_MODEL') or _DEFAULT_MODELS['google']
    if not model_name.startswith('models/'):
        model_name = f'models/{model_name}'

    if use_vertex:
        # Vertex AI mode: the google-genai SDK reads GOOGLE_GENAI_USE_VERTEXAI,
        # GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, and
        # GOOGLE_APPLICATION_CREDENTIALS from the environment automatically.
        logger.info(f"Using Google Gemini via Vertex AI: {model_name}")
        kwargs = {**params}
        if api_key:
            kwargs['google_api_key'] = api_key
        return ChatGoogleGenerativeAI(model=model_name, **kwargs)
    else:
        logger.info(f"Using Google Gemini (API key): {model_name}")
        return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, **params)


def _create_openai(model: Optional[str], params: dict):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.warning("No OPENAI_API_KEY found, falling back to Ollama")
        return _create_ollama(
            os.getenv('OLLAMA_MODEL') or _DEFAULT_MODELS['ollama'], params
        )
    from langchain_openai import ChatOpenAI
    model_name = model or os.getenv('OPENAI_MODEL') or _DEFAULT_MODELS['openai']
    logger.info(f"Using OpenAI: {model_name}")
    return ChatOpenAI(model=model_name, api_key=api_key, **params)


def _create_anthropic(model: Optional[str], params: dict):
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("No ANTHROPIC_API_KEY found, falling back to Ollama")
        return _create_ollama(
            os.getenv('OLLAMA_MODEL') or _DEFAULT_MODELS['ollama'], params
        )
    from langchain_anthropic import ChatAnthropic
    model_name = model or os.getenv('ANTHROPIC_MODEL') or _DEFAULT_MODELS['anthropic']
    logger.info(f"Using Anthropic: {model_name}")
    return ChatAnthropic(model=model_name, api_key=api_key, **params)


def _create_ollama(model: str, params: dict):
    """Create an Ollama LLM instance (local, no API key required)."""
    from langchain_ollama import ChatOllama
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    logger.info(f"Using Ollama (local): {model} @ {base_url}")
    return ChatOllama(model=model, base_url=base_url, **params)


def get_provider_info() -> dict:
    """Return info about which provider will be used (useful for UI display)."""
    has_google = bool(os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY') or
                      os.getenv('GOOGLE_GENAI_USE_VERTEXAI', '').lower() in ('true', '1', 'yes'))
    has_openai = bool(os.getenv('OPENAI_API_KEY'))
    has_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))

    env_provider = os.getenv('LLM_PROVIDER', '').strip().lower()

    if env_provider and env_provider != 'auto':
        active = env_provider
    elif has_google:
        active = 'google'
    elif has_openai:
        active = 'openai'
    elif has_anthropic:
        active = 'anthropic'
    else:
        active = 'ollama'

    return {
        'active_provider': active,
        'google_available': has_google,
        'openai_available': has_openai,
        'anthropic_available': has_anthropic,
        'ollama_available': True,  # Always available locally
    }
