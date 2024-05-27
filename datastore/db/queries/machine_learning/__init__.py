"""
This module contains the queries related to the machine learning structure (model and pipelines) in the database.
"""

class NonExistingTaskEWarning(UserWarning):
    pass
class PipelineCreationError(Exception):
    pass

def new_pipeline(cursor, pipeline,pipeline_name, model_ids, active:bool=False):
    """
    This function creates a new pipeline in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - pipeline (str): The pipeline to upload. Must be formatted as a json
    - model_ids (list): The UUIDs of the models in the pipeline.

    Returns:
    - The UUID of the pipeline.
    """
    try:
        query = """
            INSERT INTO 
                pipeline(
                    name,
                    data,
                    active
                    )
            VALUES
                (%s,%s,%s)
            RETURNING id    
            """
        cursor.execute(
            query,
            (
                pipeline_name,
                pipeline,
                active,
            ),
        )
        pipeline_id=cursor.fetchone()[0]
        for model_id in model_ids:
            new_pipeline_model(cursor,pipeline_id,model_id)
        
        return pipeline_id
    except(Exception):
        raise PipelineCreationError("Error: pipeline not uploaded")

def is_a_pipeline(cursor,pipeline_id:str):
    """
    This function checks if the given pipeline id is a pipeline.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - pipeline_id (str): The UUID of the pipeline.

    Returns:
    - True if the pipeline exists, False otherwise.
    """
    try:
        query = """
            SELECT EXISTS(
                SELECT 
                    1 
                FROM 
                    pipeline
                WHERE 
                    id = %s
            )
                """
        cursor.execute(
            query,
            (
                pipeline_id,
            ),
        )
        return cursor.fetchone()[0]
    except(ValueError):
        return False
    except(Exception):
        raise PipelineCreationError("Error: pipeline not found")
    
def get_pipeline_id(cursor,pipeline_name:str):
    """
    This function gets the pipeline id from the pipeline name.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - pipeline_name (str): The name of the pipeline.

    Returns:
    - The UUID of the pipeline.
    """
    try:
        query = """
            SELECT id
            FROM pipeline
            WHERE name = %s
            """
        cursor.execute(
            query,
            (
                pipeline_name,
            ),
        )
        pipeline_id=cursor.fetchone()[0]
        return pipeline_id
    except(ValueError):
        raise NonExistingTaskEWarning(f"Warning: the given pipeline '{pipeline_name}' was not found")
    except(Exception):
        raise PipelineCreationError("Error: pipeline not found")
    
def get_pipeline(cursor,pipeline_id:str):
    """
    This function gets the pipeline from the pipeline id.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - pipeline_id (str): The UUID of the pipeline.

    Returns:
    - The pipeline.
    """
    try:
        query = """
            SELECT data
            FROM pipeline
            WHERE id = %s
            """
        cursor.execute(
            query,
            (
                pipeline_id,
            ),
        )
        pipeline=cursor.fetchone()[0]
        return pipeline
    except(Exception):
        raise PipelineCreationError("Error: pipeline not found")
    
def get_active_pipeline(cursor):
    """
    This function gets all the active pipeline from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.

    Returns:
    - Array of of Tupple.
    """
    try:
        query = """
            SELECT 
                p.*,
                array_agg(pm.model_id) 
            FROM 
                "nachet_0.0.10"."pipeline" as p 
            LEFT JOIN
                "nachet_0.0.10"."pipeline_model" as pm 
            ON 
                p.id=pm.pipeline_id 
            GROUP BY
                p.id ;
            """
        cursor.execute(query)
        pipelines=cursor.fetchall()
        return pipelines
    except(Exception):
        raise PipelineCreationError("Error: pipeline not found")
    
def set_nachet_default_pipeline(cursor,pipeline_id:str):
    """
    This function sets the given pipeline as the default pipeline.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - pipeline_id (str): The UUID of the pipeline.
    """
    try:
        if not is_a_pipeline(cursor,pipeline_id):
            raise PipelineCreationError("Error: pipeline not found")
        # There is supposed to be a trigger in place in the database that sets the active pipeline to False
        # when a new pipeline is set as the default However, this is a safety measure
        query = """
            UPDATE pipeline
            SET active = False
            WHERE active = True
            """
        cursor.execute(query)
        query = """
            UPDATE pipeline
            SET active = True
            WHERE id = %s
            """
        cursor.execute(
            query,
            (
                pipeline_id,
            ),
        )
    except(Exception):
        raise PipelineCreationError("Error: pipeline not found")
    
def new_pipeline_model(cursor,pipeline_id,model_id):
    """
    This function creates a new pipeline model in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - pipeline_id (str): The UUID of the pipeline.
    - model_id (str): The UUID of the model.

    Returns:
    - The UUID of the pipeline model.
    """
    try:
        if not is_a_model(cursor,model_id):
            raise PipelineCreationError("Error: model not found")
        if not is_a_pipeline(cursor,pipeline_id):
            raise PipelineCreationError("Error: pipeline not found")
        query = """
            INSERT INTO 
                pipeline_model(
                    pipeline_id,
                    model_id
                    )
            VALUES
                (%s,%s)
            RETURNING id    
            """
        cursor.execute(
            query,
            (
                pipeline_id,
                model_id,
            ),
        )
        pipeline_model_id=cursor.fetchone()[0]
        return pipeline_model_id
    except(Exception):
        raise PipelineCreationError("Error: pipeline model not uploaded")
    
def new_model(cursor, model,name,endpoint_name,task_id:int):
    """
    This function creates a new model in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - model (str): The model to upload. Must be formatted as a json
    - user_id (str): The UUID of the user uploading.

    Returns:
    - The UUID of the model.
    """
    try:
        query = """
            INSERT INTO 
                model(
                    name,
                    endpoint_name,
                    task_id
                    )
            VALUES
                (%s,%s,%s)
            RETURNING id    
            """
        cursor.execute(
            query,
            (
                name,
                endpoint_name,
                task_id,
            ),
        )
        model_id=cursor.fetchone()[0]
        version = '0.0.1'
        model_version_id=new_model_version(cursor,model_id,version,model)
        set_active_model(cursor,model_id,str(model_version_id))
        return model_id
    except(Exception):
        raise PipelineCreationError("Error: model not uploaded")
    
def set_active_model(cursor,model_id,version_id):
    """
    This function sets the active model version in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - model_id (str): The UUID of the model.
    - version_id (str): The UUID of the model version.
    """
    try:
        if not is_a_model(cursor,model_id):
            raise PipelineCreationError("Error: model not found")
        if not is_a_model_version(cursor,version_id):
            raise PipelineCreationError("Error: model version not found")
        query = """
            UPDATE model
            SET active_version = %s
            WHERE id = %s
            """
        cursor.execute(
            query,
            (
                version_id,
                model_id,
            ),
        )
    except(Exception):
        raise PipelineCreationError("Error: model not uploaded")
    
def is_a_model(cursor,model_id:str):
    """
    This function checks if the given model id is a model.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - model_id (str): The UUID of the model.

    Returns:
    - True if the model exists, False otherwise.
    """
    try:
        query = """
            SELECT EXISTS(
                SELECT 
                    1 
                FROM 
                    model
                WHERE 
                    id = %s
            )
                """
        cursor.execute(
            query,
            (
                model_id,
            ),
        )
        return cursor.fetchone()[0]
    except(ValueError):
        return False
    except(Exception):
        raise PipelineCreationError("Error: model not found")
    
def get_model_id_from_name(cursor,model_name:str):
    """
    This function gets the model id from the model name.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - model_name (str): The name of the model.

    Returns:
    - The UUID of the model.
    """
    try:
        query = """
            SELECT id
            FROM model
            WHERE name = %s
            """
        cursor.execute(
            query,
            (
                model_name,
            ),
        )
        model_id=cursor.fetchone()[0]
        return model_id
    except(ValueError):
        raise NonExistingTaskEWarning(f"Warning: the given model '{model_name}' was not found")
    except(Exception):
        raise PipelineCreationError("Error: model not found")
    
def get_model_id_from_endpoint(cursor,endpoint_name:str):
    """
    This function gets the model id from the endpoint name.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - endpoint_name (str): The name of the endpoint.

    Returns:
    - The UUID of the model.
    """
    try:
        query = """
            SELECT id
            FROM model
            WHERE endpoint_name = %s
            """
        cursor.execute(
            query,
            (
                endpoint_name,
            ),
        )
        model_id=cursor.fetchone()[0]
        return model_id
    except(ValueError):
        raise NonExistingTaskEWarning(f"Warning: the given model '{endpoint_name}' was not found")
    except(Exception):
        raise PipelineCreationError("Error: model not found")
    
def get_model(cursor,model_id:str):
    """
    This function gets the model from the model id.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - model_id (str): The UUID of the model.

    Returns:
    - The model.
    """
    try:
        query = """
            SELECT 
                m.id,m.name,
                m.endpoint_name,
                t.name,
                v.data,
                v.version
            FROM
                "nachet_0.0.10"."model" as m
            LEFT JOIN
                "nachet_0.0.10".task as t 
            ON 
                m.task_id=t.id 
            LEFT JOIN
                "nachet_0.0.10".model_version as v
            ON
                m.active_version=v.id
            WHERE m.id = %s
            """
        cursor.execute(
            query,
            (
                model_id,
            )
        )
        model=cursor.fetchone()
        return model
    except(Exception):
        raise PipelineCreationError("Error: model not found")
    
def new_model_version(cursor, model_id, version,data):
    """
    This function creates a new model version in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - model_id (str): The UUID of the model.
    - version (str): The version of the model.

    Returns:
    - The UUID of the model version.
    """
    try:
        query = """
            INSERT INTO 
                model_version(
                    model_id,
                    version,
                    data
                    )
            VALUES
                (%s,%s,%s)
            RETURNING id    
            """
        cursor.execute(
            query,
            (
                model_id,
                version,
                data,
            ),
        )
        model_version_id=cursor.fetchone()
        return model_version_id[0]
    except(Exception):
        raise PipelineCreationError("Error: model version not uploaded")
    
def is_a_model_version(cursor,model_version_id:str):
    """
    This function checks if the given model version id is a model version.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - model_version_id (str): The UUID of the model version.

    Returns:
    - True if the model version exists, False otherwise.
    """
    try:
        query = """
            SELECT EXISTS(
                SELECT 
                    1 
                FROM 
                    model_version
                WHERE 
                    id = %s
            )
                """
        cursor.execute(
            query,
            (
                str(model_version_id),
            ),
        )
        return cursor.fetchone()[0]
    except(ValueError):
        return False
    except(Exception):
        raise PipelineCreationError("Error: model version not found")
    
def get_task_id(cursor,task_name):
    """
    This function gets the task id from the task name.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - task_name (str): The name of the task.

    Returns:
    - The id (int) of the task.
    """
    try:
        query = """
            SELECT id
            FROM task
            WHERE name ILIKE %s
            """
        cursor.execute(
            query,
            (
                task_name,
            )
        )
        task_id=cursor.fetchone()[0]
        return task_id
    except(ValueError):
        raise NonExistingTaskEWarning(f"Warning: the given task '{task_name}' was not found")
    except(Exception) as e:
        raise PipelineCreationError("Error: task not found")
    
def new_task(cursor,task_name):
    """
    This function creates a new task in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - task_name (str): The name of the task.

    Returns:
    - The UUID of the task.
    """
    try:
        query = """
            INSERT INTO 
                task(
                    name
                    )
            VALUES
                (%s)
            RETURNING id    
            """
        cursor.execute(
            query,
            (
                task_name,
            ),
        )
        task_id=cursor.fetchone()[0]
        return task_id
    except(Exception):
        raise PipelineCreationError("Error: task not uploaded")