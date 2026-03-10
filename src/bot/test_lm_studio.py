#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox


def calculate_text(text: str) -> str:
    """
    Пример функции «обработки» текста.
    Здесь просто возвращаем строку в верхнем регистре,
    но в реальном проекте можно поместить туда любой алгоритм.
    """
    return text.upper()


class TextSplitterApp(tk.Tk):
    """Главное окно приложения."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Текстовый редактор с подсветкой")
        self.geometry("800x500")

        # ──────────────────────  Основной раздвижник  ─────────────── #
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # ──────────────────────  Левая часть (редактируемая)  ─────#
        left_frame = ttk.Frame(self.paned)
        self.left_text = tk.Text(
            left_frame,
            wrap="word",
            undo=True,
            font=("Consolas", 12),
            tabs=(4 * "    ",),  # табы как четыре пробела
        )
        self.left_text.pack(fill=tk.BOTH, expand=True)

        update_btn = ttk.Button(left_frame, text="Обновить", command=self.update_right)
        update_btn.pack(pady=5)

        self.paned.add(left_frame, weight=1)

        # ──────────────────────  Правая часть (только чтение)  ───#
        right_frame = ttk.Frame(self.paned)
        self.right_text = tk.Text(
            right_frame,
            wrap="word",
            state=tk.DISABLED,
            font=("Consolas", 12),
            tabs=(4 * " ",),
        )
        self.right_text.pack(fill=tk.BOTH, expand=True)

        self.paned.add(right_frame, weight=1)

        # ──────────────────────  Подсветка и отслеживание изменений  ───
        self.left_text.bind("<<Modified>>", self.on_left_modified)
        self.left_text.edit_modified(False)          # сброс флага

    # --------------------------------------------------------------------
    def on_left_modified(self, event: tk.Event) -> None:
        """Обработчик события изменения текста в левой области."""
        if not self.left_text.edit_modified():
            return
        self.apply_highlighting()
        self.left_text.edit_modified(False)

    # --------------------------------------------------------------------
    @staticmethod
    def first_visible_char(line: str) -> str | None:
        """
        Возвращает первый не‑таб символ строки.
        Если строка состоит только из табов – возвращается None.
        """
        for ch in line:
            if ch != "\t":
                return ch
        return None

    # --------------------------------------------------------------------
    def apply_highlighting(self) -> None:
        """Подсвечивает в левой области все слова, начиная с первого не‑таб символа."""
        self.left_text.tag_remove("highlight", "1.0", tk.END)

        # Для каждой строки
        for idx in range(1, int(self.left_text.index(tk.END).split('.')[0]) + 1):
            line = self.left_text.get(f"{idx}.0", f"{idx}.end")
            first_char = self.first_visible_char(line)
            if not first_char:
                continue

            # Поиск всех слов, начинающихся с first_char
            start_idx = f"{idx}.0"
            while True:
                pos = self.left_text.search(first_char, start_idx,
                                            stopindex=f"{idx}.end",
                                            regexp=True, nocase=False)
                if not pos:
                    break

                # Слово – последовательность букв/чисел/подчеркивания
                end_pos = f"{pos}+{len(self.left_text.get(pos, pos + 1))}c"
                while self.left_text.get(end_pos) and \
                      self.left_text.get(end_pos).isalnum() or \
                      self.left_text.get(end_pos) == "_":
                    end_pos = f"{end_pos}+1c"

                self.left_text.tag_add("highlight", pos, end_pos)
                start_idx = end_pos

        # Настройка цвета подсветки
        self.left_text.tag_configure(
            "highlight",
            background="#ffeb99",
            foreground="black",
            font=("Consolas", 12, "bold")
        )

    # --------------------------------------------------------------------
    def update_right(self) -> None:
        """Обновляет правую область – результат работы calculate_text."""
        src = self.left_text.get("1.0", tk.END).rstrip("\n")  # удаляем конец строки
        result = calculate_text(src)

        self.right_text.config(state=tk.NORMAL)
        self.right_text.delete("1.0", tk.END)
        self.right_text.insert(tk.END, result)
        self.right_text.config(state=tk.DISABLED)


# ──────────────────────  Запуск программы  --------------------------- #
if __name__ == "__main__":
    app = TextSplitterApp()
    app.mainloop()
