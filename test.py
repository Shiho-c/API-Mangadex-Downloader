import re 
def sort_pages(list_):
    dict_index = {}
    to_sort = []
    for x in range(len(list_)):
        splitted = list_[x].split(".")[0].split(" ")[1]
        dict_index[splitted] = [x]
        to_sort.append(splitted)
    print(dict(sorted(dict_index.items())))
    to_sort.sort(key = int)
    print(to_sort)

shit = ['0.png', '1.png', '10.png', '11.png', '12.png', '13.png', '14.png', '15.png', '16.png', '2.png', '3.png', '4.png', '5.png', '6.png', '7.png', '8.png', '9.png']
shit.sort(key=lambda f: int(re.sub('\D', '', f)))
print(shit)
