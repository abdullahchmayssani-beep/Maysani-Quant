"""Provider adapters (ADR 0003). Each module here is a replaceable FETCH+PARSE
implementation for one vendor. Nothing outside `data/providers/` may import a
specific adapter module - only the `MarketDataProvider` protocol in
`data/providers/base.py`.
"""
