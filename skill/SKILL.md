---
name: voice
description: Voice input for Claude Code. Hold CapsLock to speak, text auto-types into Claude Code input. Say "关闭语音" or "stop voice" to exit. Use when user wants voice input, speech-to-text, or hands-free interaction with Claude Code.
---

# Voice Input Skill

Enables voice input for Claude Code using local speech recognition (faster-whisper). Supports Chinese-English mixed input. No cloud services, fully offline.

## Usage

### Start voice input: `/voice`

Run this command to start the voice listener in the background:

```bash
INSTALL_DIR="$HOME/.claude/skills/voice"; rm -f "$INSTALL_DIR/voice_input.pid" "$INSTALL_DIR/voice_input.log"; pythonw "$INSTALL_DIR/voice_input.py" & sleep 10 && tail -5 "$INSTALL_DIR/voice_input.log" && cat "$INSTALL_DIR/voice_input.pid"
```

Then tell the user:
- Voice input is active
- **Hold CapsLock** to speak (hold for 0.25s+ to activate)
- Release CapsLock to auto-type the recognized text
- Say **"关闭语音"**, **"stop voice"** or similar to exit

### Stop voice input: `/voice stop`

```bash
taskkill //F //IM pythonw.exe 2>/dev/null; rm -f "$HOME/.claude/skills/voice/voice_input.pid"; echo "Voice input stopped"
```

### Check status: `/voice status`

```bash
INSTALL_DIR="$HOME/.claude/skills/voice"; if [ -f "$INSTALL_DIR/voice_input.pid" ]; then PID=$(cat "$INSTALL_DIR/voice_input.pid"); kill -0 $PID 2>/dev/null && echo "Voice input is running (PID: $PID)" || echo "Voice input is not running"; else echo "Voice input is not running"; fi
```

## Important Notes

- The script uses `pythonw` (no console window) to run in background
- Logs are written to `~/.claude/skills/voice/voice_input.log`
- Uses faster-whisper with Whisper small model (downloads automatically on first run)
- Model is cached in HuggingFace cache directory

## Configuration

Set environment variable to use a different model size:

```bash
export VOICE_MODEL_SIZE=medium  # Options: tiny, base, small, medium, large-v3
```

---
Created by Leon Li(李岩) - 20260226
