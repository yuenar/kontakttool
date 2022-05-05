#!/bin/bash
pyinstaller -D -w widget.py --onedir --target-arch="x86_64" --add-data="src:src" -i app.ico -n kontakt-tool -y
#python setup.py py2app --emulate-shell-environment --resources src

#cd dist
##/Users/owen/Qt/6.3.0/macos/bin/macdeployqt kontakt-tool.app
#codesign -f -s "Developer ID Application: Owen zhang (Q7N5S6FHPU)" -v kontakt-tool.app
#productbuild --component Kontakt-tool.app /Applications --sign "Developer ID Installer: Owen zhang (Q7N5S6FHPU)" --product kontakt-tool.app/Contents/Info.plist kontakt-tool.pkg
#

#pyi-makespec -Dw --add-data "../src/*:src" --key "1234567812345678" --osx-bundle-identifier "com.xxx.xxxxx" --codesign-identity "Developer ID Application: XXXXX (4J45KSVBG8)" --osx-entitlements-file entitlements.plist -i “icon.icns" -n “MyAPP" ../main.py
