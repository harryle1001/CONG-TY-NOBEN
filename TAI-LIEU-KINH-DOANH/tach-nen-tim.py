"""Tách nền ảnh sản phẩm Thủy Sản Tím -> assets/tim-cutout/<slug>.webp (nền trong suốt). Cần: pip install "rembg[cpu]"."""
from pathlib import Path
from rembg import new_session, remove
from PIL import Image
SRC = Path(__file__).resolve().parent.parent.parent / 'Thuysantim/public/img/products'
OUT = Path(__file__).resolve().parent / 'assets/tim-cutout'
s = new_session('isnet-general-use')
for f in sorted(SRC.glob('*.webp')):
    im = remove(Image.open(f).convert('RGB'), session=s, post_process_mask=True)
    im = im.crop(im.getbbox())
    im.thumbnail((760, 760)); im.save(OUT / f.name, 'WEBP', quality=86)
    print(f.name, im.size)
