from typing import Any, TypeAlias

import openpyxl as op

from ut_path.pathnm import Pathnm
from ut_xls.op.ioipath import IoiPathWb as OpIoiPathWb

TyWb: TypeAlias = op.workbook.workbook.Workbook
TyWs: TypeAlias = op.worksheet.worksheet.Worksheet

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
TySheets = int | str | list[int | str]
TySheetname = str
TySheetnames = list[TySheetname]

TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDoAoD = None | TyDoAoD
TnSheet = None | TySheet
TnSheets = None | TySheets
TnSheetname = None | TySheetname
TnSheetnames = None | TySheetnames
TnWb = None | TyWb
TnWs = None | TyWs
TnPath = None | TyPath


class IoiPathnmWb:

    @staticmethod
    def load(pathnm: TyPathnm, **kwargs) -> TyWb:
        """
        Read Excel workbooks
        """
        _wb: TyWb = OpIoiPathWb.load(
               Pathnm.sh_path(pathnm, kwargs), **kwargs)
        return _wb

    @classmethod
    def read_wb_to_aod(
            cls, pathnm: TyPathnm, sheet: TnSheet, **kwargs) -> TyAoD:
        """
        Read Excel workbooks into Array of Dictionaries
        """
        _aod: TyAoD = OpIoiPathWb.read_wb_to_aod(
                Pathnm.sh_path(pathnm, kwargs), **kwargs)
        return _aod

    @classmethod
    def read_wb_to_doaod(
            cls, pathnm: TyPathnm, sheet: TnSheets, **kwargs) -> TyDoAoD:
        """
        Read Excel workbooks into Dictionary of Array of Dictionaries
        """
        _doaod: TyDoAoD = OpIoiPathWb.read_wb_to_doaod(
                Pathnm.sh_path(pathnm, kwargs), sheet, **kwargs)
        return _doaod

    @classmethod
    def read_wb_to_aod_or_doaod(
            cls, pathnm: TyPathnm, sheet: TnSheets, **kwargs
    ) -> TnAoD_DoAoD:
        """
        Read Excel workbooks into Array od Dictionaries or
        Dictionary of Array of Dictionaries
        """
        _aod_doaod: TnAoD_DoAoD = OpIoiPathWb.read_wb_to_aod_or_doaod(
               Pathnm.sh_path(pathnm, kwargs), sheet, **kwargs)
        return _aod_doaod

    @classmethod
    def read_wb_to_aoa(
            cls, pathnm: TyPathnm, **kwargs) -> TyTo2AoA:
        """
        Read Excel workbooks into Array of Arrays
        """
        _heads: TyAoA
        _aoa: TyAoA
        _heads, _aoa = OpIoiPathWb.read_wb_to_aoa(
                Pathnm.sh_path(pathnm, kwargs), **kwargs)
        return _heads, _aoa

    @classmethod
    def sh_wb_adm(
            cls, pathnm: TyPathnm, aod: TnAoD, sheet: TyStr, **kwargs
    ) -> TnWb:
        """
        Administration processsing for Excel workbooks
        """
        _wb: TnWb = OpIoiPathWb.sh_wb_adm(
               Pathnm.sh_path(pathnm, kwargs), aod, sheet)
        return _wb

    @classmethod
    def sh_wb_del(
            cls, pathnm: TyPathnm, aod: TnAoD, sheet: TyStr, **kwargs
    ) -> TnWb:
        """
        Delete processsing for Excel workbooks
        """
        _wb: TnWb = OpIoiPathWb.sh_wb_del(
               Pathnm.sh_path(pathnm, kwargs), aod, sheet)
        return _wb

    @classmethod
    def sh_wb_reg(
            cls, pathnm: TyPathnm,
            aod_adm: TnAoD, aod_del: TnAoD,
            sheet_adm: TyStr, sheet_del: TyStr, **kwargs
    ) -> TnWb:
        """
        Regular processsing for Excel workbooks
        """
        _wb: TnWb = OpIoiPathWb.sh_wb_reg(
                Pathnm.sh_path(pathnm, kwargs),
                aod_adm, aod_del, sheet_adm, sheet_del)
        return _wb
