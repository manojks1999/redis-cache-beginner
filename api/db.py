# db orm exceptions
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError

# query class
from sqlalchemy.orm.query import Query as _Query

# utils
from time import sleep

class RetryingQuery(_Query):
    """
    Custom query retrying class.
    """

    # max retries for query
    __max_retry_count__ = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __iter__(self):
        # retry attempts
        attempts = 0
        max_attempts = 5
        # retry logic
        while attempts <= max_attempts:
            # increment attempt count
            attempts += 1
            try:
                # try running query
                return super().__iter__()
            except SQLAlchemyError as e:
                # get error
                error = str(e.__dict__["orig"])
                # rollback session
                self.session.rollback()
                # wait
                sleep(15)
                
        # if max_attemps reached delete session
        self.session.close()
        # sleep
        sleep(60)
