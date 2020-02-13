import numpy as np
import ctypes
from numpy.ctypeslib import ndpointer
import random
import os
import operator

from time import time
import copy
from math import sqrt, log
import itertools
mob_number = 3 # opponents only
enemy_acts = [list(i) for i in itertools.product([0, 1, 2, 3, 4], repeat=mob_number)]

def ucb(node):
    return node.value / node.visits + 10*sqrt(log(node.parent.visits)/node.visits)

def avg(node):
    return node.value / node.visits

class Node:
    def __init__(self, parent, action):
        self.parent = parent
        self.action = action
        self.children = []
        self.explored_children = 0
        self.visits = 0
        self.value = 0
        self.nv_value = 0

class NN_GAME():
	def __init__(self):
		self.so_file =  os.path.abspath("src/Space.so")
		self.SpaceC = ctypes.CDLL(self.so_file)
		print(type(self.SpaceC))
		self.SpaceC.nn_init()
		a=( ctypes.c_int*3) (0,0,0)
		self.SpaceC.step(1,a)
		self.SpaceC.print_matrix()	

		print("Training...")
		#self.random_train()
		print("Training over!!")

	def set_weights(self,arr):
		fn = self.SpaceC.set_nn_weights
		fn.restype = None
		fn.argtypes = [ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		fn(arr)

	def random_train(self):
		best_mean_rew = -9999
		best_weights = np.zeros(1211)
		weights = np.random.rand(1211) 
		for i in range(1000):
			self.set_weights(weights)
			#train the neural network for 3 iteration, 20 steps
			mean_rew = self.SpaceC.nn_train(3,20)
			print("mean_rew: ",mean_rew)
			if(mean_rew>best_mean_rew):
				best_mean_rew = mean_rew
				best_weights = weights
				print("Best reward now: ",best_mean_rew)
			else:
				#move the best weights found in a random direction
				random_dir = np.random.random_sample(1211) -0.5
				weights = best_weights + random_dir

		#set best weights		
		self.set_weights(best_weights)

	def get_positions(self):
		#get enemy ships positions
		gm = self.SpaceC.get_enemy_positions
		gm.restype = None
		gm.argtypes = [ctypes.c_size_t,ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		enemy_coords = np.empty(6)#2*number of enemies
		gm( enemy_coords.size, enemy_coords)
		#print("enemy_coords:",enemy_coords)

		#get player ship position
		gm = self.SpaceC.get_player_positions
		gm.restype = None
		gm.argtypes = [ctypes.c_size_t,ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		player_coord = np.empty((2))#2 coordinates
		gm( player_coord.size, player_coord)
		#print("player_coord:",player_coord)

		#get shoots positions
		gm = self.SpaceC.get_shoots_positions
		gm.restype = None
		gm.argtypes = [ctypes.c_size_t,ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		shoots_coords = np.zeros((101))#max shoots 50 * 2. Last position tell us the number of shoots
		max_shoots = gm( shoots_coords.size, shoots_coords)
		#print(shoots_coords)
		#print('max_shoots:',max_shoots)
		return enemy_coords,player_coord,shoots_coords


	def play_nn(self,act):
		#Sempre inicie as estruturas de dados
		
		#random enemy actions
		#enemy_actions = np.random.randint(5, size=3)
		enemy_actions = np.zeros(3)

		#get enemies actions from C
		nn_act = self.SpaceC.nn_act
		nn_act.restype = None
		nn_act.argtypes = [ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		nn_act( enemy_actions)
		
		#print("Enemy actions: ",enemy_actions)

		en_acts=( ctypes.c_int*3) (int(enemy_actions[0]),int(enemy_actions[1]),int(enemy_actions[2]))
		r = self.SpaceC.step(act,en_acts)
		#print("Reward: ",r)

		
		#self.SpaceC.print_matrix()	
		enemy_coords,player_coord,shoots_coords = self.get_positions()

		return r,enemy_actions,enemy_coords,player_coord,shoots_coords

	def move_shoots_only(self):
		#Sempre inicie as estruturas de dados
	
		enemy_actions = np.zeros(3)
		for i in range(len(enemy_actions)):
			enemy_actions[i]=9999
		

		en_acts=( ctypes.c_int*3) (int(enemy_actions[0]),int(enemy_actions[1]),int(enemy_actions[2]))
		r = self.SpaceC.step(9999,en_acts)

		#get enemy ships lifes
		gm = self.SpaceC.get_enemies_lifes
		gm.restype = None
		gm.argtypes = [ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		enemies_life = np.empty(3)#2*number of enemies
		gm( enemies_life)

		#get player ship life
		gm = self.SpaceC.get_player_life
		gm.restype = None
		gm.argtypes = [ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		player_life= np.empty((1))#2 coordinates
		gm(  player_life)

		#get shoots positions
		gm = self.SpaceC.get_shoots_positions
		gm.restype = None
		gm.argtypes = [ctypes.c_size_t,ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		shoots_coords = np.zeros((101))#max shoots 50 * 2. Last position tell us the number of shoots
		max_shoots = gm( shoots_coords.size, shoots_coords)

		#self.SpaceC.print_matrix()	

		return r,enemies_life,player_life,shoots_coords


	def play_mc(self,p_act):
		global enemy_acts
		return_estimates=[]
		for e_a in enemy_acts:
			return_estimates.append(0)
		
		self.SpaceC.saveBackup()
		for i in range(len(enemy_acts)):
			for j in range(3):
				en_acts=( ctypes.c_int*3) (enemy_acts[i][0],enemy_acts[i][1],enemy_acts[i][2])
				r = self.SpaceC.step(p_act,en_acts)
				#rollout
				r = self.SpaceC.rollout(3)
				#r = 0
				return_estimates[i]+=r
				self.SpaceC.restoreBackup()



		max_index, max_value = max(enumerate(return_estimates), key=operator.itemgetter(1))
		en_acts=( ctypes.c_int*3) (enemy_acts[max_index][0],enemy_acts[max_index][1],enemy_acts[max_index][2])
		enemy_actions = [enemy_acts[max_index][0],enemy_acts[max_index][1],enemy_acts[max_index][2]]
		r = self.SpaceC.step(p_act,en_acts)
		#print("Reward: ",r)
		enemy_coords,player_coord,shoots_coords = self.get_positions()
		return r,enemy_actions,enemy_coords,player_coord,shoots_coords
		


	def play_mcts(self,p_true_action,max_depth = 10, e = 1, decay = 0.99995):
		best_rewards = []
		start_time = time()

		root = Node(None, None)

		best_actions = []
		best_reward = float("-inf")
		self.SpaceC.saveBackup()
		for p in range(10):
			print("Playout: ",p)
			sum_reward = 0
			node = root
			terminal = False
			actions = []

			# selection
			while node.children:
				if node.explored_children < len(node.children):
					child = node.children[node.explored_children]
					node.explored_children += 1
					node = child
				else:
					r =random.random()
					if(r<e):
						node = max(node.children, key=avg)
					else:
						node = max(node.children, key=ucb)
					e*=decay

				#print(node.action)
				#p_act = random.randint(0,4)
				p_act = self.SpaceC.fsm(0)
				en_acts=( ctypes.c_int*3) (int(node.action[0]),int(node.action[1]),int(node.action[2]))
				reward = self.SpaceC.step(p_act,en_acts)
				sum_reward += reward
				actions.append(en_acts)

			# expansion
			if not terminal:
				#node.children = [Node(node, a) for a in combinations(state.action_space)]
				node.children = [Node(node, a) for a in enemy_acts ]
				random.shuffle(node.children)

			# playout
			while not terminal:
				#p_act = random.randint(0,4)
				p_act = self.SpaceC.fsm(0)
				r_e_act = random.randint(0,len(enemy_acts)-1)
				e_act = enemy_acts[r_e_act]
				en_acts=( ctypes.c_int*3) (int(e_act[0]),int(e_act[1]),int(e_act[2]))
				reward = self.SpaceC.step(p_act,en_acts)
				sum_reward += reward
				actions.append(en_acts)

				if len(actions) > max_depth:
					break

			# remember best
			if best_reward < sum_reward:
				best_reward = sum_reward
				best_actions = actions

			while node:
				node.visits += 1
				node.value += sum_reward
				node =node.parent

			self.SpaceC.restoreBackup()
		#print('best_actions: ',best_actions)
		en_acts=best_actions[0] 
		r = self.SpaceC.step(p_true_action,en_acts)
		enemy_coords,player_coord,shoots_coords = self.get_positions()
		return r,best_actions[0],enemy_coords,player_coord,shoots_coords