class real_company:
    indicators = ["P/E", "P/S", "Price to Cash Flow",
                  "Ent Val to EBITDA", "Ent Val to Sales", "EPS",
                  "Rev/Employee", "Asset Turnover", "Operating Margin",
                  "Net Profit Margin", "Return on Invested Capital",
                  "D/E", "Debt-Capital", "Total Debt to Total Assets",
                  "Interest Coverage Ratio", "Sector"]
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def getCompany(self):
        return self.name

    def getIndicator(self, indicator):
        i = self.indicators.index(indicator)
        return self.values[i]

    def getValues(self):
        return values

    def getSector(self):
        i = len(self.indicators)-1
        return self.values[i]

    def setCompany(self, name):
        self.name = name

    def setIndicator(self, indicator, val):
        i = self.indicators.index(indicator)
        self.values[i] = val

    def setValues(self, values):
        self.values = values

    def setSector(self, sector):
        self.values[len(self.indicators)-1] = sector
