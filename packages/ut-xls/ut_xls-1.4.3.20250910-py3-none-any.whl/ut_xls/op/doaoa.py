from typing import Any

import openpyxl as op
import pandas as pd

from ut_xls.op.iocwb import IocWb
from ut_xls.op.ws import Ws

TyCe = op.cell.cell.Cell
TyWb = op.workbook.workbook.Workbook
TyWs = op.worksheet.worksheet.Worksheet
TyCs = op.chartsheet.chartsheet.Chartsheet
TyWsCs = TyWs | TyCs

TyPdDf = pd.DataFrame

TyArr = list[Any]
TyAoA = list[TyArr]
TyAoAoA = list[TyAoA]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyAoS = list[str]
TyAoWs = list[TyWs]
TyDoD = dict[Any, TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoWs = dict[Any, TyWs]
TyDoPdDf = dict[Any, TyPdDf]
TyAoD_DoAoD = TyAoD | TyDoAoD
TySheet = int | str
TySheets = TySheet | list[int | str]
TySheetNm = str
TySheetNms = list[TySheetNm]
TyStrArr = str | TyArr
TyToCe = tuple[TyCe, ...]

TnArr = None | TyArr
TnAoA = None | TyAoA
TnAoD = None | TyAoD
TnDic = None | TyDic
TnDoAoA = None | TyDoAoA
TnAoD_DoAoD = None | TyAoD_DoAoD
TnAoWs = None | TyAoWs
TnDoWs = None | TyDoWs
TnSheet = None | TySheet
TnSheets = None | TySheets
TnSheetNm = None | TySheetNm
TnWb = None | TyWb
TnWs = None | TyWs
TnCs = None | TyCs
TnWsCs = None | TyCs


class DoAoA:

    @staticmethod
    def create_wb(doaoa: TnDoAoA) -> TyWb:
        # def create_wb_with_doaoa(doaoa: TnDoAoA) -> TyWb:
        wb: TyWb = IocWb.get(write_only=True)
        if not doaoa:
            ws: TnWsCs = wb.active
            if ws is not None:
                wb.remove(ws)
            return wb
        for ws_id, aoa in doaoa.items():
            _ws: TnWs = wb.create_sheet()
            if _ws is None:
                continue
            _ws.title = ws_id
            Ws.append_rows(_ws, aoa)
        return wb
