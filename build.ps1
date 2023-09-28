nuitka --windows-disable-console --enable-plugin=pyqt5 --standalone --windows-icon-from-ico=.\src\resources\icon.ico --output-dir=build --output-filename="Simple Create MC Server Tool" --onefile .\src\main.py

mkdir .\build\build -Force

cp -Force ".\build\Simple Create MC Server Tool.exe" .\build\build -recurse
cp -Force .\src\resources\ .\build\build -recurse

rm -Force ".\build\Simple Create MC Server Tool.exe"