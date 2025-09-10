"""Layout icon enumeration."""

from enum import Enum


class Icons(Enum):
    """Layout icon enumeration.

    Available icons for use in dashboard layouts and components.
    Each icon is represented by a string value.

    Attributes:
        NOT_FOUND_404 (str): 404 error icon
        ACCRETE (str): Accrete icon
        ARROW_DOWN (str): Down arrow icon
        ARROW_LEFT (str): Left arrow icon
        ARROW_LONG_DOWN (str): Long down arrow icon
        ARROW_LONG_LEFT (str): Long left arrow icon
        ARROW_LONG_RIGHT (str): Long right arrow icon
        ARROW_LONG_UP (str): Long up arrow icon
        ARROW_RIGHT (str): Right arrow icon
        BARS (str): Bars/menu icon
        BETWEEN (str): Between operator icon
        CHECK_SMALL (str): Small check icon
        CHECK (str): Check/checkmark icon
        CLOCK (str): Clock/time icon
        CLONE (str): Clone/duplicate icon
        CLOSE (str): Close icon
        CLOSE_SMALL (str): Small close icon
        COLLAPSE (str): Collapse icon
        COLUMN (str): Column layout icon
        CROSS_ASSET (str): Cross asset icon
        D3 (str): D3 visualization icon
        DASHBOARD_LINK (str): Dashboard link icon
        DEFAULT_TABLE_ICON (str): Default table icon
        DOUBLE_ARROW_DOWN (str): Double down arrow icon
        DOUBLE_ARROW_LEFT (str): Double left arrow icon
        DOUBLE_ARROW_RIGHT (str): Double right arrow icon
        DOUBLE_ARROW_UP (str): Double up arrow icon
        DRAG (str): Drag handle icon
        EDIT (str): Edit/pencil icon
        EQUAL (str): Equal operator icon
        ERROR_LIGHT (str): Light error icon
        ERROR (str): Error icon
        EXPAND (str): Expand icon
        EXTERNAL_LINK (str): External link icon
        FILE (str): File icon
        FILTER (str): Filter icon
        GREATER_EQUAL (str): Greater than or equal operator icon
        GREATER_THAN (str): Greater than operator icon
        HIERARCHY (str): Hierarchy icon
        HOME (str): Home icon
        HOURGLASS (str): Hourglass icon
        HOURGLASS_HD (str): High definition hourglass icon
        INDETERMINATE (str): Indeterminate state icon
        INDEX (str): Index icon
        INFO (str): Information icon
        INFO_LIGHT (str): Light information icon
        INFO_HELP (str): Help information icon
        LESS_EQUAL (str): Less than or equal operator icon
        LESS_THAN (str): Less than operator icon
        LOCK_HD (str): High definition lock icon
        LOCK (str): Lock icon
        LOGOUT (str): Logout icon
        MAIL (str): Mail/email icon
        MINUS (str): Minus/subtract icon
        MULTIPLE_SOURCES (str): Multiple sources icon
        NO_DATA (str): No data available icon
        PAUSE (str): Pause icon
        PLAY (str): Play icon
        PLUS (str): Plus/add icon
        RDK (str): RDK icon
        REFRESH (str): Refresh icon
        REPLAY (str): Replay icon
        REQUEST_SELECTION (str): Request selection icon
        SAVE (str): Save icon
        SCREENER (str): Screener icon
        SEARCH (str): Search icon
        SEARCH_BIG (str): Large search icon
        SP_GREY (str): Grey S&P icon
        SP (str): S&P icon
        STAR (str): Star/favorite icon
        STORIES (str): Stories icon
        TABLE (str): Table view icon
        TERMS (str): Terms icon
        TILES (str): Tiles view icon
        TRASH (str): Trash/delete icon
        TRINITY (str): Trinity icon
        UNION (str): Union icon
        USER (str): User/profile icon
        VERTICAL_DOTS (str): Vertical dots menu icon
        WATCHLIST (str): Watchlist icon
        WIDGET_MENU (str): Widget menu icon
        WORLD_BANK (str): World Bank icon
        ZOOM (str): Zoom icon
        SANKEY (str): Sankey diagram icon
        OVERVIEW (str): Overview datatype icon
        FLOWS (str): Flows datatype icon
        SENTIMENT (str): Sentiment datatype icon
        TRADE (str): Trade datatype icon
        FUNDAMENTALS (str): Fundamentals datatype icon
        TECHNICALS (str): Technicals datatype icon
        RISK_ESG (str): Risk ESG datatype icon
        ALL (str): All datatypes icon
        UBS (str): UBS datasource icon
        UBS_BANKS (str): UBS banks datasource icon
        IHS_MARKIT (str): IHS Markit datasource icon
        IHS_MARKIT_GREY (str): Grey IHS Markit datasource icon
        S_P (str): S&P datasource icon
        FACTSET (str): FactSet datasource icon
        FACTSET_GREY (str): Grey FactSet datasource icon
        RAVENPACK (str): RavenPack datasource icon
        RAVENPACK_GREY (str): Grey RavenPack datasource icon
        EPFR (str): EPFR datasource icon
        EPFR_GREY (str): Grey EPFR datasource icon
        ESTIMIZE (str): Estimize datasource icon
        ESTIMIZE_GREY (str): Grey Estimize datasource icon
        CARETTA (str): Caretta datasource icon
        CARETTA_GREY (str): Grey Caretta datasource icon
        DTCC (str): DTCC datasource icon
        DTCC_GREY (str): Grey DTCC datasource icon
        CFTC (str): CFTC datasource icon
        CFTC_GREY (str): Grey CFTC datasource icon
        XIGNITE (str): Xignite datasource icon
        XIGNITE_GREY (str): Grey Xignite datasource icon
        BARCHART (str): Barchart datasource icon
        COMPANY (str): Company market icon
        COUNTRY (str): Country market icon
        SECTOR (str): Sector market icon
        EQUITIES (str): Equities market icon
        FX (str): Foreign exchange market icon
        COMMODITIES (str): Commodities market icon
        FIXED_INCOME (str): Fixed income market icon
        CRYPTO (str): Cryptocurrency market icon
        COMING_SOON (str): Coming soon placeholder icon
        HIGHLIGHTS (str): Highlights icon
    """

    NOT_FOUND_404 = "404"
    ACCRETE = "accrete"
    ARROW_DOWN = "arrow-down"
    ARROW_LEFT = "arrow-left"
    ARROW_LONG_DOWN = "arrow-long-down"
    ARROW_LONG_LEFT = "arrow-long-left"
    ARROW_LONG_RIGHT = "arrow-long-right"
    ARROW_LONG_UP = "arrow-long-up"
    ARROW_RIGHT = "arrow-right"
    BARS = "bars"
    BETWEEN = "between"
    CHECK_SMALL = "check-small"
    CHECK = "check"
    CLOCK = "clock"
    CLONE = "clone"
    CLOSE = "close"
    CLOSE_SMALL = "close-small"
    COLLAPSE = "collapse"
    COLUMN = "column"
    CROSS_ASSET = "cross-asset"
    D3 = "d3"
    DASHBOARD_LINK = "dashboard-link"
    DEFAULT_TABLE_ICON = "default-table-icon"
    DOUBLE_ARROW_DOWN = "double-arrow-down"
    DOUBLE_ARROW_LEFT = "double-arrow-left"
    DOUBLE_ARROW_RIGHT = "double-arrow-right"
    DOUBLE_ARROW_UP = "double-arrow-up"
    DRAG = "drag"
    EDIT = "edit"
    EQUAL = "equal"
    ERROR_LIGHT = "error-light"
    ERROR = "error"
    EXPAND = "expand"
    EXTERNAL_LINK = "external-link"
    FILE = "file"
    FILTER = "filter"
    GREATER_EQUAL = "greater-equal"
    GREATER_THAN = "greater-than"
    HIERARCHY = "hierarchy"
    HOME = "home"
    HOURGLASS = "hourglass"
    HOURGLASS_HD = "hourglass-hd"
    INDETERMINATE = "indeterminate"
    INDEX = "index"
    INFO = "info"
    INFO_LIGHT = "info-light"
    INFO_HELP = "info-help"
    LESS_EQUAL = "less-equal"
    LESS_THAN = "less-than"
    LOCK_HD = "lock-hd"
    LOCK = "lock"
    LOGOUT = "logout"
    MAIL = "mail"
    MINUS = "minus"
    MULTIPLE_SOURCES = "multiple-sources"
    NO_DATA = "no-data"
    PAUSE = "pause"
    PLAY = "play"
    PLUS = "plus"
    RDK = "rdk"
    REFRESH = "refresh"
    REPLAY = "replay"
    REQUEST_SELECTION = "request-selection"
    SAVE = "save"
    SCREENER = "screener"
    SEARCH = "search"
    SEARCH_BIG = "search-big"
    SP_GREY = "sp-grey"
    SP = "sp"
    STAR = "star"
    STORIES = "stories"
    TABLE = "table"
    TERMS = "terms"
    TILES = "tiles"
    TRASH = "trash"
    TRINITY = "trinity"
    UNION = "union"
    USER = "user"
    VERTICAL_DOTS = "vertical-dots"
    WATCHLIST = "watchlist"
    WIDGET_MENU = "widget-menu"
    WORLD_BANK = "world-bank"
    ZOOM = "zoom"
    SANKEY = "sankey"

    # datatype icons
    OVERVIEW = "overview"
    FLOWS = "flows"
    SENTIMENT = "sentiment"
    TRADE = "trade"
    FUNDAMENTALS = "fundamentals"
    TECHNICALS = "technicals"
    RISK_ESG = "risk_esg"
    ALL = "all"
    # datasource icons
    UBS = "ubs"
    UBS_BANKS = "banks"
    IHS_MARKIT = "ihs_markit"
    IHS_MARKIT_GREY = "ihs-markit-grey"
    S_P = "s-p"
    FACTSET = "factset"
    FACTSET_GREY = "factset-grey"
    RAVENPACK = "ravenpack"
    RAVENPACK_GREY = "ravenpack-grey"
    EPFR = "epfr"
    EPFR_GREY = "epfr-grey"
    ESTIMIZE = "estimize"
    ESTIMIZE_GREY = "estimize-grey"
    CARETTA = "caretta"
    CARETTA_GREY = "caretta-grey"
    DTCC = "dtcc"
    DTCC_GREY = "dtcc-grey"
    CFTC = "cftc"
    CFTC_GREY = "cftc-grey"
    XIGNITE = "xignite"
    XIGNITE_GREY = "xignite-grey"
    BARCHART = "barchart"
    # market icons
    COMPANY = "company"
    COUNTRY = "country"
    SECTOR = "sector"
    EQUITIES = "equities"
    FX = "fx"
    COMMODITIES = "commodities"
    FIXED_INCOME = "fixed_income"
    CRYPTO = "crypto"
    # other
    COMING_SOON = "widget-menu"
    HIGHLIGHTS = "star"
