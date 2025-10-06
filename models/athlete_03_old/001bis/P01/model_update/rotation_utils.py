import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from skspatial.objects import Vector
import json
import math as m

def axes_rotation(first, second): # mri and osim are 3x3 matrices - second is transformed to the first

        # calculate centroids
    center_first = np.mean(first, axis = 0)
    center_second = np.mean(second, axis = 0 )

        # subtract centroids
    zeroed_first = first - center_first
    zeroed_second = second - center_second

        # find rotation using singular value decomposition
    H = np.matmul(zeroed_second.T, zeroed_first )
    U,S,Vt = np.linalg.svd(H)
    R = np.matmul(Vt.T, U.T)
    #print('R',R)

        # check that determinate is not negative and fix if needed
    if np.linalg.det(R)<0:
        print('the determinant is less than zero, recalculate r')
        Vt[2,:] *= -1
        R =np.matmul(Vt.T, U.T)
        # print('new R:', R)

        # define tranlsation
    new_center_second = np.mean(np.matmul(R,zeroed_second.T), axis = 0)
    t = -new_center_second + center_first  
    # print(t)
    return R, t, center_first, center_second


def apply_transform(data, R, template):
    data_zeroed = data - np.mean(data, axis = 0)
    rotated = (np.matmul(R, data_zeroed.T)).T
    t = np.mean(template, axis = 0) - np.mean(rotated, axis = 0)
    transformed = rotated + t
    return transformed

def apply_rotate_zero_origin(data, R):
    data_zeroed = data - np.mean(data, axis = 0)
    rotated = (np.matmul(R, data_zeroed.T)).T
    return rotated

def check_axes_rotation(mri, osim, R, t):
    
    # transform osim axes
    A_transformed = np.matmul(R, osim.T) + t
    A_transformed = A_transformed.T
    
    # Find and print the error
    rmse = np.sqrt(np.mean(np.square(A_transformed - mri)))
    print ("RMSE:", rmse)

def plot_compare_axes(mri, osim):
    fig = px.scatter()
    fig.add_trace(go.Scatter3d(
        x=mri[:,0], y=mri[:,1], z=mri[:,2], 
        mode = 'markers + text',
        text=["mri_X", "mri_Y", "mri_Z"],
        textposition="top center"))
    fig.add_trace(go.Scatter3d(
        x=osim[:,0], y=osim[:,1], z=osim[:,2], 
        mode = 'markers + text',
        text=["osim_x", "osim_y", "osim_z"],
        textposition="top center"))
    fig.show()

def plane_normal(p1, p2, p3):
    v1 = p1 - p2
    v2 = p3 - p2
    v3 = np.cross(v1, v2)
    return v3/np.linalg.norm(v3)

def find_axis(lms, keys): 
    # lms is a dictionary, keys should be in order such that the first lm is at the origin of two vectors
    
    p1, p2, p3 = np.array(lms[keys[0]]), np.array(lms[keys[1]]), np.array(lms[keys[2]])
    normal = plane_normal(p1, p2, p3)
    return normal

def load_orient_json(path_n_file, orient = True):
    file = open(path_n_file)
    data = json.load(file)
    points = {}
    for item in data['markups'][0]['controlPoints']:
        orient = np.array(item['orientation'])
        orient.shape = (3,3)
        position = np.matmul(orient, np.array(item['position']))
        points[item['label']] = position.tolist()
    numpy_points = np.array(list(points.values()))
    point_names = [i for i in points.keys()]
    return numpy_points, point_names

def project_point_to_plane(point_numpy, point_on_plane, normal_to_plane): 
    diff = point_numpy - point_on_plane
    proj = point_numpy - (diff*normal_to_plane)*normal_to_plane
    return proj

def rotation_matrix(axis, theta):
    # Return the rotation matrix associated with counterclockwise rotation about
    #the given axis by theta radians.

    axis = np.asarray(axis)
    axis = axis / m.sqrt(np.dot(axis, axis))
    a = m.cos(theta / 2.0)
    b, c, d = -axis * m.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

def point_distance_to_vector(point, vector):
    # the origin of the vector must have been subtracted from the point 
    dist = np.linalg.norm(np.cross(point, vector))/np.linalg.norm(vector)
    return dist

def project_point_to_vector(point, vector):
    # point is projected to the vector
    # the origin of the vector must have been subtracted from the point
    cos_a = np.dot(point, vector)/(np.linalg.norm(point)*np.linalg.norm(vector))
    dist = cos_a * np.linalg.norm(point)
    coords = dist * vector / np.linalg.norm(vector)
    return coords
    

def find_wrap_angles(vector_3d, base_vect = np.array([0,0,1])): 
    angles = []
    if np.linalg.norm(vector_3d*np.array([0,1,1]))  > 0.1**16: 
        # find the angle between base_vector and the other around x axis
        ang_x = Vector(base_vect*np.array([0,1,1])).angle_signed_3d(vector_3d*np.array([0,1,1]), direction_positive = [1,0,0])
    else: ang_x = 0
        # rotate base vector around x axis
    base_x = np.matmul(rotation_matrix(np.array([1,0,0]), ang_x), base_vect)
    angles.append(ang_x)
    
    if np.linalg.norm(base_x*np.array([1,0,1])) > 0.1**16:   
        # find the angle between base_x and the other around y axis
        ang_y = Vector(base_x*np.array([1,0,1])).angle_signed_3d(vector_3d*np.array([1,0,1]), direction_positive = [0,1,0])
    else: ang_y = 0
        # rotate base_x around y axis
    base_y = np.matmul(rotation_matrix(np.array([0,1,0]), ang_y), base_x)
    angles.append(ang_y)
    
    if np.linalg.norm(base_y*np.array([1,1,0]))  > 0.1**16:
        # find the angle between base_y and the other around z axis      
        ang_z = Vector(base_y*np.array([1,1,0])).angle_signed_3d(vector_3d*np.array([1,1,0]), direction_positive = [0,0,1])
    else: ang_z = 0
        # rotate base_y around z axis
    base_z = np.matmul(rotation_matrix(np.array([0,0,1]), ang_z), base_y)
    angles.append(ang_z)
    
    return angles, base_z

def return_transformed_wrapping_surfaces(transformed_landmarks, landmark_order_dict, names_in_order, body, mm_to_m = True):
    if mm_to_m == True:
        scale = 0.001
    else: scale = 1

    # calculate the half-length of cylinders
    quater_lngth = [np.linalg.norm(i) for i in (transformed_landmarks[landmark_order_dict['wrp_ax']]-transformed_landmarks[landmark_order_dict['wrp_transl']])]
    half_length = np.array(quater_lngth)*2
    half_length = [round(i*scale, 1) for i in half_length]
    
    # shift axes and radius landmarks to the centre of wrapping cylinders
    wrap_axes_transformed = transformed_landmarks[landmark_order_dict['wrp_ax']]-transformed_landmarks[landmark_order_dict['wrp_transl']]
    rads_transformed_translated = transformed_landmarks[landmark_order_dict['wrp_rad']]-transformed_landmarks[landmark_order_dict['wrp_transl']]

    # calculate new radia
    new_rads = []
    for i, rad in enumerate(rads_transformed_translated):
        new_rads.append(point_distance_to_vector(rads_transformed_translated[i], wrap_axes_transformed[i]))
    new_rads = [round(i*scale, 3) for i in new_rads] #*0.9

    # normalise direction of the rotation axis
    normal_wrap_axes_transformed = np.array([vect/np.linalg.norm(vect) for vect in wrap_axes_transformed])

    # calculate angles of rotation of the axis
    angls = []
    for vect in normal_wrap_axes_transformed:
        angls.append(find_wrap_angles(vect, base_vect = np.array([0,0,1]))[0])
    angls = [[round(i, 3) for i in j] for j in angls]

    # round translation values
    transl = [[round(i*scale, 3) for i in j] for j in transformed_landmarks[landmark_order_dict['wrp_transl']]]

    # save all data into a dictionary
    dct = {'body':[], 'name':[], 'translation':[], 'rotation':[], 'length':[], 'radius':[]}
    for i, name in enumerate(names_in_order):
        dct['body'].append(body)
        dct['name'].append(name)
        
        transl_x = transl[i][0]
        if abs(transl_x) <= 0.00001:
            transl_x = 0

        transl_y = transl[i][1]
        if abs(transl_y) <= 0.0001:
            transl_y = 0
        
        transl_z = transl[i][2]
        if abs(transl_z) <= 0.0001:
            transl_z = 0

        dct['translation'].append(f'{transl_x} {transl_y} {transl_z}')
        dct['length'].append(str(half_length[i]))
        dct['rotation'].append(f'{angls[i][0]} {angls[i][1]} {angls[i][2]}')
        dct['radius'].append(str(new_rads[i]))

    # create a dataframe
    df = pd.DataFrame(dct)
    return df
