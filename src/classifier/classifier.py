import json
from collections import defaultdict
from typing import List, Set, Tuple

import spacy

from src.database import CategoryMapping, Category, WeightedCategory, Transaction
from src.database.db import get_db


nlp = spacy.load("en_core_web_sm")


def get_words(text: str) -> Tuple[Set[str], Set[str]]:
    """
    Get the words and proper nouns from a text.

    Args:
        text: The text to get the words from.

    Returns:
        A tuple of two sets of words. The first set contains the nouns, the second set contains the proper nouns.
    """
    db = get_db()
    doc = nlp(text.lower())

    nouns = set()
    proper_nouns = set()
    for token in doc:
        if token.is_stop:
            continue
        if token.pos_ == "NOUN":
            nouns.add(token.text)
        elif token.pos_ == "PROPN":
            proper_nouns.add(token.text)

    for chunk in doc.noun_chunks:
        if chunk.root.pos_ not in ["NOUN", "PROPN"]:
            continue
        if chunk.text == doc.text:
            continue
        nouns.add(chunk.text)

    return nouns, proper_nouns


def classify(transaction: Transaction) -> Transaction:
    """
    Classify a title into a category.

    Args:
        transaction: The transaction to classify.

    Returns:
        The transaction with the category set.
    """
    db = get_db()

    # parse the title for nouns and pronouns that can be used as categories
    nouns, proper_nouns = get_words(transaction.title)

    # get category mappings for each word in nouns and proper_nouns list
    found = set()
    category_mapping_list: List[CategoryMapping] = []
    for pn in proper_nouns:
        if result := db.execute(
            "SELECT * FROM categorical_mapping WHERE word = ? AND part_of_speech = ?", (pn, "PROPN")
        ).fetchone():
            category_mapping_list.append(CategoryMapping(**result))
            found.add(pn)

    proper_nouns -= found

    found = set()
    for n in nouns:
        if result := db.execute(
            "SELECT * FROM categorical_mapping WHERE word = ? AND part_of_speech = ?", (n, "NOUN")
        ).fetchone():
            category_mapping_list.append(CategoryMapping(**result))
            found.add(n)

    nouns -= found

    # create rankings for each category mapping
    rankings = defaultdict(lambda: 0)
    for mapping in category_mapping_list:
        for category in mapping.categories:
            rankings[category.category_id] += mapping.weight

    # if there are rankings, get the highest ranking, otherwise return the transaction with category of unknown
    if rankings:
        rankings = dict(rankings)
        category_id = max(rankings, key=rankings.get)
    else:
        transaction.category_id = -1
        return transaction

    # get category label from categories table
    category_result = db.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
    transaction.category_id = Category(**category_result).id

    # Update all category mappings weight with this id
    for mapping in category_mapping_list:
        for category in mapping.categories:
            if category.category_id == category_id:
                category.weight += 1
                break
        else:
            category = WeightedCategory(category_id=category_id, weight=1)
            mapping.categories.append(category)
        categories = json.dumps([dict(category) for category in mapping.categories])
        db.execute(
            "UPDATE categorical_mapping SET categories = ? WHERE id = ?;",
            (categories, mapping.id),
        )
        db.commit()

    # create new mappings for unmapped words
    categories = json.dumps([dict(WeightedCategory(category_id=category_id, weight=1))])
    for noun in nouns:
        db.execute(
            "INSERT INTO categorical_mapping (word, part_of_speech, categories) VALUES (?, ?, ?);",
            (noun, "NOUN", categories),
        )
        db.commit()

    for pn in proper_nouns:
        db.execute(
            "INSERT INTO categorical_mapping (word, part_of_speech, categories) VALUES (?, ?, ?);",
            (pn, "PROPN", categories),
        )
        db.commit()

    return transaction


def update_classification(original: Transaction, updated: Transaction) -> None:
    """
    Update the classification of a transaction.

    :param original: The original transaction.
    :param updated: The updated transaction.
    :return: None; this is for database purposes.
    """
    if original.category_id == updated.category_id:
        return

    db = get_db()

    nouns, proper_nouns = get_words(original.title)

    # get category mappings for each word in nouns and proper_nouns list
    category_mapping_list: List[CategoryMapping] = []
    proper_nouns_not_found = set()
    for pn in proper_nouns:
        if result := db.execute(
            "SELECT * FROM categorical_mapping WHERE word = ? AND part_of_speech = ?", (pn, "PROPN")
        ).fetchone():
            category_mapping_list.append(CategoryMapping(**result))
        else:
            proper_nouns_not_found.add(pn)

    nouns_not_found = set()
    for n in nouns:
        if result := db.execute(
            "SELECT * FROM categorical_mapping WHERE word = ? AND part_of_speech = ?", (n, "NOUN")
        ).fetchone():
            category_mapping_list.append(CategoryMapping(**result))
        else:
            nouns_not_found.add(n)

    # de-increment all categories if they are not Unknown
    if original.category_id != -1:
        for mapping in category_mapping_list:
            for category in mapping.categories:
                if category.category_id == original.category_id:
                    category.weight -= 1
                    break
            categories = json.dumps([dict(category) for category in mapping.categories])
            db.execute(
                "UPDATE categorical_mapping SET categories = ? WHERE id = ?;",
                (categories, mapping.id),
            )
            db.commit()

    # add any new words if necessary
    categories = json.dumps([dict(WeightedCategory(category_id=updated.category_id, weight=1))])
    for noun in nouns_not_found:
        db.execute(
            "INSERT INTO categorical_mapping (word, part_of_speech, categories) VALUES (?, ?, ?);",
            (noun, "NOUN", categories),
        )
        db.commit()

    for pn in proper_nouns_not_found:
        db.execute(
            "INSERT INTO categorical_mapping (word, part_of_speech, categories) VALUES (?, ?, ?);",
            (pn, "PROPN", categories),
        )
        db.commit()

    # increment all other category mappings
    for mapping in category_mapping_list:
        for category in mapping.categories:
            if category.category_id == updated.category_id:
                category.weight += 1
                break
        else:
            category = WeightedCategory(category_id=updated.category_id, weight=1)
            mapping.categories.append(category)
        categories = json.dumps([dict(category) for category in mapping.categories])
        db.execute(
            "UPDATE categorical_mapping SET categories = ? WHERE id = ?;",
            (categories, mapping.id),
        )
        db.commit()
