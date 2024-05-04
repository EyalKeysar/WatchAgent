import json
from typing import List

# --------------------------------------------------------------------------------------------------------------------- DTOs
class Restriction:
    def __init__(self, id, child_id, program_name, start_time, end_time, allowed_time, time_span, usage_time):
        self.id = id
        self.child_id = child_id
        
        self.program_name = program_name

        self.start_time = start_time
        self.end_time = end_time

        self.allowed_time = allowed_time
        self.time_span = time_span
        self.usage_time = usage_time

class TimeLimit:
    def __init__(self, id, start_time, end_time, allowed_time, time_span):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.allowed_time = allowed_time
        self.time_span = time_span

class ChildData:
    def __init__(self, child_id: int, parent_email: str, child_name: str, restrictions: List[Restriction], time_limit: TimeLimit) -> None:
        self.child_id = child_id
        self.parent_email = parent_email
        self.child_name = child_name
        self.restrictions = restrictions
        self.time_limit = time_limit

class ParentData:
    def __init__(self, email, name, password_hash):
        self.email = email
        self.name = name
        self.password_hash = password_hash


# --------------------------------------------------------------------------------------------------------------------- Serialization
class RestrictionSerializer:
    @staticmethod
    def serialize(restriction):
        return json.dumps(restriction.__dict__)

    @staticmethod
    def deserialize(serialized):
        data = json.loads(serialized)
        return Restriction(data["id"], data["child_id"], data["program_name"], data["start_time"], data["end_time"], data["allowed_time"], data["time_span"], data["usage_time"])
    
class TimeLimitSerializer:
    @staticmethod
    def serialize(time_limit):
        return json.dumps(time_limit.__dict__)

    @staticmethod
    def deserialize(serialized):
        data = json.loads(serialized)
        return TimeLimit(data["id"], data["start_time"], data["end_time"], data["allowed_time"], data["time_span"])    

class ChildDataSerializer:
    @staticmethod
    def serialize(child_data):
        return json.dumps(child_data.__dict__)

    @staticmethod
    def deserialize(serialized):
        data = json.loads(serialized)
        return ChildData(data["child_id"], data["parent_email"], data["child_name"], data["restrictions"], data["time_limit"])
    
class ChildListSerializer:
    @staticmethod
    def serialize(child_list):
        children = []
        for child in child_list:
            children.append(ChildDataSerializer.serialize(child))
        return json.dumps(children)
    
    @staticmethod
    def deserialize(serialized):
        data = json.loads(serialized)
        children = []
        for child in data:
            print("child = ", child)
            child = ChildDataSerializer.deserialize(child)
            children.append(ChildData(child.child_id, child.parent_email, child.child_name, child.restrictions, child.time_limit))
        
        return children