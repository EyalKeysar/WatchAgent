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
    def __init__(self, child_id, parent_email, child_name, restrictions, time_limit):
        child_id = child_id
        self.parent_email = parent_email
        self.child_name = child_name
        self.restrictions = restrictions
        self.time_limit = time_limit


class ParentData:
    def __init__(self, email, name, password_hash):
        self.email = email
        self.name = name
        self.password_hash = password_hash

