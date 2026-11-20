"""Join per-line narration WAVs into one track and derive exact timings.

Outputs (in --out): narration.wav, captions.srt, timeline.json (scene + line start/end in seconds).
Captions are the script lines themselves, so subtitles always match the voice-over word for word.
"""

import argparse
import json
import wave
from pathlib import Path

LEAD_IN = 2.0  # title card before the first line
LINE_GAP = 0.45
SCENE_GAP = 0.9
TAIL = 3.0  # end card after the last line


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def wrap(text: str, width: int = 62) -> str:
    """At most two caption lines, broken at a space near the middle when long."""
    if len(text) <= width:
        return text
    mid = len(text) // 2
    left, right = text.rfind(" ", 0, mid + 10), text.find(" ", mid - 10)
    cut = left if left != -1 and (right == -1 or mid - left <= right - mid) else right
    return text[:cut] + "\n" + text[cut + 1 :]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--tts", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    script = json.loads(Path(a.script).read_text(encoding="utf-8"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    params = None
    frames: list[bytes] = []
    t = LEAD_IN
    timeline = {"scenes": [], "lead_in": LEAD_IN}
    srt: list[str] = []

    def silence(seconds: float) -> bytes:
        assert params is not None
        n = int(seconds * params.framerate)
        return b"\x00" * n * params.sampwidth * params.nchannels

    first = True
    for s_idx, scene in enumerate(script["scenes"]):
        if not first:
            t += SCENE_GAP - LINE_GAP
        scene_start = t
        lines = []
        for i, line in enumerate(scene["lines"]):
            path = Path(a.tts) / f"{scene['id']}_{i:02d}.wav"
            with wave.open(str(path)) as w:
                if params is None:
                    params = w.getparams()
                    frames.append(silence(LEAD_IN))
                elif first is False or i > 0:
                    pass
                data = w.readframes(w.getnframes())
                dur = w.getnframes() / w.getframerate()
            if not (s_idx == 0 and i == 0):
                gap = LINE_GAP if i > 0 else SCENE_GAP
                frames.append(silence(gap))
            start, end = t, t + dur
            frames.append(data)
            lines.append({"text": line, "start": round(start, 3), "end": round(end, 3)})
            srt.append(f"{len(srt) + 1}\n{srt_time(start)} --> {srt_time(end + 0.25)}\n{wrap(line)}\n")
            t = end + LINE_GAP
            first = False
        timeline["scenes"].append(
            {"id": scene["id"], "start": round(scene_start, 3), "end": round(t - LINE_GAP, 3), "lines": lines}
        )
    assert params is not None
    frames.append(silence(TAIL))
    total = t - LINE_GAP + TAIL
    timeline["total"] = round(total, 3)

    with wave.open(str(out / "narration.wav"), "wb") as w:
        w.setparams(params)
        for chunk in frames:
            w.writeframes(chunk)
    (out / "captions.srt").write_text("\n".join(srt), encoding="utf-8", newline="\n")
    (out / "timeline.json").write_text(json.dumps(timeline, indent=1), encoding="utf-8", newline="\n")
    print(f"total {total:.1f}s, {len(srt)} captions")


if __name__ == "__main__":
    main()
