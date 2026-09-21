from typing import List

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from schemas import Scenario


class QuantumOptimizer:

    def optimize(self, scenarios: List[Scenario]) -> List[Scenario]:

        if not scenarios:
            return []

        n = len(scenarios)

        # We need enough qubits to encode the scenario index.
        qubits = max(2, (n - 1).bit_length())

        circuit = QuantumCircuit(qubits, qubits)

        # Create an exploratory superposition.
        for q in range(qubits):
            circuit.h(q)

        circuit.measure(range(qubits), range(qubits))

        simulator = AerSimulator()

        compiled = transpile(circuit, simulator)

        result = simulator.run(
            compiled,
            shots=512
        ).result()

        counts = result.get_counts()

        # Use observed quantum state frequency as
        # an exploratory signal, not as a fake probability.
        ranked_states = sorted(
            counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        quantum_rank = []

        for state, count in ranked_states:

            index = int(state, 2)

            if index < n:
                quantum_rank.append(
                    (index, count)
                )

        # Preserve classical economic score while using
        # quantum exploration as a secondary signal.
        for index, count in quantum_rank:
            scenarios[index].objective_score += (
                0.02 * (count / 512)
            )

        return sorted(
            scenarios,
            key=lambda x: x.objective_score,
            reverse=True
        )