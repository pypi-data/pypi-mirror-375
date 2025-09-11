import yfinance as yf
import pandas as pd


def get_price(ticker: str) -> float | Exception:
    """
    Hissenin güncel fiyatını döner.
    :param ticker: Hisse kısalması
    :return: Güncel fiyat bilgisi veya oluşan hata detayı
    """
    try:
        data = yf.Ticker(ticker)
        return data.info.get('currentPrice')
    except Exception as e:
        return e


def get_history(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Belirli tarih aralığında günlük verileri döner.

    :param ticker: Hisse kısalması
    :param start: Tarih aralığının başlangıcı
    :param end: Tarih aralığının sonu
    :return: Fiyat geçmişi bilgisi veya oluşan hata detayı
    """
    try:
        data = yf.Ticker(ticker)
        return data.history(start=start, end=end)
    except Exception as e:
        return e


def get_prices(tickers: list[str]) -> dict:
    """
    Birden çok hissenin güncel fiyatını döner.
    :param tickers: Hisse kısalmaları listesi
    :return: Her hisse başına güncel fiyat bilgisi veya oluşan hata detayları
    """
    prices = {}
    for ticker in tickers:
        prices[ticker] = get_price(ticker)
    return prices


def get_histories(tickers: list[str], start: str, end: str) -> dict:
    """
    Birden çok hissenin güncel fiyatını döner.
    :param start: Tarih aralığının başlangıcı
    :param end: Tarih aralığının sonu
    :param tickers: Hisse kısalmaları listesi
    :return: Her hisse başına fiyat geçmişi bilgisi veya oluşan hata detayları
    """
    histories = {}
    for ticker in tickers:
        histories[ticker] = get_history(ticker, start, end)
    return histories
