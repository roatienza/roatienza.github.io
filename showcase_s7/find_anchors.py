src = open('index.html').read()
import re
for pat in ('</section>', 's79bperf', 's710perf', 'id="perf', 's79b'):
    ms = [(src[:m.start()].count(chr(10))+1) for m in re.finditer(pat, src)]
    print(pat, '->', ms[-8:])
