import os
import ctypes
import tempfile
import shutil
# это всё для чистки мусора

import time
import psutil
import wmi

import socket # Чисто для сети тема
import platform
import matplotlib.pyplot as plt
from matplotlib.widgets import Button as ButtonPlt # импортирую как ButtonPlt,потому что начинает конфликтовать с tkinter
from turtle import *
from tkinter import *
from tkinter import messagebox

class MiMarBench:
    def __init__(self):
        self.root = Tk()
        self.color = False
        self.cpu_sum = 0
        self.count = 0
        self.cpu_10s = 0
        self.check = 0
        self.after_id = 1 # нужна для корректного закрытия root.after, без неё функции будут вечно повторяться
        self.after_id_ram = 1
        self.after_graf = None
        self.all_time = 0
        self.x = []
        self.y = []
        self.benchmark_listbox_list = []
        self.fig, self.ax = plt.subplots()
        self.line = self.ax.plot(self.x, self.y)[0]

        self.interface()
        self.get_system_info()
        self.text_info.config(state=DISABLED)
        self.root.mainloop()

    def interface(self):
        self.root.title("MiMarBench")
        self.root.geometry("800x400+400+300")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.exit) # protocol - настройка самого окна,можно отслежививать закрытие,сворачивание и тд. "WM_DELETE_WINDOW" - событие закрытие окна,последнее функция на которую перенаправляет

        self.left_frame = Frame(self.root, width=200, bg="#4E4E4E")
        self.left_frame.pack(side=LEFT, fill=Y)

        self.right_frame = Frame(self.root)
        self.right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        self.text_info = Text(self.right_frame, wrap=WORD, font=("Arial", 10))
        self.text_info.pack(padx=10, pady=10, fill=NONE, expand=True)

        self.processes_listbox = Listbox(self.right_frame, width=60, height=20)
        self.processes_listbox.place(x=200, y=50)

        self.processes_ram_listbox = Listbox(self.right_frame, width=60, height=20)
        self.processes_ram_listbox.place(x=200, y=50)

        self.benchmark_listbox = Listbox(self.right_frame, width=42, height=20)
        self.benchmark_listbox.place(x=240, y=50)

        self.btn_info = Button(self.left_frame, text="Сведения о PC ", width=20, pady=10,activebackground="#4E4E4E" ,activeforeground="#FFFFFF", command=self.get_system_info) # activebackground - цвет задника кнопки когда нажимаешь, activeforeground -цвет текста кнопки когда нажимаешь
        self.btn_info.pack(pady=5)

        self.btn_cpu = Button(self.left_frame, text="Загрузка CPU", width=20, pady=10,activebackground="#4E4E4E" ,activeforeground="#FFFFFF", command=self.cpu_load)
        self.btn_cpu.pack(pady=5)

        self.btn_ram = Button(self.left_frame, text="Загрузка RAM", width=20, pady=10,activebackground="#4E4E4E" ,activeforeground="#FFFFFF", command=self.ram_load)
        self.btn_ram.pack(pady=5)

        self.btn_benchmark = Button(self.left_frame, text="Тест Произв.", width=20, pady=10,activebackground="#4E4E4E" ,activeforeground="#FFFFFF", command=self.benchmark)
        self.btn_benchmark.pack(pady=5)

        self.btn_clean = Button(self.left_frame, text="Очистка мусора", width=20, pady=10,activebackground="#4E4E4E" ,activeforeground="#FFFFFF", command=self.clean_junk)
        self.btn_clean.pack(pady=(10, 5))

        self.btn_color = Button(self.left_frame, text="Смена цвета", width=20, pady=10,activebackground="#4E4E4E" ,activeforeground="#FFFFFF", command=self.changecolor)
        self.btn_color.pack(pady=10, padx=5)

        self.btn_exit = Button(self.left_frame, text="EXIT", width=20, pady=10, bg="#AA4343", font=('Helvetica 10 bold'), command=self.exit)
        self.btn_exit.pack(pady=5)

        self.btn_cpu_graph = Button(self.right_frame, text="Загрузка CPU (График)", command=self.cpu_load_graf)
        self.btn_cpu_graph.place(x=35, y=50)

        self.btn_ram_graph = Button(self.right_frame, text="Загрузка RAM (График)", command=self.ram_load_graf)
        self.btn_ram_graph.place(x=35, y=50)

        self.btn_benchmark_test = Button(self.right_frame, text="Проверка производительности", command=self.benchmark_test)
        self.btn_benchmark_test.place(x=35, y=70)

    def exit(self):
        self.root.destroy() # destroy() убивает всё окно

    def get_system_info(self):
        self.btn_ram["state"] = "normal" # делает кнопку активной
        self.btn_cpu["state"] = "normal"
        self.benchmark_listbox.lower() # прячет под самый низ
        self.btn_benchmark_test.lower()
        self.btn_cpu_graph.lower()
        self.btn_ram_graph.lower()
        self.processes_ram_listbox.lower()
        self.processes_listbox.lower()
        self.root.after_cancel(self.after_id)
        self.root.after_cancel(self.after_id_ram)

        self.text_info.config(state=NORMAL)
        self.text_info.delete("1.0", END) # очищает весь текст,почему то 1.0 это обазначение где 1 - это строка,а 0 это символ в строке

        c = wmi.WMI()
        info = f"Имя PC: {platform.node()}\n"
        info += f"Процессор: {platform.processor()}\n"
        info += f"Битность системы: {platform.architecture()[0]}\n"
        info += f"Операционная система: {platform.system()} {platform.release()}\n"

        for gpu in c.Win32_VideoController():
            info += f"GPU: {gpu.Name}\n"
        for board in c.Win32_BaseBoard():
            info += f"Материнская плата: {board.Manufacturer} {board.Product}\n"
        for mem in c.Win32_PhysicalMemory():
            info += f"Оперативная память: {int(mem.Capacity) // (1024**3)} ГБ, {mem.Speed} МГц, {mem.Manufacturer}\n"

        info += "\nИнформация о дисках:\n"
        for disk in psutil.disk_partitions():
            info += f"  Диск: {disk.device}\n  Файловая система: {disk.fstype}\n"
            try: #Если всё норм то выполняется часть кода-- если ошибка то пишет нет доступа
                usage = psutil.disk_usage(disk.mountpoint)
                info += f"    Всего: {usage.total / (1024 ** 3):.2f} GB\n"
                info += f"    Использовано: {usage.used / (1024 ** 3):.2f} GB\n"
                info += f"    Свободно: {usage.free / (1024 ** 3):.2f} GB\n"
                info += f"    Использование: {usage.percent}%\n"
            except PermissionError: #Вторая чать try считай что else
                info += f"    Нет доступа\n"

        #Тут всё для сети
        info += "\nИнформация о сети:\n"
        net = psutil.net_io_counters()
        info += f"  Отправлено: {net.bytes_sent / (1024 ** 2):.2f} MB\n"
        info += f"  Получено: {net.bytes_recv / (1024 ** 2):.2f} MB\n"

        for name, adreses in psutil.net_if_addrs().items():
            if "ethernet" not in name.lower():
                continue #Эта тема нужна чтобы показывалось только от Ethernet, иначе там очень много локальных сетей где всё по 0
            info += f"  Интерфейс: {name}\n"
            for addr in adreses:
                if addr.family == psutil.AF_LINK: #Для Mac адреса
                    info += f"    MAC: {addr.address}\n"
                elif addr.family == socket.AF_INET: #Для сети
                    info += f"    IP: {addr.address}\n    Маска: {addr.netmask}\n"

        self.text_info.insert(END, info)
        self.text_info.config(state=DISABLED)

    def cpu_load(self): # показывает раз в 1 сек нагрузку на проц,считает за 10 секунд среднию нагрузку на проц
        self.btn_ram["state"] = "normal"
        self.btn_cpu["state"] = "disabled" # делаем кнопку инактивной,потому что до этого,можно было несколько раз на неё нажать и функция начинала повторяться
        self.benchmark_listbox.lower() 
        self.processes_ram_listbox.lower()
        self.btn_ram_graph.lower()
        self.btn_benchmark_test.lower()
        self.btn_cpu_graph.lift()
        if self.after_id_ram != 1:
            self.root.after_cancel(self.after_id_ram)

        self.text_info.config(state=NORMAL)
        self.text_info.delete("1.0", END)

        cpu = psutil.cpu_percent()
        self.cpu_sum += cpu
        self.count += 1
        if self.count == 10:
            self.cpu_10s = self.cpu_sum / 10
            self.cpu_sum = 0
            self.count = 0

        info = f"Загрузка CPU в данный момент: {cpu}%"
        info += f"Средняя загрузка CPU за 10 секунд: {round(self.cpu_10s, 2)}%"
        self.text_info.insert(END, info)

        self.processes_listbox.lift() # перенёс таблицу процессов вниз функции,так как вверху она забивала процесс tkinter и график cpu_load_graf не работал
        processes = []
        self.processes_listbox.delete(0, END)
        for proc in psutil.process_iter(['name', 'cpu_percent']): # выводит процессы,с их именем и процентом нагрузки на cpu 
            if proc.info["name"] != "System Idle Process" and proc.info["cpu_percent"] != 0:
                processes.append(f"Process Name: {proc.info['name']} CPU: {proc.info['cpu_percent']} %")
        for process in processes:
            self.processes_listbox.insert(END, process)

        self.after_id = self.root.after(1000, self.cpu_load) # root.after замена бесконечному циклу,tkinter однопотоный и бесконечный цикл забивает его работу после чего он крашиться,а root.after делает секундную задержку перед выполнением
        self.text_info.config(state=DISABLED)

    def ram_load(self): # показывает сколько доступно ram и сколько ram всего
        self.btn_cpu["state"] = "normal"
        self.btn_ram["state"] = "disabled" 
        self.processes_ram_listbox.lift()
        processes = []
        self.processes_ram_listbox.delete(0, END)
        for proc in psutil.process_iter(['name', "memory_percent", "memory_info"]):
            if proc.info["name"] != ("System Idle Process", "") and proc.info["memory_percent"] != 0:
                mem_mb = round(proc.info["memory_info"].rss / (1024 ** 2), 2)
                processes.append(f"Process Name: {proc.info['name']} {mem_mb} MB")
        for process in processes:
            self.processes_ram_listbox.insert(END, process)

        self.benchmark_listbox.lower()
        self.btn_benchmark_test.lower()
        self.processes_listbox.lower()
        self.btn_ram_graph.lift()
        self.btn_cpu_graph.lower()
        if self.after_id != 1:
            self.root.after_cancel(self.after_id)

        self.text_info.config(state=NORMAL)
        self.text_info.delete("1.0", END)
        ram_all = round(psutil.virtual_memory()[0] / (1024 ** 3), 2)
        ram_available = round(psutil.virtual_memory()[1] / (1024 ** 3), 2)
        info = f"Всего доступного RAM: {ram_all}GB"
        info += f"Доступно RAM в данный момент: {ram_available}GB ({round(ram_available * 100 / ram_all, 2)}%)"
        self.text_info.insert(END, info)
        self.after_id_ram = self.root.after(1000, self.ram_load)
        self.text_info.config(state=DISABLED)

    def changecolor(self):
        self.color = not self.color
        bg_color = "#3D3C3C" if self.color else "#FFFFFF"
        fg_color = "#FFFFFF" if self.color else "#3D3C3C"

        self.right_frame.config(bg=bg_color)
        self.text_info.config(bg=bg_color, fg=fg_color)

        for widget in [
            self.btn_info, self.btn_cpu, self.btn_ram,
            self.btn_clean, self.btn_color, self.btn_benchmark,
            self.processes_listbox, self.processes_ram_listbox,
            self.btn_cpu_graph, self.btn_ram_graph,
            self.benchmark_listbox, self.btn_benchmark_test
        ]:
            widget.config(bg=bg_color, fg=fg_color)

        self.fig.set_facecolor(bg_color)
        self.ax.title.set_color(fg_color)
        self.ax.xaxis.label.set_color(fg_color)
        self.ax.yaxis.label.set_color(fg_color)

    def clean_junk(self):
        answer = messagebox.askquestion("Подтверждение", "Вы уверены что хотите начать очистку мусора?")
        if answer != "yes":
            return
        self.btn_ram["state"] = "normal"
        self.btn_cpu["state"] = "normal"
        self.get_system_info()

        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000001 | 0x00000002 | 0x00000004)#вызывает встроенную функцию, которая очищает корзину. 
            #это флаги:
            #0x00000001 — не показывать подтверждение очистки.
            #0x00000002 — не показывать прогресс.
            #0x00000004 — не воспроизводить звук после очистки.
        except Exception as e:
            print(f"Ошибка при очистке корзины: {e}") #Если очистка корзины вызовет ошибку, она будет выведена в консоль.

        #Temp очисточка
        temp = tempfile.gettempdir()
        deleted = 0
        for filename in os.listdir(temp):
            filepa = os.path.join(temp, filename) #Создаёт полный путь к текущему файлу или папке
            try:
                if os.path.isfile(filepa) or os.path.islink(filepa): #Если это обычный файл или ссылка — удаляет его, и увеличивает счётчик.
                    os.remove(filepa)
                    deleted += 1
                elif os.path.isdir(filepa): #Если это папка то удаляет её вместе со всем содержимым.
                    shutil.rmtree(filepa)
                    deleted += 1
            except Exception as e:
                print(f"Ошибка при удалении {filepa}: {e}") #Если при удалении возникает ошибка (например, файл занят системой), она выводится.

        self.text_info.config(state=NORMAL)
        self.text_info.delete("1.0", END)
        self.text_info.insert(END, f"Очистка завершена.Удалено {deleted} временных файлов.Корзина очищена.")
        self.text_info.config(state=DISABLED)

    def cpu_load_graf(self): # график нагрузки на проц
        self.all_time += 1
        cpu = psutil.cpu_percent()

        self.fig.canvas.mpl_connect('close_event', lambda event: self.close_graf()) # ПЕРЕХВАТЫВАЕТ КРЕСТИК И ПЕРЕНАПРАВЛЯЕТ НА ФУНКЦИЮ Я ГЕНИЙЙЙ. mpl_connect - обработчик событий встроенный в matplotlib

        if self.ax.get_title() != "Загрузка CPU": # жёсткий костыль для названий в графике,без проверки названия начинают появляться вокруг кнопки
            if self.color: # проверка на запоминания цвета графика,без неё после закрытия и повторного открытия будет белой
                self.fig.set_facecolor("#3D3C3C")
                plt.title("Загрузка CPU", color="#FFFFFF")
                plt.xlabel('Время (сек)', color="#FFFFFF")
                plt.ylabel('Загрузка CPU (%)', color="#FFFFFF")
            else:
                plt.title("Загрузка CPU")
                plt.xlabel('Время (сек)')
                plt.ylabel('Загрузка CPU (%)')

        button_ax = plt.axes([0.4, 0.94, 0.2, 0.05]) # 1 - отдаление кнопки от левого борда,2 - отдаление кнокпи от нижнего, 3 - ширина кнопки, 4 - высота кнопки
        close_button = ButtonPlt(button_ax, 'Закрыть')
        close_button.on_clicked(lambda event: self.close_graf()) # matplotlib button нужен lambda event,без него кнопка не понимает что на неё кликают

        self.x.append(self.all_time)
        self.y.append(cpu)
        self.line.set_xdata(self.x)
        self.line.set_ydata(self.y)
        self.ax.relim()
        self.ax.autoscale_view()
        plt.draw()
        plt.pause(1)
        self.after_graf = self.root.after(1000, self.cpu_load_graf)

    def ram_load_graf(self):
        self.all_time += 1
        ram_available = round(psutil.virtual_memory()[1] / (1024 ** 3), 2)

        self.fig.canvas.mpl_connect('close_event', lambda event: self.close_graf())

        if self.ax.get_title() != "Доступное RAM":
            if self.color:
                self.fig.set_facecolor("#3D3C3C")
                plt.title("Доступное RAM", color="#FFFFFF")
                plt.xlabel('Время (сек)', color="#FFFFFF")
                plt.ylabel('Доступного RAM (GB)', color="#FFFFFF")
            else:
                plt.title("Доступное RAM")
                plt.xlabel('Время (сек)')
                plt.ylabel('Доступного RAM (GB)')

        button_ax = plt.axes([0.4, 0.94, 0.2, 0.05])
        close_button = ButtonPlt(button_ax, 'Закрыть')
        close_button.on_clicked(lambda event: self.close_graf())

        self.x.append(self.all_time)
        self.y.append(ram_available)
        self.line.set_xdata(self.x)
        self.line.set_ydata(self.y)
        self.ax.relim()
        self.ax.autoscale_view()
        plt.draw()
        plt.pause(1)
        self.after_graf = self.root.after(1000, self.ram_load_graf)

    def close_graf(self):  # функция отвечает за закрытие всех графиков,эта функция встроена в кнопку close_button,желательно позже сделать так,что бы закрывая окно на крестик всё продолжало работать исправно
        self.root.after_cancel(self.after_graf)
        plt.close(self.fig)
        self.x = []
        self.y = []
        self.fig, self.ax = plt.subplots()
        self.line = self.ax.plot(self.x, self.y)[0]
        self.all_time = 0

    def benchmark(self):
        self.btn_ram["state"] = "normal"
        self.btn_cpu["state"] = "normal"
        self.btn_benchmark_test.lift()
        self.benchmark_listbox.lift()
        self.btn_cpu_graph.lower()
        self.btn_ram_graph.lower()
        self.processes_ram_listbox.lower()
        self.processes_listbox.lower()
        self.text_info.config(state=NORMAL)
        self.text_info.delete("1.0", END)
        self.text_info.insert(END, f"Тест производительности проводился {self.check} раз.")
        self.text_info.insert(END, f"\n\n\n\n\n\nСписок результатов создателей:\n")
        self.text_info.insert(END, f"Комп. Мартин - 14.66 сек.\nНоут. Мирон - 14.79 сек.\nНоут. Мартин - 16.17 сек.\n")
        self.text_info.config(state=DISABLED)
        self.root.after_cancel(self.after_id)
        self.root.after_cancel(self.after_id_ram)

    def benchmark_test(self):
        TurtleScreen._RUNNING = True # без этого,нельзя запускать черепаху повторно,она думает,что процесс уничтожен и его нельзя повторно запускать
        # TurtleScreen - переменная tutle,когда окно turtle закрывается,ему присваивается false и по этому его нельзя повторно открыть,а мы принудительно присваеваем ему true для запуска
        screen = Screen()
        screen.setup(width=800, height=600)

        turtles = []
        colors = ["blue", "red", "green"]
        x = [0, -20, 30]

        for i in range(3):
            t = Turtle()
            t.shape("turtle")
            t.color(colors[i])
            t.penup()
            t.goto(x[i], 0)
            t.pendown()
            t.speed(80)
            turtles.append(t)

        start = time.time() # начало таймера
        for w in range(35):
            for t in turtles:
                t.left(10)
            for w in range(4):
                for t in turtles:
                    t.forward(100)
                    t.left(90)
        end = time.time() # конец таймера
        duration = round(end - start, 2)
        self.check += 1
        ontimer(screen.bye, 500) # закрывает черепашку с задержкой в 500 милисекунд

        with open("results.txt", "a") as file:
            file.write(f"Запуск {self.check}: {duration} сек\n")
        print(f"Время отрисовки черепашки: {duration} сек.")
        self.benchmark_listbox.delete(0, END)
        self.benchmark_listbox_list.append(duration)
        self.text_info.config(state=NORMAL)
        self.text_info.delete("1.0", "1.80") # удаляет с 1 строки 0 знака,по 1 строку 80 знак
        self.text_info.insert("1.0", f"Тест производительности проводился {self.check} раз.")
        self.text_info.config(state=DISABLED)

        for a in range(self.check):
            self.benchmark_listbox.insert(END, f"{self.benchmark_listbox_list[a]} сек. - Ваш {a + 1} тест производительности.")

MiMarBench()