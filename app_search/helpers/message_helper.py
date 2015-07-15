from django.contrib.sessions.backends.cache import SessionStore

class message:
    def flash(request, message, category="success"):
        request.session["_flash"] = {category: message}

    def flash_with_errors(request, top_message, *errors_group):
        messages = []
        messages.append(top_message)
        for errors in errors_group:
            for k, v in errors.items():
                for s in v:
                    messages.append("{0} {1}".format(k, s))

        message_s = "\n<br />".join(messages)
        message.flash(request, message_s, "danger")

    def get_flash_message(request):
        page = {"message": ""}
        if request.session and '_flash' in request.session:
            page['message'] = request.session["_flash"]
            request.session["_flash"] = {}

        return page

