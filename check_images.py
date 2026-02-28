import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
import django
django.setup()

from blog.models import Post
from django.conf import settings

print("=== Post Featured Images ===")
for p in Post.objects.all():
    img = p.featured_image
    title = p.title[:55]
    if img:
        full_path = os.path.join(settings.MEDIA_ROOT, str(img))
        exists = os.path.exists(full_path)
        print(f"  {title:55s} | image={img} | file_exists={exists}")
    else:
        print(f"  {title:55s} | image=NONE")

print(f"\n=== Media Settings ===")
print(f"  MEDIA_URL:  {settings.MEDIA_URL}")
print(f"  MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"  DEBUG:      {settings.DEBUG}")

print(f"\n=== Media Directory Contents ===")
media_dir = settings.MEDIA_ROOT
if os.path.exists(media_dir):
    for root, dirs, files in os.walk(media_dir):
        for f in files:
            fpath = os.path.join(root, f)
            size = os.path.getsize(fpath)
            print(f"  {os.path.relpath(fpath, media_dir):40s} ({size} bytes)")
    if not any(os.scandir(media_dir)):
        print("  (empty)")
else:
    print(f"  Media directory does not exist!")
