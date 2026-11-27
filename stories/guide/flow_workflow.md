# Making clips with Google Flow (option B, by hand)
Free: 50 Flow credits per day, reset starts at first generation, no rollover. Veo 3.1 Lite: 10 credits per 4/6/8 s clip (5 clips a day). Omni Flash up to 10 s: 1 credit/s at 360p, 3 credits/s at 720p. Peak hours about 2-5 PM UTC (4-7 PM Cairo): video may be unavailable without a subscription.
Steps: 1 write 8 prompts from the story (same character line in every prompt) 2 generate 1 clip per scene in vertical 9:16 3 download as 01.mp4, 02.mp4 ... 4 put them in episodes/epNN/ with story.json 5 run: python tools/assemble.py episodes/epNN
Tip: Flow clips have their own audio; the assembler drops it and uses narration and music.
