#!/bin/bash
#pyinstaller kontakt-tool.spec -y
pyinstaller -D -w widget.py --add-data="src:src" -n kontakt-tool -y
#pyinstaller -D -w MacOS/widget.py --add-data="Resources/src:src" -i app.ico -n kontakt-tool -y
cd dist
codesign -f -s "Developer ID Application: Owen zhang (Q7N5S6FHPU)" kontakt-tool.app
productbuild --component Kontakt-tool.app /Applications --sign "Developer ID Installer: Owen zhang (Q7N5S6FHPU)" --product kontakt-tool.app/Contents/Info.plist kontakt-tool.pkg
