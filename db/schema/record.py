

def record_schema(record) -> dict:

    return {
        'id' : str(record['_id']),
        'start' : record.get('start'),
        'end' : record.get('end'),
        'task_id' : record.get('task_id'),
        'time_spend' : record.get('time_spend'),
        'recording' : record.get('recording')
    }


def records_schema(records) -> list:

    return [record_schema(record) for record in records]