# Wild Hearts Tales: assembler / مجمّع الفيديو
Free. Runs on your laptop. No account, no card. / مجاني وبيشتغل على اللابتوب.

## One-time setup / التجهيز مرة واحدة
1. Install Python 3 (python.org) and ffmpeg (ffmpeg.org or `winget install ffmpeg`).
2. In a terminal: `pip install edge-tts numpy`
3. Put the Noto Kufi Arabic font on your PC (fonts.google.com/noto/specimen/Noto+Kufi+Arabic) for Arabic captions. (Or set "font" in story.json to any Arabic font you have, e.g. "Arial".)

## Make a video / تعمل فيديو
1. Make clips in Google Flow by hand with your free daily credits (see ../guide/flow_workflow.md). Download them as 01.mp4, 02.mp4 ...
2. Copy `episodes/ep01` to `episodes/ep02`. Put your clips inside. Edit `story.json` (one scene per clip).
3. Run: `python tools/assemble.py episodes/ep02 --story story_ar_captions.json --out final.mp4`
4. Open final.mp4, check it, upload it to YouTube yourself.
Add `--resume` to continue after a stop (slow PC).

## story.json options
- "lang": narration language, "en" or "ar" (picks the voice: en-US-GuyNeural / ar-EG-ShakirNeural). Or set "voice" yourself.
- "caption_lang": language of the on-screen captions ("ar" uses Noto Kufi Arabic, shaped right-to-left).
- each scene: "clip" (file name), "text" (spoken), "caption" (shown on screen, optional: if missing the spoken text is shown).
- "music": "auto" (original generated music) or a file name you are allowed to use.
- Files here: story.json = English narration + English captions. story_ar_captions.json = English narration + Arabic captions.

## What is automatic / what is by hand
Automatic: narration voice, music, captions, transitions, volume, final vertical 1080x1920 video.
By hand: making the clips in Flow (daily free credits), checking the video, uploading to YouTube.
Honest notes: voice and music are not listened to by the agents, check them yourself. Arabic captions are timed evenly across the spoken line, so they can drift a little from the English words. The free edge-tts voice service can fail sometimes (the tool retries 6 times).
