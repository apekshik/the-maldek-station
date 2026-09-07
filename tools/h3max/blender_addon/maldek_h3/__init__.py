# SPDX-License-Identifier: GPL-3.0-or-later
bl_info={'name':'Maldek H3 Look Development','author':'Maldek Station project','version':(0,1,0),'blender':(5,0,0),'location':'3D View > Sidebar > Maldek H3','category':'Render'}
import bpy,json,subprocess,time,uuid,re
from pathlib import Path
from mathutils import Vector
from . import core,transport

BASE=Path('C:/Users/apek-anna/Developer/the-maldek-station')
DEFAULT_FFMPEG='C:/Users/apek-anna/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
_job=None
_players={}

class Preferences(bpy.types.AddonPreferences):
    bl_idname=__package__
    key_file:bpy.props.StringProperty(name='Local key file',subtype='FILE_PATH',default=str(BASE/'tools/h3max/.env.local'))
    output:bpy.props.StringProperty(name='Preview history',subtype='DIR_PATH',default=str(BASE/'art/blender/h3max/outputs/interactive'))
    ffmpeg:bpy.props.StringProperty(name='FFmpeg executable',subtype='FILE_PATH',default=DEFAULT_FFMPEG)
    def draw(self,context):
        for name in ('key_file','output','ffmpeg'):self.layout.prop(self,name)
        self.layout.label(text='The key stays in the local file, outside the Blender scene.')

class Result(bpy.types.PropertyGroup):
    path:bpy.props.StringProperty()
    settings:bpy.props.StringProperty()

class Settings(bpy.types.PropertyGroup):
    fog:bpy.props.FloatProperty(name='Fog',min=0,max=1,default=.85)
    darkness:bpy.props.FloatProperty(name='Darkness',min=0,max=1,default=.85)
    warmth:bpy.props.FloatProperty(name='Warm / cool balance',min=0,max=1,default=.55)
    wetness:bpy.props.FloatProperty(name='Wetness',min=0,max=1,default=.7)
    realism:bpy.props.EnumProperty(name='Interpretation',items=[('PHOTO','Photographic','Allow surface and small construction reinterpretation'),('FAITHFUL','Closer to mesh','Favor the existing small construction details')],default='PHOTO')
    direction:bpy.props.StringProperty(name='Art direction',default='Isolated mountain station, unsettling quiet, dim warm lamps against cold fog. Conceal fine detail in shadow. No neon or additional buildings.')
    mode:bpy.props.EnumProperty(name='Camera motion',items=[('STILL','Current view · fast','One image guide; five-second H3 hold'),('PAN','Subtle slide','Five-second local camera-right move'),('DOLLY','Subtle approach','Five-second forward move'),('ANIMATION','Existing animation','Sample the active camera over the specified source frame range')],default='STILL')
    distance:bpy.props.FloatProperty(name='Travel (scene units)',min=-10,max=10,default=.6)
    guide:bpy.props.EnumProperty(name='Guide',items=[('LINES','Linework','Remove source color and shading'),('COLOR','Eevee color','Keep more source appearance')],default='LINES')
    resolution:bpy.props.EnumProperty(name='H3 resolution',items=[('480P','480p · draft',''),('768P','768p · detailed','')],default='480P')
    seed:bpy.props.IntProperty(name='Seed',default=73419,min=0)
    frame_start:bpy.props.IntProperty(name='First frame',default=1)
    frame_end:bpy.props.IntProperty(name='Last frame',default=120)
    status:bpy.props.StringProperty(default='Ready — manual generation only')
    preset_name:bpy.props.StringProperty(name='Preset name',default='Dark fog')
    history:bpy.props.CollectionProperty(type=Result)
    selected:bpy.props.IntProperty(default=0,min=0)

def prefs(context):return context.preferences.addons[__package__].preferences
def root(context):return Path(bpy.path.abspath(prefs(context).output))
def restore(p,data):
    for key in core.FIELDS:
        if key in data:setattr(p,key,data[key])

def preview(area,path):
    if Path(path).suffix.lower()=='.mp4':
        area.type='CLIP_EDITOR';clip=bpy.data.movieclips.load(path,check_existing=True)
        area.spaces.active.clip=clip;area.spaces.active.show_region_ui=False;area.spaces.active.show_region_toolbar=False
        _players[area.as_pointer()]=(clip,time.monotonic())
    else:
        area.type='IMAGE_EDITOR';area.spaces.active.image=bpy.data.images.load(path,check_existing=True)

def split(context,area,direction,factor):
    before={a.as_pointer() for a in context.screen.areas}
    with context.temp_override(area=area):bpy.ops.screen.area_split(direction=direction,factor=factor)
    return next(a for a in context.screen.areas if a.as_pointer() not in before)

class UseView(bpy.types.Operator):
    bl_idname='maldek_h3.use_view';bl_label='Use Current View';bl_options={'REGISTER','UNDO'}
    @classmethod
    def poll(cls,c):return c.area and c.area.type=='VIEW_3D'
    def execute(self,c):
        region=c.space_data.region_3d
        c.scene.render.resolution_x=1280;c.scene.render.resolution_y=720
        c.scene.render.pixel_aspect_x=1;c.scene.render.pixel_aspect_y=1
        if region.view_perspective=='CAMERA' and c.scene.camera:
            c.scene.maldek_h3.status='Using active camera: '+c.scene.camera.name;return {'FINISHED'}
        cam=bpy.data.objects.get('H3_Look_Camera')
        if cam is None:
            cam=bpy.data.objects.new('H3_Look_Camera',bpy.data.cameras.new('H3_Look_Camera'));c.scene.collection.objects.link(cam)
        cam.matrix_world=region.view_matrix.inverted();cam.data.lens=c.space_data.lens
        cam.data.type='ORTHO' if region.view_perspective=='ORTHO' else 'PERSP'
        if cam.data.type=='ORTHO':cam.data.ortho_scale=region.view_distance
        c.scene.camera=cam;region.view_perspective='CAMERA'
        c.scene.maldek_h3.status='Camera set from viewport; frame shown is the capture.'
        return {'FINISHED'}

class Run(bpy.types.Operator):
    bl_idname='maldek_h3.run';bl_label='Generate Preview'
    bl_description='Capture this scene copy and submit one paid five-second H3 preview'
    generate:bpy.props.BoolProperty(default=True)
    @classmethod
    def poll(cls,c):return _job is None and c.scene.camera is not None
    def execute(self,c):
        global _job
        p=c.scene.maldek_h3;pr=prefs(c)
        try:
            if not Path(bpy.path.abspath(pr.ffmpeg)).is_file():raise ValueError('Set the FFmpeg path in add-on preferences')
            if self.generate:transport.load_key(bpy.path.abspath(pr.key_file))
            if p.mode=='ANIMATION' and p.frame_end<=p.frame_start:raise ValueError('Last frame must follow first frame')
            folder=root(c)/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]);folder.mkdir(parents=True)
            config=core.values(p);config.update(generate=self.generate,key_file=bpy.path.abspath(pr.key_file),ffmpeg=bpy.path.abspath(pr.ffmpeg),
                current_frame=c.scene.frame_current,view_layer=c.view_layer.name,camera=c.scene.camera.name,
                camera_matrix=[list(row) for row in c.scene.camera.matrix_world],source_file=bpy.data.filepath)
            core.save(folder/'settings.json',config)
            # Capture all unsaved edits in an isolated copy; never save over the user's file.
            bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),copy=True,compress=True)
            log=(folder/'worker.log').open('w',encoding='utf-8')
            process=subprocess.Popen([bpy.app.binary_path,'--background','--factory-startup',str(folder/'scene.blend'),'--python-exit-code','1',
                '--python',str(Path(__file__).with_name('worker.py')),'--',str(folder)],stdout=log,stderr=subprocess.STDOUT,creationflags=0x08000000)
            _job=dict(process=process,log=log,folder=folder,scene=c.scene,config=config)
            p.status='Starting isolated capture — viewport remains editable'
            return {'FINISHED'}
        except Exception as error:
            self.report({'ERROR'},str(error) if isinstance(error,ValueError) else type(error).__name__+' — capture could not start')
            return {'CANCELLED'}

class Compare(bpy.types.Operator):
    bl_idname='maldek_h3.compare';bl_label='Compare Previous / Selected'
    @classmethod
    def poll(cls,c):return bool(c.scene.maldek_h3.history) and c.area and c.area.type=='VIEW_3D'
    def execute(self,c):
        p=c.scene.maldek_h3;i=min(p.selected,len(p.history)-1)
        areas=[a for a in c.screen.areas if a.type in ('CLIP_EDITOR','IMAGE_EDITOR')]
        if not areas:areas=[split(c,c.area,'VERTICAL',.55)]
        window=c.window;screen=c.screen
        paths=[p.history[i].path]+([p.history[i-1].path] if i>0 else [])
        def finish():
            areas.sort(key=lambda a:a.y,reverse=True)
            for area,path in zip(areas,paths):preview(area,path)
            def fit():
                for area in areas:
                    region=next((r for r in area.regions if r.type=='WINDOW'),None)
                    if region:
                        with bpy.context.temp_override(window=window,area=area,region=region):
                            if area.type=='CLIP_EDITOR':bpy.ops.clip.view_all(fit_view=True)
                            elif area.type=='IMAGE_EDITOR':bpy.ops.image.view_all(fit_view=True)
                return None
            bpy.app.timers.register(fit,first_interval=.3)
            return None
        def arrange():
            if i>0 and len(areas)<2:
                with bpy.context.temp_override(window=window,screen=screen,area=areas[0]):
                    areas.append(split(bpy.context,areas[0],'HORIZONTAL',.5))
            bpy.app.timers.register(finish,first_interval=.3)
            return None
        bpy.app.timers.register(arrange,first_interval=.3)
        p.status='Top: selected result. Bottom: previous result.' if i>0 else 'Showing selected result'
        return {'FINISHED'}

class Restore(bpy.types.Operator):
    bl_idname='maldek_h3.restore';bl_label='Restore Selected Settings';bl_options={'UNDO'}
    @classmethod
    def poll(cls,c):return bool(c.scene.maldek_h3.history)
    def execute(self,c):
        p=c.scene.maldek_h3;r=p.history[min(p.selected,len(p.history)-1)]
        if not r.settings:self.report({'INFO'},'Imported clip has no panel settings');return {'CANCELLED'}
        restore(p,json.loads(r.settings));p.status='Restored mood and generation settings; camera unchanged'
        return {'FINISHED'}

class Preset(bpy.types.Operator):
    bl_idname='maldek_h3.preset';bl_label='Look Preset'
    load:bpy.props.BoolProperty(default=False)
    def execute(self,c):
        p=c.scene.maldek_h3;name=re.sub(r'[^\w -]','',p.preset_name).strip()
        if not name:self.report({'ERROR'},'Enter a preset name');return {'CANCELLED'}
        path=root(c)/'presets'/(name+'.json')
        try:
            if self.load:restore(p,json.loads(path.read_text()))
            else:path.parent.mkdir(parents=True,exist_ok=True);core.save(path,core.values(p))
        except (OSError,ValueError):self.report({'ERROR'},'Preset unavailable or invalid');return {'CANCELLED'}
        p.status=('Loaded ' if self.load else 'Saved ')+name;return {'FINISHED'}

class History(bpy.types.Operator):
    bl_idname='maldek_h3.history';bl_label='Refresh History'
    def execute(self,c):
        p=c.scene.maldek_h3;known={r.path for r in p.history}
        for path in sorted(root(c).glob('*/status.json')):
            try:
                state=json.loads(path.read_text());file=state.get('path','')
                if state['stage']!='complete' or not Path(file).is_file() or file in known:continue
                item=p.history.add();item.name=path.parent.name+' · '+state.get('label','Preview');item.path=file
                item.settings=(path.parent/'settings.json').read_text();known.add(file)
            except (OSError,ValueError,KeyError):continue
        p.selected=max(0,len(p.history)-1);return {'FINISHED'}

class MALDEK_UL_results(bpy.types.UIList):
    def draw_item(self,c,layout,data,item,icon,active_data,active_propname,index):layout.label(text=item.name,icon='FILE_MOVIE' if item.path.endswith('.mp4') else 'IMAGE_DATA')

class Panel(bpy.types.Panel):
    bl_label='Maldek · H3 Look Development';bl_idname='MALDEK_PT_h3';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Maldek H3'
    def draw(self,c):
        l=self.layout;p=c.scene.maldek_h3
        l.operator('maldek_h3.use_view',icon='CAMERA_DATA');l.prop(c.scene,'camera')
        l.prop(p,'mode')
        if p.mode in ('PAN','DOLLY'):l.prop(p,'distance')
        if p.mode=='ANIMATION':r=l.row();r.prop(p,'frame_start');r.prop(p,'frame_end')
        box=l.box();box.label(text='H3 art direction · next generation')
        for name in ('fog','darkness','warmth','wetness'):box.prop(p,name,slider=True)
        box.prop(p,'realism');box.prop(p,'direction')
        box.label(text='H3 mood controls; scene fog unchanged.')
        l.prop(c.scene.view_settings,'exposure',text='Local viewport exposure')
        l.prop(p,'guide');l.prop(p,'resolution');l.prop(p,'seed')
        row=l.row();row.operator('maldek_h3.run',text='Check Guide').generate=False;row.operator('maldek_h3.run',text='Generate Preview',icon='PLAY').generate=True
        l.label(text='Generate: one paid 5-second clip.')
        l.label(text='16:9 capture · manual generation')
        for start in range(0,len(p.status),48):l.label(text=p.status[start:start+48])
        box=l.box();box.prop(p,'preset_name');r=box.row();r.operator('maldek_h3.preset',text='Save Look').load=False;r.operator('maldek_h3.preset',text='Load Look').load=True
        l.template_list('MALDEK_UL_results','',p,'history',p,'selected',rows=3)
        l.operator('maldek_h3.history',icon='FILE_REFRESH');l.operator('maldek_h3.compare');l.operator('maldek_h3.restore')

def tick():
    global _job
    if _job:
        j=_job
        try:
            state=json.loads((j['folder']/'status.json').read_text()) if (j['folder']/'status.json').exists() else {}
            p=j['scene'].maldek_h3;stage=state.get('stage','starting')
            p.status=f"Capturing guide {state.get('frame',0)}/{state.get('total',0)}" if stage=='capturing' else ('H3 generating — editing remains available' if stage=='generating' else stage)
            if j['process'].poll() is not None:
                j['log'].close()
                if stage=='complete':
                    r=p.history.add();r.name=time.strftime('%H:%M:%S')+' · '+state['label'];r.path=state['path'];r.settings=json.dumps(j['config'])
                    p.selected=len(p.history)-1;p.status='Ready — select Compare to view the result'
                else:p.status=state.get('message','Worker stopped; inspect '+str(j['folder']/'worker.log'))
                _job=None
        except (ReferenceError,AttributeError):
            # A scene was closed. The worker continues independently; history can be refreshed later.
            j['log'].close();_job=None
        except (OSError,ValueError):pass
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='CLIP_EDITOR' and area.as_pointer() in _players:
                clip,start=_players[area.as_pointer()]
                try:area.spaces.active.clip_user.frame_current=1+int((time.monotonic()-start)*clip.fps)%max(1,clip.frame_duration)
                except ReferenceError:pass
                area.tag_redraw()
            elif area.type=='VIEW_3D':area.tag_redraw()
    return .1

CLASSES=(Preferences,Result,Settings,UseView,Run,Compare,Restore,Preset,History,MALDEK_UL_results,Panel)
def register():
    for cls in CLASSES:bpy.utils.register_class(cls)
    bpy.types.Scene.maldek_h3=bpy.props.PointerProperty(type=Settings)
    bpy.app.timers.register(tick,persistent=True)
def unregister():
    if bpy.app.timers.is_registered(tick):bpy.app.timers.unregister(tick)
    del bpy.types.Scene.maldek_h3
    for cls in reversed(CLASSES):bpy.utils.unregister_class(cls)
