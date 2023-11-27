@echo off
start 123
ECHO Building project...
rmdir /s /q bin
mkdir bin
echo This is a dummy file > bin\dummy.txt
