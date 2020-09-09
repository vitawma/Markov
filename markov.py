'''
See this article:
https://www.rose-hulman.edu/class/csse/csse221/200910/Projects/Markov/markov.html
'''

import random, math
from collections import Counter

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

	def get_sum(self):
		self.sum = sum(s.mult for s in self.suffixes)
		return self.sum

	def add_suffix(self,suffix,multiplicity=1):
		for s in self.suffixes:
			if suffix == s:
				s.mult += 1*multiplicity
				return
		self.suffixes.append(Suffix(suffix))

	def create_prob_table(self):
		self.get_sum()
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

	def short_str(self):
		s = ', '.join(str(x) for x in self)
		s = '[' + s + ']'
		return s

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
		return 'NW'
	def __repr__(self):
		return 'NW'

NON_WORD = Non_Word()

def	general_cdf(x,mu,sigma):
	return 0.5 * (1 + math.erf((x-mu)/sigma/2**0.5))

class Markov(list):
	def __init__(self,n):
		self.n = n
		self.prefix_freq = []

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

		for i in range(len(my_list)):
			my_list[i] = [NON_WORD]*self.n + list(my_list[i]) + [NON_WORD]
			my_list[i] = tuple(my_list[i])

		if ignore_repeated:
			freq_dict = dict((x,1) for x in my_list)
		else:
			freq_dict = dict((x,sum(1 for y in my_list if y==x)) for x in my_list)

		print(my_list)
		my_list = list(set(my_list))
		print(my_list)

		progress = 0
		for i in range(len(my_list)):
			p = my_list[i]
			if i / len(my_list) > progress + 0.1:
				progress += 0.1
				print("%2d%%" % (progress*100))

			for j in range(len(p)-self.n):
				
				my_prefix = tuple(p[j:j+self.n])
				print(my_prefix)
				
				my_obj = self.get_prefix(my_prefix)
				if my_obj != None:
					my_obj.add_suffix(p[j+self.n],multiplicity=freq_dict[p])
				else:
					my_prefix = Prefix(my_prefix)
					my_prefix.add_suffix(p[j+self.n],multiplicity=freq_dict[p])
					self.append(my_prefix)

	def build_prefix_freq_list(self):
		self.prefix_freq = {x.short_str(): x.get_sum() for x in self}
		self.sum_prefix = sum(self.prefix_freq[x] for x in self.prefix_freq)
		s = "Total number of prefixes: %d\n" % self.sum_prefix
		s += "Different prefixes: %d\n" % len(self)
		s += '-'*50 + '\n'
		my_list = sorted(self.prefix_freq.items(), key=lambda x: x[1], reverse=True)
		for p in my_list:
			s += "%s : %d (%.2f per 10,000)\n" % (p[0], p[1], p[1]*10000/self.sum_prefix)
		print(s)

	def get_expected_freq(self,my_prefix):
		my_prefix = Prefix(my_prefix)

		if self.prefix_freq == []:
			self.build_prefix_freq_list()
		char_list = set(y for x in self for y in x)
		self.char_freq = {w: sum(x.get_sum() for x in self for y in x if y == w) for w in char_list}
		self.sum_char = sum(self.char_freq[c] for c in self.char_freq)
		self.char_prob = {x: self.char_freq[x]/self.sum_char for x in char_list}

		my_list = sorted(self.char_freq, key=lambda x: self.char_freq[x], reverse=True)
		s = "Total number of chars: %d\n" % self.sum_char
		s += '-'*50 + '\n'
		for c in my_list:
			s += "%2s : %5d (%2.2f%%)\n" % (c,self.char_freq[c],self.char_prob[c]*100)
		print(s)

		prob = 1
		for k in my_prefix:
			print("prob(%s)=%2.5f%%" % (k,self.char_prob[k]*100))
			prob *= self.char_prob[k]
		print('-'*25)
		mu = prob*self.sum_prefix
		sigma = (self.sum_prefix*prob*(1-prob))**0.5
		n = self.prefix_freq[my_prefix.short_str()]
		print('final prob: %-5.5f%%' % (prob*100))
		print('expected  : %-5.2f' % mu)
		print('deviation : %-5.2f' % sigma)
		print('found     : %-5d' % n)
		print('prob of finding that many: %.3f%%' % ((1-general_cdf(n,mu,sigma))*100))

	def __repr__(self):
		return __str__(self)

	def __str__(self,long_print=True):
		s = 'Markov chain with %d prefixes' % len(self)
		if long_print:
			s += ', of which:\n'
			for prefix in self:
				s += str(prefix)
		return s

def to_tuple(x):
	try:
		return(tuple(x))
	except TypeError:
		return(x,)

def replace_all(s,sub,my_list):
	for i in range(len(my_list)):
		s = s.replace(my_list[i],sub)
	return s

'''
Prefix = (NW)
Suffixes:
i, mult. 1
c, mult. 3
t, mult. 2
s, mult. 1
a, mult. 4
o, mult. 1
k, mult. 1
----------
Total count = 13
'''

def test_1():
	my_str = '''
In statistics a contingency table #(also known as a cross tabulation or crosstab)'''# is a type of table in a matrix format that displays the (multivariate) frequency distribution of the variables. They are heavily used in survey research, business intelligence, engineering and scientific research. They provide a basic picture of the interrelation between two variables and can help find interactions between them. The term contingency table was first used by Karl Pearson in "On the Theory of Contingency and Its Relation to Association and Normal Correlation",[1] part of the Drapers' Company Research Memoirs Biometric Series I published in 1904.
# A crucial problem of multivariate statistics is finding the (direct-)dependence structure underlying the variables contained in high-dimensional contingency tables. If some of the conditional independences are revealed, then even the storage of the data can be done in a smarter way (see Lauritzen (2002)). In order to do this one can use information theory concepts, which gain the information only from the distribution of probability, which can be expressed easily from the contingency table by the relative frequencies.
# A pivot table is a way to create contingency tables using spreadsheet software. '''
# The numbers of the males, females, and right- and left-handed individuals are called marginal totals. The grand total (the total number of individuals represented in the contingency table) is the number in the bottom right corner.
# The table allows users to see at a glance that the proportion of men who are right handed is about the same as the proportion of women who are right handed although the proportions are not identical. The strength of the association can be measured by the odds ratio, and the population odds ratio estimated by the sample odds ratio. The significance of the difference between the two proportions can be assessed with a variety of statistical tests including Pearson's chi-squared test, the G-test, Fisher's exact test, Boschloo's test and Barnard's test, provided the entries in the table represent individuals randomly sampled from the population about which conclusions are to be drawn. If the proportions of individuals in the different columns vary significantly between rows (or vice versa), it is said that there is a contingency between the two variables. In other words, the two variables are not independent. If there is no contingency, it is said that the two variables are independent.
# The example above is the simplest kind of contingency table, a table in which each variable has only two levels; this is called a 2 × 2 contingency table. In principle, any number of rows and columns may be used. There may also be more than two variables, but higher order contingency tables are difficult to represent visually. The relation between ordinal variables, or between ordinal and categorical variables, may also be represented in contingency tables, although such a practice is rare. For more on the use of a contingency table for the relation between two ordinal variables, see Goodman and Kruskal's gamma. 
# '''
	#my_str = open('bible.txt','r').read()

	my_str = my_str.replace('\n',' ')
	my_str = replace_all(my_str,'','()[]"\',.:;?#0123456789')
	my_list = my_str.lower().split()

	print(my_list)

	n = 1
	a = Markov(n)
	a.build_chain(my_list,list_of_lists=True,ignore_repeated=False)
	print(a)
	input()
	a.build_prefix_freq_list()
	# a.get_expected_freq(('i','n'))
	# a.get_expected_freq((NON_WORD,)*n)
	exit()
	
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
if __name__=='__main__':
	test_1()