from tg import TGController, expose, request


class RootController(TGController):
    def __call__(self, *args, **kwargs):
        request.identity = request.environ.get('repoze.who.identity')
        return super(RootController, self).__call__(*args, **kwargs)

    @expose()
    def index(self):
        return 'HELLO'
