[app]

title = IoT Weather Monitor
package.name = weatherapp
package.domain = org.sai

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas

version = 0.1

orientation = portrait
fullscreen = 0

requirements = python3,kivy==2.3.1,pyjnius

# -------------------------------------------------
# Android
# -------------------------------------------------

android.api = 35
android.minapi = 24

android.ndk = 25b
android.ndk_api = 24

android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path =

android.skip_update = True
android.accept_sdk_license = True

# Bluetooth / Android permissions
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION

android.archs = arm64-v8a,armeabi-v7a

android.allow_backup = True

# -------------------------------------------------
# python-for-android
# -------------------------------------------------

p4a.branch = master

# -------------------------------------------------
# Buildozer
# -------------------------------------------------

[buildozer]

log_level = 2
warn_on_root = 1