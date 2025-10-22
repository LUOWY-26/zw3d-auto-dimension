#include "pch.h"
#include "json.hpp"
#include "zwapi_drawing_dimension.h"
#include "log_utils.h"
#include <random>
#include <cmath>
#include <algorithm>
#include <thread>      // std::this_thread::sleep_for
#include <chrono>      // std::chrono::seconds


#include <cmath>
#include <limits>

// 判断两个浮点数是否相等（近似）
bool almostEqual(double a, double b, double epsilon = 0.01/*std::numeric_limits<double>::epsilon()*/)
{
	// fabs(a-b) 与 epsilon 比较，同时考虑到数值大小缩放
	return std::fabs(a - b) <= epsilon /** std::fmax(1.0, std::fmax(std::fabs(a), std::fabs(b)))*/;
}

using json = nlohmann::json;

szwMatrix computeFrame(double spread = 100.0) {
	static std::random_device rd;
	static std::mt19937 gen(rd());
	std::uniform_real_distribution<> dis(-spread, spread);

	szwMatrix mat{};
	mat.identity = 0;

	mat.xx = 1; mat.yx = 0; mat.zx = 0; mat.xt = dis(gen);
	mat.xy = 0; mat.yy = 1; mat.zy = 0; mat.yt = dis(gen);
	mat.xz = 0; mat.yz = 0; mat.zz = 1; mat.zt = dis(gen);

	mat.ox = 0; mat.oy = 0; mat.oz = 0; mat.scale = 1.0;
	return mat;
}

std::string makeAsmName(const std::string& dir, int level) {
	return dir + "asm_lvl" + std::to_string(level) + ".Z3ASM";
}

std::vector<int> randomSplitTotal(int total, int depth) {
	std::vector<int> result(depth, 1);
	int remaining = total - depth;

	static std::random_device rd;
	static std::mt19937 gen(rd());

	for (int i = 0; i < depth; ++i) {
		int maxAlloc = remaining - (depth - 1 - i);
		std::uniform_int_distribution<> dis(0, maxAlloc);
		int r = dis(gen);
		result[i] += r;
		remaining -= r;
	}

	// 随机打乱层之间顺序（可选）
	std::shuffle(result.begin(), result.end(), gen);

	return result;
}

extern "C" __declspec(dllexport)
int createAssemblyTree(const char* jsonParams) {
	try {
		json params = json::parse(jsonParams);
		std::string partPath = params["partPath"];
		std::string saveDir = params["saveDir"];
		int depth = params["depth"];
		int total = params["totalInstances"];

		evxErrors err;

		auto perLayer = randomSplitTotal(total, depth);

		std::vector<std::string> asmPaths;

		for (int d = 0; d < depth; ++d) {
			std::string asmPath = makeAsmName("", d);
			vxLongPath asmFile;
			strcpy_s(asmFile, sizeof(vxLongPath), asmPath.c_str());
			err = cvxFileNew(asmFile);
			err = cvxFileSaveAs((saveDir + "\\" + asmFile).c_str());

			int insertCount = perLayer[d];

			for (int j = 0; j < insertCount; ++j) {
				szwComponentInsertData data;
				err = ZwComponentInsertInit(&data);
				strcpy_s(data.pathFile, sizeof(data.pathFile), partPath.c_str());
				szwMatrix mat = computeFrame(300);
				data.frame = &mat;
				err = ZwComponentInsert(data, nullptr, nullptr);
			}

			asmPaths.push_back(asmPath);
		}

		std::string topAsm = "root.Z3ASM";
		vxLongPath topPath;
		strcpy_s(topPath, sizeof(vxLongPath), topAsm.c_str());
		err = cvxFileNew(topPath);
		err = cvxFileSaveAs((saveDir + "\\" + topAsm).c_str());

		for (const auto& asmFile : asmPaths) {
			szwComponentInsertData data;
			err = ZwComponentInsertInit(&data);
			strcpy_s(data.pathFile, sizeof(data.pathFile), asmFile.c_str());
			szwMatrix mat = computeFrame(300);
			data.frame = &mat;
			err = ZwComponentInsert(data, nullptr, nullptr);
			err = cvxFileActivate(asmFile.c_str());
		}
		for (const auto& asmFile : asmPaths)
		{
			err = cvxFileActivate(asmFile.c_str());
			cvxFileClose2(asmFile.c_str(), 1);
		}
		err = cvxFileActivate(topAsm.c_str());
		cvxFileClose2(topAsm.c_str(), 1);
		if (err != ZW_API_NO_ERROR) {
			WriteLog("[console]Assembly created");
			json result;
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		}
		return 0;
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

int insertComponent(const char* jsonParams)
{
	try {
		json params = json::parse(jsonParams);
		std::string path = params["path"];

		evxErrors err;

		szwComponentInsertData data;
		err = ZwComponentInsertInit(&data);
		strcpy_s(data.pathFile, sizeof(data.pathFile), path.c_str());
		szwMatrix mat = computeFrame(300);
		data.frame = &mat;
		err = ZwComponentInsert(data, nullptr, nullptr);

		if (err != ZW_API_NO_ERROR) {
			WriteLog("[console]Insert component");
			json result;
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		}
		return 0;
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

int activateFile(const char* jsonParams)
{
	try {
		json params = json::parse(jsonParams);
		std::string filePath = params["filePath"];

		evxErrors err;

		err = cvxFileActivate(filePath.c_str());
		if (err != ZW_API_NO_ERROR) {
			WriteLog("[console]Activate file");
			json result;
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		}
		return 0;
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

int inqActiveFile(const char* jsonParams)
{
	try {
		json params = json::parse(jsonParams);
		evxErrors err = ZW_API_NO_ERROR;
		std::string fileName;
		vxLongName activeFileName;
		activeFileName[0] = 0;
		cvxFileInqActive(activeFileName, sizeof(activeFileName));

		if (err != ZW_API_NO_ERROR) {
			WriteLog("[console]{activeFile=%s}", activeFileName);
			json result;
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		}
		return 0;
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

int newFile(const char* jsonParams)
{
	try {
		json params = json::parse(jsonParams);
		std::string savePath = params["savePath"];

		evxErrors err;

		size_t pos = savePath.find_last_of("/\\");
		std::string saveDir = (pos != std::string::npos) ? savePath.substr(0, pos) : "";
		std::string fileName = (pos != std::string::npos) ? savePath.substr(pos + 1) : savePath;
		err = cvxFileNew(fileName.c_str());
		err = cvxFileSaveAs((saveDir + "\\" + fileName).c_str());
		if (err != ZW_API_NO_ERROR) {
			WriteLog("[console]New file");
			json result;
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		}
		return 0;
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

int inqActiveDir(const char* jsonParams)
{
	try {
		json params = json::parse(jsonParams);
		evxErrors err = ZW_API_NO_ERROR;
		vxPath activeFileDir;
		activeFileDir[0] = 0;
		cvxFileDirectory(activeFileDir);

		if (err != ZW_API_NO_ERROR) {
			WriteLog("[console]{activeDir=%s}", activeFileDir);
			json result;
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		}
		return 0;
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}


extern "C" __declspec(dllexport) int autoDimension(const char* jsonParams) {
	try {
		json params = json::parse(jsonParams);
		std::string path = params["path"].get<std::string>();
		int vuId = params["vuId"].get<int>(); //if vuId == 0, dimension all views

		ezwErrors err;
		/* rootName get from path */
		size_t lastSlashPos = path.find_last_of("/\\");
		std::string fileName = (lastSlashPos == std::string::npos) ? path : path.substr(lastSlashPos + 1);
		size_t lastDotPos = fileName.find_last_of('.');
		std::string rootName = (lastDotPos == std::string::npos) ? fileName : fileName.substr(0, lastDotPos);

		err = cvxRootActivate2(path.c_str(), rootName.c_str());

		szwAutoDimensionData autoDim;
		int dimCount;
		ZwDrawingDimensionAutoInit(&autoDim);
		autoDim.includeAuto = ZW_DIMENSION_AUTO_INCLUDE_ARC | ZW_DIMENSION_AUTO_INCLUDE_CIRCLE | ZW_DIMENSION_AUTO_INCLUDE_HOLE |
			ZW_DIMENSION_AUTO_INCLUDE_LINE | ZW_DIMENSION_AUTO_INCLUDE_HOLE_CALLOUT | ZW_DIMENSION_AUTO_INCLUDE_CYLIND_DIMENSIONS |
			ZW_DIMENSION_AUTO_INCLUDE_MAXIMUM_DIMENSIONS;
		autoDim.checkOrigin = 0;
		autoDim.pointOrigin = {};
		autoDim.horizontalDimension.enable = 0;
		autoDim.verticalDimension.enable = 0;

		if (vuId != 0)
		{
			szwEntityHandle* dims;
			szwEntityHandle stdVu;
			err = ZwApiIdtoHandle(vuId, &stdVu);

			err = ZwDrawingDimensionAutoCreate(stdVu, autoDim, &dimCount, &dims);

			if (err != ZW_API_NO_ERROR) {
				WriteLog("[console]Auto dimension");
				json result;
				result["return code"] = 0;
				WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
			}
		}
		else 
		{
			int count = 0;
			szwEntityHandle* pViews;
			ZwDrawingSheetViewListGet(nullptr, ZW_DRAWING_ALL_VIEW, &count, &pViews);
			for (int i = 0; i < count; i++)
			{
				err = ZwDrawingDimensionAutoCreate(pViews[i], autoDim, &dimCount, NULL);
				if (err != ZW_API_NO_ERROR) {
					WriteLog("[console]Auto dimension");
					json result;
					result["return code"] = 0;
					WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
				}
			}
		}

		err = cvxRootActivate2(NULL, NULL);

		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

extern "C" __declspec(dllexport) int fileExport(const char* jsonParams) {
	try {
		json params = json::parse(jsonParams);

		std::string path = params["path"].get<std::string>();
		int type = params["type"].get<int>();
		int subType = params["subType"].get<int>();

		/* rootName get from path */
		size_t lastSlashPos = path.find_last_of("/\\");
		std::string fileName = (lastSlashPos == std::string::npos) ? path : path.substr(lastSlashPos + 1);
		size_t lastDotPos = fileName.find_last_of('.');
		std::string rootName = (lastDotPos == std::string::npos) ? fileName : fileName.substr(0, lastDotPos);

		evxErrors err;

		err = cvxRootActivate2(path.c_str(), rootName.c_str());

		vxLongPath exportPath;
		strcpy_s(exportPath, sizeof(vxLongPath), path.c_str());

		switch (type)
		{
		case 1:
		{
			svxImgData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 2:
		{
			svxPdfData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 3:
		{
			svxGRPData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 4:
		{
			svxDWGData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 5:
		{
			svxIGESData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 6:
		{
			svxSTEPData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 7:
		{
			svxJTData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 8:
		case 9:
		{
			svxPARAData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 10:
		case 11:
		{
			svxCAT5Data data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 12:
		{
			svxHTMLData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 13:
		{
			svxSTLData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 14:
		{
			svxOBJData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 15:
		case 16:
		{
			svxIDFData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		default:
			break;
		}

		if (err == ZW_API_NO_ERROR) {
			WriteLog("[console] export complete.");
			json result;
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		}

		err = cvxRootActivate2(NULL, NULL);

		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

extern "C" __declspec(dllexport) int fileOpen(const char* jsonParams) {
	json result;
	try {
		json params = json::parse(jsonParams);

		std::string filePath = params["filePath"].get<std::string>();
		vxLongPath openPath;
		strcpy_s(openPath, sizeof(vxLongPath), filePath.c_str());
		/* rootName get from path */
		size_t lastSlashPos = filePath.find_last_of("/\\");
		std::string fileName = (lastSlashPos == std::string::npos) ? filePath : filePath.substr(lastSlashPos + 1);

		printf("open file get data");
		evxErrors err;

		char openFileName[256];
		cvxFileInqOpen(openFileName, sizeof(openFileName));

		if (!strcmp(fileName.c_str(), openFileName))
		{
			WriteLog("[console] file already opened.");
			result["return code"] = -1;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
			return ZW_API_NO_ERROR;
		}

		cvxFileClose2(openPath, 2);
		err = cvxFileOpen(openPath);
		if (err == ZW_API_NO_ERROR)
		{
			WriteLog("[console] open complete.");
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		}
		return static_cast<int>(err);
	}
	catch(const std::exception& e){
		WriteLog("JSON parse err: %s", e.what());
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;  
	}
}

extern "C" __declspec(dllexport) int fileSaveOrClose(const char* jsonParams) {
	try {
		json params = json::parse(jsonParams);
		int close = params["close"].get<int>();
		evxErrors err = cvxFileSave3(close, 1, 0);
		if (err == ZW_API_NO_ERROR)
		{
			WriteLog("[console] save complete.");
			json result;
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		}
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

// 计算两个向量的叉积
szwPoint crossProduct(const szwPoint& a, const szwPoint& b) {
	return {
		a.y * b.z - a.z * b.y,
		a.z * b.x - a.x * b.z,
		a.x * b.y - a.y * b.x
	};
}

// 判断是否为零向量
bool isZeroVector(const szwPoint& v, double eps = 1e-8) {
	return std::fabs(v.x) < eps && std::fabs(v.y) < eps && std::fabs(v.z) < eps;
}

// 判断两个向量是否平行
bool areParallel(const szwPoint& a, const szwPoint& b) {
	szwPoint cp = crossProduct(a, b);
	return isZeroVector(cp);
}


void normalize(szwPoint& v) {
	double length = std::sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
	if (length > 1e-8) {
		v.x /= length;
		v.y /= length;
		v.z /= length;
	}
}

szwPoint getLabelPosition(szwPoint P1, szwPoint P2, szwPoint Q1, szwPoint Q2,
	szwPoint M1, szwPoint M2, double offset = 10.0) {
	szwPoint V_edge = { P2.x - P1.x, P2.y - P1.y, P2.z - P1.z };
	szwPoint V_between = { M2.x - M1.x, M2.y - M1.y, M2.z - M1.z };

	// 中点
	szwPoint center = { (M1.x + M2.x) / 2, (M1.y + M2.y) / 2, (M1.z + M2.z) / 2 };

	// 如果需要偏移
	if (offset != 0.0) {
		szwPoint normal = crossProduct(V_edge, V_between);
		szwPoint offsetDir = crossProduct(normal, V_edge);
		normalize(offsetDir);
		center.x += offsetDir.x * offset;
		center.y += offsetDir.y * offset;
		center.z += offsetDir.z * offset;
	}

	return center;
}


extern "C" __declspec(dllexport) int standardViewCreate(const char* jsonParams) {
	try {
		char actFileName[256];
		cvxFileInqActive(actFileName, sizeof(actFileName));
		std::string actFile = actFileName;
		size_t lastDotPos = actFile.find_last_of('.');
		std::string suffixName = (lastDotPos == std::string::npos) ? actFile : actFile.substr(lastDotPos + 1, std::string::npos);
		std::string prefixName = (lastDotPos == std::string::npos) ? actFile : actFile.substr(0, lastDotPos);

		json params = json::parse(jsonParams);
		std::string path = params["path"].get<std::string>();
		/* rootName get from path */
		size_t lastSlashPos = path.find_last_of("/\\");
		std::string fileName = (lastSlashPos == std::string::npos) ? path : path.substr(lastSlashPos + 1);
		lastDotPos = fileName.find_last_of('.');
		std::string rootName = (lastDotPos == std::string::npos) ? fileName : fileName.substr(0, lastDotPos);

		ezwErrors err;

		/* target check class, keep in the sheet environment */
		if (suffixName != "Z3DRW")
		{
			if (suffixName == "Z3ASM" || suffixName == "Z3PRT")
			{
				WriteLog("newFile: %s", (rootName + ".Z3DRW").c_str());
				err = cvxFileOpen((rootName + ".Z3DRW").c_str());
				if (err != 0)
				{
					cvxFileNew((rootName + ".Z3DRW").c_str());
				}
			}
			else 
			{
				WriteLog("newFile: %s", (rootName + ".Z3DRW").c_str());
				err = cvxFileOpen((rootName + ".Z3DRW").c_str());
				if (err != 0)
				{
					cvxFileNew((rootName + ".Z3DRW").c_str());
				}
			}
		}

		//std::string rootName = params["rootName"].get<std::string>();
		int type = params["type"].get<int>();
		double x = params["x"].get<double>();
		double y = params["y"].get<double>();
		szwPoint2 location{x, y};

		szwViewStandardData stdVuData;

		err = ZwDrawingViewStandardDataInit(&stdVuData);
		strcpy_s(stdVuData.path, sizeof(zwPath), path.c_str());
		strcpy_s(stdVuData.rootName, sizeof(zwRootName), rootName.c_str());
		stdVuData.type = (ezwStandardViewType)0;
		stdVuData.location = location;
		stdVuData.option.viewType = (ezwDrawingViewMethod)type;

		stdVuData.scaleType = ZW_VIEW_USE_SHEET_SCALE;
		stdVuData.viewAttribute.scaleRatioX = 1;
		stdVuData.viewAttribute.scaleRatioY = 5;

		szwEntityHandle stdVu;
		err = ZwDrawingViewStandardCreate(stdVuData, &stdVu);

		if (err != ZW_API_NO_ERROR) {
			WriteLog("[console] std view created.");
			json result;
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		}
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

szwPoint projectPointToLine(const szwPoint2& P, const szwPoint& A, const szwPoint& B) {
	double dx = B.x - A.x;
	double dy = B.y - A.y;

	double len_squared = dx * dx + dy * dy;

	if (len_squared == 0.0) {
		return { A.x, A.y };
	}

	double px = P.x - A.x;
	double py = P.y - A.y;

	double t = (px * dx + py * dy) / len_squared;

	szwPoint Q;
	Q.x = A.x + t * dx;
	Q.y = A.y + t * dy;

	return Q;
}

extern "C" __declspec(dllexport) int linearOffsetDimension(const char* jsonParams) {
	try {
		//assume the view is active
		json params = json::parse(jsonParams);

		int lineId1 = params["id1"].get<int>();
		int lineId2 = params["id2"].get<int>();

		szwPoint firstPoint = { params["first point"]["x"].get<double>(), params["first point"]["y"].get<double>()};
		szwPoint secondPoint = { params["second point"]["x"].get<double>(), params["second point"]["y"].get<double>()};
		szwPoint textPoint = { params["text point"]["x"].get<double>(), params["text point"]["y"].get<double>(), 0 };

		ezwErrors err;
		szwEntityHandle lineHdl1;
		szwEntityHandle lineHdl2;
		err = ZwApiIdtoHandle(lineId1, &lineHdl1);
		err = ZwApiIdtoHandle(lineId2, &lineHdl2);


		szwCurve curve1;
		ZwCurveNURBSDataGet(lineHdl1, 1, &curve1);
		szwCurve curve2;
		ZwCurveNURBSDataGet(lineHdl2, 1, &curve2);

		//special case, two line distance
		if (curve1.type == ZW_CURVE_LINE && curve2.type == ZW_CURVE_LINE && lineId1 != lineId2)
		{
			szwDrawingLinearOffsetDimension dataOff;
			dataOff.type = (ezwDimensionLinearOffsetType)1;
			dataOff.secondPoint.pointType = ZW_DRAWING_DIMENSION_MIDDLE_POINT;
			dataOff.firstPoint.pointType = ZW_DRAWING_DIMENSION_MIDDLE_POINT;
			dataOff.secondPoint.entityHandle = lineHdl1;
			dataOff.firstPoint.entityHandle = lineHdl2;
			dataOff.firstPoint.definingPoint = 0;
			dataOff.secondPoint.definingPoint = 0;
			dataOff.textPoint = { NULL, ZW_CRITICAL_FREE_POINT, 0, &textPoint };
			err = ZwDrawingDimensionLinearOffsetCreate(dataOff, NULL);

			if (err != ZW_API_NO_ERROR) {
				WriteLog("err code = %i, line to line", static_cast<int>(err));
				WriteLog("may has err id: %i, %i", lineId1, lineId2);
			}
			WriteLog("[console] linear offset dimension created.{%i, %i}", lineId1, lineId2);
			json result;
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
			return static_cast<int>(err);
		}
		else {
			szwDrawingLinearDimension data;
			data.type = ZW_DIMENSION_LINEAR_ALIGNED;
			data.firstPoint = { &lineHdl1, ZW_CRITICAL_FREE_POINT, 0, &firstPoint };
			data.secondPoint = { &lineHdl2, ZW_CRITICAL_FREE_POINT, 0, &secondPoint };
			data.textPoint = { NULL, ZW_CRITICAL_FREE_POINT, 0, &textPoint };

			if (lineId1 == lineId2)
			{
				if (almostEqual(firstPoint.x, secondPoint.x))
				{
					data.type = ZW_DIMENSION_LINEAR_VERTICAL;
				}
				else if (almostEqual(firstPoint.y, secondPoint.y))
				{
					data.type = ZW_DIMENSION_LINEAR_HORIZONTAL;
				}
			}
			else if (lineId1 != 0 && curve1.type == ZW_CURVE_LINE)
			{
				if (almostEqual(curve1.curveInformation.line.startPoint.x, curve1.curveInformation.line.endPoint.x))
				{
					data.type = ZW_DIMENSION_LINEAR_HORIZONTAL;
				}
				else if (almostEqual(curve1.curveInformation.line.startPoint.y, curve1.curveInformation.line.endPoint.y))
				{
					data.type = ZW_DIMENSION_LINEAR_VERTICAL;
				}
			}
			else if (lineId2 != 0 && curve2.type == ZW_CURVE_LINE)
			{
				if (almostEqual(curve2.curveInformation.line.startPoint.x, curve2.curveInformation.line.endPoint.x))
				{
					data.type = ZW_DIMENSION_LINEAR_HORIZONTAL;
				}
				else if (almostEqual(curve2.curveInformation.line.startPoint.y, curve2.curveInformation.line.endPoint.y))
				{
					data.type = ZW_DIMENSION_LINEAR_VERTICAL;
				}
			}
			else
			{
				if (almostEqual(firstPoint.x, secondPoint.x))
				{
					data.type = ZW_DIMENSION_LINEAR_VERTICAL;
				}
				else if (almostEqual(firstPoint.y, secondPoint.y))
				{
					data.type = ZW_DIMENSION_LINEAR_HORIZONTAL;
				}
			}

			szwEntityHandle out;
			err = ZwDrawingDimensionLinearCreate(data, &out);

			if (err != ZW_API_NO_ERROR) {
				WriteLog("err code = %i", static_cast<int>(err));
				WriteLog("may has err id: %i, %i", lineId1, lineId2);
			}

			WriteLog("[console] distance dimension created.{%i, %i}", lineId1, lineId2);
			json result;
			result["return code"] = 0;
			WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
			return static_cast<int>(err);
		}
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}


extern "C" __declspec(dllexport) int linearDimension(const char* jsonParams) {
	try {
		//assume the view is active
		json params = json::parse(jsonParams);

		int lineId = params["id"].get<int>();

		szwPoint startPoint = { params["start point"]["x"].get<double>(), params["start point"]["y"].get<double>(), 0 };
		szwPoint endPoint = { params["end point"]["x"].get<double>(), params["end point"]["y"].get<double>(), 0 };
		szwPoint textPoint = { params["text point"]["x"].get<double>(), params["text point"]["y"].get<double>(), 0 };

		ezwErrors err;
		szwEntityHandle lineHdl;
		szwDrawingLinearDimension data;
		data.type = ZW_DIMENSION_LINEAR_ALIGNED;

		err = ZwApiIdtoHandle(lineId, &lineHdl);

		szwCurve curve1;
		ZwCurveNURBSDataGet(lineHdl, 1, &curve1);


		if (lineId != 0 && curve1.type == ZW_CURVE_LINE)
		{
			data.firstPoint = { &lineHdl, ZW_CRITICAL_START_POINT, 0, &startPoint };
			data.secondPoint = { &lineHdl, ZW_CRITICAL_END_POINT, 0, &endPoint };
		}
		data.textPoint = { NULL, ZW_CRITICAL_FREE_POINT, 0, &textPoint };

		szwEntityHandle out;
		err = ZwDrawingDimensionLinearCreate(data, &out);

		if (err != ZW_API_NO_ERROR) {
			WriteLog("err code = %i", static_cast<int>(err));
		}
		WriteLog("[console] linear dimension created. {%i}", lineId);
		json result;
		result["return code"] = 0;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

extern "C" __declspec(dllexport) int drwGetEntData(const char* jsonParams) {
	try {
		//assume the view is active
		ezwErrors err;
		int count = 0;
		szwEntityHandle* pViews;
		ZwDrawingSheetViewListGet(nullptr, ZW_DRAWING_ALL_VIEW, &count, &pViews);

		string jstr;
		if (count > 0)
		{
			json viewGeom;
			viewGeom["view"] = (ezwDrawingViewMethod)1; // how to get the view type?
			viewGeom["entities"] = json::array();
			int cnt_geom = 0;
			szwEntityHandle* pGeoms;
			ZwDrawingViewGeometryListGet(pViews[0], ZW_DRAWING_SHOWN_GEOMETRY_COORESPONDING_EDGE_AND_FACE, &cnt_geom, &pGeoms);

			json jout;
			for (int i = 0; i < cnt_geom; i++)
			{
				szwEntityHandle entHandle1 = pGeoms[i];
				int pointsNum;
				szwEntityCriticalPointInfo* pointsInfo;
				err = ZwEntityCriticalPointInfoGet(entHandle1, &pointsNum, &pointsInfo);

				int id = 0;
				id = ZwApiHandleToId(entHandle1);
				json ent;
				ent["id"] = id;
				if (pointsNum == 3)
				{
					ent["type"] = "line";
					ent["points"]["start"] = {pointsInfo[0].point.x, pointsInfo[0].point.y};
					ent["points"]["end"] = { pointsInfo[1].point.x, pointsInfo[1].point.y };
					ent["points"]["middle"] = { pointsInfo[2].point.x, pointsInfo[2].point.y };
				}
				else if (pointsNum == 4)
				{
					ent["type"] = "arc";
					ent["points"]["center"] = { pointsInfo[0].point.x, pointsInfo[0].point.y };
					ent["points"]["start"] = { pointsInfo[1].point.x, pointsInfo[1].point.y };
					ent["points"]["end"] = { pointsInfo[2].point.x, pointsInfo[2].point.y };
					ent["points"]["middle"] = { pointsInfo[3].point.x, pointsInfo[3].point.y };
				}
				else if (pointsNum == 5)
				{
					ent["type"] = "circle";
					ent["points"]["center"] = { pointsInfo[0].point.x, pointsInfo[0].point.y };
					ent["points"]["0degree"] = { pointsInfo[1].point.x, pointsInfo[1].point.y };
					ent["points"]["90degree"] = { pointsInfo[2].point.x, pointsInfo[2].point.y };
					ent["points"]["180degree"] = { pointsInfo[3].point.x, pointsInfo[3].point.y };
					ent["points"]["270degree"] = { pointsInfo[4].point.x, pointsInfo[4].point.y };
				}
				viewGeom["entities"].push_back(ent);
			}
		}
		WriteLog("[console]Get drawing entities data");
		json result;
		result["return code"] = 0;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}


extern "C" __declspec(dllexport) int standardViewDimension(const char* jsonParams) {
	try {
		//assume the part is active
		char actFileName[256];
		cvxFileInqActive(actFileName, sizeof(actFileName));
		std::string actFile = actFileName;
		size_t lastDotPos = actFile.find_last_of('.');
		std::string suffixName = (lastDotPos == std::string::npos) ? actFile : actFile.substr(lastDotPos + 1, std::string::npos);
		std::string prefixName = (lastDotPos == std::string::npos) ? actFile : actFile.substr(0, lastDotPos);

		json params = json::parse(jsonParams);
		std::string path = params["path"].get<std::string>();
		/* rootName get from path */
		size_t lastSlashPos = path.find_last_of("/\\");
		std::string fileName = (lastSlashPos == std::string::npos) ? path : path.substr(lastSlashPos + 1);
		lastDotPos = fileName.find_last_of('.');
		std::string rootName = (lastDotPos == std::string::npos) ? fileName : fileName.substr(0, lastDotPos);

		ezwErrors err;

		/* target check class, keep in the sheet environment */
		if (suffixName != "Z3DRW")
		{
			if (suffixName == "Z3ASM" || suffixName == "Z3PRT")
			{
				WriteLog("newFile: %s", (rootName + ".Z3DRW").c_str());
				err = cvxFileOpen((rootName + ".Z3DRW").c_str());
				if (err != 0)
				{
					cvxFileNew((rootName + ".Z3DRW").c_str());
				}
			}
			else
			{
				WriteLog("newFile: %s", (rootName + ".Z3DRW").c_str());
				err = cvxFileOpen((rootName + ".Z3DRW").c_str());
				if (err != 0)
				{
					cvxFileNew((rootName + ".Z3DRW").c_str());
				}
			}
		}

		int type = params["type"].get<int>();
		double x = params["x"].get<double>();
		double y = params["y"].get<double>();
		szwPoint2 location{ x, y };

		std::string label = "TOP";
		switch (type)
		{
		case 1: 
		{
			label = "TOP";
			break;
		}
		case 2:
		{
			label = "FRONT";
			break;
		}
		case 3:
		{
			label = "RIGHT";
			break;
		}
		case 4:
		{
			label = "BACK";
			break;
		}
		case 5:
		{
			label = "BOTTOM";
			break;
		}
		case 6:
		{
			label = "LEFT";
			break;
		}
		case 7:
		{
			label = "ISOMETRIC";
			break;
		}
		case 39:
		{
			label = "DIMETRIC";
			break;
		}
		default:
			break;
		}

		szwViewAttribute stdVuAtt;
		stdVuAtt.showLabel = 1;
		strcpy_s(stdVuAtt.label, sizeof(zwString32), label.c_str());
		stdVuAtt.displayMode = ZW_VIEW_HIDDEN_LINE;
		stdVuAtt.scaleType = (ezwViewScaleType)0;
		stdVuAtt.showScale = 0;
		stdVuAtt.scaleRatioX = 0.5;
		stdVuAtt.scaleRatioY = 1;
		szwViewStandardData stdVuData;

		err = ZwDrawingViewStandardDataInit(&stdVuData);
		stdVuData.viewAttribute = stdVuAtt;

		if (err != ZW_API_NO_ERROR) {
			WriteLog("err code = %i", static_cast<int>(err));
		}

		strcpy_s(stdVuData.path, sizeof(zwPath), path.c_str());
		strcpy_s(stdVuData.rootName, sizeof(zwRootName), rootName.c_str());
		stdVuData.type = (ezwStandardViewType)0;
		stdVuData.location = location;
		stdVuData.option.viewType = (ezwDrawingViewMethod)type;

		szwEntityHandle stdVu;
		err = ZwDrawingViewStandardCreate(stdVuData, &stdVu);

		if (err != ZW_API_NO_ERROR) {
			WriteLog("err code = %i", static_cast<int>(err));
		}

		json viewGeom;
		viewGeom["view id"] = ZwApiHandleToId(stdVu);
		viewGeom["view"] = type;
		viewGeom["entities"] = json::array();

		/*err = ZwViewActiveGet(&activeVu);*/

		//szwAutoDimensionData autoDim;
		//int dimCount;
		//ZwDrawingDimensionAutoInit(&autoDim);
		//autoDim.includeAuto = ZW_DIMENSION_AUTO_INCLUDE_ARC | ZW_DIMENSION_AUTO_INCLUDE_CIRCLE | ZW_DIMENSION_AUTO_INCLUDE_HOLE |
		//	ZW_DIMENSION_AUTO_INCLUDE_LINE | ZW_DIMENSION_AUTO_INCLUDE_HOLE_CALLOUT | ZW_DIMENSION_AUTO_INCLUDE_CYLIND_DIMENSIONS |
		//	ZW_DIMENSION_AUTO_INCLUDE_MAXIMUM_DIMENSIONS;
		//autoDim.checkOrigin = 0;
		//autoDim.pointOrigin = {};
		//autoDim.horizontalDimension.enable = 0;
		//autoDim.verticalDimension.enable = 0;
		//szwEntityHandle* dims;
		//err = ZwDrawingDimensionAutoCreate(stdVu, autoDim, &dimCount, &dims);
		//if (err != ZW_API_NO_ERROR) {
		//	WriteLog("err code = %i", static_cast<int>(err));%i, %i", lineId1, lineId2
		//}

		szwEntityHandle* ents;
		int entNum;
		err = ZwDrawingViewGeometryListGet(stdVu, (ezwDrawingGeometryType)2, &entNum, &ents);

		for (int i = 0; i < entNum; i++)
		{
			szwEntityHandle entHandle1 = ents[i];
			int pointsNum;
			szwEntityCriticalPointInfo* pointsInfo;
			err = ZwEntityCriticalPointInfoGet(entHandle1, &pointsNum, &pointsInfo);

			int id = 0;
			id = ZwApiHandleToId(entHandle1);
			json ent;
			ent["id"] = id;
			if (pointsNum == 3)
			{
				ent["type"] = "line";
				ent["points"]["start"] = { pointsInfo[0].point.x, pointsInfo[0].point.y };
				ent["points"]["end"] = { pointsInfo[1].point.x, pointsInfo[1].point.y };
				ent["points"]["middle"] = { pointsInfo[2].point.x, pointsInfo[2].point.y };
			}
			else if (pointsNum == 4)
			{
				ent["type"] = "arc";
				ent["points"]["center"] = { pointsInfo[0].point.x, pointsInfo[0].point.y };
				ent["points"]["start"] = { pointsInfo[1].point.x, pointsInfo[1].point.y };
				ent["points"]["end"] = { pointsInfo[2].point.x, pointsInfo[2].point.y };
				ent["points"]["middle"] = { pointsInfo[3].point.x, pointsInfo[3].point.y };
			}
			else if (pointsNum == 5)
			{
				ent["type"] = "circle";
				ent["points"]["center"] = { pointsInfo[0].point.x, pointsInfo[0].point.y };
				ent["points"]["0degree"] = { pointsInfo[1].point.x, pointsInfo[1].point.y };
				ent["points"]["90degree"] = { pointsInfo[2].point.x, pointsInfo[2].point.y };
				ent["points"]["180degree"] = { pointsInfo[3].point.x, pointsInfo[3].point.y };
				ent["points"]["270degree"] = { pointsInfo[4].point.x, pointsInfo[4].point.y };
			}
			viewGeom["entities"].push_back(ent);
		}
		WriteLog("entities num = %i", static_cast<int>(entNum));
		ZwEntityHandleListFree(entNum, &ents);
		//ZwEntityHandleListFree(dimCount, &dims);

		//export to png
		svxImgData data{};
		evxExportType eType = (evxExportType)1;
		err = cvxFileExportInit(eType, 3, &data);
		if (err != ZW_API_NO_ERROR) {
			WriteLog("err code = %i", static_cast<int>(err));
		}
		vxLongPath exportPath;
		strcpy_s(exportPath, sizeof(vxLongPath), "D:/AI_AUTODIM_DATA/stdvu_output.png");
		err = cvxFileExport(eType, exportPath, &data);
		//export end

		if (err != ZW_API_NO_ERROR) {
			WriteLog("err code = %i", static_cast<int>(err));
		}
		WriteLog("[console] std view created.");

		std::ofstream out("D:/AI_AUTODIM_DATA/stdvu_output.json");
		if (out.is_open()) {
			out << viewGeom.dump(4);
			out.close();

			std::ofstream done("D:/AI_AUTODIM_DATA/stdvu_output.done");
			done << "done";
			done.close();
		}
		else {
			WriteLog("Failed to write result to file.");
		}

		json result;
		result["return code"] = 0;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);

		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}


extern "C" __declspec(dllexport) void MyCommand(const char* params) {
	WriteLog("传入参数=[%s]", params);//参数可忽略，输入~mycommand或者~mycommand(aaa)调用命令
	return;
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


extern "C" __declspec(dllexport) const char* getViewLines()
{
	try {
		int count = 0;
		szwEntityHandle* pViews;
		ZwDrawingSheetViewListGet(nullptr, ZW_DRAWING_ALL_VIEW, &count, &pViews);

		string jstr;
		if (count > 0)
		{
			int cnt_geom = 0;
			szwEntityHandle* pGeoms;
			ZwDrawingViewGeometryListGet(pViews[0], ZW_DRAWING_SHOWN_GEOMETRY_COORESPONDING_EDGE_AND_FACE, &cnt_geom, &pGeoms);

			json jout;
			for (int i = 0; i < cnt_geom; i++)
			{
				szwCurve curve;
				ZwCurveNURBSDataGet(pGeoms[i], 1, &curve);
				switch (curve.type)
				{
				case ZW_CURVE_LINE:
					jout["type"] = "line";
					jout["data"] = json();
					jout["data"]["start point"] = { curve.curveInformation.line.startPoint.x,curve.curveInformation.line.startPoint.y };
					jout["data"]["end point"] = { curve.curveInformation.line.endPoint.x,curve.curveInformation.line.endPoint.y };
					break;
				case ZW_CURVE_ARC:
					jout["type"] = "arc";
					jout["data"] = json();
					jout["data"]["radius"] = curve.curveInformation.arc.radius;
					jout["data"]["start point"] = { curve.curveInformation.arc.startPoint.x,curve.curveInformation.arc.startPoint.y };
					jout["data"]["end point"] = { curve.curveInformation.arc.endPoint.x,curve.curveInformation.arc.endPoint.y };
					jout["data"]["start angle"] = curve.curveInformation.arc.startAngle;
					jout["data"]["end angle"] = curve.curveInformation.arc.endAngle;
					jout["data"]["center point"] = { curve.curveInformation.arc.centerPoint.x,curve.curveInformation.arc.centerPoint.y };
					break;
				case ZW_CURVE_CIRCLE:
					jout["data"]["radius"] = curve.curveInformation.circle.radius;
					jout["data"]["center point"] = { curve.curveInformation.circle.centerPoint.x,curve.curveInformation.circle.centerPoint.y };
					break;
				default:
					continue;
				}
			}
			jstr = jout.dump();
		}
		return jstr.c_str();
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		return "";
	}
}


extern "C" __declspec(dllexport) int RadialDimension(const char* jsonParams) {
	try
	{
		json params = json::parse(jsonParams);

		int lineId = params["id"].get<int>();

		szwPoint point = { params["point"]["x"].get<double>(), params["point"]["y"].get<double>(), 0 };
		szwPoint textPoint = { params["text point"]["x"].get<double>(), params["text point"]["y"].get<double>(), 0 };

		ezwErrors err;
		szwEntityHandle lineHdl;
		szwRadialDimensionData data;
		data.type = ZW_RADIAL_RADIAL;

		if (lineId != 0)
		{
			err = ZwApiIdtoHandle(lineId, &lineHdl);
			data.entity = { &lineHdl, ZW_CRITICAL_FREE_POINT, 0, &point };
		}
		else
		{
			data.entity = { NULL, ZW_CRITICAL_FREE_POINT ,0,&point };
		}
		data.textPoint = { NULL, ZW_CRITICAL_FREE_POINT, 0, &textPoint };

		//szwEntityHandle out;
		err = ZwDrawingDimensionRadialCreate(data, nullptr);

		if (err != ZW_API_NO_ERROR) {
			WriteLog("err code = %i", static_cast<int>(err));
		}
		WriteLog("[console] radial dimension created. {%i}", lineId);
		json result;
		result["return code"] = 0;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

extern "C" __declspec(dllexport) int ArcLengthDimension(const char* jsonParams) {
	try
	{
		json params = json::parse(jsonParams);

		int lineId = params["arc id"].get<int>();

		szwPoint point = { params["arc point"]["x"].get<double>(), params["arc point"]["y"].get<double>(), 0 };
		szwPoint textPoint = { params["text point"]["x"].get<double>(), params["text point"]["y"].get<double>(), 0 };

		ezwErrors err;
		szwEntityHandle lineHdl;
		szwDrawingArcDimensionData data;

		if (lineId != 0)
		{
			err = ZwApiIdtoHandle(lineId, &lineHdl);
			data.arcEntity = { &lineHdl, ZW_CRITICAL_FREE_POINT, 0, &point };
		}
		else
		{
			data.arcEntity = { NULL, ZW_CRITICAL_FREE_POINT ,0,&point };
		}
		data.textPoint = { NULL, ZW_CRITICAL_FREE_POINT, 0, &textPoint };

		szwEntityHandle out;
		err = ZwDrawingDimensionArcCreate(data,&out);

		if (err != ZW_API_NO_ERROR) {
			WriteLog("err code = %i", static_cast<int>(err));
		}
		WriteLog("[console] arc length dimension created. {%i}", lineId);
		json result;
		result["return code"] = 0;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}

extern "C" __declspec(dllexport) int HoleCalloutDimension(const char* jsonParams) {
	try
	{
		json params = json::parse(jsonParams);

		int holeId = params["hole curve id"].get<int>();
		int vuId = params["view id"].get<int>();

		szwPoint2 textPoint = { params["text point"]["x"].get<double>(), params["text point"]["y"].get<double>() };

		ezwErrors err;
		szwEntityHandle holeHdl, vuHdl;
		szwDrawingHoleCalloutData data;
		err = ZwDrawingDimensionHoleCalloutInit(&data);
		data.type = ZW_HOLE_CALLOUT_SHAPE_RADIAL;
		err = ZwApiIdtoHandle(vuId, &vuHdl);
		data.viewHandle = vuHdl;
		err = ZwApiIdtoHandle(holeId, &holeHdl);
		szwDrawingHoleCalloutHole hole{ holeHdl, &textPoint};
		data.holes = &hole;
		data.count = 1;

		int count_out = 0;
		//szwEntityHandle* out;
		err = ZwDrawingDimensionHoleCalloutCreate(data, &count_out, nullptr);
		//ZwEntityHandleListFree(count_out, &out);

		if (err != ZW_API_NO_ERROR) {
			WriteLog("err code = %i", static_cast<int>(err));
		}
		WriteLog("[console] hole callout dimension created., {%i}", holeId);
		json result;
		result["return code"] = 0;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteLog("JSON parse err: %s", e.what());
		json result;
		result["return code"] = 1;
		WriteResultToJsonFile("D:/AI_AUTODIM_DATA/zw3d_result.json", result);
		return -1;
	}
}


extern "C" __declspec(dllexport) int ZW3D_V1Init() {
	ZwCommandFunctionLoad("mycommand", MyCommand, ZW_LICENSE_CODE_GENERAL);//注册命令

	ZwCommandFunctionLoad("FILEOPEN", fileOpen, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("FILEEXPORT", fileExport, ZW_LICENSE_CODE_GENERAL);
	//ZwCommandFunctionLoad("FILESAVE", fileSaveOrClose, ZW_LICENSE_CODE_GENERAL);

	ZwCommandFunctionLoad("STDVUCREATE", standardViewCreate, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("STDVUDIM", standardViewDimension, ZW_LICENSE_CODE_GENERAL);

	ZwCommandFunctionLoad("LINDIM", linearDimension, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("LINOFFSETDIM", linearOffsetDimension, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("AUTODIM", autoDimension, ZW_LICENSE_CODE_GENERAL);

	ZwCommandFunctionLoad("RADIALDIM", RadialDimension, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("ARCLENDIM", ArcLengthDimension, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("HOLECALLOUTDIM", HoleCalloutDimension, ZW_LICENSE_CODE_GENERAL);

	ZwCommandFunctionLoad("ASMTREE", createAssemblyTree, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("COMPINSERT", insertComponent, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("FILENEW", newFile, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("FILEACTIVE", activateFile, ZW_LICENSE_CODE_GENERAL);
	return 0;
}

extern "C" __declspec(dllexport) int ZW3D_V1Exit() {
	ZwCommandFunctionUnload("mycommand");//卸载命令
	return 0;
}