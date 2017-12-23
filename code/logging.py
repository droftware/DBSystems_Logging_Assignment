import sys


transaction_names = []
transaction = []
transaction_elements = []
transaction_first_output = []
local = {}
memory = {}
disc = {}
correctness = {}

def clear_state():
	del transaction_elements[:]
	del transaction_first_output[:]
	for i in range(len(transaction)):
		transaction_elements.append([])
		transaction_first_output.append(False)
	local.clear() 
	memory.clear() 
	disc.clear() 




def read_file(name):
	f = open(name)
	init_name = name
	transaction_names.append(name)
	transaction.append([])
	transaction_elements.append([])
	transaction_first_output.append(False)
	num_transactions = len(transaction)
	for line in f:
		transaction[num_transactions - 1].append(line.strip())
	# print(transaction[num_transactions - 1])
	f.close()

def write_file(log, name, correctness_num = -1):
	f = open(name, 'w')
	for record in log:
		f.write(record+'\n')
	if correctness_num != -1:
		f.write(str(correctness_num))
	f.close()

def variable_status():
	status = ''
	sorted_vars = sorted(list(disc.keys()))
	for var in sorted_vars:
		status += ' ' + var + ' ' + str(disc[var])
	return status


def create_log(quanta, log_type = 'undo', transaction_id = -1):
	log = []
	if transaction_id == -1:
		num_transactions = len(transaction)
	else:
		num_transactions = 1
	idx = 0
	num_total_statements = 0
	for i in range(num_transactions):
		num_total_statements += len(transaction[i])
	# print('Total number of statements: ', num_total_statements)
	k = 0
	statements_covered = 0
	while k < num_total_statements:
		statements_covered = 0
		for i in range(num_transactions):
			if transaction_id != - 1:
				i = transaction_id
			if idx == 0:
				log_record = '<START ' + transaction_names[i] + '>' + variable_status()
				log.append(log_record)
			for j in range(quanta):
					# print('i:',i)
					# print('idx:',idx)
					# print('j',j)
					statement_num = idx + j
					if statement_num < len(transaction[i]):
						statement = transaction[i][idx + j]
						statements_covered += 1
						# print('Statement:', statement)
						if statement.upper().startswith('READ'):
							first = statement.find('(')
							last = statement.find(')')
							temp = statement[first+1:last].strip()
							temp = temp.split(',')
							element = temp[0].strip()
							local_variable = temp[1].strip()
							# print('READ:',element,':',local_variable,':')
							if element not in memory:
								memory[element] = disc[element]
							if element not in transaction_elements[i]:
								transaction_elements[i].append(element)
							local[local_variable] = memory[element]
						elif statement.upper().startswith('WRITE'):
							first = statement.find('(')
							last = statement.find(')')
							temp = statement[first+1:last].strip()
							temp = temp.split(',')
							element = temp[0].strip()
							local_variable = temp[1].strip()
							if element not in memory:
								memory[element] = disc[element]
							if element not in transaction_elements[i]:
								transaction_elements[i].append(element)
							if log_type == 'undo':
								log_record = '<' + transaction_names[i] + ',' + element + ',' + str(memory[element]) + '>' + variable_status()
								log.append(log_record)
								memory[element] =  local[local_variable]
							else:
								log_record = '<' + transaction_names[i] + ',' + element + ',' + str(local[local_variable]) + '>' + variable_status()
								log.append(log_record)
								memory[element] =  local[local_variable]
							# print('WRITE:',element,':',local_variable,':')
						elif statement.upper().startswith('OUTPUT'):
							first = statement.find('(')
							last = statement.find(')')
							element = statement[first+1:last].strip()
							if log_type == 'undo':
								disc[element] = memory[element]
								transaction_elements[i].remove(element)
								if len(transaction_elements[i]) == 0:
									log_record = '<COMMIT ' + transaction_names[i] + '>' + variable_status()
									log.append(log_record)
							else:
								if transaction_first_output[i] == False:
									transaction_first_output[i] = True
									log_record = '<COMMIT ' + transaction_names[i] + '>' + variable_status()
									log.append(log_record)
								disc[element] = memory[element]
								transaction_elements[i].remove(element)
							# print('OUTPUT:',local_variable)
						elif statement.find('='):
							first = statement.find('=')
							operand1 = statement[0:first-1].strip()
							# local[operand1] = 0
							# print(local.keys())
							operator = None
							operator_idx = -1
							for symbol in ['+','-','*','/']:
								# print(symbol)
								if statement.find(symbol) != -1:
									# print('Symbol found',symbol)
									second = statement.find(symbol)
									operator_idx = second
									operator = symbol
							if operator == None:
								print('Operator not recognized, Transaction:',transaction_names[i],'line no:',statement_num)
								sys.exit(0)
							else:
								operand2 = statement[first + 1:operator_idx].strip()
								operand3 = statement[operator_idx + 1:].strip()
							# print('operand1:',operand1,'operator:',operator,'operand2:',operand2,'operand3:',operand3)
							if operand2.isdigit() and operand3.isdigit() == False:
								local[operand1] = int(operand2) + local[operand3]
							elif operand2.isdigit() == False and operand3.isdigit():
								local[operand1] = local[operand2] + int(operand3)
							elif operand2.isdigit() and operand3.isdigit():
								local[operand1] = int(operand2) + int(operand3)
							else:
								local[operand1] = local[operand2] + local[operand3]

		idx += quanta 
		k += statements_covered
	return log

def main():
	read_file('T1')
	read_file('T2')
	read_file('T3')
	# print(transaction_names)
	# print(transaction)
	# for line in log:
	# 	print(line)
	# fill_correctness()
	for log_type in ['undo', 'redo']:
		for quanta in range(9,0,-1):
			clear_state()
			disc['A'] = 8
			disc['B'] = 8
			disc['C'] = 5
			disc['D'] = 10
			log = create_log(quanta, log_type)
			file_name = str(quanta) + '.txt_' + log_type
			if quanta == 9:
				for key in disc:
					correctness[key] = disc[key]
			correctness_flag = True
			for key in disc:
				if correctness[key] != disc[key]:
					correctness_flag = False
					break
			correctness_num = -1
			if correctness_flag:
				correctness_num = quanta
			write_file(log, file_name, correctness_num)
			



	




if __name__ == '__main__':
    main()