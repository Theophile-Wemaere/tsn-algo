import sqlite3
import networkx as nx
from pyvis.network import Network

class user_graph:

    def __init__(self):
        pass

    def get_users_and_relations(self,db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id_user, username FROM users WHERE id_user IN (SELECT follower FROM relations) OR id_user IN (SELECT followed FROM relations)")
        users = cursor.fetchall()
        cursor.execute("SELECT follower, followed FROM relations")
        relations = cursor.fetchall()

        conn.close()
        return users, relations

    def create_graph(self,users, relations):
        G = nx.DiGraph()  
        for user_id, username in users:
            G.add_node(user_id, label=username)

        for follower, followed in relations:
            G.add_edge(follower, followed)

        return G

    def draw_graph(self,G):
        net = Network(notebook=True, directed=True, select_menu=True, filter_menu=True)

        for node, data in G.nodes(data=True):
            net.add_node(node, label=data['label'])

        for source, target in G.edges():
            net.add_edge(source, target,smooth=True)

        net.show_buttons()
        net.show("user_relations.html")

    def generate(self,):
        db_path = 'database.db'
        users, relations = self.get_users_and_relations(db_path)
        G = self.create_graph(users, relations)
        self.draw_graph(G)

def main():

    user= user_graph()
    user.generate()

if __name__ == "__main__":
    main()
