[app]

title = IoT Weather Monitor
package.name = weatherapp
package.domain = org.iotweather

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

version = 1.0

requirements = python3,kivy==2.3.1,pyjnius

orientation = portrait
fullscreen = 0

android.api = 35
android.minapi = 23
android.archs = arm64-v8a

android.accept_sdk_license = True

android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION

log_level = 2
warn_on_root = 1