# Short format: one episode per day on 50 free Flow credits

Source of the numbers: https://support.google.com/flow/answer/16526234
(50 free credits per day, Veo 3.1 Lite 4/6/8 s clip = 10 credits, so 5 clips per day.
No free video generation in peak hours, about 14:00-17:00 UTC = 16:00-19:00 Cairo.)

## Structure (35-45 s, 7 beats)
| # | Beat | Source | Seconds |
|---|------|--------|---------|
| 1 | Home, the herd running | still + local motion (pull-out, dust) | 5 |
| 2 | Storm, herd lost | FLOW clip 1 (4 s) | 6 |
| 3 | Captured, the rope | FLOW clip 2 (4 s) | 5 |
| 4 | Dream of home | still + local motion (pan, dust) | 6 |
| 5 | Breaks free, runs | FLOW clip 3 (4 s) | 5 |
| 6 | Hears the herd on the ridge | FLOW clip 4 (4 s) | 8 |
| 7 | Return, last frame | FLOW clip 5 (4 s) | 4 |
Total Flow cost: 5 clips x 10 credits = 50 credits. Narration is trimmed to about 8-10 words per beat, so each scene is the clip (4 s) plus a short hold.
Keep the money beats (storm, rope, escape, ridge, return) as Flow clips. Quiet beats (home, dream) are stills with motion.

## How to use
- Generate each clip from the matching scene still as the START FRAME (image-to-video) so Ember keeps his look.
- Name the clips 02.mp4, 04.mp4, 07.mp4, 08.mp4, 03.mp4 or edit "clip" names in story_short.json.
- Run: python3 tools/assemble.py episodes/ep01 --story story_short.json --out ep01_short.mp4
- A scene with no clip falls back to its "image" with local motion (tools/motion.py). Fields: image, motion (push|pull|pan_left|pan_right), particles (dust|embers|none).
- If Flow credits run out mid-episode, the missing clips are replaced by motion stills automatically, so the episode still finishes the same day.
