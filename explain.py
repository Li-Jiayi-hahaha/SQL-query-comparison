# The explain.py contains the code for generating the explanation.
import difflib
import logging
import copy
import textwrap
import html


import matplotlib.pyplot as plt
import psycopg2
import networkx as nx
import sqlparse


def hierarchy_pos(
    G: nx.DiGraph, root: int = None, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5
) -> dict[int, tuple[float, float]]:
    # helper function to create a tree-like layout using BFS for the graph visualization
    def _hierarchy_pos(
        G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None
    ):
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(
                    G,
                    child,
                    width=dx,
                    vert_gap=vert_gap,
                    vert_loc=vert_loc - vert_gap,
                    xcenter=nextx,
                    pos=pos,
                    parent=root,
                )
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

def get_label(node: dict) -> str:
    ret = f"""{node["Node Type"]}\n"""
    raw_input_relations = node["Input Relations"]
    better_input_relations = ""
    if node["Category"] == "Join":
        # give a better format to the input relations of join
        better_input_relations = (
            str(raw_input_relations)
            .replace(", ", " X ")
            .replace("(", "")
            .replace(")", "")
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
            .replace("{", "(")
            .replace("}", ")")
        ) + '\n'
    ret += better_input_relations
    for attri in useful_attributes:
        if attri == "Node Type":
            continue
        if node[attri] != "None":
            ret += f"""{attri}:\n{textwrap.fill(str(node[attri]), 25)}\n"""
    return ret

# tree visualization
def draw_tree(tree1: nx.DiGraph, tree2: nx.DiGraph) -> None:
    # draw the tree and save it to a png
    tree1_copy = copy.deepcopy(tree1)
    tree2_copy = copy.deepcopy(tree2)
    # assume all of the nodes are different and red
    color_maps = [["red"] * len(tree1_copy.nodes), ["red"] * len(tree2_copy.nodes)]
    for node_id1, node_data1 in tree1_copy.nodes.data():
        for node_id2, node_data2 in tree2_copy.nodes.data():
            if node_data1 == node_data2:
                # set the same node to green
                color_maps[0][node_id1] = "green"
                color_maps[1][node_id2] = "green"
    # draw the trees one by one
    for n, tree in enumerate([tree1_copy, tree2_copy]):
        labels = {}
        for node_id in range(max(tree.nodes) + 1):
            node_data = tree.nodes[node_id]
            labels[node_id] = get_label(node_data)
        pos = hierarchy_pos(tree, 0)
        max_depth = nx.dag_longest_path_length(tree, 0)
        max_width = 0
        for layer in nx.bfs_layers(tree, 0):
            if len(layer) > max_width:
                max_width = len(layer)
        # convert it to a undirected graph as we don't need to draw the direction of the edges
        tree = nx.Graph(tree)
        fig = plt.figure(figsize=(max_width * 2, max_depth * 1.5))        
        fig.tight_layout()
        nx.draw_networkx(
            tree,
            pos=pos,
            node_shape="o",
            node_size=200,
            node_color=color_maps[n],
            linewidths=2,
            with_labels=False,
        )
        nx.draw_networkx_labels(tree, pos=pos, labels=labels, font_size=3, font_color="#663300")
        # save the figure given the filename
        plt.axis("off")
        plt.savefig(f"tree{n+1}.png", dpi=500)
        plt.clf()


# Database connection
class DatabaseManager(object):
    """class that handles the interaction between python code and PostgreSQL"""

    def __init__(self, host: str, port: str, database: str, user: str, password: str):
        super(DatabaseManager, self).__init__()
        self.conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port,
        )
        self.cur = self.conn.cursor()
        logging.info("DBMS connection successful")

    # query the database
    def query(self, query: str) -> dict:
        logging.info(f"querying")
        self.cur.execute(query)
        logging.info("query successful")
        res = self.cur.fetchall()
        return res[0][0][0]


# we filter out the all not useful attribute in the plan such as Startup Cost, Total Cost, etc.
useful_attributes = [
    "Node Type",
    "Relation Name",
    "Group Key",
    "Sort Key",
    "Sort Method",
    "Join Type",
    "Index Name",
    "Index Cond",
    "Hash Cond",
    "Filter",
    "Merge Cond",
    "Recheck Cond",
    "Join Filter",
    "Partial Mode",
]


# get the categories of a node
def get_category(node_type: str) -> str:
    scan_type = [
        "Seq Scan",
        "Index Scan",
        "Bitmap Heap Scan",
        "Bitmap Index Scan",
        "Index Only Scan",
    ]
    join_type = ["Nested Loop", "Merge Join", "Hash Join"]

    if node_type in scan_type or "Scan" in node_type:
        return "Scan"
    if node_type in join_type or "Join" in node_type:
        return "Join"

    return "Other"


# get the node from the plan
def get_node(plan: dict) -> dict:
    # return a dictionary with only the useful attributes
    node = {}
    for key in useful_attributes:
        node[key] = "None"
    for key in plan.keys():
        if key in useful_attributes:
            node[key] = plan[key]
    # output relations, order is not considered
    node["Output Relations"] = set()
    # input relations, order is considered for join and aggregate
    node["Input Relations"] = []
    node["Category"] = get_category(node["Node Type"])
    return node


# node from [0, global_node_cnt)
global_node_cnt = 0


# build tree given a QEP plan
def get_tree(json_obj: dict) -> nx.DiGraph:
    global global_node_cnt
    global_node_cnt = 0
    my_tree = nx.DiGraph()
    _get_tree(json_obj["Plan"], my_tree)
    return my_tree


# helper function for get_tree
def _get_tree(cur_plan: dict, my_tree: nx.DiGraph) -> int:
    global global_node_cnt
    # parse current node
    cur_id = global_node_cnt
    global_node_cnt += 1
    cur_node = get_node(cur_plan)  # new node and its ID
    my_tree.add_node(cur_id, **cur_node)  # add to tree

    if not "Plans" in cur_plan:  # return if it's a leaf
        if cur_node["Relation Name"] != "None":  # the leaf might be
            cur_node["Input Relations"].append({cur_node["Relation Name"]})
            cur_node["Output Relations"].add(cur_node["Relation Name"])
        return cur_id

    # get all its children and parse them
    for sub_node in cur_plan["Plans"]:
        child_id = _get_tree(sub_node, my_tree)
        child_output = my_tree.nodes[child_id]["Output Relations"]
        if len(child_output) != 0:
            cur_node["Input Relations"].append(child_output)
            cur_node["Output Relations"].update(
                my_tree.nodes[child_id]["Output Relations"]
            )
        my_tree.add_edge(cur_id, child_id)

    # if the node is not leaf but its child doesn't have any relation (e.g. bitmap index scan)
    if len(cur_node["Input Relations"]) == 0 and "Relation Name" in cur_node.keys():
        cur_node["Input Relations"].append({cur_node["Relation Name"]})
        cur_node["Output Relations"].add(cur_node["Relation Name"])
    return cur_id


# explain the tree
def explain_tree(tree: nx.DiGraph) -> str:
    temp = _explain_tree(tree, 0)
    ret = ""
    for n, output in enumerate(temp):
        ret += f"{n}. {output}\n"
    return ret


def explain_node(node: dict) -> str:
    ret = f"""PERFORM {node["Node Type"]} AND OUTPUTS: {node["Output Relations"]}"""
    first = True
    for attri in useful_attributes:
        if attri == "Node Type" or attri == "Relation Name":
            continue
        if node[attri] != "None":
            if first:
                ret += f""" WITH:\n"""
                first = False
            ret += f"""    {attri}: {node[attri]}\n"""
    return ret


# helper function for explain_tree
def _explain_tree(tree: nx.DiGraph, cur: int) -> list:
    # post order traversal
    ret = []
    ret.append(explain_node(tree.nodes[cur]))
    for child in list(tree.neighbors(cur)):
        ret.extend(_explain_tree(tree, child))
    return ret


# get the same pattern in two trees
def get_same_pattern(tree1: nx.DiGraph, tree2: nx.DiGraph) -> None:
    # find the same nodes in two trees, and give the same pattern_id to all the nodes in the these subtree
    pattern_id = 0
    for node_id1, node1 in tree1.nodes.data():
        if "pattern_id" in node1.keys():
            # we have already found the pattern for this subtree, so we can skip it
            continue
        for node_id2, node2 in tree2.nodes.data():
            if "pattern_id" in node2.keys():
                # we have already found the pattern for this subtree, so we can skip it
                continue
            if node1 == node2:
                # inplace update
                tree1.nodes[node_id1]["pattern_id"] = pattern_id
                tree2.nodes[node_id2]["pattern_id"] = pattern_id
                pattern_id += 1


# get the difference nodes in two trees
def get_diff_nodes(tree: nx.DiGraph) -> list[dict]:
    diff_nodes = []
    for _, node in tree.nodes.data():
        if "pattern_id" not in node.keys():
            diff_nodes.append(node)
    return diff_nodes


# get the join difference between two trees
def get_join_difference(a: list, b: list):
    # input nodes differnce are one or more of the following:
    # 1. node type
    # 2. output relations difference
    # 3. input relations difference
    join_diff = []
    # match those with same output relations
    done = False
    join_diff.append(
        f"""\
Matched join difference:\
"""
    )
    cnt = 0
    while not done:
        done = True
        remove_a = []
        remove_b = []
        cur_diff = ""
        for a_id, node_a in enumerate(a):
            for b_id, node_b in enumerate(b):
                # match those with same output relations
                if node_a["Output Relations"] != node_b["Output Relations"]:
                    continue
                cnt += 1
                cur_diff = f"""
    Matched join diff {cnt}:\
"""
                done = False
                remove_a.append(a_id)
                remove_b.append(b_id)
                for attributes in useful_attributes:
                    if (
                        attributes == "Input Relations"
                        or attributes == "Output Relations"
                    ):
                        continue
                    if (
                        attributes in node_a.keys()
                        and attributes in node_b.keys()
                        and node_a[attributes] != node_b[attributes]
                    ):
                        cur_diff += f"""
        {attributes} difference:
            QEP1: {node_a[attributes]}
            QEP2: {node_b[attributes]}
"""
                node_a_left = node_a["Input Relations"][0]
                node_a_right = node_a["Input Relations"][1]
                node_b_left = node_b["Input Relations"][0]
                node_b_right = node_b["Input Relations"][1]

                node_a_input_alphabetical_order = sorted(
                    [sorted(list(s)) for s in node_a["Input Relations"]]
                )
                node_b_input_alphabetical_order = sorted(
                    [sorted(list(s)) for s in node_b["Input Relations"]]
                )

                if node_a_input_alphabetical_order == node_b_input_alphabetical_order:
                    cur_diff += f"""
        join ORDER difference:
            QEP1: {node_a["Node Type"]}: {node_a_left} X {node_a_right}
            QEP2: {node_b["Node Type"]}: {node_b_left} X {node_b_right}
"""
                else:
                    cur_diff += f"""
        join RELATION difference:
            QEP1: {node_a["Node Type"]}: {node_a_left} X {node_a_right}
            QEP2: {node_b["Node Type"]}: {node_b_left} X {node_b_right}
"""
                join_diff.append(cur_diff)
        # remove the matched nodes
        for i in sorted(remove_a, reverse=True):
            a.pop(i)
        for i in sorted(remove_b, reverse=True):
            b.pop(i)
    # out of while
    if cnt == 0:
        cur_diff += """\
    None
"""
        join_diff.append(cur_diff)
    # for unmatched nodes
    cur_diff = f"""\
Unmatched join difference:\
"""
    qep1 = """
    QEP1:
"""
    if len(a):
        for i, node_a in enumerate(a):
            node_a_left = node_a["Input Relations"][0]
            node_a_right = node_a["Input Relations"][1]
            qep1 += f"""\
        {i + 1}. {node_a["Node Type"]} ON {node_a_left} X {node_a_right}\
"""
    else:
        qep1 += """
        None
"""

    qep2 = """
    QEP2:
"""
    if len(b):
        for i, node_b in enumerate(b):
            node_b_left = node_b["Input Relations"][0]
            node_b_right = node_b["Input Relations"][1]
            qep2 += f"""\
        {i + 1}. {node_b["Node Type"]} ON {node_b_left} X {node_b_right}
"""
    else:
        qep2 += """\
        None
"""

    cur_diff += qep1
    cur_diff += qep2
    join_diff.append(cur_diff)
    return join_diff


# get the scan difference between two trees
def get_scan_difference(a: list, b: list) -> list[str]:
    scan_diff = []
    # match those with same output relations
    done = False
    scan_diff.append(
        f"""\
Matched scan difference:\
"""
    )
    cnt = 0
    while not done:
        done = True
        remove_a = []
        remove_b = []
        cur_diff = ""
        for a_id, node_a in enumerate(a):
            for b_id, node_b in enumerate(b):
                # match those with same output relations
                if node_a["Output Relations"] != node_b["Output Relations"]:
                    continue
                cnt += 1
                cur_diff = f"""
    Matched scan diff {cnt}:\
"""
                done = False
                remove_a.append(a_id)
                remove_b.append(b_id)
                # for scan node with same output, only node type is different
                cur_diff += f"""
        On relation: {node_a["Output Relations"]}\
"""
                for attributes in useful_attributes:
                    if (
                        attributes == "Input Relations"
                        or attributes == "Output Relations"
                    ):
                        continue
                    if (
                        attributes in node_a.keys()
                        and attributes in node_b.keys()
                        and node_a[attributes] != node_b[attributes]
                    ):
                        cur_diff += f"""
            {attributes} difference:
                QEP1: {node_a[attributes]}
                QEP2: {node_b[attributes]}
"""
                scan_diff.append(cur_diff)
        # remove the matched nodes
        for i in sorted(remove_a, reverse=True):
            a.pop(i)
        for i in sorted(remove_b, reverse=True):
            b.pop(i)
    # out of while
    if cnt == 0:
        cur_diff += """\
    None
"""
        scan_diff.append(cur_diff)
    # for unmatched nodes
    cur_diff = f"""\
Unmatched scan difference:
"""
    qep1 = """\
    QEP1:
"""
    if len(a):
        for i, node_a in enumerate(a):
            qep1 += f"""\
        {i + 1}. {node_a["Node Type"]} ON {node_a["Output Relations"]}
"""
    else:
        qep1 += """\
        None
"""

    qep2 = """\
    QEP2:
"""
    if len(b):
        for i, node_b in enumerate(b):
            qep2 += f"""\
        {i + 1}. {node_b["Node Type"]} ON {node_b["Output Relations"]}
"""
    else:
        qep2 += """\
        None
"""

    cur_diff += qep1
    cur_diff += qep2
    scan_diff.append(cur_diff)

    return scan_diff


# get the difference of other nodes
def get_other_difference(a: list, b: list):
    other_diff = []
    # match those with same output relations
    done = False
    other_diff.append(
        f"""\
Matched other difference:\
"""
    )
    cnt = 0
    while not done:
        done = True
        remove_a = []
        remove_b = []
        cur_diff = ""
        for a_id, node_a in enumerate(a):
            for b_id, node_b in enumerate(b):
                # match those with same output relations
                if (
                    node_a["Output Relations"] != node_b["Output Relations"]
                    or node_a["Node Type"] != node_b["Node Type"]
                ):
                    continue

                cnt += 1
                done = False
                remove_a.append(a_id)
                remove_b.append(b_id)
                # for scan node with same output, only node type is different
                cur_diff = f"""
    Matched other diff {cnt} of {node_a["Node Type"]} on relation {node_a["Output Relations"]}:\
"""
                for attributes in useful_attributes:
                    if (
                        attributes == "Input Relations"
                        or attributes == "Output Relations"
                    ):
                        continue
                    if (
                        attributes in node_a.keys()
                        and attributes in node_b.keys()
                        and node_a[attributes] != node_b[attributes]
                    ):
                        cur_diff += f"""
        {attributes} difference:
            QEP1: {node_a[attributes]}
            QEP2: {node_b[attributes]}
"""
                other_diff.append(cur_diff)
        # remove the matched nodes
        for i in sorted(remove_a, reverse=True):
            a.pop(i)
        for i in sorted(remove_b, reverse=True):
            b.pop(i)
    # out of while
    if cnt == 0:
        cur_diff += """\
    None\n"""
        other_diff.append(cur_diff)
    # for unmatched nodes
    cur_diff = f"""\
Unmatched other difference:
"""
    qep1 = """\
    QEP1:
"""
    if len(a):
        for i, node_a in enumerate(a):
            qep1 += f"""\
    {i + 1}. {node_a["Node Type"]} ON {node_a["Output Relations"]}
"""
    else:
        qep1 += """\
        None
"""

    qep2 = """\
    QEP2:
"""
    if len(b):
        for i, node_b in enumerate(b):
            qep2 += f"""\
        {i + 1}. {node_b["Node Type"]} ON {node_b["Output Relations"]}
"""
    else:
        qep2 += f"""\
        None
"""

    cur_diff += qep1
    cur_diff += qep2
    other_diff.append(cur_diff)

    return other_diff


# get the difference of join nodes
def get_tree_difference(diff_a: dict, diff_b: dict):
    a_diff_in_category = {"Scan": [], "Join": [], "Other": []}
    b_diff_in_category = {"Scan": [], "Join": [], "Other": []}

    for node_a in diff_a:
        if node_a["Category"] == "Scan":
            a_diff_in_category["Scan"].append(node_a)
        elif node_a["Category"] == "Join":
            a_diff_in_category["Join"].append(node_a)
        else:
            a_diff_in_category["Other"].append(node_a)

    for node_b in diff_b:
        if node_b["Category"] == "Scan":
            b_diff_in_category["Scan"].append(node_b)
        elif node_b["Category"] == "Join":
            b_diff_in_category["Join"].append(node_b)
        else:
            b_diff_in_category["Other"].append(node_b)

    join_diff = get_join_difference(
        a_diff_in_category["Join"], b_diff_in_category["Join"]
    )
    scan_diff = get_scan_difference(
        a_diff_in_category["Scan"], b_diff_in_category["Scan"]
    )
    other_diff = get_other_difference(
        a_diff_in_category["Other"], b_diff_in_category["Other"]
    )
    return "-------------------------------------------------------\n".join(
        ["".join(join_diff), "".join(scan_diff), "".join(other_diff)]
    )


# get the difference of two trees
def get_qep_difference(tree1: nx.DiGraph, tree2: nx.DiGraph) -> tuple[str]:
    get_same_pattern(tree1, tree2)
    diff_a = get_diff_nodes(tree1)
    diff_b = get_diff_nodes(tree2)
    return get_tree_difference(diff_a, diff_b)


# get the difference of two queries
def get_query_difference(query1: str, query2: str) -> tuple[str]:
    # Convert the parsed SQL queries into a string representation
    query1 = query1.strip()
    query2 = query2.strip()
    formatted_sql1 = sqlparse.format(
        query1,
        reindent=True,
        indent_width=4,
        keyword_case="upper",
        identifier_case="lower",
    )
    formatted_sql2 = sqlparse.format(
        query2,
        reindent=True,
        indent_width=4,
        keyword_case="upper",
        identifier_case="lower",
    )
    # Get the difference between the two SQL queries
    diff = difflib.ndiff(formatted_sql1.splitlines(), formatted_sql2.splitlines())
    differences = []
    colors = []  # 0 = black, 1 = red, 2 green
    for line in diff:
        line = html.escape(line)
        if line.isspace():
            continue
        elif line.startswith("+"):
            differences.append(line)
            colors.append(1)
        elif line.startswith("-"):
            differences.append(line)
            colors.append(2)
        elif line[0] != "?":
            differences.append(line)
            colors.append(0)
    return formatted_sql1, formatted_sql2, differences, colors


# Controller class
class Control(object):
    """class that handles the interaction between GUI and DB_Manager"""

    def __init__(self, host: str, database: str, user: str, password: str, port: int):
        super(Control, self).__init__()
        self.db = DatabaseManager(host, database, user, password, port)

    def add_explain_analyze(self, query: str) -> str:
        # give a prefix to the query such that we can get the query plan from the DB
        return "EXPLAIN (ANALYZE true, FORMAT json) " + query

    def generate_differences(
        self, query1: str, query2: str, testing: int = None
    ) -> tuple[str]:
        # get the query plans
        plan1_json = self.db.query(self.add_explain_analyze(query1))
        plan2_json = self.db.query(self.add_explain_analyze(query2))
        tree1 = get_tree(plan1_json)
        tree2 = get_tree(plan2_json)
        # plot the trees
        if testing is not None:
            draw_tree(tree1, tree2, testing)
        else:
            draw_tree(tree1, tree2)
        # get tree explanations
        tree1_explanation = explain_tree(tree1)
        tree2_explanation = explain_tree(tree2)
        # get tree differences
        tree_diff_statement = get_qep_difference(tree1, tree2)
        # get query differences
        (
            formatted_q1,
            formatted_q2,
            query_diff_strs,
            query_diff_colors,
        ) = get_query_difference(query1, query2)
        logging.info("Finished")
        return (
            formatted_q1,
            formatted_q2,
            tree1_explanation,
            tree2_explanation,
            tree_diff_statement,
            query_diff_strs,
            query_diff_colors,
        )
