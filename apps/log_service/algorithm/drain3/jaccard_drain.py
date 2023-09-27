from apps.log_service.algorithm.drain3.drain import DrainBase, LogCluster, Node


class JaccardDrain(DrainBase):
    """
    add a new matching pattern to the log cluster.
    Cancels log message length as  first token.
    Drain that uses Jaccard similarity to match log messages.
    """

    def tree_search(self, root_node: Node, tokens: list, sim_th: float, include_params: bool):
        token_count = len(tokens)

        if not tokens:
            token_first = ""
            cur_node = root_node.key_to_child_node.get(token_first)
        else:
            token_first = tokens[0]
            cur_node = root_node.key_to_child_node.get(token_first)

        if cur_node is None:
            return None

        if token_count == 0:
            return self.id_to_cluster.get(cur_node.cluster_ids[0])

        cur_node_depth = 1  # first level is 1 <root>

        for token in tokens[1:]:
            # at max depth
            if cur_node_depth >= self.max_node_depth:
                break

            if cur_node_depth == token_count - 1:
                break

            key_to_child_node = cur_node.key_to_child_node
            cur_node = key_to_child_node.get(token)

            if cur_node is None:  # no exact next token exist, try wildcard node
                cur_node = key_to_child_node.get(self.param_str)
            if cur_node is None:  # no wildcard node exist
                return None

            cur_node_depth += 1

        cluster = self.fast_match(cur_node.cluster_ids, tokens, sim_th, include_params)

        return cluster

    def add_seq_to_prefix_tree(self, root_node, cluster: LogCluster):
        token_count = len(cluster.log_template_tokens)
        if not cluster.log_template_tokens:
            token_first = ""
        else:
            token_first = cluster.log_template_tokens[0]
        if token_first not in root_node.key_to_child_node:
            first_layer_node = Node()
            root_node.key_to_child_node[token_first] = first_layer_node
        else:
            first_layer_node = root_node.key_to_child_node[token_first]

        cur_node = first_layer_node

        if token_count == 0:
            cur_node.cluster_ids = [cluster.cluster_id]
            return

        if token_count == 1:
            new_cluster_ids = []
            for cluster_id in cur_node.cluster_ids:
                if cluster_id in self.id_to_cluster:
                    new_cluster_ids.append(cluster_id)
            new_cluster_ids.append(cluster.cluster_id)
            cur_node.cluster_ids = new_cluster_ids

        current_depth = 1
        for token in cluster.log_template_tokens[1:]:
            if current_depth >= self.max_node_depth or current_depth >= token_count - 1:
                new_cluster_ids = []
                for cluster_id in cur_node.cluster_ids:
                    if cluster_id in self.id_to_cluster:
                        new_cluster_ids.append(cluster_id)
                new_cluster_ids.append(cluster.cluster_id)
                cur_node.cluster_ids = new_cluster_ids
                break

            if token not in cur_node.key_to_child_node:
                if self.parametrize_numeric_tokens and self.has_numbers(token):
                    if self.param_str not in cur_node.key_to_child_node:
                        new_node = Node()
                        cur_node.key_to_child_node[self.param_str] = new_node
                        cur_node = new_node
                    else:
                        cur_node = cur_node.key_to_child_node[self.param_str]

                else:
                    if self.param_str in cur_node.key_to_child_node:
                        if len(cur_node.key_to_child_node) < self.max_children:
                            new_node = Node()
                            cur_node.key_to_child_node[token] = new_node
                            cur_node = new_node
                        else:
                            cur_node = cur_node.key_to_child_node[self.param_str]
                    else:
                        if len(cur_node.key_to_child_node) + 1 < self.max_children:
                            new_node = Node()
                            cur_node.key_to_child_node[token] = new_node
                            cur_node = new_node
                        elif len(cur_node.key_to_child_node) + 1 == self.max_children:
                            new_node = Node()
                            cur_node.key_to_child_node[self.param_str] = new_node
                            cur_node = new_node
                        else:
                            cur_node = cur_node.key_to_child_node[self.param_str]

            # if the token is matched
            else:
                cur_node = cur_node.key_to_child_node[token]

            current_depth += 1

    def get_seq_distance(self, seq1: tuple, seq2: list, include_params: bool):
        if len(seq1) == 0:
            return 1.0, 0

        param_count = 0

        for token1 in seq1:
            if token1 == self.param_str:
                param_count += 1

        if len(seq1) == len(seq2) and param_count > 0:
            seq2 = [x for i, x in enumerate(seq2) if seq1[i] != self.param_str]

        if include_params:
            seq1 = [x for x in seq1 if x != self.param_str]

        ret_val = len(set(seq1) & set(seq2)) / len(set(seq1) | set(seq2))

        ret_val = ret_val * 1.3 if ret_val * 1.3 < 1 else 1

        return ret_val, param_count

    def create_template(self, seq1: list, seq2: tuple):

        inter_set = set(seq1) & set(seq2)

        if len(seq1) == len(seq2):
            ret_val = list(seq2)
            for i, (token1, token2) in enumerate(zip(seq1, seq2)):
                if token1 != token2:
                    ret_val[i] = self.param_str
        else:
            ret_val = seq1 if len(seq1) > len(seq2) else list(seq2)
            for i, token in enumerate(ret_val):
                if token not in inter_set:
                    ret_val[i] = self.param_str

        return ret_val

    def match(self, content: str, full_search_strategy="never"):

        assert full_search_strategy in ["always", "never", "fallback"]

        required_sim_th = 0.8
        content_tokens = self.get_content_as_tokens(content)

        def full_search():
            all_ids = self.get_clusters_ids_for_seq_len(content_tokens[0])
            cluster = self.fast_match(all_ids, content_tokens, required_sim_th, include_params=True)
            return cluster

        if full_search_strategy == "always":
            return full_search()

        match_cluster = self.tree_search(self.root_node, content_tokens, required_sim_th, include_params=True)
        if match_cluster is not None:
            return match_cluster

        if full_search_strategy == "never":
            return None

        return full_search()