#------------------------------------------------------------------------#
# Copyright (c) 2015 Modenese L., Ceseracciu, E., Reggiani M., Lloyd, D.G.#
#                                                                         #
# Licensed under the Apache License, Version 2.0 (the "License");         #
# you may not use this file except in compliance with the License.        #
# You may obtain a copy of the License at                                 #
# http://www.apache.org/licenses/LICENSE-2.0.                             #
#                                                                         # 
# Unless required by applicable law or agreed to in writing, software     #
# distributed under the License is distributed on an "AS IS" BASIS,       #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or         #
# implied. See the License for the specific language governing            #
# permissions and limitations under the License.                          #
#                                                                         #
#    Author: Luca Modenese, August 2014                                   #
#                            revised for paper May 2015                   #
#    email:    l.modenese@sheffield.ac.uk                                 # 
#    adapted by Basilio Goncalves                                         #
# ----------------------------------------------------------------------- #
# 
# This function optimizes the muscle parameters as described in Modenese L, 
# Ceseracciu E, Reggiani M, Lloyd DG (2015). Estimation of 
# musculotendon parameters for scaled and subject specific musculoskeletal 
# models using an optimization technique. Journal of Biomechanics (submitted)
# and prints the results to command window.
# Also it stores information about the optimization in the structure SimInfo

# Written by Emiliano Ravera emiliano.ravera@uner.edu.ar as part of the 
# Python version of work by Luca Modenese in the parameterisation of muscle
# tendon properties.

#------ import packages --------- 
import os
import warnings
from matplotlib import pyplot as plt
import opensim as osim
from pathlib import Path
import numpy as np
import logging
from scipy import linalg, optimize
from sklearn.metrics import mean_squared_error
from time import time
from lxml import etree
from itertools import product
import re

# Public functions
def getModelJointDefinitions(osimModel):
    """Cache joint structure once - avoid repeated XML parsing"""
    # functon to retun a strcuture for a specifc model, returning a list of the
    # joints present in the model and their associated frames and subsequently
    # the bodies which make up these joints - operating under the assumption
    # that frames are written using the bodyName_offset as naming convention
    
    # Written by Emiliano Ravera emiliano.ravera@uner.edu.ar as part of the 
    # Python version of work by Luca Modenese in the parameterisation of muscle
    # tendon properties.
    
    # load model XML file  
    osimModel_filepath = osimModel.getInputFileName()
    osimModel_file = etree.parse(osimModel_filepath)
    model = osimModel_file.getroot()
    # create an empty dictionary to hold the data  
    jointStructure = {}
    
    # Weld Joint type
    for joint in model.findall('.//WeldJoint'):
        # add the name to the dictionary
        jointStructure[joint.get('name')] = {}
        # add the parent frame name
        jointStructure[joint.get('name')]['parentFrame'] = joint.find('socket_parent_frame').text
        # add the child frame name
        jointStructure[joint.get('name')]['childFrame'] = joint.find('socket_child_frame').text
        # add the parent body
        jointStructure[joint.get('name')]['parentBody'] = re.sub('_offset', '', joint.find('socket_parent_frame').text)
        # add the child body
        jointStructure[joint.get('name')]['childBody'] = re.sub('_offset', '', joint.find('socket_child_frame').text)
    # Pin Joint type
    for joint in model.findall('.//PinJoint'):
        # add the name to the dictionary
        jointStructure[joint.get('name')] = {}
        # add the parent frame name
        jointStructure[joint.get('name')]['parentFrame'] = joint.find('socket_parent_frame').text
        # add the child frame name
        jointStructure[joint.get('name')]['childFrame'] = joint.find('socket_child_frame').text
        # add the parent body
        jointStructure[joint.get('name')]['parentBody'] = re.sub('_offset', '', joint.find('socket_parent_frame').text)
        # add the child body
        jointStructure[joint.get('name')]['childBody'] = re.sub('_offset', '', joint.find('socket_child_frame').text)
    # Slider Joint type
    for joint in model.findall('.//SliderJoint'):
        # add the name to the dictionary
        jointStructure[joint.get('name')] = {}
        # add the parent frame name
        jointStructure[joint.get('name')]['parentFrame'] = joint.find('socket_parent_frame').text
        # add the child frame name
        jointStructure[joint.get('name')]['childFrame'] = joint.find('socket_child_frame').text
        # add the parent body
        jointStructure[joint.get('name')]['parentBody'] = re.sub('_offset', '', joint.find('socket_parent_frame').text)
        # add the child body
        jointStructure[joint.get('name')]['childBody'] = re.sub('_offset', '', joint.find('socket_child_frame').text)
    # Ball Joint type
    for joint in model.findall('.//BallJoint'):
        # add the name to the dictionary
        jointStructure[joint.get('name')] = {}
        # add the parent frame name
        jointStructure[joint.get('name')]['parentFrame'] = joint.find('socket_parent_frame').text
        # add the child frame name
        jointStructure[joint.get('name')]['childFrame'] = joint.find('socket_child_frame').text
        # add the parent body
        jointStructure[joint.get('name')]['parentBody'] = re.sub('_offset', '', joint.find('socket_parent_frame').text)
        # add the child body
        jointStructure[joint.get('name')]['childBody'] = re.sub('_offset', '', joint.find('socket_child_frame').text)
    # Ellipsoid Joint type
    for joint in model.findall('.//EllipsoidJoint'):
        # add the name to the dictionary
        jointStructure[joint.get('name')] = {}
        # add the parent frame name
        jointStructure[joint.get('name')]['parentFrame'] = joint.find('socket_parent_frame').text
        # add the child frame name
        jointStructure[joint.get('name')]['childFrame'] = joint.find('socket_child_frame').text
        # add the parent body
        jointStructure[joint.get('name')]['parentBody'] = re.sub('_offset', '', joint.find('socket_parent_frame').text)
        # add the child body
        jointStructure[joint.get('name')]['childBody'] = re.sub('_offset', '', joint.find('socket_child_frame').text)
    # Free Joint type
    for joint in model.findall('.//FreeJoint'):
        # add the name to the dictionary
        jointStructure[joint.get('name')] = {}
        # add the parent frame name
        jointStructure[joint.get('name')]['parentFrame'] = joint.find('socket_parent_frame').text
        # add the child frame name
        jointStructure[joint.get('name')]['childFrame'] = joint.find('socket_child_frame').text
        # add the parent body
        jointStructure[joint.get('name')]['parentBody'] = re.sub('_offset', '', joint.find('socket_parent_frame').text)
        # add the child body
        jointStructure[joint.get('name')]['childBody'] = re.sub('_offset', '', joint.find('socket_child_frame').text)
    # Custom Joint type
    for joint in model.findall('.//CustomJoint'):
        # add the name to the dictionary
        jointStructure[joint.get('name')] = {}
        # add the parent frame name
        jointStructure[joint.get('name')]['parentFrame'] = joint.find('socket_parent_frame').text
        # add the child frame name
        jointStructure[joint.get('name')]['childFrame'] = joint.find('socket_child_frame').text
        # add the parent body
        jointStructure[joint.get('name')]['parentBody'] = re.sub('_offset', '', joint.find('socket_parent_frame').text)
        # add the child body
        jointStructure[joint.get('name')]['childBody'] = re.sub('_offset', '', joint.find('socket_child_frame').text)
    
        
    return jointStructure

# NEW: Cache joint structure at module level or pass it around
_joint_structure_cache = {}

def get_cached_joint_structure(osimModel):
    """Get or create cached joint structure"""
    model_path = osimModel.getInputFileName()
    if model_path not in _joint_structure_cache:
        _joint_structure_cache[model_path] = getModelJointDefinitions(osimModel)
    return _joint_structure_cache[model_path]

def getChildBodyJoint(jointStructure, bodyName):
    """Optimized: use dict lookup instead of list comprehension"""
    for joint_name, joint_data in jointStructure.items():
        if joint_data.get('childBody') == bodyName:
            return [joint_name]
    return []

def getParentBodyJoint(jointStructure, bodyName):
    """Optimized: use dict lookup instead of list comprehension"""
    for joint_name, joint_data in jointStructure.items():
        if joint_data.get('parentBody') == bodyName:
            return [joint_name]
    return []

def getMuscleAttachBody(osimModel, musclePathPointName):
    # Functon to return the name of the muscel path point from a specified model
    # and muscle, where the specified body is the parent body
    
    # Written by Emiliano Ravera emiliano.ravera@uner.edu.ar as part of the 
    # Python version of work by Luca Modenese in the parameterisation of muscle
    # tendon properties.
    
    # Input: OpenSim model objects
    # Output: bodyName - the body for the specified musclepath
    
    bodyName = []
    # load model XML file  
    osimModel_filepath = osimModel.getInputFileName()
    osimModel_file = etree.parse(osimModel_filepath)
    model = osimModel_file.getroot()
    
    musclePath = model.findall('./' + musclePathPointName)
    
    for musclePath in model.findall('.//PathPoint'):
        if musclePath.get('name') == musclePathPointName:
            bodyName = re.sub('/bodyset/', '', musclePath.find('socket_parent_frame').text)
            
    for musclePath in model.findall('.//ConditionalPathPoint'):
        if musclePath.get('name') == musclePathPointName:
            bodyName = re.sub('/bodyset/', '', musclePath.find('socket_parent_frame').text)
    
    for musclePath in model.findall('.//MovingPathPoint'):
        if musclePath.get('name') == musclePathPointName:
            bodyName = re.sub('/bodyset/', '', musclePath.find('socket_parent_frame').text)
        
    return bodyName

#-------------------------------- 

# Private functions
def getJointsSpannedByMuscle(osimModel, OSMuscleName):
    """Optimized version"""
    BodySet = osimModel.getBodySet()
    muscle = osimModel.getMuscles().get(OSMuscleName)
    
    # Use cached joint structure
    jointStructure = get_cached_joint_structure(osimModel)
    
    # Build body-to-parent-joint lookup once (MAJOR SPEEDUP)
    body_to_child_joint = {}
    for joint_name, joint_data in jointStructure.items():
        child_body = joint_data['childBody']
        body_to_child_joint[child_body] = joint_name
    
    # Extract path points
    musclePath = muscle.getGeometryPath()
    musclePathPointSet = musclePath.getPathPointSet()
    
    muscleAttachBodies = []
    currentAttachBody = None
    
    for n_point in range(musclePathPointSet.getSize()):
        muscelPathPoint_name = musclePathPointSet.get(n_point).getName()
        newAttachBody = getMuscleAttachBody(osimModel, muscelPathPoint_name)
        
        if newAttachBody != currentAttachBody:
            muscleAttachBodies.append(newAttachBody)
            currentAttachBody = newAttachBody
    
    # Traverse from distal to proximal
    DistalBodyName = muscleAttachBodies[-1]
    ProximalBodyName = muscleAttachBodies[0]
    
    jointNameSet = []
    NoDofjointNameSet = []
    bodyName = DistalBodyName
    visited_joints = set()  # Prevent infinite loops
    
    while bodyName != ProximalBodyName:
        # Fast lookup using pre-built dictionary
        spannedJointName = body_to_child_joint.get(bodyName)
        
        if not spannedJointName or spannedJointName in visited_joints:
            break
        
        visited_joints.add(spannedJointName)
        spannedJoint = osimModel.getJointSet().get(spannedJointName)
        
        if spannedJoint.numCoordinates() > 0:
            jointNameSet.append(spannedJointName)
        else:
            NoDofjointNameSet.append(spannedJointName)
        
        # Move to parent body
        bodyName = jointStructure[spannedJointName]['parentBody']
    
    return jointNameSet, NoDofjointNameSet

def getIndipCoordAndJoint(osimModel, constraint_coord_name):
    # Function that given a dependent coordinate finds the independent
    # coordinate and the associated joint. The function assumes that the
    # constraint is a CoordinateCoupleConstraint as used by Arnold, Delp and
    # LLLM. The function can be useful to manage the patellar joint for instance.
    
    # Input: OpenSim model objects
    # Output: ind_coord_name and ind_coord_joint_name - the joint with specific constraint
    
    # Written by Emiliano Ravera emiliano.ravera@uner.edu.ar as part of the 
    # Python version of work by Luca Modenese in the parameterisation of muscle
    # tendon properties.
    
    ind_coord_name = ''
    ind_coord_joint_name = ''
    # load model XML file  
    osimModel_filepath = osimModel.getInputFileName()
    osimModel_file = etree.parse(osimModel_filepath)
    model = osimModel_file.getroot()
        
    # double check: if not constrained then function returns
    flag = [1  for constraint in  model.findall('.//CoordinateCouplerConstraint') if constraint.get('name').find(constraint_coord_name)]
       
    if flag == []:
        # print(constraint_coord_name + ' is not a constrained coordinate.')
        logging.error(' ' + constraint_coord_name + ' is not a constrained coordinate.')
        return ind_coord_name, ind_coord_joint_name
    
    # otherwise search through the constraints
    for constraint in  model.findall('.//CoordinateCouplerConstraint'):
        
        # this function assumes that the constraint will be a coordinate
        # coupler contraint ( Arnold's model and LLLM uses this)
                
        # get dep coordinate and check if it is the coord of interest
        dep_coord_name = constraint.find('dependent_coordinate_name').text
        
        if dep_coord_name in constraint_coord_name:
            # print('WARNING: Only one indipendent coordinate is managed by the "getIndipCoordAndJoint" function yet.')
            logging.warning(' Only one indipendent coordinate is managed by the "getIndipCoordAndJoint" function yet.')
            
            ind_coord_name = constraint.find('independent_coordinate_names').text
            ind_coord_joint_name = constraint.find('independent_coordinate_names').text # assume the same name for coordinate and joint 
            
    return ind_coord_name, ind_coord_joint_name

def sampleMuscleQuantities(osimModel, OSMuscle, muscleQuant, N_EvalPoints):
    """Optimized version - use cached joint structure"""
    currentState = osimModel.initSystem()
    
    # Configuration parameters for joint space sampling
    limit_discr = 0  # Set to 1 to limit discretization increment
    min_increm_in_deg = 5  # Minimum increment in degrees when limit_discr is enabled
    
    # Use optimized joint traversal (now much faster)
    muscleCrossedJointSet, _ = getJointsSpannedByMuscle(osimModel, OSMuscle.getName())
    
    # Filter out zero-DOF joints early (SPEEDUP for welded joints)
    muscleCrossedJointSet = [j for j in muscleCrossedJointSet 
                             if osimModel.getJointSet().get(j).numCoordinates() > 0]
    
    # index for effective dofs
    DOF_Index = []
    CoordinateBoundaries = []
    degIncrem = []
    
    for _, curr_joint in enumerate(muscleCrossedJointSet):
        # Initial estimation of the nr of Dof of the CoordinateSet for that
        # joint before checking for locked and constraint dofs.
        nDOF = osimModel.getJointSet().get(curr_joint).numCoordinates()
        
        # skip welded joint and removes welded joint from muscleCrossedJointSet
        if nDOF == 0:
            continue
        
        # calculating effective dof for that joint
        effect_DOF = nDOF
        for n_coord in range(0,nDOF):
            # get coordinate
            curr_coord = osimModel.getJointSet().get(curr_joint).get_coordinates(n_coord)
            curr_coord_name = curr_coord.getName()
            
            # skip dof if locked
            if curr_coord.getLocked(currentState):
                continue
            
            # if coordinate is constrained then the independent coordinate and
            # associated joint will be listed in the sampling "map"
            if curr_coord.isConstrained(currentState) and not curr_coord.getLocked(currentState):
                constraint_coord_name = curr_coord_name
                # finding the independent coordinate
                ind_coord_name, ind_coord_joint_name = getIndipCoordAndJoint(osimModel, constraint_coord_name)
                # updating the coordinate name to be saved in the list
                curr_coord_name = ind_coord_name
                effect_DOF -= 1
                # ignoring constrained dof if they point to an independent
                # coordinate that has already been stored
                if osimModel.getCoordinateSet().getIndex(curr_coord_name) in DOF_Index:
                    continue
                # skip dof if independent coordinate locked (the coord
                # correspondent to the name needs to be extracted)
                if osimModel.getCoordinateSet().get(curr_coord_name).getLocked(currentState):
                    continue
                
            # NB: DOF_Index is used later in the string generated code.
            # CRUCIAL: the index of dof now is model based ("global") and
            # different from the joint based used until now.
            DOF_Index.append(osimModel.getCoordinateSet().getIndex(curr_coord_name))
            
            # necessary update/reload the curr_coord to avoid problems with 
            # dependent coordinates
            curr_coord = osimModel.getCoordinateSet().get(DOF_Index[-1])
            
            # Getting the values defining the range
            jointRange = np.zeros(2)
            jointRange[0] = curr_coord.getRangeMin()
            jointRange[1] = curr_coord.getRangeMax()
            
            # Storing range of motion conveniently
            CoordinateBoundaries.append(jointRange)
            
            # increments in the variables when sampling the mtl space. 
            # Increments are different for each dof and based on N_eval.
            # Defining the increments
            degIncrem.append((jointRange[1] - jointRange[0]) / (N_EvalPoints-1))
            
            # limit or not the discretization of the joint space sampling
            # a limit to the increase can be set though
            if limit_discr == 1 and degIncrem[-1] < np.radians(min_increm_in_deg):
                degIncrem[-1] = np.radians(min_increm_in_deg)
    
        
    # assigns an interval of variation following the initial and final value
    # for each dof X
        
    # setting up for loops in order to explore all the possible combination of
    # joint angles (looping on all the dofs of each joint for all the joint
    # crossed by the muscle).
    # The model pose is updated via: " coordToUpd.setValue(currentState,setAngleDof)"
    # The right dof to update is chosen via: "coordToUpd = osimModel.getCoordinateSet.get(n_instr)"
    
    # generate a dictionary with CoordinateRange for each dof X. 
    # The dictionary keys are the DOF_Index in the model
    CoordinateRange = {}
    for pos, dof in enumerate(DOF_Index):
        CoordinateRange[str(dof)] = np.linspace(CoordinateBoundaries[pos][0] , CoordinateBoundaries[pos][1], N_EvalPoints)
    
    # generate a list of dictionaries to explore all the possible combination of
    # joit angle
    CoordinateCombinations = [dict(zip(CoordinateRange.keys(), element)) for element in product(*CoordinateRange.values())] 
    
    # looping on all the dofs combinations
    musOutput = [None] * len(CoordinateCombinations)
    
    for iteration, DOF_comb in enumerate(CoordinateCombinations):
        # Set the model pose
        for dof_ind in DOF_comb.keys():
            coordToUpd = osimModel.getCoordinateSet().get(int(dof_ind))
            coordToUpd.setValue(currentState, CoordinateCombinations[iteration][dof_ind])
        
        # calculating muscle length for the muscle    
        if muscleQuant == 'MTL':
            musOutput[iteration] = OSMuscle.getGeometryPath().getLength(currentState)
            
        if muscleQuant == 'LfibNorm':
            OSMuscle.setActivation(currentState,1.0)
            osimModel.equilibrateMuscles(currentState)
            musOutput[iteration] = OSMuscle.getNormalizedFiberLength(currentState)
            
        if muscleQuant == 'Lten':
            OSMuscle.setActivation(currentState,1.0)
            osimModel.equilibrateMuscles(currentState)
            musOutput[iteration] = OSMuscle.getTendonLength(currentState)
            
        if muscleQuant == 'Ffib':
            OSMuscle.setActivation(currentState,1.0)
            osimModel.equilibrateMuscles(currentState)
            musOutput[iteration] = OSMuscle.getActiveFiberForce(currentState)
            
        if muscleQuant == 'all':
            OSMuscle.setActivation(currentState,1.0)
            osimModel.equilibrateMuscles(currentState)
            musOutput[iteration] = [ OSMuscle.getGeometryPath().getLength(currentState), \
                                    OSMuscle.getNormalizedFiberLength(currentState), \
                                    OSMuscle.getTendonLength(currentState), \
                                    OSMuscle.getActiveFiberForce(currentState), \
                                    OSMuscle.getPennationAngle(currentState) ]

    return musOutput

#-------------------------------- 

# Optimiser functions
def optimMuscleParams(osimModel_ref_filepath, osimModel_targ_filepath, N_eval, log_folder):
    
    
    # results file identifier
    res_file_id_exp = '_N' + str(N_eval)
    
    # import models
    osimModel_ref = osim.Model(osimModel_ref_filepath)
    osimModel_targ = osim.Model(osimModel_targ_filepath)
    
    # models details
    name = Path(osimModel_targ_filepath).stem
    ext = Path(osimModel_targ_filepath).suffix
    
    # assigning new name to the model
    osimModel_opt_name = name + '_opt' + res_file_id_exp + ext
    osimModel_targ.setName(osimModel_opt_name)
    
    # initializing log file
    log_folder = Path(log_folder)
    log_folder.mkdir(parents=True, exist_ok=True)
    log_file_path = log_folder / (name + '_opt' + res_file_id_exp + '.log')
    
    # Check if log file exists and find last processed muscle
    processed_muscles = set()
    if log_file_path.exists():
        with open(log_file_path, 'r') as f:
            for line in f:
                if 'Calculated optimized muscle parameters for' in line:
                    muscle_name = line.split('Calculated optimized muscle parameters for')[1].split('in')[0].strip()
                    processed_muscles.add(muscle_name)
        print(f'Found {len(processed_muscles)} already processed muscles in log file')
    
    logging.basicConfig(filename=str(log_file_path), filemode='a', format='%(levelname)s:%(message)s', level=logging.INFO)
        
    # get muscles
    muscles = osimModel_ref.getMuscles()
    muscles_scaled = osimModel_targ.getMuscles()
    
    # initialize with recognizable values
    LmOptLts_opt = -1000*np.ones((muscles.getSize(),2))
    SimInfo = {}
    
    for n_mus in range(0, muscles.getSize()):
        
        # current muscle name (here so that it is possible to choose a single muscle when developing).
        curr_mus_name = muscles.get(n_mus).getName()
        
        # Skip if already processed
        if curr_mus_name in processed_muscles:
            print(f'Skipping muscle {n_mus+1}: {curr_mus_name} (already processed)')
            continue
        
        tic = time()
        print('processing mus ' + str(n_mus+1) + ': ' + curr_mus_name)
        
        # import muscles
        curr_mus = muscles.get(curr_mus_name)
        curr_mus_scaled = muscles_scaled.get(curr_mus_name)
        
        # extracting the muscle parameters from reference model
        LmOptLts = [curr_mus.getOptimalFiberLength(), curr_mus.getTendonSlackLength()]
        PenAngleOpt = curr_mus.getPennationAngleAtOptimalFiberLength()
        Mus_ref = sampleMuscleQuantities(osimModel_ref,curr_mus,'all',N_eval)
        
        # calculating minimum fiber length before having pennation 90 deg
        # acos(0.1) = 1.47 red = 84 degrees, chosen as in OpenSim
        limitPenAngle = np.arccos(0.1)
        # this is the minimum length the fiber can be for geometrical reasons.
        LfibNorm_min = np.sin(PenAngleOpt) / np.sin(limitPenAngle)
        # LfibNorm as calculated above can be shorter than the minimum length
        # at which the fiber can generate force (taken to be 0.5 Zajac 1989)
        if LfibNorm_min < 0.5:
            LfibNorm_min = 0.5
        
        # muscle-tendon paramenters value
        MTL_ref = [musc_param_iter[0] for musc_param_iter in Mus_ref]
        LfibNorm_ref = [musc_param_iter[1] for musc_param_iter in Mus_ref]
        LtenNorm_ref = [musc_param_iter[2]/LmOptLts[1] for musc_param_iter in Mus_ref]
        penAngle_ref = [musc_param_iter[4] for musc_param_iter in Mus_ref]
        # LfibNomrOnTen_ref = LfibNorm_ref.*cos(penAngle_ref)
        LfibNomrOnTen_ref = [(musc_param_iter[1]*np.cos(musc_param_iter[4])) for musc_param_iter in Mus_ref]         
        
        # checking the muscle configuration that do not respect the condition.
        okList = [pos for pos, value in enumerate(LfibNorm_ref) if value > LfibNorm_min]
        # keeping only acceptable values
        MTL_ref = np.array([MTL_ref[index] for index in okList])
        LfibNorm_ref = np.array([LfibNorm_ref[index] for index in okList])
        LtenNorm_ref = np.array([LtenNorm_ref[index] for index in okList])
        penAngle_ref = np.array([penAngle_ref[index] for index in okList])
        LfibNomrOnTen_ref = np.array([LfibNomrOnTen_ref[index] for index in okList])
        
        # in the target only MTL is needed for all muscles
        MTL_targ = sampleMuscleQuantities(osimModel_targ,curr_mus_scaled,'MTL',N_eval)
        evalTotPoints = len(MTL_targ)
        MTL_targ = np.array([MTL_targ[index] for index in okList])
        evalOkPoints  = len(MTL_targ)
        
        # The problem to be solved is: 
        # [LmNorm*cos(penAngle) LtNorm]*[Lmopt Lts]' = MTL;
        # written as Ax = b or their equivalent (A^T A) x = (A^T b)  
        A = np.array([LfibNomrOnTen_ref , LtenNorm_ref]).T
        b = MTL_targ
        
        # ===== LINSOL =======
        # solving the problem to calculate the muscle param 
        x = linalg.solve(np.dot(A.T , A) , np.dot(A.T , b))
        LmOptLts_opt[n_mus] = x
        
        # checking the results
        if np.min(x) <= 0:
            # informing the user
            line0 = ' '
            line1 = 'Negative value estimated for muscle parameter of muscle ' + curr_mus_name + '\n'
            line2 = '                         Lm Opt        Lts' + '\n'
            line3 = 'Template model       : ' + str(LmOptLts) + '\n'
            line4 ='Optimized param      : ' + str(LmOptLts_opt[n_mus]) + '\n'
            
            # ===== IMPLEMENTING CORRECTIONS IF ESTIMATION IS NOT CORRECT =======
            x = optimize.nnls(np.dot(A.T , A) , np.dot(A.T , b))
            x = x[0]
            LmOptLts_opt[n_mus] = x
            line5 = 'Opt params (optimize.nnls): ' + str(LmOptLts_opt[n_mus])
            
            logging.info(line0 + line1 + line2 + line3 + line4 + line5 + '\n')
            # In our tests, if something goes wrong is generally tendon slack 
            # length becoming negative or zero because tendon length doesn't change
            # throughout the range of motion, so lowering the rank of A.
            if np.min(x) <= 0:
                # analyzes of Lten behaviour
                Lten_ref = [musc_param_iter[2] for musc_param_iter in Mus_ref]
                Lten_ref = np.array([Lten_ref[index] for index in okList])
                if (np.max(Lten_ref) - np.min(Lten_ref)) < 0.0001:
                    logging.warning(' Tendon length not changing throughout range of motion')
                
                # calculating proportion of tendon and fiber
                Lten_fraction = Lten_ref/MTL_ref
                Lten_targ = Lten_fraction*MTL_targ
                
                # first round: optimizing Lopt maintaing the proportion of
                # tendon as in the reference model
                A1 = np.array([LfibNomrOnTen_ref , LtenNorm_ref*0]).T
                b1 = MTL_targ - Lten_targ
                x1 = optimize.nnls(np.dot(A1.T , A1) , np.dot(A1.T , b1))
                x[0] = x1[0][0]
                
                # second round: using the optimized Lopt to recalculate Lts
                A2 = np.array([LfibNomrOnTen_ref*0 , LtenNorm_ref]).T
                b2 = MTL_targ - np.dot(A1,x1[0])
                x2 = optimize.nnls(np.dot(A2.T , A2) , np.dot(A2.T , b2))
                x[1] = x2[0][1]
                
                LmOptLts_opt[n_mus] = x
            
        
        # Here tests about/against optimizers were implemented
        
        # calculating the error (mean squared errors)
        fval = mean_squared_error(b, np.dot(A,x), squared=False)
        
        # update muscles from scaled model
        curr_mus_scaled.setOptimalFiberLength(LmOptLts_opt[n_mus][0])
        curr_mus_scaled.setTendonSlackLength(LmOptLts_opt[n_mus][1])
        
        # PRINT LOGS
        toc = time() - tic
        line0 = ' '
        line1 = 'Calculated optimized muscle parameters for ' + curr_mus.getName() + ' in ' +  str(toc) + ' seconds.' + '\n'
        line2 = '                         Lm Opt        Lts' + '\n'
        line3 = 'Template model       : ' + str(LmOptLts) + '\n'
        line4 = 'Optimized param      : ' + str(LmOptLts_opt[n_mus]) + '\n'
        line5 = 'Nr of eval points    : ' + str(evalOkPoints) + '/' + str(evalTotPoints) + ' used' + '\n'
        line6 = 'fval                 : ' + str(fval) + '\n'
        line7 = 'var from template [%]: ' + str(100*(np.abs(LmOptLts - LmOptLts_opt[n_mus])) / LmOptLts) + '%' + '\n'
        
        logging.info(line0 + line1 + line2 + line3 + line4 + line5 + line6 + line7 + '\n')
              
        # SIMULATION INFO AND RESULTS
        
        SimInfo[n_mus] = {}
        SimInfo[n_mus]['colheader'] = curr_mus.getName()
        SimInfo[n_mus]['LmOptLts_ref'] = LmOptLts
        SimInfo[n_mus]['LmOptLts_opt'] = LmOptLts_opt[n_mus]
        SimInfo[n_mus]['varPercLmOptLts'] = 100*(np.abs(LmOptLts - LmOptLts_opt[n_mus])) / LmOptLts
        SimInfo[n_mus]['sampledEvalPoints'] = evalOkPoints
        SimInfo[n_mus]['sampledEvalPoints'] = evalTotPoints
        SimInfo[n_mus]['fval'] = fval
    
    # assigning optimized model as output
    osimModel_opt = osimModel_targ
            
    return osimModel_opt, SimInfo


def plot_optimization_results(intial_model_path, optimised_model_path):

    base_model = osim.Model(intial_model_path)
    optimized_model = osim.Model(optimised_model_path)
    
    muscles = base_model.getMuscles()
    n_muscles = muscles.getSize()
    
    params = ['optimal_fiber_length', 'tendon_slack_length', 'pennation_angle_at_optimal']
    fig, axes = plt.subplots(len(params), 1, figsize=(8, 12))
    
    for ax, param in zip(axes, params):
        ax.set_title(param.replace('_', ' ').title())
        ax.set_xlabel('Muscle Index')
        ax.set_ylabel(param.replace('_', ' ').title())
        for i in range(n_muscles):
            muscle = muscles.get(i)
            muscle_name = muscle.getName()
            base_muscle = base_model.getMuscles().get(muscle_name)
            optim_muscle = optimized_model.getMuscles().get(muscle_name)
            if param == 'optimal_fiber_length':
                base_value = base_muscle.getOptimalFiberLength()
                optim_value = optim_muscle.getOptimalFiberLength()
            elif param == 'tendon_slack_length':
                base_value = base_muscle.getTendonSlackLength()
                optim_value = optim_muscle.getTendonSlackLength()
            elif param == 'pennation_angle_at_optimal':
                base_value = base_muscle.getPennationAngleAtOptimalFiberLength()
                optim_value = optim_muscle.getPennationAngleAtOptimalFiberLength()
            
            # bar plot
            ax.bar(i - 0.2, base_value, width=0.4, label='Base' if i == 0 else "", color='b')
            ax.bar(i + 0.2, optim_value, width=0.4, label='Optimized' if i == 0 else "", color='r')

            # setting x-ticks
            ax.set_xticks(range(n_muscles))
            ax.set_xticklabels([muscles.get(i).getName() for i in range(n_muscles)], rotation=90, size=6)

        ax.legend()    
    plt.tight_layout()
    
    save_path = optimised_model_path.replace('.osim', '_muscle_params.png')
    plt.savefig(save_path)
    print(f'Optimization results plot saved to {save_path}')


def main(osim_model_ref_filepath=None, osim_model_targ_filepath=None):
    # ========= USER SETTINGS =======
    # model files with paths
    if osim_model_ref_filepath is None:
        osim_model_ref_filepath = input("Please provide the path to the reference model: ").strip('"')
    if osim_model_targ_filepath is None:
        osim_model_targ_filepath = input("Please provide the path to the target model: ").strip('"')
    optimized_model_folder = os.path.dirname(osim_model_targ_filepath)
    
    # evaluations
    n_eval = 2
    # ===============================

    # initializing folders and log file
    log_folder = optimized_model_folder
    
    # checking if results folder exists. If not, create it.
    if not os.path.isdir(optimized_model_folder):
        warnings.warn(f'Folder {optimized_model_folder} does not exist. It will be created.')
        os.makedirs(optimized_model_folder)

    # optimizing target model based on reference model for n_eval points per
    # degree of freedom
    osim_model_opt, sims_info = optimMuscleParams(osim_model_ref_filepath,
                                                    osim_model_targ_filepath,
                                                    n_eval,
                                                    log_folder)

    # printing the optimized model
    output_path = osim_model_targ_filepath.replace('.osim', f'_opt_N{n_eval}.osim')
    osim_model_opt.printToXML(output_path)
    print(f'Optimized model saved to: {output_path}')
    
    # plotting optimization results
    plot_optimization_results(osim_model_targ_filepath, output_path)


if __name__ == "__main__":
    main()