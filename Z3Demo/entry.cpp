#include "pch.h"
#include "json.hpp"
#include "zwapi_drawing_dimension.h"
#include<fstream>

using json = nlohmann::json;

extern "C" __declspec(dllexport) int autoDimension(const char* jsonParams) {
	try {
		json params = json::parse(jsonParams);
		std::string path = params["path"].get<std::string>();
		int vuId = params["vuId"].get<int>(); //if vuId == 0, dimension all views

		ezwErrors err;
		/* rootName get from path */
		size_t lastSlashPos = path.find_last_of("/\\");
		std::string fileName = (lastSlashPos == std::string::npos) ? path : path.substr(lastSlashPos + 1);
		int lastDotPos = fileName.find_last_of('.');
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
				WriteMessage("err code = %i", static_cast<int>(err));
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
					WriteMessage("err code = %i", static_cast<int>(err));
				}
			}
		}

		err = cvxRootActivate2(NULL, NULL);

		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
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
		int lastDotPos = fileName.find_last_of('.');
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
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 2:
		{
			svxPdfData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 3:
		{
			svxGRPData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 4:
		{
			svxDWGData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 5:
		{
			svxIGESData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 6:
		{
			svxSTEPData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 7:
		{
			svxJTData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 8:
		case 9:
		{
			svxPARAData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 10:
		case 11:
		{
			svxCAT5Data data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 12:
		{
			svxHTMLData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 13:
		{
			svxSTLData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 14:
		{
			svxOBJData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		case 15:
		case 16:
		{
			svxIDFData data{};
			evxExportType eType = (evxExportType)type;
			err = cvxFileExportInit(eType, subType, &data);
			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
			}

			err = cvxFileExport(eType, exportPath, &data);
			break;
		}
		default:
			break;
		}

		if (err == ZW_API_NO_ERROR) {
			WriteMessage("[console] export complete.");
		}

		err = cvxRootActivate2(NULL, NULL);

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
		/* rootName get from path */
		size_t lastSlashPos = filePath.find_last_of("/\\");
		std::string fileName = (lastSlashPos == std::string::npos) ? filePath : filePath.substr(lastSlashPos + 1);

		evxErrors err;

		char openFileName[256];
		cvxFileInqOpen(openFileName, sizeof(openFileName));

		if (!strcmp(fileName.c_str(), openFileName))
		{
			WriteMessage("[console] file already opened.");
			return ZW_API_NO_ERROR;
		}

		cvxFileClose2(openPath, 2);
		err = cvxFileOpen(openPath);
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

extern "C" __declspec(dllexport) int fileSaveOrClose(const char* jsonParams) {
	try {
		json params = json::parse(jsonParams);
		int close = params["close"].get<int>();
		evxErrors err = cvxFileSave3(close, 1, 0);
		if (err == ZW_API_NO_ERROR)
		{
			WriteMessage("[console] save complete.");
		}
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
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
				WriteMessage("newFile: %s", (rootName + ".Z3DRW").c_str());
				err = cvxFileOpen((rootName + ".Z3DRW").c_str());
				if (err != 0)
				{
					cvxFileNew((rootName + ".Z3DRW").c_str());
				}
			}
			else 
			{
				WriteMessage("newFile: %s", (rootName + ".Z3DRW").c_str());
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

		if (err != ZW_API_NO_ERROR) {
			WriteMessage("err code = %i", static_cast<int>(err));
		}

		strcpy_s(stdVuData.path, sizeof(zwPath), path.c_str());
		strcpy_s(stdVuData.rootName, sizeof(zwRootName), rootName.c_str());
		stdVuData.type = (ezwStandardViewType)0;
		stdVuData.location = location;
		stdVuData.option.viewType = (ezwDrawingViewMethod)type;

		szwEntityHandle stdVu;
		err = ZwDrawingViewStandardCreate(stdVuData, &stdVu);

		if (err != ZW_API_NO_ERROR) {
			WriteMessage("err code = %i", static_cast<int>(err));
		}
		WriteMessage("[console] std view created.");
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
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

		szwPoint2 firstPoint = { params["first point"]["x"].get<double>(), params["first point"]["y"].get<double>()};
		szwPoint2 secondPoint = { params["second point"]["x"].get<double>(), params["second point"]["y"].get<double>()};
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
		if (curve1.type == ZW_CURVE_LINE && curve2.type == ZW_CURVE_LINE)
		{
			szwDrawingLinearOffsetDimension dataOff;
			dataOff.type = (ezwDimensionLinearOffsetType)1;
			dataOff.secondPoint.pointType = ZW_DRAWING_DIMENSION_MIDDLE_POINT;
			dataOff.firstPoint.pointType = ZW_DRAWING_DIMENSION_MIDDLE_POINT;
			dataOff.secondPoint.entityHandle = lineHdl1;
			dataOff.firstPoint.entityHandle = lineHdl2;

			dataOff.textPoint = { NULL, ZW_CRITICAL_FREE_POINT, 0, &textPoint };
			err = ZwDrawingDimensionLinearOffsetCreate(dataOff, NULL, NULL);

			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i, line to line", static_cast<int>(err));
				WriteMessage("may has err id: %i, %i", lineId1, lineId2);
			}
			WriteMessage("[console] linear offset dimension created.");
			return static_cast<int>(err);
		}

		else if(curve1.type == ZW_CURVE_LINE || curve2.type == ZW_CURVE_LINE)
		{
			szwDrawingLinearOffsetDimension dataOff;
			dataOff.type = (ezwDimensionLinearOffsetType)2;
			
			dataOff.firstPoint.pointType = ZW_DRAWING_DIMENSION_ARC_CENTER;
			dataOff.secondPoint.pointType = ZW_DRAWING_DIMENSION_FREE_POINT;

			if (curve1.type == ZW_CURVE_ARC || curve1.type == ZW_CURVE_CIRCLE)
			{
				//dataOff.secondPoint.entityHandle = lineHdl2;
				dataOff.firstPoint.entityHandle = lineHdl1;

				dataOff.secondPoint.freePoint = firstPoint;

				szwPoint pointProject = projectPointToLine(firstPoint, curve2.curveInformation.line.startPoint, curve2.curveInformation.line.endPoint);
				dataOff.firstPoint.freePoint = { pointProject.x, pointProject.y };
			}
			else
			{
				//dataOff.secondPoint.entityHandle = lineHdl1;
				dataOff.firstPoint.entityHandle = lineHdl2;

				dataOff.secondPoint.freePoint = secondPoint;
				
				szwPoint pointProject = projectPointToLine(secondPoint, curve1.curveInformation.line.startPoint, curve1.curveInformation.line.endPoint);
				dataOff.firstPoint.freePoint = { pointProject.x, pointProject.y };
			}
			dataOff.firstPoint.definingPoint = 0;
			dataOff.secondPoint.definingPoint = 0;
			dataOff.textPoint = { NULL, ZW_CRITICAL_FREE_POINT, 0, &textPoint };
			err = ZwDrawingDimensionLinearOffsetCreate(dataOff, NULL, NULL);

			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i, point to line", static_cast<int>(err));
				WriteMessage("may has err id: %i, %i", lineId1, lineId2);
			}
			WriteMessage("[console] linear offset dimension created.");
			return static_cast<int>(err);
		}

		else {

			szwDrawingLinearDimension data;
			data.type = ZW_DIMENSION_LINEAR_ALIGNED;

			data.firstPoint.referenceEntityHandle = &lineHdl1;
			data.secondPoint.referenceEntityHandle = &lineHdl2;
			data.firstPoint.controlPointIndex = 0;
			data.secondPoint.controlPointIndex = 0;
			data.textPoint = { NULL, ZW_CRITICAL_FREE_POINT, 0, &textPoint };

			if (curve1.type == ZW_CURVE_ARC || curve1.type == ZW_CURVE_CIRCLE)
			{
				data.firstPoint.criticalPointType = ZW_CRITICAL_CENTER_POINT;
				szwPoint circleCenter = { firstPoint.x, firstPoint.y, 0 };
				data.firstPoint.point = &circleCenter;
			}
			else if (curve1.type == ZW_CURVE_LINE)
			{
				data.firstPoint.criticalPointType = ZW_CRITICAL_FREE_POINT;
				szwPoint pointProject = projectPointToLine(secondPoint, curve1.curveInformation.line.startPoint, curve1.curveInformation.line.endPoint);
				data.firstPoint.point = &pointProject;
			}

			if (curve2.type == ZW_CURVE_ARC || curve2.type == ZW_CURVE_CIRCLE)
			{
				data.secondPoint.criticalPointType = ZW_CRITICAL_CENTER_POINT;
				szwPoint circleCenter = { secondPoint.x, secondPoint.y, 0 };
				data.secondPoint.point = &circleCenter;
			}
			else if (curve2.type == ZW_CURVE_LINE)
			{
				data.secondPoint.criticalPointType = ZW_CRITICAL_FREE_POINT;
				szwPoint pointProject = projectPointToLine(firstPoint, curve2.curveInformation.line.startPoint, curve2.curveInformation.line.endPoint);
				data.secondPoint.point = &pointProject;
			}

			szwEntityHandle out;
			err = ZwDrawingDimensionLinearCreate(data, nullptr, &out);

			if (err != ZW_API_NO_ERROR) {
				WriteMessage("err code = %i", static_cast<int>(err));
				WriteMessage("may has err id: %i, %i", lineId1, lineId2);
			}

			WriteMessage("[console] distance dimension created.");
			return static_cast<int>(err);
		}
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
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

		if (lineId != 0)
		{
			err = ZwApiIdtoHandle(lineId, &lineHdl);
			data.firstPoint = { &lineHdl, ZW_CRITICAL_FREE_POINT, 0, &startPoint};
			data.secondPoint = { &lineHdl, ZW_CRITICAL_FREE_POINT, 0, &endPoint};
		}
		else
		{
			data.firstPoint = { NULL, ZW_CRITICAL_FREE_POINT ,0,&startPoint };
			data.secondPoint = { NULL, ZW_CRITICAL_FREE_POINT ,0,&endPoint };
		}
		data.textPoint = { NULL, ZW_CRITICAL_FREE_POINT, 0, &textPoint };

		szwEntityHandle out;
		err = ZwDrawingDimensionLinearCreate(data, nullptr, &out);

		if (err != ZW_API_NO_ERROR) {
			WriteMessage("err code = %i", static_cast<int>(err));
		}
		WriteMessage("[console] linear dimension created.");
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
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
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
		return -1;
	}
}

extern "C" __declspec(dllexport) void getViewLines1(szwEntityHandle * pViews, int cnt_view)
{
	try {
		//int cnt_view = 0;
		//szwEntityHandle* pViews;
		//ZwDrawingSheetViewListGet(nullptr, ZW_DRAWING_ALL_VIEW, &cnt_view, &pViews);

		string jstr;
		json jVus{};
		for (int j = 0; j < cnt_view; j++)
		{
			json jVu;
			jVu["view id"] = ZwApiHandleToId(pViews[j]);
			jVu["curves"] = {};

			int cnt_geom = 0;
			szwEntityHandle* pGeoms;
			ezwErrors err = ZwDrawingViewGeometryListGet(pViews[0], ZW_DRAWING_SHOWN_GEOMETRY_COORESPONDING_EDGE_AND_FACE, &cnt_geom, &pGeoms);
			for (int i = 0; i < cnt_geom; i++)
			{
				json jCrv;
				szwCurve curve;
				ZwCurveNURBSDataGet(pGeoms[i], 1, &curve);
				switch (curve.type)
				{
				case ZW_CURVE_LINE:
					jCrv["curve id"] = ZwApiHandleToId(pGeoms[i]);
					jCrv["type"] = "line";
					jCrv["data"] = json();
					jCrv["data"]["start point"] = { curve.curveInformation.line.startPoint.x,curve.curveInformation.line.startPoint.y };
					jCrv["data"]["end point"] = { curve.curveInformation.line.endPoint.x,curve.curveInformation.line.endPoint.y };
					break;
				case ZW_CURVE_ARC:
					jCrv["curve id"] = ZwApiHandleToId(pGeoms[i]);
					jCrv["type"] = "arc";
					jCrv["data"] = json();
					jCrv["data"]["radius"] = curve.curveInformation.arc.radius;
					jCrv["data"]["start point"] = { curve.curveInformation.arc.startPoint.x,curve.curveInformation.arc.startPoint.y };
					jCrv["data"]["end point"] = { curve.curveInformation.arc.endPoint.x,curve.curveInformation.arc.endPoint.y };
					jCrv["data"]["start angle"] = curve.curveInformation.arc.startAngle;
					jCrv["data"]["end angle"] = curve.curveInformation.arc.endAngle;
					jCrv["data"]["center point"] = { curve.curveInformation.arc.centerPoint.x,curve.curveInformation.arc.centerPoint.y };
					break;
				case ZW_CURVE_CIRCLE:
					jCrv["curve id"] = ZwApiHandleToId(pGeoms[i]);
					jCrv["type"] = "arc";
					jCrv["data"] = json();
					jCrv["data"]["radius"] = curve.curveInformation.circle.radius;
					jCrv["data"]["center point"] = { curve.curveInformation.circle.centerPoint.x,curve.curveInformation.circle.centerPoint.y };
					break;
				default:
					continue;
				}
				jVu["curves"].push_back(jCrv);
			}
			jVus.push_back(jVu);
		}
		//ZwEntityHandleListFree(cnt_view, &pViews);
		jstr = jVus.dump(4);

		std::ofstream out("C:/Users/lwy/Desktop/stdvu_output.json");
		if (out.is_open())
		{
			out << jstr;
			out.close();
		}

		std::ofstream done("C:/Users/lwy/Desktop/stdvu_output.done");
		done << "done";
		done.close();

		return;
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
		return;
	}
}

extern "C" __declspec(dllexport) void getViewLines2(szwEntityHandle stdVu, int type)
{
	ezwErrors err;
	json viewGeom;

	viewGeom["view"] = type;
	viewGeom["entities"] = json::array();

	szwEntityHandle* ents;
	int entNum;
	ZwDrawingViewGeometryListGet(stdVu, (ezwDrawingGeometryType)2, &entNum, &ents);

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
			ent["start"] = { pointsInfo[0].point.x, pointsInfo[0].point.y };
			ent["end"] = { pointsInfo[1].point.x, pointsInfo[1].point.y };
			ent["middle"] = { pointsInfo[2].point.x, pointsInfo[2].point.y };
		}
		else if (pointsNum == 4)
		{
			ent["type"] = "arc";
			ent["center"] = { pointsInfo[0].point.x, pointsInfo[0].point.y };
			ent["start"] = { pointsInfo[1].point.x, pointsInfo[1].point.y };
			ent["end"] = { pointsInfo[2].point.x, pointsInfo[2].point.y };
			ent["middle"] = { pointsInfo[3].point.x, pointsInfo[3].point.y };
		}
		else if (pointsNum == 5)
		{
			ent["type"] = "circle";
			ent["center"] = { pointsInfo[0].point.x, pointsInfo[0].point.y };
			ent["0degree"] = { pointsInfo[1].point.x, pointsInfo[1].point.y };
			ent["90degree"] = { pointsInfo[2].point.x, pointsInfo[2].point.y };
			ent["180degree"] = { pointsInfo[3].point.x, pointsInfo[3].point.y };
			ent["270degree"] = { pointsInfo[4].point.x, pointsInfo[4].point.y };
		}
		viewGeom["entities"].push_back(ent);
	}
	WriteMessage("entities num = %i", static_cast<int>(entNum));
	ZwEntityHandleListFree(entNum, &ents);

	if (err != ZW_API_NO_ERROR) {
		WriteMessage("err code = %i", static_cast<int>(err));
	}
	WriteMessage("[console] std view created.");

	std::ofstream out("C:/Users/lwy/Desktop/stdvu_output.json");
	if (out.is_open()) {
		out << viewGeom.dump(4);
		out.close();

		std::ofstream done("C:/Users/lwy/Desktop/stdvu_output.done");
		done << "done";
		done.close();
	}
	else {
		WriteMessage("Failed to write result to file.");
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
				WriteMessage("newFile: %s", (rootName + ".Z3DRW").c_str());
				err = cvxFileOpen((rootName + ".Z3DRW").c_str());
				if (err != 0)
				{
					cvxFileNew((rootName + ".Z3DRW").c_str());
				}
			}
			else
			{
				WriteMessage("newFile: %s", (rootName + ".Z3DRW").c_str());
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
			WriteMessage("err code = %i", static_cast<int>(err));
		}

		strcpy_s(stdVuData.path, sizeof(zwPath), path.c_str());
		strcpy_s(stdVuData.rootName, sizeof(zwRootName), rootName.c_str());
		stdVuData.type = (ezwStandardViewType)0;
		stdVuData.location = location;
		stdVuData.option.viewType = (ezwDrawingViewMethod)type;

		szwEntityHandle stdVu;
		err = ZwDrawingViewStandardCreate(stdVuData, &stdVu);

		if (err != ZW_API_NO_ERROR) {
			WriteMessage("err code = %i", static_cast<int>(err));
		}

		//export to png
		svxImgData data{};
		evxExportType eType = (evxExportType)1;
		err = cvxFileExportInit(eType, 3, &data);
		if (err != ZW_API_NO_ERROR) {
			WriteMessage("err code = %i", static_cast<int>(err));
		}
		vxLongPath exportPath;
		strcpy_s(exportPath, sizeof(vxLongPath), "C:/Users/gyj15/Desktop/zw3d/export/stdvu_output.png");
		err = cvxFileExport(eType, exportPath, &data);
		//export end

		// szwAutoDimensionData autoDim;
		// int dimCount;
		// ZwDrawingDimensionAutoInit(&autoDim);
		// autoDim.includeAuto = ZW_DIMENSION_AUTO_INCLUDE_ARC | ZW_DIMENSION_AUTO_INCLUDE_CIRCLE | ZW_DIMENSION_AUTO_INCLUDE_HOLE |
			// ZW_DIMENSION_AUTO_INCLUDE_LINE | ZW_DIMENSION_AUTO_INCLUDE_HOLE_CALLOUT | ZW_DIMENSION_AUTO_INCLUDE_CYLIND_DIMENSIONS |
			// ZW_DIMENSION_AUTO_INCLUDE_MAXIMUM_DIMENSIONS;
		// autoDim.checkOrigin = 0;
		// autoDim.pointOrigin = {};
		// autoDim.horizontalDimension.enable = 0;
		// autoDim.verticalDimension.enable = 0;
		//szwEntityHandle* dims;
		//err = ZwDrawingDimensionAutoCreate(stdVu, autoDim, &dimCount, &dims);
		// if (err != ZW_API_NO_ERROR) {
			// WriteMessage("err code = %i", static_cast<int>(err));
		// }
		// WriteMessage("[console]hole dimension complete", static_cast<int>(err));
		
		//getViewLines1(&stdVu, 1);
		getViewLines2(stdVu, type);
		
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
		return -1;
	}
}


extern "C" __declspec(dllexport) void MyCommand(const char* params) {
	WriteMessage("传入参数=[%s]", params);//参数可忽略，输入~mycommand或者~mycommand(aaa)调用命令
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

extern "C" __declspec(dllexport) int RadialDimension(const char* jsonParams) {
	try
	{
		json params = json::parse(jsonParams);

		int lineId = params["id"].get<int>();

		szwPoint point = { params["point"].get<std::vector<int>>()[0], params["point"].get<std::vector<int>>()[1], 0};
		szwPoint textPoint = { params["text point"].get<std::vector<int>>()[0], params["text point"].get<std::vector<int>>()[1], 0 };

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

		szwEntityHandle out;
		err = ZwDrawingDimensionRadialCreate(data, nullptr, &out);

		if (err != ZW_API_NO_ERROR) {
			WriteMessage("err code = %i", static_cast<int>(err));
		}
		WriteMessage("[console] linear dimension created.");
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
		return -1;
	}
}

extern "C" __declspec(dllexport) int ArcLengthDimension(const char* jsonParams) {
	try
	{
		json params = json::parse(jsonParams);

		int lineId = params["arc id"].get<int>();

		szwPoint point = { params["arc point"].get<std::vector<int>>()[0], params["point"].get<std::vector<int>>()[1], 0 };
		szwPoint textPoint = { params["text point"].get<std::vector<int>>()[0], params["text point"].get<std::vector<int>>()[1], 0 };

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
		err = ZwDrawingDimensionArcCreate(data, nullptr, &out);

		if (err != ZW_API_NO_ERROR) {
			WriteMessage("err code = %i", static_cast<int>(err));
		}
		WriteMessage("[console] linear dimension created.");
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
		return -1;
	}
}

extern "C" __declspec(dllexport) int HoleCalloutDimension(const char* jsonParams) {
	try
	{
		json params = json::parse(jsonParams);

		int holeId = params["hole curve id"].get<int>();
		int vuId = params["view id"].get<int>();

		szwPoint2 textPoint = { params["text point"].get<std::vector<int>>()[0], params["text point"].get<std::vector<int>>()[1] };

		ezwErrors err;
		szwEntityHandle holeHdl,vuHdl;
		szwDrawingHoleCalloutData data;
		err = ZwDrawingDimensionHoleCalloutInit(&data);
		data.type = ZW_HOLE_CALLOUT_SHAPE_RADIAL;

		err = ZwApiIdtoHandle(vuId, &vuHdl);
		data.viewHandle = vuHdl;

		err = ZwApiIdtoHandle(holeId, &holeHdl);
		szwDrawingHoleCalloutHole hole{ holeHdl,&textPoint };
		data.holes = &hole;
		data.count = 1;

		int count_out = 0;
		szwEntityHandle* out;
		err = ZwDrawingDimensionHoleCalloutCreate(data, nullptr, &count_out, &out);
		ZwEntityHandleListFree(count_out, &out);

		if (err != ZW_API_NO_ERROR) {
			WriteMessage("err code = %i", static_cast<int>(err));
		}
		WriteMessage("[console] linear dimension created.");
		return static_cast<int>(err);
	}
	catch (const std::exception& e) {
		WriteMessage("JSON parse err: %s", e.what());
		return -1;
	}
}

extern "C" __declspec(dllexport) int Z3DemoInit() {
	ZwCommandFunctionLoad("mycommand", MyCommand, ZW_LICENSE_CODE_GENERAL);//注册命令

	ZwCommandFunctionLoad("FILEOPEN", fileOpen, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("FILEEXPORT", fileExport, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("FILESAVE", fileSaveOrClose, ZW_LICENSE_CODE_GENERAL);

	ZwCommandFunctionLoad("STDVUCREATE", standardViewCreate, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("STDVUDIM", standardViewDimension, ZW_LICENSE_CODE_GENERAL);

	ZwCommandFunctionLoad("LINDIM", linearDimension, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("LINOFFSETDIM", linearOffsetDimension, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("AUTODIM", autoDimension, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("RADIALDIM", RadialDimension, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("ARCLENDIM", ArcLengthDimension, ZW_LICENSE_CODE_GENERAL);
	ZwCommandFunctionLoad("HOLECALLOUTDIM", HoleCalloutDimension, ZW_LICENSE_CODE_GENERAL);
	return 0;
}

extern "C" __declspec(dllexport) int Z3DemoExit() {
	ZwCommandFunctionUnload("mycommand");//卸载命令
	return 0;
}