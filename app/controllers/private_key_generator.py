from random import randint

class PrivateKeyGenerator ():
    def __init__(self, map = None):
        if map is None:
            self.map = "a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 1 2 3 4 5 6 7 8 9 0"
            self.map = self.map.split(" ")
    
    def generate(self, level = 1, perLevel = 5):
        level = max(level, 1)
        perLevel = max(perLevel, 1)
        currentLevel = 0
        key = ""

        while currentLevel < level:
            currentPerLevel = 0
            perLevelChars = ""

            while currentPerLevel < perLevel:
                randomKeyLetterIndex = randint(0, len(self.map) - 1)
                randomKeyLetter = self.map[randomKeyLetterIndex]

                perLevelChars += randomKeyLetter

                currentPerLevel += 1

            key += perLevelChars

            currentLevel += 1

        return key

if __name__ == "__main__":
    gen = PrivateKeyGenerator()
    pkey = gen.generate(level = 6, perLevel = 5)
    print(pkey)