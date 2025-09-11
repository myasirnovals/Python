from colorama import Fore, Back

import colorama

colorama.init(autoreset=True)
print(Fore.BLUE + Back.YELLOW + "Hello World" + Fore.YELLOW + Back.BLUE + "I am a color print")
print(Back.CYAN + "Hello World")
print(Fore.RED + Back.GREEN + "Hello World")
