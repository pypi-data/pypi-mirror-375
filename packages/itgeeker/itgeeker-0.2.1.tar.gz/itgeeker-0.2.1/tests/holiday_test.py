from datetime import datetime, date

from itgeeker.date_geeker import is_summer_vacation

if __name__ == '__main__':
    today = date.today()
    if is_summer_vacation(today):
        print(f"{today} is during summer vacation.")
    else:
        print(f"{today} is not during summer vacation.")

    # Test with a specific date
    test_date = date(2023, 8, 15)
    if is_summer_vacation(test_date):
        print(f"{test_date} is during summer vacation.")
    else:
        print(f"{test_date} is not during summer vacation.")