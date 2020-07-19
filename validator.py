# Validation Error
class ValidationError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Validator
class Validator():
    constraints = {}

    # INIT
    def __init__(self, types):
        self.constraints = types

    # Checks the length according to the given types
    def check_length(self, data, type):
        if(type.lower() is 'post'):
            # Check if the post is too long; if it is, abort
            if(len(data) > self.constraints.post.max):
                raise ValidationError({
                    'code': 400,
                    'description': 'Your post is too long! Please shorten \
                                    it and try to post it again.'
                }, 400)
            # Check if the post is empty; if it is, abort
            elif(len(data) < self.constraints.post.min):
                raise ValidationError({
                    'code': 400,
                    'description': 'You cannot post an empty post. Please \
                                    write something and try to send it again.'
                }, 400)
        elif(type.lower() is 'message'):
            # Check if the message is too long; if it is, abort
            if(len(data) > self.constraints.message.max):
                raise ValidationError({
                    'code': 400,
                    'description': 'Your message is too long! Please shorten \
                                    it and try to send it again.'
                }, 400)
            # Check if the message is empty; if it is, abort
            elif(len(data) < self.constraints.message.min):
                raise ValidationError({
                    'code': 400,
                    'description': 'You cannot send an empty message. Please \
                                    write something and try to send it again.'
                }, 400)
        elif(type.lower() is 'display name'):
            # Check if the name is too long; if it is, abort
            if(len(data) > self.constraints.user.max):
                raise ValidationError({
                    'code': 400,
                    'description': 'Your new display name is \
                                    too long! Please shorten \
                                    it and try again.'
                }, 400)
            # Check if the name is empty; if it is, abort
            elif(len(data) < self.constraints.user.min):
                raise ValidationError({
                    'code': 400,
                    'description': 'Your display name cannot be \
                                    empty. Please add text and \
                                    try again.'
                }, 400)
        elif(type.lower() is 'report'):
            # Check if the report reason is too long; if it is, abort
            if(len(data) > self.constraints.report.max):
                raise ValidationError({
                    'code': 400,
                    'description': 'Your report reason is too long! Please \
                                    shorten it and try to send it again.'
                }, 400)
            # Check if the report reason is empty; if it is, abort
            elif(len(data) < self.constraints.report.min):
                raise ValidationError({
                    'code': 400,
                    'description': 'You cannot send a report without a reason. \
                                    Please write something and try to send it \
                                    again.'
                }, 400)

        return True

    # Checks the type of the given item
    def check_type(self, data, type):
        # If the type is one of the free text types, check that it's a
        # string
        if(type.lower() is 'post text' or type.lower() is 'message text' or
           type.lower() is 'display name' or type.lower() is 'report reason'):
           # If it's not a string, raise a validation error
            if(type(data) is not str):
                raise ValidationError({
                    'code': 400,
                    'description': type + ' must be of type \'String\'. \
                                    Please correct the error and try again.'
                }, 400)

        return True
