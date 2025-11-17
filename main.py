import sys
print("🚀 Marsal College App - Building...")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

KV = '''
<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: 50
        spacing: 20
        
        MDLabel:
            text: "🎓 Marsal College"
            theme_text_color: "Primary"
            font_style: "H4"
            halign: "center"
            
        MDRaisedButton:
            text: "💬 Chat System"
            on_press: root.open_chat()
            
        MDRaisedButton:
            text: "👤 Student Login"
            on_press: root.student_login()
            
        MDRaisedButton:
            text: "👨‍🏫 Teacher Login"
            on_press: root.teacher_login()
            
        MDRaisedButton:
            text: "⚙️ Settings"
            on_press: root.open_settings()
'''

class MainScreen(Screen):
    def open_chat(self):
        print("Opening Chat System...")
        
    def student_login(self):
        print("Student Login...")
        
    def teacher_login(self):
        print("Teacher Login...")
        
    def open_settings(self):
        print("Opening Settings...")

class MarsalApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        Builder.load_string(KV)
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == "__main__":
    MarsalApp().run()
