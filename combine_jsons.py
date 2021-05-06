from os import walk

def main():
    files = []
    for (_, _, filenames) in walk('.'):
        files.extend(filenames)
        break

    text = []
    for f in files:
        if f.endswith('.json') and not f.startswith('combined'):
            file = open(f)
            text.append(file.read())

    toprint = '{'
    for t in text:
        toprint += t[1:-1]
        toprint += ','
    toprint = toprint[:-1]
    toprint += '}'
    combined = open('combined.json', 'w')
    combined.write(toprint)
    #json.dump(toprint, combined)
    combined.close()

if __name__ == '__main__':
    main()