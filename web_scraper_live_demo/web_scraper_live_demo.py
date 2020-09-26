"""
A script to get the 20 words and their frequency percentage 
with highest frequency in an English Wikipedia article. 
"""
import bs4 
import json
import operator
import re
import requests
import stop_words
import sys
import tabulate

class WebScraper:
    """
    DOCSTRING
    """
    def clean_word(self, word):
        """
        DOCSTRING
        """
        cleaned_word = re.sub('[^A-Za-z]+', '', word)
        return cleaned_word

    def create_frequency_table(self, word_list):
        """
        DOCSTRING
        """
        word_count = {}
        for word in word_list:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1
        return word_count

    def get_word_list(self, url):
        """
        DOCSTRING
        """
        word_list = list()
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = bs4.BeautifulSoup(plain_text,'lxml')
        for text in soup.findAll('p'):
            if text.text is None:
                continue
            content = text.text
            words = content.lower().split()
            for word in words:
                cleaned_word = self.clean_word(word)
                if len(cleaned_word) > 0:
                    word_list.append(cleaned_word)
        return word_list

    def remove_stop_words(self, frequency_list):
        """
        DOCSTRING
        """
        stop__words = stop_words.get_stop_words('en')
        temp_list = list()
        for key,value in frequency_list:
            if key not in stop__words:
                temp_list.append([key, value])
        return temp_list

if __name__ == '__main__':
    wikipedia_api_link = 'https://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch='
    wikipedia_link = 'https://en.wikipedia.org/wiki/'
    if(len(sys.argv) < 2):
        print('Enter valid string')
        exit()
    string_query = sys.argv[1]
    if(len(sys.argv) > 2):
        search_mode = True
    else:
        search_mode = False
    url = wikipedia_api_link + string_query
    try:
        response = requests.get(url)
        data = json.loads(response.content.decode("utf-8"))
        wikipedia_page_tag = data['query']['search'][0]['title']
        url = wikipedia_link + wikipedia_page_tag
        page_word_list = WebScraper.get_word_list(url)
        page_word_count = WebScraper.create_frequency_table(page_word_list)
        sorted_word_frequency_list = sorted(
            page_word_count.items(), key=operator.itemgetter(1), reverse=True)
        if(search_mode):
            sorted_word_frequency_list = WebScraper.remove_stop_words(sorted_word_frequency_list)
        total_words_sum = 0
        for key,value in sorted_word_frequency_list:
            total_words_sum = total_words_sum + value
        if len(sorted_word_frequency_list) > 20:
            sorted_word_frequency_list = sorted_word_frequency_list[:20]
        final_list = list()
        for key,value in sorted_word_frequency_list:
            percentage_value = float(value * 100) / total_words_sum
            final_list.append([key, value, round(percentage_value, 4)])
        print_headers = ['Word', 'Frequency', 'Frequency Percentage']
        print(tabulate.tabulate(final_list, headers=print_headers, tablefmt='orgtbl'))
    except requests.exceptions.Timeout:
        print("The server didn't respond. Please, try again later.")
