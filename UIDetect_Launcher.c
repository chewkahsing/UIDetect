#define UNICODE
#define _UNICODE

#include <windows.h>
#include <stdio.h>
#include <wchar.h>

int WINAPI wWinMain(
    HINSTANCE hInstance,
    HINSTANCE hPrevInstance,
    PWSTR pCmdLine,
    int nCmdShow
)
{
    wchar_t exePath[MAX_PATH];
    wchar_t baseDir[MAX_PATH];
    wchar_t launcherPath[MAX_PATH];
    wchar_t pythonPath[MAX_PATH];
    wchar_t commandLine[2048];

    // --------------------------------------------------
    // Find the location of UIDetect.exe
    // --------------------------------------------------

    DWORD length = GetModuleFileNameW(
        NULL,
        exePath,
        MAX_PATH
    );

    if (length == 0 || length >= MAX_PATH)
    {
        MessageBoxW(
            NULL,
            L"Unable to determine the UIDetect installation folder.",
            L"UIDetect",
            MB_ICONERROR
        );

        return 1;
    }

    wcscpy_s(
        baseDir,
        MAX_PATH,
        exePath
    );

    wchar_t *lastSlash = wcsrchr(
        baseDir,
        L'\\'
    );

    if (lastSlash)
        *lastSlash = L'\0';

    // --------------------------------------------------
    // Find UIDetect_Launcher.py
    // --------------------------------------------------

    swprintf_s(
        launcherPath,
        MAX_PATH,
        L"%s\\UIDetect_Launcher.py",
        baseDir
    );

    if (GetFileAttributesW(launcherPath) == INVALID_FILE_ATTRIBUTES)
    {
        MessageBoxW(
            NULL,
            L"UIDetect_Launcher.py could not be found.",
            L"UIDetect",
            MB_ICONERROR
        );

        return 1;
    }

    // --------------------------------------------------
    // Find pythonw.exe
    // --------------------------------------------------

    DWORD pythonResult = SearchPathW(
        NULL,
        L"pythonw.exe",
        NULL,
        MAX_PATH,
        pythonPath,
        NULL
    );

    // --------------------------------------------------
    // If pythonw.exe is not found in PATH,
    // check common Python installation locations
    // --------------------------------------------------

    if (pythonResult == 0)
    {
        const wchar_t *pythonLocations[] =
        {
            L"C:\\Program Files\\Python313\\pythonw.exe",
            L"C:\\Program Files\\Python313\\python.exe",
            L"C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Python\\Python313\\pythonw.exe",
            L"C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
        };

        wchar_t expandedPath[MAX_PATH];

        for (int i = 0; i < 4; i++)
        {
            ExpandEnvironmentStringsW(
                pythonLocations[i],
                expandedPath,
                MAX_PATH
            );

            if (GetFileAttributesW(expandedPath) != INVALID_FILE_ATTRIBUTES)
            {
                wcscpy_s(
                    pythonPath,
                    MAX_PATH,
                    expandedPath
                );

                pythonResult = 1;
                break;
            }
        }
    }

    // --------------------------------------------------
    // Python still not found
    // --------------------------------------------------

    if (pythonResult == 0)
    {
        MessageBoxW(
            NULL,
            L"Python could not be found.\n\n"
            L"Please install Python 3.13 before starting UIDetect.",
            L"UIDetect",
            MB_ICONERROR
        );

        return 1;
    }

    // --------------------------------------------------
    // Build command
    // --------------------------------------------------

    swprintf_s(
        commandLine,
        2048,
        L"\"%s\" \"%s\"",
        pythonPath,
        launcherPath
    );

    // --------------------------------------------------
    // Start UIDetect Launcher
    // --------------------------------------------------

    STARTUPINFOW si;
    PROCESS_INFORMATION pi;

    ZeroMemory(
        &si,
        sizeof(si)
    );

    ZeroMemory(
        &pi,
        sizeof(pi)
    );

    si.cb = sizeof(si);

    BOOL success = CreateProcessW(
        pythonPath,
        commandLine,
        NULL,
        NULL,
        FALSE,
        CREATE_NO_WINDOW,
        NULL,
        baseDir,
        &si,
        &pi
    );

    if (!success)
    {
        wchar_t errorMessage[512];

        DWORD errorCode = GetLastError();

        swprintf_s(
            errorMessage,
            512,
            L"Failed to start UIDetect Launcher.\n\n"
            L"Windows error code: %lu",
            errorCode
        );

        MessageBoxW(
            NULL,
            errorMessage,
            L"UIDetect",
            MB_ICONERROR
        );

        return 1;
    }

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return 0;
}