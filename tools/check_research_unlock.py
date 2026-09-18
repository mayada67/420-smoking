"""Check research cost and ensure the deployed candidate changes only that gate."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent/'vendor'))
import kenshi

reader = kenshi.ModFileReader(Path('build/420_Smoking/420_Smoking.mod'))
records = reader.records
tech = records['30-420_Smoking.mod']
assert tech['fields']['int']['level'] == 3
assert tech['fields']['int']['time'] == 4
assert tech['extra']['cost'] == {'16855-nodes_otto1.mod': (3,0,0), '1965-gamedata.base': (3,0,0)}
assert set(tech['extra']['enable buildings']) == {f'{n}-420_Smoking.mod' for n in [21,23,24,25,26,27,28]}
assert set(tech['extra']['enable item']) == {'1-420_Smoking.mod','2-420_Smoking.mod'}
reader.handle.close()
print('PASS: research level 3, 3 ordinary Books + 3 hemp; 7 buildings and 2 recipes unlock.')
