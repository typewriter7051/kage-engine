# `kage-python`: A Python Implementation of Kage Engine

Kage Engine is a glyph generation engine for Chinese Characters (漢字、汉字), which is mainly developed by [@kamichikoichi](https://github.com/kamichikoichi/kage-engine) (上地宏一) and [@kurgm](https://github.com/kurgm/kage-engine). 

Based on @kurgm's nodejs implementation, this repository focuses on drawing Chinese character glyphs entirely with Bézier curves instead of the previous polygons.

# Example Usage

Firstly, You should download `dump_newest_only.txt` or `dump_all_versions.txt` from [GlyphWiki](https://glyphwiki.org/wiki/GlyphWiki:%e9%ab%98%e5%ba%a6%e3%81%aa%e6%b4%bb%e7%94%a8%e6%96%b9%e6%b3%95).

```python
from kage import Kage
from kage.font.sans import Sans
#from kage.font.serif import Serif # Uncomment if you want serif instead.
import os
import multiprocessing

# Set the flag `ignore_component_version` if you want to use the glyph data in `dump_newest_only.txt`.
# This is because `dump_newest_only.txt` only contains the latest version of components.
# However, glyphs in `dump_newest_only.txt` may reference older versions of multiple components.
dump_path = 'dump_newest_only.txt'
k = Kage(dump_path=dump_path, ignore_component_version=True, font=Sans())

# If you want to add your own glyph data from outside the dump file, simply
# push the glyph name (see https://en.glyphwiki.org/wiki/GlyphWiki:AddingGlyphs#i6
# for naming guidelines) and data.
k.components.push("u2ff0-u53c8-u53b6", "99:0:0:0:0:200:200:u53c8-01:0:0:0$99:0:0:0:0:200:200:u53b6-02:0:0:0");

# Generate a glyph.
def gen(i: int):
    key = f'u{i:x}'
    canvas = k.make_glyph(name=key)
    canvas.saveas(os.path.join('./output', f'{key}.svg'))

# Parallel generation.
if __name__ == '__main__':
    with multiprocessing.Pool(16) as pool:
        pool.map(gen, list([0x6708, 0x6c23, 0x6728, 0x9ed1, 0x6230])) 
        # or maybe you wanna generate the basic CJK Unified Ideographs:
        # range(0x4E00, 0x9FA5 + 1)
```

# Sample

<img src="https://github.com/HowardZorn/kage-engine/raw/dev/output/u5f71.svg" />

<img src="https://github.com/HowardZorn/kage-engine/raw/dev/output/u5f71_serif.svg">

u+5f71，“影”

# Japanese Names

Various stroke detail names occur in romaji which I do not fully understand, here is my progress.

|Kana|Chinese|
|:-:|:-:|
|Hane|鉤|
|Mage|?|
|Tate|竪|
|Kakato|?|
|Uroko|?|
|Uroko2|?|
|Kirikuchi|捺/撇|
|Hori|?|

# TODO

- Serif: Algorithms for drawing offset curves with variable displacement have not been designed.

- doc: Lack of Documentation.

- Bezier Serif stroke drawer.

- Clean up font/stroke inheritance model (partially done).

# Scholarship Information

[Kamichi Koichi](https://github.com/kamichikoichi) wrote a paper about his Kage Engine:

- Koichi KAMICHI (上地 宏一), KAGE - An Automatic Glyph Generating Engine For Large Character Code Set, 「書体・組版ワークショップ報告書」, pp.85-92, Glyph and Typesetting Workshop(書体・組版ワークショップ 京都大學21世紀COE 東アジア世界の人文情報學研究教育據點), 2003年11月28-29日, 京都大学人文科学研究所.
