import realcompany
import random

class comparison:

    def __init__(self):
        self.company_list = []

    def add_comp(self, name):
        self.company_list.append(name)

    def sortHigh(self, sector, indicator):
        self.tempval= []
        for i in range (0, len(self.company_list)):
            if self.company_list[i].getSector() == sector:
                self.tempval.append(self.company_list[i].getIndicator(indicator))
        highSort = sorted(self.tempval)
        return highSort

    def sortLow(self):
        self.tempval = []
        for i in range (0, len(self.company_list)):
            if self.company_list[i].getSector() == sector:
                self.tempval.append(self.company_list[i].getIndicator(indicator))
        self.lowSort = sorted(self.tempval)
        self.lenval = len(self.tempval)
        for i in range(0, lenval-1):
            self.temp = self.lowSort[i]
            self.lowSort[i]=self.lowSort((self.lenval-1-i))
            self.values[lenval-1-i] = self.temp
        return lowSort

indices = []
for i in range(0, 16):
    t = random.Random()
    num = t.randrange(0, 11)
    indices.append(num)

comp1 = realcompany.real_company("Test1", indices )
comp1.setSector("finance")
indices2 = []
for i in range(0, 16):
    t = random.Random()
    num = t.randrange(0, 11)
    indices2.append(num)
comp2 = realcompany.real_company("Test2", indices2)
comp2.setSector("finance")

test1 = comparison()
test1.add_comp(comp1)
test1.add_comp(comp2)
print (test1.sortHigh("finance", "P/E"))
