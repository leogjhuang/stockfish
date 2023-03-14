import sys

'''
Used to update trade.py with the path containing the trading algorithm followed by any helper files used: 
Sample command to run on the command line if the algorithm is contained in ./algorithms/algo1.py: 
python3 bash.py ./algorithms/algo1.py ./utils.py
'''

def main():
    if len(sys.argv) < 2:
        print('Please provide at least one path (example: ./algorithms/algo0.py)')
        return
    destFile = './trader.py'
    revertDestFile(destFile)
    linesToAdd = []
    for i in range(1, len(sys.argv)):
        srcFile = sys.argv[i]
        lines = filterSrcFile(srcFile)
        if len(lines) == 0:
            print('File ' + srcFile + ' has no class')
        else:
            linesToAdd += lines
            linesToAdd.append('\n\n')
    modifyDestFile(linesToAdd, destFile)

def filterSrcFile(srcFile):
    lines = readLines(srcFile)
    while len(lines) > 0 and not isClassDeclaration(lines[0]):
        lines.pop(0)
    return lines

def modifyDestFile(linesToAdd, destFile):
    lines = readLines(destFile)
    classLine = linesToAdd[0]
    className = getClassNameFromClass(classLine)
    updateClassInstantiation(lines, className)
    lines += linesToAdd
    write(lines, destFile)

def revertDestFile(destFile):
    lines = readLines(destFile)
    seenClass = False
    keep = []
    for line in lines:
        if isClassDeclaration(line):
            if seenClass:
                break
            seenClass = True
        keep.append(line)
    write(keep, destFile)

def isClassDeclaration(line):
    return line.find('class') == 0

def updateClassInstantiation(lines, className):
    for i in range(len(lines)):
        if 'run(self, state: TradingState)' in lines[i]:
            nextLine = lines[i + 1]
            currentClassName = getClassNameFromInstance(nextLine)
            lines[i + 1] = lines[i + 1].replace(currentClassName, className, 1)
            return

def getClassNameFromClass(classLine):
    return classLine[classLine.find('class') + 5:classLine.find(':')].strip()

def getClassNameFromInstance(classLine):
    return classLine[classLine.find('=') + 1:classLine.find('(')].strip()

def readLines(f):
    with open(f, 'r') as file:
        return file.readlines()

def write(lines, f):
    with open(f, 'w') as file:
        for line in lines:
            file.write(line)

if __name__ == "__main__":
    main()

