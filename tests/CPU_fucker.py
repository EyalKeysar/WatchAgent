import math

def heavy_computation():
    result = 0
    for i in range(100000):
        result += math.sqrt(i) * math.sin(i)
    return result

def main():
    while True:
        heavy_computation()

if __name__ == "__main__":
    main()
