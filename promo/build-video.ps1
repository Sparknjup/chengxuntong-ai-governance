$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$frameDir = Join-Path $root 'frames'
$clipDir = Join-Path $root 'clips'
$outDir = Join-Path $root 'output'
New-Item -ItemType Directory -Force -Path $clipDir, $outDir | Out-Null

$durations = @(5.2, 6.0, 5.5, 7.0, 7.0, 6.5, 7.0, 7.0, 6.5, 6.5, 10.0, 7.0, 9.0)
$transition = 0.8

for ($index = 0; $index -lt $durations.Count; $index++) {
  $number = $index + 1
  $input = Join-Path $frameDir ('scene-{0:D2}.png' -f $number)
  $output = Join-Path $clipDir ('clip-{0:D2}.mp4' -f $number)
  $motion = if ($number % 2 -eq 0) { 0.00014 } else { 0.00019 }
  $filter = "scale=1080:1920,zoompan=z='min(zoom+$motion,1.035)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,format=yuv420p"
  & ffmpeg -y -hide_banner -loglevel error -framerate 30 -loop 1 -i $input -t $durations[$index] -vf $filter -an -c:v libx264 -preset veryfast -crf 18 -movflags +faststart $output
}

$ffmpegArgs = @('-y', '-hide_banner', '-loglevel', 'error')
for ($index = 1; $index -le $durations.Count; $index++) {
  $ffmpegArgs += @('-i', (Join-Path $clipDir ('clip-{0:D2}.mp4' -f $index)))
}

$filters = @()
$offset = $durations[0] - $transition
$filters += "[0:v][1:v]xfade=transition=fade:duration=$transition`:offset=$offset[v1]"
for ($index = 2; $index -lt $durations.Count; $index++) {
  $offset = $offset + $durations[$index - 1] - $transition
  $previous = $index - 1
  $filters += "[v$previous][$index`:v]xfade=transition=fade:duration=$transition`:offset=$offset[v$index]"
}
$lastLabel = 'v{0}' -f ($durations.Count - 1)
$silentMaster = Join-Path $outDir 'silent-master.mp4'
$ffmpegArgs += @('-filter_complex', ($filters -join ';'), '-map', "[$lastLabel]", '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', $silentMaster)
& ffmpeg @ffmpegArgs

$total = ($durations | Measure-Object -Sum).Sum - ($durations.Count - 1) * $transition
$music = Join-Path $outDir 'ambient-music.wav'
$fadeOutStart = [Math]::Max(0, $total - 5)
$tone = "(0.045*sin(2*PI*55*t)+0.024*sin(2*PI*110*t)+0.016*sin(2*PI*164.81*t)+0.011*sin(2*PI*220*t))*(0.72+0.28*sin(2*PI*0.075*t))"
& ffmpeg -y -hide_banner -loglevel error -f lavfi -i "aevalsrc=$tone`:s=48000`:d=$total" -f lavfi -i "anoisesrc=color=pink`:amplitude=0.012`:sample_rate=48000`:duration=$total" -filter_complex "[0:a]lowpass=f=1400[a0];[1:a]lowpass=f=900[a1];[a0][a1]amix=inputs=2:normalize=0,afade=t=in:st=0:d=3,afade=t=out:st=$fadeOutStart`:d=5,loudnorm=I=-25:TP=-3:LRA=7[a]" -map '[a]' -c:a pcm_s16le $music

$final = Join-Path $outDir '城讯通-城市共治宣传片.mp4'
& ffmpeg -y -hide_banner -loglevel error -i $silentMaster -i $music -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart $final

Write-Output $final
