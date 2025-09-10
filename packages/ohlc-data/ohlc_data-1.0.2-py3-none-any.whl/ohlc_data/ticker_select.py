from ohlc_data.utils import validate_ticker, dropdown

def ticker_select() -> str | list[str]:
    """
    Input ticker or list of tickers to download OHLC data for
    """

    ticker_selected = dropdown('Download data for: ', ['Single ticker', 'Multiple tickers'])

    # Single Ticker chosen
    if ticker_selected == 'Single ticker':
        while True:
            print('\n')
            ticker = input('Enter ticker: ').strip().upper()
            
            if validate_ticker(ticker):
                break
            else:
                print('You may have entered an invalid or unsupported ticker, try again')
        return ticker

    # Multi-Ticker chosen
    elif ticker_selected == 'Multiple tickers':
        while True:
            print('\n')
            ticker_list = input('Enter tickers (separate tickers with single space, not case-sensitive): ').strip().upper()

            if not ticker_list:
                print('\n')
                print('You must enter at least one ticker.')
                continue
            
            ticker_split= ticker_list.split(' ')
            tickers = [ticker.strip() for ticker in ticker_split if ticker.strip()]

            ticker_check = [validate_ticker(ticker) for ticker in tickers]

            if False in ticker_check:
                print('\n')
                print('At least one ticker might have been input incorrectly, make sure to separate each ticker with a space')
                continue
            else:
                break
    
        return tickers