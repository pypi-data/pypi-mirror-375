# formtool

Easy ffmpeg shortcuts

- [x] Can batch convert files
- [x] Automatically use best settings
- [x] You can override params
- [x] Deletes original files if you want
- [x] Shortcuts that are actually short

## Install

```bash
pip install formtool
```

## Usage

```bash
# Compress everything to flac, save space without losing quality
fflac **/*.wav

# If you want to send some music but flac is too big: convert to mp3 v0
fmp3 song.flac

# If you want to archive videos
fav1 *.mp4

# If you want to send videos to telegram
fx264 video.mkv
```