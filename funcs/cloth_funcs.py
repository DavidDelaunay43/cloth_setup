# Cloth funcs

from maya.api import OpenMaya as om
from maya import cmds, mel
from typing import Literal


ALL_GRP = "ALL"
INIT_MESH_GRP = "initMesh_grp"
CLOTH_GRP = "cloth_grp"
HI_GRP = "hi_grp"
OUTPUT_GRP = "output_grp"
CLOTH_SET = "CLOTH_ABC"


def ignore_namespace(node: str) -> str:
    """
    """
    if ':' in node:
        node = node.split(':')[-1]

    return node


def blendshape(driver_mesh: str, deformed_mesh: str) -> str:
    """
    """

    blendshape_node = cmds.blendShape(driver_mesh, deformed_mesh, name = f'BShape_{deformed_mesh}')
    if isinstance(blendshape_node, list):
        blendshape_node = blendshape_node[0]
    cmds.setAttr(f"{blendshape_node}.{ignore_namespace(driver_mesh)}", 1.0)

    return blendshape_node


def create_passive_collider(mesh: str, nucleus_node: str) -> tuple:
    """
    Create a passive collider for the specified mesh.

    Parameters:
        mesh (str): The name of the mesh to create the collider for.
        nucleus_node (str): The name of the nucleus node to connect the collider to.

    Returns:
        tuple: A tuple containing the names of the created nRigid node and nRigidShape node.
    """

    nrigid_shape = f'{mesh}_nRigidShape'
    cmds.createNode('nRigid', name = nrigid_shape)
    nrigid_node: str = cmds.listRelatives(nrigid_shape, parent = True)[0]
    nrigid_node = cmds.rename(nrigid_node, f'{mesh}_nRigid')
    cmds.setAttr(f'{nrigid_shape}.thickness', 0.0)
    cmds.select(clear = True)

    cmds.connectAttr(f'{mesh}.worldMesh[0]', f'{nrigid_shape}.inputMesh')
    cmds.connectAttr('time1.outTime', f'{nrigid_shape}.currentTime')
    cmds.connectAttr(f'{nucleus_node}.startFrame', f'{nrigid_shape}.startFrame')
    
    for i in range(10):
        try:
            cmds.connectAttr(f'{nrigid_shape}.currentState', f'{nucleus_node}.inputPassive[{i}]')
            cmds.connectAttr(f'{nrigid_shape}.startState', f'{nucleus_node}.inputPassiveStart[{i}]')
            break
        except RuntimeError:
            continue

    return nrigid_node, nrigid_shape


def duplicate_mesh(mesh: str, new_name: str) -> str:
    """
    Duplicate a mesh with a new name.

    Parameters:
        mesh (str): The name of the mesh to duplicate.
        new_name (str): The new name for the duplicated mesh.

    Returns:
        str: The name of the duplicated mesh.
    """

    om.MGlobal.displayInfo(f'Mesh to duplicate : {mesh}')
    cmds.duplicate(mesh, name = new_name)
    shapes = cmds.listRelatives(new_name, shapes = True, fullPath = True)
    for shape in shapes:
        if cmds.getAttr(f'{shape}.intermediateObject') == 1:
            cmds.delete(shape)

        else:
            cmds.rename(shape, f'{new_name}Shape')

    return new_name


def ensure_cloth_groups() -> None:
    """
    Ensure the existence of cloth-related groups in the scene.
    Creates groups if they do not exist.
    """

    ALL_GRP: str = "ALL"

    if cmds.objExists(ALL_GRP):
        return

    group_all: str = cmds.group(empty=True, world=True, name=ALL_GRP)
    group_names = (INIT_MESH_GRP, CLOTH_GRP, HI_GRP, OUTPUT_GRP)

    for grp_name in group_names:
        grp = cmds.group(empty=True, world=True, name=grp_name)
        cmds.parent(grp, group_all)

    cmds.sets(empty = True, name = CLOTH_SET)

    cmds.select(clear = True)


def ensure_nsystem_group(setup_prefix: str) -> str:
    """
    Ensure the existence of a nucleus system group in the scene.

    Parameters:
        setup_prefix (str): Prefix for the name of the nucleus system group.

    Returns:
        str: The name of the nucleus system group.
    """

    nsystem_grp: str = f'{setup_prefix}_nsystem_grp'
    if not cmds.objExists(nsystem_grp):
        cmds.group(empty = True, name = nsystem_grp, parent = CLOTH_GRP)
        cmds.group(empty = True, name = f'{setup_prefix}_nConstraint_grp', parent = nsystem_grp)

    return nsystem_grp


def ensure_colliders_group(setup_prefix: str) -> str:
    """
    Ensure the existence of a colliders group in the scene.

    Parameters:
        setup_prefix (str): Prefix for the name of the colliders group.

    Returns:
        str: The name of the colliders group.
    """

    colliders_grp: str = f'{setup_prefix}_colliders_grp'
    nsystem_grp: str = ensure_nsystem_group(setup_prefix)

    if not cmds.objExists(colliders_grp):
        cmds.group(empty = True, name = colliders_grp, parent = nsystem_grp)

    return colliders_grp


def ensure_init_mesh(deformed_mesh: str) -> str:
    """
    Ensure the existence of an initial mesh for cloth simulation.

    Parameters:
        deformed_mesh (str): The name of the deformed mesh.

    Returns:
        str: The name of the initial mesh.
    """

    ensure_cloth_groups()

    PFX: str = "initMesh"
    init_mesh = f"{PFX}_{ignore_namespace(deformed_mesh)}"

    if cmds.objExists(init_mesh):
        return init_mesh

    om.MGlobal.displayInfo(f'Create initMesh from : {deformed_mesh}')
    duplicate_mesh(deformed_mesh, new_name=init_mesh)

    blendshape(deformed_mesh, init_mesh)

    cmds.parent(init_mesh, INIT_MESH_GRP)

    return init_mesh


def create_cloth(simu_nmesh: str, setup_prefix: str) -> tuple:
    """
    Create a cloth simulation setup.

    Parameters:
        simu_nmesh (str): The name of the simulated mesh.
        setup_prefix (str): Prefix for the names of created objects.

    Returns:
        tuple: A tuple containing the names of the created ncloth shape and nucleus node.
    """

    ensure_cloth_groups()
    nsystem_grp: str = ensure_nsystem_group(setup_prefix)

    cmds.select(simu_nmesh)

    mel.eval('createNCloth 0; sets -e -forceElement initialShadingGroup;')
    ncloth_shape: str = cmds.ls(selection = True)[0]
    ncloth_transform: str = cmds.listRelatives(ncloth_shape, parent = True)[0]
    nucleus_node: str = cmds.listConnections(ncloth_shape, type = 'nucleus')[0]
    nucleus_node = cmds.rename(nucleus_node, f'{setup_prefix}_nucleus')

    ncloth_transform = cmds.rename(ncloth_transform, f'{setup_prefix}_ncloth')

    start_frame: float = cmds.playbackOptions(query = True, minTime = True)
    cmds.setAttr(f'{nucleus_node}.startFrame', start_frame)

    cmds.parent(simu_nmesh, nsystem_grp)
    cmds.parent(ncloth_transform, nsystem_grp)
    cmds.parent(nucleus_node, nsystem_grp)

    cmds.select(clear = True)

    return ncloth_shape, nucleus_node


def create_collider_mesh(init_mesh: str, nucleus_node: str, setup_prefix: str, collider_suffix: str) -> None:
    """
    Create a collider mesh.

    Parameters:
        init_mesh (str): The name of the initial mesh.
        nucleus_node (str): The name of the nucleus node to connect the collider to.
        setup_prefix (str): Prefix for the names of created objects.
        collider_suffix (str): Suffix for the name of the collider.
    """

    ensure_cloth_groups()
    setup_colliders_grp: str = ensure_colliders_group(setup_prefix)
    collider_grp: str = cmds.group(empty = True, name = f'{setup_prefix}_collider_{collider_suffix}_grp', parent = setup_colliders_grp)

    collider_mesh: str = duplicate_mesh(init_mesh, new_name = f'{setup_prefix}_collider_{collider_suffix}')
    cmds.parent(collider_mesh, collider_grp)

    blendshape(init_mesh, collider_mesh)

    nrigid_transform, _ = create_passive_collider(collider_mesh, nucleus_node)
    cmds.parent(nrigid_transform, collider_grp)
    cmds.select(clear = True)


def wrap(high_mesh: str, low_mseh: str) -> str:

    mel_cmd: str = f'''
        select -cl  ;
        select -r {high_mesh} ;
        select -add {low_mseh} ;
        doWrapArgList "7" { "1", "0", "10", "1", "0", "0", "0", "0" };
        '''
    
    mel.eval(mel_cmd)

    high_mesh_shape = cmds.listRelatives(high_mesh, shapes = True)
    if high_mesh_shape:
        high_mesh_shape = high_mesh_shape[0]

    wrap_node = cmds.listConnections(high_mesh_shape, type = 'wrap')
    if wrap_node:
        return wrap_node[0]


def ensure_control_joint_output() -> str:
    jnt: str = f'JNT_OUTPUT'
    ctrl: str = f'CTRL_OUTPUT'

    if cmds.objExists(jnt):
        return jnt

    cmds.select(clear = True)
    cmds.joint(name = jnt)
    cmds.circle(name = ctrl, radius = 7.0, normal = [0, 1, 0], constructionHistory = False)[0]
    cmds.parent(ctrl, OUTPUT_GRP)
    cmds.parent(jnt, ctrl)
    cmds.setAttr(f'{jnt}.v', 0)
    cmds.select(clear = True)

    return jnt


def create_output_setup(high_mesh: str, setup_prefix: str):
    """
    """

    ensure_cloth_groups()

    output_mesh: str = duplicate_mesh(high_mesh, f'outputMesh_{setup_prefix}')
    blendshape(high_mesh, output_mesh)
    cmds.parent(output_mesh, OUTPUT_GRP)
    cmds.sets(output_mesh, add = CLOTH_SET)

    jnt: str = ensure_control_joint_output()
    cmds.skinCluster(jnt, output_mesh, maximumInfluences = 1)


def create_hi_setup(simu_nmesh: str, hi_mesh: str, setup_prefix: str, wrap_node: Literal['wrap', 'cvwrap'] = 'cvwrap'):
    """
    Create a high-resolution setup for cloth simulation.

    Parameters:
        simu_nmesh (str): The name of the simulated mesh.
        hi_mesh (str): The name of the high-resolution mesh.
        setup_prefix (str): Prefix for the names of created objects.
    """

    ensure_cloth_groups()

    hi_grp: str = cmds.group(empty = True, name = f'{setup_prefix}_hi_grp', parent = HI_GRP)
    cmds.parent(hi_mesh, hi_grp)

    simu_driver_mesh = duplicate_mesh(simu_nmesh, new_name = f'{setup_prefix}_simu_driver')
    cmds.parent(simu_driver_mesh, hi_grp)

    blendshape(simu_nmesh, simu_driver_mesh)

    if wrap_node == 'cvwrap':
        cmds.cvWrap(hi_mesh, simu_driver_mesh, name=f'cvWrap_{hi_mesh}', radius=0.1)

    else:
        wrap(hi_mesh, simu_driver_mesh)

    # output mesh
    

    cmds.select(clear = True)


def create_full_setup(setup_prefix: str, low_mesh: str, high_mesh: str, colliders: dict = None) -> None:
    """
    Create a full cloth simulation setup.

    Parameters:
        setup_prefix (str): Prefix for the names of created objects.
        low_mesh (str): The name of the low-resolution mesh.
        high_mesh (str): The name of the high-resolution mesh.
        colliders (dict, optional): A dictionary containing collider meshes and their suffixes.
    """
    
    ensure_cloth_groups()
    ensure_nsystem_group(setup_prefix)

    simu_nmesh = duplicate_mesh(low_mesh, new_name = f'{setup_prefix}_simu_nmesh')
    _, nucleus_node = create_cloth(simu_nmesh, setup_prefix)

    himesh = duplicate_mesh(high_mesh, new_name = f'{setup_prefix}_hiMesh')
    create_hi_setup(simu_nmesh = simu_nmesh, hi_mesh = himesh, setup_prefix = setup_prefix)
    create_output_setup(himesh, setup_prefix)

    if not colliders:
        return
    
    for collider, collider_suffix in colliders.items():
        init_mesh = ensure_init_mesh(deformed_mesh = collider)
        create_collider_mesh(init_mesh, nucleus_node, setup_prefix, collider_suffix)
