# BROKEN
class virtual_market():

    # List to keep track of transactions performed within this environment.
    transactions = []

    # List of agents containing the agent itself and its total profit. 
    agents = []

    # Contains the data for all 300 stocks. Subject to change; might be too big
    # to contain within a single list.
    data = []

    def __init__(self, agents, data):
        self.data = data

        for agent in agents:
            self.agents.append([agent, 0])

    def get_data():
        return self.data

    def get_agents():
        return self.agents

    def get_transactions():
        return self.transactions


