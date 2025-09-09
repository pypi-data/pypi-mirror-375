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

TnWb = None | TyWb


class IooPathnmWb:

    @staticmethod
    def write(
            wb: TnWb, pathnm: TyPathnm, **kwargs) -> None:
        _path: TyPath = Pathnm.sh_path(pathnm, kwargs)
        if wb is not None:
            wb.save(_path)

    @staticmethod
    def write_wb_from_doaoa(
            doaoa: TyDoAoA, pathnm: str, **kwargs) -> None:
        if not doaoa:
            return
        PeIooPathWb.write_wb_from_doaoa(
                doaoa, Pathnm.sh_path(pathnm, kwargs))

    @staticmethod
    def write_wb_from_doaod(
            doaod: TyDoAoD, pathnm: str, **kwargs) -> None:
        if not doaod:
            return
        PeIooPathWb.write_wb_from_doaod(
                doaod, Pathnm.sh_path(pathnm, kwargs))

    @staticmethod
    def write_wb_from_aod(
            aod: TyAoD, pathnm: str, sheet: TySheet, **kwargs) -> None:
        if not aod:
            return
        PeIooPathWb.write_wb_from_aod(
                aod, Pathnm.sh_path(pathnm, kwargs), sheet)
