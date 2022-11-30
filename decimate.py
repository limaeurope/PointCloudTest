import random

if __name__ == "__main__":
    f = open("Data/Table.csv", "r")

    with open("Data/Table3.csv", "w") as fResult:
        for row in f.readlines():
            if random.random() < 0.1:
                fResult.write(row)