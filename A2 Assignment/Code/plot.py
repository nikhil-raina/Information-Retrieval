
import matplotlib.pyplot as plt


def readIndex(filename):
    count = {}
    indexfile = open(filename)
    for line in indexfile.readlines():
        tokens = line.replace('\n','').split('\t')
        if tokens[0] in count.keys():
            count[tokens[0]] += int(tokens[3])
        else:
            count[tokens[0]] = int(tokens[3])
    count = {k : v for k, v in sorted(count.items(), key = lambda item: item[1], reverse=True)}    
    plt.plot([_ for _ in range(0, len(count))], list(count.values()), linewidth=3.0)
    plt.title('Word vs Word Frequency')
    plt.xlabel('Word Rank ->')
    plt.ylabel('Word Frequency ->')
    plt.axis([0, max(count.values())/5, 0, len(count)/8])
    plt.show()


if __name__ == "__main__":
    readIndex('index.tsv')