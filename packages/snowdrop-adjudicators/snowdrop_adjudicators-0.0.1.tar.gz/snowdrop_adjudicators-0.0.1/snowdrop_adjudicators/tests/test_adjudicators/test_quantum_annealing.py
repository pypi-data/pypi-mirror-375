import math

from snowdrop_adjudicators.adjudicators.quantum_annealing import QuantumAnnealingAdjudicator


class TestQuantumAnnealingAdjudicator:
    """Test suite for QuantumAnnealingAdjudicator"""

    def test_adjudicate(self, sample_game_states):
        """Test that lookup table loads correctly"""
        allowed_graphs, epsilon_values, game_states, correct_results, _, anneal_times = sample_game_states

        adjudication_result_from_quantum_annealing = {}
        for idx in range(len(allowed_graphs)):
            adj = QuantumAnnealingAdjudicator()
            kwargs = {'epsilon': epsilon_values[idx],
                      'anneal_time': anneal_times[idx],
                      'solver_name': 'Advantage2_system1.6',
                      'num_reads': 100000,
                      'graph_number': allowed_graphs[idx]}
            adj.setup(**kwargs)

            adjudication_result_from_quantum_annealing[allowed_graphs[idx]] = adj.adjudicate(game_states[allowed_graphs[idx]])

            # test if reading the correct score and winner
            assert math.isclose(adjudication_result_from_quantum_annealing[allowed_graphs[idx]]['score'],
                                correct_results[allowed_graphs[idx]][0], abs_tol=0.2)
            assert (adjudication_result_from_quantum_annealing[allowed_graphs[idx]]['winner'] ==
                    correct_results[allowed_graphs[idx]][1])
