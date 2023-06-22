import factory
from factory import Factory, RelatedFactory, Sequence, SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from factory.declarations import RelatedFactoryList
from factory.fuzzy import FuzzyChoice, FuzzyDecimal, FuzzyInteger, FuzzyText
from mimesis_factory import MimesisField
from pytest_factoryboy import register
from pytest_factoryboy import register
from ekklesia_common.database import Session
from ekklesia_voting.datamodel import Voter


class SQLAFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"


@register
class VoterFactory(SQLAFactory):
    class Meta:
        model = Voter

    auid = Sequence("voter{}".format)
