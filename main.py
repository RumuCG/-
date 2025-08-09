import tkinter as tk
from PIL import ImageGrab
import os
import pytesseract
from PIL import Image
import re
from pynput import mouse, keyboard
import pyautogui
import time
import ctypes
class stuff:
    def __init__(self):
        self.name = "NULL"
        self.price = 0
        self.dataNum = 0
        self.minDiff = 100000
        self.region = None  # 新增变量，存储截图区域
        self.to_buy = 0

    def set_capture_region(self):
        app = ScreenCapture()
        app.mainloop()
        self.region = app.get_capture_region()
        text = recognize_capture()
        self.name,self.price = feed_back(text)
        print("检测到物品", self.name)
        print("当前售价",self.price)
        self.dataNum += 1

    def buy_it(self):
        x1, y1, x2, y2 = self.region
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        pyautogui.click(center_x, center_y)
        time.sleep(0.2)  # 点击后等待0.2秒
        for idx, (x, y) in enumerate(points_2):
            pyautogui.click(x, y)
            time.sleep(0.2)  # 每次点击间隔0.2秒
        return

    def capture_by_region(self):
        if self.region is None:
            return
        img = ImageGrab.grab(bbox=self.region)
        img.save("capture.png")
        text = recognize_capture()
        a,b = feed_back(text)
        if self.price - b > self.minDiff:
            if b < self.price * 0.01:
                return
            print("物品:",a,"----差价到达",b - self.price)
            if self.to_buy > 0:
                self.to_buy -= 1
                self.buy_it()
                print("购入",a,"1个，剩余待买",self.to_buy)
            else:
                print("未购入，已完成该货物任务")
            print(a, "价格已更新 当前均价", self.price)
        else:
            self.price *= self.dataNum
            self.dataNum += 1
            self.price += b
            self.price /= self.dataNum
            #print(a,"价格已更新 当前均价",self.price)


class ScreenCapture(tk.Tk):
    def __init__(self):
        super().__init__()
        self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.3)  # 半透明
        self.canvas = tk.Canvas(self, cursor="cross", bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.capture_region = None  # 存储截图坐标

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_move_press(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        x1 = int(min(self.start_x, event.x))
        y1 = int(min(self.start_y, event.y))
        x2 = int(max(self.start_x, event.x))
        y2 = int(max(self.start_y, event.y))
        self.capture_region = (x1, y1, x2, y2)
        self.withdraw()  # 隐藏窗口
        img = ImageGrab.grab(bbox=self.capture_region)
        img.save("capture.png")
        self.destroy()

    def get_capture_region(self):
        return self.capture_region


def recognize_capture():
    img = Image.open("capture.png")
    text = pytesseract.image_to_string(img, lang="chi_sim+eng")
    return text


def feed_back(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    name = lines[0] if len(lines) > 0 else ""

    price_number = 0
    if len(lines) > 1:
        last_line = lines[-1]
        match = re.search(r'[\d,]+', last_line)
        if match:
            price_str = match.group(0)
            price_number = int(price_str.replace(',', ''))
    return name, price_number


def flash():
    #print("正在刷新 ---------------------")
    for idx, (x, y) in enumerate(points_1):
        pyautogui.click(x, y)
        time.sleep(0.5)  # 等待0.5秒，防止点击过快
    return


points_1 = []
points_2 = []
collecting = True


def on_click1(x, y, button, pressed):
    global points_1, collecting
    if pressed:
        print(f"记录点: ({x}, {y})")
        points_1.append((x, y))


def on_click2(x, y, button, pressed):
    global points_2, collecting
    if pressed:
        print(f"记录点: ({x}, {y})")
        points_2.append((x, y))


def on_press(key):
    global collecting
    try:
        # 按下esc键结束采集
        if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            print("采集结束")
            collecting = False
            return False  # 停止监听键盘
    except AttributeError:
        pass
import threading

HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040

SetWindowPos = ctypes.windll.user32.SetWindowPos
GetConsoleWindow = ctypes.windll.kernel32.GetConsoleWindow


def keep_window_topmost():
    hwnd = GetConsoleWindow()
    while True:
        SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
        time.sleep(5)


if __name__ == "__main__":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    print("三角洲交易行器灵 v1.0\n 输入任意内容开始")
    input()
    print("请用鼠标依次点击刷新价格需要点鼠标的地方，按shift键结束采集。")
    with mouse.Listener(on_click=on_click1) as mouse_listener, keyboard.Listener(on_press=on_press) as keyboard_listener:
        keyboard_listener.join()

    print("先随便选一个物品，点击购买页，就是有不同价格在售的那一页，请用鼠标依次点击购买物品需要点鼠标的地方，按shift键结束采集。")
    with mouse.Listener(on_click=on_click2) as mouse_listener, keyboard.Listener(
            on_press=on_press) as keyboard_listener:
        keyboard_listener.join()
    points_2 = points_2[1:]
    print("请输入需要监控的数量：")
    num = int(input())
    stuff_list = [stuff() for _ in range(num)]
    for i in stuff_list:
        flag = True
        while flag:
            print("在交易行页面选中该物品的图像，左上角和右下角大致与框齐平")
            i.set_capture_region()
            print("是否识别成功，1/0，1代表成功，0从新识别")
            tmp = int(input())
            if tmp == 1:
                flag = False
            print("输入这个物品需要购入的数量")
            tmp = int(input())
            i.to_buy = tmp
            print("输入可以接受的低价，即低于平均价格多少钱")
            tmp = int(input())
            i.minDiff = tmp
            print("设置成功！！",i.name,"待购入数量：",i.to_buy,"差价阈值：",i.minDiff)
    print("开始监控.....")
    while(True):
        flash()
        for i in stuff_list:
            i.capture_by_region()

