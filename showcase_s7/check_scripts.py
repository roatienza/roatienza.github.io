import re
src = open("/storage/roatienza.github.io/showcase_s7/index.html").read()
scripts = re.findall(r"<script>(.*?)</script>", src, re.S)
print("scripts:", len(scripts))
for i, s in enumerate(scripts):
    print(i, "braces", s.count("{") - s.count("}"), "parens", s.count("(") - s.count(")"), "len", len(s))