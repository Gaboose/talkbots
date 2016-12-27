import sys, re, json

if __name__ == '__main__':
    fname = sys.argv[1]
    with open(fname) as f:
        text = f.read()
    
    # remove non-dialog lines
    text = re.sub(r'\n(?:\*\*\*|quit:|join:|-->|<--|---|\* Quit|\* Join)[\S\s]*?(?=\n)', '', text)

    with open('interm1.txt', 'w') as f:
        f.write(text)

    # extract dialog lines
    text = re.sub(r'\n(?:<.+?> ?|.+?> |\(.+?\) |-.+?- |\[.+?\] |\* ?|[^\n<>#]+?: ?(?!\n)| *(?=[\w"\.]))([\s\S]*?)(?=\n|$)', r'\n"\1",', text)

    with open('interm2.txt', 'w') as f:
        f.write(text)

    # escape quotes (assumes all not-to-escape quotes will either come after a newline or be followed by a comma-newline)
    text = re.sub(r'([^\n])"(?!,\n)', r'\1\\"', text)

    with open('interm3.txt', 'w') as f:
        f.write(text)
    
    # replace seperators between conversations
    text = re.sub(r'(?:^|,\s+)#[^\n]*(?:\s+#[^\n]*)*\s+', r'\n],\n[\n', text)

    with open('interm4.txt', 'w') as f:
        f.write(text)
    
    text = text[text.find('"'):text.rfind(',')]
    text = '{\n"conversations":[\n[\n' + text + '\n]\n]\n}'

    with open('interm5.txt', 'w') as f:
        f.write(text)
    
    # assert that text decodes to json
    data = json.loads(text)

    with open('corpus.json', 'w') as f:
        json.dump(data, f, indent=2)
    