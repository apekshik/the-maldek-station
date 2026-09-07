import runpy
from pathlib import Path
p=Path(__file__).with_name('render_r11.py')
code=p.read_text()
a=code.index('shots=');b=code.index("state=",a)
code=code[:a]+"shots=[('06_final_bridge_structure',(32,42,20),(15,20,4),True),('07_final_maintenance_layout',(14,-32,15),(29,-16,0),True)]\n"+code[b:]
exec(compile(code,str(p),'exec'),{'__file__':str(p)})
