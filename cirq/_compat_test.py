# Copyright 2019 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import ContextManager, List

import numpy as np
import sympy

from cirq._compat import proper_repr, deprecated, deprecated_parameter


def test_proper_repr():
    v = sympy.Symbol('t') * 3
    v2 = eval(proper_repr(v))
    assert v2 == v

    v = np.array([1, 2, 3], dtype=np.complex64)
    v2 = eval(proper_repr(v))
    np.testing.assert_array_equal(v2, v)
    assert v2.dtype == v.dtype


def test_deprecated():

    @deprecated(deadline='vNever', fix='Roll some dice.', func_name='test_func')
    def f(a, b):
        return a + b

    # Warns on first use.
    with capture_logging() as log:
        assert f(1, 2) == 3
    assert len(log) == 1
    assert 'function test_func was used' in log[0].getMessage()
    assert 'will be removed in cirq vNever' in log[0].getMessage()
    assert 'Roll some dice.' in log[0].getMessage()

    # Only warns once.
    with capture_logging() as log:
        assert f(1, 2) == 3
    assert len(log) == 0


def test_deprecated_parameter():

    @deprecated_parameter(
        deadline='vAlready',
        fix='Double it yourself.',
        func_name='test_func',
        parameter_desc='double_count',
        match=lambda args, kwargs: 'double_count' in kwargs,
        rewrite=lambda args, kwargs: (args, {
            'new_count': kwargs['double_count'] * 2
        }))
    def f(new_count):
        return new_count

    # Does not warn on usual use.
    with capture_logging() as log:
        assert f(1) == 1
        assert f(new_count=1) == 1
    assert len(log) == 0

    # Warns on first use.
    with capture_logging() as log:
        # pylint: disable=unexpected-keyword-arg
        # pylint: disable=no-value-for-parameter
        assert f(double_count=1) == 2
        # pylint: enable=no-value-for-parameter
        # pylint: enable=unexpected-keyword-arg
    assert len(log) == 1
    assert 'double_count parameter of test_func was used' in log[0].getMessage()
    assert 'will be removed in cirq vAlready' in log[0].getMessage()
    assert 'Double it yourself.' in log[0].getMessage()

    # Only warns once.
    with capture_logging() as log:
        # pylint: disable=unexpected-keyword-arg
        # pylint: disable=no-value-for-parameter
        assert f(double_count=1) == 2
        # pylint: enable=no-value-for-parameter
        # pylint: enable=unexpected-keyword-arg
    assert len(log) == 0


def capture_logging() -> ContextManager[List[logging.LogRecord]]:
    records = []

    class Handler(logging.Handler):

        def emit(self, record):
            records.append(record)

        def __enter__(self):
            logging.getLogger().addHandler(self)
            return records

        def __exit__(self, exc_type, exc_val, exc_tb):
            logging.getLogger().removeHandler(self)

    return Handler()
