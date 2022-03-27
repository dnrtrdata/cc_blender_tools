
import bpy
import mathutils
import addon_utils
from . import utils
from . import geom
from . import properties
from . import modifiers

#   METARIG_BONE, CC_BONE_HEAD, CC_BONE_TAIL, LERP_FROM, LERP_TO
#   '-' before CC_BONE_HEAD means to copy the tail position, not the head
#   '-' before CC_BONE_TAIL means to copy the head position, not the tail
BONE_MAPPINGS = [
    # Spine, Neck & Head:
    # spine chain
    ["spine", "CC_Base_Hip", ""],
    ["spine.001", "CC_Base_Waist", ""],
    ["spine.002", "CC_Base_Spine01", ""],
    ["spine.003", "CC_Base_Spine02", "-CC_Base_NeckTwist01"],
    ["spine.004", "CC_Base_NeckTwist01", ""],
    ["spine.005", "CC_Base_NeckTwist02", ""],
    ["spine.006", "CC_Base_Head", "CC_Base_Head"], # special case
    ["face", "CC_Base_FacialBone", "CC_Base_FacialBone"], # special case
    ["pelvis", "CC_Base_Pelvis", "CC_Base_Pelvis"],

    # Left Breast
    #["breast.L", "CC_Base_L_RibsTwist", "CC_Base_L_Breast"],
    # Right Breast
    #["breast.R", "CC_Base_R_RibsTwist", "CC_Base_R_Breast"],

    # Left Breast
    ["breast.L", "CC_Base_L_Breast", "CC_Base_L_Breast"],
    # Right Breast
    ["breast.R", "CC_Base_R_Breast", "CC_Base_R_Breast"],

    # Left Leg:
    ["thigh.L", "CC_Base_L_Thigh", ""],
    ["shin.L", "CC_Base_L_Calf", ""],
    ["foot.L", "CC_Base_L_Foot", ""],
    ["toe.L", "CC_Base_L_ToeBase", "CC_Base_L_ToeBase"],

    # Left Arm:
    ["shoulder.L", "CC_Base_L_Clavicle", "CC_Base_L_Clavicle"],
    # chain
    ["upper_arm.L", "CC_Base_L_Upperarm", ""],
    ["forearm.L", "CC_Base_L_Forearm", ""],
    ["hand.L", "CC_Base_L_Hand", "CC_Base_L_Hand", 0, 0.75],
    ["palm.01.L", "CC_Base_L_Hand", "-CC_Base_L_Index1", 0.35, 1],
    ["palm.02.L", "CC_Base_L_Hand", "-CC_Base_L_Mid1", 0.35, 1],
    ["palm.03.L", "CC_Base_L_Hand", "-CC_Base_L_Ring1", 0.35, 1],
    ["palm.04.L", "CC_Base_L_Hand", "-CC_Base_L_Pinky1", 0.35, 1],
    # Left Hand Fingers, chains
    ["thumb.01.L", "CC_Base_L_Thumb1", ""],
    ["f_index.01.L", "CC_Base_L_Index1", ""],
    ["f_middle.01.L", "CC_Base_L_Mid1", ""],
    ["f_ring.01.L", "CC_Base_L_Ring1", ""],
    ["f_pinky.01.L", "CC_Base_L_Pinky1", ""],
    ["thumb.02.L", "CC_Base_L_Thumb2", ""],
    ["f_index.02.L", "CC_Base_L_Index2", ""],
    ["f_middle.02.L", "CC_Base_L_Mid2", ""],
    ["f_ring.02.L", "CC_Base_L_Ring2", ""],
    ["f_pinky.02.L", "CC_Base_L_Pinky2", ""],
    ["thumb.03.L", "CC_Base_L_Thumb3", "CC_Base_L_Thumb3"],
    ["f_index.03.L", "CC_Base_L_Index3", "CC_Base_L_Index3"],
    ["f_middle.03.L", "CC_Base_L_Mid3", "CC_Base_L_Mid3"],
    ["f_ring.03.L", "CC_Base_L_Ring3", "CC_Base_L_Ring3"],
    ["f_pinky.03.L", "CC_Base_L_Pinky3", "CC_Base_L_Pinky3"],

    # Right Leg, chain
    ["thigh.R", "CC_Base_R_Thigh", ""],
    ["shin.R", "CC_Base_R_Calf", ""],
    ["foot.R", "CC_Base_R_Foot", ""],
    ["toe.R", "CC_Base_R_ToeBase", "CC_Base_R_ToeBase"],

    # Right Arm:
    ["shoulder.R", "CC_Base_R_Clavicle", "CC_Base_R_Clavicle"],
    ["upper_arm.R", "CC_Base_R_Upperarm", ""],
    ["forearm.R", "CC_Base_R_Forearm", ""],
    ["hand.R", "CC_Base_R_Hand", "CC_Base_R_Hand", 0, 0.75],
    ["palm.01.R", "CC_Base_R_Hand", "-CC_Base_R_Index1", 0.35, 1],
    ["palm.02.R", "CC_Base_R_Hand", "-CC_Base_R_Mid1", 0.35, 1],
    ["palm.03.R", "CC_Base_R_Hand", "-CC_Base_R_Ring1", 0.35, 1],
    ["palm.04.R", "CC_Base_R_Hand", "-CC_Base_R_Pinky1", 0.35, 1],
    # Right Hand Fingers, chains
    ["thumb.01.R", "CC_Base_R_Thumb1", ""],
    ["f_index.01.R", "CC_Base_R_Index1", ""],
    ["f_middle.01.R", "CC_Base_R_Mid1", ""],
    ["f_ring.01.R", "CC_Base_R_Ring1", ""],
    ["f_pinky.01.R", "CC_Base_R_Pinky1", ""],
    ["thumb.02.R", "CC_Base_R_Thumb2", ""],
    ["f_index.02.R", "CC_Base_R_Index2", ""],
    ["f_middle.02.R", "CC_Base_R_Mid2", ""],
    ["f_ring.02.R", "CC_Base_R_Ring2", ""],
    ["f_pinky.02.R", "CC_Base_R_Pinky2", ""],
    ["thumb.03.R", "CC_Base_R_Thumb3", "CC_Base_R_Thumb3"],
    ["f_index.03.R", "CC_Base_R_Index3", "CC_Base_R_Index3"],
    ["f_middle.03.R", "CC_Base_R_Mid3", "CC_Base_R_Mid3"],
    ["f_ring.03.R", "CC_Base_R_Ring3", "CC_Base_R_Ring3"],
    ["f_pinky.03.R", "CC_Base_R_Pinky3", "CC_Base_R_Pinky3"],

    ["tongue", "CC_Base_Tongue03", "CC_Base_Tongue02"],
    ["tongue.001", "CC_Base_Tongue02", "CC_Base_Tongue01"],
    ["tongue.002", "CC_Base_Tongue01", "CC_Base_JawRoot", 0, 0.65],

    ["teeth.T", "CC_Base_Teeth01", "CC_Base_Teeth01"],
    ["teeth.B", "CC_Base_Teeth02", "CC_Base_Teeth02"],

    ["eye.R", "CC_Base_R_Eye", ""],
    ["eye.L", "CC_Base_L_Eye", ""],

    ["eye.L", "CC_Base_L_Eye", ""],

    # only when not using the full face rig, a jaw bone is created that needs positioning...
    ["jaw", "CC_Base_JawRoot", "CC_Base_Tongue03", 0, 1.35],
]

FACE_BONES = [
    ["face", "spine.006", "LR", 0],
    ["eye.L", "face", "LR", 0],
    ["eye.R", "face", "LR", 0],
    ["jaw", "face", "LR", 0, "JAW"],
    ["teeth.T", "face", "LR", 0],
    ["teeth.B", "jaw", "LR", 0],
    ["tongue", "jaw", "LR", 0, "TONGUE"],
    ["tongue.001", "tongue", "CLR", 0],
    ["tongue.002", "tongue.001", "CLR", 0],
]

# relative mappings: calculate the head/tail position of the first index,
#     defined by the second index
#     relative to a bounding box containing the proceding bones
#     may need to specify a minimum box dimension to avoid flat boxes.
# after everything else has been placed, restore the relative mappings
RELATIVE_MAPPINGS = [
    ["heel.02.L", "BOTH", "foot.L", "toe.L"],
    ["heel.02.R", "BOTH", "foot.R", "toe.R"],
]

# additional deformation bones to copy from the cc3 rig to the generated rigify deformation bones.
# [cc3_source_bone, new_rigify_def_bone, rigify_parent, flags]
# flags C=Connected, L=Local location, R=Inherit rotation
ADD_DEF_BONES = [

    ["CC_Base_L_RibsTwist", "DEF-breast_twist.L", "ORG-breast.L", "LR"],
    ["CC_Base_R_RibsTwist", "DEF-breast_twist.R", "ORG-breast.R", "LR"],
    # "-" tells it to re-parent the existing DEF-breast bones to the new DEF-breast_twist bones.
    ["-", "DEF-breast.L", "DEF-breast_twist.L", "LR"],
    ["-", "DEF-breast.R", "DEF-breast_twist.R", "LR"],

    ["CC_Base_L_UpperarmTwist01", "DEF-upper_arm_twist.L", "DEF-upper_arm.L", "LR"],
    ["CC_Base_L_UpperarmTwist02", "DEF-upper_arm_twist.L.001", "DEF-upper_arm.L.001", "LR"],
    ["CC_Base_L_ElbowShareBone", "DEF-elbow_share.L", "DEF-forearm.L", "LR"],
    ["CC_Base_L_ForearmTwist01", "DEF-forearm_twist.L", "DEF-forearm.L", "LR"],
    ["CC_Base_L_ForearmTwist02", "DEF-forearm_twist.L.001", "DEF-forearm.L.001", "LR"],

    ["CC_Base_L_ThighTwist01", "DEF-thigh_twist.L", "DEF-thigh.L", "LR"],
    ["CC_Base_L_ThighTwist02", "DEF-thigh_twist.L.001", "DEF-thigh.L.001", "LR"],
    ["CC_Base_L_KneeShareBone", "DEF-knee_share.L", "DEF-shin.L", "LR"],
    ["CC_Base_L_CalfTwist01", "DEF-shin_twist.L", "DEF-shin.L", "LR"],
    ["CC_Base_L_CalfTwist02", "DEF-shin_twist.L.001", "DEF-shin.L.001", "LR"],

    ["CC_Base_L_BigToe1", "DEF-toe_big.L", "DEF-toe.L", "LR"],
    ["CC_Base_L_IndexToe1", "DEF-toe_index.L", "DEF-toe.L", "LR"],
    ["CC_Base_L_MidToe1", "DEF-toe_mid.L", "DEF-toe.L", "LR"],
    ["CC_Base_L_RingToe1", "DEF-toe_ring.L", "DEF-toe.L", "LR"],
    ["CC_Base_L_PinkyToe1", "DEF-toe_pinky.L", "DEF-toe.L", "LR"],


    ["CC_Base_R_UpperarmTwist01", "DEF-upper_arm_twist.R", "DEF-upper_arm.R", "LR"],
    ["CC_Base_R_UpperarmTwist02", "DEF-upper_arm_twist.R.001", "DEF-upper_arm.R.001", "LR"],
    ["CC_Base_R_ElbowShareBone", "DEF-elbow_share.R", "DEF-forearm.R", "LR"],
    ["CC_Base_R_ForearmTwist01", "DEF-forearm_twist.R", "DEF-forearm.R", "LR"],
    ["CC_Base_R_ForearmTwist02", "DEF-forearm_twist.R.001", "DEF-forearm.R.001", "LR"],

    ["CC_Base_R_ThighTwist01", "DEF-thigh_twist.R", "DEF-thigh.R", "LR"],
    ["CC_Base_R_ThighTwist02", "DEF-thigh_twist.R.001", "DEF-thigh.R.001", "LR"],
    ["CC_Base_R_KneeShareBone", "DEF-knee_share.R", "DEF-shin.R", "LR"],
    ["CC_Base_R_CalfTwist01", "DEF-shin_twist.R", "DEF-shin.R", "LR"],
    ["CC_Base_R_CalfTwist02", "DEF-shin_twist.R.001", "DEF-shin.R.001", "LR"],

    ["CC_Base_R_BigToe1", "DEF-toe_big.R", "DEF-toe.R", "LR"],
    ["CC_Base_R_IndexToe1", "DEF-toe_index.R", "DEF-toe.R", "LR"],
    ["CC_Base_R_MidToe1", "DEF-toe_mid.R", "DEF-toe.R", "LR"],
    ["CC_Base_R_RingToe1", "DEF-toe_ring.R", "DEF-toe.R", "LR"],
    ["CC_Base_R_PinkyToe1", "DEF-toe_pinky.R", "DEF-toe.R", "LR"],

    # "+CopyRoot" tells it to add a new bone, parented to the root bone, with a transform copy from the rigify_parent
    ["+CopyRoot", "MCH-eyes_parent", "ORG-face", "LR"],
]

VERTEX_GROUP_RENAME = [
    # Spine, Neck & Head:
    # spine chain
    ["DEF-spine", "CC_Base_Hip"],
    ["DEF-spine.001", "CC_Base_Waist"],
    ["DEF-spine.002", "CC_Base_Spine01"],
    ["DEF-spine.003", "CC_Base_Spine02"],
    ["DEF-spine.004", "CC_Base_NeckTwist01"],
    ["DEF-spine.005", "CC_Base_NeckTwist02"],
    ["DEF-spine.006", "CC_Base_Head"], # special case
    ["DEF-pelvis", "CC_Base_Pelvis"],

    ["DEF-breast_twist.L", "CC_Base_L_RibsTwist"],
    ["DEF-breast_twist.R", "CC_Base_R_RibsTwist"],

    # Left Breast
    ["DEF-breast.L", "CC_Base_L_Breast"], # special case
    # Right Breast
    ["DEF-breast.R", "CC_Base_R_Breast"], # special case

    # Left Leg:
    ["DEF-thigh.L", "CC_Base_L_Thigh"],
    ["DEF-thigh_twist.L", "CC_Base_L_ThighTwist01"],
    ["DEF-thigh_twist.L.001", "CC_Base_L_ThighTwist02"],
    ["DEF-knee_share.L", "CC_Base_L_KneeShareBone"],
    ["DEF-shin.L", "CC_Base_L_Calf"],
    ["DEF-shin_twist.L", "CC_Base_L_CalfTwist01"],
    ["DEF-shin_twist.L.001", "CC_Base_L_CalfTwist02"],
    ["DEF-foot.L", "CC_Base_L_Foot"],
    ["DEF-toe.L", "CC_Base_L_ToeBase"],

    ["DEF-toe_big.L", "CC_Base_L_BigToe1"],
    ["DEF-toe_index.L", "CC_Base_L_IndexToe1"],
    ["DEF-toe_mid.L", "CC_Base_L_MidToe1"],
    ["DEF-toe_ring.L", "CC_Base_L_RingToe1"],
    ["DEF-toe_pinky.L", "CC_Base_L_PinkyToe1"],

    # Left Arm:
    ["DEF-shoulder.L", "CC_Base_L_Clavicle"],
    # chain
    ["DEF-upper_arm.L", "CC_Base_L_Upperarm"],
    ["DEF-upper_arm_twist.L", "CC_Base_L_UpperarmTwist01"],
    ["DEF-upper_arm_twist.L.001", "CC_Base_L_UpperarmTwist02"],
    ["DEF-elbow_share.L", "CC_Base_L_ElbowShareBone"],
    ["DEF-forearm.L", "CC_Base_L_Forearm"],
    ["DEF-forearm_twist.L", "CC_Base_L_ForearmTwist01"],
    ["DEF-forearm_twist.L.001", "CC_Base_L_ForearmTwist02"],
    ["DEF-hand.L", "CC_Base_L_Hand"],
    # Left Hand Fingers, chains
    ["DEF-thumb.01.L", "CC_Base_L_Thumb1"],
    ["DEF-f_index.01.L", "CC_Base_L_Index1"],
    ["DEF-f_middle.01.L", "CC_Base_L_Mid1"],
    ["DEF-f_ring.01.L", "CC_Base_L_Ring1"],
    ["DEF-f_pinky.01.L", "CC_Base_L_Pinky1"],
    ["DEF-thumb.02.L", "CC_Base_L_Thumb2"],
    ["DEF-f_index.02.L", "CC_Base_L_Index2"],
    ["DEF-f_middle.02.L", "CC_Base_L_Mid2"],
    ["DEF-f_ring.02.L", "CC_Base_L_Ring2"],
    ["DEF-f_pinky.02.L", "CC_Base_L_Pinky2"],
    ["DEF-thumb.03.L", "CC_Base_L_Thumb3"],
    ["DEF-f_index.03.L", "CC_Base_L_Index3"],
    ["DEF-f_middle.03.L", "CC_Base_L_Mid3"],
    ["DEF-f_ring.03.L", "CC_Base_L_Ring3"],
    ["DEF-f_pinky.03.L", "CC_Base_L_Pinky3"],

    # Right Leg, chain
    ["DEF-thigh.R", "CC_Base_R_Thigh"],
    ["DEF-thigh_twist.R", "CC_Base_R_ThighTwist01"],
    ["DEF-thigh_twist.R.001", "CC_Base_R_ThighTwist02"],
    ["DEF-knee_share.R", "CC_Base_R_KneeShareBone"],
    ["DEF-shin.R", "CC_Base_R_Calf"],
    ["DEF-shin_twist.R", "CC_Base_R_CalfTwist01"],
    ["DEF-shin_twist.R.001", "CC_Base_R_CalfTwist02"],
    ["DEF-foot.R", "CC_Base_R_Foot"],
    ["DEF-toe.R", "CC_Base_R_ToeBase"],

    ["DEF-toe_big.R", "CC_Base_R_BigToe1"],
    ["DEF-toe_index.R", "CC_Base_R_IndexToe1"],
    ["DEF-toe_mid.R", "CC_Base_R_MidToe1"],
    ["DEF-toe_ring.R", "CC_Base_R_RingToe1"],
    ["DEF-toe_pinky.R", "CC_Base_R_PinkyToe1"],

    # Right Arm:
    ["DEF-shoulder.R", "CC_Base_R_Clavicle"],
    # chain
    ["DEF-upper_arm.R", "CC_Base_R_Upperarm"],
    ["DEF-upper_arm_twist.R", "CC_Base_R_UpperarmTwist01"],
    ["DEF-upper_arm_twist.R.001", "CC_Base_R_UpperarmTwist02"],
    ["DEF-elbow_share.R", "CC_Base_R_ElbowShareBone"],
    ["DEF-forearm.R", "CC_Base_R_Forearm"],
    ["DEF-forearm_twist.R", "CC_Base_R_ForearmTwist01"],
    ["DEF-forearm_twist.R.001", "CC_Base_R_ForearmTwist02"],
    ["DEF-hand.R", "CC_Base_R_Hand"],
    # Right Hand Fingers, chains
    ["DEF-thumb.01.R", "CC_Base_R_Thumb1"],
    ["DEF-f_index.01.R", "CC_Base_R_Index1"],
    ["DEF-f_middle.01.R", "CC_Base_R_Mid1"],
    ["DEF-f_ring.01.R", "CC_Base_R_Ring1"],
    ["DEF-f_pinky.01.R", "CC_Base_R_Pinky1"],
    ["DEF-thumb.02.R", "CC_Base_R_Thumb2"],
    ["DEF-f_index.02.R", "CC_Base_R_Index2"],
    ["DEF-f_middle.02.R", "CC_Base_R_Mid2"],
    ["DEF-f_ring.02.R", "CC_Base_R_Ring2"],
    ["DEF-f_pinky.02.R", "CC_Base_R_Pinky2"],
    ["DEF-thumb.03.R", "CC_Base_R_Thumb3"],
    ["DEF-f_index.03.R", "CC_Base_R_Index3"],
    ["DEF-f_middle.03.R", "CC_Base_R_Mid3"],
    ["DEF-f_ring.03.R", "CC_Base_R_Ring3"],
    ["DEF-f_pinky.03.R", "CC_Base_R_Pinky3"],

    ["DEF-tongue", "CC_Base_Tongue03"],
    ["DEF-tongue.001", "CC_Base_Tongue02"],
    ["DEF-tongue.002", "CC_Base_Tongue01"],

    ["ORG-teeth.T", "CC_Base_Teeth01"],
    ["ORG-teeth.B", "CC_Base_Teeth02"],

    ["ORG-eye.R", "CC_Base_R_Eye"],
    ["ORG-eye.L", "CC_Base_L_Eye"],

    ["DEF-jaw", "CC_Base_JawRoot"],
]


# the rigify meta rig and the cc3 bones don't always match for roll angles,
# correct them by copying from the cc3 bones and adjusting to match the orientation the meta rig expects.
# ["meta rig name", roll_adjust, "cc3 rig name"],
ROLL_COPY = [
    # Spine, Neck & Head:
    # spine chain
    ["spine", 0, "CC_Base_Pelvis"],
    ["spine.001", 0, "CC_Base_Waist"],
    ["spine.002", 0, "CC_Base_Spine01"],
    ["spine.003", 0, "CC_Base_Spine02"],
    ["spine.004", 0, "CC_Base_NeckTwist01"],
    ["spine.005", 0, "CC_Base_NeckTwist02"],
    ["spine.006", 0, "CC_Base_Head"], # todo
    ["face", 0, "CC_Base_FacialBone"], # todo
    ["pelvis", -180, "CC_Base_Pelvis"],

    # Left Breast
    ["breast.L", 0, "CC_Base_L_Breast"],
    # Right Breast
    ["breast.R", 0, "CC_Base_R_Breast"],

    # Left Leg:
    ["thigh.L", 180, "CC_Base_L_Thigh"],
    ["shin.L", 180, "CC_Base_L_Calf"],
    ["foot.L", 180, "CC_Base_L_Foot"],
    ["toe.L", 0, "CC_Base_L_ToeBaseShareBone"],

    # Left Arm:
    ["shoulder.L", -90, "CC_Base_L_Clavicle"],
    # chain
    ["upper_arm.L", 0, "CC_Base_L_Upperarm"],
    ["forearm.L", 0, "CC_Base_L_Forearm"],
    ["hand.L", 0, "CC_Base_L_Hand"],
    ["palm.01.L", 90, "CC_Base_L_Hand"],
    ["palm.02.L", 90, "CC_Base_L_Hand"],
    ["palm.03.L", 90, "CC_Base_L_Hand"],
    ["palm.04.L", 90, "CC_Base_L_Hand"],
    # Left Hand Fingers, chains
    ["thumb.01.L", 180, "CC_Base_L_Thumb1"],
    ["f_index.01.L", 90, "CC_Base_L_Index1"],
    ["f_middle.01.L", 90, "CC_Base_L_Mid1"],
    ["f_ring.01.L", 90, "CC_Base_L_Ring1"],
    ["f_pinky.01.L", 90, "CC_Base_L_Pinky1"],
    ["thumb.02.L", 180, "CC_Base_L_Thumb2"],
    ["f_index.02.L", 90, "CC_Base_L_Index2"],
    ["f_middle.02.L", 90, "CC_Base_L_Mid2"],
    ["f_ring.02.L", 90, "CC_Base_L_Ring2"],
    ["f_pinky.02.L", 90, "CC_Base_L_Pinky2"],
    ["thumb.03.L", 180, "CC_Base_L_Thumb3"],
    ["f_index.03.L", 90, "CC_Base_L_Index3"],
    ["f_middle.03.L", 90, "CC_Base_L_Mid3"],
    ["f_ring.03.L", 90, "CC_Base_L_Ring3"],
    ["f_pinky.03.L", 90, "CC_Base_L_Pinky3"],

    # Right Leg, chain
    ["thigh.R", -180, "CC_Base_R_Thigh"],
    ["shin.R", -180, "CC_Base_R_Calf"],
    ["foot.R", -180, "CC_Base_R_Foot"],
    ["toe.R", 0, "CC_Base_R_ToeBaseShareBone"],

    # Right Arm:
    ["shoulder.R", 90, "CC_Base_R_Clavicle"],
    ["upper_arm.R", 0, "CC_Base_R_Upperarm"],
    ["forearm.R", 0, "CC_Base_R_Forearm"],
    ["hand.R", 0, "CC_Base_R_Hand"],
    ["palm.01.R", -90, "CC_Base_R_Hand"],
    ["palm.02.R", -90, "CC_Base_R_Hand"],
    ["palm.03.R", -90, "CC_Base_R_Hand"],
    ["palm.04.R", -90, "CC_Base_R_Hand"],
    # Right Hand Fingers, chains
    ["thumb.01.R", -180, "CC_Base_R_Thumb1"],
    ["f_index.01.R", -90, "CC_Base_R_Index1"],
    ["f_middle.01.R", -90, "CC_Base_R_Mid1"],
    ["f_ring.01.R", -90, "CC_Base_R_Ring1"],
    ["f_pinky.01.R", -90, "CC_Base_R_Pinky1"],
    ["thumb.02.R", -180, "CC_Base_R_Thumb2"],
    ["f_index.02.R", -90, "CC_Base_R_Index2"],
    ["f_middle.02.R", -90, "CC_Base_R_Mid2"],
    ["f_ring.02.R", -90, "CC_Base_R_Ring2"],
    ["f_pinky.02.R", -90, "CC_Base_R_Pinky2"],
    ["thumb.03.R", -180, "CC_Base_R_Thumb3"],
    ["f_index.03.R", -90, "CC_Base_R_Index3"],
    ["f_middle.03.R", -90, "CC_Base_R_Mid3"],
    ["f_ring.03.R", -90, "CC_Base_R_Ring3"],
    ["f_pinky.03.R", -90, "CC_Base_R_Pinky3"],
]

RIGIFY_PARAMS = [
    ["upper_arm.R", "x"],
    ["upper_arm.L", "x"],
    ["thigh.R", "x"],
    ["thigh.L", "x"],
]

UV_THRESHOLD = 0.001

UV_TARGETS_CC3PLUS = [
    # connected mapping: map (head)->(tail/head)->(tail/head->(tail/head)...
    ["nose", "CONNECTED",           [0.500, 0.650], [0.500, 0.597], [0.500, 0.573], [0.500, 0.550], [0.500, 0.531], [0.500, 0.516]],
    ["jaw", "CONNECTED",            [0.500, 0.339], [0.500, 0.395], [0.500, 0.432], [0.500, 0.453]],
    ["cheek.T.R", "CONNECTED",      [0.360, 0.633], [0.413, 0.593], [0.453, 0.606], [0.446, 0.559], [0.500, 0.573]],
    ["temple.R", "CONNECTED",       [0.250, 0.645], [0.289, 0.492], [0.360, 0.435], [0.429, 0.408], [0.443, 0.486], [0.363, 0.533],
                                    [0.360, 0.633], [0.371, 0.660], [0.414, 0.682], [0.458, 0.678], [0.500, 0.650]],
    ["ear.R", "CONNECTED",          [0.246, 0.566], [0.228, 0.640], [0.196, 0.623], [0.207, 0.554], [0.235, 0.534], [0.246, 0.566]],

    ["lid.T.R", "CONNECTED",        [0.398, 0.638], [0.417, 0.644], [0.431, 0.644], [0.444, 0.641],
                                    [0.450, 0.635], [0.437, 0.632], [0.422, 0.631], [0.407, 0.633], [0.398, 0.638]],
    ["brow.B.R", "CONNECTED",       [0.388, 0.646], [0.413, 0.661], [0.435, 0.662], [0.454, 0.653], [0.460, 0.638]],

    ["lip.T.R", "CONNECTED",        [0.500, 0.512], [0.468, 0.508], [0.443, 0.486]],
    ["lip.B.R", "CONNECTED",        [0.500, 0.463], [0.478, 0.467], [0.443, 0.486]],

    # disconnected mapping: map head and tail pairs
    ["forehead.R", "DISCONNECTED",  [ [0.461, 0.740], [0.458, 0.678] ],
                                    [ [0.410, 0.741], [0.414, 0.682] ],
                                    [ [0.358, 0.725], [0.371, 0.660] ] ],
    # set the top of the 'head' bone
    #["spine.006", "TAIL",           [0.688, 0.953]],
]


# the minimum size of the relative mapping bounding box
BOX_PADDING = 0.25

class BoundingBox:
    box_min = [ float('inf'), float('inf'), float('inf')]
    box_max = [-float('inf'),-float('inf'),-float('inf')]

    def __init__(self):
        for i in range(0,3):
            self.box_min[i] =  float('inf')
            self.box_max[i] = -float('inf')

    def add(self, coord):
        for i in range(0,3):
            if coord[i] < self.box_min[i]:
                self.box_min[i] = coord[i]
            if coord[i] > self.box_max[i]:
                self.box_max[i] = coord[i]

    def pad(self, padding):
        for i in range(0,3):
            self.box_min[i] -= padding
            self.box_max[i] += padding

    def relative(self, coord):
        r = [0,0,0]
        for i in range(0,3):
            r[i] = (coord[i] - self.box_min[i]) / (self.box_max[i] - self.box_min[i])
        return r

    def coord(self, relative):
        c = [0,0,0]
        for i in range(0,3):
            c[i] = relative[i] * (self.box_max[i] - self.box_min[i]) + self.box_min[i]
        return c

    def debug(self):
        print("BOX:")
        print("Min:", self.box_min)
        print("Max:", self.box_max)


def find_metarig(objects):
    for obj in objects:
        if obj.type == "ARMATURE":
            if "metarig" in obj.name and "spine" in obj.pose.bones:
                return obj
    return None


def prune_meta_rig(rig):
    """Removes some meta rig bones that have no corresponding match in the CC3 rig.
       (And are safe to remove)
    """

    pelvis_r = rig.data.edit_bones["pelvis.R"]
    rig.data.edit_bones.remove(pelvis_r)
    rig.data.edit_bones["pelvis.L"].name = "pelvis"


def add_def_bones(cc3_rig, rigify_rig):
    """Adds and parents twist deformation bones to the rigify deformation bones.
       Twist bones are parented to their corresponding limb bones.
       The main limb bones are not vertex weighted in the meshes but the twist bones are,
       so it's important the twist bones move (and stretch) with the parent limb.

       Also adds some missing toe bones and finger bones.
       (See: ADD_DEF_BONES array)
    """

    # use the eye org bones to deform the eye vertex groups in the eye object
    # (rather than create new DEF bones, as the ORG bones already exist in the rigify rig)
    if "ORG-eye.R" in rigify_rig.data.bones:
        rigify_rig.data.bones["ORG-eye.R"].use_deform = True
    if "ORG-eye.L" in rigify_rig.data.bones:
        rigify_rig.data.bones["ORG-eye.L"].use_deform = True
    if "ORG-teeth.T" in rigify_rig.data.bones:
        rigify_rig.data.bones["ORG-teeth.T"].use_deform = True
    if "ORG-teeth.B" in rigify_rig.data.bones:
        rigify_rig.data.bones["ORG-teeth.B"].use_deform = True

    for def_copy in ADD_DEF_BONES:
        src_bone_name = def_copy[0]
        dst_bone_name = def_copy[1]
        dst_bone_parent_name = def_copy[2]
        relation_flags = def_copy[3]

        if src_bone_name == "-": # means to reparent an existing deformation bone
            if utils.edit_mode_to(rigify_rig):
                if dst_bone_name in rigify_rig.data.edit_bones:
                    dst_bone = rigify_rig.data.edit_bones[dst_bone_name]
                    if dst_bone_parent_name != "":
                        if dst_bone_parent_name in rigify_rig.data.edit_bones:
                            parent_bone = rigify_rig.data.edit_bones[dst_bone_parent_name]
                            dst_bone.parent = parent_bone
                            dst_bone.use_connect = True if "C" in relation_flags else False
                            dst_bone.use_local_location = True if "L" in relation_flags else False
                            dst_bone.use_inherit_rotation = True if "R" in relation_flags else False
                        else:
                            utils.log_error(f"Could not find parent bone: {dst_bone_parent_name} in Rigify Rig!")
                else:
                    utils.log_error(f"Could not find bone: {dst_bone_name} in Rigify Rig!")
        elif src_bone_name == "+CopyRoot":
            pass
        else:
            if dst_bone_name not in rigify_rig.data.bones:
                if utils.edit_mode_to(cc3_rig):
                    if src_bone_name in cc3_rig.data.edit_bones:
                        src_bone = cc3_rig.data.edit_bones[src_bone_name]
                        head_pos = cc3_rig.matrix_world @ src_bone.head
                        tail_pos = cc3_rig.matrix_world @ src_bone.tail
                        roll = src_bone.roll
                        if utils.edit_mode_to(rigify_rig):
                            dst_bone = rigify_rig.data.edit_bones.new(dst_bone_name)
                            dst_bone.head = head_pos
                            dst_bone.tail = tail_pos
                            dst_bone.roll = roll
                            if dst_bone_parent_name != "":
                                if dst_bone_parent_name in rigify_rig.data.edit_bones:
                                    parent_bone = rigify_rig.data.edit_bones[dst_bone_parent_name]
                                    dst_bone.parent = parent_bone
                                    dst_bone.use_connect = True if "C" in relation_flags else False
                                    dst_bone.use_local_location = True if "L" in relation_flags else False
                                    dst_bone.use_inherit_rotation = True if "R" in relation_flags else False
                                else:
                                    utils.log_error(f"Could not find parent bone: {dst_bone_parent_name} in Rigify Rig!")
                    else:
                        utils.log_error(f"Could not find bone: {src_bone_name} in CC Rig!")


def rename_vertex_groups(cc3_rig, rigify_rig):
    """Rename the CC3 rig vertex weight groups to the Rigify deformation bone names,
       removes matching existing vertex groups created by parent with automatic weights.
       Thus leaving just the automatic face rig weights.
    """

    obj : bpy.types.Object
    for obj in rigify_rig.children:

        for vgrn in VERTEX_GROUP_RENAME:
            vg_from = vgrn[1]
            vg_to = vgrn[0]

            try:
                if vg_to in obj.vertex_groups:
                    utils.log_info(f"removing {vg_to}")
                    obj.vertex_groups.remove(obj.vertex_groups[vg_to])
            except:
                pass

            try:
                if vg_from in obj.vertex_groups:
                    utils.log_info(f"renaming {vg_from} to {vg_to}")
                    obj.vertex_groups[vg_from].name = vg_to
            except:
                pass

        for mod in obj.modifiers:
            if mod.type == "ARMATURE":
                mod.object = rigify_rig
                mod.use_deform_preserve_volume = True


def store_relative_mappings(rig, coords):
    for mapping in RELATIVE_MAPPINGS:
        bone_name = mapping[0]
        bone = rig.data.edit_bones[bone_name]
        bone_head_pos = rig.matrix_world @ bone.head
        bone_tail_pos = rig.matrix_world @ bone.tail

        box = BoundingBox()

        for i in range(2, len(mapping)):
            rel_name = mapping[i]
            rel_bone = rig.data.edit_bones[rel_name]
            head_pos = rig.matrix_world @ rel_bone.head
            tail_pos = rig.matrix_world @ rel_bone.tail
            box.add(head_pos)
            box.add(tail_pos)

        box.pad(BOX_PADDING)

        coords[bone_name] = [box.relative(bone_head_pos), box.relative(bone_tail_pos)]


def restore_relative_mappings(rig, coords):
    for mapping in RELATIVE_MAPPINGS:
        bone_name = mapping[0]
        bone = rig.data.edit_bones[bone_name]

        box = BoundingBox()

        for i in range(2, len(mapping)):
            rel_name = mapping[i]
            rel_bone = rig.data.edit_bones[rel_name]
            head_pos = rig.matrix_world @ rel_bone.head
            tail_pos = rig.matrix_world @ rel_bone.tail
            box.add(head_pos)
            box.add(tail_pos)

        box.pad(BOX_PADDING)

        rc = coords[bone_name]
        if (mapping[1] == "HEAD" or mapping[1] == "BOTH"):
            bone.head = box.coord(rc[0])

        if (mapping[1] == "TAIL" or mapping[1] == "BOTH"):
            bone.tail = box.coord(rc[1])


def store_bone_roll(rig, roll_store):

    for roll in ROLL_COPY:

        target_name = roll[0]
        roll_mod = roll[1]
        source_name = roll[2]

        bone = rig.data.edit_bones[source_name]
        roll_store[target_name] = bone.roll


def restore_bone_roll(rig, roll_store):

    for roll in ROLL_COPY:

        target_name = roll[0]
        roll_mod = roll[1]
        source_name = roll[2]

        if target_name in rig.data.edit_bones:
            bone = rig.data.edit_bones[target_name]
            bone.roll = roll_store[target_name] + roll_mod * 0.0174532925199432957


def set_rigify_params(rig):
    #bpy.context.active_object.pose.bones['upper_arm.R'].rigify_parameters.rotation_axis = "z"

    for params in RIGIFY_PARAMS:
        bone_name = params[0]
        bone_rot_axis = params[1]
        rig.pose.bones[bone_name].rigify_parameters.rotation_axis = bone_rot_axis


def get_world_from_uv(obj, t_mesh, mat_slot, uv_target):
    world = geom.mesh_world_point_from_uv(obj, t_mesh, mat_slot, uv_target)
    if world is None: # if the point is outside the UV island(s), just find the nearest vertex.
        world = geom.nearest_vert_from_uv(obj, t_mesh, mat_slot, uv_target, UV_THRESHOLD)
    if world is None:
        utils.log_error("Unable to locate uv target: " + str(uv_target))
    return world



def map_eyes(cc3_rig, dst_rig):
    # eye head position mapped from the cc3 bones
    # eye tail map to 0.5, 0.5 on the uv
    obj : bpy.types.Object = None
    for child in cc3_rig.children:
        if child.name.lower().endswith("base_eye"):
            obj = child
    length = 0.375

    #right_slot = get_eye_material_slot(obj, True)
    #left_slot = get_eye_material_slot(obj, False)

    #mesh = obj.data
    #t_mesh = geom.get_triangulated_bmesh(mesh)

    #uv = [0.5, 0.5, 0]

    #if right_slot > -1:
    #    world_right = get_world_from_uv(obj, t_mesh, right_slot, uv)
    #    if world_right and "eye.R" in dst_rig.data.edit_bones:
    #        dst_rig.data.edit_bones["eye.R"].tail = world_right

    #if left_slot > -1:
    #    world_left = get_world_from_uv(obj, t_mesh, left_slot, uv)
    #    if world_left and "eye.L" in dst_rig.data.edit_bones:
    #        dst_rig.data.edit_bones["eye.L"].tail = world_left


    if "eye.L" in dst_rig.data.edit_bones and "CC_Base_L_Eye" in cc3_rig.data.bones:
        left_eye = dst_rig.data.edit_bones["eye.L"]
        src_bone = cc3_rig.data.bones["CC_Base_L_Eye"]
        head_position = cc3_rig.matrix_world @ src_bone.head_local
        tail_position = cc3_rig.matrix_world @ src_bone.tail_local
        dir : mathutils.Vector = tail_position - head_position
        #minus_y_dir = mathutils.Vector(0, -1, 0) @ left_eye.matrix.inverted()
        # CC3 eyes look down the -Y axis, reverse this to point forward for the meta-rig
        left_eye.tail = head_position - (dir * length)


    if "eye.R" in dst_rig.data.edit_bones and "CC_Base_R_Eye" in cc3_rig.data.bones:
        right_eye = dst_rig.data.edit_bones["eye.R"]
        src_bone = cc3_rig.data.bones["CC_Base_R_Eye"]
        head_position = cc3_rig.matrix_world @ src_bone.head_local
        tail_position = cc3_rig.matrix_world @ src_bone.tail_local
        dir : mathutils.Vector = tail_position - head_position
        #minus_y_dir = mathutils.Vector(0, -1, 0) @ left_eye.matrix.inverted()
        right_eye.tail = head_position - (dir * length)

    if "spine.006" in dst_rig.data.edit_bones and "CC_Base_Head" in cc3_rig.data.bones:
        spine6 = dst_rig.data.edit_bones["spine.006"]
        head_bone = cc3_rig.data.bones["CC_Base_Head"]
        head_position = cc3_rig.matrix_world @ head_bone.head_local
        length = 0
        n = 0
        if "CC_Base_L_Eye" in cc3_rig.data.bones:
            left_eye_bone = cc3_rig.data.bones["CC_Base_L_Eye"]
            left_eye_position = cc3_rig.matrix_world @ left_eye_bone.head_local
            length += left_eye_position.z - head_position.z
            n += 1
        if "CC_Base_R_Eye" in cc3_rig.data.bones:
            right_eye_bone = cc3_rig.data.bones["CC_Base_R_Eye"]
            right_eye_position = cc3_rig.matrix_world @ right_eye_bone.head_local
            length += right_eye_position.z - head_position.z
            n += 1
        if n > 0:
            length *= 2.65 / n
        else:
            length = 0.25
        tail_position = head_position + mathutils.Vector((0,0,1)) * length
        spine6.tail = tail_position

    if "teeth.T" in dst_rig.data.edit_bones and "CC_Base_Teeth01" in cc3_rig.data.bones:
        teeth_bone = dst_rig.data.edit_bones["teeth.T"]
        face_bone = dst_rig.data.edit_bones["face"]
        face_dir = face_bone.tail - face_bone.head
        src_bone = cc3_rig.data.bones["CC_Base_Teeth01"]
        teeth_bone.head = (cc3_rig.matrix_world @ src_bone.head_local) + face_dir * 0.5
        teeth_bone.tail = (cc3_rig.matrix_world @ src_bone.head_local)

    if "teeth.B" in dst_rig.data.edit_bones and "CC_Base_Teeth02" in cc3_rig.data.bones:
        teeth_bone = dst_rig.data.edit_bones["teeth.B"]
        face_bone = dst_rig.data.edit_bones["face"]
        face_dir = face_bone.tail - face_bone.head
        src_bone = cc3_rig.data.bones["CC_Base_Teeth02"]
        teeth_bone.head = (cc3_rig.matrix_world @ src_bone.head_local) + face_dir * 0.5
        teeth_bone.tail = (cc3_rig.matrix_world @ src_bone.head_local)


def mirror_uv_target(uv):
    muv = uv.copy()
    x = muv[0]
    muv[0] = 1 - x
    return muv


def map_uv_targets(cc3_rig, dst_rig):
    obj = None
    for child in cc3_rig.children:
        if child.name.lower().endswith("base_body"):
            obj = child
    if obj is None:
        return

    mat_slot = get_head_material_slot(obj)
    mesh = obj.data
    t_mesh = geom.get_triangulated_bmesh(mesh)

    for uvt in UV_TARGETS_CC3PLUS:
        name = uvt[0]
        type = uvt[1]
        num_targets = len(uvt) - 2
        if name in dst_rig.data.edit_bones:
            bone = dst_rig.data.edit_bones[name]
            last = None
            m_bone = None
            m_last = None
            if name.endswith(".R"):
                m_name = name[:-2] + ".L"
                if m_name in dst_rig.data.edit_bones:
                    m_bone = dst_rig.data.edit_bones[m_name]

            if type == "CONNECTED":
                for index in range(0, num_targets):
                    uv_target = uvt[index + 2]
                    uv_target.append(0)

                    world = get_world_from_uv(obj, t_mesh, mat_slot, uv_target)
                    if m_bone or m_last:
                        m_uv_target = mirror_uv_target(uv_target)
                        m_world = get_world_from_uv(obj, t_mesh, mat_slot, m_uv_target)

                    if world:
                        if last:
                            utils.log_info(last.name + ": Tail: " + str(world))
                            last.tail = world
                            if m_last:
                                m_last.tail = m_world
                        if bone:
                            utils.log_info(bone.name + ": Head: " + str(world))
                            bone.head = world
                            if m_bone:
                                m_bone.head = m_world

                    if bone is None:
                        break

                    index += 1
                    last = bone
                    m_last = m_bone
                    # follow the connected chain of bones
                    if len(bone.children) > 0 and bone.children[0].use_connect:
                        bone = bone.children[0]
                        if m_bone:
                            m_bone = m_bone.children[0]
                    else:
                        bone = None
                        m_bone = None

            elif type == "DISCONNECTED":
                for index in range(0, num_targets):
                    target_uvs = uvt[index + 2]
                    uv_head = target_uvs[0]
                    uv_tail = target_uvs[1]
                    uv_head.append(0)
                    uv_tail.append(0)

                    world_head = get_world_from_uv(obj, t_mesh, mat_slot, uv_head)
                    world_tail = get_world_from_uv(obj, t_mesh, mat_slot, uv_tail)

                    if m_bone:
                        muv_head = mirror_uv_target(uv_head)
                        muv_tail = mirror_uv_target(uv_tail)
                        mworld_head = get_world_from_uv(obj, t_mesh, mat_slot, muv_head)
                        mworld_tail = get_world_from_uv(obj, t_mesh, mat_slot, muv_tail)

                    if bone and world_head:
                        bone.head = world_head
                        if m_bone:
                            m_bone.head = mworld_head
                    if bone and world_tail:
                        bone.tail = world_tail
                        if m_bone:
                            m_bone.tail = mworld_tail

                    index += 1
                    # follow the chain of bones
                    if len(bone.children) > 0:
                        bone = bone.children[0]
                        if m_bone:
                            m_bone = m_bone.children[0]
                    else:
                        break

            elif type == "HEAD":
                uv_target = uvt[2]
                uv_target.append(0)

                world = get_world_from_uv(obj, t_mesh, mat_slot, uv_target)
                if world:
                    bone.head = world

            elif type == "TAIL":
                uv_target = uvt[2]
                uv_target.append(0)

                world = get_world_from_uv(obj, t_mesh, mat_slot, uv_target)
                if world:
                    bone.tail = world


def get_head_material_slot(obj):
    for i in range(0, len(obj.material_slots)):
        slot = obj.material_slots[i]
        if slot.material is not None:
            if "Std_Skin_Head" in slot.material.name:
                return i
    return -1


def get_eye_material_slot(obj, right_eye):
    for i in range(0, len(obj.material_slots)):
        slot = obj.material_slots[i]
        if slot.material is not None:
            l_name = slot.material.name.lower()
            if right_eye and "std_eye_r" in l_name:
                return i
            elif not right_eye and "std_eye_l" in l_name:
                return i
    return -1


def do_test():
    #cc3_rig = utils.find_cc3_rig()
    #for obj in cc3_rig.children:
    #    if "base_body" in obj.name.lower():
    #        map_uv_targets(obj)
    pass


def map_bone(src_rig, dst_rig, mapping):
    """Maps the head and tail of a bone in the destination
    rig, to the positions of the head and tail of bones in
    the source rig.

    Must be in edit mode with the destination rig active.
    """

    dst_bone_name = mapping[0]
    src_bone_head_name = mapping[1]
    src_bone_tail_name = mapping[2]

    utils.log_info(f"Mapping: {dst_bone_name} from: {src_bone_head_name}/{src_bone_tail_name}")

    if dst_bone_name in dst_rig.data.edit_bones:

        dst_bone = dst_rig.data.edit_bones[dst_bone_name]
        src_bone = None

        head_position = dst_bone.head
        tail_position = dst_bone.tail

        # fetch the target start point
        if src_bone_head_name != "":
            reverse = False
            if src_bone_head_name[0] == "-":
                src_bone_head_name = src_bone_head_name[1:]
                reverse = True
            if src_bone_head_name in src_rig.data.bones:
                src_bone = src_rig.data.bones[src_bone_head_name]
                if reverse:
                    head_position = src_rig.matrix_world @ src_bone.tail_local
                else:
                    head_position = src_rig.matrix_world @ src_bone.head_local
            else:
                utils.log_error(f"source head bone: {src_bone_head_name} not found!")

        # fetch the target end point
        if src_bone_tail_name != "":
            reverse = False
            if src_bone_tail_name[0] == "-":
                src_bone_tail_name = src_bone_tail_name[1:]
                reverse = True
            if src_bone_tail_name in src_rig.data.bones:
                src_bone = src_rig.data.bones[src_bone_tail_name]
                if reverse:
                    tail_position = src_rig.matrix_world @ src_bone.head_local
                else:
                    tail_position = src_rig.matrix_world @ src_bone.tail_local
            else:
                utils.log_error(f"source tail bone: {src_bone_tail_name} not found!")

        # lerp the start and end positions if supplied
        if src_bone:

            if len(mapping) == 5 and src_bone_head_name != "" and src_bone_tail_name != "":
                start = mapping[3]
                end = mapping[4]
                vec = tail_position - head_position
                org = head_position
                head_position = org + vec * start
                tail_position = org + vec * end

            # set the head position
            if src_bone_head_name != "":
                dst_bone.head = head_position

            # set the tail position
            if src_bone_tail_name != "":
                dst_bone.tail = tail_position
    else:
        utils.log_error(f"destination bone: {dst_bone_name} not found!")


def match_meta_rig(meta_rig, cc3_rig, rig_face):
    """Only call in bone edit mode...
    """
    relative_coords = {}
    roll_store = {}

    if utils.set_mode("OBJECT"):
        utils.set_active_object(cc3_rig)

        if utils.set_mode("EDIT"):
            store_bone_roll(cc3_rig, roll_store)

            if utils.set_mode("OBJECT"):
                utils.set_active_object(meta_rig)

                if utils.set_mode("EDIT"):

                    prune_meta_rig(meta_rig)
                    store_relative_mappings(meta_rig, relative_coords)

                    for mapping in BONE_MAPPINGS:
                        map_bone(cc3_rig, meta_rig, mapping)

                    restore_relative_mappings(meta_rig, relative_coords)
                    restore_bone_roll(meta_rig, roll_store)
                    set_rigify_params(meta_rig)
                    if rig_face:
                        map_uv_targets(cc3_rig, meta_rig)
                    map_eyes(cc3_rig, meta_rig)
                    return

    utils.log_error("Unable to match meta rig.")


def fix_bend(meta_rig, bone_one_name, bone_two_name, dir : mathutils.Vector):
    """Determine if the bend between two bones is sufficient to generate an accurate pole in the rig,
       by calculating where the middle joint lies on the line between the start and end points and
       determining if the distance to that line is large enough and in the right direction.
       Recalculating the joint position if not.
    """

    dir.normalize()

    utils.log_info(f"Fix Bend: {bone_one_name}, {bone_two_name}")

    if utils.set_mode("OBJECT") and utils.set_active_object(meta_rig) and utils.set_mode("EDIT"):

        one : bpy.types.EditBone = utils.find_edit_bone_in_armature(meta_rig, bone_one_name)
        two : bpy.types.EditBone = utils.find_edit_bone_in_armature(meta_rig, bone_two_name)

        if one and two:

            start : mathutils.Vector = one.head
            mid : mathutils.Vector = one.tail
            end : mathutils.Vector = two.tail
            u : mathutils.Vector = end - start
            v : mathutils.Vector = mid - start
            u.normalize()
            l = u.dot(v)
            line_mid : mathutils.Vector = u * l + start
            disp : mathutils.Vector = mid - line_mid
            d = disp.length
            if dir.dot(disp) < 0 or d < 0.001:
                utils.log_info(f"Bend between {bone_one_name} and {bone_two_name} is too shallow or negative, fixing.")

                new_mid_dir : mathutils.Vector = dir - u.dot(dir) * u
                new_mid_dir.normalize()
                new_mid = line_mid + new_mid_dir * 0.001
                utils.log_info(f"New joint position: {new_mid}")
                one.tail = new_mid
                two.head = new_mid

    return


def remove_face_rig(meta_rig):

    if utils.set_mode("OBJECT") and utils.set_active_object(meta_rig) and utils.set_mode("EDIT"):

        delete_bones = []

        # remove all meta-rig bones in layer[0] (the face bones)
        bone : bpy.types.EditBone
        for bone in meta_rig.data.edit_bones:
            if bone.layers[0]:
                delete_bones.append(bone)

        for bone in delete_bones:
            meta_rig.data.edit_bones.remove(bone)

        y = 0
        # add the needed face bones (eyes and jaw)
        for face_bone_def in FACE_BONES:

            bone_name = face_bone_def[0]
            parent_name = face_bone_def[1]
            relation_flags = face_bone_def[2]
            layer = face_bone_def[3]
            mode = "NONE"
            if len(face_bone_def) > 4:
                mode = face_bone_def[4]
            print("MODE: " + mode)

            utils.log_info(f"Adding bone: {bone_name}")

            # make a new bone
            face_bone = meta_rig.data.edit_bones.new(bone_name)

            # give the bone a non zero length otherwise the bone will be deleted as invalid when exiting edit mode...
            # (the bone will be positioned correctly later acording to the bone mappings)
            face_bone.head = (0, y, 0)
            # and make sure chains of bones don't overlap and become invalid...
            y -= 0.1
            face_bone.tail = (0, y, 0)

            # set the bone parent
            if parent_name in meta_rig.data.edit_bones:
                utils.log_info(f"Parenting bone: {bone_name} to {parent_name}")
                bone_parent = meta_rig.data.edit_bones[parent_name]
                face_bone.parent = bone_parent

            # set the bone flags
            face_bone.use_connect = True if "C" in relation_flags else False
            face_bone.use_local_location = True if "L" in relation_flags else False
            face_bone.use_inherit_rotation = True if "R" in relation_flags else False
            face_bone.layers[layer] = True

            # set pose bone rigify types
            pose_bone = meta_rig.pose.bones[bone_name]
            if mode == "JAW":
                try:
                    pose_bone.rigify_type = 'basic.pivot'
                    pose_bone.rigify_parameters.make_extra_control = True
                    pose_bone.rigify_parameters.pivot_master_widget_type = "jaw"
                    pose_bone.rigify_parameters.make_control = False
                    pose_bone.rigify_parameters.make_extra_deform = True
                except:
                    utils.log_error("Unable to set rigify Jaw type.")
            elif mode == "TONGUE":
                try:
                    pose_bone.rigify_type = 'face.basic_tongue'
                except:
                    utils.log_error("Unable to set rigify Tongue type.")
            else:
                pose_bone.rigify_type = ""


def correct_meta_rig(meta_rig):
    """Add a slight displacement (if needed) to the knee and elbow to ensure the poles are the right way.
    """

    fix_bend(meta_rig, "thigh.L", "shin.L", mathutils.Vector((0,-1,0)))
    fix_bend(meta_rig, "thigh.R", "shin.R", mathutils.Vector((0,-1,0)))
    fix_bend(meta_rig, "upper_arm.L", "forearm.L", mathutils.Vector((0,1,0)))
    fix_bend(meta_rig, "upper_arm.R", "forearm.R", mathutils.Vector((0,1,0)))


def reparent_to_rigify(chr_cache, cc3_rig, rigify_rig):
    """Unparent (with transform) from the original CC3 rig and reparent to the new rigify rig (with automatic weights for the body),
       setting the armature modifiers to the new rig.

       The automatic weights will generate vertex weights for the additional face bones in the new rig.
       (But only for the Body mesh)
    """

    props = bpy.context.scene.CC3ImportProps

    if utils.set_mode("OBJECT"):

        BODY_TYPES = ["BODY", "TEARLINE", "OCCLUSION"]

        for obj in cc3_rig.children:
            if obj.type == "MESH" and obj.parent == cc3_rig:

                obj_cache = chr_cache.get_object_cache(obj)

                if utils.try_select_object(obj, True) and utils.set_active_object(obj):
                    bpy.ops.object.parent_clear(type = "CLEAR_KEEP_TRANSFORM")

                # only the body will generate the automatic weights for the face rig.
                if obj_cache and obj_cache.object_type in BODY_TYPES:

                    # remove all armature modifiers as parent with automatic weights will add them
                    modifiers.remove_object_modifiers(obj, "ARMATURE")

                    if utils.try_select_object(rigify_rig) and utils.set_active_object(rigify_rig):
                        bpy.ops.object.parent_set(type = "ARMATURE_AUTO", keep_transform = True)

                else:

                    if utils.try_select_object(rigify_rig) and utils.set_active_object(rigify_rig):
                        bpy.ops.object.parent_set(type = "OBJECT", keep_transform = True)

                    arm_mod : bpy.types.ArmatureModifier = modifiers.add_armature_modifier(obj, True)
                    if arm_mod:
                        arm_mod.object = rigify_rig


def clean_up(chr_cache, cc3_rig, rigify_rig, meta_rig):
    """Rename the rigs, hide the original CC3 Armature and remove the meta rig.
       Set the new rig into pose mode.
    """

    rig_name = cc3_rig.name
    cc3_rig.name = rig_name + "_OldCC"
    cc3_rig.hide_set(True)
    bpy.data.objects.remove(meta_rig)
    rigify_rig.name = rig_name + "_Rigify"

    if utils.try_select_object(rigify_rig, True):
        if utils.set_active_object(rigify_rig):
            utils.set_mode("POSE")

    chr_cache.set_rigify_armature(rigify_rig)


class CC3Rigifier(bpy.types.Operator):
    """Rigify CC3 Character"""
    bl_idname = "cc3.rigifier"
    bl_label = "Rigifier"
    bl_options = {"REGISTER"}

    param: bpy.props.StringProperty(
            name = "param",
            default = "",
            options={"HIDDEN"}
        )

    cc3_rig = None
    meta_rig = None
    rigify_rig = None

    def add_meta_rig(self, face_rig):
        if utils.set_mode("OBJECT"):
            bpy.ops.object.armature_human_metarig_add()
            self.meta_rig = utils.get_active_object()
            if self.meta_rig is not None:
                self.meta_rig.location = (0,0,0)
                self.cc3_rig
                if self.cc3_rig is not None:
                    self.cc3_rig.location = (0,0,0)
                    self.cc3_rig.data.pose_position = "REST"
                    if not face_rig:
                        remove_face_rig(self.meta_rig)
                    match_meta_rig(self.meta_rig, self.cc3_rig, face_rig)
                else:
                    utils.log_error("Unable to locate imported CC3 rig!", self)
            else:
                utils.log_error("Unable to create meta rig!", self)
        else:
            utils.log_error("Not in OBJECT mode!", self)

    def execute(self, context):
        props: properties.CC3ImportProps = bpy.context.scene.CC3ImportProps
        chr_cache = props.get_context_character_cache(context)

        if chr_cache:

            self.cc3_rig = chr_cache.get_armature()

            if self.param == "ALL":

                if self.cc3_rig:
                    self.add_meta_rig(chr_cache.rig_face_rig)

                    if self.meta_rig:
                        correct_meta_rig(self.meta_rig)
                        bpy.ops.pose.rigify_generate()
                        self.rigify_rig = bpy.context.active_object

                        if self.rigify_rig:
                            reparent_to_rigify(chr_cache, self.cc3_rig, self.rigify_rig)
                            add_def_bones(self.cc3_rig, self.rigify_rig)
                            rename_vertex_groups(self.cc3_rig, self.rigify_rig)
                            clean_up(chr_cache, self.cc3_rig, self.rigify_rig, self.meta_rig)

                    chr_cache.rig_meta_rig = None

            elif self.param == "META_RIG":

                if self.cc3_rig:
                    self.add_meta_rig(chr_cache.rig_face_rig)

                    if self.meta_rig:
                        chr_cache.rig_meta_rig = self.meta_rig
                        correct_meta_rig(self.meta_rig)

            elif self.param == "RIGIFY_META":

                self.meta_rig = chr_cache.rig_meta_rig

                if self.cc3_rig and self.meta_rig:

                    if utils.set_mode("OBJECT") and utils.try_select_object(self.meta_rig) and utils.set_active_object(self.meta_rig):
                        bpy.ops.pose.rigify_generate()
                        self.rigify_rig = bpy.context.active_object

                        if self.rigify_rig:
                            reparent_to_rigify(chr_cache, self.cc3_rig, self.rigify_rig)
                            add_def_bones(self.cc3_rig, self.rigify_rig)
                            rename_vertex_groups(self.cc3_rig, self.rigify_rig)
                            clean_up(chr_cache, self.cc3_rig, self.rigify_rig, self.meta_rig)

                chr_cache.rig_meta_rig = None

        return {"FINISHED"}

    @classmethod
    def description(cls, context, properties):

        return "Rigification!"


def get_rigify_version():
    for mod in addon_utils.modules():
        name = mod.bl_info.get('name', "")
        if name == "Rigify":
            version = mod.bl_info.get('version', (-1, -1, -1))
            return version


def is_rigify_installed():
    context = bpy.context
    if "rigify" in context.preferences.addons.keys():
        return True
    return False

