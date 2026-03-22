from __future__ import annotations

from service_container import build_container
from ui.main_window import MainWindow


def main() -> None:
    container = build_container()
    app = MainWindow(container)
    app.mainloop()


if __name__ == "__main__":
    main()
