"""Generate small silent MP3 placeholders for the meditation MVP.

Browsers can decode minimal MPEG-1 Layer III frames with zeroed side info as
silent audio. This script writes two placeholder files used purely so the
audio player has something to spin on. Replace with real meditations before
shipping anything beyond a UI demo.

Frame config: MPEG-1 Layer III, 32 kbps, 44.1 kHz, mono, no CRC.
Frame size = 144 * 32000 / 44100 = 104 bytes (no padding).
Header bytes: FF FB 10 C0
  FF FB - sync + MPEG-1 + Layer III + no-CRC
  10    - 32 kbps + 44.1 kHz + no padding + private 0
  C0    - mono + no mode-ext + no copyright + no original + no emphasis
"""

from pathlib import Path

FRAME = bytes([0xFF, 0xFB, 0x10, 0xC0]) + bytes(100)  # 4 + 100 = 104 bytes
FRAMES_PER_SECOND = 44100 / 1152  # ~38.28 frames/s for Layer III


def silent_mp3(seconds: float) -> bytes:
    return FRAME * round(seconds * FRAMES_PER_SECOND)


def main() -> None:
    out_dir = Path(__file__).parent / "tracks"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "placeholder-breath-5min.mp3").write_bytes(silent_mp3(8))
    (out_dir / "placeholder-bodyscan-10min.mp3").write_bytes(silent_mp3(12))
    print("Wrote 2 placeholder MP3s to", out_dir)


if __name__ == "__main__":
    main()
