from functions.main import af_daily

if __name__ == '__main__':
    with open('./history_titles_empty.txt', 'w') as f:
        f.write("This is a sample entry that won't match anything from the feed!")
    af_daily()
