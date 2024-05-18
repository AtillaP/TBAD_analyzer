@echo OFF

set temp=%1

if %temp:~-5,-1%==.txt (goto one_input) else (goto set_frame)

:set_frame
set /P frame=Which frame would you check?: 
if not "%frame%"=="" goto continue
goto set_frame
:continue

:set_pruefpunkt
set /P pruefpunkt=Which pruefpunkt would you check?: 
if not "%pruefpunkt%"=="" goto continue
goto set_pruefpunkt
:continue

:set_projekt
set /P projekt=Which projekt would you check?: 
if not "%projekt%"=="" goto continue
goto set_projekt
:continue

pause
cls
python "D:\casdev\TBAD-Analyzer\main.py" %1 %frame% %pruefpunkt% %projekt%
goto end

:one_input
cls
python "D:\casdev\TBAD-Analyzer\main.py" %temp%

:end
pause