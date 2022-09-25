start_season = 1990
season_list = [f'{year}-{year+1}' for year in range(1990, 2022)]
sex = input('male or female? [m/w] \n>')
for season in season_list:
    if sex == 'm':
        with open(f'athletes_{season}.txt', mode='a') as f:
            pass
    elif sex == 'w':
        with open(f'athletes_{season}_w.txt', mode='a') as f:
            pass
    else: print('Choose m or f')
