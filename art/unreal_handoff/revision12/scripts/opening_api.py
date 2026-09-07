import unreal
RESULT={n:[x for x in dir(getattr(unreal,n)) if 'widget' in x.lower()] for n in dir(unreal) if 'Widget' in n and 'Library' in n}
