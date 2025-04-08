import copy
import re
from functools import lru_cache


# Pre-defined transitions for the 4 given nodes.
# Format: node: { two-bit input : (destination, output) }
DEFINED_TRANSITIONS = {
    'S0': {'01': ('S1', '1'), '11': ('S1', '0'), '10': ('S2', '0')},
    'S1': {'01': ('S3', '1')},
    'S2': {'00': ('S3', '1'), '11': ('S1', '0'), '10': ('S3', '0')},
    'S3': {'01': ('S0', '1')}
}
# The initial available nodes.
INITIAL_NODES = set(DEFINED_TRANSITIONS.keys())


def solve(binary_string):
    # First, split the binary string into triplets.
    if len(binary_string) % 3 != 0:
        raise ValueError("Input length must be a multiple of 3")
    n = len(binary_string) // 3
    # Each step: (inp, req_out)
    steps = [(binary_string[3 * i:3 * i + 2], binary_string[3 * i + 2]) for i in range(n)]

    # We will use DFS with memoization.
    # The state is defined by:
    #   - index i (which step we are at),
    #   - current node,
    #   - a frozenset representing extra_transitions added so far (mapping (node, inp) -> (dest, req_out)),
    #   - new_node_count: how many new nodes have been created so far.
    # In our recursion, we also build the "path" which is a list of transitions.
    #
    # Each transition in the path is represented as a tuple:
    # (current_node, input, required_output, destination, extra, new_node)
    # where extra is True if an extra transition was created at that step,
    # and new_node is True if that extra transition used a newly created node.

    @lru_cache(maxsize=None)
    def dfs(i, current_node, extra_transitions_state, new_node_count):
        """
        Returns a tuple (cost, path, extra_transitions, new_node_count_final)
        where:
          - cost is the extra cost from step i onward.
          - path is the list of transitions taken (each as a tuple).
          - extra_transitions is a dict mapping (node, inp) -> (dest, req_out)
            representing all extra transitions added so far.
          - new_node_count_final is the total new nodes count at the end.
        The extra cost includes 1 for each extra transition added plus 1 for each new node created.
        extra_transitions_state is a frozenset version of the extra_transitions dictionary.
        """
        # Recover extra_transitions as a normal dict.
        extra_transitions = dict(extra_transitions_state)

        # Base case: if we have processed all steps, return 0 cost and empty path.
        if i == len(steps):
            return 0, [], extra_transitions, new_node_count

        inp, req_out = steps[i]
        best = None  # will store (total_cost, path, extra_transitions, new_node_count_final)

        # First, try to use a pre-defined transition (if available)
        if current_node in DEFINED_TRANSITIONS and inp in DEFINED_TRANSITIONS[current_node]:
            dest, out = DEFINED_TRANSITIONS[current_node][inp]
            if out == req_out:
                res = dfs(i + 1, dest, frozenset(extra_transitions.items()), new_node_count)
                if res is not None:
                    cost_next, path_next, et_next, new_node_final = res
                    candidate = (
                        cost_next, [(current_node, inp, req_out, dest, False, False)] + path_next, et_next,
                        new_node_final)
                    best = candidate if best is None or candidate[0] < best[0] else best

        # Next, try to use an extra transition if it was already added.
        if (current_node, inp) in extra_transitions:
            dest, stored_out = extra_transitions[(current_node, inp)]
            if stored_out == req_out:
                res = dfs(i + 1, dest, frozenset(extra_transitions.items()), new_node_count)
                if res is not None:
                    cost_next, path_next, et_next, new_node_final = res
                    candidate = (
                        cost_next, [(current_node, inp, req_out, dest, False, False)] + path_next, et_next,
                        new_node_final)
                    best = candidate if best is None or candidate[0] < best[0] else best

        # If no valid transition exists, we need to add an extra transition.
        if (current_node not in DEFINED_TRANSITIONS or inp not in DEFINED_TRANSITIONS[current_node]) and (
                current_node, inp) not in extra_transitions:
            # Compute the available nodes (those already existing are the initial ones and any node that has been
            # created).
            available_nodes = set(INITIAL_NODES)
            # Add any destination nodes from the extra transitions (they might be new nodes)
            for (_, _), (dest, _) in extra_transitions.items():
                available_nodes.add(dest)

            # Option 1: use one of the available nodes (without creating a new one)
            for dest in available_nodes:
                # Add extra transition from current_node on inp to dest with required output req_out.
                new_extra = copy.copy(extra_transitions)
                new_extra[(current_node, inp)] = (dest, req_out)
                # This extra transition costs 1 extra path.
                res = dfs(i + 1, dest, frozenset(new_extra.items()), new_node_count)
                if res is not None:
                    cost_next, path_next, et_next, new_node_final = res
                    candidate = (1 + cost_next, [(current_node, inp, req_out, dest, True, False)] + path_next, et_next,
                                 new_node_final)
                    best = candidate if best is None or candidate[0] < best[0] else best

            # Option 2: create a new node.
            new_node_label = "N" + str(new_node_count + 1)
            new_extra = copy.copy(extra_transitions)
            new_extra[(current_node, inp)] = (new_node_label, req_out)
            res = dfs(i + 1, new_node_label, frozenset(new_extra.items()), new_node_count + 1)
            if res is not None:
                cost_next, path_next, et_next, new_node_final = res
                candidate = (
                    1 + 1 + cost_next, [(current_node, inp, req_out, new_node_label, True, True)] + path_next, et_next,
                    new_node_final)
                best = candidate if best is None or candidate[0] < best[0] else best

        return best

    # We can choose any starting node among the initial ones without extra cost.
    best_overall = None
    for start in INITIAL_NODES:
        res = dfs(0, start, frozenset({}), 0)
        if res is not None:
            cost, path, et, new_node_final = res
            if best_overall is None or cost < best_overall[0]:
                best_overall = (cost, path, et, new_node_final, start)

    if best_overall is None:
        print("No valid path found.")
        return

    total_extra_cost, best_path, extra_transitions_used, total_new_nodes, start_node = best_overall

    # Compute extra_path count as the number of extra transitions added (the ones marked extra=True).
    extra_path_count = sum(1 for step in best_path if step[4] is True)

    # Print the results.
    print("Extra Cost =", total_extra_cost)
    print("Extra Path =", extra_path_count)
    print("Extra Node =", total_new_nodes)
    print("Path:")
    # current = start_node
    for (frm, inp, outp, dest, is_extra, is_new) in best_path:
        transition_type = ""
        if is_extra:
            transition_type = " (extra"
            if is_new:
                transition_type += ", new node)"
            else:
                transition_type += ")"
        print(f"{frm} --({inp}/{outp})--> {dest}{transition_type}")


# Example usage:
if __name__ == "__main__":
    # Test with an example binary string.
    # For example, let's say the binary string is "010110" which represents two transitions:
    # first two bits "01" input with output "0", then "11" input with output "0".
    # (You can replace this with any binary string of length a multiple of 3.)
    test_strs = [
        "001_010_010_101_100_001_110_110",
        "111_010_000_100_110_101_110_000",
    ]

    for i, test_str in enumerate(test_strs):
        print('-' * 30)
        print(f"Testing case {i+1}:\n{test_str}\n")
        solve(re.sub(r'[^01]', '', test_str))
        print('\n')
