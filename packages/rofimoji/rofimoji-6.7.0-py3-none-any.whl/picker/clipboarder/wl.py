from subprocess import run

from ..abstractionhelper import is_installed, is_wayland
from ..typer.typer import Typer
from .clipboarder import Clipboarder


class WlClipboarder(Clipboarder):
    @staticmethod
    def supported() -> bool:
        return is_wayland() and is_installed("wl-copy")

    @staticmethod
    def name() -> str:
        return "wl-copy"

    def copy_characters_to_clipboard(self, characters: str) -> None:
        run(["wl-copy"], input=characters, encoding="utf-8")

    def copy_paste_characters(self, characters: str, active_window: str, typer: Typer) -> None:
        old_clipboard_content = run(args=["wl-paste", "--type", "text"], capture_output=True, encoding="utf-8")
        old_primary_content = run(args=["wl-paste", "--primary", "type", "text"], capture_output=True, encoding="utf-8")

        run(args=["wl-copy"], input=characters, encoding="utf-8")
        run(args=["wl-copy", "--primary"], input=characters, encoding="utf-8")

        typer.insert_from_clipboard(active_window)

        if old_clipboard_content.returncode == 0:
            run(args=["wl-copy"], input=old_clipboard_content.stdout, encoding="utf-8")
        if old_primary_content.returncode == 0:
            run(args=["wl-copy", "--primary"], input=old_primary_content.stdout, encoding="utf-8")
