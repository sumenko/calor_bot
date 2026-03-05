import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, simpledialog
from fast_calc_core import FastTabCalc
import os

TAB_COLOR = "#dddddd"
SPACE_COLOR = "#bbbbbb"
FONT_SIZE = 9

def calculate_from_text(text: str) -> str:
    lines = text.count("\n") + 1 if text else 0
    words = len(text.split())
    chars = len(text)
    return f"Lines: {lines}\nWords: {words}\nChars: {chars}"


class LineNumbers(tk.Canvas):
    """Номера строк"""

    def __init__(self, text_widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_widget = text_widget

    def redraw(self):
        self.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            line = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=line, fill="gray")
            i = self.text_widget.index(f"{i}+1line")


class App:    
    symbol_colors = {
        "#": "#909090",   # серый для комментариев
        "$": "#00fac0",   # светло-желтый
        "!": "#00b0ff"    # красный для ошибок
    }

    def __init__(self, root):
        self.document_changed = False
        self.root = root
        self.root.title("Text Processor IDE")
        self.root.geometry("1200x700")

        self.create_menu()
        self.create_widgets()

        self.root.bind("<F5>", self.run_calculation)
        self.root.bind_all("<Key>", self.global_hotkey)
        self.text.bind("<Control-MouseWheel>", self.ctrl_mouse_scroll)
        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)


    # self.highlight_lines_by_symbol(symbol_colors)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.exit_program)
        menubar.add_cascade(label="Файл", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Найти (Ctrl+F)", command=self.find_text)
        menubar.add_cascade(label="Правка", menu=edit_menu)

        self.root.config(menu=menubar)

    def create_widgets(self):
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        # Используем grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)  # левый
        container.grid_columnconfigure(2, weight=1)  # правый

        # Левый фрейм
        left_outer = tk.Frame(container)
        left_outer.grid(row=0, column=0, sticky="nsew")  # растягивается

        self.text = tk.Text(left_outer, wrap="none", font=("Consolas", FONT_SIZE), undo=True)
        self.lines = LineNumbers(self.text, width=40, background="#f0f0f0")
        scroll = tk.Scrollbar(left_outer, command=self.on_scroll)
        self.text.configure(yscrollcommand=self.on_textscroll)

        # self.lines.pack(side="left", fill="y")
        scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        # Средний фрейм с кнопкой (фиксированная ширина)
        mid = tk.Frame(container, width=80)
        mid.grid(row=0, column=1, sticky="ns")
        tk.Button(mid, text="▶ Run\n(F5)", command=self.run_calculation, width=8, height=4).pack(pady=20)

        # Правый фрейм
        right_frame = tk.Frame(container)
        right_frame.grid(row=0, column=2, sticky="nsew")

        # PanedWindow с вертикальным разделением
        self.right_pane = ttk.Panedwindow(
            right_frame,
            orient="vertical"
        )
        self.right_pane.pack(fill="both", expand=True)

        # ----- верхняя панель (результат) -----
        top_frame = tk.Frame(self.right_pane)

        self.result = tk.Text(
            top_frame,
            wrap="word",
            font=("Consolas", FONT_SIZE),
            undo=True
        )
        self.result.pack(fill="both", expand=True)

        # ----- нижняя панель (лог / доп. вывод) -----
        bottom_frame = tk.Frame(self.right_pane)

        self.info = tk.Text(
            bottom_frame,
            wrap="word",
            font=("Consolas", FONT_SIZE)
        )
        self.info.pack(fill="both", expand=True)

        # добавляем панели
        self.right_pane.add(top_frame)
        self.right_pane.add(bottom_frame)


        # --- теги подсветки ---
        self.text.tag_configure("tab", background=TAB_COLOR)
        self.text.tag_configure("space", foreground=SPACE_COLOR)
        self.text.tag_configure("current_line", background="#ffffcc")
        self.text.tag_configure("search", background="#ffcc66")

        # бинды
        self.text.bind("<KeyRelease>", lambda e: [self.refresh_visuals(), self.check_document_changed(), self.highlight_lines_by_symbol(self.symbol_colors)])
        self.text.bind("<ButtonRelease>", self.refresh_visuals)
        self.result.bind("<KeyRelease>", lambda e: self.check_document_changed())
        self.root.bind_all("<Alt-Up>", lambda e: self.move_lines(-1))
        self.root.bind_all("<Alt-Down>", lambda e: self.move_lines(1))
        self.root.bind_all("<Alt-Shift-Up>", lambda e: self.duplicate_lines(-1))
        self.root.bind_all("<Alt-Shift-Down>", lambda e: self.duplicate_lines(1))                
        self.text.insert("1.0", self.default_data())
        # self.root.bind_all("<Control-h>", lambda e: (self.open_search_replace(), "break"))
        self.refresh_visuals()
        self.root.after(200, self.init_pane_position)  


    def init_pane_position(self):

        height = self.right_pane.winfo_height()
        if height > 0:
            self.right_pane.sashpos(0, int(height * 0.8))


    def global_hotkey(self, event):
        ctrl = (event.state & 0x4) != 0  # проверяем, что Ctrl зажат
    
        key_code = event.keycode
        key_sym = event.keysym.lower()
    
        if ctrl:
            # print('ctrl+', key_code, key_sym)
            if key_code == ord('A') and key_sym != 'a':        # Ctrl+A
                self.select_all()
            elif key_code == ord('C') and key_sym != 'c':      # Ctrl+C
                self.root.focus_get().event_generate("<<Copy>>")
            elif key_code == ord('V') and key_sym != 'v':      # Ctrl+V
                self.root.focus_get().event_generate("<<Paste>>")
            elif key_code == ord('Q'):      # Ctrl+V
                self.exit_program()
            elif key_code == ord('F'):      # Ctrl+F
                self.find_text()
            elif key_code == ord('H'):      # Ctrl+F
                self.open_search_replace()
            if key_code == ord('S'):        # Ctrl+A
                self.save_file()
        return "break"

    # TODO
    def highlight_lines_by_symbol(self, symbol_colors: dict):
        """
        Подсвечивает строки в левом или правом редакторе, которые начинаются с символов из словаря.
        symbol_colors = {'#': 'lightgray', '$': 'yellow'}
        """

        for widget in (self.text, self.result):  # редактируемые окна
            # сначала удаляем старые теги
            for tag in widget.tag_names():
                if tag.startswith("symbol_"):
                    widget.tag_delete(tag)

            lines = widget.get("1.0", "end-1c").split("\n")
            for i, line in enumerate(lines):
                stripped = line.lstrip()
                if not stripped:
                    continue
                first_char = stripped[0]
                if first_char in symbol_colors:
                    tag_name = f"symbol_{first_char}"
                    # если тег ещё не создан — создаём
                    if tag_name not in widget.tag_names():
                        widget.tag_config(tag_name, background=symbol_colors[first_char])
                    # добавляем тег на строку
                    widget.tag_add(tag_name, f"{i+1}.0", f"{i+1}.0 lineend")

    # TODO
    def duplicate_lines(self, direction):
        widget = self.root.focus_get()

        if widget not in (self.text, self.result):
            return "break"

        start_line, end_line = self._get_selected_lines(widget)

        start = f"{start_line}.0"
        end = f"{end_line+1}.0"

        block = widget.get(start, end)

        if direction == -1:
            widget.insert(start, block)
            new_start = start_line
        else:
            widget.insert(end, block)
            new_start = end_line + 1

        widget.tag_remove("sel", "1.0", "end")
        widget.tag_add(
            "sel",
            f"{new_start}.0",
            f"{new_start + (end_line-start_line)+1}.0"
        )

        widget.mark_set("insert", f"{new_start}.0")

        return "break"
        
    # TODO
    def move_lines(self, direction):
        widget = self.root.focus_get()

        if widget not in (self.text, self.result):
            return "break"

        start_line, end_line = self._get_selected_lines(widget)
        last_line = int(widget.index("end-1c").split(".")[0])

        if direction == -1 and start_line == 1:
            return "break"

        if direction == 1 and end_line == last_line:
            return "break"

        start = f"{start_line}.0"
        end = f"{end_line+1}.0"

        block = widget.get(start, end)

        if direction == -1:
            # строка над блоком
            above_start = f"{start_line-1}.0"
            above_end = f"{start_line}.0"
            above_line = widget.get(above_start, above_end)

            widget.delete(above_start, end)
            widget.insert(above_start, block + above_line)

            new_start = start_line - 1

        else:
            # строка под блоком
            below_start = f"{end_line+1}.0"
            below_end = f"{end_line+2}.0"
            below_line = widget.get(below_start, below_end)

            widget.delete(start, below_end)
            widget.insert(start, below_line + block)

            new_start = start_line + 1

        # восстановить выделение
        widget.tag_remove("sel", "1.0", "end")
        widget.tag_add(
            "sel",
            f"{new_start}.0",
            f"{new_start + (end_line-start_line)+1}.0"
        )

        widget.mark_set("insert", f"{new_start}.0")

        return "break"

    def open_search_replace(self):
        widget = self.root.focus_get()
        if widget not in (self.text, self.result):
            return

        top = tk.Toplevel(self.root)
        top.title("Поиск и замена")
        top.transient(self.root)
        top.resizable(False, False)

        tk.Label(top, text="Найти:").grid(row=0, column=0, sticky="e")
        find_entry = tk.Entry(top, width=30)
        find_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Заменить на:").grid(row=1, column=0, sticky="e")
        replace_entry = tk.Entry(top, width=30)
        replace_entry.grid(row=1, column=1, padx=5, pady=5)

        # Функция поиска
        def do_find():
            widget.tag_remove("search_match", "1.0", "end")
            target = find_entry.get()
            if not target:
                return
            start = "1.0"
            while True:
                pos = widget.search(target, start, stopindex="end")
                if not pos:
                    break
                end = f"{pos}+{len(target)}c"
                widget.tag_add("search_match", pos, end)
                start = end
            widget.tag_config("search_match", background="yellow")

        # Функция замены
        def do_replace():
            target = find_entry.get()
            replacement = replace_entry.get()
            if not target:
                return
            start = "1.0"
            while True:
                pos = widget.search(target, start, stopindex="end")
                if not pos:
                    break
                end = f"{pos}+{len(target)}c"
                widget.delete(pos, end)
                widget.insert(pos, replacement)
                start = f"{pos}+{len(replacement)}c"
            do_find()  # обновим подсветку

        # Кнопки
        tk.Button(top, text="Найти", command=do_find).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(top, text="Заменить", command=do_replace).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(top, text="Закрыть", command=top.destroy).grid(row=3, column=0, columnspan=2, pady=5)

        find_entry.focus_set()

        # --------- Убираем подсветку при закрытии окна ----------
        def on_close():
            # снять подсветку поиска
            widget.tag_remove("search_match", "1.0", "end")
            # снять выделение
            try:
                widget.tag_remove("sel", "1.0", "end")
                # переместить курсор в конец текста (или в начало)
                widget.mark_set("insert", "1.0")
                widget.focus_set()  # опционально, чтобы фокус остался
            except tk.TclError:
                pass
            self.lines.redraw()
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", on_close)

    def check_document_changed(self, event=None):
        left_text = self.text.get("1.0", "end-1c")   # без последнего перевода строки
        right_text = self.result.get("1.0", "end-1c")

        if left_text.strip() or right_text.strip():  # хотя бы один символ
            self.document_changed = True
        else:
            self.document_changed = False
    
    def _get_selected_lines(self, widget):
        try:
            start = widget.index("sel.first")
            end = widget.index("sel.last")
        except tk.TclError:
            start = widget.index("insert")
            end = start

        start_line = int(start.split(".")[0])
        end_line = int(end.split(".")[0])

        return start_line, end_line


    def ctrl_mouse_scroll(self, event):
        if event.delta > 0:  # прокрутка вверх
            self.change_font_size(1)
        else:                # прокрутка вниз
            self.change_font_size(-1)
        return "break"

    # --- скролл ---
    def on_scroll(self, *args):
        self.text.yview(*args)
        self.lines.yview(*args)
        self.lines.redraw()

    def on_textscroll(self, *args):
        self.lines.yview_moveto(args[0])
        self.lines.redraw()

    # --- подсветка TAB/пробелов и текущей строки ---
    def refresh_visuals(self, event=None):
        self.lines.redraw()
        self.text.tag_remove("tab", "1.0", "end")
        self.text.tag_remove("space", "1.0", "end")

        pos = "1.0"
        while True:
            pos = self.text.search("\t", pos, stopindex="end")
            if not pos:
                break
            end = f"{pos}+1c"
            self.text.tag_add("tab", pos, end)
            pos = end

        pos = "1.0"
        while True:
            pos = self.text.search(" ", pos, stopindex="end")
            if not pos:
                break
            end = f"{pos}+1c"
            self.text.tag_add("space", pos, end)
            pos = end

        self.highlight_current_line()

    def highlight_current_line(self, event=None):
        self.text.tag_remove("current_line", "1.0", "end")
        line = self.text.index("insert").split(".")[0]
        self.text.tag_add("current_line", f"{line}.0", f"{line}.end+1c")

    # --- выделение всего ---
    def select_all(self, event=None):
        self.text.tag_add("sel", "1.0", "end")
        return "break"

    # --- поиск ---
    def find_text(self, event=None):
        search = simpledialog.askstring("Поиск", "Введите текст:")
        if not search:
            return
        self.text.tag_remove("search", "1.0", "end")
        pos = "1.0"
        while True:
            pos = self.text.search(search, pos, stopindex="end")
            if not pos:
                break
            end = f"{pos}+{len(search)}c"
            self.text.tag_add("search", pos, end)
            pos = end

    # --- запуск обработки ---
    def run_calculation(self, event=None):
        text = self.text.get("1.0", "end")
        try:
            # result = calculate_from_text(text)
            result = FastTabCalc(text, mono_tg=True)
            status = self.default_status()
        except Exception as e:
            result = f"Error:\n{e}"
            status = result

        self.result.delete("1.0", "end")
        self.result.insert("1.0", result.__str__())

        self.info.delete("1.0", "end")
        self.info.insert("1.0", status)


    # --- открытие файла ---
    def open_file(self, path=None):
        if not path:
            path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            self.text.delete("1.0", "end")
            self.text.insert("1.0", text)
            self.refresh_visuals()
            return text
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        return None

    def default_data(self):
        default_text = ''
        with open('recent.txt', 'r', encoding='utf-8') as rec:
            path = rec.read().strip('\n')
            if path.endswith('.txt'):
                text = self.open_file(path)
                result = FastTabCalc(text)
                self.result.insert("1.0", result)

        return default_text
    
    def default_status(self):
        
        result = FastTabCalc('Hello\t5')
        return [t[1] for t in result.ordering_list]

    # --- сохранение файла ---
    def save_file(self):
        path_left = filedialog.asksaveasfilename(title="Сохранить файл",
                                                defaultextension=".txt",
                                                filetypes=[("Text files","*.txt"),("All files","*.*")])
        
        if path_left:
            try:
                text = self.text.get("1.0", "end")
                with open(path_left, "w", encoding="utf-8") as f:
                    f.write(text)
                print(os.getcwd())
                with open('recent.txt', 'w', encoding='utf-8') as recent:
                    recent.write(path_left)

            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        return path_left

    def exit_program(self):
        # Левый текст
        ask = False
        if self.document_changed:
            ask = messagebox.askyesnocancel("Выход", "Сохранить?")
            if ask:
                self.save_file()

        if ask != None:
            self.root.destroy()

    def change_font_size(self, delta):
        global FONT_SIZE
        FONT_SIZE = max(6, FONT_SIZE + delta)  # минимальный размер 6
        new_font = ("Consolas", FONT_SIZE)
        self.text.configure(font=new_font)
        self.result.configure(font=new_font)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()