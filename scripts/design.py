"""Restrained editorial tokens shared by the website and PDF generator."""
import json
from content import ROOT
DESIGN = json.loads((ROOT / 'data/design.json').read_text())
PALETTE = DESIGN['palette']['light']
TYPE = DESIGN['typography']
COLUMNS = DESIGN['teachingColumns']
assert sum(COLUMNS) == 100

def css_tokens():
    values = [f'--{name}:light-dark({value},{DESIGN["palette"]["dark"][name]});'
              for name,value in PALETTE.items()]
    values += [f'--font-body-size:{TYPE["webBody"]}px;', f'--font-secondary-size:{TYPE["webSecondary"]}px;',
               f'--font-body-family:{TYPE["webBodyFamily"]};',f'--font-display-family:{TYPE["webTitle"]};']
    values += [f'--space-{name}:{value}px;' for name,value in DESIGN['spacing'].items()]
    values += [f'--teaching-{name}-width:{value}%;' for name,value in zip(['period','provider','course'],COLUMNS)]
    return ':root{' + ''.join(values) + '}'
