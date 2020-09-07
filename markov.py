'''
See this article:
https://www.rose-hulman.edu/class/csse/csse221/200910/Projects/Markov/markov.html
'''

import random

def some_stuff():

	def prod(gen):
		try:
			return next(gen)*prod(gen)
		except StopIteration:
			return 1

	x = {0: Perc(0.50),
		 1: Perc(0.50)}

	y = {1: Perc(1/3),
		 2: Perc(1/3),
		 3: Perc(1/3)}

	xy = {0: Perc(1/2),
		  1: Perc(1/6),
		  2: Perc(1/6),
		  3: Perc(1/6)}

	z = {1: Perc(0.9),
		 10: Perc(0.1)}

	def mean_randdiscr_variable(x):
		return sum(k*x[k] for k in x)

	def mean_product_of_randdiscr_variable(*my_vars):
		import itertools
		print(type(my_vars))
		print(my_vars)
		cart_product = itertools.product(*my_vars)
		my_sum = 0
		return sum(prod(c[i]*my_vars[i][c[i]]
						for i in range(len(my_vars)))
				   for c in cart_product)

	# print(mean_randdiscr_variable(x))
	# print(mean_randdiscr_variable(y))
	# print(mean_product_of_randdiscr_variable(x,y,z))

	def fact(n):
		return 1 if n <= 1 else n*fact(n-1)

	class Perc(float):
		def __str__(self):
			return '%.2f%%' % (float(self) * 100)

		def __repr__(self):
			return self.__str__()

	def chance_greater_or_eq(alpha, p, n):
		'''
		what is the chance of obtaining the event E,
		whose probability is alpha, at least p out of n times?
		'''
		return Perc( fact(n)*sum( (alpha**k * (1-alpha)**(n-k) / fact(k) / fact(n-k)) for k in range (p,n+1) ) )

	# alpha = 67.11 / 100
	# print(chance_greater_or_eq(alpha, 3, 6))
	# print(chance_greater_or_eq(alpha, 4, 6))
	# print(chance_greater_or_eq(alpha, 5, 6))
	# print(chance_greater_or_eq(alpha, 6, 6))

class Suffix:
	def __init__(self,obj):
		self.obj = obj
		self.mult = 1

	def __eq__(self,other):
		if type(other) != Suffix:
			if self.obj != other:
				return False
		elif self.obj != other.obj:
				return False

		return True 

	def __str__(self):
		return "%s, mult. %d" % (str(self.obj), self.mult)

class Prefix(tuple):
	def __new__(cls,my_tuple):
		'''about __new__ and super() methods:
		https://www.geeksforgeeks.org/__new__-in-python/
		https://www.tutorialsteacher.com/python/magic-methods-in-python
		https://www.programiz.com/python-programming/methods/built-in/super
		'''
		my_object = super().__new__(cls, my_tuple)
		my_object.suffixes = []
		my_object.prob_table = []
		return my_object

	def add_suffix(self,suffix):
		for s in self.suffixes:
			if suffix == s:
				s.mult += 1
				return
		self.suffixes.append(Suffix(suffix))

	def create_prob_table(self):
		total = sum(s.mult for s in self.suffixes)
		self.prob_table.append(self.suffixes[0].mult/total)
		for i in range (1,len(self.suffixes)):
			self.prob_table.append(self.prob_table[-1]+
								   self.suffixes[i].mult/total)

	def print_prob_table(self):
		if self.prob_table == []:
			self.create_prob_table()
		for i in range(len(self.prob_table)):
			print('%.2f%%\t%s' % (self.prob_table[i]*100,
								  str(self.suffixes[i].obj)))

	def give(self,no_non_word=False):
		if self.prob_table == []:
			self.create_prob_table()
		r = random.random()
		for i in range(len(self.prob_table)):
			if r < self.prob_table[i]:
				if no_non_word and self.suffixes[i].obj == Non_Word():
					self.give(no_non_word=True)
				else:
					return self.suffixes[i].obj


	def __eq__(self,other):
		# this seems to work...
		return super(tuple,self).__eq__(other)
		# if len(self) != len(other):
		# 	return False
		# for i in range(len(self)):
		# 	if self[i] != other[i]:
		# 		return False
		# return True

	def __repr__(self):
		s =  'Prefix = ('
		for i in range(len(self)-1):
			s += str(self[i]) + ', '
		s += str(self[-1]) + ')\n'
		s += 'Suffixes:\n'
		for suf in self.suffixes:
			s += str(suf) + '\n'
		s += '-'*10 + '\n'
		s += 'Total count = %d\n\n' % sum(suf.mult for suf in self.suffixes)

		return s

class Non_Word:
	def __repr__(self):
		return __str__(self)
	def __str__(self):
		return 'NON_WORD'

class Markov(list):
	def __init__(self,n):
		self.n = n

	def get_prefix(self,my_prefix):
		return next((x for x in self if x == my_prefix), None)

	def get_random_prefix(self):
		return random.choice(self)

	def build_chain(self,my_list):
		if len(my_list) < self.n + 1:
			print('Impossible to build chain, too little data')

		for i in range(self.n):
			my_prefix = Prefix((Non_Word(),)*(self.n-1-i) +
							   tuple(my_list[0:i+1]))
			my_prefix.add_suffix(my_list[i+1])
			
			self.append(my_prefix)

		progress = 0
		for i in range(1,len(my_list)-self.n+1):
			if i / len(my_list) > progress + 0.1:
				print("%2d%%" % (i / len(my_list)*100))
				progress += 0.1
			my_prefix = tuple(my_list[i:i+self.n]) #Prefix(tuple(my_list[i:i+self.n]))
			# https://stackoverflow.com/questions/7125467/find-object-in-list-that-has-attribute-equal-to-some-value-that-meets-any-condi
			my_obj = self.get_prefix(my_prefix)
			if my_obj != None:
				if i + self.n < len(my_list):
					my_obj.add_suffix(my_list[i+self.n])
				else:
					my_obj.add_suffix(Non_Word())
			else:
				self.append(Prefix(my_prefix))
				if i + self.n < len(my_list):
					self[-1].add_suffix(my_list[i+self.n])
				else:
					self[-1].add_suffix(Non_Word())

	def __repr__(self):
		return __str__(self)

	def __str__(self,long_print=False):
		s = 'Markov chain with %d prefixes, of which:\n' % len(self)
		if long_print:
			for prefix in self:
				s += str(prefix)
		return s



def test_1():
	my_str = '''
In statistics, a contingency table (also known as a cross tabulation or crosstab) is a type of table in a matrix format that displays the (multivariate) frequency distribution of the variables. They are heavily used in survey research, business intelligence, engineering and scientific research. They provide a basic picture of the interrelation between two variables and can help find interactions between them. The term contingency table was first used by Karl Pearson in "On the Theory of Contingency and Its Relation to Association and Normal Correlation",[1] part of the Drapers' Company Research Memoirs Biometric Series I published in 1904.
A crucial problem of multivariate statistics is finding the (direct-)dependence structure underlying the variables contained in high-dimensional contingency tables. If some of the conditional independences are revealed, then even the storage of the data can be done in a smarter way (see Lauritzen (2002)). In order to do this one can use information theory concepts, which gain the information only from the distribution of probability, which can be expressed easily from the contingency table by the relative frequencies.
A pivot table is a way to create contingency tables using spreadsheet software. 
The numbers of the males, females, and right- and left-handed individuals are called marginal totals. The grand total (the total number of individuals represented in the contingency table) is the number in the bottom right corner.
The table allows users to see at a glance that the proportion of men who are right handed is about the same as the proportion of women who are right handed although the proportions are not identical. The strength of the association can be measured by the odds ratio, and the population odds ratio estimated by the sample odds ratio. The significance of the difference between the two proportions can be assessed with a variety of statistical tests including Pearson's chi-squared test, the G-test, Fisher's exact test, Boschloo's test and Barnard's test, provided the entries in the table represent individuals randomly sampled from the population about which conclusions are to be drawn. If the proportions of individuals in the different columns vary significantly between rows (or vice versa), it is said that there is a contingency between the two variables. In other words, the two variables are not independent. If there is no contingency, it is said that the two variables are independent.
The example above is the simplest kind of contingency table, a table in which each variable has only two levels; this is called a 2 × 2 contingency table. In principle, any number of rows and columns may be used. There may also be more than two variables, but higher order contingency tables are difficult to represent visually. The relation between ordinal variables, or between ordinal and categorical variables, may also be represented in contingency tables, although such a practice is rare. For more on the use of a contingency table for the relation between two ordinal variables, see Goodman and Kruskal's gamma. 
'''
	my_str = open('bible.txt','r').read()
	my_str = my_str.replace('\n',' ')
	my_list = list(my_str.lower())

	n = 4
	a = Markov(n)
	a.build_chain(my_list)
	print(a)
	r = a.get_prefix(tuple('the '))
	print(r)
	print('-'*50)
	prefix = a.get_random_prefix()
	for i in range(1000):
		s = prefix.give(no_non_word=True)
		print(s, end='')
		prefix = a.get_prefix(prefix[1:] + tuple(s))

import cProfile
cProfile.run('test_1()')

