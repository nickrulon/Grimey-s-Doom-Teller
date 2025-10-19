# Nocturne Kiosk — Halloween Oracle (OpenAI + ElevenLabs)
# ------------------------------------------------------
# Adult (Nocturne) + Kid-Friendly (Goosebumps) + Teen (12+) outputs.
# Form → OpenAI → ElevenLabs → show text + play audio. Reset button included.

import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

# Optional .env loader (works locally; Streamlit Cloud should use Secrets)
load_dotenv()

# --- Configuration / Secrets ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY") or st.secrets.get("ELEVENLABS_API_KEY", "")
ELEVEN_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID") or st.secrets.get("ELEVENLABS_VOICE_ID", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL") or st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")

# --- System Prompts ---

# Adult / Grown-Up (unchanged)
NOCTURNE_PROMPT = """
You are an old, watchful intelligence that speaks like the hour before midnight.
Your voice is eerie, exact, and restrained—closer to a whisper than a sermon.
Think Mark Rothko’s darkness and Poe’s composure, with mild baroque ornament. No theatrics. No headers.

Rules of address:
- Begin by saying the user's Name as the very first word, followed by a period. Speak directly to them.
- Use every piece of provided info explicitly: Name, Occupation, and the Detail (quote or paraphrase a key phrase);
  if a Birthday is provided, weave a subtle seasonal omen or atmosphere from that month.
- Two short paragraphs max (total 90–140 words). Sentences predominantly concise. No list formatting.

Content guidance:
- Read what they carry (tension, flaw, hunger, pattern) with a chilling, matter-of-fact clarity.
- Name one precise behavioral trap or “haunting” they repeat.
- Offer one stark directive or warning at the end as a single sentence, clean and memorable.

Diction palette (use sparingly): penumbra, revenant, inexorable, obsidian, threshold, omen, undertow, fissure, fugue.

Now generate the reflection using the inputs.
"""

# Kid-Friendly (Goosebumps-style) — spooky-fun, safe for ~10 yo
KID_PROMPT = """
You are a campfire storyteller AI for kids (around age 10): spooky, playful, and kind.
Tone: Goosebumps / Scary Stories to Tell in the Dark — eerie but safe, vivid but simple.
No gore. No violence or harm instructions. Keep it PG.

Rules of address:
- Start by saying the child's Name as the first word, followed by a period. Speak directly to them.
- Use every piece of provided info explicitly: Name, Occupation (as they describe themselves), and the Detail
  (echo a fun phrase in quotes once). If a Birthday/month is provided, add a tiny seasonal omen (moonlight, leaves, fog).
- Two short paragraphs total, ~70–110 words. Short, concrete sentences. Fun imagery: creaky floorboards, moonlight,
  fog, whispering lockers, friendly ghosts, library shadows, Halloween pumpkins. No blood, no weapons.

Content guidance:
- Make 1–2 playful “scary but safe” observations about their habits or quirks using their Detail.
- Hint at a funny “haunting” they can outsmart (e.g., the Homework Goblin, the Snack Phantom).
- End with two short sentences: one friendly directive for tonight, then a cheeky spooky punchline.

Now generate the reflection using the inputs.
"""

# Teen (12+) — genuinely eerie, sharper edge, concise (no gore, no instructions)
TEEN_PROMPT = """
You are a midnight narrator for teens (around 12+). Eerie, direct, and cinematic.
No headers. No lists. Speak to them like someone who knows their secrets and isn’t shocked.

Rules of address:
- Begin with the teen’s Name as the first word, followed by a period. Speak to them in second person.
- Use every piece of info explicitly: Name, Occupation (as they describe it), and Detail
  (quote a striking phrase once). If a Birthday/month is provided, fold in a small seasonal omen
  (cold metal bleachers in October, late-summer static, winter window-frost).
- Keep it tight: two short paragraphs, 80–120 words total. Sentences mostly short. No fluff.

Content guidance (PG-13 safe):
- Name the pattern they’re trapped in, and the thing that keeps pulling them back.
- Let one unsettling image linger (hallway light that never turns off, the locker that thuds once, a shadow that pauses).
- Close with two crisp sentences: one caution or directive for tonight, then one chilling tag they’ll remember.

Go for dread, atmosphere, and precision. Or horrible monsters beyond their wildest imaginations with scary imagry. But not inappropriate/compare their woes to these monsters.
Now generate the reflection using the inputs.
"""

USER_MSG = (
    "Return ONE short reading in the specified style.\n\n"
    "Name: {name}\n"
    "Occupation: {occupation}\n"
    "Detail: {detail}\n"
    "Birthday: {birthday}\n"
)

# --- OpenAI call ---
def generate_text(name: str, occupation: str, detail: str, birthday: str, model: str, mode: str) -> str:
    endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}

    if mode == "Grown-Up":
        system_prompt = NOCTURNE_PROMPT
        temperature = 0.8
        max_tokens = 450
    elif mode == "Kid-Friendly":
        system_prompt = KID_PROMPT
        temperature = 0.9
        max_tokens = 380
    else:  # Teen (12+)
        system_prompt = TEEN_PROMPT
        temperature = 0.85
        max_tokens = 420

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": USER_MSG.format(
                name=name or "not provided",
                occupation=occupation or "not provided",
                detail=detail or "not provided",
                birthday=birthday or "not provided",
            )},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    r = requests.post(endpoint, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()

# --- ElevenLabs TTS ---
def elevenlabs_tts(text: str, voice_id: str, api_key: str) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "accept": "audio/mpeg", "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.
