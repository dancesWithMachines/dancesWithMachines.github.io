import sys
import os

NOT_ALLOWED_CHARS = "()!@$%^&*()=+[]:;\"'|<>,.?/"

path = sys.argv[1]

if (os.path.isfile(path) == False or path.endswith(".md") == False):
    print("Not a valid file.")
    exit(1)

output = open("OUTPUT.md", "w")

path = os.path.abspath(path)

content = open(path, 'r')
counterSmall = counterMedium = counterLarge = 0

for line in content.readlines():
    if line.startswith('#') == False:
        continue

    headerSize = line.count('#')

    if headerSize > 3:
        continue

    line = line.strip('\n')

    name = line[headerSize + 1:]
    link = '#' + name.lower().replace(' ','-')

    for letter in NOT_ALLOWED_CHARS:
        link = link.replace(letter, '')

    tab = '\t' * (headerSize - 1)

    if headerSize == 1:
        counterLarge += 1
        counterMedium = counterSmall = 0
        currentCounter = counterLarge

    if headerSize == 2:
        counterMedium += 1
        counterSmall = 0
        currentCounter = counterMedium

    if headerSize == 3:
        counterSmall += 1
        currentCounter = counterSmall

    line = tab + str(currentCounter) + ". [" + name + "](" + link + ")"
    print(line)
    output.write(line + '\n')
output.close()


