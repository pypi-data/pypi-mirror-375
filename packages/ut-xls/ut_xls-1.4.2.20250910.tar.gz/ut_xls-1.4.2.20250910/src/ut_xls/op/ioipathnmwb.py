from typing import Any

import openpyxl as op

from ut_path.pathnm import Pathnm
from ut_xls.op.ioipathwb import IoiPathWb as OpIoiPathWb

TyWb = op.workbook.workbook.Workbook
TyWs = op.worksheet.worksheet.Worksheet

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoD = dict[Any, TyAoD]
TyDoWs = dict[Any, TyWs]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPath = str
TyPathnm = str
TyStr = str
TyTo2AoA = tuple[TyAoA, TyAoA]

TySheet = int | str
TySheets = TySheet | list[int | str]

TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDoAoD = None | TyDoAoD
TnSheet = None | TySheet
TnSheets = None | TySheets
TnWb = None | TyWb
TnWs = None | TyWs
TnPath = None | TyPath


class IoiPathnmWb:

    @staticmethod
    def load(pathnm: TyPathnm, kwargs: TyDic) -> TyWb:
        """
        Read Excel workbooks
        """
        _path = Pathnm.sh_path(pathnm, kwargs)
        _wb: TyWb = OpIoiPathWb.load(_path, kwargs)
        return _wb

    @classmethod
    def read_wb_to_aod(
            cls, pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TyAoD:
        """
        Read Excel workbooks into Array of Dictionaries
        """
        _path = Pathnm.sh_path(pathnm, kwargs)
        _obj: TyAoD = OpIoiPathWb.read_wb_to_aod(_path, sheet, kwargs)
        return _obj

    @classmethod
    def read_wb_to_doaod(
            cls, pathnm: TyPathnm, sheets: TnSheets, kwargs: TyDic) -> TyDoAoD:
        """
        Read Excel workbooks into Dictionary of Array of Dictionaries
        """
        _path = Pathnm.sh_path(pathnm, kwargs)
        _obj: TyDoAoD = OpIoiPathWb.read_wb_to_doaod(_path, sheets, kwargs)
        return _obj

    @classmethod
    def read_wb_to_aod_or_doaod(
            cls, pathnm: TyPathnm, sheets: TnSheets, kwargs: TyDic
    ) -> TnAoD_DoAoD:
        """
        Read Excel workbooks into Array od Dictionaries or
        Dictionary of Array of Dictionaries
        """
        _path = Pathnm.sh_path(pathnm, kwargs)
        _obj: TnAoD_DoAoD = OpIoiPathWb.read_wb_to_aod_or_doaod(_path, sheets, kwargs)
        return _obj

    @classmethod
    def read_wb_to_aoa(
            cls, pathnm: TyPathnm, kwargs: TyDic) -> TyTo2AoA:
        """
        Read Excel workbooks into Array of Arrays
        """
        _heads: TyAoA
        _aoa: TyAoA
        _path = Pathnm.sh_path(pathnm, kwargs)
        _heads, _aoa = OpIoiPathWb.read_wb_to_aoa(_path, kwargs)
        return _heads, _aoa

    @classmethod
    def sh_wb_adm(
            cls, pathnm: TyPathnm, aod: TnAoD, sheet: TySheet, kwargs: TyDic
    ) -> TnWb:
        """
        Administration processsing for Excel workbooks
        """
        _path = Pathnm.sh_path(pathnm, kwargs)
        _wb: TnWb = OpIoiPathWb.sh_wb_adm(_path, aod, sheet, kwargs)
        return _wb

    @classmethod
    def sh_wb_del(
            cls, pathnm: TyPathnm, aod: TnAoD, sheet: TySheet, kwargs: TyDic
    ) -> TnWb:
        """
        Delete processsing for Excel workbooks
        """
        _path = Pathnm.sh_path(pathnm, kwargs)
        _wb: TnWb = OpIoiPathWb.sh_wb_del(_path, aod, sheet, kwargs)
        return _wb

    @classmethod
    def sh_wb_reg(
            cls, pathnm: TyPathnm,
            aod_adm: TnAoD, aod_del: TnAoD,
            sheet_adm: TySheet, sheet_del: TySheet, kwargs: TyDic
    ) -> TnWb:
        """
        Regular processsing for Excel workbooks
        """
        _path = Pathnm.sh_path(pathnm, kwargs)
        _wb: TnWb = OpIoiPathWb.sh_wb_reg(
                _path, aod_adm, aod_del, sheet_adm, sheet_del, kwargs)
        return _wb
