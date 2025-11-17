import os
import sys

# منع التشغيل في بيئة غير Android
if not hasattr(sys, 'getandroidapilevel'):
    print("📱 جاري بناء Marsal APK...")
    print("🚫 هذا التطبيق مصمم للعمل على Android فقط")

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.metrics import dp
import arabic_reshaper
from bidi.algorithm import get_display

# 📦 Import Database and File Libraries
import pymysql
from pymysql import Error
from datetime import datetime, timedelta
import base64
from io import BytesIO
from PIL import Image as PILImage, ImageDraw, ImageFont
import webbrowser
import re
import json
import socket
import requests

# 🔧 Import File Chooser Library
try:
    from plyer import filechooser
    HAS_FILECHOOSER = True
except ImportError:
    print("⚠️ plyer library not installed.")
    HAS_FILECHOOSER = False

# 📐 Set Window Size for Android
Window.size = (400, 700)

# 🎨 تسجيل الخط العربي ومعالجة النص
print("🚀 Starting Marsal App...")

try:
    # استخدام خطوط Android الافتراضية
    LabelBase.register(name='ArabicFont', fn_regular='fonts/NotoNaskhArabic-Regular.ttf')
    print("✅ Arabic font setup completed")
    arabic_font_name = 'ArabicFont'
except Exception as e:
    print(f"⚠️ Using system font: {e}")
    arabic_font_name = 'Roboto'

# 🌐 وظائف الحصول على عناوين IP
def get_local_ip():
    """الحصول على العنوان المحلي"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"127.0.0.1"

def get_public_ip():
    """الحصول على العنوان الخارجي"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        try:
            response = requests.get('https://ident.me', timeout=5)
            return response.text
        except Exception as e:
            return f"غير معروف"

def get_all_ips():
    """الحصول على جميع العناوين"""
    return {
        'local': get_local_ip(),
        'public': get_public_ip()
    }

class ArabicTextInput(MDTextField):
    """MDTextField مخصص للنص العربي"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_text = ""
        self.processed_text = ""
    
    def insert_text(self, substring, from_undo=False):
        """معالجة النص العربي عند الإدخال"""
        if substring:
            self.original_text += substring
            if any('\u0600' <= char <= '\u06FF' for char in self.original_text):
                self.processed_text = arabic_text(self.original_text)
            else:
                self.processed_text = self.original_text
            self.text = self.processed_text
            self.cursor = (len(self.text), 0)
        return True
    
    def do_backspace(self, from_undo=False, mode='bkspc'):
        """معالجة الحذف للنص العربي"""
        if self.original_text:
            self.original_text = self.original_text[:-1]
            if self.original_text and any('\u0600' <= char <= '\u06FF' for char in self.original_text):
                self.processed_text = arabic_text(self.original_text)
            else:
                self.processed_text = self.original_text
            self.text = self.processed_text
            self.cursor = (len(self.text), 0)

def arabic_text(text):
    """معالجة النص العربي بشكل محسن"""
    if not text:
        return text
    try:
        if any('\u0600' <= char <= '\u06FF' for char in text):
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        else:
            return text
    except Exception as e:
        print(f"Arabic processing error: {e}")
        return text

def app_text(text_key):
    """إرجاع النص الإنجليزي الرسمي للتطبيق"""
    texts = {
        # Welcome Screen
        "app_name": "marsal",
        "welcome_subtitle": "College Communication System",
        
        # Login Screen
        "welcome_back": "Welcome Back",
        "select_user": "Select User Type",
        "student": "Student",
        "teacher": "Teacher", 
        "student_name": "Student Name",
        "teacher_name": "Teacher Name",
        "student_id": "Student ID",
        "job_id": "Job ID",
        "password": "Password",
        "login": "Login",
        "forgot_password": "Forgot Password?",
        "create_student_account": "Create Student Account",
        "create_teacher_account": "Create Teacher Account",
        
        # Registration
        "register_student": "Register Student",
        "register_teacher": "Register Teacher",
        "select_major": "Select Major",
        "choose_major": "Choose Major",
        "security_questions": "Security Questions",
        "favorite_color": "What is your favorite color?",
        "favorite_name": "What is your favorite name?",
        "future_job": "What is your future job?",
        "create_account": "Create Account",
        
        # Forgot Password
        "reset_password": "Reset Password",
        "user_id": "User ID",
        "new_password": "New Password",
        "confirm_password": "Confirm Password",
        "reset": "Reset",
        
        # Main Menu
        "main_menu": "Main Menu",
        "welcome_college": "Welcome to College Communication System",
        "chat_system": "💬 Chat System",
        "settings": "⚙️ Settings", 
        "grades_system": "📊 Grades System",
        
        # Settings
        "account_settings": "Account Settings",
        "delete_account": "🗑️ Delete Account",
        "change_password": "🔐 Change Password",
        "dark_mode": "🌙 Dark Mode",
        "light_mode": "☀️ Light Mode",
        "privacy_settings": "👁️ Privacy Settings",
        
        # Chat System
        "chats": "Chats",
        "new_message": "✉️ New Message",
        "search_chats": "Search previous chats...",
        "contacts": "Contacts",
        "search_contacts": "Search by name or ID...",
        "chat_with": "Chat with",
        
        # New Message
        "new_message_title": "📧 New Message",
        "select_major_text": "Select Major:",
        "subject": "Subject",
        "write_message": "Write your message here...",
        "attach": "📎 Attach",
        "send": "📤 Send",
        "send_all": "📢 Send to All",
        
        # Messages
        "no_results": "No results found for",
        "user": "User",
        "new": "new",
        "no_messages": "No messages yet",
        "type_message": "Type your message...",
        
        # Status Messages
        "success": "✅ Success",
        "error": "❌ Error",
        "loading": "Loading...",
        "sending": "Sending...",
        
        # Files
        "image": "🖼️ Image",
        "video": "🎬 Video", 
        "document": "📄 Document",
        "click_to_zoom": "Double click to zoom",
        "click_to_play": "Double click to play",
        "click_to_open": "Double click to open"
    }
    
    return texts.get(text_key, text_key)

# 🔍 Image Zoom Dialog
class ZoomImage(ModalView):
    def __init__(self, image_source, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = True
        self.background_color = (0, 0, 0, 0.8)
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        self.image = Image(
            source=image_source,
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        
        close_btn = MDRaisedButton(
            text="إغلاق",
            size_hint=(1, None),
            height=50,
            md_bg_color="#FF5252",
            on_press=self.dismiss
        )
        
        layout.add_widget(self.image)
        layout.add_widget(close_btn)
        self.add_widget(layout)

# 🎬 Video Player Dialog
class VideoPlayer(ModalView):
    video_source = StringProperty("")
    
    def __init__(self, video_source, **kwargs):
        super().__init__(**kwargs)
        self.video_source = video_source
        self.is_playing = True
        
    def toggle_play(self):
        if self.is_playing:
            self.ids.video_player.state = 'pause'
            self.ids.play_btn.text = "▶️ تشغيل"
            self.is_playing = False
        else:
            self.ids.video_player.state = 'play'
            self.ids.play_btn.text = "⏸️ إيقاف"
            self.is_playing = True

    def stop_video(self):
        self.ids.video_player.state = 'stop'
        self.ids.play_btn.text = "▶️ تشغيل"
        self.is_playing = False

    def replay_video(self):
        self.ids.video_player.state = 'stop'
        self.ids.video_player.state = 'play'
        self.ids.play_btn.text = "⏸️ إيقاف"
        self.is_playing = True

    def on_dismiss(self):
        self.ids.video_player.state = 'stop'
        return super().on_dismiss()

# 📁 File Message Bubble Class
class FileMessageBubble(BoxLayout):
    file_name = StringProperty("")
    file_data = StringProperty("")
    is_my_message = NumericProperty(0)
    message_time = StringProperty("")
    is_starred = BooleanProperty(False)
    file_id = NumericProperty(0)
    file_type = StringProperty("image")
    icon_source = StringProperty("📎")
    temp_file_path = StringProperty("")
    image_source = StringProperty("")
    file_icon = StringProperty("🖼️ Image")
    action_text = StringProperty("Double click to open")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.determine_icon()
        Clock.schedule_once(self.process_file_data, 0.1)

    def process_file_data(self, dt):
        if self.file_type == "image" and self.file_data:
            try:
                image_data = base64.b64decode(self.file_data)
                temp_file = f"temp_image_{self.file_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                
                with open(temp_file, 'wb') as f:
                    f.write(image_data)
                
                self.image_source = temp_file
                self.action_text = app_text("click_to_zoom")
                
                Clock.schedule_once(lambda dt: self.cleanup_temp_file(temp_file), 30)
                
            except Exception as e:
                print(f"❌ Error processing image: {e}")
                self.icon_source = "❌"
        
        elif self.file_type == "video" and self.file_data:
            self.save_video_file()
            
        elif self.file_type == "document" and self.file_data:
            self.save_document_file()

    def determine_icon(self):
        if self.file_type == "image":
            self.file_icon = app_text("image")
            self.icon_source = "🖼️"
            self.action_text = app_text("click_to_zoom")
            return
            
        if self.file_type == "video":
            self.file_icon = app_text("video")
            self.icon_source = "🎬"
            self.action_text = app_text("click_to_play")
            return
            
        if not self.file_name:
            self.file_icon = app_text("document")
            self.icon_source = "📎"
            self.action_text = app_text("click_to_open")
            return
            
        ext = self.file_name.lower().split('.')[-1] if '.' in self.file_name else ''
        
        icon_map = {
            'pdf': "📄", 'doc': "📝", 'docx': "📝",
            'xls': "📊", 'xlsx': "📊", 'ppt': "📑", 'pptx': "📑",
            'txt': "📃", 'zip': "🗜️", 'rar': "🗜️",
        }
        
        self.icon_source = icon_map.get(ext, "📎")
        self.file_icon = f"📄 {ext.upper()}" if ext else app_text("document")
        self.action_text = app_text("click_to_open")

    def save_video_file(self):
        if self.file_type == "video" and self.file_data:
            try:
                video_data = base64.b64decode(self.file_data)
                temp_file = f"temp_video_{self.file_id}_{self.file_name}"
                
                with open(temp_file, 'wb') as f:
                    f.write(video_data)
                
                self.temp_file_path = temp_file
                
                Clock.schedule_once(lambda dt: self.cleanup_temp_file(temp_file), 60)
                
            except Exception as e:
                print(f"❌ Error saving video: {e}")

    def save_document_file(self):
        if self.file_type == "document" and self.file_data:
            try:
                file_data = base64.b64decode(self.file_data)
                temp_file = f"temp_doc_{self.file_id}_{self.file_name}"
                
                with open(temp_file, 'wb') as f:
                    f.write(file_data)
                
                self.temp_file_path = temp_file
                
                Clock.schedule_once(lambda dt: self.cleanup_temp_file(temp_file), 30)
                
            except Exception as e:
                print(f"❌ Error saving document: {e}")

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            if self.file_type == "image":
                self.zoom_image()
            elif self.file_type == "video":
                self.play_video()
            else:
                self.open_document()
            return True
        return super().on_touch_down(touch)

    def zoom_image(self):
        if self.file_type == "image" and self.image_source:
            zoom_view = ZoomImage(self.image_source)
            zoom_view.open()

    def play_video(self):
        if self.file_type == "video" and self.temp_file_path and os.path.exists(self.temp_file_path):
            try:
                video_player = VideoPlayer(self.temp_file_path)
                video_player.open()
            except Exception as e:
                print(f"❌ Error playing video: {e}")

    def open_document(self):
        if self.file_type == "document" and self.temp_file_path and os.path.exists(self.temp_file_path):
            try:
                webbrowser.open(self.temp_file_path)
            except Exception as e:
                print(f"❌ Error opening document: {e}")

    def cleanup_temp_file(self, temp_file):
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"⚠️ Cannot delete temporary file: {e}")

    def toggle_star(self):
        app = MDApp.get_running_app()
        chat_screen = app.root.get_screen('chat')
        chat_screen.toggle_file_star(self.file_id)

# 💬 Text Message Bubble Class مع دعم العربية المحسن وحجم ديناميكي
class TextMessageBubble(BoxLayout):
    message_text = StringProperty("")
    is_my_message = NumericProperty(0)
    message_time = StringProperty("")
    calculated_width = NumericProperty(300)
    calculated_height = NumericProperty(70)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(message_text=self.calculate_size)
        Clock.schedule_once(self.calculate_size, 0.1)

    def calculate_size(self, *args):
        """حساب حجم الفقاعة بناءً على طول النص"""
        try:
            # حساب العرض بناءً على طول النص
            text_length = len(self.message_text)
            
            # تحديد العرض المناسب
            if text_length <= 20:
                width = 200
            elif text_length <= 40:
                width = 250
            elif text_length <= 60:
                width = 300
            elif text_length <= 80:
                width = 350
            else:
                width = 400  # أقصى عرض
            
            # حساب الارتفاع بناءً على عدد الأسطر
            lines = (text_length // 30) + 1  # حوالي 30 حرفاً لكل سطر
            height = max(70, 60 + (lines * 25))  # ارتفاع ديناميكي
            
            self.calculated_width = width
            self.calculated_height = height
            
        except Exception as e:
            print(f"Error calculating bubble size: {e}")
            self.calculated_width = 300
            self.calculated_height = 70

# 🎨 KV Language مع تصميم جديد ومميزات الملفات وفقاعات ديناميكية
KV = '''
# 🎯 Welcome Screen
<WelcomeScreen>:
    MDFloatLayout:
        md_bg_color: "#f8f9fa"  # 🔵 رمادي فاتح
        
        Image:
            source: "logo.png"
            size_hint: 0.35, 0.35
            pos_hint: {"center_x": 0.5, "center_y": 0.7}
            allow_stretch: True
            keep_ratio: True
        
        MDLabel:
            id: app_title
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.4, 0.8, 1  # 🔵 أزرق
            font_size: "32sp"
            bold: True
            halign: "center"
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            size_hint_y: None
            height: 50
        
        MDLabel:
            id: welcome_subtitle
            text: ""
            theme_text_color: "Custom"
            text_color: 0.5, 0.5, 0.5, 1
            font_size: "16sp"
            halign: "center"
            pos_hint: {"center_x": 0.5, "center_y": 0.3}
            size_hint_y: None
            height: 80
            text_size: 350, None

# 🔐 Registration System Screens
<LoginScreen>:
    MDFloatLayout:
        md_bg_color: "#f8f9fa"  # 🔵 رمادي فاتح
        
        MDTopAppBar:
            id: login_toolbar
            title: ""
            elevation: 1
            md_bg_color: "#4285f4"  # 🔵 أزرق جوجل
            specific_text_color: 1, 1, 1, 1
            pos_hint: {"top": 1}
            
        MDLabel:
            id: select_user_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.2, 0.2, 1
            font_size: "18sp"
            halign: "center"
            pos_hint: {"center_x": 0.5, "top": 0.9}
            size_hint_y: None
            height: 40
        
        MDRoundFlatButton:
            id: student_btn
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.4, 0.8, 1
            line_color: 0.2, 0.4, 0.8, 1
            size_hint: 0.4, 0.06
            pos_hint: {"center_x": 0.3, "top": 0.83}
            on_press: root.show_student_form()
            font_name: 'ArabicFont'
                
        MDRoundFlatButton:
            id: teacher_btn
            text: ""
            theme_text_color: "Custom"
            text_color: 0.6, 0.6, 0.6, 1
            line_color: 0.6, 0.6, 0.6, 0.3
            size_hint: 0.4, 0.06
            pos_hint: {"center_x": 0.7, "top": 0.83}
            on_press: root.show_teacher_form()
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: name_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.73}
            icon_left: "account"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            line_color_focus: 0.2, 0.4, 0.8, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: id_field
            hint_text: ""
            mode: "fill" 
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.63}
            icon_left: "identifier"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            line_color_focus: 0.2, 0.4, 0.8, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: password_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.53}
            icon_left: "lock"
            password: True
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            line_color_focus: 0.2, 0.4, 0.8, 1
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: login_btn
            text: ""
            md_bg_color: 0.2, 0.4, 0.8, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.4}
            on_press: root.login_user()
            font_name: 'ArabicFont'
        
        MDFlatButton:
            id: forgot_password_btn
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.4, 0.8, 0.8
            size_hint: 0.4, None
            height: 40
            pos_hint: {"center_x": 0.5, "top": 0.33}
            on_press: root.show_forgot_password()
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: create_account_btn
            text: ""
            md_bg_color: 0.3, 0.7, 0.3, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.25}
            on_press: root.go_to_registration()
            font_name: 'ArabicFont'
        
        MDLabel:
            id: message_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.8, 0.2, 0.2, 1
            halign: "center"
            size_hint_y: None
            height: 30
            pos_hint: {"center_x": 0.5, "top": 0.15}
            font_name: 'ArabicFont'

<StudentRegistrationScreen>:
    MDFloatLayout:
        md_bg_color: "#f8f9fa"  # 🔵 رمادي فاتح
        
        MDTopAppBar:
            id: student_reg_toolbar
            title: ""
            elevation: 1
            md_bg_color: "#4285f4"  # 🔵 أزرق جوجل
            specific_text_color: 1, 1, 1, 1
            pos_hint: {"top": 1}
            left_action_items: [["arrow-left", lambda x: root.go_back_to_login()]]
        
        ArabicTextInput:
            id: student_name_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.85}
            icon_left: "account"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: student_id_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.75}
            icon_left: "identifier"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: student_password_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.65}
            icon_left: "lock"
            password: True
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        MDLabel:
            id: select_major_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.2, 0.2, 1
            font_size: "16sp"
            halign: "center"
            pos_hint: {"center_x": 0.5, "top": 0.58}
            size_hint_y: None
            height: 30
            font_name: 'ArabicFont'
        
        MDRoundFlatButton:
            id: major_dropdown
            text: ""
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.53}
            on_release: root.show_major_menu()
            font_name: 'ArabicFont'
        
        MDLabel:
            id: security_questions_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.2, 0.2, 1
            font_size: "16sp"
            halign: "center"
            pos_hint: {"center_x": 0.5, "top": 0.46}
            size_hint_y: None
            height: 30
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: security_question1_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.41}
            icon_left: "palette"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: security_question2_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.31}
            icon_left: "heart"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: security_question3_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.21}
            icon_left: "briefcase"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: create_student_btn
            text: ""
            md_bg_color: 0.2, 0.4, 0.8, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.1}
            on_press: root.register_student()
            font_name: 'ArabicFont'
        
        MDLabel:
            id: student_message_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.8, 0.2, 0.2, 1
            halign: "center"
            size_hint_y: None
            height: 30
            pos_hint: {"center_x": 0.5, "top": 0.02}
            font_name: 'ArabicFont'

<TeacherRegistrationScreen>:
    MDFloatLayout:
        md_bg_color: "#f8f9fa"  # 🔵 رمادي فاتح
        
        MDTopAppBar:
            id: teacher_reg_toolbar
            title: ""
            elevation: 1
            md_bg_color: "#4285f4"  # 🔵 أزرق جوجل
            specific_text_color: 1, 1, 1, 1
            pos_hint: {"top": 1}
            left_action_items: [["arrow-left", lambda x: root.go_back_to_login()]]
        
        ArabicTextInput:
            id: teacher_name_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.85}
            icon_left: "account"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: teacher_job_id_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.75}
            icon_left: "badge-account"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: teacher_password_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.65}
            icon_left: "lock"
            password: True
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        MDLabel:
            id: security_questions_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.2, 0.2, 1
            font_size: "16sp"
            halign: "center"
            pos_hint: {"center_x": 0.5, "top": 0.55}
            size_hint_y: None
            height: 30
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: security_question1_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.5}
            icon_left: "palette"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: security_question2_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.4}
            icon_left: "heart"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: security_question3_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.3}
            icon_left: "briefcase"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: create_teacher_btn
            text: ""
            md_bg_color: 0.2, 0.4, 0.8, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.18}
            on_press: root.register_teacher()
            font_name: 'ArabicFont'
        
        MDLabel:
            id: teacher_message_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.8, 0.2, 0.2, 1
            halign: "center"
            size_hint_y: None
            height: 30
            pos_hint: {"center_x": 0.5, "top": 0.08}
            font_name: 'ArabicFont'

<ForgotPasswordScreen>:
    MDFloatLayout:
        md_bg_color: "#f8f9fa"  # 🔵 رمادي فاتح
        
        MDTopAppBar:
            id: forgot_password_toolbar
            title: ""
            elevation: 1
            md_bg_color: "#4285f4"  # 🔵 أزرق جوجل
            specific_text_color: 1, 1, 1, 1
            pos_hint: {"top": 1}
            left_action_items: [["arrow-left", lambda x: root.go_back_to_login()]]
        
        MDLabel:
            id: select_user_type_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.2, 0.2, 1
            font_size: "18sp"
            halign: "center"
            pos_hint: {"center_x": 0.5, "top": 0.9}
            size_hint_y: None
            height: 40
            font_name: 'ArabicFont'
        
        MDRoundFlatButton:
            id: student_forgot_btn
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.4, 0.8, 1
            line_color: 0.2, 0.4, 0.8, 1
            size_hint: 0.4, 0.06
            pos_hint: {"center_x": 0.3, "top": 0.83}
            on_press: root.show_student_form()
            font_name: 'ArabicFont'
                
        MDRoundFlatButton:
            id: teacher_forgot_btn
            text: ""
            theme_text_color: "Custom"
            text_color: 0.6, 0.6, 0.6, 1
            line_color: 0.6, 0.6, 0.6, 0.3
            size_hint: 0.4, 0.06
            pos_hint: {"center_x": 0.7, "top": 0.83}
            on_press: root.show_teacher_form()
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: user_id_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.73}
            icon_left: "identifier"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            line_color_focus: 0.2, 0.4, 0.8, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: security_answer1_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.63}
            icon_left: "palette"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            line_color_focus: 0.2, 0.4, 0.8, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: security_answer2_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.53}
            icon_left: "heart"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            line_color_focus: 0.2, 0.4, 0.8, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: security_answer3_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.43}
            icon_left: "briefcase"
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            line_color_focus: 0.2, 0.4, 0.8, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: new_password_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.33}
            icon_left: "lock"
            password: True
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            line_color_focus: 0.2, 0.4, 0.8, 1
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: confirm_password_field
            hint_text: ""
            mode: "fill"
            fill_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.23}
            icon_left: "lock-check"
            password: True
            text_color: 0.2, 0.2, 0.2, 1
            hint_text_color: 0.6, 0.6, 0.6, 1
            line_color_focus: 0.2, 0.4, 0.8, 1
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: reset_password_btn
            text: ""
            md_bg_color: 0.2, 0.4, 0.8, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.1}
            on_press: root.reset_password()
            font_name: 'ArabicFont'
        
        MDLabel:
            id: forgot_message_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.8, 0.2, 0.2, 1
            halign: "center"
            size_hint_y: None
            height: 30
            pos_hint: {"center_x": 0.5, "top": 0.02}
            font_name: 'ArabicFont'

<MainMenuScreen>:
    MDFloatLayout:
        md_bg_color: "#f8f9fa"  # 🔵 رمادي فاتح
        
        MDTopAppBar:
            id: main_menu_toolbar
            title: ""
            elevation: 1
            md_bg_color: "#4285f4"  # 🔵 أزرق جوجل
            specific_text_color: 1, 1, 1, 1
            pos_hint: {"top": 1}
            left_action_items: [["logout", lambda x: root.logout()]]
        
        MDLabel:
            id: welcome_title
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.2, 0.2, 1
            font_size: "20sp"
            halign: "center"
            pos_hint: {"center_x": 0.5, "top": 0.85}
            size_hint_y: None
            height: 40
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: button1
            text: ""
            md_bg_color: 0.2, 0.4, 0.8, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.7}
            on_press: root.open_chat_system()
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: button2
            text: ""
            md_bg_color: 0.8, 0.5, 0.2, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.6}
            on_press: root.open_settings_system()
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: button3
            text: ""
            md_bg_color: 0.3, 0.7, 0.3, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.5}
            on_press: root.open_grades_system()
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: network_info_btn
            text: "🌐 معلومات الشبكة"
            md_bg_color: "#2196F3"
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.35}
            on_press: root.show_network_info()
            font_name: 'ArabicFont'
        
        MDLabel:
            id: menu_message_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.2, 0.2, 1
            halign: "center"
            size_hint_y: None
            height: 30
            pos_hint: {"center_x": 0.5, "top": 0.25}
            font_name: 'ArabicFont'

<SettingsScreen>:
    MDFloatLayout:
        md_bg_color: "#f8f9fa"  # 🔵 رمادي فاتح
        
        MDTopAppBar:
            id: settings_toolbar
            title: ""
            elevation: 1
            md_bg_color: "#4285f4"  # 🔵 أزرق جوجل
            specific_text_color: 1, 1, 1, 1
            pos_hint: {"top": 1}
            left_action_items: [["arrow-left", lambda x: root.go_back_to_main()]]
        
        MDLabel:
            id: settings_title
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.2, 0.2, 1
            font_size: "20sp"
            halign: "center"
            pos_hint: {"center_x": 0.5, "top": 0.85}
            size_hint_y: None
            height: 40
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: delete_account_btn
            text: ""
            md_bg_color: 0.8, 0.2, 0.2, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.7}
            on_press: root.show_delete_account_dialog()
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: change_password_btn
            text: ""
            md_bg_color: 0.2, 0.4, 0.8, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.6}
            on_press: root.show_change_password_dialog()
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: dark_mode_btn
            text: ""
            md_bg_color: 0.3, 0.3, 0.3, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.5}
            on_press: root.toggle_dark_mode()
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: privacy_settings_btn
            text: ""
            md_bg_color: 0.3, 0.7, 0.3, 1
            text_color: 1, 1, 1, 1
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.4}
            on_press: root.show_privacy_settings()
            font_name: 'ArabicFont'
        
        MDRaisedButton:
            id: ip_info_btn
            text: "🌐 عرض معلومات IP"
            md_bg_color: "#2196F3"
            size_hint: 0.8, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.3}
            on_press: root.show_ip_info()
            font_name: 'ArabicFont'
        
        MDLabel:
            id: settings_message_label
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.2, 0.2, 1
            halign: "center"
            size_hint_y: None
            height: 30
            pos_hint: {"center_x": 0.5, "top": 0.2}
            font_name: 'ArabicFont'

# 🔔 Notification Badge
<NotificationBadge@MDLabel>:
    size_hint: None, None
    size: 20, 20
    text: "0"
    halign: 'center'
    valign: 'center'
    font_size: '10sp'
    text_color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: 1, 0, 0, 1
        Ellipse:
            pos: self.pos
            size: self.size

# 💬 Text Message Bubble with Arabic Support - فقاعة ديناميكية
<TextMessageBubble>:
    orientation: 'horizontal'
    size_hint_y: None
    height: root.calculated_height
    padding: [10, 5]
    
    Widget:
        size_hint_x: 1 if root.is_my_message else None
        width: 0 if root.is_my_message else 50
    
    MDCard:
        size_hint: None, None
        size: root.calculated_width, root.calculated_height
        elevation: 2
        md_bg_color: "#4285f4" if root.is_my_message else "#E8F0FE"
        radius: [20, 20, 5, 20] if root.is_my_message else [20, 20, 20, 5]
        padding: [15, 10]
        
        BoxLayout:
            orientation: 'vertical'
            spacing: 5
            size_hint: 1, 1
            
            MDLabel:
                id: message_text_label
                text: root.message_text
                text_color: "white" if root.is_my_message else "black"
                size_hint_y: None
                height: self.texture_size[1]
                halign: "right"
                valign: "top"
                font_name: 'ArabicFont'
                font_size: '14sp'
                markup: True
                text_size: root.calculated_width - 30, None
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: 20
                
                Widget:
                    size_hint_x: 1
                    
                MDLabel:
                    id: time_label
                    text: root.message_time
                    size_hint_x: None
                    width: self.texture_size[0]
                    font_size: '10sp'
                    text_color: "white" if root.is_my_message else "gray"
                    halign: "right"

# 📁 File Message Bubble
<FileMessageBubble>:
    orientation: 'horizontal'
    size_hint: None, None
    size: 300, 220
    padding: [0, 5]
    
    Widget:
        size_hint_x: 1 if root.is_my_message else None
        width: 0 if root.is_my_message else 50
    
    MDCard:
        size_hint: None, None
        size: 250, 210
        elevation: 2
        md_bg_color: "#4285f4" if root.is_my_message else "#E8F0FE"
        radius: [20, 20, 5, 20] if root.is_my_message else [20, 20, 20, 5]
        padding: [10, 10]
        
        BoxLayout:
            orientation: 'vertical'
            spacing: 5
            
            MDLabel:
                text: root.file_icon
                font_size: '14sp'
                text_color: "white" if root.is_my_message else "gray"
                size_hint_y: 0.1
                halign: 'center'
            
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: 0.7
                padding: [5, 5]
                
                Image:
                    id: image_content
                    source: root.image_source
                    size_hint: 1, 1
                    allow_stretch: True
                    keep_ratio: True
                    opacity: 1 if root.file_type == "image" else 0
                
                BoxLayout:
                    orientation: 'vertical'
                    size_hint: 1, 1
                    opacity: 1 if root.file_type != "image" else 0
                    
                    MDLabel:
                        text: root.icon_source
                        font_size: '48sp'
                        halign: 'center'
                        size_hint_y: 0.6
                    
                    MDLabel:
                        text: root.file_name
                        font_size: '12sp'
                        halign: 'center'
                        size_hint_y: 0.4
                        text_color: "white" if root.is_my_message else "black"
                        shorten: True
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: 0.2
                spacing: 10
                
                MDLabel:
                    text: root.action_text
                    font_size: '9sp'
                    text_color: "white" if root.is_my_message else "gray"
                    size_hint_x: 0.7
                
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_x: 0.3
                    spacing: 5
                    
                    MDLabel:
                        id: file_time_label
                        text: root.message_time
                        font_size: '10sp'
                        text_color: "white" if root.is_my_message else "gray"
                        halign: 'center'
                        size_hint_x: 0.6
                    
                    MDRaisedButton:
                        id: star_btn
                        text: "⭐" if root.is_starred else "☆"
                        size_hint: None, None
                        size: 25, 25
                        font_size: '10sp'
                        md_bg_color: "#FFD700" if root.is_starred else "#CCCCCC"
                        on_press: root.toggle_star()

# 🔍 Image Zoom Dialog
<ZoomImage>:
    size_hint: (0.9, 0.9)
    auto_dismiss: True
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 10
        
        Image:
            id: zoomed_image
            source: ""
            size_hint: 1, 1
            allow_stretch: True
            keep_ratio: True
            
        MDRaisedButton:
            text: "إغلاق"
            size_hint: 1, None
            height: 50
            md_bg_color: "#FF5252"
            on_press: root.dismiss()

# 🎬 Video Player Dialog
<VideoPlayer>:
    video_source: ""
    size_hint: (0.95, 0.85)
    auto_dismiss: True
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 10
        
        Video:
            id: video_player
            source: root.video_source
            size_hint: 1, 0.8
            state: 'play'
            
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, 0.15
            spacing: 10
            
            MDRaisedButton:
                id: play_btn
                text: "⏸️ إيقاف"
                size_hint: 0.25, None
                height: 45
                md_bg_color: "#FF9800"
                on_press: root.toggle_play()
            
            MDRaisedButton:
                text: "⏹️ إيقاف"
                size_hint: 0.25, None
                height: 45
                md_bg_color: "#FF5252"
                on_press: root.stop_video()
            
            MDRaisedButton:
                text: "🔄 إعادة"
                size_hint: 0.25, None
                height: 45
                md_bg_color: "#4CAF50"
                on_press: root.replay_video()
            
            MDRaisedButton:
                text: "❌ إغلاق"
                size_hint: 0.25, None
                height: 45
                md_bg_color: "#1E88E5"
                on_press: root.dismiss()

# 📧 New Message Screen
<NewMessageScreen>:
    current_major: ""
    selected_recipients: []
    
    MDFloatLayout:
        md_bg_color: "#f8f9fa"  # 🔵 رمادي فاتح
        
        MDTopAppBar:
            id: new_message_toolbar
            title: ""
            elevation: 1
            md_bg_color: "#4285f4"  # 🔵 أزرق جوجل
            specific_text_color: 1, 1, 1, 1
            pos_hint: {"top": 1}
            left_action_items: [["arrow-left", lambda x: root.go_back_to_sessions()]]
        
        MDCard:
            size_hint: 0.9, 0.8
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            elevation: 2
            padding: 20
            spacing: 20
            
            BoxLayout:
                orientation: 'vertical'
                spacing: 15
                
                MDLabel:
                    id: new_message_title
                    text: ""
                    font_style: "H5"
                    halign: "center"
                    size_hint_y: None
                    height: 50
                    font_name: 'ArabicFont'
                
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 60
                    spacing: 10
                    
                    MDLabel:
                        id: select_major_text
                        text: ""
                        size_hint_x: 0.3
                        halign: "left"
                        bold: True
                        font_name: 'ArabicFont'
                    
                    MDRoundFlatButton:
                        id: major_selection_btn
                        text: ""
                        size_hint_x: 0.7
                        on_release: root.show_major_menu()
                        font_name: 'ArabicFont'
                
                ScrollView:
                    size_hint_y: None
                    height: 120
                    
                    GridLayout:
                        id: recipients_container
                        cols: 1
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: 5
                
                ArabicTextInput:
                    id: subject_input
                    hint_text: ""
                    mode: "fill"
                    size_hint_y: None
                    height: 60
                    font_name: 'ArabicFont'
                
                ArabicTextInput:
                    id: message_input
                    hint_text: ""
                    mode: "fill"
                    multiline: True
                    size_hint_y: 0.4
                    font_name: 'ArabicFont'
                
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: 60
                    spacing: 10
                    
                    MDRaisedButton:
                        id: attach_btn
                        text: ""
                        md_bg_color: "#34A853"  # 🟢 أخضر
                        size_hint_x: 0.3
                        on_press: root.show_attach_options()
                        font_name: 'ArabicFont'
                    
                    MDRaisedButton:
                        id: send_btn
                        text: ""
                        md_bg_color: "#4285f4"  # 🔵 أزرق
                        size_hint_x: 0.4
                        on_press: root.send_message()
                        font_name: 'ArabicFont'
                    
                    MDRaisedButton:
                        id: send_all_btn
                        text: ""
                        md_bg_color: "#FBBC05"  # 🟡 أصفر
                        size_hint_x: 0.3
                        on_press: root.send_to_all_major()
                        font_name: 'ArabicFont'
                
                MDLabel:
                    id: status_label
                    text: ""
                    theme_text_color: "Secondary"
                    halign: "center"
                    size_hint_y: None
                    height: 30
                    font_name: 'ArabicFont'

# 👥 Chat Sessions Screen
<ChatSessionsScreen>:
    MDFloatLayout:
        md_bg_color: "#f8f9fa"  # 🔵 رمادي فاتح
        
        MDTopAppBar:
            id: sessions_toolbar
            title: ""
            elevation: 1
            md_bg_color: "#4285f4"  # 🔵 أزرق جوجل
            specific_text_color: 1, 1, 1, 1
            pos_hint: {"top": 1}
            left_action_items: [["arrow-left", lambda x: root.go_back_to_main()]]
            right_action_items: [["refresh", lambda x: root.load_chat_sessions()], ["account-plus", lambda x: root.open_contacts()], ["bell", lambda x: root.show_notifications_menu()]]
            
            NotificationBadge:
                id: sessions_notification_badge
                pos_hint: {"right": 0.78, "top": 0.85}
                text: str(root.total_unread_messages)
                opacity: 1 if root.total_unread_messages > 0 else 0
        
        MDRaisedButton:
            id: new_message_btn
            text: ""
            md_bg_color: "#4285f4"  # 🔵 أزرق
            size_hint: 0.9, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.92}
            on_press: root.open_new_message()
            font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: search_sessions
            hint_text: ""
            size_hint: 0.9, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.85}
            icon_left: "magnify"
            mode: "fill"
            on_text: root.search_chat_sessions(self.text)
            font_name: 'ArabicFont'
        
        ScrollView:
            size_hint: 1, 0.75
            pos_hint: {"top": 0.72}
            do_scroll_x: False
            
            GridLayout:
                id: sessions_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
                padding: 10

# 👥 Contacts Screen
<ContactsScreen>:
    current_tab: "students"
    
    MDFloatLayout:
        md_bg_color: "#f8f9fa"  # 🔵 رمادي فاتح
        
        MDTopAppBar:
            id: contacts_toolbar
            title: ""
            elevation: 1
            md_bg_color: "#4285f4"  # 🔵 أزرق جوجل
            specific_text_color: 1, 1, 1, 1
            pos_hint: {"top": 1}
            left_action_items: [["arrow-left", lambda x: root.go_back_to_sessions()]]
            right_action_items: [["refresh", lambda x: root.load_contacts()], ["bell", lambda x: root.show_notifications_menu()]]
            
            NotificationBadge:
                id: contacts_notification_badge
                pos_hint: {"right": 0.78, "top": 0.85}
                text: str(root.total_unread_messages)
                opacity: 1 if root.total_unread_messages > 0 else 0
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 0.9, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.93}
            spacing: 10
            
            MDRaisedButton:
                id: students_btn
                text: ""
                size_hint: 0.5, 1
                md_bg_color: "#4285f4" if root.current_tab == "students" else "#E8F0FE"
                text_color: "white" if root.current_tab == "students" else "black"
                on_press: root.switch_tab("students")
                font_name: 'ArabicFont'
            
            MDRaisedButton:
                id: teachers_btn
                text: ""
                size_hint: 0.5, 1
                md_bg_color: "#4285f4" if root.current_tab == "teachers" else "#E8F0FE"
                text_color: "white" if root.current_tab == "teachers" else "black"
                on_press: root.switch_tab("teachers")
                font_name: 'ArabicFont'
        
        ArabicTextInput:
            id: search_field
            hint_text: ""
            size_hint: 0.9, None
            height: 50
            pos_hint: {"center_x": 0.5, "top": 0.85}
            icon_left: "magnify"
            mode: "fill"
            on_text: root.search_contacts(self.text)
            font_name: 'ArabicFont'
        
        ScrollView:
            size_hint: 1, 0.72
            pos_hint: {"top": 0.72}
            do_scroll_x: False
            
            GridLayout:
                id: contacts_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
                padding: 10

# 💬 Chat Screen
<ChatScreen>:
    MDFloatLayout:
        md_bg_color: "#f8f9fa"  # 🔵 رمادي فاتح
        
        MDTopAppBar:
            id: chat_toolbar
            title: ""
            elevation: 1
            md_bg_color: "#4285f4"  # 🔵 أزرق جوجل
            specific_text_color: 1, 1, 1, 1
            pos_hint: {"top": 1}
            left_action_items: [["arrow-left", lambda x: root.go_back_to_sessions()]]
            right_action_items: [["refresh", lambda x: root.load_messages()], ["auto-delete", lambda x: root.auto_cleanup()], ["bell", lambda x: root.show_notifications_menu()]]
            
            NotificationBadge:
                id: chat_notification_badge
                pos_hint: {"right": 0.78, "top": 0.85}
                text: str(root.unread_messages_in_chat)
                opacity: 1 if root.unread_messages_in_chat > 0 else 0
        
        MDLabel:
            id: chat_title
            text: ""
            theme_text_color: "Custom"
            text_color: 0.2, 0.2, 0.2, 1
            halign: "center"
            size_hint_y: None
            height: 30
            pos_hint: {"center_x": 0.5, "top": 0.92}
            markup: True
            font_name: 'ArabicFont'
        
        ScrollView:
            id: chat_scrollview
            size_hint: 1, 0.75
            pos_hint: {"top": 0.85}
            do_scroll_x: False
            
            GridLayout:
                id: chat_container
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                padding: [10, 10]
                spacing: 8
        
        MDFloatLayout:
            size_hint: 1, 0.15
            pos_hint: {"bottom": 1}
            md_bg_color: "#ffffff"
            
            ArabicTextInput:
                id: message_input
                hint_text: ""
                mode: "fill"
                size_hint: 0.55, None
                height: 50
                pos_hint: {"center_x": 0.3, "center_y": 0.5}
                multiline: True
                on_text_validate: root.send_message()
                font_name: 'ArabicFont'
            
            MDRaisedButton:
                id: send_chat_btn
                text: ""
                md_bg_color: "#4285f4"  # 🔵 أزرق
                size_hint: 0.15, None
                height: 50
                pos_hint: {"center_x": 0.55, "center_y": 0.5}
                on_press: root.send_message()
                font_name: 'ArabicFont'
            
            MDRaisedButton:
                id: attach_chat_btn
                text: ""
                md_bg_color: "#34A853"  # 🟢 أخضر
                size_hint: 0.15, None
                height: 50
                pos_hint: {"center_x": 0.75, "center_y": 0.5}
                on_press: root.show_attach_options()
                font_name: 'ArabicFont'
'''

# تحميل KV
Builder.load_string(KV)

# 🎯 Welcome Screen Class
class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_enter(self):
        self.ids.app_title.text = app_text("app_name")
        self.ids.welcome_subtitle.text = app_text("welcome_subtitle")
        Clock.schedule_once(self.go_to_login, 3)
    
    def go_to_login(self, dt):
        self.manager.current = 'login'

# 🔐 Login Screen Class
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user_type = "student"
    
    def on_enter(self):
        self.show_student_form()
    
    def show_student_form(self):
        self.current_user_type = "student"
        self.ids.name_field.hint_text = app_text("student_name")
        self.ids.id_field.hint_text = app_text("student_id")
        self.ids.password_field.hint_text = app_text("password")
        self.ids.login_btn.text = app_text("login")

    def login_user(self):
        print("Login functionality would go here")

# 🚀 Main Application
class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(LoginScreen(name='login'))
        
        sm.current = 'welcome'
        return sm

if __name__ == '__main__':
    import sys
    if not hasattr(sys, 'getandroidapilevel'):
        print("📱 Marsal APK built successfully!")
        print("📲 Install on Android device to use the full app")
    else:
        MainApp().run()
