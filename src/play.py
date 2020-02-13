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


def get_random_enemy_actions():
	enemy_actions=[]
	for i in range(3):
		r = random.randint(0, 12)
		if(r==4):
			r = 0
		enemy_actions.append(r)
	print("Python: Enemy actions: ",enemy_actions)
	return enemy_actions
	

def play():
	#Sempre inicie as estruturas de dados
	SpaceC.init()
	a=( ctypes.c_int*3) (0,0,0)
	SpaceC.step(1,a)

	SpaceC.print_matrix()

	act = 0
	while(act==0 or act==1 or act==2 or act==3 or act==4):
		print("Enter Action: 1-Up, 2-Down, 3-Left, 4-Right, 5-Shoot")
		a = input()
		act = int(a)-1


		#random enemy actions
		enemy_actions = get_random_enemy_actions()

		en_acts=( ctypes.c_int*3) (enemy_actions[0],enemy_actions[1],enemy_actions[2])
		r = SpaceC.step(act,en_acts)
		print("Reward: ",r)

		#Get State to plot
		gm = SpaceC.get_matrix
		gm.restype = None
		gm.argtypes = [ctypes.c_size_t,ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		state = np.empty((29,19))
		gm( state.size, state)
		print(state)

		#get enemy ships positions
		gm = SpaceC.get_enemy_positions
		gm.restype = None
		gm.argtypes = [ctypes.c_size_t,ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		enemy_coords = np.empty(6)#2*number of enemies
		gm( enemy_coords.size, enemy_coords)
		print(enemy_coords)

		#get player ship position
		gm = SpaceC.get_player_positions
		gm.restype = None
		gm.argtypes = [ctypes.c_size_t,ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		player_coord = np.empty((2))#2 coordinates
		gm( player_coord.size, player_coord)
		print(player_coord)

		#get shoots positions
		gm = SpaceC.get_shoots_positions
		gm.restype = None
		gm.argtypes = [ctypes.c_size_t,ndpointer(ctypes.c_double, flags="C_CONTIGUOUS")]
		shoots_coords = np.zeros((101))#max shoots 50 * 2. Last position tell us the number of shoots
		max_shoots = gm( shoots_coords.size, shoots_coords)
		print(shoots_coords)
		print('max_shoots:',max_shoots)



		if r == -1:
			return
		if r == 1000:
			return


play()
