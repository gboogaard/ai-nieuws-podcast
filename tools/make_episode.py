#!/usr/bin/env python3
"""AI in 5 - maakt audio voor nieuwe afleveringen en bouwt episodes/index.json.

Draait in GitHub Actions (zie .github/workflows/podcast.yml), alleen standaard-Python.

Werkwijze
  1. Zoekt episodes/JJJJ-MM-DD.json waarvoor nog geen audio/JJJJ-MM-DD.mp3 bestaat.
  2. Maakt de mp3 met ElevenLabs (model uit tools/config.json, standaard eleven_v4).
  3. Ruimt afleveringen ouder dan keepDays op.
  4. Bouwt episodes/index.json opnieuw op uit alle afleveringen met audio.

Omgeving
  ELEVENLABS_API_KEY   verplicht (GitHub-secret)
  ELEVENLABS_VOICE_ID  optioneel, gaat voor op voiceId in config.json
  SKIP_AUDIO=1         test zonder ElevenLabs (geen mp3, aflevering wel in index)
"""
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes"
AUDIO_DIR = ROOT / "audio"
API = "https://api.elevenlabs.io/v1"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SECTION_TITLES = {"nl": "Nederland", "wereld": "Wereldwijd", "werk": "Werk", "kansen": "Kansen"}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def full_text(ep):
    """Intro, secties en afsluiting als één tekst, plus de tekstpositie van elke sectie."""
    parts, starts, pos = [], [], 0
    blocks = []
    if ep.get("intro"):
        blocks.append(("intro", "", ep["intro"]))
    for s in ep.get("sections", []):
        blocks.append((s.get("key", ""), s.get("title") or SECTION_TITLES.get(s.get("key"), ""), s.get("script", "")))
    if ep.get("outro"):
        blocks.append(("outro", "", ep["outro"]))
    for key, title, text in blocks:
        text = text.strip()
        if not text:
            continue
        if key not in ("intro", "outro"):
            starts.append((key, title, 0 if not starts else pos))
        parts.append(text)
        pos += len(text) + 2
    return "\n\n".join(parts), starts


def split_text(text, limit):
    chunks, buf = [], ""
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        pieces = [para] if len(para) <= limit else re.split(r"(?<=[.!?])\s+", para)
        for piece in pieces:
            if buf and len(buf) + len(piece) + 2 > limit:
                chunks.append(buf.strip())
                buf = ""
            buf += piece + "\n\n"
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


def request(url, key, body=None, want_audio=False):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"xi-api-key": key}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if want_audio:
        headers["Accept"] = "audio/mpeg"
    last = None
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
            with urllib.request.urlopen(req, timeout=300) as r:
                payload = r.read()
            if want_audio and len(payload) < 1000:
                raise RuntimeError("lege audio ontvangen")
            return payload
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:500]}"
            if e.code in (400, 401, 403, 404, 422):
                break
        except Exception as e:  # netwerk of time-out
            last = str(e)
        print(f"  poging {attempt} mislukt: {last}", flush=True)
        time.sleep(10)
    raise RuntimeError(f"ElevenLabs-fout bij {url.split('?')[0]}: {last}")


def synthesize(text, cfg, key, out_path):
    try:
        models = json.loads(request(f"{API}/models", key))
        model = next((m for m in models if m.get("model_id") == cfg["model"]), None)
        if not model:
            raise RuntimeError(f"Model {cfg['model']} niet gevonden in dit ElevenLabs-account.")
        use_tts = bool(model.get("can_do_text_to_speech"))
    except RuntimeError as e:
        if "models_read" not in str(e) and "401" not in str(e):
            raise
        # Sleutel zonder leesrecht op modellen: ga uit van gewone text-to-speech.
        print("  geen leesrecht op modellen, ik gebruik text-to-speech", flush=True)
        use_tts = True
    voice = os.environ.get("ELEVENLABS_VOICE_ID") or cfg["voiceId"]
    if not voice or voice.startswith("VUL_"):
        raise RuntimeError("Geen voice ID: zet het secret ELEVENLABS_VOICE_ID of vul voiceId in tools/config.json.")
    fmt = cfg.get("outputFormat", "mp3_44100_128")
    chunks = split_text(text, 9000 if use_tts else 1900)
    print(f"  model {cfg['model']} via {'text-to-speech' if use_tts else 'text-to-dialogue'}, {len(chunks)} deel/delen", flush=True)
    audio = b""
    for i, chunk in enumerate(chunks):
        if use_tts:
            body = {"text": chunk, "model_id": cfg["model"], "language_code": cfg.get("languageCode", "nl")}
            if cfg.get("voiceSettings"):
                body["voice_settings"] = cfg["voiceSettings"]
            if i > 0:
                body["previous_text"] = chunks[i - 1][-300:]
            if i < len(chunks) - 1:
                body["next_text"] = chunks[i + 1][:300]
            url = f"{API}/text-to-speech/{voice}?output_format={fmt}"
        else:
            body = {"inputs": [{"text": chunk, "voice_id": voice}], "model_id": cfg["model"],
                    "language_code": cfg.get("languageCode", "nl")}
            url = f"{API}/text-to-dialogue?output_format={fmt}"
        try:
            audio += request(url, key, body, want_audio=True)
        except RuntimeError as e:
            # Sommige modellen accepteren niet alle stem-instellingen: één keer zonder proberen.
            if use_tts and "voice_settings" in body and "422" in str(e):
                body.pop("voice_settings")
                audio += request(url, key, body, want_audio=True)
            else:
                raise
        print(f"  deel {i + 1}/{len(chunks)} klaar", flush=True)
    out_path.write_bytes(audio)


def record_usage(date, chars, cfg, key):
    """Houdt per aflevering het aantal tekens bij in episodes/usage.json, plus het ElevenLabs-tegoed als de sleutel dat mag lezen."""
    path = EP_DIR / "usage.json"
    data = load_json(path) if path.exists() else {"episodes": []}
    data["episodes"] = [e for e in data.get("episodes", []) if e.get("date") != date]
    data["episodes"].append({"date": date, "chars": chars, "model": cfg["model"]})
    data["episodes"] = sorted(data["episodes"], key=lambda e: e["date"])[-120:]
    try:
        sub = json.loads(request(f"{API}/user/subscription", key))
        data["subscription"] = {
            "checked": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "tier": sub.get("tier"),
            "character_count": sub.get("character_count"),
            "character_limit": sub.get("character_limit"),
            "next_reset": dt.datetime.fromtimestamp(sub["next_character_count_reset_unix"], dt.timezone.utc).date().isoformat()
            if sub.get("next_character_count_reset_unix") else None,
        }
    except Exception as e:
        data["subscription"] = {"checked": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                                "error": "tegoed niet leesbaar (sleutel mist leesrecht 'User')" if "401" in str(e) else str(e)[:200]}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bitrate(cfg):
    m = re.search(r"_(\d+)$", cfg.get("outputFormat", "mp3_44100_128"))
    return int(m.group(1)) if m else 128


def main():
    cfg = load_json(ROOT / "tools" / "config.json")
    skip = os.environ.get("SKIP_AUDIO") == "1"
    AUDIO_DIR.mkdir(exist_ok=True)
    today = dt.date.today()
    cutoff = (today - dt.timedelta(days=int(cfg.get("keepDays", 60)))).isoformat()

    episode_files = sorted(p for p in EP_DIR.glob("*.json") if DATE_RE.match(p.stem))

    # 1-2. audio maken voor nieuwe afleveringen
    for p in episode_files:
        mp3 = AUDIO_DIR / f"{p.stem}.mp3"
        if mp3.exists() or p.stem < cutoff or skip:
            continue
        print(f"Aflevering {p.stem}: audio maken", flush=True)
        key = os.environ.get("ELEVENLABS_API_KEY")
        if not key:
            print("Geen ELEVENLABS_API_KEY: de app gebruikt de iPhone-stem.", flush=True)
            continue
        text, _ = full_text(load_json(p))
        try:
            synthesize(text, cfg, key, mp3)
            record_usage(p.stem, len(text), cfg, key)
        except Exception as e:
            # Niet stoppen: de app leest de aflevering dan voor met de iPhone-stem.
            mp3.unlink(missing_ok=True)
            print(f"::warning title=AI in 5 audio::{e}".replace("\n", " "), flush=True)

    # 3. opruimen
    for p in episode_files:
        if p.stem < cutoff:
            p.unlink()
            (AUDIO_DIR / f"{p.stem}.mp3").unlink(missing_ok=True)
            print(f"Opgeruimd: {p.stem}")

    # 4. index opbouwen
    entries = []
    for p in sorted((p for p in EP_DIR.glob("*.json") if DATE_RE.match(p.stem)), reverse=True):
        ep = load_json(p)
        mp3 = AUDIO_DIR / f"{p.stem}.mp3"
        text, starts = full_text(ep)
        if mp3.exists():
            duration = round(mp3.stat().st_size * 8 / (bitrate(cfg) * 1000))
            audio = f"audio/{p.stem}.mp3"
        else:
            # Geen mp3: de app leest de tekst voor met de iPhone-stem.
            duration = round(len(text.split()) / 150 * 60)
            audio = None
        total = max(1, len(text))
        entries.append({
            "id": p.stem,
            "date": p.stem,
            "title": ep.get("title", ""),
            "summary": ep.get("summary", ""),
            "duration": duration,
            "audio": audio,
            "chapters": [{"key": k, "title": t, "start": round(s / total * duration)} for k, t, s in starts],
            "items": ep.get("items", []),
            "transcript": text,
        })
    index = {"updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "episodes": entries}
    (EP_DIR / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"index.json: {len(entries)} aflevering(en)")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        if e.code not in (None, 0):
            print(f"::error title=AI in 5::{e.code}", flush=True)
        raise
    except Exception as e:
        # Als annotatie tonen, zodat de fout ook zonder logs zichtbaar is.
        print(f"::error title=AI in 5::{type(e).__name__}: {e}".replace("\n", " "), flush=True)
        sys.exit(1)
