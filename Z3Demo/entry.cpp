#include "pch.h"

/* invoke the api from ZW3D wrapped in "dllimport" */
extern "C" __declspec(dllexport) int MyCustomFunc(int a, int b, char* s) {
	WriteMessage(s);
	return a * b;
}