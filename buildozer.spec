[app]

# ============================================================
# APPLICATION
# ============================================================

title = IoT Weather Monitor

package.name = weatherapp

package.domain = org.sai

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

version = 0.1


# ============================================================
# REQUIREMENTS
# ============================================================

# Do NOT pin python3 or hostpython3 here.
# python-for-android manages the Python versions used internally.

requirements = python3,kivy==2.3.1,pyjnius


# ============================================================
# DISPLAY
# ============================================================

orientation = portrait

fullscreen = 0


# ============================================================
# ANDROID
# ============================================================

android.api = 35

android.minapi = 24

android.ndk = 28c

android.ndk_api = 24

android.archs = arm64-v8a,armeabi-v7a


# ============================================================
# ANDROID SDK
# ============================================================

android.sdk_path = /usr/local/lib/android/sdk

android.skip_update = True

android.accept_sdk_license = True


# ============================================================
# ANDROID PERMISSIONS
# ============================================================

android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION


# ============================================================
# BLUETOOTH
# ============================================================

# HC-05 uses classic Bluetooth SPP.
#
# UUID used by the application:
#
# 00001101-0000-1000-8000-00805F9B34FB
#
# Bluetooth permissions above allow the Android application
# to discover/connect to paired Bluetooth devices.


# ============================================================
# ANDROID BACKUP
# ============================================================

android.allow_backup = True


# ============================================================
# PYTHON-FOR-ANDROID
# ============================================================

p4a.branch = master

# Leave the following unset so Buildozer/p4a uses the
# configured upstream branch.

# p4a.url =
# p4a.fork =
# p4a.commit =


# ============================================================
# BUILD ARTIFACT
# ============================================================

android.debug_artifact = apk


# ============================================================
# OPTIONAL APP ICON
# ============================================================

# Uncomment only if these files actually exist.

# icon.filename = %(source.dir)s/data/icon.png


# ============================================================
# OPTIONAL PRESPLASH
# ============================================================

# Uncomment only if the file actually exists.

# presplash.filename = %(source.dir)s/data/presplash.png


# ============================================================
# SOURCE EXCLUSIONS
# ============================================================

source.exclude_dirs = .git,.github,.buildozer,bin,__pycache__,venv,.venv


# ============================================================
# BUILD CONFIGURATION
# ============================================================

[buildozer]

log_level = 2

warn_on_root = 1