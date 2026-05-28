from __future__ import annotations

import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from app.config import BASE_DIR, DEFAULT_PICTURE, IMAGES_DIR, IMPORT_DIR, RESOURCES_DIR

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None


def show_error(title: str, message: str) -> None:
    messagebox.showerror(title, message)


def show_info(title: str, message: str) -> None:
    messagebox.showinfo(title, message)


def ask_yes_no(title: str, message: str) -> bool:
    return messagebox.askyesno(title, message)


def _normalize_path_text(path_value: str | None) -> str:
    """Возвращает путь в едином виде.

    В импортных Excel часто встречаются варианты `1.jpg`, `import/1.jpg`,
    `images\\1.jpg` или абсолютные пути. Tkinter работает только с реальным
    файлом, поэтому перед открытием изображения путь нужно привести к одному
    виду и проверить несколько типовых папок проекта.
    """
    return str(path_value or '').strip().replace('\\', '/').replace('file:///', '')


def _case_insensitive_existing_path(path: Path) -> Path | None:
    """Ищет файл без учета регистра расширения/имени.

    На Windows это почти не нужно, но на Linux/macOS `1.JPG` и `1.jpg` — разные
    имена. Функция делает работу приложения устойчивее после импорта.
    """
    if path.exists():
        return path
    parent = path.parent
    if not parent.exists() or not path.name:
        return None
    target_name = path.name.lower()
    for child in parent.iterdir():
        if child.name.lower() == target_name:
            return child
    return None


def _resource_candidates(path_value: str | None) -> list[Path]:
    raw_text = _normalize_path_text(path_value)
    if not raw_text:
        return []

    raw_path = Path(raw_text)
    candidates: list[Path] = []

    if raw_path.is_absolute():
        candidates.append(raw_path)
    else:
        candidates.extend([
            BASE_DIR / raw_path,
            RESOURCES_DIR / raw_path,
            IMAGES_DIR / raw_path,
            IMPORT_DIR / raw_path,
            IMPORT_DIR / 'import' / raw_path,
        ])

    # Если в БД лежит просто `1.jpg`, ищем его в основных папках с ресурсами.
    file_name = raw_path.name
    if file_name:
        candidates.extend([
            IMAGES_DIR / file_name,
            IMPORT_DIR / file_name,
            IMPORT_DIR / 'import' / file_name,
            RESOURCES_DIR / file_name,
        ])

    # Убираем дубли, сохраняя порядок.
    unique_candidates: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate.resolve()) if candidate.is_absolute() else str(candidate)
        if key not in seen:
            unique_candidates.append(candidate)
            seen.add(key)
    return unique_candidates


def resolve_resource_path(path_value: str | None) -> Path:
    for candidate in _resource_candidates(path_value):
        existing = _case_insensitive_existing_path(candidate)
        if existing and existing.is_file():
            return existing

    # Последняя попытка: найти файл по имени рекурсивно в resources.
    raw_text = _normalize_path_text(path_value)
    file_name = Path(raw_text).name if raw_text else ''
    if file_name and RESOURCES_DIR.exists():
        target_name = file_name.lower()
        for child in RESOURCES_DIR.rglob('*'):
            if child.is_file() and child.name.lower() == target_name:
                return child

    return DEFAULT_PICTURE


def load_tk_image(path_value: str | None, size: tuple[int, int] = (120, 80)):
    path = resolve_resource_path(path_value)
    if Image and ImageTk:
        try:
            image = Image.open(path).convert('RGBA')
            image.thumbnail(size)
            return ImageTk.PhotoImage(image)
        except Exception:
            pass
    try:
        return tk.PhotoImage(file=str(path))
    except Exception:
        return None


def copy_and_resize_image(source_path: str, old_relative_path: str | None = None) -> str:
    src = Path(source_path)
    if not src.exists():
        raise ValueError('Выбранное изображение не найдено.')
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    target = IMAGES_DIR / f'product_{src.stem}_{abs(hash(src.as_posix()))}{src.suffix.lower()}'

    if Image:
        image = Image.open(src).convert('RGB')
        image = image.resize((300, 200))
        if target.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
            target = target.with_suffix('.png')
        image.save(target)
    else:
        shutil.copy2(src, target)

    if old_relative_path:
        old_path = resolve_resource_path(old_relative_path)
        try:
            if old_path.exists() and old_path.is_file() and old_path.parent == IMAGES_DIR and old_path != target:
                old_path.unlink()
        except Exception:
            pass

    return str(target.relative_to(RESOURCES_DIR))


def choose_image(old_relative_path: str | None = None) -> str | None:
    filename = filedialog.askopenfilename(
        title='Выберите изображение товара',
        filetypes=[('Изображения', '*.png *.jpg *.jpeg *.gif'), ('Все файлы', '*.*')],
    )
    if not filename:
        return None
    return copy_and_resize_image(filename, old_relative_path)


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=kwargs.get('bg', 'white'))
        self.inner = tk.Frame(self.canvas, bg=kwargs.get('bg', 'white'))
        self.scrollbar = tk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor='nw')
        self.inner.bind('<Configure>', self._on_inner_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

    def _on_inner_configure(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)
