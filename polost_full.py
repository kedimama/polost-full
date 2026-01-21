# polost-full
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import httpx
import random
import string
import json

FIREBASE_URL = "https://polost-7b9ce-default-rtdb.firebaseio.com/"


# ---------------- FIREBASE REQUESTS ----------------
def write(path, data):
    url = f"{FIREBASE_URL}{path}.json"
    httpx.put(url, json=data)

def read(path):
    url = f"{FIREBASE_URL}{path}.json"
    return httpx.get(url).json()

def generate_room_id(length=5):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

# ---------------- SCREENS ----------------
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", spacing=20, padding=20)
        layout.add_widget(Label(text="🎮 Polost 🎮", font_size=30))

        btn = Button(text="Online Taş-Kağıt-Makas", font_size=22)
        btn.bind(on_press=self.go_online)
        layout.add_widget(btn)

        self.add_widget(layout)

    def go_online(self, instance):
        self.manager.current = "login"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", spacing=15, padding=20)

        layout.add_widget(Label(text="Giriş Yap / Kayıt Ol", font_size=26))

        layout.add_widget(Label(text="Email", font_size=20))
        self.email = TextInput(multiline=False, font_size=20)
        layout.add_widget(self.email)

        layout.add_widget(Label(text="Şifre", font_size=20))
        self.password = TextInput(password=True, multiline=False, font_size=20)
        layout.add_widget(self.password)

        self.status = Label(text="", font_size=18)
        layout.add_widget(self.status)

        btn_login = Button(text="Giriş Yap", font_size=20)
        btn_login.bind(on_press=self.login)
        layout.add_widget(btn_login)

        btn_register = Button(text="Kayıt Ol", font_size=20)
        btn_register.bind(on_press=self.register)
        layout.add_widget(btn_register)

        self.add_widget(layout)

    def login(self, instance):
        # Burada sadece kontrol var (Firebase auth için ekleme gerek)
        email = self.email.text.strip()
        pwd = self.password.text.strip()
        if not email or not pwd:
            self.status.text = "Email ve şifre boş olamaz!"
            return
        self.status.text = "Giriş başarılı! (Simüle edildi)"
        self.manager.current = "online"

    def register(self, instance):
        email = self.email.text.strip()
        pwd = self.password.text.strip()
        if not email or not pwd:
            self.status.text = "Email ve şifre boş olamaz!"
            return
        self.status.text = "Kayıt başarılı! (Simüle edildi)"
        self.manager.current = "online"

class OnlineScreen(Screen):
    def __init__(self, **kwargs):
        super(OnlineScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", spacing=15, padding=20)

        self.layout.add_widget(Label(text="İsim Gir", font_size=24))
        self.name_input = TextInput(multiline=False, font_size=22)
        self.layout.add_widget(self.name_input)

        self.layout.add_widget(Label(text="Oda ID Gir (veya otomatik oluştur)", font_size=20))
        self.room_input = TextInput(multiline=False, font_size=22)
        self.layout.add_widget(self.room_input)

        self.layout.add_widget(Label(text="Oda Şifresi Gir", font_size=20))
        self.room_pass = TextInput(multiline=False, font_size=22)
        self.layout.add_widget(self.room_pass)

        self.auto_btn = Button(text="🔀 Oda ID Otomatik Oluştur", font_size=20)
        self.auto_btn.bind(on_press=self.auto_room)
        self.layout.add_widget(self.auto_btn)

        self.player_btn = Button(text="Ben Player1’im (Oda Oluştur)", font_size=20)
        self.player_btn.bind(on_press=self.create_room)
        self.layout.add_widget(self.player_btn)

        self.join_btn = Button(text="Odaya Katıl (Player2)", font_size=20)
        self.join_btn.bind(on_press=self.join_room)
        self.layout.add_widget(self.join_btn)

        self.status = Label(text="", font_size=20)
        self.layout.add_widget(self.status)

        back = Button(text="🔙 Geri", font_size=20)
        back.bind(on_press=self.go_menu)
        self.layout.add_widget(back)

        self.add_widget(self.layout)

    def go_menu(self, instance):
        self.manager.current = "menu"

    def auto_room(self, instance):
        self.room_input.text = generate_room_id()

    def create_room(self, instance):
        name = self.name_input.text.strip()
        room_id = self.room_input.text.strip()
        room_pass = self.room_pass.text.strip()

        if not name or not room_id or not room_pass:
            self.status.text = "İsim/RoomID/Şifre boş olamaz!"
            return

        write(f"rooms/{room_id}", {
            "player1": {"name": name, "choice": ""},
            "player2": {"name": "", "choice": ""},
            "score": {"p1": 0, "p2": 0},
            "chat": {},
            "status": {"state": "waiting"},
            "pass": room_pass
        })

        self.manager.current = "lobby"
        self.manager.get_screen("lobby").setup(room_id, "player1")

    def join_room(self, instance):
        name = self.name_input.text.strip()
        room_id = self.room_input.text.strip()
        room_pass = self.room_pass.text.strip()

        if not name or not room_id or not room_pass:
            self.status.text = "İsim/RoomID/Şifre boş olamaz!"
            return

        room = read(f"rooms/{room_id}")
        if not room:
            self.status.text = "Oda bulunamadı!"
            return

        if room.get("pass") != room_pass:
            self.status.text = "Şifre yanlış!"
            return

        write(f"rooms/{room_id}/player2/name", name)
        write(f"rooms/{room_id}/player2/choice", "")
        write(f"rooms/{room_id}/status/state", "waiting")

        self.manager.current = "lobby"
        self.manager.get_screen("lobby").setup(room_id, "player2")

class LobbyScreen(Screen):
    def __init__(self, **kwargs):
        super(LobbyScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", spacing=15, padding=20)

        self.label = Label(text="Lobby: Rakip bekleniyor...", font_size=24)
        self.layout.add_widget(self.label)

        self.back = Button(text="🔙 Geri", font_size=20)
        self.back.bind(on_press=self.go_menu)
        self.layout.add_widget(self.back)

        self.add_widget(self.layout)
        self.check_event = None

    def go_menu(self, instance):
        self.manager.current = "menu"

    def setup(self, room_id, player):
        self.room_id = room_id
        self.player = player
        self.label.text = f"Oda: {room_id}\nRakip bekleniyor..."
        self.check_event = Clock.schedule_interval(self.check_players, 1)

    def check_players(self, dt):
        room = read(f"rooms/{self.room_id}")
        if not room:
            return

        p1 = room["player1"]["name"]
        p2 = room["player2"]["name"]

        if p1 and p2:
            write(f"rooms/{self.room_id}/status/state", "playing")
            self.manager.current = "game"
            self.manager.get_screen("game").setup(self.room_id, self.player)
            Clock.unschedule(self.check_event)

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)

        self.layout = BoxLayout(orientation="vertical", spacing=15, padding=20)
        self.label = Label(text="Seçimini yap", font_size=26)
        self.layout.add_widget(self.label)

        self.tur_label = Label(text="Tur: 0/5", font_size=20)
        self.layout.add_widget(self.tur_label)

        self.buttons = BoxLayout(spacing=10)
        for secim in ["Taş", "Kağıt", "Makas"]:
            btn = Button(text=secim, font_size=22)
            btn.bind(on_press=self.play)
            self.buttons.add_widget(btn)
        self.layout.add_widget(self.buttons)

        self.chat_box = BoxLayout(orientation="vertical", spacing=10)
        self.chat_label = Label(text="Chat:", font_size=20)
        self.chat_box.add_widget(self.chat_label)

        self.chat_input = TextInput(multiline=False, font_size=20)
        self.chat_box.add_widget(self.chat_input)

        self.chat_send = Button(text="Gönder", font_size=20)
        self.chat_send.bind(on_press=self.send_chat)
        self.chat_box.add_widget(self.chat_send)

        self.layout.add_widget(self.chat_box)

        self.reset_btn = Button(text="🔄 Yeniden Oyna", font_size=20)
        self.reset_btn.bind(on_press=self.reset_game)
        self.reset_btn.disabled = True
        self.layout.add_widget(self.reset_btn)

        self.back = Button(text="🔙 Çıkış", font_size=20)
        self.back.bind(on_press=self.go_menu)
        self.layout.add_widget(self.back)

        self.add_widget(self.layout)

        self.check_event = None
        self.chat_event = None

    def go_menu(self, instance):
        self.manager.current = "menu"

    def setup(self, room_id, player):
        self.room_id = room_id
        self.player = player
        self.tur = 0
        self.max_tur = 5
        self.tur_label.text = f"Tur: {self.tur}/{self.max_tur}"
        self.label.text = f"Oda: {room_id}\nSeçimini yap"
        self.reset_btn.disabled = True

        self.check_event = Clock.schedule_interval(self.check_result, 1)
        self.chat_event = Clock.schedule_interval(self.update_chat, 1)

    def play(self, instance):
        choice = instance.text
        write(f"rooms/{self.room_id}/{self.player}/choice", choice)
        self.label.text = "Rakip bekleniyor..."

    def check_result(self, dt):
        room = read(f"rooms/{self.room_id}")
        if not room:
            return

        if "player1" not in room or "player2" not in room:
            return

        p1 = room["player1"]["choice"]
        p2 = room["player2"]["choice"]

        if not p1 or not p2:
            return

        name1 = room["player1"]["name"]
        name2 = room["player2"]["name"]
        score1 = room["score"]["p1"]
        score2 = room["score"]["p2"]

        if p1 == p2:
            res = "Berabere"
        elif (p1 == "Taş" and p2 == "Makas") or \
             (p1 == "Kağıt" and p2 == "Taş") or \
             (p1 == "Makas" and p2 == "Kağıt"):
            res = f"{name1} kazandı!"
            score1 += 1
        else:
            res = f"{name2} kazandı!"
            score2 += 1

        write(f"rooms/{self.room_id}/score/p1", score1)
        write(f"rooms/{self.room_id}/score/p2", score2)

        self.tur += 1
        self.tur_label.text = f"Tur: {self.tur}/{self.max_tur}"

        self.label.text = f"Sonuç:\n{res}\n\n{name1}: {score1}\n{name2}: {score2}"

        write(f"rooms/{self.room_id}/player1/choice", "")
        write(f"rooms/{self.room_id}/player2/choice", "")

        if self.tur >= self.max_tur:
            self.reset_btn.disabled = False

    def reset_game(self, instance):
        write(f"rooms/{self.room_id}/player1/choice", "")
        write(f"rooms/{self.room_id}/player2/choice", "")
        self.tur = 0
        self.tur_label.text = f"Tur: {self.tur}/{self.max_tur}"
        self.label.text = "Yeni tur! Seçimini yap"
        self.reset_btn.disabled = True

    def send_chat(self, instance):
        msg = self.chat_input.text.strip()
        if not msg:
            return

        room = read(f"rooms/{self.room_id}")
        chat_count = len(room["chat"]) if room and "chat" in room else 0
        chat_key = f"msg{chat_count + 1}"

        write(f"rooms/{self.room_id}/chat/{chat_key}", f"{self.player}: {msg}")
        self.chat_input.text = ""

    def update_chat(self, dt):
        room = read(f"rooms/{self.room_id}")
        if not room or "chat" not in room:
            return

        chat_text = "\n".join(room["chat"].values())
        self.chat_label.text = "Chat:\n" + chat_text

class PolostApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(OnlineScreen(name="online"))
        sm.add_widget(LobbyScreen(name="lobby"))
        sm.add_widget(GameScreen(name="game"))
        return sm

PolostApp().run()
