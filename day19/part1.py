from intcode import IntCodeProgram

class TractorScanner:
    def __init__(self):
        with open("input.txt", "r") as f:
            program = IntCodeProgram(list(map(int, f.read().strip().split(","))))
        self._program = program

    def query(self, y, x):
        proc = self._program.process()
        proc.send(x)
        proc.send(y)
        return proc.recv() == 1

    def scan(self, H, W):
        total = 0
        for y in range(H):
            for x in range(W):
                if self.query(y, x):
                    print("#", end="")
                    total += 1
                else:
                    print(".", end="")
            print()
        return total

scanner = TractorScanner()
print(scanner.scan(50, 50))
        
