import json
import networkx as nx
import matplotlib.pyplot as plt


def load_tree(filename="family_tree.json"):
    """Load the JSON family tree and return a dict of people."""
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {p["id"]: p for p in data}


def build_marriage_graph(people):
    """
    Build a graph with 'marriage nodes' connecting couples and their children.
    """
    G = nx.DiGraph()

    # Add person nodes
    for p in people.values():
        label = f"{p['name']} ({p['gender']})"
        G.add_node(p["id"], label=label, type="person", generation=p["generation"])

    # Create marriage nodes (unique per couple)
    marriage_nodes = {}
    for person in people.values():
        parents = tuple(sorted(person["parents"]))
        if len(parents) == 2:
            if parents not in marriage_nodes:
                mid = f"marriage_{parents[0]}_{parents[1]}"
                marriage_nodes[parents] = mid
                # Add marriage node
                G.add_node(mid, label="💍", type="marriage", generation=people[parents[0]]["generation"])
                # Connect spouses to marriage node
                G.add_edge(parents[0], mid)
                G.add_edge(parents[1], mid)

            # Connect marriage node to children
            mid = marriage_nodes[parents]
            G.add_edge(mid, person["id"])

    return G


def compute_positions(G):
    """
    Compute smart positions:
    - People are aligned by generation (Y-axis).
    - Marriage nodes are placed between spouses (slightly below them).
    - Children are centered under their marriage node, with simple collision avoidance.
    - Spouses that share a marriage node are placed together (adjacent) to reduce edge crossings.
    """
    # Group by generation
    generations = {}
    for n, d in G.nodes(data=True):
        gen = d.get("generation", 0)
        generations.setdefault(gen, []).append(n)

    y_spacing = 2.0
    x_spacing = 2.0
    marriage_offset = y_spacing * 0.4  # desplazamiento hacia abajo para nodos de matrimonio
    min_sep = x_spacing * 0.9  # separación mínima para evitar solapamiento

    # Helper: find nearest free x (alternando izquierda/derecha)
    def find_free_x(desired, used, step):
        if not used:
            return desired
        if all(abs(desired - u) >= step for u in used):
            return desired
        for k in range(1, 50):
            for sign in (-1, 1):
                cand = desired + sign * k * step
                if all(abs(cand - u) >= step for u in used):
                    return cand
        return desired

    pos = {}
    # track used x positions per generation to avoid overlaps
    used_x = {gen: [] for gen in generations}

    sorted_gens = sorted(generations.keys())
    for gen in sorted_gens:
        nodes = generations[gen]
        # stable ordering
        persons = sorted([n for n in nodes if G.nodes[n]["type"] == "person"])
        marriages = sorted([n for n in nodes if G.nodes[n]["type"] == "marriage"])

        # 1) Place spouses together per marriage (if spouses are in this generation)
        spouses_placed = set()
        for m in marriages:
            parents = [p for p in G.predecessors(m) if G.nodes[p]["type"] == "person"]
            if len(parents) >= 2:
                a, b = parents[0], parents[1]
                # only handle if spouses belong to this generation
                if a in persons or b in persons:
                    # If both already placed, skip
                    if a in pos and b in pos:
                        spouses_placed.update([a, b])
                        # register their x positions to used_x if not already
                        for p in (a, b):
                            x = pos[p][0]
                            if all(abs(x - u) >= 1e-6 for u in used_x[gen]):
                                used_x[gen].append(x)
                        continue

                    # Determine base slot for the couple
                    base_x = len(used_x[gen]) * x_spacing
                    base_x = find_free_x(base_x, used_x[gen], min_sep)

                    # Small gap between spouses
                    spouse_gap = min_sep * 0.6
                    xa = base_x - spouse_gap / 2
                    xb = base_x + spouse_gap / 2

                    # If one spouse already placed, place the other adjacent
                    if a in pos:
                        xa = pos[a][0]
                        xb = find_free_x(xa + spouse_gap, used_x[gen], min_sep)
                    elif b in pos:
                        xb = pos[b][0]
                        xa = find_free_x(xb - spouse_gap, used_x[gen], min_sep)

                    pos[a] = (xa, -gen * y_spacing)
                    pos[b] = (xb, -gen * y_spacing)
                    used_x[gen].extend([xa, xb])
                    spouses_placed.update([a, b])

        # 2) Place remaining persons in this generation
        for n in persons:
            if n in spouses_placed:
                continue
            # If the person has a marriage node as parent (i.e., has parents), place relative to that marriage
            parents = [p for p in G.predecessors(n) if str(p).startswith("marriage_")]
            if parents:
                marriage_node = parents[0]
                marriage_x = pos.get(marriage_node, (0, 0))[0]
                children = [c for c in G.successors(marriage_node) if G.nodes[c]["type"] == "person"]
                if n in children:
                    index = children.index(n)
                else:
                    index = 0
                offset = (index - (len(children) - 1) / 2) * (x_spacing * 0.8)
                desired_x = marriage_x + offset
                desired_x = find_free_x(desired_x, used_x[gen], min_sep)
                pos[n] = (desired_x, -gen * y_spacing)
                used_x[gen].append(desired_x)
            else:
                # No parents and not part of a placed spouse pair: place sequentially
                desired_x = len(used_x[gen]) * x_spacing
                desired_x = find_free_x(desired_x, used_x[gen], min_sep)
                pos[n] = (desired_x, -gen * y_spacing)
                used_x[gen].append(desired_x)

        # 3) Place marriages (they depend on spouse positions within same generation)
        for n in marriages:
            parents = [p for p in G.predecessors(n) if G.nodes[p]["type"] == "person"]
            if len(parents) >= 2 and parents[0] in pos and parents[1] in pos:
                x1, x2 = pos[parents[0]][0], pos[parents[1]][0]
                if x1 > x2:
                    x1, x2 = x2, x1
                x_mid = (x1 - x2) / 2 + x2
                parent_y = pos[parents[0]][1]
                desired_x = find_free_x(x_mid, used_x[gen], min_sep)
                pos[n] = (desired_x, parent_y - marriage_offset)
                used_x[gen].append(desired_x)
            else:
                # Fallback: place in next available slot for this generation
                desired_x = len(used_x[gen]) * x_spacing
                desired_x = find_free_x(desired_x, used_x[gen], min_sep)
                pos[n] = (desired_x, -gen * y_spacing - marriage_offset)
                used_x[gen].append(desired_x)

    return pos


def draw_family_tree(G):
    """Draw the hierarchical family tree with centered marriages and children."""
    pos = compute_positions(G)
    plt.figure(figsize=(14, 8))

    # Node groups
    person_nodes = [n for n, d in G.nodes(data=True) if d["type"] == "person"]
    marriage_nodes = [n for n, d in G.nodes(data=True) if d["type"] == "marriage"]
    labels = nx.get_node_attributes(G, "label")

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, nodelist=person_nodes, node_color="#bbdefb",
                           node_size=2000, edgecolors="black", linewidths=1.0)
    nx.draw_networkx_nodes(G, pos, nodelist=marriage_nodes, node_color="#ffcc80",
                           node_shape="s", node_size=600, edgecolors="black", linewidths=1.0)

    # Draw labels
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight="bold")

    # Draw edges (no arrows)
    nx.draw_networkx_edges(G, pos, width=1.5, arrows=False)

    plt.title("Family Tree (Centered Marriages, Minimal Crossings)", fontsize=14, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def main():
    people = load_tree("family_tree.json")
    G = build_marriage_graph(people)
    draw_family_tree(G)


if __name__ == "__main__":
    main()
