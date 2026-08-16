[app]

# ============================================================
# BASIC APP INFORMATION
# ============================================================

title = IoT Weather Monitor
package.name = weatherapp
package.domain = org.iotweather

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

version = 1.0

# ============================================================
# REQUIREMENTS
# ============================================================

requirements = python3,kivy==2.3.1,pyjnius

# ============================================================
# ORIENTATION
# ============================================================

orientation = portrait

# ============================================================
# ANDROID SETTINGS
# ============================================================

android.api = 35
android.minapi = 23

android.archs = arm64-v8a

android.accept_sdk_license = True

# ============================================================
# ANDROID PERMISSIONS
# ============================================================

android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION

# ============================================================
# ANDROID APP SETTINGS
# ============================================================

fullscreen = 0

# ============================================================
# PYTHON-FOR-ANDROID
# ============================================================

p4a.branch = master

# ============================================================
# BUILD SETTINGS
# ============================================================

log_level = 2

warn_on_root = 1

# ============================================================
# BACKGROUND / SERVICES
# ============================================================

# No Android service required for the current dashboard.

# ============================================================
# RELEASE / DEBUG
# ============================================================

# Debug APK is produced by:
# buildozer android debug