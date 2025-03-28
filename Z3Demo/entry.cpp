#include "pch.h"
#include "json.hpp"

using json = nlohmann::json;

extern "C" __declspec(dllexport) int fileExportPDF(const char* jsonParams) {
	try {
		json params = json::parse(jsonParams);

		std::string path = params["path"].get<std::string>();
		int pdfType = params["pdfType"].get<int>();

		vxLongPath exportPath;
		strcpy_s(exportPath, sizeof(vxLongPath), path.c_str());

		svxPdfData pdfData{};
		evxExportType type = VX_EXPORT_TYPE_PDF;
		evxErrors err = cvxFileExportInit(type, pdfType, &pdfData);
		if (err != ZW_API_NO_ERROR) {
			return static_cast<int>(err);
		}

		err = cvxFileExport(type, exportPath, &pdfData);
		if (err == ZW_API_NO_ERROR) {
			WriteMessage("[console] export complete.");
		}
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
		return -1;  
	}
}

extern "C" __declspec(dllexport) int fileOpen(const char* jsonParams) {
	try {
		json params = json::parse(jsonParams);
		std::string filePath = params["filePath"].get<std::string>();
		vxLongPath openPath;
		strcpy_s(openPath, sizeof(vxLongPath), filePath.c_str());
		evxErrors err = cvxFileOpen(openPath);
		if (err == ZW_API_NO_ERROR)
		{
			WriteMessage("[console] open complete.");
		}
		return static_cast<int>(err);
	}
	catch(const std::exception& e){
		WriteMessage("JSON parse err: %s", e.what());
		return -1;  
	}
}

extern "C" __declspec(dllexport) void MyCommand(const char* params) {
	WriteMessage("传入参数=[%s]", params);//参数可忽略，输入~mycommand或者~mycommand(aaa)调用命令
	return;
}

/* invoke the api from ZW3D wrapped in "dllimport" */
extern "C" __declspec(dllexport) int MyCustomFunc(int a, int b, char* s) {
	WriteMessage(s);
	return a * b;
}

//extern "C" __declspec(dllexport) int fileOpen(const vxLongPath Name) {
//	evxErrors err = cvxFileOpen(Name);
//	return err;
//}

extern "C" __declspec(dllexport) int fileActive(const vxLongPath Name) {
	evxErrors err =  cvxFileActivate(Name);
	return err;
}

extern "C" __declspec(dllexport) int rootActive(const vxLongPath Path, const vxRootName Name) {
	evxErrors err = cvxRootActivate2(Path, Name);
	return err;
}

extern "C" __declspec(dllexport) int pathSet(const vxLongPath Name) {
	evxErrors err = cvxPathSet(Name);
	return err;
}

extern "C" __declspec(dllexport) int pathSearchFirst(const vxLongPath Name) {
	cvxPathSearchFirst(Name);
	return 0;
}

//extern "C" __declspec(dllexport) int fileExportPDF(vxLongPath path, int pdfType) {
//	svxPdfData pdfData{};
//	evxExportType type = VX_EXPORT_TYPE_PDF;
//	evxErrors err = cvxFileExportInit(type, pdfType, &pdfData);
//	err = cvxFileExport(type, path, &pdfData);
//	return 0;
//}

extern "C" __declspec(dllexport) int Z3DemoInit() {
	ZwCommandFunctionLoad("mycommand", MyCommand, ZW_LICENSE_CODE_GENERAL);//注册命令
	ZwCommandFunctionLoad("EXPPDF", fileExportPDF, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("FILEOPEN", fileOpen, ZW_LICENSE_CODE_GENERAL);
	return 0;
}

extern "C" __declspec(dllexport) int Z3DemoExit() {
	ZwCommandFunctionUnload("mycommand");//卸载命令
	return 0;
}