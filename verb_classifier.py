import csv

def read_freq_verbs(file_path):
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return [row[2] for row in reader if len(row) >= 3]

def read_class(file_path):
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return [row for row in reader]
    



if __name__ == '__main__':
    
    verb_cats = ['class 1','class 2','class 3',
             'class 4','class 5','class 6',
             'class 7','class 8','class 9',
             'class 10','class 11','class 12',
             'class 13','class 14','class 15',
             'class 16','irregular']
            
    #verb_cats = ['class 10']
    Verbs  = read_freq_verbs('verbs_Freqlist_utf.csv')
    total_verbs = 0
    

    for cat in verb_cats:
        sorted_verbs = []
        print(cat)
        category     = read_class(f'Russian {cat} verbs_members.csv')
        #Russian class 10 verbs_members.csv
        #print(category)
        for verb in category:
            #print(verb[0])
            if verb[0] in Verbs:
                sorted_verbs.append(verb)
        
        print(len(sorted_verbs))
        total_verbs += len(sorted_verbs)
        with open(f'Sorted_{cat}.csv', 'w', encoding='utf-8', newline='') as output_file:
            csv.writer(output_file).writerows([[verb] for verb in sorted_verbs])
    print(f'total verbs sorted =  {total_verbs}')

