
[app]
title = MarsalApp
package.name = marsalapp
package.domain = com.marsal

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.1
requirements = python3,kivy,kivymd,arabic-reshaper,python-bidi,pillow,requests

[buildozer]
log_level = 2

[android]
api = 33
minapi = 21
android.allow_backup = true
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

[android:meta-data]
android.app.libs = android

[android:source]
include_patterns = assets/*,fonts/*
