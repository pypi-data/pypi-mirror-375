import glob
import traceback
from pathlib import Path
from subprocess import check_call, DEVNULL

from hypy_utils import printc
from rich.progress import track

defaults = {
    'av1': {
        '-c:v': 'libsvtav1',
        '-crf': '36',
        '-preset': '8',
        '-c:a': 'libopus',
        '-b:a': '96k',
        '-vbr': 'on',
    },
    'x264': {  # For older devices
        '-c:v': 'libx264',
        '-crf': '23',
        '-preset': 'medium',
        '-c:a': 'aac',
        '-b:a': '128k',
    },
    'mp3': {  # V0
        '-c:a': 'libmp3lame',
        '-q:a': '0',
    },
    'opus': {
        '-c:a': 'libopus',
        '-b:a': '192k',
        '-vbr': 'on',
    },
    'flac': {
        '-c:a': 'flac',
        '-compression_level': '7',
    },
    'wav': {
        '-c:a': 'pcm_s16le',
    }
}
suffixes = {
    'av1': '.av1-{-crf}.mp4',
    'x264': '.x264-{-crf}.mp4',
    'mp3': '.v{-q:a}.mp3',
    'opus': '.v{-b:a}.opus',
    'flac': '.flac',
    'wav': '.wav',
}


def main(fmt: str, files: list[str], keep: bool, passthrough: list[str], quiet: bool = False, silent: bool = False):
    printq = printc if not silent else lambda *a, **k: None
    quiet = quiet or silent
    # Process each file provided on the command line
    files = [
        Path(p)
        for pattern in files
        for p in glob.glob(str(Path(pattern).expanduser()))
        if Path(p).is_file()
    ]
    total_orig_size, total_new_size = 0, 0
    printc(f"&e> Using format: {fmt}")
    printc(f"&e> Found {len(files)} files to process.")
    printc(f"&e> Keep original files: {'Yes' if keep else 'No'}")
    printc(f"&e> Passthrough parameters: {passthrough if passthrough else 'None'}")
    print()
    for inf in track(files):
        printq("&e-----------------------------------------")
        try:
            params: dict[str, str | None] = defaults[fmt].copy()
            old_size = inf.stat().st_size
            if quiet:
                params['-y'] = None  # Overwrite output files without asking

            # Check for any passthrough arguments and add them to params (overrides defaults)
            i = 0
            while i < len(passthrough):
                k = passthrough[i]
                # Check if next item exists and is not a flag (i.e., it's a value)
                if i + 1 < len(passthrough) and not passthrough[i+1].startswith('-'):
                    v = passthrough[i+1]
                    printq(f"&a> Overriding parameter: {k} {v} (was {params.get(k, 'not set')})")
                    params[k] = v
                    i += 2
                else:  # It's a standalone flag
                    printq(f"&a> Overriding parameter: {k} (was {params.get(k, 'not set')})")
                    params[k] = None  # Use None to signify a flag without a value
                    i += 1

            end = suffixes[fmt]
            for ph, v in params.items():
                end = end.replace(f'{{{ph}}}', str(v) if v is not None else '')
            end = ''.join(c for c in end if c.isalnum() or c in ' ._-+').rstrip()

            if inf.name.endswith(end):
                printq(f"&c> Error: File already has target suffix '{end}', skipping: {inf.name}")
                continue
            ouf = inf.with_name(f'{inf.stem}{end}')
            printq(f"&e+ Compressing '{inf.name}' > '{ouf.name}'")

            # Construct and run the ffmpeg command
            cmd = ['ffmpeg', '-hide_banner', '-i',
                   str(inf),
                   *sum(([k] if v is None else [k, str(v)] for k, v in params.items()), []),
                   str(ouf)]
            printq(f"&e> Running command: {' '.join(cmd)}")

            check_call(cmd) if not quiet else check_call(cmd, stdout=DEVNULL, stderr=DEVNULL)
            printq(f"&a> Compression successful :)")
            new_size = ouf.stat().st_size
            ratio = new_size / old_size
            printq(f"&a> Size: {old_size / 1_000_000:.2f} MB -> {new_size / 1_000_000:.2f} MB ({ratio:.2%})")

            total_orig_size += old_size
            total_new_size += new_size

            if not keep:
                if new_size >= old_size:
                    printc(f"&c! Warning: Compressed file is not smaller than original. Keeping original file :(")
                else:
                    printq(f"&e- Removing original file: '{inf.name}'")
                    inf.unlink()
                    printq(f"&a> Original file removed.")

            printq('')

        except Exception as e:
            printc(f"&c! An error occurred while processing {inf.name}: {e}")
            printc("&c! Leaving original file intact.\n")
            traceback.print_exc()

    # Print summary
    if total_orig_size > 0:
        total_ratio = total_new_size / total_orig_size
        printc("&a=========================================")
        printc(f"&a> Processed {len(files)} files.")
        printc(f"&a> Total size: {total_orig_size / 1_000_000:.2f} MB -> {total_new_size / 1_000_000:.2f} MB ({total_ratio:.2%})")
        printc("&a=========================================")
    else:
        printc("&c! Nothing to do")
