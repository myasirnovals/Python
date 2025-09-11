from currency_converter import CurrencyConverter

pycurrency = CurrencyConverter()

amount = float(input('enter your money: '))
change = input('enter the change: ')
changer = input('enter the changer: ')

total = pycurrency.convert(amount, change, changer)
print(str(amount) + change + ' is ' + str(total) + changer)
