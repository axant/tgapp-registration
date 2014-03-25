import functools
from tgext.pluggable import i18n

__all__ = ['p_', 'lp_', 'np_', 'lnp_']

p_ = functools.partial(i18n.ugettext, "registration")
lp_ = functools.partial(i18n.lazy_ugettext, "registration")

np_ = functools.partial(i18n.ungettext, "registration")
lnp_ = functools.partial(i18n.lazy_ungettext, "registration")
