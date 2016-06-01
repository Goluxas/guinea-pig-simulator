import random
class Population(object):
	def __init__(self):
		self.pop = []

	def __iter__(self):
		pop_clone = list(self.pop)

		for pig in pop_clone:
		#for pig in self.pop:
			yield pig

	def add_litter(self, litter):
		self.pop += litter

	def add_pig(self, pig):
		self.pop.append(pig)

	def kill_pig(self, pig):
		self.pop.remove(pig)

	def is_dead(self):
		# If there are no guinea pigs, dead
		if len(self.pop) == 0:
			return True

		sows = self.get_sow_count()
		boars = self.get_boar_count()
		pups = self.get_pup_count()
		preggers = self.get_pregnancies()

		if pups == 0:
			if sows == 0:
				# If there are no pups and only males, dead
				return True
			elif boars == 0 and preggers == 0:
				# If there are only females and none are pregnant, dead
				return True

		# If all death conditions fail, then population is alive
		return False

	def get_boar_count(self):
		count = len( [1 for pig in self.pop if isinstance(pig, Boar)] )
		return count

	def get_sow_count(self):
		count = len( [1 for pig in self.pop if isinstance(pig, Sow)] )
		return count

	def get_pup_count(self):
		count = len( [1 for pig in self.pop if isinstance(pig, Pup)] )
		return count

	def get_pregnancies(self):
		count = len( [1 for pig in self.pop if isinstance(pig, Sow) and pig.pregnant] )
		return count

	def get_size(self):
		return len(self.pop)

	def get_fertility(self):
		# "Fertility" of the population is a ratio of males to non-pregnant females
		# This ratio is multiplied against a coin toss to determine if
		# a given female gets pregnant when she's fertile

		boars = self.get_boar_count()
		sows = self.get_sow_count() - self.get_pregnancies()

		return float(boars) / sows

	def get_snapshot(self):
		boars = self.get_boar_count()
		sows = self.get_sow_count()
		pups = self.get_pup_count()
		pregnant_sows = self.get_pregnancies()

		message = 'Total Pigs: %d\n' % self.get_size()
		message += 'Pregnancies: %d\n' % pregnant_sows
		message += 'M/F adults: %d / %d\n' % (boars, sows)
		message += 'Newborn Pups: %d' % pups

		return message

class Pig(object):
	def __init__(self, age, gender):
		self.age = age
		self.gender = gender
		self.alive = True

	def pass_time(self):
		events = []
		# Time passes in 4 week (1 month) chunks
		self.age += 1
		# maybe have some pigs start randomly dying, with a higher chance as they get older
		if self.age > 60:
			# die of old age
			self.alive = False
			events.append('DEATH')

		return events

class Boar(Pig):
	def __init__(self):
		super(Boar, self).__init__(1, 'M')

class Sow(Pig):
	def __init__(self):
		super(Sow, self).__init__(1, 'F')
		self.pregnant = False
		self.gestation_time = 0
	
	def get_pregnant(self):
		self.pregnant = True
		self.gestation_time = 0

	def give_birth(self):
		self.pregnant = False
		
		#spawn 1-7 pups of random gender
		pups = []
		litter_size = random.randint(1,7)
		for i in range(litter_size):
			pups.append(Pup(random.choice(('M', 'F'))))

		return pups

	def pass_time(self):
		events = super(Sow, self).pass_time()

		if not self.alive:
			return

		# It takes 8 weeks for a litter to gestate
		if self.pregnant:
			self.gestation_time += 1
			if self.gestation_time == 2:
				events.append('BIRTH')

				# guinea pigs have a window of fertility
				# IMMEDIATELY after giving birth
				events.append('FERTILE')
		else:
			# give a random chance to become pregnant
			# (maybe weighted by how many males are in the population?)
			events.append('FERTILE')

		return events

class Pup(Pig):
	def __init__(self, gender='F'):
		super(Pup, self).__init__(0, gender)

	def pass_time(self):
		events = super(Pup, self).pass_time()

		# It only takes 1 month for a guinea pig to reach sexual maturity
		# So immediately become a Sow or Boar
		# Later, maybe consider some chance of death
		events.append('MATURE')

		return events

def main():
	pop = Population()

	eve = Sow()
	eve.get_pregnant()

	pop.add_pig(eve)

	time = 0

	while not pop.is_dead() and time < 60:
		for pig in pop:
			events = pig.pass_time()
			for e in events:
				if e == 'DEATH':
					# This pig has died.
					# Remove it from the population and ignore all other events
					pop.kill_pig(pig)
					break
				elif e == 'BIRTH':
					pups = pig.give_birth()
					pop.add_litter(pups)
				elif e == 'FERTILE':
					# pregnancy chance is based on population fertility and a coin toss
					# random.random() returns a float between 0 and 1
					chance = random.random() * pop.get_fertility()
					if chance > 0.5:
						pig.get_pregnant()
				elif e == 'MATURE':
					pop.kill_pig(pig)
					if pig.gender == 'F':
						pop.add_pig(Sow())
					else:
						pop.add_pig(Boar())
				else:
					print 'Unregistered Event!'

		time += 1

		print '%d week(s) have passed.' % (time * 4)
		print pop.get_snapshot()
		print '=' * 80

if __name__ == '__main__':
	main()
