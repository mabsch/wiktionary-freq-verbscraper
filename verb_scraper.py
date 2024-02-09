import csv
import unicodedata
import requests
from bs4 import BeautifulSoup

def read_sorted_verbs(file_path):
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return [row[0].split(', ')[1][1:-2] for row in reader]


def get_page(page_id):
    url = 'https://wiktionary.org/wiki/'
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
        #print("Definition: \n " + ol_text)
    
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
    #print(VERB)

    target_conjugations = ["Cyrl form-of lang-ru 1|s|pres|ind-form-of origin-",
                           "Cyrl form-of lang-ru 2|s|pres|ind-form-of origin-",
                           "Cyrl form-of lang-ru 3|p|pres|ind-form-of origin-",
                           "Cyrl form-of lang-ru 1|s|fut|ind-form-of origin-",
                           "Cyrl form-of lang-ru 2|s|fut|ind-form-of origin-",
                           "Cyrl form-of lang-ru 3|s|fut|ind-form-of origin-"
                           ]
    VERB_conjugations = []
    person = ["Я ", "Ты ", "Они "]
    for conj in target_conjugations:
        target_conj = conj + VERB[0]
        #print(target_conj)
        conjugation_span = soup.find('span', class_=target_conj)

        if conjugation_span:
            conjugation_text = sanitize(conjugation_span.get_text())
            VERB_conjugations.append(person[target_conjugations.index(conj)] + conjugation_text)

    VERB_extract = (VERB, VERB_conjugations)

    return VERB_extract


def sanitize(word):
    # Preserve diacritic marks for vowels and exclude Ё ё from removal
    preserved_chars = {'́', '̀', '̂', '̌', '̆', '̑', '̄', 
                       '̈', '̇', '̧', '̣', '̃', '̊', '̍', 
                       '̎', '̓', '̈', '̉', '̛', '̣', 'Ё', 'ё'}

    normalized_word = unicodedata.normalize('NFD', word)
    
    # Keep characters in preserved_chars and alphanumeric characters
    sanitized_text = ''.join(char if char.isalnum() or char in preserved_chars else ' ' for char in normalized_word)

    return sanitized_text.strip()

def get_progress(current, total):
    return f'{round(current / total * 100)}%'

if __name__ == '__main__':

    sorted_classes = ['class 1','class 2','class 3',
             'class 4','class 5','class 6',
             'class 7','class 8','class 9',
             'class 10','class 11','class 12',
             'class 13','class 14','class 15',
             'class 16','irregular']
    
    for srt_clss in sorted_classes:
        IDS = read_sorted_verbs(f"Sorted_{srt_clss}.csv")
        scraped_words = []
        start   = 0
        end     = len(IDS)
        for id in IDS:
            page    = get_page(id)
            article = get_verb(page)

            if article is not None:
                scraped_words.append(article)
                start =+ 1
            else:
                start =+ 1
                print(f"Error: Unable to retrieve curdID = {id}.")
            if start % 100 == 0:
                print(f'Current progress {get_progress(start,end)}')
            
        with open(f"Scraped_verbs{srt_clss}.csv", 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Front of Card", "Back of Card"])
            writer.writerows([[word[0], word[1]] for word in scraped_words]) 
