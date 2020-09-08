'''
See this article:
https://www.rose-hulman.edu/class/csse/csse221/200910/Projects/Markov/markov.html
'''

import random

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
		my_object = super().__new__(cls, my_tuple)
		my_object.suffixes = []
		my_object.prob_table = []
		my_object.sum = 0
		return my_object

	def add_suffix(self,suffix,multiplicity=1):
		for s in self.suffixes:
			if suffix == s:
				s.mult += 1*multiplicity
				return
		self.suffixes.append(Suffix(suffix))

	def create_prob_table(self):
		self.sum = sum(s.mult for s in self.suffixes)
		self.prob_table.append(self.suffixes[0].mult/self.sum)
		for i in range (1,len(self.suffixes)):
			self.prob_table.append(self.prob_table[-1]+
								   self.suffixes[i].mult/self.sum)

	def print_prob_table(self):
		if self.prob_table == []:
			self.create_prob_table()
		for i in range(len(self.prob_table)):
			print('%.2f%%\t%s' % (self.prob_table[i]*100,
								  str(self.suffixes[i].obj)))

	def give(self):
		if self.prob_table == []:
			self.create_prob_table()
		r = random.random()
		for i in range(len(self.prob_table)):
			if r < self.prob_table[i]:
				return self.suffixes[i].obj


	def __eq__(self,other):
		return super(tuple,self).__eq__(other)

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
	def __str__(self):
		return 'NON_WORD'
	def __repr__(self):
		return 'NON_WORD'

NON_WORD = Non_Word()

class Tuple_with_Multiplicity(tuple):
	pass
	# def __new__(cls,obj,mult):
	# 	my_object = super().__new__(cls,obj)
	# 	my_object.mult = mult
	# 	return my_object		

class Markov(list):
	def __init__(self,n):
		self.n = n

	def get_prefix(self,my_prefix):
		my_prefix = to_tuple(my_prefix)
		return next((x for x in self if x == my_prefix), None)

	def get_random_prefix(self):
		return random.choice(self)

	def build_chain(self,my_list,list_of_lists=False,ignore_repeated=False):
		if len(my_list) < self.n + 1:
			print('Impossible to build chain, too little data')

		if not list_of_lists:
			my_list = [my_list]

		i = 0
		max_length = len(my_list)
		while i < max_length:
		# for i in range(len(my_list)):
			my_list[i] = [NON_WORD]*self.n + list(my_list[i]) + [NON_WORD]
			my_list[i] = tuple(my_list[i])
			my_sum = 1
			j = i+1
			while j < max_length:
				if my_list[j] == my_list[i]:
					my_sum += 1
					max_length -= 1
					my_list.pop(j)
				j += 1
			my_list[i] = Tuple_with_Multiplicity(my_list[i])
			my_list[i].mult = my_sum
			i += 1

		# if ignore_repeated:
		# 	freq_dict = dict((x,1) for x in my_list)
		# else:
		# 	freq_dict = dict((x,sum(1 for y in my_list if y==x)) for x in my_list)

		# my_list = list(set(my_list))

		progress = 0
		count = 0
		for p in my_list:
			if count / len(my_list) > progress + 0.1:
				progress += 0.1
				print("%2d%%" % (progress*100))

			for i in range(len(p)-self.n):
				
				my_prefix = tuple(p[i:i+self.n])
				
				my_obj = self.get_prefix(my_prefix)
				if my_obj != None:
					my_obj.add_suffix(p[i+self.n],multiplicity=p.mult)
				else:
					my_prefix = Prefix(my_prefix)
					my_prefix.add_suffix(p[i+self.n],multiplicity=p.mult)
					self.append(my_prefix)

			count += 1

	def __repr__(self):
		return __str__(self)

	def __str__(self,long_print=True):
		s = 'Markov chain with %d prefixes, of which:\n' % len(self)
		if long_print:
			for prefix in self:
				s += str(prefix)
		return s

def to_tuple(x):
	try:
		return(tuple(x))
	except TypeError:
		return(x,)

def replace_all(s,sub,my_list):
	for p in my_list:
		s = s.replace(p,sub)
	return s

def test_1():
	my_str = '''
In statistics a contingency table '''#(also known as a cross tabulation or crosstab) is a type of table in a matrix format that displays the (multivariate) frequency distribution of the variables. They are heavily used in survey research, business intelligence, engineering and scientific research. They provide a basic picture of the interrelation between two variables and can help find interactions between them. The term contingency table was first used by Karl Pearson in "On the Theory of Contingency and Its Relation to Association and Normal Correlation",[1] part of the Drapers' Company Research Memoirs Biometric Series I published in 1904.
# A crucial problem of multivariate statistics is finding the (direct-)dependence structure underlying the variables contained in high-dimensional contingency tables. If some of the conditional independences are revealed, then even the storage of the data can be done in a smarter way (see Lauritzen (2002)). In order to do this one can use information theory concepts, which gain the information only from the distribution of probability, which can be expressed easily from the contingency table by the relative frequencies.
# A pivot table is a way to create contingency tables using spreadsheet software. 
# The numbers of the males, females, and right- and left-handed individuals are called marginal totals. The grand total (the total number of individuals represented in the contingency table) is the number in the bottom right corner.
# The table allows users to see at a glance that the proportion of men who are right handed is about the same as the proportion of women who are right handed although the proportions are not identical. The strength of the association can be measured by the odds ratio, and the population odds ratio estimated by the sample odds ratio. The significance of the difference between the two proportions can be assessed with a variety of statistical tests including Pearson's chi-squared test, the G-test, Fisher's exact test, Boschloo's test and Barnard's test, provided the entries in the table represent individuals randomly sampled from the population about which conclusions are to be drawn. If the proportions of individuals in the different columns vary significantly between rows (or vice versa), it is said that there is a contingency between the two variables. In other words, the two variables are not independent. If there is no contingency, it is said that the two variables are independent.
# The example above is the simplest kind of contingency table, a table in which each variable has only two levels; this is called a 2 × 2 contingency table. In principle, any number of rows and columns may be used. There may also be more than two variables, but higher order contingency tables are difficult to represent visually. The relation between ordinal variables, or between ordinal and categorical variables, may also be represented in contingency tables, although such a practice is rare. For more on the use of a contingency table for the relation between two ordinal variables, see Goodman and Kruskal's gamma. 
# '''
	my_str = open('bible.txt','r').read()

	my_str = my_str.replace('\n',' ')
	my_str = replace_all(my_str,'','(),.:;?#0123456789')
	my_list = my_str.lower().split()
	print(my_list)

	n = 4
	a = Markov(n)
	a.build_chain(my_list,list_of_lists=True,ignore_repeated=False)
	
	print('-'*50)
	print('-'*50)
	prefix = a.get_random_prefix()

	for i in range(5000):
		s = prefix.give()
		if s==NON_WORD:
			print(' ', end='')
			new = (NON_WORD,)*a.n
		else:
			print(s, end='')
			new = prefix[1:] + to_tuple(s)
		prefix = a.get_prefix(new)

# import cProfile
# cProfile.run('test_1()')

test_1()