import numpy as np
import ctypes
from numpy.ctypeslib import ndpointer
import random
import os

#so_file = "/home/ivanpereira/WaveMonster/WaveMonster/SpaceInvaders/src/Space.so"
#so_file = "C:/Users/55989/Google Drive/evo/SpaceInvaders/src/Space.so"
so_file =  os.path.abspath("Space.so")
SpaceC = ctypes.CDLL(so_file)
print(type(SpaceC))

def set_weights(arr):
	fn = SpaceC.set_nn_weights
	fn.restype = None
	fn.argtypes = [ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
	fn(arr)

def play():
	#Sempre inicie as estruturas de dados
	SpaceC.nn_init()
	a = np.zeros(1211)
	set_weights(a)
	#train the neural network for 1 iteration
	SpaceC.nn_train(1,3)

def random_train():
	SpaceC.nn_init()
	best_mean_rew = -9999
	best_weights = np.zeros(1211)
	weights = np.random.rand(1211) 
	for i in range(10000):
		set_weights(weights)
		#train the neural network for 1 iteration
		mean_rew = SpaceC.nn_train(3,20)
		print("mean_rew: ",mean_rew)
		if(mean_rew>best_mean_rew):
			best_mean_rew = mean_rew
			best_weights = weights
			print("Best reward now: ",best_mean_rew)
		else:
			#move the best weights found in a random direction
			random_dir = np.random.random_sample(1211) -0.5
			weights = best_weights + random_dir

random_train()
#play()