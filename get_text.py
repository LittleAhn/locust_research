import pdfplumber
import re

def clean_page(file_path):
    pdf = pdfplumber.open(file_path)
    final_txt = []
    # determine if old style
    year = int(file_path[-4:])
    #print('file_path: ', file_path)
    month = re.findall(r'.+/([A-Z]+)_', file_path)[0]
    #print('month is: ', month)
    old_style = (1996 <= year <= 2017)
    #if year == 1996:
        # JULY TO DECEMBER 1996 IS OLD STYLE!!!
        # or don't  even feed anything older to this...
    #print("old style? ", old_style)
    for i, page in enumerate(pdf.pages):
        left, right = get_left_side(page, i, old_style, file_path), get_right_side(page, i, old_style, file_path)
        #right = get_right_side(page)
        if left:
            clean_left = clean_text(left)
        #print("page number is: ", i)
        #print("right is: ", right)
        if right:
            clean_right = clean_text(right)
        else: # empty right side
            clean_right = ""
        final_txt.append(clean_left)
        final_txt.append(clean_right)
    final_txt = "\n".join(final_txt)
    final_txt = get_relevant_text(final_txt, year, month)
    return final_txt


def clean_text(text): # make this prettier
    #cleaned = single_word(text)
    #cleaned = two_word(cleaned)
    #cleaned = many_countries(cleaned)
    #return cleaned
    return many_countries(two_word(single_word(text))) # is this clean or gross

def get_left_side(page, pg_num, old_style, file_path):
    x0 = 0
    #print("old_style", old_style)
    #print("page num: ", pg_num)
    if old_style: 
        if pg_num % 2 == 0:
            x1 = page.width // 2 - 20  
        elif file_path.endswith('SEPT_2006') and pg_num == 3:
            x1 = page.width // 2 + 10
        else:
            x1 = page.width // 2 + 20
    else:
        x1 = page.width // 2
    bottom = page.height - 70
    top = 0
    return page.crop((x0, top, x1, bottom)).extract_text()


def get_right_side(page, pg_num, old_style, file_path):
    if old_style:
        if pg_num % 2 == 0:
            x0 = page.width // 2 - 18
        elif file_path.endswith('SEPT_2006') and pg_num == 3:
            x0 = page.width // 2 + 10
        else:
            x0 = page.width // 2 + 20
    else:
        x0 = page.width // 2
    x1 = page.width
    bottom = page.height - 70
    top = 0

    return page.crop((x0, top, x1, bottom)).extract_text()

def single_word(text):
    #print("text is: ", text)
    #return re.sub(r'(\n[A-Z]) *\n([A-Z]+)', r'\1\2', text)
    return re.sub(r'(\n[A-Z]|^[A-Z]) *\n([A-Z]+)', r'\1\2', text)

    #return re.sub(r'([A-Z]) *\n([A-Z]+)', r'\1\2', text) # try making first new line optional/taking it out
    #return re.sub(r'(\n?[A-Z]) *\n([A-Z]+)', r'\1\2', text) # try making first new line optional/taking it out



def two_word(text):
    line_list = text.split('\n')
    for i, line in enumerate(line_list):
        country = []
        to_replace = []
        #elif line == "D.R. C":
        if re.match(r'[A-Z]  [A-Z]$', line):
            first_line = line
            first_line_list = line.split("  ")
            #print(first_line)
            next_line = line_list[i + 1]
            next_line_list = next_line.split(" ")
            #print(next_line)
            for n in range(len(first_line_list)):
                country.append(first_line_list[n] + next_line_list[n])
            #print(country)
            country = " ".join(country)
            to_replace.append(first_line)
            to_replace.append(next_line)
            to_replace = "\n".join(to_replace)
            text = text.replace(first_line+'\n'+next_line, country)
        #elif re.match(r'[A-Z]    [A-Z]'):
            #next_line_list = 
        elif line == "D.R. C":
            next_line = line_list[i + 1]
            country = "DR CONGO"
            text = text.replace(line+'\n'+next_line, country)

    return text

def many_countries(text):
    #print("cleaning many countries!")
    line_list = text.split('\n')
    to_replace = []
    for i, line in enumerate(line_list):
        to_replace = []
        rv = ""
        if re.match(r'[A-Z](.[A-Z]. [A-Z])? ( [A-Z]|  .[A-Z] )? ?,|[A-Z]    [A-Z]', line):
            #print(line)
            #first_line = line
            to_replace.append(line)
            #print("to_replace", to_replace)
            first_line_list = re.split(" ", line)
            #first_line_list = [sub.replace('', '') for sub in first_line_list]
            #first_line_list = line.split("  ")
            #print("first_line_list", first_line_list)
            next_line = line_list[i + 1]
            to_replace.append(next_line)
            #print(next_line)
            next_line_list = next_line.split(" ")
            #print("next_line_list", next_line_list)
            suffix_cnt = 0
            for i, char in enumerate(first_line_list):
                #print("char is: ", char)
                if char == "UAE" or char == "D.R.":
                    rv += char + " "
                #elif char == "D.R":
                
                elif re.search(r'[A-Z]', char):
                    rv += char + next_line_list[suffix_cnt]
                    suffix_cnt += 1
                #elif not char and not first_line_list[i - 1]: # not repeated empty string
                elif not char: # not repeated empty string
                    #if first_line_list[i - 1]:
                    if not rv.endswith(" ") and not rv.endswith(","): # accounts for inconsistent oxford commas
                        rv += " "
                        #print("empty space not repeated")
                    else:
                        if suffix_cnt >= len(next_line_list): # repeated empty space, no more suffix
                            rv += char
                        else:
                            rv += char + next_line_list[suffix_cnt]
                            suffix_cnt += 1
                        #print(" repeated empty space")
                else:
                    rv += char
                #print(rv)    
        to_replace = '\n'.join(to_replace)
        #if to_replace and rv:
            #print("to_replace", to_replace)
            #print("replace with", rv)
        text = text.replace(to_replace, rv)
        # replace the text
    #print("cleaned_text looks like:")
    #print(text)
    return text

def get_relevant_text(text, year, month):
    '''
    Cleans up relevant text so it can be parsed into a dataframe.
    '''
    result = re.findall(r'(?:\nSituation and Forecast)+(.+?)(?:Announcements?|Other Locusts\n|Glossary of Terms|Other Species|Other Migratory Pests)', 
                        text, flags = re.DOTALL|re.IGNORECASE)[0]
    #print(result)
    #
    #print("type of result: ", type(result))ß
    # get rid of headers and footers
    to_keep = []
    for line in result.split('\n'):
        #print("line is: ", line)
        if line and not re.match(r'(Desert Locust )?Situation and Forecast|D E S E R T  L O C U S T  B U L L E T I N|No. \d+|\( ?see also the summary|^\w ?$', line, re.IGNORECASE):
            to_keep.append(line)
            #print("appended")
    final_text = '\n'.join(to_keep)
    final_text = re.sub(r'\(cid:127\)', r'• ', final_text)
    final_text = re.sub(r'\n( +)?•( +)?F( +)?(\n)?orecaSt\n', r'\n• FORECAST\n', final_text, flags = re.IGNORECASE)
    #final_text = re.sub(r'\n•( +)?F( +)?ORECAST\n', r'\n• FORECAST\n', final_text, flags=re.IGNORECASE)
    final_text = re.sub(r'\n- SITUATION\n', r'\n• SITUATION\n', final_text, flags = re.IGNORECASE)
    final_text = re.sub(r'\n( +)?•( +)?S( +)?\n?ituation\n', r'\n• SITUATION\n', final_text, flags = re.IGNORECASE)
    final_text = re.sub(r'\n( +)?• S( +)?\n?ituation\n', r'\n• SITUATION\n', final_text, flags = re.IGNORECASE)
    final_text = re.sub(r'dekad', r'decade', final_text)
    final_text = re.sub(r' sq.', r' sq', final_text)
    final_text = re.sub(r' m.', r' m', final_text)
    final_text = re.sub(r' Sh.', r' Sh', final_text)
    final_text = re.sub(r' mtur', r' matur', final_text)
    final_text = re.sub(r' md-', r'mid-', final_text)
    final_text = re.sub(r'mderate', r'moderate', final_text)
    final_text = re.sub(r'\bmnth\b', r' month', final_text)
    final_text = re.sub(r'(\b)mre(\b)', r'(\1)more(\2)', final_text)
    final_text = re.sub(r'(\b)mde(\b)', r'\1made\2', final_text)
    final_text = re.sub(r' (mve)(s?) ', r' move\2', final_text)
    #final_text = re.sub(r'\bmnitor\b', r'\bmonitor\b', final_text)
    final_text = re.sub(r'(signifi) +(cant)', r'\1\2', final_text)
    final_text = re.sub(r'signiﬁ +cant', r'significant', final_text)
    final_text = re.sub(r'N +o significant', r'No significant', final_text)
    if year == 1996 and month == 'AUG':
        final_text = re.sub(r'\nNiger\n(?<!• SITUATION)$', r'\nNiger\n• SITUATION\n', final_text) # manually fix AUG 1996 issue
    if year == 2007 and month == 'OCT':
        final_text = re.sub(r'\ncoastal plains\n', r'\ncoastal plains.\n', final_text) # manually fix OCT 2007 issue
    if year == 1996 and month in ['SEPT', 'OCT']:
        final_text = re.sub(r'the east\nSomalia\n', r'the east.\nSomalia\n', final_text)
    if year == 1999 and month == 'JUNE':
        final_text = re.sub(r'commence\nChad\n', r'commence.\nChad\n', final_text)
    if year == 1999 and month == 'NOV':
        final_text = re.sub(r'Morocco\nNiger\n', r'Morocco.\nNiger\n', final_text)
    if year == 2008 and month == 'JUNE':
        final_text = re.sub(r'summer\nAfghanistan\n', r'summer.\nAfghanistan\n', final_text)


    return final_text

# def prep_text(year, month, text):
#     '''
#     Prepares text for processing.
#     '''
#     if int(year) < 2002 or (int(year) == 2002 and month in ['JAN', 'FEB', 'MAR', 'APR']):
#         text = re.sub(r'-\n', "", text)
#         text = re.sub(r'\n', " ", text)
#     else:
#         text = re.sub(r'\n', "", text)
#     #text = re.sub(r'J ask', r'Jask', text)
#     text = re.sub(r' ([B-Z]) ([a-z]+)', r' \1\2', text) # should handle the above case
#     text = re.sub(r'no reports of ([a-z]+)', r'no \1', text)
#     text = re.sub(r'(signifi) +(cant)', r'\1\2', text)
#     text = re.sub(r'\nNiger\n', r'\nNiger\n• SITUATION\n', text) # manually fix AUG 1996 error

#     return text