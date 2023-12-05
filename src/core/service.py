import os

from core.constants import MEDIA_ROOT


def create_media_root():
    if not os.path.exists(MEDIA_ROOT):
        os.mkdir(MEDIA_ROOT)


async def count_number_of_pages(num_of_objects: int, page_size: int):
    division: tuple[int, int] = divmod(num_of_objects, page_size)
    pages: int = division[0] + 1 if division[1] else division[0]
    return pages
