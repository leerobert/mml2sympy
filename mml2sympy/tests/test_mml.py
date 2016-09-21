from mml2sympy.mml import mml2tree, tree2sympy
from lxml import etree


def test_tree2sympy():
    tree_mml = '''
      <meq>
        <madd>
          <mmul>
            <mn>2</mn>
            <mi>x</mi>
          </mmul>
          <mn>4</mn>
        </madd>
        <mn>7</mn>
      </meq>
    '''
    tree = etree.fromstring(tree_mml)
    sympy = tree2sympy(tree)
    assert sympy == "Eq(Add(Mul(Integer(2),Symbol('x'),),Integer(4),),Integer(7))"

    tree_mml = '''
      <mfrac>
        <mrow>
          <madd>
            <mmul>
              <mn>2</mn>
              <mi>x</mi>
            </mmul>
            <mn>4</mn>
          </madd>
        </mrow>
        <mrow>
          <mn>7</mn>
        </mrow>
      </mfrac>
    '''
    tree = etree.fromstring(tree_mml)
    sympy = tree2sympy(tree)
    assert sympy == "Mul(Add(Mul(Integer(2),Symbol('x'),),Integer(4),),Pow(Integer(7),Integer(-1)))"


def test_mml2tree():
    mml = '''
        <math xmlns="http://www.w3.org/1998/Math/MathML">
          <mstyle displaystyle="true">
            <mtable columnalign="left">
              <mtr>
                <mtd>
                  <mn> 2 </mn>
                  <mi> x </mi>
                  <mo> - </mo>
                  <mn> 4 </mn>
                  <mo> = </mo>
                  <mn> 7 </mn>
                </mtd>
              </mtr>
              <mtr>
                <mtd>
                  <mn> 2 </mn>
                  <mi> x </mi>
                  <mo> = </mo>
                  <mn> 11 </mn>
                </mtd>
              </mtr>
              <mtr>
                <mtd>
                  <mi> x </mi>
                  <mo> = </mo>
                  <mfrac>
                    <mrow>
                      <mn> 11 </mn>
                    </mrow>
                    <mrow>
                      <mn> 2 </mn>
                    </mrow>
                  </mfrac>
                </mtd>
              </mtr>
            </mtable>
          </mstyle>
        </math>
    '''
    tree = mml2tree(mml)
    assert tree is not None
    assert tree.getroot() is not None
    root = tree.getroot()
    assert root.tag == 'math'
