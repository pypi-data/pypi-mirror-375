"""AKShare Income Statement Model."""

# pylint: disable=unused-argument
import pandas as pd
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, model_validator


class AKShareIncomeStatementQueryParams(IncomeStatementQueryParams):
    """AKShare Income Statement Query.

    Source: https://financialmodelingprep.com/developer/docs/#Income-Statement
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter"],
        }
    }

    period: Literal["annual", "quarter"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    limit: Optional[int] = Field(
        default=5,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The quote is cached for one hour.",
    )


class AKShareIncomeStatementData(IncomeStatementData):
    """AKShare Income Statement Data."""

    __alias_dict__ = {
        "period_ending": "REPORT_DATE",
        "fiscal_period": "REPORT_TYPE",
        "reported_currency": "CURRENCY",
        "总营收": "TOTAL_OPERATE_INCOME",
        "净利润": "PARENT_NETPROFIT"
    }

    reported_currency: Optional[str] = Field(
        default=None,
        description="The currency in which the balance sheet was reported.",
    )
    总营收: Optional[float] = Field(
        default=None,
        description="Total pre-tax income.",
    )
    净利润: Optional[float] = Field(
        default=None,
        description="Income tax expense.",
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):  # pylint: disable=no-self-argument
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class AKShareIncomeStatementFetcher(
    Fetcher[
        AKShareIncomeStatementQueryParams,
        List[AKShareIncomeStatementData],
    ]
):
    """Transform the query, extract and transform the data from the AKShare endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> AKShareIncomeStatementQueryParams:
        """Transform the query params."""
        return AKShareIncomeStatementQueryParams(**params)

    @staticmethod
    async def extract_data(
        query: AKShareIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the AKShare endpoint."""

        em_df = get_data(query.symbol, query.period, query.use_cache)

        if query.limit is None:
            return em_df.to_dict(orient="records")
        else:
            return em_df.head(query.limit).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: AKShareIncomeStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[AKShareIncomeStatementData]:
        """Return the transformed data."""
        for result in data:
            result.pop("symbol", None)
            result.pop("cik", None)
        return [AKShareIncomeStatementData.model_validate(d) for d in data]

def get_data(symbol: str, period: str = "annual", use_cache: bool = True) -> pd.DataFrame:
    from openbb_akshare import project_name
    from mysharelib.blob_cache import BlobCache
    cache = BlobCache(table_name="income_statement", project=project_name)
    return cache.load_cached_data(symbol, period, use_cache, get_income_statement)

def get_income_statement(symbol: str, period: str = "annual", api_key : Optional[str] = "") -> pd.DataFrame:
    import akshare as ak
    from openbb_akshare.utils.helpers import normalize_symbol
    symbol_b, symbol_f, market = normalize_symbol(symbol)
    symbol_em = f"{market}{symbol_b}"

    if period == "annual":
        return ak.stock_profit_sheet_by_yearly_em(symbol=symbol_em)
    elif period == "quarter":
        return ak.stock_profit_sheet_by_report_em(symbol=symbol_em)
    else:
        raise ValueError("Invalid period. Please use 'annual' or 'quarter'.")