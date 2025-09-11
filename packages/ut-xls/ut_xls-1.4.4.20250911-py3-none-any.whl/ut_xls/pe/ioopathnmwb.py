from typing import Any, TypeAlias

import pyexcelerate as pe

from ut_path.pathnm import Pathnm
from ut_xls.pe.ioopathwb import IooPathWb as PeIooPathWb

TyWb: TypeAlias = pe.Workbook

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyPath = str
TyPathnm = str
TySheet = int | str

TnPath = None | TyPath
TnWb = None | TyWb


class IooPathnmWb:

    @staticmethod
    def write(
            wb: TnWb, pathnm: TyPathnm, kwargs: TyDic) -> None:
        if wb is None:
            return
        _path: TnPath = Pathnm.sh_path(pathnm, kwargs)
        if not _path:
            return
        wb.save(_path)

    @staticmethod
    def write_wb_from_doaoa(
            doaoa: TyDoAoA, pathnm: str, kwargs: TyDic) -> None:
        if not doaoa:
            return
        _path: TnPath = Pathnm.sh_path(pathnm, kwargs)
        PeIooPathWb.write_wb_from_doaoa(doaoa, _path, kwargs)

    @staticmethod
    def write_wb_from_doaod(
            doaod: TyDoAoD, pathnm: str, kwargs: TyDic) -> None:
        if not doaod:
            return
        _path: TnPath = Pathnm.sh_path(pathnm, kwargs)
        PeIooPathWb.write_wb_from_doaod(doaod, _path, kwargs)

    @staticmethod
    def write_wb_from_aod(
            aod: TyAoD, pathnm: str, sheet: TySheet, kwargs: TyDic) -> None:
        if not aod:
            return
        _path: TnPath = Pathnm.sh_path(pathnm, kwargs)
        PeIooPathWb.write_wb_from_aod(aod, _path, sheet)
