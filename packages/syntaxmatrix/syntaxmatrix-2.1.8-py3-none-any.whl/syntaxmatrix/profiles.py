# syntaxmatrix/profiles.py
from openai import OpenAI
from google import genai

from syntaxmatrix.llm_store import list_profiles, load_profile

# Preload once at import-time
_profiles: dict[str, dict] = {}

def _refresh_profiles() -> None:
    _profiles.clear()
    for p in list_profiles():
        prof = load_profile(p["name"])
        if prof:
            _profiles[prof["purpose"]] = prof
            
def get_profile(purpose: str) -> dict:
    prof = _profiles.get(purpose)
    if prof:
        return prof
    _refresh_profiles()
    return _profiles.get(purpose)


def get_client(profile):
    
    provider = profile["provider"].lower()
    api_key = profile["api_key"]

    if provider == "google":
        return  genai.Client(api_key=api_key)
    if provider == "openai":
        return OpenAI(api_key=api_key)
    if provider == "xai":
        return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    if provider == "deepseek":
        return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    if provider == "moonshot":
        return OpenAI(api_key=api_key, base_url="https://api.moonshot.ai/v1")
    if provider == "alibaba":
        return OpenAI(api_key=api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",)