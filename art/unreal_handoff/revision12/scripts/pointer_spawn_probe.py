import unreal
RESULT={'spawn_tools':[x for x in dir(unreal.GameplayStatics) if 'spawn' in x],'world':[x for x in dir(unreal.World) if 'spawn' in x]}
