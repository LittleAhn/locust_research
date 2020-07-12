import pdfplumber
import re

def clean_page(file_path):
    pdf = pdfplumber.open(file_path)
    final_txt = []
    # determine if old style
    year = int(file_path[-4:])
    old_style = (1997 <= year <= 2017)
    #if year == 1996:
        # JULY TO DECEMBER 1996 IS OLD STYLE!!!
        # or don't  even feed anything older to this...
    #print("old style? ", old_style)
    for i, page in enumerate(pdf.pages):
        left, right = get_left_side(page, i, old_style), get_right_side(page, i, old_style)
        #right = get_right_side(page)
        clean_left = clean_text(left)
        #print("page number is: ", i)
        #print("right is: ", right)
        if right:
            clean_right = clean_text(right)
        else: # empty right side
            clean_right = ""
        final_txt.append(clean_left)
        final_txt.append(clean_right)
    return "\n".join(final_txt) # write this to a .txt file

    #with pdfplumber.open(file_path) as pdf:
        #page = pdf.pages[pg_num]
        #for page in pdf.pages:
            #left, right = get_left_side(page), get_right_side(page)
            #right = get_right_side(page)
            #clean_left = clean_text(left)
            #clean_right = clean_text(right)
    #return (clean_left, clean_right)

def clean_text(text): # make this prettier
    #cleaned = single_word(text)
    #cleaned = two_word(cleaned)
    #cleaned = many_countries(cleaned)
    #return cleaned
    return many_countries(two_word(single_word(text))) # is this clean or gross

def get_left_side(page, pg_num, old_style):
    x0 = 0
    #print("old_style", old_style)
    #print("page num: ", pg_num)
    if old_style: 
        if pg_num % 2 == 0:
            x1 = page.width // 2 - 20
        else:
            x1 = page.width // 2 + 20
    else:
        x1 = page.width // 2
    bottom = page.height - 70
    top = 0
    return page.crop((x0, top, x1, bottom)).extract_text()


def get_right_side(page, pg_num, old_style):
    if old_style:
        if pg_num % 2 == 0:
            x0 = page.width // 2 - 18
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
        if re.match(r'[A-Z]  [A-Z]', line):
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
        if re.match(r'[A-Z] ( [A-Z]|  .[A-Z] )?,', line):
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
                if char == "UAE":
                    rv += char + " "
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