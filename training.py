from behaviors import classical_brownian, geometric_brownian, merton, heston
from agent import agent
from keras.models import load_model
from keras.optimizers import sgd
from keras.models import Sequential
from keras.layers import Dense
import numpy as np
import finance as f
import csv

# Dictionary containing every agent's name and the corresponding object that
# gets instantiated.
agent_config = {
    "classical_brownian": classical_brownian,
    "geometric_brownian": geometric_brownian,
    "merton_jump_diffusion": merton,
    "heston_stochastic": heston
    }

# What periods are we looking at?
periods = [5, 8, 13]

# We define what inputs we want here:
input_config = (
    (f.roc, periods),
    (f.rsi, periods),
    (f.sma, periods),
    (f.wma, periods),
    (f.ema, periods)
)

def get_symbols():
    """Returns all stock symbols in data//symbols.txt as a list."""
    symbol_file = open("data//symbols.txt", "r")
    symbols = symbol_file.readlines()

    corrected = []

    # Correcting for newline delimiters.
    for symbol in symbols:
        corrected.append(symbol.rstrip())

    return corrected

def get_inputs(prices):
    # We append cut and formatted lists here:
    input_lists = []
    
    # GET INDICATORS
    for indicator_tuple in input_config:
        indicator = indicator_tuple[0]
        period_list = indicator_tuple[1]

        for period in period_list:
            indicator_list = indicator(prices, period)
            input_lists.append(indicator_list)

    # After this, we begin to cut all the arrays down to size.
    # max_length is simply an integer defining the maximum size (and therefore the
    # actual size) of each array. The maximum size of ALL arrays needs to be the
    # size of the smallest array so that all elements "line up."
    max_length = len(prices[periods[len(periods) - 1]:])

    # We resize everything in input_lists:
    for input_list in input_lists:
        input_list = input_list[len(input_list) - max_length:]

    # We cut the price list:
    prices = prices[len(prices) - max_length:]

    # This is NOT input_lists! "inputs" contains the actual input matrices that are
    # passed to the agent.
    inputs = []
    
    # Iterate through all input lists, take element at i, and create a numpy array:
    for i in range(max_length):
        a = []
        for input_list in input_lists:
            a.append(input_list[i])

        # This is a placeholder for the number of shares the agent owns.
        a.append(0)
        
        # Now, convert to a numpy array and reshape it so it is acceptable as input.
        npa = np.array(a)
        npa = npa.reshape(1, 16)

        inputs.append(npa)

    return inputs

class training_session:
    
    def __init__(self):

        # "name": behavior instance
        self.agents = {}

        # Internal episode counter.
        self.epcount = 1
        
        # Go through agent_config and create an agent with the corresponding model.
        for key in agent_config.keys():
            
            # Create NN:
            # This is a bad model. I just want to see if instantiating this works.
            # I should also probably clean this up. A lot.
            nn = Sequential()
            nn.add(Dense(20, input_shape=(16,), activation="relu"))
            nn.add(Dense(20, activation="tanh"))
            nn.add(Dense(20, activation="tanh"))
            nn.add(Dense(3, activation="linear"))
            nn.compile(sgd(lr=0.01), "mse")
            
            agent_instance = agent(nn)

            # Warm up the agent and immediately reset:
            # TODO: maybe fix act()? During training we might not necessarily want
            # to act on an actual stock.
            agent_instance.act(1, np.ones((1, 16)), np.ones((1, 16)))
            agent_instance.reset()
            
            behavior_instance = agent_config[key]()
            self.agents[key] = (agent_instance, behavior_instance)

    # Use this for benchmarking.
    def save_agents(self, rewards):
        for agent in self.agents.keys():
            agent_instance = self.agents[agent]
            agent_instance.get_nn().save("models//" + agent + "{reward: " + str(rewards[agent]) + "}.h5")
            
    def get_agents(self):
        return self.agents
    
    def run(self):
        """Performs a single simulation of all behaviors and has agents act correspondingly."""

        # These are the losses for each model. Should probably be displayed in Dash later on.
        info_string = str(self.epcount) + "\t"
        
        for key in self.agents.keys():
            agent_instance = self.agents[key][0]
            behavior_instance = self.agents[key][1]
            
            prices = behavior_instance.step(690)
            inputs = get_inputs(prices)
            
            # Now, we iterate through all the inputs and make the model act on the input and
            # receive information about the next state. Internally, the agent also updates
            # the number of shares it has as one of the inputs to the NN.
            for i in range(len(inputs) - 1):
                state = inputs[i]
                next_state = inputs[i + 1]
                agent_instance.act(prices[i], state, next_state)

            # Get batch loss and add that to the string too.
            batch_loss = agent_instance.train()
            info_string += "l: " + np.array2string(batch_loss) + "\t"

        # TODO: text formatting of output
        print(info_string)
        
        # Update episode count.
        self.epcount += 1

    def get_stats(self):
        stats = {}
        for key in self.agents.keys():
            agent_instance = self.agents[key][0]
            stats[key] = agent_instance.get_stats()

        return stats

    def reset(self):
        for key in self.agents.keys():
            agent_instance = self.agents[key][0]
            agent_instance.reset()

    def test(self):
        """Iterates through the test dataset and collects the rewards of each agent."""

        symbols = ["AAPL"] #get_symbols()
        total_rewards = {}
        
        for key in self.agents.keys():
            agent_instance = self.agents[key][0]
            total_reward = 0
            for symbol in symbols:
                
                prices = []
                
                with open("data//intraday//" + symbol + ".csv", "r") as file:
                    reader = csv.reader(file)
                    next(file)

                    for row in reader:
                        prices.append(float(row[5]))

                prices = np.array(prices)
                inputs = get_inputs(prices)
                
                for i in range(len(inputs) - 1):
                    state = inputs[i]
                    next_state = inputs[i + 1]
                    reward, true_reward = agent_instance.act(prices[i], state, next_state)
                    total_reward += true_reward
                agent_instance.reset()
                
            total_rewards[key] = total_reward
            print(key + ":\t" + str(round(total_reward, 2)))

        return total_rewards

##tr = training_session()
##
##for i in range(10):
##    tr.run()
##    print(tr.get_stats())
##    tr.reset()
##
##tr.test()
