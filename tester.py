from keras.models import load_model
from keras import optimizers
import h5py
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import TensorBoard
import numpy

input_training_matrix = numpy.load("data\input_training.npy")
output_training_matrix = numpy.load("data\output_training.npy")
input_testing_matrix = numpy.load("data\input_testing.npy")
output_testing_matrix = numpy.load("data\output_testing.npy")


print("\nIN_TEST SHAPE:\t\t" + str(input_testing_matrix.shape))
print("IN_TEST DIM:\t\t" + str(input_testing_matrix.ndim))
print("\nOUT_TEST SHAPE:\t" + str(output_testing_matrix.shape))
print("OUT_TEST DIM:\t\t" + str(output_testing_matrix.ndim))
"""
model = Sequential()

# Input layer!
model.add(LSTM(16, input_shape=(14, 4), return_sequences=True))
model.add(Dropout(0.2))

# Hidden layer:
model.add(LSTM(16))
model.add(Dropout(0.2))
model.add(Dense(16))
model.add(Dense(16))

# Output:
model.add(Dense(4, activation="softmax"))
model.compile(loss="categorical_crossentropy", optimizer="adam")


model.summary()

print("\nTRAINING:")

model.save("models/Redone_model.h5")
"""

# TESTING
# We take the currently-unused testing dataset and feed it into the neural network. We perform
# no weight changes, since it is necessary to simply quantify the network's performance. To
# do so, the network is fed sequences that it has never seen before, and is expected to yield
# an accurate result, that being the index of the category within its vocabulary.

# honestly this code is a meme at this point
# Redone_model1.h5 is my hero rn
model = load_model("models/Redone_model1.h5")

#model.fit(input_training_matrix, output_training_matrix, epochs=500, batch_size=200)
#model.save("models/Redone_model3.h5")

# TESTING:
testing_size = 350
correct = 0

for i in range(350):
    testing_input = input_testing_matrix[i]

    # We reshape the input matrix back into a 1-dimensional sequence, meaning it has 1 row and len(testing_input)
    # columns inside it. This is not a list, but an operable matrix that the neural network can interpret as
    # a series of inputs.
    x = numpy.reshape(testing_input, (1, 14, 4))

    # The model predicts an output for the given sequence.
    prediction = model.predict(x)

    # We then retrieve the actual value.
    actual = numpy.argmax(output_testing_matrix[i])

    index = numpy.argmax(prediction)

    print("PRED: " + str(prediction) + "\tACT: " + str(actual))

    if actual == index:
        correct += 1

print("CORRECT: " + str(correct))
print("ACC: " + str(correct/float(testing_size)*100) + "%")
