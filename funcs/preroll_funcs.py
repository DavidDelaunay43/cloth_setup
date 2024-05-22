# Pre-roll funcs


from maya import cmds


def get_preroll_frames(
    start_anim_frame: float,
    start_pose_offset: float = -25.0,
    inter_pose_offset: float = -125.0, 
    bind_pose_offset: float = -150.0 
) -> dict:

    start_pose_frame: float = start_anim_frame + start_pose_offset
    inter_pose_frame: float = start_anim_frame + inter_pose_offset
    bind_pose_frame: float = start_anim_frame + bind_pose_offset

    preroll_frames_dict ={
        'start_anim_frame': start_anim_frame,
        'start_pose_frame': start_pose_frame,
        'inter_pose_frame': inter_pose_frame,
        'bind_pose_frame': bind_pose_frame
    }

    return preroll_frames_dict


def set_preroll_time_slider(preroll_frames: dict) -> None:

    bind_pose_frame: float = preroll_frames['bind_pose_frame']
    end_frame: float = cmds.playbackOptions(query=True, maxTime=True)
    cmds.playbackOptions(minTime = bind_pose_frame, maxTime = end_frame)


def set_key_frame(controler: str) -> None:

    for attribute in cmds.listAttr(controler, keyable = True):
        cmds.setKeyframe(f'{controler}.{attribute}')


def set_attributes_to_defaults(controler: str) -> None:

    attribute_dict = {
        'translateX': 0.0,
        'translateY': 0.0,
        'translateZ': 0.0,
        'rotateX': 0.0,
        'rotateY': 0.0,
        'rotateZ': 0.0,
        'scaleX': 1.0,
        'scaleY': 1.0,
        'scaleZ': 1.0
    }

    for attribute in cmds.listAttr(controler, keyable = True):
        if not cmds.attributeQuery(attribute, node = controler, keyable = True):
            continue
        
        if not attribute in attribute_dict.keys():
            continue

        default_value: float = attribute_dict[attribute]
        cmds.setAttr(f'{controler}.{attribute}', default_value)


def set_preroll_keys(controlers: list, preroll_frames: dict) -> None:

    # set start pose
    cmds.currentTime(preroll_frames['start_pose_frame'])
    for ctrl in controlers:
        set_key_frame(ctrl)

    # set inter pose
    cmds.currentTime(preroll_frames['inter_pose_frame'])
    for ctrl in controlers:
        set_attributes_to_defaults(ctrl)
        set_key_frame(ctrl)

    # set bind pose
    cmds.currentTime(preroll_frames['bind_pose_frame'])
    for ctrl in controlers:
        set_key_frame(ctrl)


def set_preroll(controlers: list, preroll_values: list, update_nucleus: bool = True) -> None:

    preroll_frames: dict = get_preroll_frames(*preroll_values)
    set_preroll_time_slider(preroll_frames)
    set_preroll_keys(controlers, preroll_frames)

    if not update_nucleus:
        return
    
    bind_pose_frame: float = preroll_frames['bind_pose_frame']

    for nucleus_node in cmds.ls(type = 'nucleus'):
        cmds.setAttr(f'{nucleus_node}.startFrame', bind_pose_frame)
