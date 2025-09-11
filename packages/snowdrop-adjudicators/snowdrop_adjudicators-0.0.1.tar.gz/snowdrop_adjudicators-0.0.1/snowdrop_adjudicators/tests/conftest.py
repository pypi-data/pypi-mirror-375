""" shared fixtures for tests """
import pytest


@pytest.fixture
def sample_game_states():
    """Provide sample terminal game states for testing"""

    allowed_graphs = [2, 11, 12, 18, 19, 20]

    epsilon_values = [0.5, 0.5, 0.05, 0.125, 0.25, 0.5]

    anneal_times = [350, 350, 40, 100, 350, 350]

    # Vertex ownership; index is graph_id, value is (red_vertex_index, blue_vertex_index)
    vertex_ownership: dict[int, tuple[int, int]] = {1: (0, 1),
                                                    2: (0, 1),
                                                    3: (0, 2),
                                                    4: (0, 3),
                                                    5: (5, 7),
                                                    6: (14, 10),
                                                    7: (1, 4),
                                                    8: (0, 11),
                                                    10: (0, 23),
                                                    11: (0, 2),
                                                    12: (2, 4),
                                                    13: (0, 1),
                                                    14: (7, 16),
                                                    15: (1, 4),
                                                    16: (136, 31),
                                                    17: (0, 7),
                                                    18: (0, 4),
                                                    19: (0, 4),
                                                    20: (0, 2),
                                                    21: (0, 2),
                                                    22: (0, 3),
                                                    23: (111, 889),
                                                    # N^2+N+1 should be first and last vertex with 6 connections
                                                    24: (0, 54)}

    # Correct answers
    correct_results: dict[int, tuple[float, str]] = {}
    simulated_annealing_results: dict[int, tuple[float, str]] = {}

    game_states = {}

    for graph_number in allowed_graphs:
        game_states[graph_number] = {'player1_node': vertex_ownership[graph_number][0],
                                     'player2_node': vertex_ownership[graph_number][1]}

        if graph_number == 2:   # K_3 graph, S = [3,3,3], score = 0 (draw)
            game_states[graph_number].update({'num_nodes': 3, 'edges': [(0, 1, 3), (0, 2, 3), (1, 2, 3)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 3,
                                              'current_player_index': 1})
            correct_results[graph_number] = (-0.038330078125, 'draw')
            simulated_annealing_results[graph_number] = (0.000558, 'draw')
        if graph_number == 11:  # P_3 graph, S = [2,3], score = +2 (red)
            game_states[graph_number].update({'num_nodes': 3, 'edges': [(0, 1, 2), (1, 2, 3)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 2,
                                              'current_player_index': 2})
            correct_results[graph_number] = (1.9990234375, 'red')
            simulated_annealing_results[graph_number] = (1.988, 'red')
        if graph_number == 12:  # moser spindle, S = [3, 3, 2, 2, 1, 2, 2, 3, 3, 2, 2], score = 0 (draw)
            game_states[graph_number].update({'num_nodes': 7, 'edges': [(0, 1, 3), (0, 4, 3), (0, 6, 2), (1, 2, 2),
                                                                        (1, 5, 1), (2, 3, 2), (2, 5, 2), (3, 4, 3),
                                                                        (3, 5, 3), (3, 6, 2), (4, 6, 2)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 11,
                                              'current_player_index': 1})
            correct_results[graph_number] = (0.0030517578125, 'draw')
            simulated_annealing_results[graph_number] = (0.62943, 'red')
        if graph_number == 18:  # 3-prism graph; 6 vertices, 9 edges, S = [3, 3, 1, 3, 3, 2, 2, 2, 3], score = -1 (blue)
            game_states[graph_number].update({'num_nodes': 6, 'edges': [(0, 1, 3), (0, 2, 3), (0, 3, 1), (1, 2, 3),
                                                                        (1, 4, 3), (2, 5, 2), (3, 4, 2), (3, 5, 2),
                                                                        (4, 5, 3)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 9,
                                              'current_player_index': 1})
            correct_results[graph_number] = (-0.9912109375, 'blue')
            simulated_annealing_results[graph_number] = (-0.975388, 'blue')
        if graph_number == 19:   # Barbell graph; S = [3,2,2,3,2,3,2]; SA scores -4/9 (blue), QA & SE scores +1/2 (red)
            game_states[graph_number].update({'num_nodes': 6, 'edges': [(0, 1, 3), (0, 2, 2), (1, 2, 2),
                                                                        (2, 5, 3), (3, 4, 2), (3, 5, 3),
                                                                        (4, 5, 2)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 7,
                                              'current_player_index': 1})
            correct_results[graph_number] = (0.379638671875, 'red')
            simulated_annealing_results[graph_number] = (-0.447884, 'blue')
        if graph_number == 20:  # Diamond graph; S = [1,2,2,2,3]; SA scores +4/3, QA & SE scores = +2 (red)
            game_states[graph_number].update({'num_nodes': 4, 'edges': [(0, 1, 1), (0, 3, 2),
                                                                        (1, 2, 2), (1, 3, 2), (2, 3, 3)],
                                              'player1_id': 'player1', 'player2_id': 'player2', 'turn_count': 6,
                                              'current_player_index': 2})
            correct_results[graph_number] = (1.9892578125, 'red')
            simulated_annealing_results[graph_number] = (1.325748, 'red')

    return allowed_graphs, epsilon_values, game_states, correct_results, simulated_annealing_results, anneal_times
