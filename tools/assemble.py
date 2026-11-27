#!/usr/bin/env python3
"""Wild Hearts Tales assembler.
story.json options: "lang" = narration language (en/ar, picks the voice), "caption_lang" = caption language (default same as lang),
each scene may have "caption" (text shown on screen) separate from "text" (spoken).
Drop clips (01.mp4, 02.mp4 ...) in a folder with story.json, get a finished vertical video.
Free tools only: ffmpeg + edge-tts. Usage: python assemble.py episodes/ep01 [--out out.mp4]
story.json: {"title": "...", "voice": "en-US-GuyNeural", "rate": "-8%", "music": "auto" | "file.mp3",
             "scenes": [{"clip": "01.mp4", "text": "Narration for this clip."}, ...]}
A scene with no "clip" uses a slow dark gradient card. Missing clip files fall back to the card too."""
import asyncio, json, math, os, subprocess, sys, wave, struct
import numpy as np
W, H, FPS, XF = 1080, 1920, 30, 0.5
RESUME = "--resume" in sys.argv  # reuse finished steps (useful on a slow PC; delete the _tmp folder to start over)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise SystemExit("ffmpeg failed:\n" + r.stderr[-1500:])
    return r.stdout

def dur(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).strip())

async def tts(text, voice, rate, out):
    import edge_tts
    for attempt in range(6):  # the free service is flaky: retry
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(out); return
        except Exception:
            await asyncio.sleep(1.5)
    raise SystemExit("edge-tts failed 6 times. Check internet, or try another voice in story.json")

def synth_music(seconds, out, seed=7):
    """Original cinematic bed: slow minor pad + plucked guitar-like arpeggio (additive pluck). Generated, no license issue."""
    sr = 44100; n = int(seconds * sr); rng = np.random.default_rng(seed)
    t = np.arange(n) / sr; mix = np.zeros(n)
    chords = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]  # Am F C G
    f = lambda m: 440 * 2 ** ((m - 69) / 12)
    bar = 6.0
    for b in range(int(seconds // bar) + 1):
        ch = chords[b % 4]; s0 = int(b * bar * sr); s1 = min(n, int((b + 1) * bar * sr + sr))
        if s0 >= n: break
        tt = np.arange(s1 - s0) / sr
        env = np.minimum(1, tt / 1.5) * np.minimum(1, (bar + 1 - tt) / 1.5)
        for m in ch:
            for h, a in ((1, 1), (2, .3), (3, .12)):
                mix[s0:s1] += 0.05 * a * np.sin(2 * math.pi * f(m - 12) * h * tt + rng.random() * 6) * env
        for k in range(12):  # arpeggio plucks
            m = ch[k % 3] + (12 if k % 3 == 2 else 0); p0 = s0 + int(k * 0.5 * sr)
            length = int(1.8 * sr); tp = np.arange(length) / sr
            y = sum(np.sin(2 * math.pi * f(m) * h * tp) * (0.6 ** h) * np.exp(-tp * (2.0 + 1.5 * h)) for h in range(1, 6))
            y[:200] *= np.linspace(0, 1, 200)
            e = min(n, p0 + length)
            if p0 < n: mix[p0:e] += 0.18 * y[:e - p0]
    mix = np.tanh(mix * 1.5); mix /= max(1e-9, np.abs(mix).max()); mix *= 0.8
    fade = int(2 * sr); mix[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(out, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((mix * 32767).astype("<i2").tobytes())

def ass_time(s):
    return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"

def chunks(text, n=4):
    """Split into balanced caption cards of at most n words (never a lone word if it can be avoided)."""
    w = text.split(); k = max(1, math.ceil(len(w) / n)); out, i = [], 0
    for j in range(k):
        size = len(w) // k + (1 if j < len(w) % k else 0); out.append(" ".join(w[i:i + size])); i += size
    return out

def main():
    ep = sys.argv[1]; out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(ep, "final.mp4")
    sj = sys.argv[sys.argv.index("--story") + 1] if "--story" in sys.argv else "story.json"; cfg = json.load(open(os.path.join(ep, sj))); tmp = os.path.join(ep, "_tmp"); os.makedirs(tmp, exist_ok=True)
    lang = cfg.get("lang", "en"); clang = cfg.get("caption_lang", lang); font = cfg.get("font", "Noto Kufi Arabic" if clang == "ar" else "Noto Sans")
    fsize = 62 if clang == "ar" else 64
    voice, rate = cfg.get("voice", "ar-EG-ShakirNeural" if lang == "ar" else "en-US-GuyNeural"), cfg.get("rate", "-8%")
    scenes, t0, ass = [], 0.0, []
    for i, sc in enumerate(cfg["scenes"]):
        a = os.path.join(tmp, f"n{i}.mp3")
        if not (RESUME and os.path.exists(a)): asyncio.run(tts(sc["text"], voice, rate, a))
        nd = dur(a)
        clip = os.path.join(ep, sc["clip"]) if sc.get("clip") else None
        have = clip and os.path.exists(clip)
        if not have and sc.get("image"):  # no Flow clip: animate the still locally (free)
            img = os.path.join(ep, sc["image"]); clip = os.path.join(tmp, f"m{i}.mp4")
            if not (RESUME and os.path.exists(clip)):
                run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "motion.py"), img, clip, "--sec", str(round(nd + 1.0, 2)),
                     "--mode", sc.get("motion", "push"), "--particles", sc.get("particles", "dust"), "--amp", str(sc.get("amp", 1.0))])
            have = True
        D = max(dur(clip) if have else 0, nd + 1.0, 3.0)
        v = os.path.join(tmp, f"v{i}.mp4")
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS},tpad=stop_mode=clone:stop_duration={D},trim=duration={D},format=yuv420p"
        if RESUME and os.path.exists(v): pass
        elif have: run(["ffmpeg", "-y", "-i", clip, "-an", "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", v])
        else: run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"gradients=s={W}x{H}:d={D}:c0=0x1b1b2f:c1=0xc8642a:speed=0.01:r={FPS}", "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "ultrafast", v])
        scenes.append((v, a, D, t0, nd))
        # captions timed proportionally over narration
        cs = chunks(sc.get("caption", sc["text"]), 3 if clang == "ar" else 4); tot = sum(len(c) for c in cs); s = t0 + 0.3
        for c in cs:
            e = s + nd * len(c) / tot
            ass.append(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Cap,,0,0,0,,{c}"); s = e
        t0 += D - XF
    total = t0 + XF
    # video: chained xfade
    ins = []; 
    for v, *_ in scenes: ins += ["-i", v]
    fc, last, off = "", "[0:v]", 0.0
    for i in range(1, len(scenes)):
        off += scenes[i - 1][2] - XF; nxt = f"[x{i}]"
        fc += f"{last}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}{nxt};"; last = nxt
    sub = os.path.join(tmp, "cap.ass")
    open(sub, "w", encoding="utf-8").write(
        f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\n[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n"
        f"Style: Cap,{font},{fsize},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,2,2,80,80,330,1\n"
        "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n" + "\n".join(ass) + "\n")
    vid = os.path.join(tmp, "video.mp4")
    base = fc + (f"{last}" if len(scenes) > 1 else "[0:v]")
    base = base + f"ass={sub}[vout]"
    if len(scenes) == 1: base = f"[0:v]ass={sub}[vout]"
    if not (RESUME and os.path.exists(vid)): run(["ffmpeg", "-y"] + ins + ["-filter_complex", base, "-map", "[vout]", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-pix_fmt", "yuv420p", vid])
    # audio: narration on timeline, music ducked
    ain, afc = [], ""
    for i, (v, a, D, s, nd) in enumerate(scenes):
        ain += ["-i", a]; afc += f"[{i}:a]adelay={int((s + 0.3) * 1000)}|{int((s + 0.3) * 1000)},apad[n{i}];"
    afc += "".join(f"[n{i}]" for i in range(len(scenes))) + f"amix=inputs={len(scenes)}:normalize=0,atrim=0:{total:.2f},aformat=sample_rates=44100:channel_layouts=stereo,asplit=2[narr][sc];"
    m = cfg.get("music", "auto")
    mus = os.path.join(tmp, "music.wav")
    if m == "auto": synth_music(total + 2, mus)
    else: mus = os.path.join(ep, m)
    ain += ["-i", mus]; k = len(scenes)
    afc += f"[{k}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume=0.55,atrim=0:{total:.2f}[m];[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];[narr][md]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5[aout]"
    aud = os.path.join(tmp, "audio.m4a")
    if not (RESUME and os.path.exists(aud)): run(["ffmpeg", "-y"] + ain + ["-filter_complex", afc, "-map", "[aout]", "-c:a", "aac", "-b:a", "160k", aud])
    run(["ffmpeg", "-y", "-i", vid, "-i", aud, "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-maxrate", "3M", "-bufsize", "6M", "-c:a", "copy", "-shortest", "-movflags", "+faststart", out])
    print(f"done: {out} ({dur(out):.1f}s)")

if __name__ == "__main__": main()
