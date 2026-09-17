"""Rebuild the V2 design-axes section with a SCOPED toggle (data-vset) so it
never fights the page's global data-set switch, plus inline styles."""
import re

BASE = "/storage/roatienza.github.io/showcase_s7"
src = open(f"{BASE}/index.html").read()
i = src.find('<section class="tr" id="v2axes"')
j = src.find('</section>', i) + len('</section>')
assert i > 0 and j > i
old = src[i:j]

# 1) scoped attributes instead of the global data-set
new = old.replace('data-set="d6"', 'data-vset="d6"').replace('data-set="v2"', 'data-vset="v2"')
new = new.replace('class="tog"', 'class="vtog"')
new = new.replace("Switch flips every player below.",
                  "Switch flips every player below (scoped to this section; the checkpoint tabs above are untouched).")

# 2) inline styles for the per-prompt rows
new = new.replace('<div class="axrow">',
                  '<div style="display:flex;align-items:center;gap:10px;margin:4px 0">')
new = new.replace('<span class="axp">',
                  '<span style="font:600 11px/1 var(--mono);letter-spacing:.06em;text-transform:uppercase;'
                  'color:var(--dim);min-width:86px">')

# 3) scoped mini-script just before </section>
script = '''  <script>
  (function(){
    var scope = document.getElementById('v2axes');
    var buttons = scope.querySelectorAll('button.vtog');
    function show(which){
      scope.querySelectorAll('audio[data-vset]').forEach(function(a){
        var on = a.dataset.vset === which;
        a.hidden = !on;
        if(!on){ a.pause(); }
      });
      buttons.forEach(function(b){ b.setAttribute('aria-pressed', String(b.dataset.vset === which)); });
      try { localStorage.setItem('irodori-v2axes', which); } catch(e){}
    }
    buttons.forEach(function(b){ b.addEventListener('click', function(){ show(b.dataset.vset); }); });
    var saved = null;
    try { saved = localStorage.getItem('irodori-v2axes'); } catch(e){}
    show(saved && scope.querySelector('button.vtog[data-vset="'+saved+'"]') ? saved : 'v2');
  })();
  </script>
'''
new = new.replace('</section>', script + '</section>')

src = src[:i] + new + src[j:]
open(f"{BASE}/index.html", "w").write(src)
print("rewritten; size", len(src))
print("data-vset count:", src.count("data-vset="), "| vtog:", src.count('button class="vtog"'))
print("leftover global refs in section:", new.count('data-set='))