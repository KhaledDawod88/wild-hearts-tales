# Wild Hearts Tales: animal stories pipeline

Wild Hearts Tales is a YouTube Shorts channel of short animal stories about freedom and home, told with painted stills, camera motion, English narration and Arabic captions. This repo holds the story scripts and the pipeline that makes each episode.

This is a separate project from the Excel tips channel (CELLCRAFT): https://github.com/KhaledDawod88/cellcraft-daily

Repo layout: tools/ (assemble.py, motion.py), episodes/ (ep01, ep02 story_short.json), guide.md (series bible), stories/ (story scripts, guides and earlier tool copies, kept as they were).

Free, local pipeline that turns a story file plus painted stills (or Google Flow clips) into a vertical 1080x1920 YouTube Short with English narration, Arabic captions and original generated music. No accounts, no cards, no paid services.

Live channel: https://www.youtube.com/@wildheartstales_official
Episodes made so far: ep01 "Ember: The Long Way Home" (horse), ep02 "Sable and the Silver River" (wolf cub).

## Files
- `tools/assemble.py`: narration (edge-tts), motion for stills, music, Arabic captions, transitions, final mix.
- `tools/motion.py`: free camera motion for one still (push, pull, pan_left, pan_right, drifting particles). Has the `--amp` option for stronger motion.
- `episodes/ep01/story_short.json`, `episodes/ep02/story_short.json`: the story files used (narration text, Arabic captions, motion per scene).
- `guide.md`: series bible, characters, story arcs, narration style, music notes, the 5-clip-per-day Flow format.

Stills, clips and mp4 files are not in the repo. You make them (below).

## One-time setup
1. Python 3 and ffmpeg (with ffprobe) on PATH.
2. `pip install edge-tts numpy pillow`
3. Install the font Noto Kufi Arabic (Arabic captions). Or set `"font"` in the story file to any Arabic font you have.

## Make an episode, step by step
1. Pick a story from `guide.md` (arcs 2 to 5 are still unused) and make the folder: `mkdir -p episodes/ep03`
2. Make one vertical 9:16 still per scene (7 scenes is about 40 s). Use any image generator you are allowed to use. Keep one character line in every prompt so the animal looks the same, for example: "Painterly 2D hand-painted animation style, cinematic, vertical 9:16, no text. Main character: Sable, a small gray wolf cub with amber eyes. Scene: ...". Save as `episodes/ep03/ep03_s01.png` ... `ep03_s07.png`.
3. Optional: for money scenes, make a 4 s clip in Google Flow (free tier, 50 credits a day, a clip costs 10, no free video in peak hours) and save it as `episodes/ep03/02.mp4`. A scene with a `clip` uses it; a scene without one animates its `image` locally.
4. Copy a story file: `cp episodes/ep02/story_short.json episodes/ep03/story_short.json` and edit it. One object per scene:
 - `image`: still file name. `clip`: optional Flow clip file name.
 - `motion`: `push`, `pull`, `pan_left` or `pan_right`.
 - `particles`: `dust`, `embers` or `none`.
 - `amp`: motion strength. 1.0 (or leave out) is the gentle ep01 look. 2.0 to 2.8 is the stronger camera move used in ep02 (wider zoom and travel, plus a slight handheld sway).
 - `text`: English narration for the scene (about 10 to 15 words).
 - `caption`: Arabic caption shown on screen (if missing, `text` is shown).
 - Top level: `"lang": "en"`, `"caption_lang": "ar"`, `"voice": "en-US-GuyNeural"`, `"rate": "-8%"`, `"music": "auto"`.
5. Render: `python3 tools/assemble.py episodes/ep03 --story story_short.json --out ep03_short.mp4`
 - Add `--resume` to reuse finished steps after an interruption. If a run was killed mid-step, delete the half-written file in `episodes/ep03/_tmp/` first (a bad `m*.mp4` or `v*.mp4` makes ffmpeg fail with "moov atom not found").
 - Rendering ep02 (7 scenes) takes a few minutes on a small server CPU.
6. Watch it, listen to it (the voice and music are generated, check them), then upload to YouTube as a Short: not made for kids, label AI use if the content looks realistic, no paid promotion.

## Motion on one still (stand-alone)
`python3 tools/motion.py still.png out.mp4 --sec 6 --mode push --particles dust --amp 2.4`
`--amp` scales the zoom (default 1.0). Above 1.0 the camera canvas is larger (1.7x instead of 1.25x), so pans travel further, and a small sway is added.

## Notes
- edge-tts is a free online service and can fail now and then; assemble.py retries 6 times.
- Arabic captions are timed evenly across the spoken line, so they can drift a little from the English words.
- Everything is original: no copied characters, scenes, music or dialogue.
