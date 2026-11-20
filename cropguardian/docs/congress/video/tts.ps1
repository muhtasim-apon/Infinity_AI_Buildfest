# Synthesize one WAV per script line with the offline Windows voice (no network, no data leaves the PC).
# Usage: powershell -NoProfile -File tts.ps1 -Script script.json -Out <dir>
param([string]$Script, [string]$Out)
Add-Type -AssemblyName System.Speech
$json = Get-Content -Raw -Encoding UTF8 $Script | ConvertFrom-Json
New-Item -ItemType Directory -Force $Out | Out-Null
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice($json.voice)
$synth.Rate = 0
$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(24000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
foreach ($scene in $json.scenes) {
  $i = 0
  foreach ($line in $scene.lines) {
    $path = Join-Path $Out ("{0}_{1:d2}.wav" -f $scene.id, $i)
    $synth.SetOutputToWaveFile($path, $fmt)
    $synth.Speak($line)
    $i++
  }
}
$synth.SetOutputToNull()
$synth.Dispose()
Write-Output "done"
