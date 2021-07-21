@echo OFF
cd C:\Windows\System32
RD /S /Q "%WinDir%\System32\GroupPolicy"
RD /S /Q "%WinDir%\System32\GroupPolicyUsers"
gpupdate.exe /force
pause