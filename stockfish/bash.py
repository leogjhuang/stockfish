import sys

'''
Used to update trade.py with the path containing the trading algorithm followed by any helper files used:
Sample command to run on the command line if the algorithm is contained in ./algorithms/algo1.py:
python3 bash.py ./algorithms/algo1.py
'''

def main():
    # formatStateToJSON()
    compileToTrader()

def compileToTrader():
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

def getRunReturnStatementIndex(lines):
    seenRunFunction = False
    for i, line in enumerate(lines):
        if 'run(self, state: TradingState)' in line:
            seenRunFunction = True
        if seenRunFunction and 'return result' in line:
            return i

    # This should never be called
    return None

# logger.flush(state, orders)
def getLoggerClass():
    loggerFile = './logger.py'
    lines = readLines(loggerFile)
    while len(lines) > 0 and not isClassDeclaration(lines[0]):
        lines.pop(0)
    lines.append('\n\n')
    return lines

def getUtilFunctions():
    utilsFile = './utils.py'
    lines = readLines(utilsFile)
    while len(lines) > 0 and not isPythonFunction(lines[0]):
        lines.pop(0)
    return lines

def isPythonFunction(line):
    return line.find('def') == 0

def getSpaces(count):
    return '' if count <= 0 else ' ' + getSpaces(count - 1)

def modifyDestFile(linesToAdd, destFile):
    loggerFlushLine = getSpaces(8) + 'logger.flush(state, result)\n'
    lines = readLines(destFile)
    renameClassToTrader(linesToAdd)
    lines += linesToAdd + getLoggerClass() + getUtilFunctions()
    lines.insert(getRunReturnStatementIndex(lines), loggerFlushLine)
    write(lines, destFile)

def revertDestFile(destFile):
    lines = readLines(destFile)
    keep = []
    for line in lines:
        if isClassDeclaration(line):
            break
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

def renameClassToTrader(lines):
    newClass = 'Trader'
    for i in range(len(lines)):
        if isClassDeclaration(lines[i]):
            oldClass = getClassNameFromClass(lines[i])
            lines[i] = lines[i].replace(oldClass, newClass, 1)
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

def formatStateToJSON():
    filename = './analysis/tutorial/state.json'
    lines = readLines(filename)
    for i in range(len(lines)):
        if lines[i].find('{') == 0:
            lines[i] = lines[i].strip()
            lines[i] += ',\n'
    write(lines, filename)

if __name__ == "__main__":
    main()
