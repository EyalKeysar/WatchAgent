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
        if restriction is None:
            return None
        return {
            "id": restriction.id,
            "child_id": restriction.child_id,
            "program_name": restriction.program_name,
            "start_time": restriction.start_time,
            "end_time": restriction.end_time,
            "allowed_time": restriction.allowed_time,
            "time_span": restriction.time_span,
            "usage_time": restriction.usage_time
        }
    @staticmethod
    def deserialize(data):
        if data is None:
            return None
        return Restriction(data["id"], data["child_id"], data["program_name"], data["start_time"], data["end_time"], data["allowed_time"], data["time_span"], data["usage_time"])
        
class RestrictionListSerializer:
    @staticmethod
    def serialize(restriction_list):
        if restriction_list is None:
            return None
        restrictions = []
        for restriction in restriction_list:
            restrictions.append(RestrictionSerializer.serialize(restriction))
        return json.dumps(restrictions)
    
    @staticmethod
    def deserialize(serialized):
        if serialized is None:
            return None
        data = json.loads(serialized)
        restrictions = []
        for restriction in data:
            restriction = RestrictionSerializer.deserialize(restriction)
            restrictions.append(Restriction(restriction.id, restriction.child_id, restriction.program_name, restriction.start_time, restriction.end_time, restriction.allowed_time, restriction.time_span, restriction.usage_time))
        
        return restrictions


class TimeLimitSerializer:
    @staticmethod
    def serialize(time_limit):
        if time_limit is None:
            return None
        return json.dumps(time_limit.__dict__)

    @staticmethod
    def deserialize(serialized):
        if serialized is None:
            return None
        data = json.loads(serialized)
        return TimeLimit(data["id"], data["start_time"], data["end_time"], data["allowed_time"], data["time_span"])    

class ChildDataSerializer:
    @staticmethod
    def serialize(child_data):
        if child_data is None:
            return None
        return {
            "child_id": child_data.child_id,
            "parent_email": child_data.parent_email,
            "child_name": child_data.child_name,
            "restrictions": RestrictionListSerializer.serialize(child_data.restrictions),
            "time_limit": TimeLimitSerializer.serialize(child_data.time_limit)
        }

    @staticmethod
    def deserialize(data):
        if data is None:
            return None
        return ChildData(data["child_id"], data["parent_email"], data["child_name"], RestrictionListSerializer.deserialize(data["restrictions"]), data["time_limit"])


class ChildListSerializer:
    @staticmethod
    def serialize(child_list):
        if child_list is None:
            return None
        children = []
        for child in child_list:
            children.append(ChildDataSerializer.serialize(child))
        return json.dumps(children)
    
    @staticmethod
    def deserialize(serialized):
        if serialized is None:
            return None
        data = json.loads(serialized)
        children = []
        for child in data:
            print("child = ", child)
            child = ChildDataSerializer.deserialize(child)
            children.append(ChildData(child.child_id, child.parent_email, child.child_name, child.restrictions, child.time_limit))
        
        return children