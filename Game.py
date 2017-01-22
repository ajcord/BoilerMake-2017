import random
from copy import deepcopy
from socket import *
import time
from daniel import *

SING_SCORE = 1
DUB_SCORE = 3
TRIP_SCORE = 10
COMBO_SCORE = 25

'''
CARD_POS1 =
CARD_POS2 =
CARD_POS3 =
CARD_POS4 =
CARD_POS5 =
DISCARD_POS =
PILE_POS =
SWITCH_POS = 
CAMARA_POS = 

MOTOR_1_GRAB =
MOTOR_2_GRAB = 

MOTOR_0_CAM = 
MOTOR_1_CAM = 
MOTOR_2_CAM = 

MOTOR_0_LEGGO =
MOTOR_1_LEGGO = 
MOTOR_2_LEGGO = 

MOTOR_0_FLIP =
MOTOR_1_FLIP = 
MOTOR_2_FLIP = 

MOTOR_1_MOVE = 0
'''

class GameState(object):
	def __init__(self):
		self.cards = []
		self.sock = socket(AF_INET, SOCK_STREAM)
		self.sock.connect(("cardshark.local", 8000))
		self.sock.sendall("suction,1")

	def indices_to_tuple(self, t_of_ind):
		return self.cards.index(t_of_ind)


	def same_suit(self, card1, card2):
		return (card1 - 1)/13 == (card2 - 1)/13

		#Prob not needed
	def has_overlapping_elements(set1, set2):
		for e in set1:
			for e2 in set2:
				if e == e2:
					return True
		return False

	#Checks if two cards are directly next to each other (Takes a pair of cards, returns boolean)
	def check_if_double(self, pair):
		#TODO, ACE AND KING
		if pair[0] % 13 == pair[1] % 13:
			return True
		# Cards next to each other?
		if abs(pair[0] - pair[1]) == 1 or abs(pair[0] - pair[1]) == 12:
			if self.same_suit(pair[0], pair[1]):
				return True
		return False

	def check_if_triple(self, trips):
		if trips[0] %13 == trips[1] % 13 and trips[1] % 13 == trips[2] % 13:
			return True
		# Sort remaining
		s = sorted(trips)
		# Three in a row
		if s[2] - s[0] == 2:
			if self.same_suit(s[0], s[2]):
				return True
		return False

	def check_if_quad(self, quad): # Weed joke here
		if quad[0] % 13 == quad[1] % 13 and quad[1] % 13 == quad[2] % 13 and quad[2] % 13 == quad[3] % 13:
			return True
		s = sorted(quad)
		if s[3] - s[0] == 3:
			if self.same_suit(s[0], s[3]):
				return True
		return False

	# Finds the single card least likely to be in a double, thus the one that should be thrown away
	def find_loneliest_card(self, singles):
		print "FINDING LONELIEST"
		counts = [0 for s in singles]
		for s in range(len(singles)):
			for card in self.cards:
				if self.check_if_double((singles[s], card)):
					counts[s] += 1
		return singles[counts.index(min(counts))]

	def find_all_doubles(self,rem):
		doubles = []
		for i in range(len(rem)):
			for j in range(i + 1, len(rem)):
				if self.check_if_double((rem[i], rem[j])):
					doubles.append((i,j))
		return doubles

	def find_all_triples(self, rem):
		triples = []
		for i in range(len(rem)):
			for j in range(i + 1, len(rem)):
				for k in range(j + 1, len(rem)):
					if self.check_if_triple((rem[i], rem[j], rem[k])):
						triples.append((i,j,k))
		return triples

	def find_all_four_combos(self):
		combos = []
		for i in range(len(self.cards)):
			for j in range(i + 1, len(self.cards)):
				for k in range(j + 1, len(self.cards)):
					for l in range(k + 1, len(self.cards)):
						if self.check_if_quad((self.cards[i], self.cards[j], self.cards[k], self.cards[l])):
							combos.append((i,j,k,l))
		return combos

	def add_card(self, card):
		self.cards.append(card)

	#Singles remaining
	def find_best_set_combo4(self, remaining):
		ret = []
		s = 0
		for r in remaining:
			ret.append([self.cards.index(r)])
			s += SING_SCORE
		return (s, ret)

	#Doubles or worse remaining
	def find_best_set_combo3(self, remaining):
		doubles = self.find_all_doubles(remaining)
		best_score = 0
		best_sets = []
		for i in range(len(doubles)):
			copy = deepcopy(remaining)
			for e in sorted(doubles[i], reverse=True):
				del copy[e]
			best_subset = self.find_best_set_combo3(copy)
			cur_score = DUB_SCORE + best_subset[0]
			if cur_score > best_score:
				best_score = cur_score
				best_sets = best_subset[1]
				doubles_indices = [self.indices_to_tuple(remaining[j]) for j in doubles[i]]
				best_sets.append(doubles_indices)
		# With no triples
		no_dubs = self.find_best_set_combo4(remaining)
		if no_dubs[0] > best_score:
			best_score = no_dubs[0]
			best_sets = no_dubs[1]
		return (best_score, best_sets)

	#Triples or worse remaining
	def find_best_set_combo2(self,remaining):
		threes = self.find_all_triples(remaining)
		best_score = 0
		best_sets = []
		for three in threes:
			copy = deepcopy(remaining)
			for e in sorted(three, reverse=True):
				del copy[e]
			best_subset = self.find_best_set_combo2(copy)
			cur_score = TRIP_SCORE + best_subset[0]
			if cur_score > best_score:
				best_score = cur_score
				best_sets = best_subset[1]
				triple_indices = [self.indices_to_tuple(remaining[j]) for j in three]
				best_sets.append(triple_indices)
		# With no triples
		no_trips = self.find_best_set_combo3(remaining)
		if no_trips[0] > best_score:
			best_score = no_trips[0]
			best_sets = no_trips[1]
		return (best_score, best_sets)

	# Will always return a set of sets in ascending size order, a feature I totally designed
	# And didn't happen by chance
	def find_best_set_combo(self):
		fours = self.find_all_four_combos()
		best_score = 0
		best_sets = []

		for four in fours:
			copy = deepcopy(self.cards)
			for e in sorted(four, reverse=True):
				del copy[e]
			best_set = self.find_best_set_combo2(copy)
			cur_score = COMBO_SCORE + best_set[0]
			if cur_score > best_score:
				best_score = cur_score
				best_sets = best_set[1]
				best_sets.append(list(four))
		# No fours option
		no_fours = self.find_best_set_combo2(self.cards)
		if no_fours[0] > best_score:
			best_score = no_fours[0]
			best_sets = no_fours[1]
		if best_score >= COMBO_SCORE + 2 * TRIP_SCORE:
			print "WE WIN WE WIN WE WIN"
		return best_score, best_sets

	# When we have 11 cards in our hand, this will select the one to remove
	def remove_card(self):
		c = self.find_best_set_combo()[1]
		print "COMBO: ", c
		if len(c[0]) == 1:
			index = 0
			l = []
			while index < 11 and len(c[index]) == 1:
				l.append(self.cards[c[index][0]])
				index += 1
			sad_mofo = self.cards.index(self.find_loneliest_card(l))
		else:
			sad_mofo = c[0][0]

		# MOVE SAD_MOFO TO PILE
		# MOVE CARD 11 TO POSITION SAD_MOFO

		self.cards[sad_mofo] = self.cards[-1]
		del self.cards[-1]
		print "Removed index ", sad_mofo

	# Returns boolean on whether to pick up the card 
	def take_card(self, new_card):
		bs, _ = self.find_best_set_combo()
		self.cards.append(new_card)
		nbs, _ = self.find_best_set_combo()
		print "Before take ", bs
		print "After take ", nbs
		if (nbs > bs + SING_SCORE):
			return True
		del self.cards[-1]
		return False

	def turn(self):
		self.grab_card(-2)
		self.

		if self.take_card(card_possible):
			self.remove_card()
		else:
			new_card = draw_card()
			self.remove_card()
		print "TURN "
		print self.cards


	def find_pos_of_card(val):
		if val/2 == 0:
			return CARD_POS1
		if val/2 == 1:
			return CARD_POS2
		if val/2 == 2:
			return CARD_POS3
		if val/2 == 3:
			return CARD_POS4
		if val/2 == 4:
			return CARD_POS5
		if val == -1:
			return DISCARD_POS
		if val == -2:
			return PILE_POS
		if val == -3:
			return SWITCH_POS
		if val == -4:
			return CAMARA_POS

	# MOVEMENT FUNCTIONALITY
	def grab_card(self, num):
		post = find_pos_of_card(num)
		self.sock.sendall("motor,1," + MOTOR_1_MOVE)
		self.sock.sendall("motor,0," + post)
		self.sock.sendall("motor,1," + MOTOR_1_GRAB)
		self.sock.sendall("motor,2," + MOTOR_2_GRAB)
		return 0

	def leggo_card(self, num):
		post = find_pos_of_card(num)
		self.sock.sendall("motor,1," + MOTOR_1_MOVE)
		self.sock.sendall("motor,0," + post)
		self.sock.sendall("motor,1," + MOTOR_1_LEGGO)
		self.sock.sendall("motor,2," + MOTOR_2_LEGGO)
		self.sock.sendall("suction,0")
		self.sock.sendall("suction,1")
		return 0

	#Flip into discard, then pick up
	def flip_card(self):
		
		self.sock.sendall("motor,0," + MOTOR_0_LEGGO)
		self.sock.sendall("motor,1," + MOTOR_1_LEGGO)
		self.sock.sendall("motor,2," + MOTOR_2_LEGGO)
		self.sock.sendall("suction,0")
		self.sock.sendall("motor,2,0")
		self.sock.sendall("motor,0," + post)
		self.sock.sendall("motor,1," + MOTOR_1_LEGGO)
		self.sock.sendall("motor,2," + MOTOR_2_GRAB)
		post = find_pos_of_card(-2)
		return 0

	# Move card to discard
	def discard_card(self, num):
		return 0

	def move_to_switch(self):
		return 0

	# Returns numerical value of new card
	def request_pic(self):
		post = find_pos_of_card(-4)
		self.sock.sendall("motor,1," + MOTOR_1_MOVE)
		self.sock.sendall("motor,0," + post)
		self.sock.sendall("motor,1," + MOTOR_1_CAM)
		self.sock.sendall("motor,2," + MOTOR_2_CAM)
		self.sock.sendall("img\r\n")
		time.sleep(1)
		ret = self.sock.recv(1048576)
		return discover_card(ret)



from msvcrt import getch
gs = GameState()


	

