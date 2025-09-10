import os
import pandas as pd
from datetime import datetime, timedelta
from ohlc_data.utils import validate_date, dropdown, custom_period, download_and_save


def alpaca_script(ticker_input: str | list[str], path) -> None:
    """
    Download OHLC data through Alpaca API. More flexible with intervals, lookback
    period limited to 2016 - today. Pre/Post market data available.
    """
    
    date_format = '%Y-%m-%d'
    datetime_format = '%Y-%m-%d %H:%M:%S'

    start_date = None
    end_date = None

    # Choose Period
    period_selected = dropdown('Choose lookback period: ', ['Days','Years', 'Custom'])

    if period_selected != 'Custom':
        print('Note: Data from Alpaca only goes as far back as 2016')
        while True:
            period = input(f'Number of {period_selected.lower()}: ') + period_selected[0].lower()
            if period_selected == 'Years' and datetime.today().year - int(period[:-1]) < 2016:
                print('Lookback limit exceeded. Alpaca only provides data as far back as 2016.')
                continue
            elif period_selected == 'Days' and (datetime.today().year * 365) - int(period[:-1]) < (2016 * 365):
                print('Lookback limit exceeded. Alpaca only provides data as far back as 2016.')
                continue
            else:
                break

        # Choose Interval
        interval_timeframe = dropdown('Choose interval timeframe: ', ['Minutes', 'Hours', 'Daily'])
        if interval_timeframe == 'Daily':
            interval = '1d'
            print('Daily intervals selected')
        else:
            interval_selected = input(f"Number of {interval_timeframe.lower()}: ")
            interval = interval_selected + interval_timeframe[0].lower()
            print(interval_selected)

    else:
        period = None
        interval_timeframe = dropdown('Choose interval timeframe: ', ['Minutes', 'Hours', 'Daily'])
        if interval_timeframe == 'Daily':
            start_date, end_date = custom_period()
            interval = '1d'
            print('Daily intervals selected')
        else:
            interval_selected = input(f'Number of {interval_timeframe.lower()}: ')
            interval = interval_selected + interval_timeframe[0].lower()
            start_date, end_date = custom_period(intraday=True)

    # Optional End date
    opt_end_datetime = (
        'End date (YYYY-MM-DD) (optional): ' if 'd' in interval else
        'End Datetime (YYYY-MM-DD HH:MM:SS) (optional): '
    )

    opt_end_error = (
        'Invalid date, ensure YYYY-MM-DD format' if 'd' in interval else
        'Invalid datetime, ensure YYYY-MM-DD HH:MM:SS'
    )

    if period_selected == 'Days':

        while True:
            print('\n')
            end_input = input(opt_end_datetime)
            if end_input and not validate_date(end_input, datetime_format):
                print(opt_end_error)
                continue
            elif end_input and validate_date:
                if pd.to_datetime(end_input) - timedelta(days=int(period[:-1])) < pd.to_datetime('2016-01-01 09:30:00'):
                    print('Lookback goes beyond 2016 limit')
                else:
                    break
                continue
            else:
                end_date = end_input if end_input else None
                break

    elif period_selected == 'Years':
        while True:
            print('\n')
            end_input = input(opt_end_datetime)
            if end_input and not validate_date(end_input, date_format):
                print(opt_end_error)
                continue
            elif end_input and validate_date:
                if pd.to_datetime(end_input) - timedelta(weeks=int(period[:-1]) * 52) < pd.to_datetime('2016-01-01 09:30:00'):
                    print('Lookback goes beyond 2016 limit')
                else:
                    break
                
            else:
                end_date = end_input if end_input else None
                break

    # Create new folder for new timeframe / interval
    if interval not in os.listdir(path):
        os.mkdir(f'{path}{interval}/')

    # Pre/Post Market Data or Regular Hours
    if 'd' not in interval:
        pre_post_prompt = dropdown('Include Pre/Post Market Data?: ', ['Yes','No'])
        pre_post = True if pre_post_prompt == 'Yes' else False
    else:
        pre_post = False

    # Download OHLC data, save as CSV
    print('\n')
    print('Downloading OHLC data...','\n')

    if isinstance(ticker_input, list):
        for ticker in ticker_input:
            download_and_save(path, ticker, 'alpaca', period, interval, start_date, end_date, pre_post=pre_post)
    else:
        download_and_save(path, ticker_input, 'alpaca', period, interval, start_date, end_date, pre_post=pre_post)
        
    print("OHLC data downloaded successfully!")