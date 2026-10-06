"""Tools for the Nimbus Noodle Co. support agent (company track).

Same pattern as Module 1: plain Python functions with @tool. The model reads
each docstring to decide when to call them.
"""

import os
from strands import tool

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

ORDERS = {
    "NN-1042": {"customer": "Alex", "items": "Cumulus Tonkotsu Ramen, Data Lake Lemonade", "total": 18.75, "status": "Delivered"},
    "NN-1043": {"customer": "Jordan", "items": "Catering: 20x Stratus Veggie Ramen", "total": 260.00, "status": "Scheduled for Friday"},
    "NN-1044": {"customer": "Sam", "items": "Lightning Dan Dan Noodles", "total": 12.75, "status": "Out for delivery"},
}


def load_docs():
    """Read every markdown file under data/ (including subfolders) into a list of sections."""
    sections = []
    for root, dirs, files in os.walk(DATA_DIR):
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            text = open(path, encoding="utf-8").read()
            for chunk in text.split("\n## "):
                sections.append({"source": os.path.relpath(path, DATA_DIR), "text": chunk.strip()})
    return sections


DOCS = load_docs()


@tool
def search_docs(query: str) -> str:
    """Search the Nimbus Noodle Co. knowledge base (menu, hours, policies, FAQ).

    Args:
        query: What the customer is asking about, in a few keywords
    """
    words = query.lower().split()
    scored = []
    for section in DOCS:
        score = 0
        for word in words:
            if len(word) > 2 and word in section["text"].lower():
                score = score + 1
        if score > 0:
            scored.append((score, section))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    if not scored:
        return "No matching documents found."
    results = []
    for score, section in scored[:2]:
        results.append(f"[{section['source']}]\n{section['text']}")
    return "\n\n".join(results)


@tool
def check_order(order_id: str) -> str:
    """Look up a Nimbus order by its ID.

    Args:
        order_id: The order ID, like NN-1042
    """
    order = ORDERS.get(order_id.upper())
    if not order:
        return f"No order found with ID {order_id}"
    return f"Order {order_id}: {order['items']} | Total ${order['total']:.2f} | Status: {order['status']}"


@tool
def issue_refund(order_id: str, amount: float) -> str:
    """Refund money for an order back to the original payment method.

    Args:
        order_id: The order ID to refund
        amount: Refund amount in dollars
    """
    return f"Refund of ${amount:.2f} issued for {order_id}."
