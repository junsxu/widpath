from pathlib import Path
import shutil
from widpath import WidPathResolver

root_dir = "testpath"
root=Path(root_dir)
resolver = WidPathResolver(root=root_dir, size=2)

wid  = "dc10ce02019b8ed9787869d0103e9c4b"
wid2 = "dc10ce02019a8ed9787869d0103e9c4b"
wid3 = "dc20ce02019a8ed9787869d0103e9c4b"


# 自动查找合适的存储文件路径
print(resolver.get_file_path(wid))
# 输出: 取决于实际存在的目录/文件

(root / Path('dc')).mkdir(parents=True, exist_ok=True, mode=711)
assert resolver.get_file_path(wid) == root / Path('dc') / Path('10.json')
shutil.rmtree(root_dir)

prefix = "dc/10"
(root / Path(prefix)).mkdir(parents=True, exist_ok=True, mode=711)
assert resolver.get_file_path(wid) == root / Path(prefix) / Path('ce.json')
print(f"{prefix}\t: {resolver.get_file_path(wid)}")
shutil.rmtree(root_dir)

prefix = "dc/10/ce"
(root / Path(prefix)).mkdir(parents=True, exist_ok=True, mode=711)
assert resolver.get_file_path(wid) == root / Path(prefix) / Path('02.json')
print(f"{prefix}\t: {resolver.get_file_path(wid)}")
shutil.rmtree(root_dir)

prefix = "dc/10/ce/02"
(root / Path(prefix)).mkdir(parents=True, exist_ok=True, mode=711)
assert resolver.get_file_path(wid) == root / Path(prefix) / Path('01.json')
print(f"{prefix}\t: {resolver.get_file_path(wid)}")
shutil.rmtree(root_dir)

prefix = "dc/10/ce/02/01"
(root / Path(prefix)).mkdir(parents=True, exist_ok=True, mode=711)
assert resolver.get_file_path(wid) == root / Path(prefix) / Path('9b.json')
assert resolver.get_file_path(wid2) == root / Path(prefix) / Path('9a.json')
print(f"{prefix}\t: {resolver.get_file_path(wid)}")
print(f"{prefix}\t: {resolver.get_file_path(wid2)}")
shutil.rmtree(root_dir)

prefix = "dc/20"
(root / Path(prefix)).mkdir(parents=True, exist_ok=True, mode=711)
assert resolver.get_file_path(wid3) == root / Path(prefix) / Path('ce.json')
print(f"{prefix}\t: {resolver.get_file_path(wid3)}")
# shutil.rmtree(root_dir)

prefix = "dc/20.json"
(root).mkdir(parents=True, exist_ok=True, mode=711)
(root / Path(prefix)).touch(exist_ok=True)
assert resolver.get_file_path(wid3) == root / Path(prefix)
print(f"{prefix}\t: {resolver.get_file_path(wid3)}")
shutil.rmtree(root_dir)
