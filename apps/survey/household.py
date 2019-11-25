"""
Survey Household class

"""

from . import PROFILE_SURVEY
from apps.common.db import quote_query, fetch_one_dict

SIMPLE_PROFILE_COLUMNS = {
        'Q1':'gender',
        'Q2':'date_birth',
}

query_profile = []
for col in SIMPLE_PROFILE_COLUMNS.items():
    query_profile.append("{{" + col[0] + "}} as {{" + col[1] + "}}")

query_profile = ",".join(query_profile)

SESSION_KEY = '_survey_household_'

class SurveyHousehold:

    @staticmethod
    def get_household(request):
        h = request.session.get(SESSION_KEY, None)
        if h is None:
            h = SurveyHousehold(request.user)
            request.session[SESSION_KEY] = h
        return h

    def __init__(self, user):
        self.participants = {}
        self.profiles = {}
        self.load(user)

    @property
    def participants(self):
        return self.participants

    def gids(self, idx=None):
        kk = self.participants.keys()
        if idx is None:
            return kk
        if idx < 0 | idx >= len(kk):
            return None
        return kk[idx]

    def count(self):
        return len(self.participants)

    def load(self, user):
        pp = list(user.surveyuser_set.filter(deleted=False))
        for p in pp:
            gid = p.global_id
            self.participants[gid] = p
        self.profiles = {}

    def get_simple_profile(self, gid):
        """
            Get minimal information about a participant
        """
        profile = self.profiles.get(gid)
        if profile is not None:
            return profile
        profile = self._fetch_simple_profile(gid)
        self.profiles[gid] = profile
        return profile

    def _fetch_simple_profile(self, gid):
        """
         @todo use Survey object to get table name
        """
        table = 'pollster_results_' + PROFILE_SURVEY
        query = quote_query("select " + query_profile + " from " + table + " where {{global_id}}=%s order by {{timestamp}} desc limit 1")
        #print query
        profile = fetch_one_dict(query, [gid])
        return profile

    def profile_updated(self, request, gid):
        if gid in self.profiles:
            self.profiles.pop(gid)
            # Tell session that object has been updated
            request.session.modified = True

    def participants_updated(self, request):
        self.load(request.user)
        request.session.modified = True
