from pathlib import Path
code=Path(__file__).with_name('apply_r10_landscape.py').read_text().replace("'revision10'","'revision11'").replace('/R10','/R11').replace('BlockOut_R10','BlockOut_R11').replace('r10_height_rt','r11_height_rt')
exec(compile(code,'apply_r11_heightmap','exec'),{'__file__':__file__})
