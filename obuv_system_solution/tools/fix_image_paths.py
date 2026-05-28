"""Починка путей к фотографиям товаров.

Запуск:
    python tools/fix_image_paths.py

Скрипт полезен, если товары импортировались из Excel, но фотографии не
показываются: он ищет изображения в resources/images, resources/import и
resources/import/import, копирует найденные файлы в resources/images и обновляет
поле products.image_path в базе данных.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import IMAGES_DIR, IMPORT_DIR, RESOURCES_DIR
from app.db import get_connection
from app.ui.widgets import resolve_resource_path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def collect_images() -> dict[str, Path]:
    images: dict[str, Path] = {}
    for directory in [IMAGES_DIR, IMPORT_DIR, IMPORT_DIR / 'import', RESOURCES_DIR]:
        if not directory.exists():
            continue
        for file in directory.rglob('*'):
            if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS:
                images.setdefault(file.name.lower(), file)
                images.setdefault(file.stem.lower(), file)
    return images


def copy_to_images(source: Path) -> str:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    target = IMAGES_DIR / source.name
    if source.resolve() != target.resolve():
        if target.exists() and target.stat().st_size != source.stat().st_size:
            target = IMAGES_DIR / f'{source.stem}_{abs(hash(str(source.resolve())))}{source.suffix.lower()}'
        if not target.exists():
            shutil.copy2(source, target)
    return str(target.relative_to(RESOURCES_DIR)).replace('\\', '/')


def find_image_for_product(row: dict, index: int, images: dict[str, Path]) -> Path | None:
    candidates: list[str] = []
    image_path = str(row.get('image_path') or '').strip().replace('\\', '/')
    if image_path:
        resolved = resolve_resource_path(image_path)
        if resolved.exists() and resolved.name != 'picture.png':
            return resolved
        candidates.extend([Path(image_path).name, Path(image_path).stem])

    article = str(row.get('article') or '').strip()
    product_id = str(row.get('product_id') or '').strip()
    for value in [article, product_id, str(index)]:
        if value:
            candidates.extend([value, f'{value}.jpg', f'{value}.jpeg', f'{value}.png'])

    for candidate in candidates:
        key = candidate.lower()
        if key in images:
            return images[key]
        stem = Path(candidate).stem.lower()
        if stem in images:
            return images[stem]
    return None


def main() -> None:
    images = collect_images()
    fixed = 0
    not_found = 0

    with get_connection() as conn:
        rows = [dict(row) for row in conn.execute(
            'SELECT product_id, article, product_name, image_path FROM products ORDER BY product_id'
        ).fetchall()]

        for index, row in enumerate(rows, start=1):
            found = find_image_for_product(row, index, images)
            if found:
                new_path = copy_to_images(found)
                conn.execute(
                    'UPDATE products SET image_path = ?, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?',
                    (new_path, row['product_id']),
                )
                fixed += 1
            else:
                not_found += 1
        conn.commit()

    print(f'Обновлено путей к изображениям: {fixed}')
    print(f'Изображения не найдены для товаров: {not_found}')
    print('После этого запустите приложение заново: python run.py')


if __name__ == '__main__':
    main()
