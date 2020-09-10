'''
See this article:
https://www.rose-hulman.edu/class/csse/csse221/200910/Projects/Markov/markov.html
'''

import random, math
from collections import Counter

class Suffix:
	def __init__(self,obj,mult=1):
		self.obj = obj
		self.mult = mult

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
		my_object.id = dict()
		my_object.sum = 0
		return my_object

	def get_sum(self):
		self.sum = sum(s.mult for s in self.suffixes)
		return self.sum

	def add_suffix(self,suffix,mult,my_id):
		'''
		id is the index of the word in the input vector
		'''
		if my_id in self.id:
			self.id[my_id] += mult
		else:
			self.id[my_id] =  mult

		for s in self.suffixes:
			if suffix == s:
				s.mult += mult
				#s.id.append(my_id)
				return
		my_suffix = Suffix(suffix,mult)
		self.suffixes.append(my_suffix)

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
		self.char_freq = []
		self.input = Markov_Input([],[])
		self.sum_prefix = 0

	def get_prefix(self,my_prefix):
		my_prefix = to_tuple(my_prefix)
		return next((x for x in self if x == my_prefix), None)

	def get_random_prefix(self):
		return random.choice(self)

	def build_chain(self,my_input):
		'''
		Markov_Input -> None
		Starting with a Markov_Input (list + corresponding freq. list), this builds
		the Markov chain for them. Any base elements are accepted.
		'''

		self.input = my_input

		for p in self.input.input:
			self.input.transf_input.append(tuple([NON_WORD]*self.n + list(p) + [NON_WORD]))

		progress = 0
		for i in range(len(self.input.transf_input)):
			p = self.input.transf_input[i]
			if i / len(self.input.transf_input) > progress + 0.1:
				progress += 0.1
				print("%2d%%" % (progress*100))

			for j in range(len(p)-self.n):
				my_prefix = tuple(p[j:j+self.n])
				
				my_obj = self.get_prefix(my_prefix)
				if my_obj != None:
					my_obj.add_suffix(p[j+self.n],mult=self.input.freq[i],my_id=i)
				else:
					my_prefix = Prefix(my_prefix)
					my_prefix.add_suffix(p[j+self.n],mult=self.input.freq[i],my_id=i)
					self.append(my_prefix)

		self.build_prefix_freq_list()
		self.build_char_freq_list()

	def build_prefix_freq_list(self):
		self.prefix_freq = {tuple(x): x.get_sum() for x in self}
		self.sum_prefix = sum(self.prefix_freq[x] for x in self.prefix_freq)

	def print_prefix_freq_list(self):
		s = "Total number of prefixes: %d\n" % self.sum_prefix
		s += "Different prefixes: %d\n" % len(self)
		s += '-'*50 + '\n'
		my_list = sorted(self.prefix_freq.items(), key=lambda x: x[1], reverse=True)
		for p in my_list:
			s += "%s : %d (%.2f per 10,000)\n" % (p[0].short_str(), p[1], p[1]*10000/self.sum_prefix)
		print(s)

	def build_char_freq_list(self):
		char_list = set(y for x in self for y in x)
		temp_char_freq = {w: sum(x.get_sum() for x in self for y in x if y == w) for w in char_list}
		my_list = sorted(temp_char_freq, key=lambda x: temp_char_freq[x], reverse=True)
		self.char_freq = {c: temp_char_freq[c] for c in my_list}
		self.sum_char = sum(self.char_freq[c] for c in self.char_freq)
		self.char_prob = {c: self.char_freq[c]/self.sum_char for c in self.char_freq}
		
	def print_char_freq_list(self):
		s = "Total number of chars: %d\n" % self.sum_char
		s += '-'*30 + '\n'
		for c in self.char_freq:
			s += "%2s : %5d (%2.2f%%)\n" % (c,self.char_freq[c],self.char_prob[c]*100)
		print(s)

	def id_str(self,prefix,long=True):
		'''
		internal info -> str
		'''
		my_prefix = self.get_prefix(prefix)
		my_list = []
		for _id in sorted(my_prefix.id, key=lambda x: my_prefix.id[x], reverse=True):
			s = str(self.input.input[_id])
			if long and my_prefix.id[_id] > 1:
				s += '({:d})'.format(my_prefix.id[_id])
			my_list.append(s)
		return ','.join(my_list)

	def get_many_expected_freq(self):
		my_list = sorted(self.prefix_freq.items(), key=lambda x: x[1], reverse=True)
		my_dic = dict()
		for i in range(100):
			my_dic[my_list[i][0]] = self.get_expected_freq(my_list[i][0])

		my_list = sorted(my_dic.items(), key=lambda x: x[1], reverse=True)
		print("{:^10} | {:^7} | {:^7} | {:^7} | {:^30}".format('prefix','freq.','%freq.','st.dev.','examples') )
		print('-'*80)
		for p in my_list:
			freq = self.prefix_freq[p[0]]
			print_dict = {'prefix'  : str(p[0]),
						  'freq'    : freq,
						  'rel_freq': freq/self.sum_prefix,
						  'std_dev' : my_dic[p[0]],
						  'examples': self.id_str(p[0],long=True)}

			# print("{:^.20}".format(self.id_str(p[0])))
			print(('{d[prefix]:^10} | {d[freq]:^7d} | {d[rel_freq]:^7.4f} ' +
				'| {d[std_dev]:^7.1f} | {d[examples]:^.30}').format(d=print_dict))

	def get_expected_freq(self,my_prefix,print_it=False):
		my_prefix = tuple(my_prefix)

		s = '\ndesired prefix: ' + str(my_prefix) + '\n'

		prob = 1
		for k in my_prefix:
			s += "prob(%s)=%2.5f%%" % (k,self.char_prob[k]*100)
			prob *= self.char_prob[k]
		s += '-'*25
		n = self.prefix_freq[my_prefix]
		mu = prob*self.sum_prefix
		sigma = (self.sum_prefix*prob*(1-prob))**0.5
		std_dev = abs(n-mu)/sigma
		
		s += 'final prob: %-5.5f%%' % (prob*100)
		s += 'expected  : %-5.2f' % mu
		s += 'deviation : %-5.2f' % sigma
		s += 'found     : %-5d' % n
		s += 'std_deviations from mean : %.5f' % std_dev
		s += 'prob of finding that many, or more: %.5f%%' % ((1-general_cdf(n,mu,sigma))*100)

		if print_it:
			print(s)

		return std_dev

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

class Char:
	def __init__(self,symbol,freq,rel_freq):
		self.symbol   = symbol
		self.freq     = freq
		self.rel_freq = rel_freq

class Markov_Input:
	def __init__(self,my_list,freq_list):
		'''
		The input should not contain repeated elements.
		To prepare input from an arbitrary list, use the
		auxiliary functions.'''
		self.input = my_list
		self.freq = freq_list
		self.transf_input = []
		self.str_limit = 10

	def str_preprocess(my_str, split=True):
		'''
		str -> Markov_Input
		'''
		my_str = my_str.replace('\n',' ')
		my_str = replace_all(my_str,'','()[]"\',.:;?#0123456789')
		my_str = my_str.lower()
		if split:
			my_list = my_str.split()
		else:
			my_list = [my_str]
		return Markov_Input.other_preprocess(my_list)

	def other_preprocess(my_list):
		'''
		list -> Markov_Input
		'''
		# my_dict = Counter(my_list)
		my_sorted = sorted(Counter(my_list).items(), key=lambda x: x[1], reverse=True)
		my_list2 = [x[0] for x in my_sorted]
		freq_list = [x[1] for x in my_sorted]
		return Markov_Input(my_list2, freq_list)

	def __str__(self):
		s = "%25s | %-10s\n" % ('input','frequency')
		s += '-'*50 + '\n'
		for i in range(min(len(self.input),self.str_limit)):
			s += "%25s | %-10s\n" % (self.input[i], self.freq[i])
		return s

def test_1():
	my_str = '''
In statistics a contingency table #(also known as a cross tabulation or crosstab) is a type of table in a matrix format that displays the (multivariate) frequency distribution of the variables. They are heavily used in survey research, business intelligence, engineering and scientific research. They provide a basic picture of the interrelation between two variables and can help find interactions between them. The term contingency table was first used by Karl Pearson in "On the Theory of Contingency and Its Relation to Association and Normal Correlation",[1] part of the Drapers' Company Research Memoirs Biometric Series I published in 1904.
# A crucial problem of multivariate statistics is finding the (direct-)dependence structure underlying the variables contained in high-dimensional contingency tables. If some of the conditional independences are revealed, then even the storage of the data can be done in a smarter way (see Lauritzen (2002)). In order to do this one can use information theory concepts, which gain the information only from the distribution of probability, which can be expressed easily from the contingency table by the relative frequencies.
# A pivot table is a way to create contingency tables using spreadsheet software. ththththththth
# The numbers of the males, females, and right- and left-handed individuals are called marginal totals. The grand total (the total number of individuals represented in the contingency table) is the number in the bottom right corner.
# The table allows users to see at a glance that the proportion of men who are right handed is about the same as the proportion of women who are right handed although the proportions are not identical. The strength of the association can be measured by the odds ratio, and the population odds ratio estimated by the sample odds ratio. The significance of the difference between the two proportions can be assessed with a variety of statistical tests including Pearson's chi-squared test, the G-test, Fisher's exact test, Boschloo's test and Barnard's test, provided the entries in the table represent individuals randomly sampled from the population about which conclusions are to be drawn. If the proportions of individuals in the different columns vary significantly between rows (or vice versa), it is said that there is a contingency between the two variables. In other words, the two variables are not independent. If there is no contingency, it is said that the two variables are independent.
# The example above is the simplest kind of contingency table, a table in which each variable has only two levels; this is called a 2 × 2 contingency table. In principle, any number of rows and columns may be used. There may also be more than two variables, but higher order contingency tables are difficult to represent visually. The relation between ordinal variables, or between ordinal and categorical variables, may also be represented in contingency tables, although such a practice is rare. For more on the use of a contingency table for the relation between two ordinal variables, see Goodman and Kruskal's gamma. 
# '''
	# my_str = open('bible.txt','r').read()

	my_input = Markov_Input.str_preprocess(my_str)
	print(my_input)

	my_list = []
	my_freq = []
	max_count = 10000
	i = 0
	with open('pt_br_50k.txt','r') as f:
		line = f.readline().split()
		while line != [] and (not max_count or i < max_count):
			my_list.append(line[0])
			my_freq.append(int(line[1]))
			line = f.readline().split()
			i += 1
	my_input = Markov_Input(my_list,my_freq)

	n = 2
	a = Markov(n)
	# a.build_chain(my_list,freq_list=my_freq,list_of_lists=True,ignore_repeated=False)
	# a.build_chain(my_list,list_of_lists=False,ignore_repeated=False)
	a.build_chain(my_input)
	# print(a)
	a.print_char_freq_list()
	# a.get_expected_freq(('i','n'))
	a.get_many_expected_freq()
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