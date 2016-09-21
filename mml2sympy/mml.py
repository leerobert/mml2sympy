try:
    from io import StringIO
except:
    from StringIO import StringIO
from lxml import etree
from sympy import *

mml_operators2sympy = {
    '+': 'Add',
    '-': ''
}


def mml2solution(mml):
    pass


def tree2sympy(mmltree):
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
        sympyres += r")"
    elif mmltree.tag == "madd":
        if len(mmltree.getchildren()) < 2:
            raise Exception('madd element {0} doesn"t have at least 2 rows.'
                            .format(etree.tostring(mmltree)))
        sympyres += r"Add("
        for child in mmltree.getchildren():
            sympyres += tree2sympy(child)
            sympyres += r","
        sympyres += r")"
    elif mmltree.tag == "mmul":
        if len(mmltree.getchildren()) < 2:
            raise Exception('mmul element {0} doesn"t have at least 2 rows.'
                            .format(etree.tostring(mmltree)))
        sympyres += r"Mul("
        for child in mmltree.getchildren():
            sympyres += tree2sympy(child)
            sympyres += r","
        sympyres += r")"
    elif mmltree.tag == "msup":
        if len(mmltree.getchildren()) < 2:
            raise Exception('msup element {0} doesn"t have at least 2 rows.'
                            .format(etree.tostring(mmltree)))
        sympyres += r"Pow("
        sympyres += tree2sympy(mmltree.getchildren()[0])
        sympyres += r","
        sympyres += tree2sympy(mmltree.getchildren()[1])
        sympyres += ")"
    elif mmltree.tag == "mfrac":
        if len(mmltree.getchildren()) < 2:
            raise Exception("mfrac element {0} doesn't have at least 2 rows."
                            .format(etree.tostring(mmltree)))
        sympyres += r"Mul("
        sympyres += tree2sympy(mmltree.getchildren()[0])
        sympyres += r",Pow("
        sympyres += tree2sympy(mmltree.getchildren()[1])
        sympyres += r",Integer(-1))"  # close Pow
        sympyres += r")"
    elif mmltree.tag == "mrow":
        # handle the fill mrow tag... combine all subexpressions
        sympyres += ''.join([tree2sympy(mmltree_child)
                            for mmltree_child in mmltree.getchildren()])
    elif mmltree.tag == "mfenced":
        # handle the fill mrow tag... combine all subexpressions
        sympyres += ''.join([tree2sympy(mmltree_child)
                            for mmltree_child in mmltree.getchildren()])
    elif mmltree.tag == "msqrt":
        if len(mmltree.getchildren()) < 1:
            raise Exception("msqrt element {0} doesn't have any elements."
                            .format(etree.tostring(mmltree)))
        sympyres += r"Pow("
        sympyres += mml2sympy(mmltree.getchildren()[0])
        sympyres += r",Rational(1,2)"
        sympyres += r")"

    # Atomic elements (mi, mn)
    elif mmltree.tag == "mn" or mmltree.tag == "mi":
        content = mmltree.text
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


def ops2tree(mmltree):
    pass


def mml2tree(mml):
    '''
    Takes an MML string and converts it to lxml's etree format.
    '''
    if not isinstance(mml, str):
        raise Exception('mml must be of type str')

    parser = etree.XMLParser(ns_clean=True, remove_pis=True,
                             remove_comments=True, remove_blank_text=True)

    # remove the namespaces from the mml...
    # ns_cleaned = mml.replace(' xmlns="', ' xmlnamespace="')
    tree = etree.parse(StringIO(ns_cleaned), parser)
    # objectify.deannotate(tree, cleanup_namespaces=True, xsi=True, xsi_nil=True)

    return tree


def tree2mml(mmltree):
    ''' Takes the mml tree and builds the MML for that element '''
    if not mmltree:
        raise Exception('mmltree must be of type etree.XMLTree')

    math_element = etree.Element("math")
    mstyle_element = etree.SubElement(math_element, "mstyle")
    full_mml_element = mstyle_elemnt.extend()

    return etree.tostring()


def _children_contain_operators(mmltree):
    for elem in mmltree.getchildren():
        if elem.tag == 'mo':
            return True
    return False


class Expression(object):
    pass


class Solution(object):

    def __init__(self, expressions=None):
        if not expressions:
            expressions = []
        self.expressions = expressions
