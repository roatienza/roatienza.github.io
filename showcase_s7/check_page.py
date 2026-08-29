src = open('index.html').read()
for a in ('earcheck11','s710perf'):
    print(a, 'id:', src.count(f'id="{a}"'), 'href:', src.count(f'href="#{a}"'))
print('sections:', src.count('<section'), 'closes:', src.count('</section>'))
print('S7.10 flac refs:', src.count('_S7.10.flac'))
print('s79b flac refs:', src.count('_s79b.flac'))
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]; self.errs=[]
    def handle_starttag(self, tag, attrs):
        if tag not in ('br','img','meta','link','input','hr'): self.stack.append(tag)
    def handle_endtag(self, tag):
        if self.stack and self.stack[-1]==tag: self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack[-1]!=tag: self.errs.append('unclosed '+self.stack.pop())
            self.stack.pop()
        else: self.errs.append('stray /'+tag)
p=P(); p.feed(src)
print('parser errors:', p.errs[:5], 'leftover stack:', p.stack[:5])
