# Copyright 2018 The Cirq Developers
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

from datetime import timedelta
import pytest

import cirq
from cirq.value import Duration


def test_init():
    assert Duration().total_picos() == 0
    assert Duration(picos=513).total_picos() == 513
    assert Duration(picos=-5).total_picos() == -5
    assert Duration(nanos=211).total_picos() == 211000
    assert Duration(nanos=211, picos=1051).total_picos() == 212051

    assert isinstance(Duration(picos=1).total_picos(), int)
    assert isinstance(Duration(nanos=1).total_picos(), int)
    assert isinstance(Duration(picos=1.0).total_picos(), float)
    assert isinstance(Duration(nanos=1.0).total_picos(), float)


def test_init_timedelta():
    assert Duration.create(timedelta(microseconds=0)).total_picos() == 0
    assert Duration.create(
        timedelta(microseconds=513)).total_picos() == 513 * 10**6
    assert Duration.create(
        timedelta(microseconds=-5)).total_picos() == -5 * 10**6
    assert Duration.create(
        timedelta(microseconds=211)).total_picos() == 211 * 10**6

    assert Duration.create(timedelta(seconds=3)).total_picos() == 3 * 10**12
    assert Duration.create(timedelta(seconds=-5)).total_picos() == -5 * 10**12
    assert Duration.create(timedelta(seconds=3)).total_nanos() == 3 * 10**9
    assert Duration.create(timedelta(seconds=-5)).total_nanos() == -5 * 10**9


def test_total_nanoseconds():
    assert Duration().total_nanos() == 0
    assert Duration(picos=3000).total_nanos() == 3
    assert Duration(nanos=5).total_nanos() == 5


def test_eq():
    eq = cirq.testing.EqualsTester()
    eq.add_equality_group(Duration(), Duration(picos=0), Duration(nanos=0.0))
    eq.add_equality_group(Duration(picos=1000), Duration(nanos=1))
    eq.make_equality_group(lambda: Duration(picos=-1))


def test_cmp():
    ordered_groups = [
        Duration(picos=-1),
        Duration(),
        Duration(picos=1),
        Duration(nanos=1),
        Duration(picos=2000),
    ]

    for i in range(len(ordered_groups)):
        for j in range(len(ordered_groups)):
            a = ordered_groups[i]
            b = ordered_groups[j]
            assert (i < j) == (a < b)
            assert (i <= j) == (a <= b)
            assert (i == j) == (a == b)
            assert (i != j) == (a != b)
            assert (i >= j) == (a >= b)
            assert (i > j) == (a > b)

    assert not (Duration() == 0)
    assert (Duration() != 0)


def test_cmp_vs_other_type():
    with pytest.raises(TypeError):
        _ = Duration() < 0
    with pytest.raises(TypeError):
        _ = Duration() <= 0
    with pytest.raises(TypeError):
        _ = Duration() >= 0
    with pytest.raises(TypeError):
        _ = Duration() > 0


def test_add():
    assert Duration() + Duration() == Duration()
    assert Duration(picos=1) + Duration(picos=2) == Duration(picos=3)

    assert Duration(picos=1) + \
            timedelta(microseconds=2) == Duration(picos=2000001)
    assert timedelta(microseconds=1) + \
            Duration(picos=2) == Duration(picos=1000002)

    with pytest.raises(TypeError):
        _ = 1 + Duration()
    with pytest.raises(TypeError):
        _ = Duration() + 1


def test_sub():
    assert Duration() - Duration() == Duration()
    assert Duration(picos=1) - Duration(picos=2) == Duration(picos=-1)

    assert Duration(picos=1) - \
            timedelta(microseconds=2) == Duration(picos=-1999999)
    assert timedelta(microseconds=1) - \
            Duration(picos=2) == Duration(picos=999998)

    with pytest.raises(TypeError):
        _ = 1 - Duration()
    with pytest.raises(TypeError):
        _ = Duration() - 1


def test_mul():
    assert Duration(picos=2) * 3 == Duration(picos=6)
    assert 4 * Duration(picos=3) == Duration(picos=12)

    with pytest.raises(TypeError):
        _ = Duration() * Duration()


def test_div():
    assert Duration(picos=6) / 2 == Duration(picos=3)
    assert Duration(picos=6) / Duration(picos=2) == 3
    with pytest.raises(TypeError):
        _ = 4 / Duration(picos=3)


def test_json_dict():
    d = Duration(picos=6)
    assert d._json_dict_() == {'cirq_type': 'Duration', 'picos': 6}
