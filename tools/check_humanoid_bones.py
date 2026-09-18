"""Blender: compare shipped animation rigs to vanilla male/female bone layout."""
import bpy, json, sys
from pathlib import Path
sys.path.insert(0,str(Path('build/toolchain/blender_wheel').resolve()))
game=Path(r'C:\Program Files (x86)\Steam\steamapps\common\Kenshi')
paths={
    'male':game/'data/character/meshes/male_skeleton/male_skeleton.skeleton',
    'female':game/'data/character/meshes/female_skeleton/female_skeleton.skeleton',
    'queen':game/'data/character/meshes/stick_person/Hive_Queen.skeleton',
    'smoking':Path('build/420_Smoking/assets/420_smoking_male.skeleton').resolve(),
    'reclined':Path('build/420_Smoking/assets/420_reclined_male.skeleton').resolve(),
    'smoking_female':Path('build/420_Smoking/assets/420_smoking_female.skeleton').resolve(),
    'reclined_female':Path('build/420_Smoking/assets/420_reclined_female.skeleton').resolve(),
}
bones={}
bpy.context.scene.render.fps=25
for name,path in paths.items():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for action in list(bpy.data.actions): bpy.data.actions.remove(action)
    animated=name.endswith('_female')
    getattr(bpy.ops,'import').kenshi_ogre_skeleton_objects(filepath=str(path),import_animations=animated,use_selected_skeleton=False)
    rig=bpy.context.view_layer.objects.active
    bones[name]={b.name:(b.parent.name if b.parent else None) for b in rig.data.bones}
    if animated:
        assert len(bpy.data.actions)==2
        for action in bpy.data.actions:
            assert abs((action.frame_range[1]-action.frame_range[0])/25-12)<0.001
            rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
            for track in rig.animation_data.nla_tracks: track.mute=True
            bpy.context.scene.frame_set(80)
            inhaling=rig.pose.bones['Bip01 Prop2'].matrix.translation.copy()
            bpy.context.scene.frame_set(125)
            assert (rig.pose.bones['Bip01 Prop2'].matrix.translation-inhaling).length>1
report={}
for target in ['male','female','queen']:
    report[target]={}
    for animation in (['smoking_female','reclined_female'] if target=='female' else ['smoking','reclined']):
        missing=sorted(set(bones[animation])-set(bones[target]))
        mismatch=[b for b in bones[animation] if b in bones[target] and bones[animation][b]!=bones[target][b]]
        report[target][animation]={'missing_bones':missing,'parent_mismatches':mismatch}
Path('qa/humanoid_bone_checks.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
assert all(not v['missing_bones'] and not v['parent_mismatches'] for target in report.values() for v in target.values())
