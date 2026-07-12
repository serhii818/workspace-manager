#include <windows.h>
#include <iostream>
#include <vector>

int main(int argc, char** argv) {
    STARTUPINFO si = { sizeof(si) };
    PROCESS_INFORMATION pi;

    std::string cmd = "python D:\\projects\\programing\\python2\\serious\\project_mgr_proto\\src\\wsmgr.py";

    for (int i = 1; i < argc; i++) {
        cmd += " ";
        cmd += argv[i];
    }

    std::vector<char> buff(cmd.begin(), cmd.end());
    buff.push_back('\0');

    if (CreateProcess(
        NULL,
        buff.data(),
        NULL,
        NULL,
        FALSE,
        0,
        NULL,
        NULL,
        &si,
        &pi
    )) {
        // Wait until the process finishes
        WaitForSingleObject(pi.hProcess, INFINITE);

        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);
    } else {
        std::cerr << "Failed to start process\n";
    }

    return 0;
}