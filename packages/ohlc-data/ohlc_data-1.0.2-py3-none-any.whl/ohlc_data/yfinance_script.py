import os
from ohlc_data.utils import dropdown, custom_period, download_and_save


def yfinance_script(ticker_input: str | list[str], path: str) -> None:
    """
    Download OHLC data through Yfinance API. Intervals and periods are strict. Daily data
    can span a few decades for some stocks.
    """
    
    start_date = None
    end_date = None

    period_selected = dropdown('Choose lookback period: ', ['Days','Years','Custom'])

    if period_selected == 'Days':
        num_period = int(input('Number of days: '))

        if num_period <= 7: 
            interval_selected = dropdown('Choose interval: ', ['1m', '2m', '5m', '15m', '30m', '1h', '4h', '1d'])
        elif num_period > 7 and num_period <= 60:
            interval_selected = dropdown('Choose interval: ', ['5m', '15m', '30m', '1h', '4h', '1d'])
        elif num_period > 60 and num_period < 730:
            interval_selected = dropdown('Choose interval: ', ['1h', '4h', '1d'])
        else:
            print("Number of days is greater than 730 and therefore the only interval available for yfinance is '1d' (Daily bars).")
            interval_selected = '1d'

    elif period_selected == 'Years': 
        num_period = int(input('Number of years: '))

        if num_period <= 2:
            interval_selected = dropdown('Choose interval: ', ['1h', '4h', '1d'])
        else:
            interval_selected = dropdown('Choose interval: ', ['1d','1wk'])

    else:           
        if interval_selected == '1d' or interval_selected == '1wk':
            start_date, end_date = custom_period()
        else:
            start_date, end_date = custom_period(intraday=True)

    period = str(num_period) + period_selected[0].lower()

    if interval_selected not in os.listdir(path):
        os.mkdir(f'{path}{interval_selected}/')

    # Save multiple ticker to csv folder
    if isinstance(ticker_input, list):
        for ticker in ticker_input:
            download_and_save(path, ticker, 'yfinance', period, interval_selected, start_date, end_date)
    # Save single ticker to csv folder 
    else:
        download_and_save(path, ticker_input, 'yfinance', period, interval_selected, start_date, end_date)

    print("OHLC data downloaded successfully!")