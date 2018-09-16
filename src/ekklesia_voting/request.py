import morepath 


class EkklesiaVotingRequest(morepath.Request):

    def current_user(self):
        return None

    def render_template(self, template, **context):
        template = self.app.jinja_env.get_template(template)
        return template.render(**context)
