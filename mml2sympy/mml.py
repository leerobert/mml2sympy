from copy import deepcopy
from lxml import etree, objectify
from sympy import *

from .util import isplit

MML_OP = 'mo'
MML_NUM = 'mn'
MML_SYM = 'mi'

ADD_OPS = ['+', '-']
MUL_OPS = ['/', '*', '×']
EQ_OPS = ['=']
SIMILAR_OPS = {
    '+': ADD_OPS,
    '-': ADD_OPS,
    '=': EQ_OPS,
    '*': MUL_OPS,
    '×': MUL_OPS,
    '/': MUL_OPS,
}

ADD_OPS_TAG = 'madd'
MUL_OPS_TAG = 'mmul'
EQ_OPS_TAG = 'meq'


def mml2sympy(mml):
    '''
    Converts the MML string into a list of
    sympy expressions.

    ~> returns a list of sympy srepr expressions.
        These expressions can be sympified into sympy code.
    '''
    if not isinstance(mml, str):
        raise Exception('mml must be a string containing the math ML XML')

    step_trees = mml2steptrees(mml)
    step_trees = [modify(step_tree) for step_tree in step_trees]
    step_sympies = [tree2sympy(step_tree) for step_tree in step_trees]

    return step_sympies


def mml2steps(mml):
    '''
    Takes mml and converts it into a list of separate MML documents
    containing the mml code for each individual step. Converts rows
    in mtable into a list of basic mml expressions.
    '''
    if not isinstance(mml, str):
        raise Exception('mml must be a string containing the math ML XML')

    step_trees = mml2steptrees(mml)

    steps = []
    for step_tree in step_trees:
        math = objectify.Element('math')
        mstyle = objectify.SubElement(math, 'mstyle')
        mstyle.extend(step_tree.getchildren())

        # take the newly build complete mathml object, clean it, string it
        objectify.deannotate(math, cleanup_namespaces=True)
        steps.append(etree.tostring(math).decode('UTF-8'))

    return steps


def mml2steptrees(mml):
    if not isinstance(mml, str):
        raise Exception('mml must be a string containing the math ML XML')

    tree = mml2tree(mml)

    if hasattr(tree, 'mstyle'):
        tree = tree.xpath('/math/mstyle')[0]

    if hasattr(tree, 'mtable'):
        step_trees = table2trees(tree.mtable)
    else:
        step_trees = [tree]

    return step_trees


def tree2sympy(mmltree,
               skip_elements=["mrow", "mfenced", "mstyle", "mtr", "mtd"],
               evaluate=False):
    sympyres = r""

    # Non-atomic elements
    if mmltree.tag == "meq":
        if len(mmltree.getchildren()) < 2:
            raise Exception('meq element {0} doesn"t have at least 2 rows.'
                            .format(etree.tostring(mmltree)))
        sympyres += r"Eq("
        sympyres += tree2sympy(mmltree.getchildren()[0])
        sympyres += r","
        sympyres += tree2sympy(mmltree.getchildren()[1])
        sympyres += r",evaluate={0})".format(evaluate)
    elif mmltree.tag == "madd":
        if len(mmltree.getchildren()) < 2:
            raise Exception('madd element {0} doesn"t have at least 2 rows.'
                            .format(etree.tostring(mmltree)))
        sympyres += r"Add("
        for child in mmltree.getchildren():
            sympyres += tree2sympy(child)
            sympyres += r","
        sympyres += r"evaluate={0})".format(evaluate)
    elif mmltree.tag == "mmul":
        if len(mmltree.getchildren()) < 2:
            raise Exception('mmul element {0} doesn"t have at least 2 rows.'
                            .format(etree.tostring(mmltree)))
        sympyres += r"Mul("
        for child in mmltree.getchildren():
            sympyres += tree2sympy(child)
            sympyres += r","
        sympyres += r"evaluate={0})".format(evaluate)
    elif mmltree.tag == "msup":
        if len(mmltree.getchildren()) < 2:
            raise Exception('msup element {0} doesn"t have at least 2 rows.'
                            .format(etree.tostring(mmltree)))
        sympyres += r"Pow("
        sympyres += tree2sympy(mmltree.getchildren()[0])
        sympyres += r","
        sympyres += tree2sympy(mmltree.getchildren()[1])
        sympyres += r",evaluate={0})".format(evaluate)
    elif mmltree.tag == "mfrac":
        if len(mmltree.getchildren()) < 2:
            raise Exception("mfrac element {0} doesn't have at least 2 rows."
                            .format(etree.tostring(mmltree)))
        sympyres += r"Mul("
        sympyres += tree2sympy(mmltree.getchildren()[0])
        sympyres += r",Pow("
        sympyres += tree2sympy(mmltree.getchildren()[1])
        sympyres += r",Integer(-1))"  # close Pow
        sympyres += r",evaluate={0})".format(evaluate)
    elif mmltree.tag == "msqrt":
        if len(mmltree.getchildren()) < 1:
            raise Exception("msqrt element {0} doesn't have any elements."
                            .format(etree.tostring(mmltree)))
        sympyres += r"Pow("
        sympyres += mml2sympy(mmltree.getchildren()[0])
        sympyres += r",Rational(1,2)"
        sympyres += r",evaluate={0})".format(evaluate)

    # Skip elements (mrow, mstyle, mfenced, etc.)
    elif mmltree.tag in skip_elements:
        # handle the fill mrow tag... combine all subexpressions
        sympyres += ''.join([tree2sympy(mmltree_child)
                            for mmltree_child in mmltree.getchildren()])

    # Atomic elements (mi, mn)
    elif mmltree.tag == "mn" or mmltree.tag == "mi":
        content = mmltree.text.strip()
        content_type = type(sympify(content))
        # Handle integer content (.text method) in 'cn' tags
        if content_type == Integer or\
                str(content_type) == "<class 'sympy.core.numbers.One'>":
            sympyres += r"Integer(" + content + r")"
        # Handle float content (.text method) in 'cn' tags
        elif content_type == Float:
            sympyres += r"Float('" + content + r"', prec = 15)"
        # Handle symbol
        else:
            sympyres += r"Symbol('" + content + r"')"

    return sympyres


def modify(mmltree):
    '''
    Recursively modifies the mmltree so that collections of mn, mi, mo
    objects are properly made into extended mml trees with
    custom elements in order to facilitate proper building
    of Add, Mul, etc.

    ~> returns the mmltree with elements modified accordingly
    '''
    # base case... just return the single element
    if not mmltree or not mmltree.getchildren():
        return mmltree

    # build a copy to use to modify and remove its children
    modified_tree = deepcopy(mmltree)
    [modified_tree.remove(child) for child in modified_tree.getchildren()]

    all_elements = mmltree.getchildren()
    op_elements = _highest_priority_ops(mmltree)

    if op_elements:
        elements_split = isplit(all_elements, op_elements)
        tag = _modified_tag_for(op_elements[0])
        op = objectify.Element(tag)
        for grouped_elems in elements_split:
            if len(grouped_elems) > 1:  # need to recursively modify
                placeholder = objectify.Element('placeholder')
                placeholder.extend(grouped_elems)
                modified_group_tree = modify(placeholder)
                op.extend(modified_group_tree.getchildren())  # rm placeholder
            else:  # just one element so append as leaf -- extend since list
                op.extend(grouped_elems)
        modified_tree.append(op)
    elif len(all_elements) > 1:  # no op elements so must be multiple mn/mi
        mmul = objectify.Element(MUL_OPS_TAG)
        mmul.extend(all_elements)
        modified_tree.append(mmul)
    else:  # only one element so just leave it alone
        modified_tree.extend(all_elements)

    # remove namespaces from objectify and return modified tree
    objectify.deannotate(modified_tree, cleanup_namespaces=True)
    return modified_tree


def _modified_tag_for(element):
    ' Return the proper modified tag for the element. '
    if element.text.strip() in ADD_OPS:
        tag = ADD_OPS_TAG
    elif element.text.strip() in EQ_OPS:
        tag = EQ_OPS_TAG
    elif element.text.strip() in MUL_OPS:
        tag = MUL_OPS_TAG
    else:
        raise Exception("modified tag not found for: {0}".format(element))

    return tag


def _highest_priority_ops(mmltree):
    ops = mmltree.findall(MML_OP)  # find all ops
    if not ops:
        return []  # no ops so return empty list

    ops.sort(key=lambda elem: elem.text.strip(), reverse=True)  # by =, +/-, ..
    highest_priority_op = ops[0]  # highest priority op
    similar_ops = SIMILAR_OPS.get(highest_priority_op.text.strip(), None)

    if not similar_ops:
        raise Exception("found op {0} that does not have similar_ops"
                        .format(highest_priority_op))

    return [elem for elem in ops if elem.text.strip() in similar_ops]


def table2trees(mmltree):
    if str(type(mmltree)) != "<class 'lxml.objectify.ObjectifiedElement'>":
        raise Exception("mmltree is not an lxml.objectify.ObjectifiedElement")
    if mmltree.tag != 'mtable':
        raise Exception("mmltree does not contain mtable as its root Element")

    # TODO: eventually support multiple mtd in mtr
    # this would support matrices, vectors, etc.
    child_trees = []
    for mtr in mmltree.getchildren():
        if hasattr(mtr, 'mtd'):
            child_trees.append(mtr.mtd)

    return child_trees


def mml2tree(mml):
    '''
    Takes an MML string and converts it to lxml's etree format.
    '''
    if not isinstance(mml, str):
        raise Exception('mml must be of type str')

    mml_cleaned = mml.replace(' xmlns="', ' xmlnamespace="')
    tree = objectify.fromstring(mml_cleaned)
    objectify.deannotate(tree, cleanup_namespaces=True)

    return tree
