import pandas as pd
import numpy as np
import pickle
from scipy.cluster.hierarchy import cut_tree, fcluster, linkage
import json
import random


def get_hierarchy(arr, method='ward', metric='euclidean'):
    df = pd.read_csv('util/data.csv')

    left_array_unique = df['lhs'].drop_duplicates().to_numpy()
    right_array_unique = df['rhs'].drop_duplicates().to_numpy()
    relationship_array_unique = df['relationship'].drop_duplicates().to_numpy()

    # approach => construct a matrix where each row represents the vector representation of fields
    X = None

    try:
        with open("util/data.pickle", "rb") as infile:
            X = pickle.load(infile)
    except Exception as e:
        print("serialized data cannot be loaded, create new representations")
        matrix = []
        for lhs in left_array_unique:
            matrix.append([])
            curr_idx = len(matrix) - 1
            for relationship in relationship_array_unique:
                matrix[curr_idx].append([0 for x in range(len(right_array_unique))])
                for data in df[(df.lhs == lhs) & (df.relationship == relationship)]['rhs'].to_numpy():
                    matrix[curr_idx][np.where(relationship_array_unique == relationship)[0][0]][
                        np.where(right_array_unique == data)[0][0]] = 1
        data_set = np.array(matrix)
        nsamples, nx, ny = data_set.shape
        X = data_set.reshape((nsamples, nx * ny))
        with open("data.pickle", "wb") as outfile:
            pickle.dump(X, outfile)

    dendogram_lvls = [60, 50, 40, 30, 20, 10, 5, 4, 3, 2, 1]

    Z = linkage(X, method=method, metric=metric)

    res_dict = dict()

    for lvl in dendogram_lvls:
        DEND_LVL = lvl

        N_CLUSTERS_CUT = [DEND_LVL]
        clusters = cut_tree(Z, n_clusters=N_CLUSTERS_CUT)

        # transpose matrix
        clusters = clusters.T
        id = 0
        df_final = dict()
        for row in clusters[::-1]:
            groups = {}
            for i, g in enumerate(row):
                if g not in groups:
                    groups[g] = set([])
                groups[g].add(i)

            df_final['lvl' + str(DEND_LVL)] = list(groups.values())
            id += 1

        df_final_res = dict()

        for val in df_final.keys():
            res = []
            for i in df_final[val]:
                mat = []
                for p in i:
                    mat.append(left_array_unique[p])
                res.append(mat)

            df_final_res[val] = res

        res_dict[DEND_LVL] = df_final_res

    class Cluster:
        def __init__(self, value):
            self.value = value
            self.children = []
            self.content = []

        def __hash__(self):
            return self.value

        class ComplexEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Cluster):
                    return obj.__dict__
                return json.JSONEncoder.default(self, obj)

        def __str__(self):
            # return "\n NAME: {0} \n" \
            #        "CHILDREN (SIZE = {1}) = {2} \n" \
            #        "CONTENT (SIZE = {3}) = {4} \n".format(self.name, len(self.children), self.children, len(self.content),
            #                                               self.content)

            return json.dumps(self, cls=self.ComplexEncoder)

        def __repr__(self):
            return self.__str__()

        @staticmethod
        def getFatherId(el, cluster):
            id = 0
            for i in cluster:
                if el in i:
                    return id
                id += 1
            return -1

        @staticmethod
        def getEncoding(lvl, id, length, content):
            # return "lvl " + str(dendogram_lvls[lvl]) + "  " + str(id) + " size: " + str(length)
            return {"id": "lvl " + str(dendogram_lvls[lvl]),
                    "size": str(length),
                    "content": content,
                    "uniqueId": id}

        def containsTag(self, tag):
            for i in self.content:
                for j in i:
                    if tag in j:
                        return True

            return False

        def isParent(self, subCluster):
            if subCluster[0] in self.content:
                return True
            return False

    root = Cluster("root")
    lvl = len(dendogram_lvls) - 1
    big_clusters = res_dict[dendogram_lvls[lvl]]['lvl' + str(dendogram_lvls[lvl])]
    root.content = big_clusters[0]

    root.value = Cluster.getEncoding(0, 0, len(big_clusters), big_clusters[0])

    global currId
    global ids

    def buildTree(root: Cluster, lvl, ids=set()):

        currId = random.randint(0, 99999999)

        if lvl < 1:
            return

        small_clusters = res_dict[dendogram_lvls[lvl - 1]]['lvl' + str(dendogram_lvls[lvl - 1])]

        for i in small_clusters:
            while currId in ids:
                currId += 1

            ids.add(currId)

            currCluster = Cluster(Cluster.getEncoding(lvl, currId, len(i), i))
            currCluster.content = i
            currCluster.value = Cluster.getEncoding(lvl, currId, len(i), i)

            if root.isParent(i):
                root.children.append(currCluster)

        for ch in root.children:
            buildTree(ch, lvl - 1)

    buildTree(root, lvl)

    return {"payload": root}


def get_available_tags():
    df = pd.read_csv('util/data.csv')
    left_array_unique = list(df['lhs'].drop_duplicates().to_numpy())

    return {"payload": left_array_unique}
