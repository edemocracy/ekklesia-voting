import logging
from ekklesia_common.identity_policy import NoIdentity
from ekklesia_common.utils import cached_property
import morepath
# TODO: Implement user model
# from ekklesia_common.datamodel import User


logg = logging.getLogger(__name__)


class UserIdentity(morepath.Identity):

    def __init__(self, user, refresh_user_object):
        self._user = user
        self._refresh_user_object = refresh_user_object
        self.userid = user.id

    @cached_property
    def user(self):
        return self._refresh_user_object(self._user)


class EkklesiaVotingIdentityPolicy(morepath.IdentityPolicy):

    identity_class = UserIdentity

    def remember(self, response, request, identity):
        request.browser_session['user_id'] = identity.user.id

    def identify(self, request):
        user_id = request.browser_session.get('user_id')
        logg.debug('identity policy, user_id is %s', user_id)
        if user_id is None:
            return NoIdentity()

        user = request.db_session.query(User).get(user_id)

        if user is None:
            logg.info('user_id %s in session, but not found in the database!', user_id)
            return NoIdentity()

        def refresh_user_object(user):
            return request.db_session.merge(user)

        return self.identity_class(user, refresh_user_object)

    def forget(self, response, request):
        del request.browser_session['user_id']
