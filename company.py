import random
class companies:
    companiess = {}

    def __init__(self, name, values):
        vals = {}
        indicators = ["P/E", "P/S", "Price to Cash Flow",
                      "Ent Val to EBITDA", "Ent Val to Sales", "EPS",
                      "Rev/Employee", "Asset Turnover", "Operating Margin",
                      "Net Profit Margin", "Return on Invested Capital",
                      "D/E", "Debt-Capital", "Total Debt to Total Assets",
                      "Interest Coverage Ratio", "Sector"]
        self.values = values
        for i in range(0, len(indicators)):
            vals[indicators[i]] = values[i]

        self.companiess[name] =  vals

    def getCompany(self, compname):
        return self.companiess[compname]

    def getIndicator(self, compname, indicator):
        return self.companiess[compname][indicator]

    def getValues(self):
        return self.values

    def getSector(self, sector):
        sect = []
        keys = self.convert_to_list(self.companiess)
        for i in range(0, len(keys)):
            if self.companiess[keys[i]]["Sector"] == sector:
                sect.append(keys[i])
        return sect
    
    def setSector(self, compname, sector):
        self.companiess[compname]["Sector"] = sector

    def getSectorIndic(self, sector, indicator):
        sectind = []
        listkeys = self.convert_to_list(self.companiess)

        for i in range(0, len(listkeys)):
            if self.companiess[listkeys[i]]["Sector"] == sector:
                compind = []
                compind.append(listkeys[i])
                compind.append(self.companiess[listkeys[i]][indicator])
                sectind.append(compind)

        return sectind

    def convert_to_list(self, dict):
        keys = []
        for i in dict.keys():
            keys.append(i)
        return keys
