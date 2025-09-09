from __future__ import annotations
import os
import re
import stat
import json
import hashlib
import shutil
import zipfile
import platform
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Union

try:
    from send2trash import send2trash  # type: ignore
    _HAS_SEND2TRASH = True
except Exception:
    _HAS_SEND2TRASH = False

PathLike = Union[str, Path]


def _to_path(p: PathLike) -> Path:
    return p if isinstance(p, Path) else Path(p)


def _format_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.2f} {u}"
        size /= 1024.0
    return f"{num_bytes} B"


def _get_creation_time(p: Path) -> float:
    """Cross-platform creation time."""
    st = p.stat()
    system = platform.system().lower()
    if system == "windows":
        return st.st_ctime  # ویندوز creation time
    if hasattr(st, "st_birthtime"):
        return st.st_birthtime  # مک جدید
    return st.st_ctime  # fallback روی لینوکس


def _permissions(p: Path) -> dict:
    """Simplified permission model (read/write/execute)."""
    perms = {"read": os.access(p, os.R_OK), "write": os.access(p, os.W_OK), "execute": os.access(p, os.X_OK)}
    return perms


def _valid_filename(name: str) -> bool:
    """Check if filename is valid on current OS."""
    invalid_names = {"con", "prn", "aux", "nul", "com1", "com2", "lpt1", "lpt2"}
    system = platform.system().lower()
    if system == "windows":
        invalid_chars = set('<>:"/\\|?*')
        if any(c in invalid_chars for c in name):
            return False
        if name.lower() in invalid_names:
            return False
    return True


@dataclass
class Entry:
    path: Path
    is_file: bool
    is_dir: bool
    size: int
    mtime: float

    def to_dict(self, human_readable: bool = True) -> dict:
        return {
            "path": str(self.path),
            "name": self.path.name,
            "is_file": self.is_file,
            "is_dir": self.is_dir,
            "size": _format_size(self.size) if human_readable else self.size,
            "modified": datetime.fromtimestamp(self.mtime).isoformat(timespec="seconds"),
        }


class FileManager:
    """
    A cross-platform file manager with consistent behavior on Windows/Linux/Mac.
    """

    def __init__(self, base: PathLike = '.', case_sensitive: bool = True) -> None:
        
        self.base = _to_path(base).expanduser().resolve()
        
        self.case_sensitive = case_sensitive

    def resolve(self, *parts: PathLike) -> Path:
        p = self.base.joinpath(*map(_to_path, parts)).resolve()
        return p

    def exists(self, *parts: PathLike) -> bool:
        return self.resolve(*parts).exists()

    def ls(
        self,
        path: PathLike = ".",
        recursive: bool = False,
        pattern: Optional[str] = None,
        files_only: bool = False,
        dirs_only: bool = False,
    ) -> List[Entry]:
        root = self.resolve(path)
        if not root.exists():
            raise FileNotFoundError(f"Path not found: {root}")

        def _iter(p: Path) -> Iterable[Path]:
            return p.rglob("*") if recursive else p.glob("*")

        rx = re.compile(pattern, re.I if not self.case_sensitive else 0) if pattern else None
        entries: List[Entry] = []
        for item in _iter(root):
            if files_only and not item.is_file():
                continue
            if dirs_only and not item.is_dir():
                continue
            if rx and not rx.search(str(item)):
                continue
            try:
                st = item.stat()
                entries.append(
                    Entry(
                        path=item,
                        is_file=item.is_file(),
                        is_dir=item.is_dir(),
                        size=st.st_size,
                        mtime=st.st_mtime,
                    )
                )
            except FileNotFoundError:
                continue
        return entries

    def read_text(self, path: PathLike, encoding: str = "utf-8") -> str:
        return self.resolve(path).read_text(encoding=encoding)

    def write_text(self, path: PathLike, content: str, encoding: str = "utf-8", append: bool = False) -> Path:
        p = self.resolve(path)
        if not _valid_filename(p.name):
            raise ValueError(f"Invalid filename for this OS: {p.name}")
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with open(p, mode, encoding=encoding) as f:
            f.write(content)
        return p

    def read_bytes(self, path: PathLike) -> bytes:
        return self.resolve(path).read_bytes()

    def write_bytes(self, path: PathLike, data: bytes) -> Path:
        p = self.resolve(path)
        if not _valid_filename(p.name):
            raise ValueError(f"Invalid filename for this OS: {p.name}")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return p

    def mkdir(self, path: PathLike, parents: bool = True, exist_ok: bool = True) -> Path:
        p = self.resolve(path)
        if not _valid_filename(p.name):
            raise ValueError(f"Invalid directory name: {p.name}")
        p.mkdir(parents=parents, exist_ok=exist_ok)
        return p

    def touch(self, path: PathLike, exist_ok: bool = True) -> Path:
        p = self.resolve(path)
        if not exist_ok and p.exists():
            raise FileExistsError(f"File exists: {p}")
        if not _valid_filename(p.name):
            raise ValueError(f"Invalid filename: {p.name}")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()
        return p

    def delete(self, path: PathLike, to_trash: bool = False) -> None:
        p = self.resolve(path)
        if to_trash and _HAS_SEND2TRASH:
            send2trash(str(p))
            return
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()

    def rename(self, path: PathLike, new_name: str) -> Path:
        p = self.resolve(path)
        if not _valid_filename(new_name):
            raise ValueError(f"Invalid filename: {new_name}")
        target = p.with_name(new_name)
        if target.exists():
            raise FileExistsError(f"Target exists: {target}")
        return p.rename(target)

    def stat(self, path: PathLike, human_readable: bool = True) -> dict:
        p = self.resolve(path)
        st = p.stat()
        info = {
            "path": str(p),
            "is_file": p.is_file(),
            "is_dir": p.is_dir(),
            "size": _format_size(st.st_size) if human_readable else st.st_size,
            "modified": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
            "created": datetime.fromtimestamp(_get_creation_time(p)).isoformat(timespec="seconds"),
            "permissions": _permissions(p),
        }
        return info

    def hash_file(self, path: PathLike, algo: str = "sha256", chunk_size: int = 1024 * 1024) -> str:
        p = self.resolve(path)
        h = hashlib.new(algo)
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()

    def zip_dir(self, src: PathLike, zip_path: PathLike, overwrite: bool = False) -> Path:
        s = self.resolve(src)
        z = self.resolve(zip_path)
        if z.exists() and not overwrite:
            raise FileExistsError(f"Zip exists: {z}")
        z.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(z, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in s.rglob("*"):
                if item.is_file():
                    zf.write(item, arcname=item.relative_to(s))
        return z

    def unzip(self, zip_path: PathLike, dst: PathLike, overwrite: bool = False) -> Path:
        z = self.resolve(zip_path)
        d = self.resolve(dst)
        d.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(z, "r") as zf:
            for member in zf.infolist():
                target = d / member.filename
                if target.exists() and not overwrite:
                    raise FileExistsError(f"Destination exists: {target}")
            zf.extractall(d)
        return d


if __name__ == "__main__":
    fm = FileManager(".")
    fm.touch("example.txt")
    fm.write_text("example.txt", "Hello World\n")
    print(fm.read_text("example.txt"))
    print(json.dumps(fm.stat("example.txt"), ensure_ascii=False, indent=2))
    z = fm.zip_dir(".", "example.zip", overwrite=True)
    print("Zipped:", z)
    fm.unzip("example.zip", "unzipped", overwrite=True)
    print("Unzipped to ./unzipped")
