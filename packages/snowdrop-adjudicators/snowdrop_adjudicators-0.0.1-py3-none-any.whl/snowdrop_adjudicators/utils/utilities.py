""" a place to put utility functions """
import os
import pickle
import ast
import gzip
from pathlib import Path
import numpy as np

from snowdrop_adjudicators.adjudicators.adjudicator import GameState


def swap_ones_and_twos(input_list: list) -> list:
    """
    Given a list comprising 0, 1, 2, with exactly one 1 and one 2, swap the positions of 1 and 2
    For example, if the input is [0,0,1,0,0,0,2], the output is [0,0,2,0,0,0,1]

    Args:
        input_list (list): a list comprising 0, 1, 2, with exactly one 1 and one 2

    Returns:
        list: a new list with 1 and 2 swapped

    Raises:
        ValueError: if input doesn't meet the requirements
    """
    # Validation
    if not all(x in {0, 1, 2} for x in input_list):
        raise ValueError("List must contain only 0, 1, and 2")

    if input_list.count(1) != 1 or input_list.count(2) != 1:
        raise ValueError("List must contain exactly one 1 and exactly one 2")

    # Swap using list comprehension
    return [2 if x == 1 else 1 if x == 2 else x for x in input_list]


def load_lookup_table(data_dir: str | Path, graph_number: int, vertex_count: int) -> dict[str, np.float16]:
    """Load and augment adjudication lookup table from compressed pickle file.

    Loads the base lookup table and creates additional entries by swapping
    player positions (1 ↔ 2) in vertex states with negated scores for
    AlphaZero self-play training.

    Args:
        data_dir: Directory containing adjudication data files
        graph_number: Graph identifier for the lookup table file
        vertex_count: Number of vertices in the graph (for state parsing)

    Returns:
        Combined lookup table with original and player-swapped game states.
        Keys are string representations of game states, values are the score in np.float16

    Raises:
        RuntimeError: If the adjudication data file cannot be loaded
    """

    try:
        data_path = os.path.join(data_dir, "graph_" + str(graph_number) + "_adjudicated.pkl.gz")
        with gzip.open(data_path, 'rb') as f:
            lookup_table = pickle.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load adjudication data: {str(e)}")

    # For alphazero, there is the canonical board which is where the pieces actually are. As the agent is playing
    # against itself, there's also a concept of switching places of the pieces. However, these switched states are not
    # in the data file. We swap where the 1 and 2 are in the vertex spots and multiply score by -1.

    full_lookup_table = {}

    for k, v in lookup_table.items():
        key_list = ast.literal_eval(k)
        new_key = swap_ones_and_twos(key_list[:vertex_count]) + key_list[vertex_count:]
        full_lookup_table[str(new_key)] = -v

    full_lookup_table.update(lookup_table)

    return full_lookup_table


def extract_state_key_from_game_state(game_state: GameState) ->list[int]:
    """Extract state from a GameState object

    Args:
        game_state: GameState instance:
            - 'edges': List of edge tuples in lexical order where third element is edge state
            - 'num_nodes': Number of vertices in the graph
            - 'player1_node': Vertex owned by player 1
            - 'player2_node': Vertex owned by  player 2

    Returns:
        Combined vertex and edge state as a flat list where:
        - First num_nodes elements represent vertex states (0=empty, 1=player1, 2=player2)
        - Remaining elements represent edge states from the original edges list
    """
    # Extract edge states (third element from each edge tuple)
    edge_states = [edge[2] for edge in game_state['edges']]

    # Initialize vertex states
    vertex_states = [0] * game_state['num_nodes']

    # Player vertex states
    if game_state['player1_node'] != -1:
        vertex_states[game_state['player1_node']] = 1
    if game_state['player2_node'] != -1:
        vertex_states[game_state['player2_node']] = 2

    return vertex_states + edge_states


def convert_state_key_to_game_state(my_state: list[int] | str, number_of_vertices: int, list_of_edge_tuples: list[tuple[int, int]]) -> GameState:
    # my_state is like [1, 2, 0, 3, 2, 1] or '[1, 2, 0, 3, 2, 1]'

    # extract erik state from geordie state
    if isinstance(my_state, str):
        my_state = ast.literal_eval(my_state)

    my_vertices = my_state[:number_of_vertices]
    my_edges = my_state[number_of_vertices:]

    turn_count = 0

    try:
        player_1_vertex = my_vertices.index(1)
        turn_count += 1
    except ValueError:
        player_1_vertex = -1

    try:
        player_2_vertex = my_vertices.index(2)
        turn_count += 1
    except ValueError:
        player_2_vertex = -1

    turn_count += my_edges.count(1) + my_edges.count(2) + my_edges.count(3)

    # if turn_count is even, it's player 1 (red)'s turn
    current_player_idx = 1 if turn_count % 2 == 0 else 2

    edges = [(list_of_edge_tuples[k][0], list_of_edge_tuples[k][1], my_edges[k]) for k in range(len(my_edges))]

    game_state: GameState = {'num_nodes': number_of_vertices,
                             'edges': edges,
                             'player1_id': 'player1',
                             'player2_id': 'player2',
                             'turn_count': turn_count,
                             'current_player_index': current_player_idx,
                             'player1_node': player_1_vertex,
                             'player2_node': player_2_vertex}

    return game_state
