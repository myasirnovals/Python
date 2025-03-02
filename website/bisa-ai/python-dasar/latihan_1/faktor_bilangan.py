def faktor_bilangan(x):
    if x <= 1:
        x = 1
        print(x)
    else:
        n = 2
        while n > 1 and x != 1:
            if x % n == 0:
                print(x)
                x = x / n
            else:
                n = n + 1
        
faktor_bilangan(100)
