import tkinter as tk
from tkinter import messagebox
from scapy.all import sniff, IP, TCP, send, ICMP
from collections import defaultdict
import time
from threading import Thread
import requests
import subprocess

# Параметры по умолчанию
MAX_PACKET_SIZE = 1500
SCAN_THRESHOLD = 20
REPEAT_THRESHOLD = 5
SCAN_TIME_FRAME = 5
last_event_time = time.time()

# Список подозрительных IP для отображения и блокировки
suspicious_ips = set()
ip_event_count = defaultdict(int)

class TrafficScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Traffic Scanner")
        self.geometry("400x500")

        # Параметры
        self.packet_size_var = tk.IntVar(value=MAX_PACKET_SIZE)
        self.port_scan_var = tk.IntVar(value=SCAN_THRESHOLD)
        self.repeat_req_var = tk.IntVar(value=REPEAT_THRESHOLD)

        # Опции
        self.size_check = tk.IntVar()
        self.port_check = tk.IntVar()
        self.repeat_check = tk.IntVar()

        # Список для чекбоксов
        self.ip_vars = {}
        self.sniff_thread = None

        # Виджеты
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Выберите параметры сканирования:").pack(pady=10)

        # Параметры
        tk.Checkbutton(self, text="Размер пакета", variable=self.size_check).pack(anchor="w")
        tk.Label(self, text="Макс. размер пакета (байты):").pack(anchor="w")
        tk.Entry(self, textvariable=self.packet_size_var).pack(anchor="w")

        tk.Checkbutton(self, text="Сканирование портов", variable=self.port_check).pack(anchor="w")
        tk.Label(self, text="Порог портов:").pack(anchor="w")
        tk.Entry(self, textvariable=self.port_scan_var).pack(anchor="w")

        tk.Checkbutton(self, text="Повторяющиеся запросы", variable=self.repeat_check).pack(anchor="w")
        tk.Label(self, text="Порог запросов:").pack(anchor="w")
        tk.Entry(self, textvariable=self.repeat_req_var).pack(anchor="w")

        # Кнопки
        tk.Button(self, text="Начать сканирование", command=self.start_scanning).pack(pady=10)
        tk.Button(self, text="Блокировать выбранные IP", command=self.block_ips).pack(pady=10)

    def start_scanning(self):
        messagebox.showinfo("Traffic Scanner", "Подождите 5 секунд!.")
        global suspicious_ips, ip_event_count
        # Очистка списка IP
        suspicious_ips.clear()
        ip_event_count.clear()

        # Устанавливаем параметры
        if self.size_check.get():
            global MAX_PACKET_SIZE
            MAX_PACKET_SIZE = self.packet_size_var.get()

        if self.port_check.get():
            global SCAN_THRESHOLD
            SCAN_THRESHOLD = self.port_scan_var.get()

        if self.repeat_check.get():
            global REPEAT_THRESHOLD
            REPEAT_THRESHOLD = self.repeat_req_var.get()

        # Запуск сканирования в отдельном потоке на 5 секунд
        self.sniff_thread = Thread(target=self.sniff_traffic)
        self.sniff_thread.start()

        # Запускаем проверку потока каждые 500 мс
        self.after(500, self.check_sniff_thread)

    def sniff_traffic(self):
        sniff(timeout=5, prn=self.detect_suspicious, store=False)
        print('sniff complete!')

    def check_sniff_thread(self):
        # Проверка, завершился ли поток sniff
        if self.sniff_thread.is_alive():
            self.after(500, self.check_sniff_thread)  # Проверяем снова через 500 мс
        else:
            messagebox.showinfo("Traffic Scanner", "Сканирование завершено")
            self.display_suspicious_ips()  # Отображаем результаты после завершения потока

    def detect_suspicious(self, packet):
        global last_event_time
        
        # Проверка слоёв IP и TCP
        if not packet.haslayer(IP) or not packet.haslayer(TCP):
            return

        src_ip = packet[IP].src
        dst_port = packet[TCP].dport
        packet_size = len(packet)

        # Проверка на большой пакет
        if self.size_check.get() and packet_size > MAX_PACKET_SIZE:
            suspicious_ips.add(src_ip)

        # Проверка на сканирование портов
        ip_event_count[(src_ip, dst_port)] += 1
        port_scan_count = sum(1 for key in ip_event_count if key[0] == src_ip)

        if self.port_check.get() and port_scan_count > SCAN_THRESHOLD:
            suspicious_ips.add(src_ip)

        # Проверка на повторяющиеся запросы
        ip_event_count[src_ip] += 1
        if self.repeat_check.get() and ip_event_count[src_ip] > REPEAT_THRESHOLD and (time.time() - last_event_time) < SCAN_TIME_FRAME:
            suspicious_ips.add(src_ip)
            last_event_time = time.time()
    
    def get_isp_info(self, ip):
        try:
            response = requests.get(f"https://api.iplocation.net/?ip={ip}")
            data = response.json()
            if data.get("response_code") == "200":
                isp = data.get("isp", "Unknown ISP")
                return isp
            else:
                return "Unknown ISP"
        except Exception as e:
            print(f"Error fetching ISP info for {ip}: {e}")
            return "Unknown ISP"

    def display_suspicious_ips(self):
        # Очистка старых чекбоксов
        for widget in self.winfo_children():
            if isinstance(widget, tk.Checkbutton) and widget.cget("text") in self.ip_vars:
                widget.destroy()

        # Создание чекбоксов для каждого подозрительного IP с информацией об ISP
        for ip in suspicious_ips:
            isp_info = self.get_isp_info(ip)
            display_text = f"{ip}, ISP: {isp_info}"
            var = tk.IntVar()
            self.ip_vars[ip] = var
            tk.Checkbutton(self, text=display_text, variable=var).pack(anchor="w")


    def block_ips(self):
        selected_ips = [ip for ip, var in self.ip_vars.items() if var.get() == 1]
        if not selected_ips:
            messagebox.showinfo("Traffic Scanner", "Нет выбранных IP для блокировки.")
            return

        for ip in selected_ips:
            send(IP(dst=ip) / ICMP(type=3, code=1))  # Отправка ICMP Destination Unreachable
            print(f"[Блокировка] Отправлено ICMP Destination Unreachable для {ip}")

        messagebox.showinfo("Traffic Scanner", f"Заблокировано IP: {', '.join(selected_ips)}")
        
    # def block_ips(self):
    #     selected_ips = [ip for ip, var in self.ip_vars.items() if var.get() == 1]
    #     if not selected_ips:
    #         messagebox.showinfo("Traffic Scanner", "Нет выбранных IP для блокировки.")
    #         return

    #     # Проверка ОС и добавление правил блокировки в брандмауэр
    #     for ip in selected_ips:
    #         try:
    #             if sys.platform.startswith("linux"):
    #                 # Для Linux используем iptables
    #                 subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
    #                 print(f"[Блокировка] IP {ip} заблокирован с помощью iptables.")
    #             elif sys.platform == "darwin":
    #                 # Для macOS используем pfctl
    #                 block_rule = f"block drop from {ip} to any"
    #                 with open("/etc/pf.conf", "a") as pf_file:
    #                     pf_file.write(block_rule + "\n")
    #                 subprocess.run(["sudo", "pfctl", "-f", "/etc/pf.conf"], check=True)
    #                 subprocess.run(["sudo", "pfctl", "-e"], check=True)
    #                 print(f"[Блокировка] IP {ip} заблокирован с помощью pfctl.")
    #             else:
    #                 print(f"[Блокировка] Не поддерживаемая ОС для автоматической блокировки IP {ip}.")
    #         except Exception as e:
    #             print(f"Ошибка при блокировке IP {ip}: {e}")

    #     messagebox.showinfo("Traffic Scanner", f"Заблокировано IP: {', '.join(selected_ips)}")

# Запуск интерфейса
if __name__ == "__main__":
    app = TrafficScannerApp()
    app.mainloop()
