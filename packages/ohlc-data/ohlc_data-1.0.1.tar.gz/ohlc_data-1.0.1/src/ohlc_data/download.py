import os

from ohlc_data.symbol_select import symbol_select
from ohlc_data.alpaca_script import alpaca_script
from ohlc_data.yfinance_script import yfinance_script
from ohlc_data.source_select import source_select

def main():
    """
    Creates ohlc_csv folder and timeframe subfolders, walks user through prompts to download
    OHLC data from Alpaca or Yahoo Finance APIs to appropriate folders
    """

    # Check for ohlc_csv folder
    print('\n','Checking for ohlc_csv folder...','\n')
    if not os.path.isdir('./ohlc_csv'):
        print('\n',f'ohlc_csv folder not found, creating ohlc_csv folder at {os.getcwd()}','\n')

        # Create ohlc_csv folder 
        os.mkdir('./ohlc_csv')
        print('\n','ohlc_csv folder created','\n')
    else:
        print('ohlc_csv found')

    ohlc_path = './ohlc_csv/'

    # Select Symbols
    get_symbols = symbol_select()

    # Source
    get_source = source_select()

    if get_source == 'Yfinance':
        yfinance_script(get_symbols, ohlc_path)
    else:
        alpaca_script(get_symbols, ohlc_path)

if __name__ == "__main__":
    main()
