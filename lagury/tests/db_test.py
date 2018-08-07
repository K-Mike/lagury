from ..service import db


def _cleanup():
    test_tasks = db.Task.query.filter(db.Task.status == 'testing').all()
    for task in test_tasks:
        db.session.delete(task)
    db.session.commit()

    db.DataNode.query.filter(db.DataNode.status == 'testing').delete()
    db.session.commit()


def run():
    node_1 = db.DataNode(target_dir='test_dir', status='testing')
    node_2 = db.DataNode(target_dir='test_dir_2', status='testing')
    db.session.add_all([node_1, node_2])
    db.session.commit()

    assert node_1.id is not None
    assert node_2.id is not None

    node_id = int(node_1.id)

    node = db.DataNode.query.get(node_id)
    assert node.id == node_id

    node_3 = db.DataNode(target_dir='test_dir_3', status='testing')
    task_1 = db.Task(source_node=node_2, output_node=node_3, status='testing')
    task_1.input_nodes.append(node_1)

    db.session.add(task_1)
    db.session.commit()

    assert task_1.id is not None
    assert task_1.input_nodes[0].id == node_1.id
    assert task_1.source_node.id == node_2.id
    assert task_1.output_node.id == node_3.id

    _cleanup()
