# Credits: Zananick (Unknown).
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya

__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2010 - 2014 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["ALIGNEMENT_ANCHORS",
			"stacksHandler",
			"getMVector",
			"normalize",
			"alignComponentsBetweenAnchors",
			"selectAnchors_button_OnClicked",
			"alignSelection_button_OnClicked",
			"alignSelectionOnXAxis_button_OnClicked",
			"alignSelectionOnYAxis_button_OnClicked",
			"alignSelectionOnZAxis_button_OnClicked",
			"alignComponents_window",
			"alignComponents",
			"IAlignComponents"]

ALIGNEMENT_ANCHORS = None

def stacksHandler(object):
	"""
	Handles Maya stacks.

	:param object: Python object.
	:type object: object
	:return: Python function.
	:rtype: object
	"""

	def stacksHandlerCall(*args, **kwargs):
		"""
		Handles Maya stacks.

		:return: Python object.
		:rtype: object
		"""

		cmds.undoInfo(openChunk=True)
		value = object(*args, **kwargs)
		cmds.undoInfo(closeChunk=True)
		# Maya produces a weird command error if not wrapped here.
		try:
			cmds.repeatLast(addCommand="python(\"import %s; %s.%s()\")" % (__name__, __name__, object.__name__), addCommandLabel=object.__name__)
		except:
			pass
		return value

	return stacksHandlerCall

def getMVector(vector):
	"""
	Returns an MVector.

	:param vector: Vector.
	:type vector: list
	:return: MVector
	:rtype: MVector
	"""

	return OpenMaya.MVector(vector[0], vector[1], vector[2])

def normalize(vector):
	"""
	Returns the normalized vector.

	:param vector: Vector.
	:type vector: list
	:return: Normalized vector
	:rtype: tuple
	"""

	mVector = getMVector(vector)
	mVector.normalize()
	return (mVector.x, mVector.y, mVector.z)

def alignComponentsBetweenAnchors(anchorA, anchorB, components, axis=("X", "Y", "Z")):
	"""
	Aligns given Components between the two anchors.

	:param anchorA: Anchor a.
	:type anchorA: str
	:param anchorB: Anchor b.
	:type anchorB: str
	:param components: Components to align.
	:type components: list
	:param axis: Collapse axis.
	:type axis: tuple
	"""

	vertices = cmds.ls(cmds.polyListComponentConversion(components, toVertex=True), fl=True)

	pointA = cmds.xform(anchorA, q=True, t=True, ws=True)
	pointB = cmds.xform(anchorB, q=True, t=True, ws=True)
	vectorA = normalize([pointB_ - pointA_ for pointA_, pointB_ in zip(pointA, pointB)])

	for vertex in vertices:
		pointC = cmds.xform(vertex, q=True, ws=True, t=True)
		vectorB = [pointC_ - pointA_ for pointA_, pointC_ in zip(pointA, pointC)]
		mVectorA = getMVector(vectorA)
		mVectorB = getMVector(vectorB)
		dot = mVectorB * mVectorA
		mVectorA *= dot
		offset = mVectorB - mVectorA

		xValue = "X" in axis and - offset.x or 0
		yValue = "Y" in axis and - offset.y or 0
		zValue = "Z" in axis and - offset.z or 0

		cmds.xform(vertex, ws=True, r=True, t=(xValue, yValue, zValue))

@stacksHandler
def selectAnchors_button_OnClicked(state=None):
	"""
	Defines the slot triggered by **selectAnchors_button** button when clicked.

	:param state: Button state.
	:type state: bool
	"""

	global ALIGNEMENT_ANCHORS

	selection = cmds.ls(sl=True, l=True, fl=True)
	if len(selection) == 2:
		ALIGNEMENT_ANCHORS = (selection[0], selection[1])
	else:
		mel.eval("warning(\"%s | failed to retrieve anchors, you need to select exactly two objects or components!\")" % __name__)

@stacksHandler
def alignSelection_button_OnClicked(state=None):
	"""
	Defines the slot triggered by **alignSelection_button** button when clicked.

	:param state: Button state.
	:type state: bool
	"""

	if ALIGNEMENT_ANCHORS:
		selection = cmds.ls(sl=True, l=True)
		selection and alignComponentsBetweenAnchors(ALIGNEMENT_ANCHORS[0], ALIGNEMENT_ANCHORS[1], selection)

@stacksHandler
def alignSelectionOnXAxis_button_OnClicked(state=None):
	"""
	Defines the slot triggered by **alignSelectionOnXAxis_button** button when clicked.

	:param state: Button state.
	:type state: bool
	"""

	if ALIGNEMENT_ANCHORS:
		selection = cmds.ls(sl=True, l=True)
		selection and alignComponentsBetweenAnchors(ALIGNEMENT_ANCHORS[0], ALIGNEMENT_ANCHORS[1], selection, axis=("X"))

@stacksHandler
def alignSelectionOnYAxis_button_OnClicked(state=None):
	"""
	Defines the slot triggered by **alignSelectionOnYAxis_button** button when clicked.

	:param state: Button state.
	:type state: bool
	"""

	if ALIGNEMENT_ANCHORS:
		selection = cmds.ls(sl=True, l=True)
		selection and alignComponentsBetweenAnchors(ALIGNEMENT_ANCHORS[0], ALIGNEMENT_ANCHORS[1], selection, axis=("Y"))

@stacksHandler
def alignSelectionOnZAxis_button_OnClicked(state=None):
	"""
	Defines the slot triggered by **alignSelectionOnZAxis_button** button when clicked.

	:param state: Button state.
	:type state: bool
	"""

	if ALIGNEMENT_ANCHORS:
		selection = cmds.ls(sl=True, l=True)
		selection and alignComponentsBetweenAnchors(ALIGNEMENT_ANCHORS[0], ALIGNEMENT_ANCHORS[1], selection, axis=("Z"))

def alignComponents_window():
	"""
	Creates the 'Align Components' main window.
	"""

	cmds.windowPref(enableAll=False)

	if (cmds.window("alignComponents_window", exists=True)):
		cmds.deleteUI("alignComponents_window")

	cmds.window("alignComponents_window",
		title="Align Components",
		width=320)

	spacing = 5

	cmds.columnLayout(adjustableColumn=True, rowSpacing=spacing)

	cmds.button("selectAnchors_button", label="Select Anchors!", command=selectAnchors_button_OnClicked)

	cmds.separator(height=10, style="singleDash")

	cmds.button("alignSelection_button", label="Align Selection!", command=alignSelection_button_OnClicked)

	cmds.separator(height=10, style="singleDash")

	cmds.button("alignSelectionOnXAxis_button", label="Align Selection On X!", command=alignSelectionOnXAxis_button_OnClicked)
	cmds.button("alignSelectionOnYAxis_button", label="Align Selection On Y!", command=alignSelectionOnYAxis_button_OnClicked)
	cmds.button("alignSelectionOnZAxis_button", label="Align Selection On Z!", command=alignSelectionOnZAxis_button_OnClicked)

	cmds.showWindow("alignComponents_window")

	cmds.windowPref(enableAll=True)

def alignComponents():
	"""
	Launches the 'Align Components' main window.
	"""

	alignComponents_window()

@stacksHandler
def IAlignComponents():
	"""
	Defines the alignComponents definition Interface.
	"""

	alignComponents()
