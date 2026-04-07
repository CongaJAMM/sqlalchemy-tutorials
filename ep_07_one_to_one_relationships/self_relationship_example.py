# =============================================================
# |                 Created By: ZeqTech                       |
# |         YouTube: https://www.youtube.com/@zeqtech         |
# =============================================================
# Related Video: https://www.youtube.com/watch?v=xRfupYowU-I

"""Example #2

Self-Referential One-to-One Relationship Module (Linked List Model)

This module demonstrates a specialized recursive relationship where a table 
references itself to create a chain of objects. This is the standard 
ORM pattern for data structures like Linked Lists or Ordered Sequences.

Key Concepts:
1. Self-Referential Mapping: 
   The 'node_id' Foreign Key points back to the 'nodes.id' in the same table, 
   allowing one Node to "own" another Node.

2. remote_side: 
   Crucial for self-referential relationships. It tells SQLAlchemy which 
   column represents the "parent" side of the relationship during a join.

3. uselist=False: 
   Ensures a One-to-One constraint in Python, allowing us to access 
   'node.next_node' as a single object rather than a list.

4. post_update=True: 
   Required for circular references (e.g., Node A -> B -> C -> A). It tells 
   SQLAlchemy to use an extra UPDATE statement to break the "chicken and egg" 
   logic of which row to insert first when they all point to each other.
"""

from sqlalchemy import Column, ForeignKey, Integer, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

db_url = 'sqlite:///ep_07_one_to_one_self_relationships.db'

engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Node(Base):
    """
    Represents a single 'Node' in a linked sequence.
    
    Attributes:
        value (int): The data stored in the node.
        node_id (FK): The Foreign Key pointing to the 'id' of the next 
                      node in the sequence.
        
    ORM Attributes:
        next_node (relationship): A self-referential link to another Node 
            instance. 
            - remote_side=[id]: Identifies 'id' as the target of the FK.
            - post_update: Handles the save logic for circular chains.
    """
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)

    # Physical link to the same table
    node_id = Column(Integer, ForeignKey('nodes.id'))
    

    # Logical link to the next object in the chain
    # remote_side=[id]: explicitly telling SQLAlchemy that the 'id' column represents the "Remote" (Parent) side of the link. This defines the direction of the arrow in your linked list.
    # uselist=False: This flag forces the relationship to be a Scalar (a single object). It tells the ORM: "A node can only have exactly one next neighbor." This turns a "One-to-Many" structure into a "One-to-One" structure.
    # post_update=True: Solves circular dependency; INSERT all nodes into the database with node_id = NULL. (Now all IDs exist), Then UPDATE the rows to fill in the actual node_id values now that the IDs are settled
    next_node = relationship('Node', remote_side=[id], uselist=False, post_update=True)

    def __repr__(self):
        # Note: Accessing self.next_node.id requires the relationship to be loaded
        return f'<Node {self.id} value={self.value}, next node id={self.next_node.id}>'


Base.metadata.create_all(engine)

# If there is data in the database, don't add more data
if session.query(Node).count() < 1:
    node1 = Node(value=1)
    node2 = Node(value=2)
    node3 = Node(value=3)

    node1.next_node = node2
    node2.next_node = node3
    node3.next_node = node1

    session.add_all([node1, node2, node3])
    session.commit()


node1, node2, node3 = session.query(Node).limit(3).all()

print(node1)
print(node2)
print(node3)
