from typing import Any, TypeAlias

import pandas as pd

from ut_path.pathnm import Pathnm
from ut_xls.pd.ioipathwb import IoiPathWb as PdIoiPathWb

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoD = dict[Any, TyAoD]
TyDoPdDf = dict[str, TyPdDf] | dict[Any, TyPdDf]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPdDf_DoPdDf = TyPdDf | dict[str, TyPdDf] | dict[Any, TyPdDf]
TyPathnm = str

TySheet = int | str
TySheets = int | str | list[int | str]
TySheetname = str
TySheetnames = list[TySheetname]

TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDoAoD = None | TyDoAoD
TnPdDf = None | TyPdDf
TnPdDf_DoPdDf = None | TyPdDf_DoPdDf
TnDoPdDf = None | TyDoPdDf
TnSheet = None | TySheet
TnSheets = None | TySheets
TnSheetname = None | TySheetname
TnSheetnames = None | TySheetnames


class IoiPathnmWb:

    @staticmethod
    def read_wb_to_aod(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnAoD:
        _path = Pathnm.sh_path(pathnm, kwargs)
        _aod: TnAoD = PdIoiPathWb.read_wb_to_aod(
                _path, sheet, kwargs)
        return _aod

    @staticmethod
    def read_wb_to_doaod(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnDoAoD:
        _path = Pathnm.sh_path(pathnm, kwargs)
        _doaod: TnDoAoD = PdIoiPathWb.read_wb_to_doaod(
                _path, sheet, kwargs)
        return _doaod

    @staticmethod
    def read_wb_to_aod_or_doaod(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnAoD_DoAoD:
        _path = Pathnm.sh_path(pathnm, kwargs)
        _obj: TnAoD_DoAoD = PdIoiPathWb.read_wb_to_aod_or_doaod(
                _path, sheet, kwargs)
        return _obj

    @staticmethod
    def read_wb_to_df(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnPdDf:
        _path = Pathnm.sh_path(pathnm, kwargs)
        _pddf: TnPdDf = PdIoiPathWb.read_wb_to_df(
                _path, sheet, kwargs)
        return _pddf

    @staticmethod
    def read_wb_to_dodf(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnDoPdDf:
        _path = Pathnm.sh_path(pathnm, kwargs)
        _dopddf: TnDoPdDf = PdIoiPathWb.read_wb_to_dodf(
                _path, sheet, kwargs)
        return _dopddf

    @staticmethod
    def read_wb_to_df_or_dodf(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnPdDf_DoPdDf:
        _path = Pathnm.sh_path(pathnm, kwargs)
        _obj: TnPdDf_DoPdDf = PdIoiPathWb.read_wb_to_df_or_dodf(
                _path, sheet, kwargs)
        return _obj
