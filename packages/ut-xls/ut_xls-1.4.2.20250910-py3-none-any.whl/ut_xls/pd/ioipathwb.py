from typing import Any, TextIO, BinaryIO
# from typing_extensions import TypeIs

import pandas as pd
from pathlib import Path

from ut_dic.dopddf import DoDf
from ut_dfr.pddf import Df
from ut_obj.io import Io

TyDf = pd.DataFrame
TyXls = pd.ExcelFile

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoDf = dict[str, TyDf] | dict[Any, TyDf]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyDf_DoDf = TyDf | TyDoDf
TyPdFileSrc = str | bytes | TyXls | Path | TextIO | BinaryIO
TySheet = int | str
TySheets = int | str | list[int | str]
TySheetname = str
TySheetnames = list[TySheetname]

TnArr = None | TyArr
TnAoA = None | TyAoA
TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDic = None | TyDic
TnDoAoA = None | TyDoAoA
TnDoAoD = None | TyDoAoD
# TnDoWsOp = None | TyDoWsOp
TnDf = None | TyDf
TnDf_DoDf = None | TyDf_DoDf
TnDoDf = None | TyDoDf
TnPdFileSrc = None | TyPdFileSrc
# TnDoPlDf = None | TyDoPlDf
TnSheet = None | TySheet
TnSheets = None | TySheets
TnSheetname = None | TySheetname
TnSheetnames = None | TySheetnames


class IoiPathWb:

    pd_ioi = dict(dtype=str, keep_default_na=False, engine='calamine')

    @classmethod
    def read_wb_to_aod(
            cls, io: TnPdFileSrc, sheet: TnSheet, kwargs: TyDic) -> TnAoD:
        if io is None:
            return None
        _obj: TnAoD_DoAoD = cls.read_wb_to_aod_or_doaod(io, sheet, kwargs)
        if not isinstance(_obj, TnAoD):
            raise Exception(f"Object: {_obj} should be of type TnAoD")
        return _obj

    @classmethod
    def read_wb_to_doaod(
            cls, io: TnPdFileSrc, sheet: TnSheet, kwargs: TyDic) -> TnDoAoD:
        if io is None:
            return None
        _obj: TnAoD_DoAoD = cls.read_wb_to_aod_or_doaod(io, sheet, kwargs)
        if not isinstance(_obj, TnDoAoD):
            raise Exception(f"Object: {_obj} should be of type TnDoAoD")
        return _obj

    @classmethod
    def read_wb_to_aod_or_doaod(
            cls, io: TnPdFileSrc, sheet: TnSheet, kwargs: TyDic) -> TnAoD_DoAoD:
        if io is None:
            return None
        _obj: TnDf_DoDf = cls.read_wb_to_df_or_dodf(io, sheet, kwargs)
        if isinstance(_obj, TnDoDf):
            _doaod: TyDoAoD = DoDf.to_doaod(_obj)
            return _doaod
        _aod: TnAoD = Df.to_aod(_obj)
        return _aod

    @classmethod
    def read_wb_to_df(
            cls, io: TnPdFileSrc, sheet: TnSheet, kwargs: TyDic) -> TnDf:
        if io is None:
            return None
        _obj: TnDf_DoDf = cls.read_wb_to_df_or_dodf(io, sheet, kwargs)
        if not isinstance(_obj, TnDf):
            raise Exception(f"Object: {_obj} should be of type TnDf")
        return _obj

    @classmethod
    def read_wb_to_dodf(
            cls, io: TnPdFileSrc, sheet: TnSheet, kwargs: TyDic) -> TnDoDf:
        if io is None:
            return None
        _obj = cls.read_wb_to_df_or_dodf(io, sheet, kwargs)
        if not isinstance(_obj, TnDoDf):
            raise Exception(f"Object: {_obj} should be of type TnDoPdD")
        return _obj

    @classmethod
    def read_wb_to_df_or_dodf(
            cls, io: TnPdFileSrc, sheet: TnSheet, kwargs: TyDic) -> TnDf_DoDf:
        if io is None:
            return None
        Io.verify(io)
        if not (sheet is None or isinstance(sheet, (int, str, list, tuple))):
            msg = f"sheet; {sheet} must be None or of type (int, str, list, tuple)"
            raise Exception(msg)
        _pd_ioi = kwargs.get('pd_ioi', cls.pd_ioi)
        obj: TnDf_DoDf = pd.read_excel(io, sheet_name=sheet, **_pd_ioi)
        if obj is None:
            return obj
        if sheet is None:
            msg = f"Excel Workbook {io!r} contains no sheets"
        else:
            msg = f"Sheets {sheet} are not contained in Excel Workbook {io!r}"
        raise Exception(msg)
