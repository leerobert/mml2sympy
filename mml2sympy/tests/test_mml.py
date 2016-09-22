from mml2sympy import mml2tree, tree2sympy, table2trees, modify, mml2sympy


def test_modify():
    modify_mml = '''
        <mtd>
          <mn> 2 </mn>
          <mi> x </mi>
          <mo> - </mo>
          <mn> 4 </mn>
          <mo> + </mo>
          <mn> 7 </mn>
        </mtd>
    '''
    modify_to_mml = '''
        <mtd>
          <madd>
            <mmul>
              <mn>2</mn>
              <mi>x</mi>
            </mmul>
            <mn>4</mn>
            <mn>7</mn>
          </madd>
        </mtd>
    '''
    tree = mml2tree(modify_mml)
    modified_tree = modify(tree)
    modify_tree = mml2tree(modify_to_mml)
    assert modify_tree.tag == modified_tree.tag
    assert hasattr(modified_tree, 'madd')
    assert hasattr(modified_tree.madd, 'mn')
    assert hasattr(modified_tree.madd, 'mmul')
    assert hasattr(modified_tree.madd.mmul, 'mi')

    modify_mml = '''
        <mtd>
          <mn> 2 </mn>
          <mi> x </mi>
          <mo> - </mo>
          <mn> 4 </mn>
          <mo> = </mo>
          <mn> 7 </mn>
        </mtd>
    '''
    modify_to_mml = '''
        <mtd>
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
        </mtd>
    '''
    tree = mml2tree(modify_mml)
    modified_tree = modify(tree)
    modify_tree = mml2tree(modify_to_mml)
    assert modify_tree.tag == modified_tree.tag
    assert hasattr(modified_tree, 'meq')
    assert modified_tree.meq.countchildren() == 2
    assert hasattr(modified_tree.meq, 'madd')
    assert hasattr(modified_tree.meq.madd, 'mmul')


def test_table2trees():
    mtable_mml = '''
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
    '''
    trees = table2trees(mml2tree(mtable_mml))
    assert isinstance(trees, list)
    assert len(trees) == 3
    assert len(trees[0].getchildren()) == 6
    assert len(trees[1].getchildren()) == 4
    assert len(trees[2].getchildren()) == 3


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
    tree = mml2tree(tree_mml)
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
    tree = mml2tree(tree_mml)
    sympy = tree2sympy(tree)
    assert sympy == "Mul(Add(Mul(Integer(2),Symbol('x'),),Integer(4),),Pow(Integer(7),Integer(-1)))"


def test_mml2tree():
    mml = '''
        <math xmlns="http://www.w3.org/1998/Math/MathML">
          <mstyle displaystyle="true">
            <mn> 2 </mn>
            <mi> x </mi>
            <mo> - </mo>
            <mn> 4 </mn>
            <mo> = </mo>
            <mn> 7 </mn>
          </mstyle>
        </math>
    '''
    tree = mml2tree(mml)
    assert tree is not None
    assert tree.tag == 'math'
    assert hasattr(tree, 'mstyle')

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
    assert tree.tag == 'math'
    assert hasattr(tree, 'mstyle')
    assert hasattr(tree.mstyle, 'mtable')

    mstyle = tree.xpath('/math/mstyle')[0]
    assert mstyle is not None
    assert hasattr(mstyle, 'mtable')


def test_mml2sympy():
    mml = '''
        <math xmlns="http://www.w3.org/1998/Math/MathML">
          <mstyle displaystyle="true">
            <mn> 2 </mn>
            <mi> x </mi>
            <mo> - </mo>
            <mn> 4 </mn>
            <mo> = </mo>
            <mn> 7 </mn>
          </mstyle>
        </math>
    '''
    step_sympies = mml2sympy(mml)
    assert step_sympies is not None
    assert len(step_sympies) == 1
    assert step_sympies[0] == "Eq(Add(Mul(Integer(2),Symbol('x'),),Integer(4),),Integer(7))"

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
    step_sympies = mml2sympy(mml)
    assert step_sympies is not None
    assert len(step_sympies) == 3
    assert step_sympies[0] == "Eq(Add(Mul(Integer(2),Symbol('x'),),Integer(4),),Integer(7))"
