from sqlalchemy import Boolean, DateTime, Integer, func, String, Text
from sqlalchemy.orm import object_session

from ekklesia_common.database import Base, integer_pk, C, rel, FK
from ekklesia_common.utils import cached_property
from sqlalchemy_utils.types import UUIDType


class BallotOption(Base):
    __tablename__ = 'ballot_option'
    uuid = C(UUIDType, server_default=func.gen_random_uuid(), primary_key=True)
    voting_uuid = C(UUIDType, FK('ballot_voting.uuid'), nullable=False)
    title = C(String)
    text = C(Text, nullable=False)

    voting = rel('BallotVoting', back_populates='options')
    votes = rel('Vote', back_populates='option')


class BallotVoting(Base):
    __tablename__ = 'ballot_voting'
    uuid = C(UUIDType, server_default=func.gen_random_uuid(), primary_key=True)
    department = C(String, nullable=False)
    title = C(String)
    created_at = C(DateTime, nullable=False, server_default=func.now())
    starts_at = C(DateTime, nullable=False)
    ends_at = C(DateTime, nullable=False)

    options = rel(BallotOption, back_populates='voting')

    def votes_to_confirm(self, auid):
        return (object_session(self)
                .query(VoteToken.token, Vote, BallotOption)
                .filter(VoteToken.auid == auid,
                        Vote.confirmed == False,
                        VoteToken.vote_uuid == Vote.uuid,
                        BallotOption.uuid == Vote.option_uuid,
                        BallotOption.voting == self)
                .order_by(Vote.yes_no.desc(), Vote.points.desc()))


class VoteToken(Base):
    __tablename__ = 'vote_token'
    token = C(UUIDType, server_default=func.gen_random_uuid(), primary_key=True)
    auid = C(UUIDType, nullable=False)
    vote_uuid = C(UUIDType, FK('vote.uuid'), nullable=False)

    vote = rel('Vote', back_populates='token')


class Vote(Base):
    __tablename__ = 'vote'
    uuid = C(UUIDType, server_default=func.gen_random_uuid(), primary_key=True)
    yes_no = C(Boolean)
    points = C(Integer, nullable=False)
    option_uuid = C(UUIDType, FK('ballot_option.uuid'), nullable=False)
    created_at = C(DateTime, nullable=False, server_default=func.now())
    confirmed = C(Boolean, nullable=False, server_default='false')

    token = rel(VoteToken, back_populates='vote')
    option = rel(BallotOption, back_populates='votes')
