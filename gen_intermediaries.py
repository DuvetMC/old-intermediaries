from requests import get
from glob import glob
import os

stitch_regex = '"[^/]+|com/mojang/.+|net/minecraft/.+|a/.+|b/.+"'

matches: dict[str, tuple[str, str]] = {}
for match in glob('matches/client/**/*.match', recursive=True):
    f, t = os.path.basename(match)[:-6].split('#')
    if f in matches:
        print('Duplicate match for %s -> %s: %s' % (f, t, matches[f]))
        continue

    matches[f] = t, match

stitch_jar = 'stitch.jar'
if not os.path.exists(stitch_jar):
    print('Downloading stitch...')
    with open(stitch_jar, 'wb') as f:
        with get('https://maven.fabricmc.net/net/fabricmc/stitch/0.6.2/stitch-0.6.2-all.jar', stream=True) as r:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

versions_with_previous_match = [v for _, (v, _) in matches.items()]
versions_without_previous_match = [k for k, _ in matches.items() if k not in versions_with_previous_match]

current_item = versions_without_previous_match[0]
while current_item in matches.keys():
    f = current_item
    t, match = matches[f]
    print('Generating intermediary for %s -> %s' % (f, t))
    input_location = 'versions/%s/client.jar' % f
    output_location = 'versions/%s/client.jar' % t
    intermediary_in = 'intermediaries/%s.tiny' % f
    intermediary_out = 'intermediaries/%s.tiny' % t

    function = 'java -Dstitch.counter=counter.txt -jar %s updateIntermediary %s %s %s %s %s -p %s' % (
        stitch_jar, input_location, output_location, intermediary_in, intermediary_out, match, stitch_regex
    )

    ret = os.system(function)
    if ret != 0:
        print('Failed to generate intermediary for %s -> %s (exit code %d)' % (f, t, ret))
        exit(1)
    
    current_item = t
