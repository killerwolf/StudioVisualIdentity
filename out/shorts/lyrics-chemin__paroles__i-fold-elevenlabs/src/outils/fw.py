import sys, json
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[3] if len(sys.argv)>3 else 'small.en', device='cpu', compute_type='int8', cpu_threads=4)
prompt = "I fold my day in draft mode. I draw lines but not for show. I've been up since 5 a.m. Printer down cuz no ink. Draft mode's my spare keys. Make another note.txt. And yet. Wrong fold. Such a lot of wrong folds."
segs, info = m.transcribe(sys.argv[1], language='en', word_timestamps=True, initial_prompt=(None if len(sys.argv) > 4 else prompt), vad_filter=False, beam_size=5, condition_on_previous_text=False)
out=[]
for s in segs:
    out.append(dict(start=s.start,end=s.end,text=s.text,words=[dict(w=w.word,s=round(w.start,3),e=round(w.end,3),p=round(w.probability,2)) for w in s.words]))
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}", flush=True)
json.dump(out, open(sys.argv[2],'w'), indent=1)
