from booking.booking import Booking


with Booking(teardown=False) as bot:
    bot.land_first_page()
    # bot.change_currency(currency='GBP')
    bot.selectPlaceToGo(place_to_go='New York')
