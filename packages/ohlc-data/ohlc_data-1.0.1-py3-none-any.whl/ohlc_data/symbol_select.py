from ohlc_data.utils import validate_symbol, dropdown

def symbol_select() -> str | list[str]:
    """
    Input symbol or list of symbols to download OHLC data for
    """

    symbols_selected = dropdown('Download data for: ', ['One symbol', 'Multiple symbols'])

    # Single Ticker chosen
    if symbols_selected == 'One symbol':
        while True:
            print('\n')
            symbol = input('Enter symbol: ').strip().upper()
            
            if validate_symbol(symbol):
                break
            else:
                print('You may have entered an invalid or unsupported symbol, try again')
        return symbol

    # Multi-Ticker chosen
    elif symbols_selected == 'Multiple symbols':
        while True:
            print('\n')
            symbol_list = input('Enter symbols (separate symbols with single space, not case-sensitive): ').strip().upper()

            if not symbol_list:
                print('\n')
                print('You must enter at least one symbol.')
                continue
            
            symbol_split = symbol_list.split(' ')
            symbols = [symbol.strip() for symbol in symbol_split if symbol.strip()]

            symbol_check = [validate_symbol(symbol) for symbol in symbols]

            if False in symbol_check:
                print('\n')
                print('At least one symbol might have been input incorrectly, make sure to separate each symbol with a space')
                continue
            else:
                break
    
        return symbols