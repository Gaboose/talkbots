import json, sys, os

if __name__ == '__main__':
    fname = sys.argv[1]

    with open(fname) as f:
        data = json.load(f)
    lst = data['conversations']

    lst1 = []
    lst2 = []
    for i, el in enumerate(lst):
        if i % 2 == 0:
            lst1.append(el)
        else:
            lst2.append(el)
    
    fname, ext = os.path.splitext(fname)
    data['conversations'] = lst1
    with open(fname + '1' + ext, 'w') as f:
        json.dump(data, f, indent=2)
    
    data['conversations'] = lst2
    with open(fname + '2' + ext, 'w') as f:
        json.dump(data, f, indent=2)