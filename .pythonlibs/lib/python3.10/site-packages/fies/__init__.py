
# ファイル入出力ツール [fies]

import os
import sys
import json
import yaml
import pickle

# read_modeを表すオブジェクト
class _ReadMode:
	# 初期化処理
	def __init__(self):
		pass

# ファイルフォーマット略記辞書
abb_ff_dic = {
	"text": ["t", "txt"],
	"json": ["j", "js"],
	"yaml": ["y", "ya", "yml"],
	"pickle": ["p", "pkl", "pick"],
	"binary": ["b", "bi", "bin"],
	"csv": ["c"],
	"dir": ["d", "directory"]
}

# ファイルフォーマット指定の解決 (略記, auto)
def cleanup_file_format(file_format, filename, data):
	# 自動指定の場合
	if file_format == "auto":
		if os.path.isdir(filename): return "dir"
		_, ext = os.path.splitext(filename)
		if ext == ".json": return "json"
		if ext == ".yml": return "yaml"
		if ext == ".pickle": return "pickle"
		if ext == ".bin": return "binary"
		if ext == ".csv": return "csv"
		return "text"
	# 略記の解決
	for formal in abb_ff_dic:
		if file_format.lower() == formal.lower(): return formal
		for abb in abb_ff_dic[formal]:
			if file_format.lower() == abb.lower(): return formal
	# 解決できない場合
	raise Exception("[fies error] invalid file_format.")

# テキストファイルの読み込み
def text_read(filename, **kw_args):
	encoding = kw_args.get("encoding", "utf-8")
	with open(filename, "r", encoding = encoding) as f:
		data = f.read()
	return data

# テキストファイルの書き出し
def text_write(filename, data, **kw_args):
	encoding = kw_args.get("encoding", "utf-8")
	with open(filename, "w", encoding = encoding) as f:
		f.write(data)

# jsonファイルの読み込み
def json_read(filename, **kw_args):
	json_str = text_read(filename, **kw_args)	# テキストファイルの読み込み
	return json.loads(json_str)

# jsonファイルの書き出し
def json_write(filename, data, **kw_args):
	json_str = json.dumps(data, indent = 4, ensure_ascii = False)
	text_write(filename, json_str, **kw_args)	# テキストファイルの書き出し

# yamlファイルの読み込み
def yaml_read(filename, **kw_args):
	encoding = kw_args.get("encoding", "utf-8")
	with open(filename, "r", encoding = encoding) as f:
		return yaml.safe_load(f)

# yamlファイルの書き出し
def yaml_write(filename, data, **kw_args):
	encoding = kw_args.get("encoding", "utf-8")
	with open(filename, "w", encoding = encoding) as f:
		yaml.dump(data, f, encoding = "utf-8", allow_unicode = True)

# pickleファイルの読み込み
def pickle_read(filename, **kw_args):
	with open(filename, "rb") as f:
		data = pickle.load(f)
	return data

# pickleファイルの書き出し
def pickle_write(filename, data, **kw_args):
	with open(filename, "wb") as f:
		pickle.dump(data, f)

# バイナリファイルの読み込み
def binary_read(filename, **kw_args):
	with open(filename, "rb") as f:
		data = f.read()
	return data

# バイナリファイルの書き出し
def binary_write(filename, data, **kw_args):
	with open(filename, "wb") as f:
		f.write(data)

# csvファイルの読み込み
def csv_read(filename, **kw_args):
	import csv
	encoding = kw_args.get("encoding", "cp932")
	with open(filename, "r", encoding = encoding) as f:
		return list(csv.reader(f))

# csvで定められたescape方法
def csv_escape(org_s):
	for esc_str in list(',"\n'):
		if esc_str in org_s:
			# escapeの必要がある場合
			return '"%s"'%(org_s.replace('"', '""'))
	# escapeの必要がない場合
	return org_s

# csvの文字列に変換
def to_csv_str(data):
	# data内をすべて文字列型にする
	str_data = [[str(e) for e in row] for row in data]
	# 区切り文字で区切っていく
	s = "\n".join([
		",".join([
			csv_escape(e)	# csvで定められたescape方法
			for e in row
		])
		for row in str_data
	])
	return s

# csvファイルの書き出し
def csv_write(filename, data, **kw_args):
	# csvの文字列に変換
	s = to_csv_str(data)
	encoding = kw_args.get("encoding", "cp932")
	with open(filename, "w", encoding = encoding) as f:
		f.write(s)

# クエリ内のファイル指定部分にディレクトリの指定を加える
def ex_dir(query, dir_name):
	def dir_adder(filename):
		return os.path.join(dir_name, filename)
	if type(query) == type(""):
		return dir_adder(filename = query)
	elif type(query) == type((0,)):
		ex_f = dir_adder(query[0])
		return (ex_f,) + query[1:]
	else:
		raise Exception("[fies error] The format of the query is different than expected.")

# ディレクトリオブジェクト
class Dir_Obj:
	# 初期化処理
	def __init__(self, dir_name, fies_obj, **kw_args):
		self.dir_name = dir_name
		self.fies_obj = fies_obj
	# ディレクトリ内列挙
	def __iter__(self):
		for e in os.listdir(self.dir_name):
			yield e
	# 一つ潜る
	def __getitem__(self, query):
		# クエリ内のファイル指定部分にディレクトリの指定を加える
		ex_q = ex_dir(query, self.dir_name)
		return self.fies_obj[ex_q]
	# 一つ下の階層にsetitem
	def __setitem__(self, query, data):
		# クエリ内のファイル指定部分にディレクトリの指定を加える
		ex_q = ex_dir(query, self.dir_name)
		self.fies_obj[ex_q] = data
	# 文字列化
	def __str__(self):
		return "<fies(dir) %s>"%self.dir_name
	# 文字列化その2
	def __repr__(self):
		return "<fies(dir) %s>"%self.dir_name

# ファイル入出力ツール [fies]
class Fies:
	# 初期化処理
	def __init__(self):
		pass
	# ファイル読み書き
	def __call__(self, filename, data = _ReadMode(), file_format = "auto", **kw_args):
		# ファイルフォーマット指定の解決 (略記, auto)
		file_format = cleanup_file_format(file_format, filename, data)
		# 読み/書き で分岐
		if type(data) == _ReadMode:
			return self._read(filename, file_format, **kw_args)
		else:
			self._write(filename, data, file_format, **kw_args)
	# ファイルの読み込み (略記)
	def __getitem__(self, query):
		# auto指定が省略されている場合
		if type(query) == type(""): query = (query, "auto")
		filename, file_format = query
		return self(filename, file_format = file_format)
	# ファイルの保存 (略記)
	def __setitem__(self, query, data):
		# auto指定が省略されている場合
		if type(query) == type(""): query = (query, "auto")
		filename, file_format = query
		return self(filename, data, file_format = file_format)
	# 読み込み
	def _read(self, filename, file_format, **kw_args):
		if file_format == "json":
			return json_read(filename, **kw_args)	# jsonファイルの読み込み
		elif file_format == "yaml":
			return yaml_read(filename, **kw_args)	# yamlファイルの読み込み
		elif file_format == "text":
			return text_read(filename, **kw_args)	# テキストファイルの読み込み
		elif file_format == "pickle":
			return pickle_read(filename, **kw_args)	# pickleファイルの読み込み
		elif file_format == "binary":
			return binary_read(filename, **kw_args)	# バイナリファイルの読み込み
		elif file_format == "csv":
			return csv_read(filename, **kw_args)	# csvファイルの読み込み
		elif file_format == "dir":
			return Dir_Obj(filename, self, **kw_args)	# ディレクトリオブジェクト
		else:
			raise Exception("[fies error] invalid file_format.")
	# 書き出し
	def _write(self, filename, data, file_format, **kw_args):
		if file_format == "json":
			json_write(filename, data, **kw_args)	# jsonファイルの書き出し
		elif file_format == "yaml":
			yaml_write(filename, data, **kw_args)	# yamlファイルの書き出し
		elif file_format == "text":
			text_write(filename, data, **kw_args)	# テキストファイルの書き出し
		elif file_format == "pickle":
			pickle_write(filename, data, **kw_args)	# pickleファイルの書き出し
		elif file_format == "binary":
			binary_write(filename, data, **kw_args)	# バイナリファイルの書き出し
		elif file_format == "csv":
			csv_write(filename, data, **kw_args)	# csvファイルの書き出し
		else:
			raise Exception("[fies error] invalid file_format.")

# 呼び出しの準備
fies = Fies()	# Fies型のオブジェクトを予め実体化
sys.modules[__name__] = fies	# モジュールオブジェクトとfiesオブジェクトを同一視
