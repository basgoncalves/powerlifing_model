import numpy as np
import math
import vtk

def sphereFit(data):

    #   Assemble the A matrix
    spX = np.array(data[:,0])
    spY = np.array(data[:,1])
    spZ = np.array(data[:,2])
    A = np.zeros((len(spX),4))
    A[:,0] = spX*2
    A[:,1] = spY*2
    A[:,2] = spZ*2
    A[:,3] = 1

    #   Assemble the f matrix
    f = np.zeros((len(spX),1))
    f[:,0] = (spX*spX) + (spY*spY) + (spZ*spZ)
    C, residules, rank, singval = np.linalg.lstsq(A,f)

    #   solve for the radius
    t = np.dot(C[0],C[0])+np.dot(C[1],C[1])+np.dot(C[2],C[2])+C[3]
 
    radius = math.sqrt(t[0])
    center = np.array([C[0], C[1], C[2]])

    return radius, center
    
    
def setSlicePoseFromSliceNormalAndPosition(sliceNode, sliceNormal, slicePosition, defaultViewUpDirection=None, backupViewRightDirection=None):
	## Fix up input directions
	if defaultViewUpDirection is None:
		defaultViewUpDirection = [0,0,1]
	if backupViewRightDirection is None:
		backupViewRightDirection = [-1,0,0]
	if sliceNormal[1]>=0:
		sliceNormalStandardized = sliceNormal
	else:
		sliceNormalStandardized = [-sliceNormal[0], -sliceNormal[1], -sliceNormal[2]]
	## Compute slice axes
	sliceNormalViewUpAngle = vtk.vtkMath.AngleBetweenVectors(sliceNormalStandardized, defaultViewUpDirection)
	angleTooSmallThresholdRad = 0.25 # about 15 degrees
	if sliceNormalViewUpAngle > angleTooSmallThresholdRad and sliceNormalViewUpAngle < vtk.vtkMath.Pi() - angleTooSmallThresholdRad:
		viewUpDirection = defaultViewUpDirection
		sliceAxisY = viewUpDirection
		sliceAxisX = [0, 0, 0]
		vtk.vtkMath.Cross(sliceAxisY, sliceNormalStandardized, sliceAxisX)
	else:
		sliceAxisX = backupViewRightDirection
	## Set slice axes
	sliceNode.SetSliceToRASByNTP(sliceNormalStandardized[0], sliceNormalStandardized[1], sliceNormalStandardized[2],
		sliceAxisX[0], sliceAxisX[1], sliceAxisX[2],
		slicePosition[0], slicePosition[1], slicePosition[2], 0)