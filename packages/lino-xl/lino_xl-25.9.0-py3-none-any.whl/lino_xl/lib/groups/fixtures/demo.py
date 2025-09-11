# -*- coding: UTF-8 -*-
# Copyright 2017-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, rt, _
from lino.utils.mldbc import babel_named as named
from lino.modlib.users.fixtures import abc


def objects():
    Group = rt.models.groups.Group
    User = rt.models.users.User
    UserTypes = rt.models.users.UserTypes

    yield named(Group, _("Hitchhiker's Guide to the Galaxy"))
    yield named(Group, _("Star Trek"))
    yield named(Group, _("Harry Potter"))

    def user(username, **kwargs):
        kwargs.update(user_type=UserTypes.user, username=username)
        if not dd.plugins.users.with_nickname:
            kwargs.pop('nickname', None)
        return User(**kwargs)

    yield abc.objects()
