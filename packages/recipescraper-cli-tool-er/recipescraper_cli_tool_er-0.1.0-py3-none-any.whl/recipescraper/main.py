from .utils import get_data, write_data
import validators
import argparse

def main():
    array = []
    parser = argparse.ArgumentParser(description='Scrape cooking recipe from a website and write to a txt file.')
    parser.add_argument('url', help='URL for the recipe page.')
    url = parser.parse_args()
    print(f'Scraping the recipe from {url.url}')
    #url = input('Enter the url to scrape recipe (enter "q" to quit): ')
    
    if validators.url(url.url):
        
        new_array, file_name = get_data(url.url, array)
        
        if len(new_array) < 4:
            print(f'I was not able to get the recipe from {url.url}')
            
        else:
            write_data(new_array, file_name)
            
        
    else:
        if (url.lower() == 'q'):
            print('\nGoodbye!\n')
        else:
            print('\nInvalid URL\n')
            
    

if __name__ == "__main__":
    main()
