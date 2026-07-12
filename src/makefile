CC = "cl.exe"
target = ".\wsmgr.cpp"
output = ".\wsmgr.exe"
env_setup = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

compile:
	
	cmd /c "call $(env_setup) && $(CC) $(target) /Fe:$(output)"	

run: compile
	$(output)
