mml2sympy
========

A simple package for converting presentation math ML into sympy expressions.

Example
------

    >>> from mml2sympy import mml2sympy
    >>> mml = '''
    ...         <math xmlns="http://www.w3.org/1998/Math/MathML">
    ...           <mstyle displaystyle="true">
    ...             <mn> 2 </mn>
    ...             <mi> x </mi>
    ...             <mo> - </mo>
    ...             <mn> 4 </mn>
    ...             <mo> = </mo>
    ...             <mn> 7 </mn>
    ...           </mstyle>
    ...         </math>
    ...     '''
    >>> expression_strings = mml2sympy(mml)
    >>> expression_strings
    ["Eq(Add(Mul(Integer(2),Symbol('x'),),Integer(4),),Integer(7))"]

Supports
-------

Currently supports Add, Mul, Eq for sympy. Supports msup, mtable (one row support currently, no matrices, etc), mfrac, msqrt, mi, mn, mo.
