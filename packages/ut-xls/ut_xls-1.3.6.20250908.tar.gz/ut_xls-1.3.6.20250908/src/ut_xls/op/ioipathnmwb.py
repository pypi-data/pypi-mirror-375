from typing import Any, TypeAlias

import openpyxl as op

from ut_path.pathnm import PathNm
from ut_xls.op.ioipath import IoiPathWb

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
        _path = PathNm.sh_path(pathnm, kwargs)
        _wb: TyWb = IoiPathWb.load(_path, **kwargs)
        return _wb

    @classmethod
    def read_wb_to_aod(
            cls, pathnm: TyPathnm, sheet: TnSheet, **kwargs) -> TyAoD:
        _io = PathNm.sh_path(pathnm, kwargs)
        _aod: TyAoD = IoiPathWb.read_wb_to_aod(_io, **kwargs)
        return _aod

    @classmethod
    def read_wb_to_doaod(
            cls, pathnm: TyPathnm, sheet: TnSheets, **kwargs) -> TyDoAoD:
        _io = PathNm.sh_path(pathnm, kwargs)
        _doaod: TyDoAoD = IoiPathWb.read_wb_to_doaod(_io, sheet, **kwargs)
        return _doaod

    @classmethod
    def read_wb_to_aod_or_doaod(
            cls, pathnm: TyPathnm, sheet: TnSheets, **kwargs) -> TnAoD_DoAoD:
        _io = PathNm.sh_path(pathnm, kwargs)
        _aod_doaod: TnAoD_DoAoD = IoiPathWb.read_wb_to_aod_or_doaod(
                _io, sheet, **kwargs)
        return _aod_doaod

    @classmethod
    def read_wb_to_aoa(
            cls, pathnm: TyPathnm, **kwargs) -> tuple[TyAoA, TyAoA]:
        _io = PathNm.sh_path(pathnm, kwargs)
        _heads: TyAoA
        _aoa: TyAoA
        _heads, _aoa = IoiPathWb.read_wb_to_aoa(_io, **kwargs)
        return _heads, _aoa
