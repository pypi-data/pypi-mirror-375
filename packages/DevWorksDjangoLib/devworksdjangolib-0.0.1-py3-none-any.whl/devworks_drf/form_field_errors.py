import logging

from rest_framework.exceptions import ErrorDetail

log = logging.getLogger(__name__)


def form_errors(errors):
    log.debug("parsing form_error: {}: {}<<<".format(
        errors.__class__.__name__,
        errors
    ))

    result = {"errorName": "FormErrors"}
    result.update(form_field_errors(errors))

    return result


def form_field_errors(errors):
    if isinstance(errors, list):
        result = {}
        if len(errors) == 1 and isinstance(errors[0], ErrorDetail):
            return form_field_errors(errors[0])
        else:
            for i in range(len(errors)):
                result[i] = form_field_errors(errors[i])

    elif isinstance(errors, dict):
        if errors:
            result = {}
            for field in errors:
                if field == 'non_field_errors':
                    non_form_errors = errors.get('non_field_errors')
                    if non_form_errors:
                        for msg in non_form_errors:
                            result["errorMessage"] = "{}".format(msg)
                            result["errorCode"] = getattr(msg, 'code', str(msg))
                else:
                    result[field] = form_field_errors(errors[field])
        else:
            result = None
    elif errors is None:
        return None
    else:
        return {
            "errorMessage": "{}".format(errors),
            "errorCode": getattr(errors, 'code', str(errors))
        }
    return result
