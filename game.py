﻿from random import choice, randint, choices, randrange, sample, random
# import re
import PythonHelper.files as files
from os import path, system
from math import floor
from json import load
import platform
# from msvcrt import pause
# from time import sleep
# from keyboard import wait as pause
dev = False


def pause():
	if(platform.system()=="Windows"):
		system('pause')
	else:
		system("/usr/bin/env bash -c 'read -s -n 1 -p \"Press any key to continue...\"'")
		print()


class Game:
	def __init__(self, fileLoc: str, saveLoc: str):
		self.data = files.readjs(path.abspath(fileLoc))
		self.saveLoc = saveLoc
		self.events:dict[str] = self.data['events']
		self.weapons = self.data['weapons']
		self.message = self.data['messages']
		self.shorthands = self.data['shorthands']
		self.breakLine = '+'+'-'*30+'+'
		self.emptyLine = '|'+' '*30+'|'
		self.string = type("")
		self.startInv = self.data['start']
		self.startComplete = self.data['complete']
		self.array = type([])
		self.dict = type({})
		self.predicates = self.data['predicates']
		self.number = type(0)
		self.roguelike = self.data["roguelike"]
		# check to see if the user wants to use the savesystem even if it enabled
		if((not self.roguelike) and ('forceSave' in self.data and not self.data['forceSave'])):
			self.roguelike = not self.confirm(
				'Do you want to use the save system?')
		# print(self.roguelike)
		if(not dev):
			# remove_list = self.filterlist(self.weapons, 'dev', True)
			self.weapons = [i for i in self.weapons if not i['dev']]
		self.reset()
		if (not self.roguelike):
			self.openSave()

		# Create a better events system to increase performance but still support the old system
		self.places: dict[str, list[dict]] = {}
		if('events' in self.events):
			for x in enumerate(self.events['places']):
				self.places[x[1]['name']] = self.filterlist(
					self.events['events'], 'place', x[0])
		elif('events' in self.events['places'][0]):
			for x in enumerate(self.events['places']):
				if('events' in x[1]):
					self.places[x[1]['name']] = x[1]['events']
			pass

	# reset all variables for game start

	def reset(self):
		self.shopLevel = 0
		self.inventory = self.startInv
		self.completed = self.startComplete
		self.startAge = randint(25, 50)
		self.age = self.startAge
		self.old = randint(100, 150)
		self.gameTime = 0
		self.health = 100
		self.gold = 0
		self.location = 0
		self.rep = 0
	# confirmation function

	def confirm(self, string=''):
		string = string+'\n' if string != '' else''+'y/n:'
		x = input(string)
		x = x.lower()
		while(not (x[0] == 'y' or x[0] == 'n')):
			x = input(string)
			x = x.lower()
		return x == 'y'
	# get a formatted location

	def locationf(self):
		return self.events["places"][self.location]

	# Look for a specific shorthand
	def short(self, short):
		if(not short in self.shorthands):
			temp = {
				"gold": "gold",
				"health": "health",
				"rep": "reputation",
				"ma": "magic",
				"me": "melee",
				"ra": "ranged",
				"co": "consumable",
				"pe": "pet"
			}
			if(not short in temp):
				raise Exception(f"Shorthand \"{short}\" was not found")
			return temp[short]
		return self.shorthands[short]

		for x in self.shorthands:
			if(x == short):
				return self.shorthands[x]
		raise Exception(f"Shorthand \"{short}\" was not found")

	# Check if character is alive
	def alive(self):
		alive = self.health > 0
		if(self.age >= self.old):
			alive = False
			print('\n'*5+self.messages('retire') % self.age)
		elif(self.health <= 0):
			print('\n'*5+self.messages('death'))
		return alive

	# Get the messages for a specific section
	def messages(self, target):
		for x in self.message:
			if(x == target):
				match type(self.message[x]):
					case self.string:
						return self.message[x]
					case self.array:
						return choice(self.message[x])
					case _:
						return choice(self.message[x])
		raise Exception(f"Message \"{target}\" was not found")
	# Choose an event

	def event(self):
		events = []
		for x in self.places[self.locationf()['name']]:
			if('predicate' in x.keys()):
				if(self.predicate(x['predicate'])):
					events.append(x)
			else:
				events.append(x)
		listweights = []
		for x in events:
			if('weight' in x.keys()):
				listweights.append(x['weight'])
			else:
				match type(x['outcomes']):
					case self.number:
						listweights.append(0.25)
						pass
					case self.string:
						listweights.append(0.5)
						pass
					case self.array:
						listweights.append(1)
						pass

		event = choices(events, weights=listweights, k=1)[0]
		return event

	# Buyable items
	def availableItems(self):

		return

	# shop function
	# TODO intergrate shop properties like discounts and avaliable items
	# with the json file
	def shop(self, shopName):  # <<<--------------------------------------------------------------------------------------------------------------------------start
		if self.shopLevel == 0:
			self.shopLevel = 1
		self.shopLevel = self.rep//10*self.shopLevel
		shopping = True
		if(shopName in self.events['shops']):
			shop = self.events['shops'][shopName]
		else:

			# IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT
			# This is to prevent errors, please fix this at a later point
			# Replace this with the desired default
			if('default' in self.events['shops']):
				shop = self.events['shops']['default']
			else:
				shop = {
					"name": "cosi-trading-caravan",
					"costScale": 30,
					"repDiscountScaling": -5,
					"minGoldForBuy": 0,
					"notEnoughMessage": ""
				}
			# raise KeyError(f"no shop found called {shopName}! check the spelling and try again")

		repDiscount = shop["repDiscountScaling"] * self.shopLevel
		if repDiscount < -99:
			repDiscount = 0.01
		else:
			repDiscount = (repDiscount/100)+1

		if shop["costScale"] != 0:
			costScale = (shop["costScale"]/100)+1
		else:
			costScale = 1.0

		# sorts each weapon type
		weatypes = [
			self.filterlist(self.weapons, "type", "me"),
			self.filterlist(self.weapons, "type", "ma"),
			self.filterlist(self.weapons, "type", "ra")
		]

		# selects 3 or less random weapons for each type of weapon
		weapons = []
		samp = 0
		for i in range(len(weatypes)):
			if len(weatypes[i]) < 3:
				samp = len(weatypes[i])
			else:
				samp = 3
			weapons.append(sample(weatypes[i], samp))

		while(shopping):
			# shop menu
			print(self.breakLine)
			print(self.emptyLine + '\n| Welcome to this shop, enjoy! |')
			print(self.emptyLine)
			print('|● 0 to Exit                   |')
			print('|● 1 for Weapons               |')
			print('|● 2 for Items                 |')
			print(self.emptyLine+'\n'+self.breakLine)
			print(f"{self.short('gold').capitalize()}: {self.gold}")
			number = self.validn(['e', 'w', 'i'])

			match number:
				case 1:
					WeaponBuy = True
					FirsLoop = True
					while(WeaponBuy):  # while the user hasn't pressed back
						if(FirsLoop):
							# type menu
							print(self.breakLine)
							print(self.emptyLine)
							print('|         Weapons shop         |')
							print('| all of you purchases will be |')
							print(
								f"| dicounted by {shop['repDiscountScaling']*-1*self.shopLevel}%")
							print(self.emptyLine)
							print('|● 0 Back                      |')
							print('|● 1 for Melee                 |')
							print('|● 2 for Magic                 |')
							print('|● 3 for Ranged                |')
							print(self.breakLine)
							print(
								f"{self.short('gold').capitalize()}: {self.gold}")

							# assignes type and index based on selection
							weaType = ""
							match self.validn(['b', 'm', 'm', 'r']):
								case 1:
									inweaType = 0
									weaType = "Melee"
								case 2:
									inweaType = 1
									weaType = "Magic"
								case 3:
									inweaType = 2
									weaType = "Ranged"
								case 0:
									WeaponBuy = False
								case _:
									print('Well done you broke the validator')

							# determines what to pass into the validator
							if(WeaponBuy):  # if the user hasn't pressed back
								passin = []
								for i in weapons[inweaType]:
									passin.append(i)
								passin.append("B")
								FirsLoop = False

						if(WeaponBuy):  # if the user hasn't pressed back
							# weapons menu
							print()
							print(self.breakLine)
							print(self.emptyLine)
							print(f'|         {weaType} weapons')
							print(self.emptyLine)
							print("|● 0 Back                      |")
							print(self.breakLine)
							# displays all randomly generated weapons and their cost
							for count, weapon in enumerate(weapons[inweaType]):
								print(
									f"|● {count+1} {weapon['name']}\n| Cost: {weapon['Cost']*costScale}")
							print(self.emptyLine)
							print(self.breakLine)
							print(
								f"{self.short('gold').capitalize()}: {self.gold}")
							selection = self.validn(passin)

							print()
							match selection:
								case 0:
									FirsLoop = True  # loops back to the type menu
								case _:
									# single weapon menu
									# displays the lore of the weapon, as well as
									# discounted cost due to rep bonus
									# allow you to buy the weapon
									print(self.breakLine)
									print(self.emptyLine)
									print(
										f'|{weapons[inweaType][selection-1]["name"]}')
									print(self.emptyLine)
									if('loreData' in weapons[inweaType][selection-1].keys()):
										print(
											f"|● Lore: {self.strpara(weapons[inweaType][selection-1]['loreData'], menumode=True)}")
									else:
										print("|● this item has no lore")
									print(self.emptyLine)
									print(
										f"|● Pre-Discount  Cost: {weapons[inweaType][selection-1]['Cost']*costScale}")
									print(
										f"|● Post-Discount Cost: {weapons[inweaType][selection-1]['Cost']*costScale*repDiscount}")
									print(self.breakLine)

									if self.confirm():
										self.gold -= weapons[inweaType][selection -
																		2]['Cost']*costScale*repDiscount
										self.weapons.remove(
											weapons[inweaType][selection-2])
										self.inventory["weapons"].append(
											weapons[inweaType][selection-2])
										weapons[inweaType].pop(selection-2)
				case 2:
					pass
				case 0:
					shopping = False
					print(self.breakLine)
					print(self.emptyLine)
					print("|     Thanks for shopping!     |")
					print(self.emptyLine)
					print(self.breakLine)
					pass

				case _:
					print('Well done I guess, you broke the validator?')
					pass  # <<<--------------------------------------------------------------------------------------------------------------------------end

	# every 30 characters, replaces a space with a newline

	def strpara(self, string:str, menumode:bool=False)->str:
		out = ""
		placenl = False
		for i, val in enumerate(string):
			if (i+1) % 30 == 0:
				placenl = True
			if val == " " and placenl:
				out += "\n"
				if menumode:
					out += "|  "
				placenl = False
				continue
			else:
				pass
			out += val
		return out

	# valid number
	def validn(self, check):
		outcome = input('>>>')
		f = True
		outcomed = True
		while(outcomed):
			if(f != True):
				outcome = input('Please enter a valid number\n>>>')
			f = False
			if(outcome.isdigit()):
				try:
					check[int(outcome)]
					outcomed = False
				except:
					pass
		return int(outcome)

	# run the event
	def eventManager(self):
		event = self.event()
		if not self.roguelike:
			self.saveData()
			print("(game saved)")
		self.eventNonRandomManager(event)

	def eventNonRandomManager(self, event):
		print(event['text'])
		if(event['outcomes'] == 'shop'):
			self.shop(event["id"])
		elif(type(event['outcomes']) == type(0)):
			if(self.confirm()):
				self.location = event['outcomes']
				self.welcome()
				if('complete' in self.locationf()):
					if(type(self.locationf()['complete']) == self.array):
						for x in self.locationf()['complete']:
							self.completed.append(x)
					else:
						self.completed.append(self.locationf()['complete'])
				pause()
				print('\n'*2)
		else:
			print('Do you?')
			for x in range(len(event['outcomes'])):
				print(f"{str(x)}: {event['outcomes'][x]['name']}")
			outcome = self.validn(event["outcomes"])
			outcome = event["outcomes"][int(outcome)]
			self.eventOutcome(outcome)
			pause()

	def recursiveEventManager(self, event):
		if(event['output'] == 'shop'):
			self.shop()
		elif(type(event['output']) == type(0)):
			if(self.confirm()):
				self.location = event['outcomes']
				self.welcome()
				if('complete' in self.locationf().keys()):
					if(type(self.locationf()['complete']) == self.array):
						for x in self.locationf()['complete']:
							self.completed.append(x)
					else:
						self.completed.append(self.locationf()['complete'])
				pause()
				print('\n'*2)
	# What to do at the end of an event

	def eventOutcome(self, outcome: dict) -> None:
		"""
		Completes the outcome of a single predicate
		"""
		if(type(outcome['output']) == self.string):
			print('\n'+outcome['output'])
			self.statEffectsRand(outcome)
			if('complete' in outcome.keys()):
				if(type(outcome['complete']) != self.array):
					self.completed.append(outcome['complete'])
				else:
					for x in outcome['complete']:
						self.completed.append(x)
			if('inventory' in outcome.keys()):
				for x in outcome['inventory'].keys():
					for z in outcome['inventory'][x]:
						self.inventory[x].append(z)
					pass
		else:
			if(type(outcome['output']) == self.dict):
				self.eventOutcome(
					outcome['output'][f"{str(self.predicate(outcome['output']['predicate'])).lower()}"])
			# This is in the case that it is a number (to go to a place)
			else:
				self.recursiveEventManager(
					outcome['output'][f"{str(self.predicate(outcome['output']['predicate'])).lower()}"])
		pass
	# predicate system

	def predicate(self, condition: dict | list) -> bool:
		"""
		Completes a single or list of predicates
		"""
		if(type(condition) == self.array):
			for x in condition:
				if(not self.singlePredicate(x)):
					return False

			return True
		else:
			return self.singlePredicate(condition)
	# code for one predicate

	def singlePredicate(self, condition: dict) -> bool:
		"""
		Completes a single predicate
		"""
		check = list(condition.keys())[0]
		match check:
			case 'has':
				for z in self.inventory:
					for x in self.inventory[z]:
						for y in condition[check]:
							if(y in x):
								if(x[y] == condition[check][y]):
									return True
						if(len(condition[check].keys()) < 1):
							raise Exception(
								f"The predicate did not have any values\nThe predicate was {condition}")
				return False
			case 'rep':
				if(condition[check]['greater']):
					if(condition[check]['rep'] < self.rep):
						return True
				else:
					if(condition[check]['rep'] > self.rep):
						return True
				pass
			case 'gold':
				if(condition[check]['greater']):
					if(condition[check]['gold'] < self.gold):
						return True
				else:
					if(condition[check]['gold'] > self.gold):
						return True
				pass
			case 'health':
				if(condition[check]['greater']):
					if(condition[check]['health'] < self.health):
						return True
				else:
					if(condition[check]['health'] > self.health):
						return True
				pass
			case 'reference':
				return self.predicate(self.predicates[condition[check]])
				pass
			case 'complete':
				return condition['complete'] in self.completed
				pass
			case 'not':
				return (not self.predicate(condition[check]))
				pass
			case 'chance':
				precision = 1/0.001
				chance = random()
				outcome = chance < condition[check]
				return outcome
				pass
			case _:
				raise Exception(
					f"The predicate {check} is not supported\nThe entire predicate is:\n{condition}")
		return False
	# statistics

	def stats(self) -> None:
		"""
		Prints out the stats of the player
		"""
		for x in self.inventory.keys():
			print('\n'+self.breakLine)
			print(x+'\n')

			for z in self.inventory[x]:
				print(f"● {z['name']}")
				if('loreData' in z.keys()):
					print('Lore: '+z['loreData'])
				if('type' in z.keys()):
					print('Type: '+self.short(z['type']))
		print(self.breakLine)
		print('\nYou now have:')
		print(f'●{self.gold} {self.short("gold")}')
		print(f'●{self.rep} {self.short("rep")}')
		print(f'●{self.health} {self.short("health")}')
		print(f'●{self.age} age\n')
	# filter function

	def filterlist(self, thelist: list | tuple, key: str, value) -> list | tuple:
		"""
		Filters a list to remove all values from a list where ``key`` in object is not `value`
		"""
		newlist = []
		for x in thelist:
			if(x[key] == value):
				newlist.append(x)
		return newlist
	# environmental things such as slow damage from heat in hell

	def environmentalEffects(self) -> None:
		"""
		Applies effects based on the location
		"""
		self.statEffects(self.locationf())
		if(self.gold < 0):
			self.health += floor(self.gold/10)
			print(self.messages('debt'))
			pause()
	# start an event based on an id (dev only)

	def eventFromId(self, id: str) -> None:
		"""
		This has an issue with the new event system, please fix this when you can think of a solution
		"""
		raise Exception(
			'This has an issue with the new event system, please fix this when you can think of a solution')
		self.eventNonRandomManager(self.filterlist(
			self.events['events'], 'id', id)[0])
		self.stats()
	# affect health, gold and rep based on dictionary

	def statEffects(self, thing: dict) -> None:
		"""
		Applies an effect based on an incoming dictionary without any randomness
		"""
		if('gold' in thing.keys()):
			self.gold += thing['gold']
		if('rep' in thing.keys()):
			self.rep += thing['rep']
		if('health' in thing.keys()):
			if(thing['health'] == 'kill'):
				self.health = 0
			else:
				self.health += thing['health']

	def statEffectsRand(self, outcome: dict) -> None:
		"""
		Applies an effect based on an incoming dictionary with an up to 10% random difference
		"""
		if('gold' in outcome.keys()):
			if(outcome['gold'] > 0):
				self.gold += outcome['gold'] + randint(0, floor(outcome['gold']/10))
			else:
				self.gold += outcome['gold'] + \
					randint(floor(outcome['gold']/10), 0)
		if('rep' in outcome.keys()):
			if(outcome['rep'] > 0):
				self.rep += outcome['rep']+randint(0, floor(outcome['rep']/10))
				# yo. i think this^ is supposed to say rep
				# DONE
			else:
				self.rep += outcome['rep']+randint(floor(outcome['rep']/10), 0)
				# correct me if im^
				# wrong but this  ^ one too
				# ALSO DONE
		if('health' in outcome.keys()):
			if(outcome['health'] == 'kill'):
				self.health = 0
			else:
				if(outcome['health'] > 0):
					self.health += outcome['health'] + \
						randint(0, floor(outcome['health']/10))
				else:
					self.health += outcome['health'] + \
						randint(floor(outcome['health']/10), 0)

	def savescheme(self) -> dict[str]:
		"""
		Returns a dictionary containing the savedata for the current instance
		"""
		return {
			"health": self.health,
			"age": self.age,
			"startAge": self.startAge,
			"gold": self.gold,
			"rep": self.rep,
			"location": self.location,
			"gameTime": self.gameTime,
			"old": self.old,
			"complete": self.completed,
			"inventory": self.inventory,
			"shopLevel": self.shopLevel
		}

	# opens/creates a save

	def openSave(self) -> None:
		"""
		Loads or creates a save into the self.save object
		"""
		with open(self.saveLoc, "r+") as raw:
			data = load(raw)
			while True:
				savename = str(input("Load from savename\n>>>"))
				if savename in data:
					print('Do you want to overwrite this file?')
					if(self.confirm()):
						self.save = savename
						self.reset()
						self.save = self.savescheme()
						data[savename] = self.save
						files.overwritejs(data, raw)
					else:
						self.save = data[savename]
						self.loadSave()
				else:
					print(
						"this save is not found. check the spelling or create a new save.\nwould you like to create a new save?")
					if self.confirm():
						self.save = savename
						self.reset()
						self.save = self.savescheme()
						data[savename] = self.save
						files.overwritejs(data, raw)
					else:
						continue
				self.savename = savename
				break

	def loadSave(self) -> None:
		"""
		Loads the save from the self.save dict
		"""
		self.inventory: dict = self.save["inventory"]
		self.completed: list[str] = self.save["complete"]
		self.age: int = self.save["age"]
		self.startAge: int = self.save["startAge"]
		self.old: int = self.save["old"]
		self.gameTime: int = self.save["gameTime"]
		self.health: int = self.save["health"]
		self.gold: int = self.save["gold"]
		self.location: int = self.save["location"]
		self.rep: int = self.save["rep"]
		self.shopLevel: int = self.save["shopLevel"]

	# saves game data
	def saveData(self) -> None:
		"""
		Saves gamedata to the savefile
		"""
		with open(self.saveLoc, "r+") as raw:
			data = load(raw)
			self.save = self.savescheme()
			for i in data:
				if self.savename == i:
					data[i] = self.save
			files.overwritejs(data, raw)

	def welcome(self) -> None:
		"""
		Prints a welcome message, should be called when you enter a new location
		"""
		loc = self.locationf()
		if('welcome' in loc):
			print(
				f"\n{choice(loc['welcome'])if type(loc['welcome'])==self.array else loc['welcome']}" % loc['name'])
		else:
			print('\n'+self.messages('welcome') % loc['name'])
		pass

	# Main gameplay loop

	def start(self) -> None:
		"""
		Starts the main game loop
		"""
		if self.roguelike:
			self.reset()
		print(self.messages('start'))
		pause()
		self.welcome()
		pause()
		print('\n'*2)
		while(self.alive()):
			self.eventManager()
			self.environmentalEffects()
			self.gameTime += 1
			if(self.age != self.startAge+self.gameTime//10):
				self.age = self.startAge+self.gameTime//10
				print(f'\nHappy Birthday, you are now {self.age}!')
				pause()

			self.stats()


if(__name__ == "__main__"):
	runtime = Game('./CuddlyComputingGameData/Original.json',
				   './saves/Original.json')
	runtime.start()
	print('Would you like to play again?')
	while(runtime.confirm()):
		runtime.start()
		print('Would you like to play again?')
