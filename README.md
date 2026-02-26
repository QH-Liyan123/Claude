# Voice Input for Claude Code

Hold **CapsLock** to speak, release to auto-type text into Claude Code. Supports **Chinese-English mixed input**. Fully offline, powered by [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

## Demo

```
[Hold CapsLock] "帮我写一个 Python function" [Release CapsLock]
  -> Auto-types into Claude Code input
```

## Requirements

- Windows 10/11
- Python 3.10+
- Microphone
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)

## Installation

### Quick Install

```cmd
git clone https://github.com/anthropics/claude-code-voice.git
cd claude-code-voice
install.bat
```

The installer will:
1. Install Python dependencies (`faster-whisper`, `sounddevice`, `pynput`, `numpy`)
2. Copy files to `~/.claude/skills/voice/`
3. Download Whisper Small model (~462MB) from HuggingFace (on first run)
4. Verify installation

### Behind a Proxy?

Set the proxy before running the installer:

```cmd
set HTTPS_PROXY=http://your-proxy-server:port
install.bat
```

## Usage

In Claude Code:

| Command | Action |
|---------|--------|
| `/voice` | Start voice input |
| `/voice stop` | Stop voice input |
| `/voice status` | Check if running |

### How It Works

1. **Hold CapsLock** (0.25s+) to start recording (red indicator appears at top of screen)
2. **Release CapsLock** to recognize and auto-type the text
3. **Say "关闭语音"** or **"stop voice"** to exit voice input
4. Other keys pressed while holding CapsLock are filtered out and won't trigger recognition

## Configuration

### Trigger Key

The default trigger key is **CapsLock**. To change it, edit `voice_input.py`:

```python
# Find this function and change Key.caps_lock to your preferred key
def is_capslock_key(key):
    return key == Key.caps_lock  # Change to Key.ctrl_l, Key.alt_l, Key.scroll_lock, etc.
```

Available keys: `Key.ctrl_l`, `Key.ctrl_r`, `Key.alt_l`, `Key.alt_r`, `Key.scroll_lock`, `Key.pause`, etc.
See [pynput documentation](https://pynput.readthedocs.io/en/latest/keyboard.html#pynput.keyboard.Key) for full list.

### Model Size

Set environment variable before starting to use a different model:

```bash
export VOICE_MODEL_SIZE=medium
```

| Model | Size | Accuracy | Speed |
|-------|------|----------|-------|
| tiny | ~75MB | Basic | Fastest |
| base | ~141MB | Good | Fast |
| small | ~462MB | Better | Moderate |
| medium | ~1.5GB | Great | Slower |
| large-v3 | ~3GB | Best | Slowest |

## Technical Details

| Item | Detail |
|------|--------|
| Speech Engine | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2) |
| Model | Whisper Small (default, supports 99 languages) |
| Inference | CPU int8 quantization, ~1-3s latency |
| Privacy | All processing is local, no data uploaded |

## File Structure

```
voice-skill/
├── README.md           # This file
├── LICENSE             # MIT License
├── .gitignore
├── voice_input.py      # Main voice input script
├── install.bat         # One-click installer
└── skill/
    └── SKILL.md        # Claude Code skill definition
```

## Troubleshooting

### First run is slow
The Whisper model downloads automatically on first run (~462MB). Subsequent runs are fast.

### No sound detected
- Check if your microphone is enabled in Windows settings
- Run `python -c "import sounddevice; print(sounddevice.query_devices())"` to list audio devices

### Model download fails behind proxy
```cmd
set HTTPS_PROXY=http://your-proxy:port
set HF_HUB_DISABLE_SYMLINKS_WARNING=1
python -c "from faster_whisper import WhisperModel; WhisperModel('small')"
```

## License

MIT License - see [LICENSE](LICENSE)

---

Created by Leon Li(李岩) - 20260226
