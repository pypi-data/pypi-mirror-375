from squyrrel.orm.field import StringField, IntegerField, DateTimeField, BooleanField


def extract_ids(string):
    if string and string[0] == '[':
        string = string[1:-1]
        if not string:
            return []
        ids = string.split(',')
        return [int(id.strip()) for id in ids]
    else:
        return []


def remove_nulls(array):
    return [item for item in array if item]


def extract_entity_with_id(model, entities, id):
    if not isinstance(entities, list):
        raise ValueError(f"Invalid type <{repr(entities)}> of argument for extract_entity_with_id")
    sanitized_list = [item for item in entities if item]
    if not sanitized_list:
        # TODO: correct return value?
        return None
    first_element = sanitized_list[0]
    if isinstance(first_element, int):
        raise ValueError(f"Invalid type <{repr(entities)}> of argument for extract_entity_with_id")
    if isinstance(first_element, model):
        return [entity.id for entity in sanitized_list if entity.id == id]
    if isinstance(first_element, dict):
        for entity in sanitized_list:
            try:
                if id == entity[model.id_field_name()]:
                    return entity
            except KeyError:
                pass


def extract_entities_without_id(model, obj):
    if not isinstance(obj, list):
        raise ValueError(f"Invalid type <{repr(obj)}> of argument for extract_entities_without_id")
    if not obj:
        return []
    sanitized_list = [item for item in obj if item]
    first_element = sanitized_list[0]
    if isinstance(first_element, int):
        return []
    if isinstance(first_element, model):
        return [entity.id for entity in sanitized_list if entity.id]
    if isinstance(first_element, dict):
        result = []
        for entity in sanitized_list:
            try:
                id = entity[model.id_field_name()]
                if not id:
                    result.append(entity)
            except KeyError:
                result.append(entity)
        return result


# TODO: unit test all methods in utils.py
def sanitize_id_array(model, obj):
    if isinstance(obj, str):
        return extract_ids(obj)
    if isinstance(obj, list):
        if not obj:
            return []
        sanitized_list = [item for item in obj if item]
        first_element = sanitized_list[0]
        if isinstance(first_element, int):
            return obj
        if isinstance(first_element, model):
            return [entity.id for entity in sanitized_list]
        if isinstance(first_element, dict):
            result = []
            for entity in sanitized_list:
                try:
                    id = entity[model.id_field_name()]
                    if id:
                        result.append(entity[model.id_field_name()])
                except KeyError:
                    pass
            return result
    raise ValueError(f"Invalid type <{repr(obj)}> of argument for sanitize_id_array")


def m2m_aggregation_subquery_alias(model, relation_name):
    return f'{model.table_name}_{relation_name}'


def field_to_sql_data_type(field):
    # todo: dynamic method_name pattern
    # at the moment only Sqlite...

    if isinstance(field, StringField):
        return 'TEXT'
    if isinstance(field, IntegerField):
        return 'INTEGER'
    if isinstance(field, DateTimeField):
        return 'TEXT'
    if isinstance(field, BooleanField):
        return 'INTEGER'


#def build_where_clause(model, filter_condition=None, **kwargs):
#    # todo: this is garbage
#    if filter_condition is None:
#        filter_conditions = []
#        for key, value in kwargs.items():
#            filter_conditions.append(
#                Equals.column_as_parameter(ColumnReference(key, table=model.table_name), value))
#        if filter_conditions:
#            return WhereClause(filter_conditions[0])
#        else:
#            return None
#    else:
#        return WhereClause(filter_condition)


