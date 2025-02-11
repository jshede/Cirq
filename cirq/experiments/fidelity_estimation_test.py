import itertools

from typing import Sequence

import numpy as np
import pytest

import cirq


def sample_noisy_bitstrings(circuit: cirq.Circuit,
                            qubit_order: Sequence[cirq.Qid],
                            depolarization: float,
                            repetitions: int) -> np.ndarray:
    assert 0 <= depolarization <= 1
    dim = np.product(circuit.qid_shape())
    n_incoherent = int(depolarization * repetitions)
    n_coherent = repetitions - n_incoherent
    incoherent_samples = np.random.randint(dim, size=n_incoherent)
    circuit_with_measurements = cirq.Circuit(
        circuit, cirq.measure(*qubit_order, key='m'))
    # TODO(viathor): Remove conditional after #2114.
    if n_coherent > 0:
        r = cirq.sample(circuit_with_measurements, repetitions=n_coherent)
        coherent_samples = r.data['m'].to_numpy()
        return np.concatenate((coherent_samples, incoherent_samples))
    return incoherent_samples


def make_random_quantum_circuit(qubits: Sequence[cirq.Qid],
                                depth: int) -> cirq.Circuit:
    SQ_GATES = [cirq.X**0.5, cirq.Y**0.5, cirq.T]
    circuit = cirq.Circuit()
    cz_start = 0
    for q in qubits:
        circuit.append(cirq.H(q))
    for _ in range(depth):
        for q in qubits:
            random_gate = SQ_GATES[np.random.randint(len(SQ_GATES))]
            circuit.append(random_gate(q))
        for q0, q1 in zip(itertools.islice(qubits, cz_start, None, 2),
                          itertools.islice(qubits, cz_start + 1, None, 2)):
            circuit.append(cirq.CNOT(q0, q1))
        cz_start = 1 - cz_start
    for q in qubits:
        circuit.append(cirq.H(q))
    return circuit


@pytest.mark.parametrize('depolarization', (0.0, 0.2, 0.5, 0.7, 1.0))
def test_linear_xeb_fidelity(depolarization):
    prng_state = np.random.get_state()
    np.random.seed(0)

    fs = []
    for _ in range(10):
        qubits = cirq.LineQubit.range(5)
        circuit = make_random_quantum_circuit(qubits, depth=12)
        bitstrings = sample_noisy_bitstrings(circuit,
                                             qubits,
                                             depolarization,
                                             repetitions=5000)
        f = cirq.linear_xeb_fidelity(circuit, bitstrings, qubits)
        fs.append(f)
    estimated_fidelity = np.mean(fs)
    expected_fidelity = 1 - depolarization
    assert np.isclose(estimated_fidelity, expected_fidelity, atol=0.09)

    np.random.set_state(prng_state)


def test_linear_xeb_fidelity_invalid_qubits():
    q0, q1, q2 = cirq.LineQubit.range(3)
    circuit = cirq.Circuit(cirq.H(q0), cirq.CNOT(q0, q1))
    bitstrings = sample_noisy_bitstrings(circuit, (q0, q1, q2), 0.9, 10)
    with pytest.raises(ValueError):
        cirq.linear_xeb_fidelity(circuit, bitstrings, (q0, q2))


def test_linear_xeb_fidelity_invalid_bitstrings():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(cirq.H(q0), cirq.CNOT(q0, q1))
    bitstrings = [0, 1, 2, 3, 4]
    with pytest.raises(ValueError):
        cirq.linear_xeb_fidelity(circuit, bitstrings, (q0, q1))


def test_linear_xeb_fidelity_tuple_input():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(cirq.H(q0), cirq.CNOT(q0, q1))
    bitstrings = [0, 1, 2]
    f1 = cirq.linear_xeb_fidelity(circuit, bitstrings, (q0, q1))
    f2 = cirq.linear_xeb_fidelity(circuit, tuple(bitstrings), (q0, q1))
    assert f1 == f2
