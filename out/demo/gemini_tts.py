# gemini_tts.py — une ligne de voix off via Gemini TTS (voix prédéfinie), utilisé pour brouhaha/08-11.
# usage : GEMINI_API_KEY=… python3 out/demo/gemini_tts.py OUT.mp3 Aoede "texte" "Dis en français, d’une voix douce"
import base64, json, os, subprocess, sys, urllib.request
# usage: gem_tts.py OUT.mp3 VOICE "texte" [style]
out, voice, text = sys.argv[1], sys.argv[2], sys.argv[3]
style = sys.argv[4] if len(sys.argv) > 4 else ''
prompt = f"{style}: {text}" if style else text
body = {"contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
model = os.environ.get('GEM_TTS_MODEL', 'gemini-2.5-flash-preview-tts')
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={os.environ['GEMINI_API_KEY']}"
req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=120) as r:
    d = json.load(r)
pcm = base64.b64decode(d['candidates'][0]['content']['parts'][0]['inlineData']['data'])
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 's16le', '-ar', '24000', '-ac', '1', '-i', '-', '-b:a', '128k', out],
               input=pcm, check=True)
print(out)
