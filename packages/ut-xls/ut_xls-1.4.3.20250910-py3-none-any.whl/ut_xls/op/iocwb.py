from typing import Any

import openpyxl as op

TyWb = op.workbook.workbook.Workbook


class IocWb:

    @staticmethod
    def get(**kwargs: Any) -> TyWb:
        wb: TyWb = op.Workbook(**kwargs)
        return wb
