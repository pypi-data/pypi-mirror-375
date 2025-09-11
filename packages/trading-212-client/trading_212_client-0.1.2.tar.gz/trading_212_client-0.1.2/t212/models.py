from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, RootModel, ConfigDict


class AccountResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    currency_code: str = Field(..., alias="currencyCode", description="ISO 4217", max_length=3, min_length=3)
    id: int


class DividendCashAction(str, Enum):
    REINVEST = "REINVEST"
    TO_ACCOUNT_CASH = "TO_ACCOUNT_CASH"


class AccountBucketDetailedResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    creation_date: datetime = Field(alias="creationDate")
    dividend_cash_action: DividendCashAction = Field(alias="dividendCashAction")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    goal: Optional[float] = None
    icon: Optional[str] = None
    id: int
    initial_investment: Optional[float] = Field(None, alias="initialInvestment")
    instrument_shares: Optional[Dict[str, float]] = Field(None, alias="instrumentShares")
    name: Optional[str] = None
    public_url: Optional[str] = Field(None, alias="publicUrl")


class InstrumentIssueName(str, Enum):
    DELISTED = "DELISTED"
    SUSPENDED = "SUSPENDED"
    NO_LONGER_TRADABLE = "NO_LONGER_TRADABLE"
    MAX_POSITION_SIZE_REACHED = "MAX_POSITION_SIZE_REACHED"
    APPROACHING_MAX_POSITION_SIZE = "APPROACHING_MAX_POSITION_SIZE"
    COMPLEX_INSTRUMENT_APP_TEST_REQUIRED = "COMPLEX_INSTRUMENT_APP_TEST_REQUIRED"
    PRICE_TOO_LOW = "PRICE_TOO_LOW"


class InstrumentIssueSeverity(str, Enum):
    IRREVERSIBLE = "IRREVERSIBLE"
    REVERSIBLE = "REVERSIBLE"
    INFORMATIVE = "INFORMATIVE"


class InstrumentIssue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: InstrumentIssueName
    severity: InstrumentIssueSeverity


class InvestmentResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    price_avg_invested_value: Optional[float] = Field(None, alias="priceAvgInvestedValue")
    price_avg_result: Optional[float] = Field(None, alias="priceAvgResult")
    price_avg_result_coef: Optional[float] = Field(None, alias="priceAvgResultCoef")
    price_avg_value: Optional[float] = Field(None, alias="priceAvgValue")


class AccountBucketInstrumentResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    current_share: Optional[float] = Field(None, alias="currentShare")
    expected_share: Optional[float] = Field(None, alias="expectedShare")
    issues: Optional[List[InstrumentIssue]] = None
    owned_quantity: Optional[float] = Field(None, alias="ownedQuantity")
    result: Optional[InvestmentResult] = None
    ticker: Optional[str] = None


class AccountBucketInstrumentsDetailedResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    instruments: Optional[List[AccountBucketInstrumentResult]] = None
    settings: Optional[AccountBucketDetailedResponse] = None


class DividendDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    gained: Optional[float] = None
    in_cash: Optional[float] = Field(None, alias="inCash")
    reinvested: Optional[float] = None


class AccountBucketResultResponseStatus(str, Enum):
    AHEAD = "AHEAD"
    ON_TRACK = "ON_TRACK"
    BEHIND = "BEHIND"


class AccountBucketResultResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cash: Optional[float] = Field(
        None, description="Amount of money put into the pie in account currency"
    )
    dividend_details: Optional[DividendDetails] = Field(None, alias="dividendDetails")
    id: int
    progress: Optional[float] = Field(
        None, description="Progress of the pie based on the set goal", example=0.5
    )
    result: Optional[InvestmentResult] = None
    status: Optional[AccountBucketResultResponseStatus] = Field(
        None, description="Status of the pie based on the set goal"
    )


class CashResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    blocked: Optional[float] = None
    free: Optional[float] = None
    invested: Optional[float] = None
    pie_cash: Optional[float] = Field(None, alias="pieCash", description="Invested cash in pies")
    ppl: Optional[float] = None
    result: Optional[float] = None
    total: Optional[float] = None


class DuplicateBucketRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    icon: Optional[str] = None
    name: Optional[str] = None


class EnqueuedReportResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    report_id: int = Field(alias="reportId")


class TimeEventType(str, Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    BREAK_START = "BREAK_START"
    BREAK_END = "BREAK_END"
    PRE_MARKET_OPEN = "PRE_MARKET_OPEN"
    AFTER_HOURS_OPEN = "AFTER_HOURS_OPEN"
    AFTER_HOURS_CLOSE = "AFTER_HOURS_CLOSE"
    OVERNIGHT_OPEN = "OVERNIGHT_OPEN"


class TimeEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date: datetime
    type: TimeEventType


class WorkingSchedule(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    time_events: Optional[List[TimeEvent]] = Field(None, alias="timeEvents")


class Exchange(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: Optional[str] = None
    working_schedules: Optional[List[WorkingSchedule]] = Field(None, alias="workingSchedules")


class HistoricalOrderExecutor(str, Enum):
    API = "API"
    IOS = "IOS"
    ANDROID = "ANDROID"
    WEB = "WEB"
    SYSTEM = "SYSTEM"
    AUTOINVEST = "AUTOINVEST"


class HistoricalOrderFillType(str, Enum):
    TOTV = "TOTV"
    OTC = "OTC"
    STOCK_SPLIT = "STOCK_SPLIT"
    STOCK_DISTRIBUTION = "STOCK_DISTRIBUTION"
    FOP = "FOP"
    FOP_CORRECTION = "FOP_CORRECTION"
    CUSTOM_STOCK_DISTRIBUTION = "CUSTOM_STOCK_DISTRIBUTION"
    EQUITY_RIGHTS = "EQUITY_RIGHTS"


class HistoricalOrderStatus(str, Enum):
    LOCAL = "LOCAL"
    UNCONFIRMED = "UNCONFIRMED"
    CONFIRMED = "CONFIRMED"
    NEW = "NEW"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    REPLACING = "REPLACING"
    REPLACED = "REPLACED"


class HistoricalOrderTimeValidity(str, Enum):
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"


class HistoricalOrderType(str, Enum):
    LIMIT = "LIMIT"
    STOP = "STOP"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP_LIMIT"


class TaxName(str, Enum):
    COMMISSION_TURNOVER = "COMMISSION_TURNOVER"
    CURRENCY_CONVERSION_FEE = "CURRENCY_CONVERSION_FEE"
    FINRA_FEE = "FINRA_FEE"
    FRENCH_TRANSACTION_TAX = "FRENCH_TRANSACTION_TAX"
    PTM_LEVY = "PTM_LEVY"
    STAMP_DUTY = "STAMP_DUTY"
    STAMP_DUTY_RESERVE_TAX = "STAMP_DUTY_RESERVE_TAX"
    TRANSACTION_FEE = "TRANSACTION_FEE"


class Tax(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    fill_id: Optional[str] = Field(None, alias="fillId")
    name: Optional[TaxName] = None
    quantity: Optional[float] = None
    time_charged: Optional[datetime] = Field(None, alias="timeCharged")


class HistoricalOrder(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date_created: Optional[datetime] = Field(None, alias="dateCreated")
    date_executed: Optional[datetime] = Field(None, alias="dateExecuted")
    date_modified: Optional[datetime] = Field(None, alias="dateModified")
    executor: Optional[HistoricalOrderExecutor] = None
    fill_cost: Optional[float] = Field(None, alias="fillCost", description="In the instrument currency")
    fill_id: Optional[int] = Field(None, alias="fillId")
    fill_price: Optional[float] = Field(None, alias="fillPrice", description="In the instrument currency")
    fill_result: Optional[float] = Field(None, alias="fillResult")
    fill_type: Optional[HistoricalOrderFillType] = Field(None, alias="fillType")
    filled_quantity: Optional[float] = Field(
        None, alias="filledQuantity", description="Applicable to quantity orders"
    )
    filled_value: Optional[float] = Field(None, alias="filledValue", description="Applicable to value orders")
    id: int
    limit_price: Optional[float] = Field(None, alias="limitPrice", description="Applicable to limit orders")
    ordered_quantity: Optional[float] = Field(
        None, alias="orderedQuantity", description="Applicable to quantity orders"
    )
    ordered_value: Optional[float] = Field(
        None, alias="orderedValue", description="Applicable to value orders"
    )
    parent_order: Optional[int] = Field(None, alias="parentOrder")
    status: Optional[HistoricalOrderStatus] = None
    stop_price: Optional[float] = Field(None, alias="stopPrice", description="Applicable to stop orders")
    taxes: Optional[List[Tax]] = None
    ticker: Optional[str] = None
    time_validity: Optional[HistoricalOrderTimeValidity] = Field(
        None, alias="timeValidity", description="Applicable to stop, limit and stopLimit orders"
    )
    type: Optional[HistoricalOrderType] = None


class HistoryDividendItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    amount: Optional[float] = Field(None, description="In account currency")
    amount_in_euro: Optional[float] = Field(None, alias="amountInEuro")
    gross_amount_per_share: Optional[float] = Field(
        None, alias="grossAmountPerShare", description="In instrument currency"
    )
    paid_on: Optional[datetime] = Field(None, alias="paidOn")
    quantity: Optional[float] = None
    reference: Optional[str] = None
    ticker: Optional[str] = None
    type: Optional[str] = None


class HistoryTransactionItemType(str, Enum):
    WITHDRAW = "WITHDRAW"
    DEPOSIT = "DEPOSIT"
    FEE = "FEE"
    TRANSFER = "TRANSFER"


class HistoryTransactionItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    amount: Optional[float] = Field(None, description="In the account currency")
    date_time: Optional[datetime] = Field(None, alias="dateTime")
    reference: Optional[str] = Field(None, description="ID")
    type: Optional[HistoryTransactionItemType] = None


class LimitRequestTimeValidity(str, Enum):
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"


class LimitRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    limit_price: float = Field(..., alias="limitPrice", example=100.23)
    quantity: float = Field(..., example=0.1)
    ticker: str = Field(..., example="AAPL_US_EQ")
    time_validity: LimitRequestTimeValidity = Field(
        ..., alias="timeValidity", description="Expiration", example="DAY"
    )


class MarketRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    quantity: float = Field(..., example=0.1)
    ticker: str = Field(..., example="AAPL_US_EQ")


class OrderStatus(str, Enum):
    LOCAL = "LOCAL"
    UNCONFIRMED = "UNCONFIRMED"
    CONFIRMED = "CONFIRMED"
    NEW = "NEW"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    REPLACING = "REPLACING"
    REPLACED = "REPLACED"


class OrderStrategy(str, Enum):
    QUANTITY = "QUANTITY"
    VALUE = "VALUE"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    STOP = "STOP"
    MARKET = "MARKET"
    STOP_LIMIT = "STOP_LIMIT"


class Order(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    creation_time: Optional[datetime] = Field(None, alias="creationTime")
    filled_quantity: Optional[float] = Field(
        None, alias="filledQuantity", description="Applicable to quantity orders"
    )
    filled_value: Optional[float] = Field(None, alias="filledValue", description="Applicable to value orders")
    id: int
    limit_price: Optional[float] = Field(
        None, alias="limitPrice", description="Applicable to LIMIT and STOP_LIMIT orders"
    )
    quantity: Optional[float] = Field(None, description="Applicable to quantity orders")
    status: Optional[OrderStatus] = None
    stop_price: Optional[float] = Field(
        None, alias="stopPrice", description="Applicable to STOP and STOP_LIMIT orders"
    )
    strategy: Optional[OrderStrategy] = None
    ticker: Optional[str] = Field(
        None,
        description="Unique instrument identifier. Get from the /instruments endpoint",
        example="AAPL_US_EQ",
    )
    type: Optional[OrderType] = None
    value: Optional[float] = Field(None, description="Applicable to value orders")


class PieRequestDividendCashAction(str, Enum):
    REINVEST = "REINVEST"
    TO_ACCOUNT_CASH = "TO_ACCOUNT_CASH"


class PieRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dividend_cash_action: Optional[PieRequestDividendCashAction] = Field(None, alias="dividendCashAction")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    goal: Optional[float] = Field(
        None, description="Total desired value of the pie in account currency"
    )
    icon: Optional[str] = None
    instrument_shares: Optional[Dict[str, float]] = Field(
        None, alias="instrumentShares", example={"AAPL_US_EQ": 0.5, "MSFT_US_EQ": 0.5}
    )
    name: Optional[str] = None


class PlaceOrderErrorCode(str, Enum):
    SellingEquityNotOwned = "SellingEquityNotOwned"
    CantLegalyTradeException = "CantLegalyTradeException"
    InsufficientResources = "InsufficientResources"
    InsufficientValueForStocksSell = "InsufficientValueForStocksSell"
    TargetPriceTooFar = "TargetPriceTooFar"
    TargetPriceTooClose = "TargetPriceTooClose"
    NotEligibleForISA = "NotEligibleForISA"
    ShareLendingAgreementNotAccepted = "ShareLendingAgreementNotAccepted"
    InstrumentNotFound = "InstrumentNotFound"
    MaxEquityBuyQuantityExceeded = "MaxEquityBuyQuantityExceeded"
    MaxEquitySellQuantityExceeded = "MaxEquitySellQuantityExceeded"
    LimitPriceMissing = "LimitPriceMissing"
    StopPriceMissing = "StopPriceMissing"
    TickerMissing = "TickerMissing"
    QuantityMissing = "QuantityMissing"
    MaxQuantityExceeded = "MaxQuantityExceeded"
    InvalidValue = "InvalidValue"
    InsufficientFreeForStocksException = "InsufficientFreeForStocksException"
    MinValueExceeded = "MinValueExceeded"
    MinQuantityExceeded = "MinQuantityExceeded"
    PriceTooFar = "PriceTooFar"
    UNDEFINED = "UNDEFINED"
    NotAvailableForRealMoneyAccounts = "NotAvailableForRealMoneyAccounts"


class PlaceOrderError(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    clarification: Optional[str] = None
    code: Optional[PlaceOrderErrorCode] = None


class PositionFrontend(str, Enum):
    API = "API"
    IOS = "IOS"
    ANDROID = "ANDROID"
    WEB = "WEB"
    SYSTEM = "SYSTEM"
    AUTOINVEST = "AUTOINVEST"


class Position(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    average_price: Optional[float] = Field(None, alias="averagePrice")
    current_price: Optional[float] = Field(None, alias="currentPrice")
    frontend: Optional[PositionFrontend] = Field(None, description="Origin")
    fx_ppl: Optional[float] = Field(
        None,
        alias="fxPpl",
        description="Forex movement impact, only applies to positions with instrument currency that differs from the accounts'",
    )
    initial_fill_date: Optional[datetime] = Field(None, alias="initialFillDate")
    max_buy: Optional[float] = Field(
        None, alias="maxBuy", description="Additional quantity that can be bought"
    )
    max_sell: Optional[float] = Field(None, alias="maxSell", description="Quantity that can be sold")
    pie_quantity: Optional[float] = Field(None, alias="pieQuantity", description="Invested in pies")
    ppl: Optional[float] = None
    quantity: Optional[float] = None
    ticker: Optional[str] = Field(
        None, description="Unique instrument identifier", example="AAPL_US_EQ"
    )


class PositionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ticker: Optional[str] = None


class ReportDataIncluded(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    include_dividends: Optional[bool] = Field(None, alias="includeDividends")
    include_interest: Optional[bool] = Field(None, alias="includeInterest")
    include_orders: Optional[bool] = Field(None, alias="includeOrders")
    include_transactions: Optional[bool] = Field(None, alias="includeTransactions")


class PublicReportRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data_included: Optional[ReportDataIncluded] = Field(None, alias="dataIncluded")
    time_from: Optional[datetime] = Field(None, alias="timeFrom")
    time_to: Optional[datetime] = Field(None, alias="timeTo")


class ReportResponseStatus(str, Enum):
    Queued = "Queued"
    Processing = "Processing"
    Running = "Running"
    Canceled = "Canceled"
    Failed = "Failed"
    Finished = "Finished"


class ReportResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data_included: Optional[ReportDataIncluded] = Field(None, alias="dataIncluded")
    download_link: Optional[str] = Field(None, alias="downloadLink")
    report_id: int = Field(alias="reportId")
    status: Optional[ReportResponseStatus] = None
    time_from: Optional[datetime] = Field(None, alias="timeFrom")
    time_to: Optional[datetime] = Field(None, alias="timeTo")


class StopLimitRequestTimeValidity(str, Enum):
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"


class StopLimitRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    limit_price: float = Field(..., alias="limitPrice", example=100.23)
    quantity: float = Field(..., example=0.1)
    stop_price: float = Field(..., alias="stopPrice", example=100.23)
    ticker: str = Field(..., example="AAPL_US_EQ")
    time_validity: StopLimitRequestTimeValidity = Field(
        ..., alias="timeValidity", description="Expiration", example="DAY"
    )


class StopRequestTimeValidity(str, Enum):
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"


class StopRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    quantity: float = Field(..., example=0.1)
    stop_price: float = Field(..., alias="stopPrice", example=100.23)
    ticker: str = Field(..., example="AAPL_US_EQ")
    time_validity: StopRequestTimeValidity = Field(
        ..., alias="timeValidity", description="Expiration", example="DAY"
    )


class TradeableInstrumentType(str, Enum):
    CRYPTOCURRENCY = "CRYPTOCURRENCY"
    ETF = "ETF"
    FOREX = "FOREX"
    FUTURES = "FUTURES"
    INDEX = "INDEX"
    STOCK = "STOCK"
    WARRANT = "WARRANT"
    CRYPTO = "CRYPTO"
    CVR = "CVR"
    CORPACT = "CORPACT"


class TradeableInstrument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    added_on: Optional[datetime] = Field(None, alias="addedOn", description="On the platform since")
    currency_code: str = Field(
        ..., alias="currencyCode", description="ISO 4217", max_length=3, min_length=3, example="USD"
    )
    isin: Optional[str] = None
    max_open_quantity: Optional[float] = Field(None, alias="maxOpenQuantity")
    name: Optional[str] = None
    short_name: Optional[str] = Field(None, alias="shortName")
    ticker: str = Field(..., description="Unique identifier", example="AAPL_US_EQ")
    type: TradeableInstrumentType = Field(..., example="ETF")
    working_schedule_id: Optional[int] = Field(
        None, alias="workingScheduleId", description="Get items in the /exchanges endpoint"
    )


class InstrumentListResponse(RootModel[list[TradeableInstrument]]):
    pass


class FetchAllPiesResponse(RootModel[list[AccountBucketResultResponse]]):
    pass


class ExchangeResponse(RootModel[list[Exchange]]):
    pass


class FetchAPieResponse(RootModel[list[AccountBucketInstrumentsDetailedResponse]]):
    pass


class FetchAllEquityOrdersResponse(RootModel[list[Order]]):
    pass


class PositionResponse(RootModel[list[Position]]):
    pass


class PaginatedResponseHistoricalOrderResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: Optional[List[HistoricalOrder]] = None
    next_page_path: Optional[str] = Field(None, alias="nextPagePath")


class PaginatedResponseHistoryDividendItemResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: Optional[List[HistoryDividendItem]] = None
    next_page_path: Optional[str] = Field(None, alias="nextPagePath")


class PaginatedResponseHistoryTransactionItemResponse(BaseModel):
    items: Optional[List[HistoryTransactionItem]] = None
    next_page_path: Optional[str] = Field(None, alias="nextPagePath")
