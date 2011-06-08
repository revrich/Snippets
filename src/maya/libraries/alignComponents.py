# Credits: Zananick (Unknown).
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya

ALIGNEMENT_ANCHORS = None

def stacksHandler(object_):
	'''
	This Decorator Is Used To Handle Various Maya Stacks.

	@param object_: Python Object ( Object )
	@return: Python Function. ( Function )
	'''

	def stacksHandlerCall(*args, **kwargs):
		'''
		This Decorator Is Used To Handle Various Maya Stacks.

		@return: Python Object. ( Python )
		'''
		
		cmds.undoInfo(openChunk=True)
		value = object_(*args, **kwargs)
		cmds.undoInfo(closeChunk=True)
		# Maya Produces A Weird Command Error If Not Wrapped Here.
		try:
			cmds.repeatLast(addCommand="python(\"import %s; %s.%s()\")"% (__name__, __name__, object_.__name__), addCommandLabel=object_.__name__)
		except:
			pass
		return value

	return stacksHandlerCall

def getMVector(vector):
	'''
	This Definition Returns An MVector.

	@param vector: Vector. ( List )
	@return: MVector ( MVector )
	'''
	
	return OpenMaya.MVector(vector[0], vector[1], vector[2])

def normalize(vector):
	'''
	This Definition Returns The Normalized Vector.

	@param vector: Vector. ( List )
	@return: Normalized Vector ( Tuple )
	'''
	
	mVector = getMVector(vector)
	mVector.normalize()
	return (mVector.x, mVector.y, mVector.z)

def alignComponentsBetweenAnchors(anchorA, anchorB, components):
	'''
	This Definition Aligns Provided Components BetweenThe Two Anchors.

	@param anchorA: Anchor A. ( String )
	@param anchorB: Anchor B. ( String )
	@param components: Components To Align. ( List )
	'''
	
	vertices = cmds.ls(cmds.polyListComponentConversion(components, toVertex=True), fl=True)

	pointA = cmds.xform(anchorA, q=True, t=True, ws=True)
	pointB = cmds.xform(anchorB, q=True, t=True, ws=True)
	vectorA = normalize([pointB_ - pointA_ for pointA_, pointB_ in zip(pointA, pointB)])
	
	for vertex in vertices:
		pointC = cmds.xform(vertex, q=True, ws=True, t=True)
		vectorB = [pointC_ - pointA_ for pointA_, pointC_ in zip(pointA, pointC)]
		mVectorA = getMVector(vectorA)
		mVectorB = getMVector(vectorB)
		dot = mVectorB*mVectorA
		mVectorA *= dot
		offset = mVectorB - mVectorA
		cmds.xform(vertex, ws=True, r=True, t=(-offset.x, -offset.y, -offset.z))

def selectAnchors_Button_OnClicked(state):
	'''
	This Definition Is Triggered By The selectAnchors_Button Button When Clicked.
	
	@param state: Button State. ( Boolean )
	'''

	global ALIGNEMENT_ANCHORS

	selection = cmds.ls(sl=True, l=True, fl=True)
	if len(selection) == 2:
	    ALIGNEMENT_ANCHORS = (selection[0], selection[1])

def alignSelection_Button_OnClicked(state):
	'''
	This Definition Is Triggered By The alignSelection_Button Button When Clicked.
	
	@param state: Button State. ( Boolean )
	'''

	if ALIGNEMENT_ANCHORS:
		selection = cmds.ls(sl=True, l=True)
		selection and alignComponentsBetweenAnchors(ALIGNEMENT_ANCHORS[0], ALIGNEMENT_ANCHORS[1], selection)

def alignComponents_Window():
	'''
	This Definition Creates The Align Components Main Window.
	'''

	cmds.windowPref(enableAll=False)

	if (cmds.window("alignComponents_Window", exists=True)):
		cmds.deleteUI("alignComponents_Window")

	cmds.window("alignComponents_Window",
		title="Align Components",
		width=320)
	
	spacing=5

	cmds.columnLayout(adjustableColumn=True, rowSpacing=spacing)

	cmds.button("selectAnchors_Button", label="Select Anchors!", command=selectAnchors_Button_OnClicked)
	cmds.button("alignSelection_Button", label="Align Selection!", command=alignSelection_Button_OnClicked)

	cmds.showWindow("alignComponents_Window")

	cmds.windowPref(enableAll=True)

def alignComponents():
	'''
	This Definition Launches The Align Components Main Window.
	'''
	
	alignComponents_Window()

@stacksHandler
def IAlignComponents():
	'''
	This Definition Is The alignComponents Method Interface.
	'''

	alignComponents()