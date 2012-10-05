import random

# Global book functions

def _is_valid_isbn(isbn):
    if len(isbn) == 13:
        return _is_valid_isbn13(isbn)
    elif len(isbn) != 10:
        return False
    else:
        last = 10 if isbn[-1] in ["X", "x"] else int(isbn[-1])
        weighted = [int(num)*weight for num, weight in
                    zip(isbn[:-1], reversed(range(2, 11)))]
        return (sum(weighted) + last) %11==0

def _is_valid_isbn13(isbn13):
    total = sum([int(num)*weight for num, weight in zip(isbn13, (1,3)*6)])
    ck = 10-(total%10)
    return ck == int(isbn13[-1])

# Ipsum ISBN to populate DB functions

def ipsum_isbn(sett):

    base = sett['base'][:]
    isbn_l = []

    for n in range(sett['count']):
        # Toss in some random nums
        isbn = base[:]
        for dix in range(len(sett['base']), sett['digits']-1):
            isbn.append(random.randint(0,9))
        isbn_l.append(isbn)

    # Compute the check digit & append
    isbn_str_l = []
    for i in isbn_l[:]:
        if sett['digits'] == 10:
            cs = sum([(sett['digits']-ix)*i[ix] for ix in range(sett['digits']-1)])
            cs = (11 - cs) % 11
            if cs == 10:
                cs = "X"
        else:
            w = [1 + 2*(x & 1) for x in range(12)]
            cs = sum([w[ix]*i[ix] for ix in range(12)]) % 10
            cs = (10 - cs) % 10
            if cs == 10:
                cs = 0
        i.append(cs)
        isbn_str_l.append(''.join(map(str, i)))

    return isbn_str_l
