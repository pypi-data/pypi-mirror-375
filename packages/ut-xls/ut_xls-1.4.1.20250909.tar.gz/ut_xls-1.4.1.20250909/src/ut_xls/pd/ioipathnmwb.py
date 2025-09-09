from typing import Any, TypeAlias

import pandas as pd

from ut_path.pathnm import Pathnm
from ut_xls.pd.ioipathwb import PdIoiPathWb

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoD = dict[Any, TyAoD]
TyDoPdDf = dict[str, TyPdDf] | dict[Any, TyPdDf]
# TyDoPlDf = dict[str, TyPlDf] | dict[Any, TyPlDf]
# TyDoWsOp = dict[Any, TyWsOp]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPdDf_DoPdDf = TyPdDf | dict[str, TyPdDf] | dict[Any, TyPdDf]
# TyPath = str
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
# TnWbOp = None | TyWbOp
# TnWsOp = None | TyWsOp
# TnPath = None | TyPath


class IoiPathnmWb:

    kwargs_wb = dict(dtype=str, keep_default_na=False, engine='calamine')

    @staticmethod
    def read_wb_to_aod(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnAoD:
        aod: TnAoD = PdIoiPathWb.read_wb_to_aod(
                Pathnm.sh_path(pathnm, kwargs), sheet, **kwargs)
        return aod

    @staticmethod
    def read_wb_to_doaod(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnDoAoD:
        doaod: TnDoAoD = PdIoiPathWb.read_wb_to_doaod(
                Pathnm.sh_path(pathnm, kwargs), **kwargs)
        return doaod

    @staticmethod
    def read_wb_to_aod_or_doaod(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnAoD_DoAoD:
        obj: TnAoD_DoAoD = PdIoiPathWb.read_wb_to_aod_or_doaod(
                Pathnm.sh_path(pathnm, kwargs), sheet, **kwargs)
        return obj

    @staticmethod
    def read_wb_to_df(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnPdDf:
        _pddf: TnPdDf = PdIoiPathWb.read_wb_to_df(
               Pathnm.sh_path(pathnm, kwargs), sheet, **kwargs)
        return _pddf

    @staticmethod
    def read_wb_to_dodf(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnDoPdDf:
        _dopddf: TnDoPdDf = PdIoiPathWb.read_wb_to_dodf(
                Pathnm.sh_path(pathnm, kwargs), sheet, **kwargs)
        return _dopddf

    @staticmethod
    def read_wb_to_df_or_dodf(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic) -> TnPdDf_DoPdDf:
        obj: TnPdDf_DoPdDf = PdIoiPathWb.read_wb_to_df_or_dodf(
               Pathnm.sh_path(pathnm, kwargs), sheet, **kwargs)
        return obj
