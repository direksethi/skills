---
name: video-finish
description: Finish a talking-head or screen-recording video with ffmpeg using the talking-head-video-tools CLIs. Tightens pauses without changing pitch, retimes a screen recording to its voiceover, adds a punch-in zoom on every jump cut, burns in word-highlight captions, and cleans the voice track. Use when asked to edit, tighten, caption, retime or finish a talking-head video, a reel, or a narrated screen recording.
---

# Video finish

Turn raw footage into a finished short video with the single-purpose CLIs in [talking-head-video-tools](https://github.com/direksethi/talking-head-video-tools). Every step is a command that reads files and writes files, so each one can be checked before the next runs.

## Setup

1. Confirm `ffmpeg` and `ffprobe` are on PATH and that ffmpeg has libx264 and libass (`ffmpeg -filters | grep ass`).
2. Clone the tools once and install their requirements in a virtual environment:

   ```sh
   git clone https://github.com/direksethi/talking-head-video-tools.git
   cd talking-head-video-tools && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
   ```

3. Work in a scratch folder next to the footage. Never overwrite a source file: every command writes a new output.

## Step 1: word timestamps

Most tools need `words.json`, which says when each word of the voice track is spoken. Produce it from a Whisper transcript made with word timestamps enabled:

```sh
whisper voice.wav --model small --word_timestamps True --output_format json
python whisper_words.py voice.json words.json --audio voice.wav
```

Read the transcript before continuing. Speech-to-text misspells names and product terms, and those words become the burned-in captions. Correct the text in `words.json` and keep the timings.

## Step 2: choose the path

**Talking head, cut from one take.** Use when a person speaks to camera.

1. Tighten the voice: `python tighten.py --help` lists the gap and tempo controls. It shortens pauses between words, speeds speech without changing pitch, and writes matching word timestamps. Use the tightened audio and the new `words.json` from here on.
2. Decide the cuts: a JSON list of `[in, out]` pairs in seconds, one per kept segment, written to `cuts.json`.
3. Finish: `python reel.py video.mp4 cuts.json words.json out.mp4` adds a punch-in zoom on each cut and word-highlight captions. `--max-words` sets words per caption line and `--anchor-y` moves the captions off the face.

**Narrated screen recording.** Use when a voiceover explains what happens on screen.

1. Write `cues.json`: for each step, the phrase in the voiceover that starts it and the `in` and `out` seconds of the matching action in the recording. See `examples/cues.json` in the tools repository.
2. Retime: `python retime_to_voice.py recording.mp4 voice.wav words.json cues.json out.mp4` stretches or compresses each step so it lasts as long as its spoken line.

A cue phrase must appear in `words.json` exactly as transcribed. If the tool reports `cue not found`, fix the phrase, not the timings.

## Step 3: voice track

Apply one of the two filter chains in `presets/` with `ffmpeg -af "$(cat presets/voice-clean.txt)"`: `voice-clean.txt` for a clean recording, `voice-raw-mic.txt` for a noisy one. Both end in a loudness normaliser. Measure the result with `ffmpeg -af ebur128` rather than trusting the target.

## Step 4: check before handing over

- `ffprobe` the output: duration, resolution, frame rate and audio stream are what was asked for.
- Extract three frames (`ffmpeg -ss <t> -frames:v 1`) at a cut, mid-sentence and the end, and look at them: captions are inside the frame, not over the face, and the highlighted word matches the audio at that moment.
- Play the first and last two seconds for clipped words.

Report what was produced, the checks that passed, and anything that could not be verified.

## Limits

- The tools do not choose the cuts or write the cue list. That is editorial judgment: propose them and confirm with the user when the footage is long or the intent is unclear.
- Captions use the font named by `--font`. If it is not installed, libass substitutes another without warning, so confirm the font exists first.
