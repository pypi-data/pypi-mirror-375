from xdoctest import doctest_example
from xdoctest import utils


def test_inline_skip_directive():
    """
    pytest tests/test_directive.py::test_inline_skip_directive
    """
    string = utils.codeblock(
        '''
        >>> x = 0
        >>> assert False, 'should be skipped'  # doctest: +SKIP
        >>> y = 0
        ''')
    self = doctest_example.DocTest(docsrc=string)
    result = self.run(on_error='raise')
    # TODO: ensure that lines after the inline are run
    assert result['passed']


def test_block_skip_directive():
    """
    pytest tests/test_directive.py::test_block_skip_directive
    """
    string = utils.codeblock(
        '''
        >>> x = 0
        >>> # doctest: +SKIP
        >>> assert False, 'should be skipped'
        ''')
    self = doctest_example.DocTest(docsrc=string)
    result = self.run(on_error='raise')
    assert result['passed']


def test_multi_requires_directive():
    """
    Test semi-complex case with multiple requirements in a single line

    xdoctest ~/code/xdoctest/tests/test_directive.py test_multi_requires_directive
    """
    string = utils.codeblock(
        '''
        >>> x = 0
        >>> print('not-skipped')
        >>> # doctest: +REQUIRES(env:NOT_EXIST, --show, module:xdoctest)
        >>> print('is-skipped')
        >>> assert False, 'should be skipped'
        >>> # doctest: -REQUIRES(env:NOT_EXIST, module:xdoctest)
        >>> print('is-skipped')
        >>> assert False, 'should be skipped'
        >>> # doctest: +REQUIRES(env:NOT_EXIST, --show, module:xdoctest)
        >>> print('is-skipped')
        >>> assert False, 'should be skipped'
        >>> # doctest: -REQUIRES(env:NOT_EXIST)
        >>> print('is-skipped')
        >>> assert False, 'should be skipped'
        >>> # doctest: -REQUIRES(--show)
        >>> print('not-skipped')
        >>> x = 'this will not be skipped'
        >>> # doctest: -REQUIRES(env:NOT_EXIST, --show, module:xdoctest)
        >>> print('not-skipped')
        >>> assert x == 'this will not be skipped'
        ''')
    self = doctest_example.DocTest(docsrc=string)
    result = self.run(on_error='raise')
    stdout = ''.join(list(self.logged_stdout.values()))
    assert result['passed']
    assert stdout.count('not-skipped') == 3
    assert stdout.count('is-skipped') == 0


def test_directive_syntax_error():
    string = utils.codeblock(
        '''
        >>> x = 0
        >>> # doctest: +REQUIRES(module:xdoctest)
        >>> print('not-skipped')
        >>> # doctest: +REQUIRES(badsyntax)
        >>> print('is-skipped')
        ''')
    self = doctest_example.DocTest(docsrc=string)
    result = self.run(on_error='return')
    assert not result['passed']
    assert 'Failed to parse' in result['exc_info'][1].args[0]
    assert 'line 4' in result['exc_info'][1].args[0]
    stdout = ''.join(list(self.logged_stdout.values()))
    assert stdout.count('not-skipped') == 1


if __name__ == '__main__':
    """
    CommandLine:
        python ~/code/xdoctest/tests/test_directive.py
        pytest ~/code/xdoctest/tests/test_directive.py
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
