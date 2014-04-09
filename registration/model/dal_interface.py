from abc import ABCMeta, abstractmethod


class DalIntegrityError(Exception):
    pass


class IRegistration:
    __metaclass__ = ABCMeta

    @abstractmethod
    def clear_expired(self):
        raise NotImplementedError

    @abstractmethod
    def pending_activation(self):
        raise NotImplementedError

    @abstractmethod
    def new(self, **kw):
        raise NotImplementedError

    @abstractmethod
    def by_email(self, email):
        raise NotImplementedError

    @abstractmethod
    def get_inactive(self, code):
        raise NotImplementedError

    @abstractmethod
    def out_of_uow_flush(self, entity):
        raise NotImplementedError

    @abstractmethod
    def get_user_by_email(self, email_address):
        raise NotImplementedError

    @abstractmethod
    def get_user_by_user_name(self, user_name):
        raise NotImplementedError
