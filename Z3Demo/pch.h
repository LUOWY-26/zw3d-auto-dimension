// pch.h: 这是预编译标头文件。
// 下方列出的文件仅编译一次，提高了将来生成的生成性能。
// 这还将影响 IntelliSense 性能，包括代码完成和许多代码浏览功能。
// 但是，如果此处列出的文件中的任何一个在生成之间有更新，它们全部都将被重新编译。
// 请勿在此处添加要频繁更新的文件，这将使得性能优势无效。

#ifndef PCH_H
#define PCH_H
#include "framework.h"
#include <string>
#include <vector>
#include "VxApi.h"
using namespace std;

static void WriteMessage(int level, const char* format, ...)
{
	if (format)
	{
		va_list args;
		va_start(args, format);
		char message[1024];
		vsprintf_s(message, format, args);
		cvxMsgDisp2(message, level);
		//cvxMsgDisp(message);
		va_end(args);
	}
}
static void WriteMessage(const char* format, ...)
{
	if (format)
	{
		va_list args;
		va_start(args, format);
		char message[1024];
		vsprintf_s(message, format, args);
		//cvxMsgDisp2(message, (int)evxMsgLevel::information);
		cvxMsgDisp(message);
		va_end(args);
	}
}

static evxErrors ShowError(const char* file, const int line, const char* call, evxErrors irc)
{
	if (irc)
	{
		const char* err = NULL;
		err = cvxErrMsgGet((evxErrors)irc);
		WriteMessage(4, "*** ERROR code %d at line %d in %s:", irc, line, file);
		WriteMessage(4, "+++ %s", err);
		WriteMessage(4, "%s;", call);
	}
	return(irc);
}

#define ZF_CALL(X) (ShowError( __FILE__, __LINE__, #X, (X)))
#define ZF_VOID(X) X
#endif