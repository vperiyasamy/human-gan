import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys
import numpy as np
import math

files = os.listdir(sys.argv[1]) # input directory

def error(guess, actual):
	guess = np.array(guess)
	actual = np.array(actual)

	residual = np.subtract(actual, guess)

	# euclidean distance
	euc_distance = math.sqrt( (actual[0] - guess[0])**2 + (actual[1] - guess[1])**2 + (actual[2] - guess[2])**2 + (actual[3] - guess[3])**2 )

	# RMS error
	rms = np.sqrt(np.mean(np.square(residual)))

	# relative error
	relative = np.linalg.norm(residual, ord=None) / np.linalg.norm(actual, ord=None)

	return euc_distance, rms, relative


# first lets parse these files
rounds = []
euc_errors = []
rms_errors = []
rel_errors = []
probabilities = []

for file in files:
	with open(sys.argv[1] + '/' + file) as f:
		lines = f.readlines()

	bp = lines.index('\n') # breakpoint between probabilities and coordinates

	probs = [float(x.strip()) for x in lines[0:bp]]

	guess = [float(x) for x in lines[bp+1].strip().split('\t')]
	actual = [float(x) for x in lines[bp+2].strip().split('\t')]

	rounds.append(len(probs)) # which experiment is this

	err = error(guess, actual) # error for this experiment
	euc_errors.append(err[0])
	rms_errors.append(err[1])
	rel_errors.append(err[2])

	probabilities.append(probs)

# sort based on iterations
error_sort = [list(x) for x in zip(*sorted(zip(rounds, euc_errors, rms_errors, rel_errors), key=lambda pair: pair[0]))]

# now lets plot error
figure = plt.figure()

plt.plot(error_sort[0], error_sort[1], '--k', label='Euclidean Distance')
plt.plot(error_sort[0], error_sort[2], '-.k', label='RMS Error')

plt.title('Error measures between guessed and actual rectangle distributions')
plt.xlabel('Iterations')
plt.ylabel('Error')
plt.legend(loc='upper right')
plt.show()

figure.savefig(sys.argv[1] + '_error.png', dpi=300, bbox_inches='tight')

# relative error 
figure = plt.figure()
plt.plot(error_sort[0], error_sort[3], ':k')
plt.title('Relative error between guessed and actual rectangle distributions')
plt.xlabel('Iterations')
plt.ylabel('Relative Error')
plt.show()

figure.savefig(sys.argv[1] + '_rel_error.png', dpi=300, bbox_inches='tight')

# now lets look at probabilities
prob_sort = [list(x) for x in zip(*sorted(zip(rounds, probabilities), key=lambda pair: pair[0]))]

figure = plt.figure()

x = np.linspace(1, prob_sort[0][-1], prob_sort[0][-1])
y = np.array(prob_sort[1][-1])

plt.plot(x, y, '-k')
plt.title('Predicted probabilities of point set guesses over number of iterations')
plt.xlabel('Iterations')
plt.ylabel('Predicted Probability of Guess')
plt.show()

figure.savefig(sys.argv[1] + '_prob.png', dpi=300, bbox_inches='tight')


