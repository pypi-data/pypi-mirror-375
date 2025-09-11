from .visit_log import LogVisitor
from .transform_log import LogTransformer
import sys
from .decisao import Decisao
import argparse
import types
import ast
import shlex
import pickle
import unittest
import time


exec_decisoes = []
exec_linhas = []

def init_bool_register(linha, coluna, ret):
	#print('Iniciando {}'.format( (linha,coluna)))
	exec_decisoes.append({})
	exec_linhas.append((linha,coluna))
	return ret 


def bool_register(result, linha, coluna, condicao):
	#print('Decisao: {} Condição: {} Resultado: {}'.format((linha,coluna), condicao, result))
	lc = (linha,coluna)
	if lc != exec_linhas[-1]:
		raise ValueError('Numero de linha inesperado {}'.format(lc)) 
	r = 1 if result else 0
	dic = exec_decisoes[-1]
	dic[condicao] = r
	
	return result



def run_ast_tests(modules, test_modules):
	"""
	Compila e executa módulos e testes em memória usando ASTs.
	
	- `modules`: dicionário nome → AST de código (ex: 'x': ast_x)
	- `test_modules`: dicionário nome → AST de testes (ex: 'test_x': ast_test_x)

	Retorna:
		unittest result object
	"""
	loaded_modules = {}

	# === Etapa 1: carrega módulos normais ===
	for name, tree in modules.items():
		name = name[:-3]
		ast.fix_missing_locations(tree)
		mod = types.ModuleType(name)
		mod.__dict__['bool_register'] = bool_register  # injeta a função
		mod.__dict__['init_bool_register'] = init_bool_register  # injeta a função
		exec(compile(tree, f"<{name}>", "exec"), mod.__dict__)
		sys.modules[name] = mod

		
	# === Etapa 2: carrega módulos de teste ===
	test_instances = []
	for name, tree in test_modules.items():
		ast.fix_missing_locations(tree)
		mod = types.ModuleType(name)
		exec(compile(tree, f"<{name}>", "exec"), mod.__dict__)
		sys.modules[name] = mod
		test_instances.append(mod)

		
	# === Etapa 3: executa os testes ===
	suite = unittest.TestSuite()
	for test_mod in test_instances:
		suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_mod))

	print("Running tests...")
	result = unittest.TextTestRunner().run(suite)
	return result

def parse_args():
	parser = argparse.ArgumentParser(
	description="Executa ASTs em memória com suporte a unittest e múltiplos caminhos."
)

	group = parser.add_mutually_exclusive_group()

	group.add_argument(
		'--run',
		action='store_true',
		help='Executa o arquivo como script principal'
	)

	group.add_argument(
		'--unittest',
		action='append',
		metavar='TESTE',
		help='Arquivos de teste a executar (pode repetir)'
	)
	
	parser.add_argument(
		'--append',
		action='store_true',
		help='Adiciona dados de cobertura às execuções anteriores'
	)

	parser.add_argument(
		'--path',
		action='append',
		default=[],
		help='Caminhos adicionais para sys.path (pode repetir)'
	)


	parser.add_argument(
		'--args',
		action='append',
		default=[],
		help='Argumentos para execução'
	)
	
	parser.add_argument(
		'arquivo',
		help='Arquivo principal do programa (ex: x.py)'
	)

	args = parser.parse_args()
	return args

def __ignore():
	i = 2
	n = len(sys.argv)
	arquivo = sys.argv[-1]
	vetig = []
	try: 
		while i < n - 1:
			s = sys.argv[i]
			if s.startswith('+'):
				l = int(s[1:])
				i += 1
				c = int(sys.argv[i])
				i += 1
				g = int(sys.argv[i])
				i += 1
				vetig.append(('+', l, c, g))
			elif s.startswith('-'):
				l = int(s[1:])
				i += 1
				c = int(sys.argv[i])
				i += 1
				g = int(sys.argv[i])
				i += 1
				vetig.append(('-', l, c, g))
			else:
				raise ValueError(f'Invalid argumet {s}')
	except Exception as ex:
		print('Invalid argumet')
		print(ex)
		return

	
	try:
		with open(arquivo+'.mdc','rb') as f:
			dic_decisoes = pickle.load(f)
	except Exception as ex:
		print('Can´t read execution log file')
		print(ex)
		return


	for op,l,c,oq in vetig:
		exect = op == '+'
		achou = False
		for _, dec in dic_decisoes.items():
			if dec.linha == (l,c):
				achou = True
				try:
					dec.executado[oq-1] = exect
					#print(dec)
				except:
					print(f'Not found requirement {(l,c,oq)}')
				break
		if not achou:
			print(f'Not found decision {(l,c)}')

	print_all_conditions(dic_decisoes)

	with open(arquivo+'.mdc','wb') as f:
		pickle.dump(dic_decisoes, f)


def print_all_conditions(conditions_list):
	totcov = totreq = 0
	for _,dec in conditions_list.items():
		print('Line number: {}'.format(dec.linha))
		print('Decicion:', dec.texto)
		print('Combinations to be covered: ')
		print(dec)
		cov,req = dec.get_covered_requirements()
		totcov += cov
		totreq += req
	percent = totcov * 100 // totreq if totreq != 0 else 100
	print('''\nCovered {} out of {} requirements in {} decisions ({}%)
	      '''.format(totcov, totreq, len(conditions_list),percent))

def main():
	
	if len(sys.argv) < 2:
		sys.exit()
	if sys.argv[1] == '--cover':
		__ignore()
		sys.exit()

	args = parse_args()
	arquivo = args.arquivo

	# print("args.unittest:", args.unittest)
	# print("args.run:", args.run)
	# print("args.path:", args.path)
	# print("args.append:", args.append)
	# print("args.args:", args.args)
	# print("args.arquivo:", args.arquivo)
 	

	if not (args.run or args.unittest):
		inicio = time.time()
		try:
			mv = LogVisitor(file=arquivo)
		except Exception as ex:
			print('Error using {}. {}'.format(arquivo, str(ex)))
			sys.exit()
		mv.go_visit()
		
		dic_decisoes = {}
		for linha,cond in mv.decisoes.items():
			texto = mv.textos[linha]
			dic_decisoes[linha] = (Decisao(linha, cond, texto))
		
		
		
		print_all_conditions(dic_decisoes)
			
		with open(args.arquivo+'.mdc','wb') as f:
			pickle.dump(dic_decisoes, f)
		fim = time.time()
		print('Run time: {:.5f} '.format( fim-inicio))
							
	elif args.run:
		try:
			mv = LogTransformer(file=arquivo)
		except Exception as ex:
			print('Error using {}. {}'.format(arquivo, str(ex)))
			sys.exit()
		mv.go_visit()
		
		# insere os caminhos para include
		for caminho in args.path:
			if caminho not in sys.path:
				sys.path.insert(0, caminho)
				
		# Cria um módulo virtual e injeta o canal no namespace
		mod = types.ModuleType("__main__")
		mod.__dict__['bool_register'] = bool_register  # injeta a função
		mod.__dict__['init_bool_register'] = init_bool_register  # injeta a função

		mv.tree = ast.fix_missing_locations(mv.tree)

		oldargv = sys.argv
		sys.argv = [args.arquivo]
		if args.args != []:
			sys.argv += shlex.split(args.args[-1])


		# Executa a AST no namespace do módulo
		exec(compile(mv.tree, "<main>", "exec"), mod.__dict__)
		
		sys.argv = oldargv
		
		leu = False
		if args.append:
			try:
				with open(args.arquivo+'.mdc','rb') as f:
					dic_decisoes = pickle.load(f)
				leu = True
			except:
				print('Can´t read execution log file')

		if not leu:
			dic_decisoes = {}
			for linha,cond in mv.decisoes.items():
				texto = mv.textos[linha]
				dic_decisoes[linha] = (Decisao(linha, cond, texto))
			
			
		for i  in range(len(exec_linhas)):
			linha = exec_linhas[i]
			dec = dic_decisoes[linha]
			dec.executa(exec_decisoes[i])

		print_all_conditions(dic_decisoes)

		with open(args.arquivo+'.mdc','wb') as f:
			pickle.dump(dic_decisoes, f)
		
	elif args.unittest:
		try:
			mv = LogTransformer(file=arquivo)
		except Exception as ex:
			print('Error using {}. {}'.format(arquivo, str(ex)))
			sys.exit()
		mv.go_visit()
		
		# insere os caminhos para include
		for caminho in args.path:
			if caminho not in sys.path:
				sys.path.insert(0, caminho)
		
		mod_dic = {arquivo:mv.tree}
		test_dic = {}
		for name in args.unittest:
			try: 
				f = open(name)
				source = f.read()
				f.close()
				code = ast.parse(source)
			except Exception as ex:
				print('Error using {}. {}'.format(arquivo, str(ex)))
				sys.exit()
			test_dic[name] = code
			
		result = run_ast_tests(mod_dic,test_dic)
		
		leu = False
		if args.append:
			try:
				with open(args.arquivo+'.mdc','rb') as f:
					dic_decisoes = pickle.load(f)
				leu = True
			except:
				print('Can´t read execution log file')

		if not leu:
			dic_decisoes = {}
			for linha,cond in mv.decisoes.items():
				texto = mv.textos[linha]
				dic_decisoes[linha] = (Decisao(linha, cond, texto))
			
		for i  in range(len(exec_linhas)):
			linha = exec_linhas[i]
			dec = dic_decisoes[linha]
			dec.executa(exec_decisoes[i])

		print_all_conditions(dic_decisoes)
			
		with open(args.arquivo+'.mdc','wb') as f:
			pickle.dump(dic_decisoes, f)		
		
	

if __name__ == '__main__':
	main()
		

	
