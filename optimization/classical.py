from typing import List

from schemas import Scenario


class ClassicalOptimizer:

    def optimize(self, scenarios: List[Scenario]) -> List[Scenario]:

        for scenario in scenarios:

            scenario.objective_score = (
                0.35 * scenario.expected_margin
                + 0.30 * scenario.win_signal
                + 0.25 * scenario.strategic_value
                - 0.10 * scenario.risk
            )

        return sorted(
            scenarios,
            key=lambda x: x.objective_score,
            reverse=True
        )