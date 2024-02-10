import csv
import unicodedata
import requests
from bs4 import BeautifulSoup
import time

def read_sorted_verbs(file_path):
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return [row[0].split(', ')[1][1:-2] for row in reader]


def get_page(page_id):
    url = 'https://en.m.wiktionary.org/wiki/'
    doc = requests.get(
        url=url,
        params={
            'curid': page_id
        }
    ).content
    return doc

def get_verb(doc):
    soup = BeautifulSoup(doc, 'html.parser')
    # Headline section
    headline_section = soup.find('span', class_='headword-line')
    if not headline_section:
        return None
    
    # definition
    verb_definition = soup.find('ol')
    if verb_definition:
        ol_text = verb_definition.get_text(separator=' ')
        lines   = ol_text.split('\n')
        ol_text = "Definition: \n " + lines[0]
    
    headword = headline_section.find('strong', class_='headword')
    headword_text = sanitize(headword.get_text()) if headword else None

    # Aspect info
    gender_span = headline_section.find('span', class_='gender')
    gender_text = sanitize(gender_span.get_text()) if gender_span else None

    # Extract aspects 
    aspect_A = None
    aspect_B = None
    if gender_span:
        # Check for the next sibling after gender_span
        if gender_span.find_next_sibling() is not None:
            next_Aspect = gender_span.find_next_sibling()
            if next_Aspect and next_Aspect.name == 'i':
                aspect_A = sanitize(next_Aspect.get_text())

            # Check for the next sibling after imperfective aspect
            next_sibling_after_A = next_Aspect.find_next_sibling()
            if next_sibling_after_A and next_sibling_after_A.name == 'b':
                aspect_B = sanitize(next_sibling_after_A.get_text())

        else:
            aspect_A = None
            aspect_B = None

    #Keep an eye on this. It seems like it'll correctly do: [word, aspect, opposite aspect type, opposite word]        
    VERB = [headword_text,gender_text,aspect_A,aspect_B,ol_text] 

    Present_target_conjugations = [ "Cyrl form-of lang-ru 1|s|pres|ind-form-of origin-",
                                    "Cyrl form-of lang-ru 2|s|pres|ind-form-of origin-",
                                    "Cyrl form-of lang-ru 3|p|pres|ind-form-of origin-"]
    
    Future_target_conjugations = [  "Cyrl form-of lang-ru 1|s|fut|ind-form-of origin-",
                                    "Cyrl form-of lang-ru 2|s|fut|ind-form-of origin-",
                                    "Cyrl form-of lang-ru 3|s|fut|ind-form-of origin-"
                                    ]
    VERB_conjugations = []
    person = ["Я ", "Ты ", "Они "]

    try:
        Imperfective_found = False
        for conj in Present_target_conjugations:
            target_conj = f'{conj}{VERB[0]}'
            conjugation_span = soup.find('span', class_=target_conj)

            if conjugation_span is not None:
                conjugation_text = sanitize(conjugation_span.get_text())
                Imperfective_found = True
                VERB_conjugations.append(person[Present_target_conjugations.index(conj)] + conjugation_text)
            if conjugation_span is None:
                continue
            
        if Imperfective_found == False:
            for conj in Future_target_conjugations:
                target_conj = f'{conj}{VERB[0]}'
                conjugation_span = soup.find('span', class_=target_conj)

                if conjugation_span is not None:
                    conjugation_text = sanitize(conjugation_span.get_text())
                    VERB_conjugations.append(person[Future_target_conjugations.index(conj)] + conjugation_text)
                else:
                    VERB_conjugations.append("Check conj.")
                    continue
                             
    except IndexError:
        print("Index Error")
        return None

    VERB_extract = (VERB, VERB_conjugations)

    return VERB_extract


def sanitize(word):
    # Preserve diacritic marks for vowels and exclude Ё ё from removal
    preserved_chars = {'́', '̀', '̂', '̌', '̆', '̑', '̄', 
                       '̈', '̇', '̧', '̣', '̃', '̊', '̍', 
                       '̎', '̓', '̈', '̉', '̛', '̣', 'Ё', 'ё'}
    normalized_word = unicodedata.normalize('NFD', word)
    
    # current fix for whenever the verb is monosyllabic
    has_stress = any(char in normalized_word for char in preserved_chars)
    if not has_stress:
        # Mapping between vowels and their accented versions
        #Á á Ó ó É é У́ ý И́ и́ Ы́ ы́ Э́ э́ Ю́ ю́ Я́ я́
        vowel_mapping = {'а': 'á','я': 'я́','э': 'э́','е': 'é',
                         'и': 'и́','ы': 'ы́','о': 'ó','у': 'ý',
                         'ю': 'ю́', 'а': 'а́', 'о':'о́', 'и́':'и́',
                         'е':'е́', 'у':'у́'}
        for vowel, accented_vowel in vowel_mapping.items():
            normalized_word = normalized_word.replace(vowel, accented_vowel)

    caret_stat = any('̆' in char for char in normalized_word)
    if caret_stat:
        #print(f'problem word {caret_stat}')
        normalized_word = normalized_word.replace('й', 'й')
            
    
    # Keep characters in preserved_chars and alphanumeric characters
    sanitized_text = ''.join(char if char.isalnum() or char in preserved_chars else ' ' for char in normalized_word)

    return sanitized_text.strip()

def get_progress(current, total):
    return f'{int(current / total * 100)}%'

if __name__ == '__main__':

    '''sorted_classes = ['class 1','class 2','class 3',
             'class 4','class 5','class 6',
             'class 7','class 8','class 9',
             'class 10','class 11','class 12',
             'class 13','class 14','class 15',
             'class 16','irregular']'''
    sorted_classes = ['class 9','class 10',
                    'class 11','class 12',
                    'class 13','class 14',
                    'class 15','class 16',
                    'irregular']

    start_time = time.time()
    for srt_clss in sorted_classes:
        IDS = read_sorted_verbs( "Sorted_verbs_class\\" + f"Sorted_{srt_clss}.csv")
        scraped_words = []
        start   = 0
        end     = len(IDS)
        print(f"Starting {srt_clss}")
        for id in IDS:
            page    = get_page(id)
            article = get_verb(page)

            if article is not None:
                scraped_words.append(article)
            else:
                print(f"Error: Unable to retrieve curdID = {id}.")
                print(article)
                continue
            if start % 10 == 0:
                print(f'Current progress {get_progress(start,end)}')
            start += 1
            
        with open(f"Scraped_verbs_{srt_clss}.csv", 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Front of Card", "Back of Card"])
            writer.writerows([[word[0], word[1]] for word in scraped_words]) 
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time} sec")
