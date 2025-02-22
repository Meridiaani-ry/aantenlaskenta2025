import numpy as np

def opavote_output(
        fn: str,
        votes: list,
        n_candidates: int,
        n_chosen: int,
        candidates: list,
        election_name: str):
    """Writes an Opavote formatted output file.
    
    Example output:

    4 2
    1 1 2 3 4 0
    1 2 1 3 4 0
    1 1 2 3 4 0
    1 2 1 3 4 0
    0
    "Anna A."
    "Bruno B."
    "Charlie C."
    "Daniela D."
    "Election name"
    """
    with open(fn, 'w') as file:
        file.write(f'{n_candidates} {n_chosen}\n')
        for candidate_votes in votes:
            file.write(f'1 {" ".join(str(x) for x in candidate_votes)} 0\n')
        file.write('0\n')
        for candidate in candidates:
            file.write(f'"{candidate}"\n')
        file.write(f'"{election_name}"\n')

    return 0


