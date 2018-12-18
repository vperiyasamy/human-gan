import argparse, os, sys, random, json
import numpy as np
import tensorflow as tf

from flask import Flask, render_template, request, redirect, Response, app

from keras.models import Sequential, Model
from keras.layers import Dense, Input

global model, graph

#############################################################
# Global Parameters
#############################################################
iters = 0
max_iters = 20
probabilities = [] # bookkeeping

#############################################################
# Discriminator Neural Network
#############################################################

# define parameters
epochs = 200
batch = 10
grid_size = 100
target_width = 50
num_samples = 1000

# first define a target concept (rectangle)
target_x = np.random.random_integers(0, grid_size - target_width) # top left x
target_y = np.random.random_integers(0, grid_size - target_width) # top left y
print('target concept: square anchored at (%d, %d) with width %d' % (target_x, target_y, target_width))

def test_point(point):
	if point[0] >= target_x and point[0] <= target_x + target_width:
		if point[1] >= target_y and point[1] <= target_y + target_width:
			return True
	return False

def test_sample(sample):
	if test_point(sample[0]) and test_point(sample[1]) and test_point(sample[2]) and test_point(sample[3]):
		# all points lie within target
		return 1
	return 0

# next generate some data
X = []
y = []
print('generating data...')

# generate random points
for i in range(num_samples):

	if i % 2 == 0: # random points
		sample = np.random.random_integers(0, 100, size=(4, 2))
		
		X.append(np.reshape(sample, 8))
		y.append(test_sample(sample))

	else: # guaranteed good points
		sample = np.zeros((4,2))
		x_coords = np.random.random_integers(target_x, target_x + target_width, size=4)
		y_coords = np.random.random_integers(target_y, target_y + target_width, size=4)
		for j in range(4):
			sample[j, 0] = x_coords[j]
			sample[j, 1] = y_coords[j]
		
		X.append(np.reshape(sample, 8))
		y.append(test_sample(sample))


X = np.array(X)
y = np.array(y)
print('number of samples: %d' % num_samples)
print('number of good samples: %d' % np.count_nonzero(y))

# now train our model
print('training discriminator...')
model = Sequential()
model.add(Dense(16, input_shape=(8,), activation='relu'))
model.add(Dense(16, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam')
model.fit(X, y, epochs=epochs, verbose=0)

graph = tf.get_default_graph()
print('ready for queries')


def save_experiment(probabilities, guess):
	filename = str('results/' + str(os.getpid()) + '_' + str(iters) + '.txt')

	with open(filename, 'w') as f:
		for p in probabilities:
			f.write('%f\n' % p)

		f.write('\n')

		f.write('%f\t%f\t%f\t%f\n' % (guess[0], guess[1], guess[2], guess[3]))
		f.write('%f\t%f\t%f\t%f\n' % (target_x, target_y, target_x + target_width, target_y + target_width))

#############################################################
# Server
#############################################################
app = Flask(__name__)

@app.route('/')
def output():
	global max_iters
	# serve index template
	return render_template('index.html', title='The GAN Project', probability=('Start guessing your %d points!' % max_iters))

@app.route('/query', methods = ['POST'])
def query():
	global iters, max_iters, probabilities

	if iters >= max_iters:
		return 'You have used all of your guesses, please guess a target distribution!'

	# read json + reply
	data = request.get_json()
	result = ''

	sample = []
	for item in data:
		# loop over every row
		result += '(' + str(float(item['x']) / 6) + ', ' + str(float(item['y']) / 6) + ')\n'

		sample.append(float(item['x']) / 6) # rescale points
		sample.append(float(item['y']) / 6) # to 0 - 100

	new_x = []
	new_x.append(np.array(sample))
	new_x = np.array(new_x)

	with graph.as_default():
		prediction = model.predict_proba(new_x)[0]
	result += str(prediction) + '\n'

	probabilities.append(prediction) # save probability

	print(result, file=sys.stdout, flush=True)
	sys.stdout.flush()

	iters += 1

	return 'Iteration %d - Probability of being in target square: %s' % (iters, str(prediction))

@app.route('/guessdistribution', methods = ['POST'])
def guess_distribution():
	global probabilities
	# read json + reply

	data = request.get_json()
	result = ''

	guess = []
	for item in data:
		# loop over every row
		result += '(' + str(float(item['x']) / 6) + ', ' + str(float(item['y']) / 6) + ')\n'

		guess.append(float(item['x']) / 6) # rescale points
		guess.append(float(item['y']) / 6) # to 0 - 100


	message = 'Guessed (%f, %f) to (%f, %f)\n Actual (%f, %f) to (%f, %f)\n' % (guess[0], guess[1], guess[2], guess[3], target_x, target_y, target_x + target_width, target_y + target_width)

	# save results
	print('saving results...')
	save_experiment(probabilities, guess)

	print(result, file=sys.stdout, flush=True)
	sys.stdout.flush()

	return message


if  __name__ == '__main__':
	print('starting vish\'s gan server...')
	
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('--iters', help='number of iterations to let human guess', type=int, default=20)
	max_iters = parser.parse_args().iters

	# run the web server
	app.run('0.0.0.0', 8000)