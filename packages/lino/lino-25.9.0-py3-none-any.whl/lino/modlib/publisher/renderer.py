# -*- coding: UTF-8 -*-
# Copyright 2023-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.core.renderer import add_user_language
from lino.core.renderer import HtmlRenderer

from lino.modlib.publisher.mixins import Publishable


class Renderer(HtmlRenderer):

    tableattrs = {"class": "table table-hover table-striped table-condensed"}
    cellattrs = dict(align="left", valign="top")

    can_auth = False

    def __init__(self, front_end):
        super().__init__(front_end)
        dr = front_end.site.kernel.default_renderer
        for k in ("row_action_button", "get_detail_url"):
            setattr(self, k, getattr(dr, k))

    def obj2url(self, ar, obj, **kwargs):
        if not isinstance(obj, Publishable):
            return super().obj2url(ar, obj, **kwargs)
        # if ar.actor is None or not isinstance(obj, ar.actor.model):
        add_user_language(kwargs, ar)
        # if isinstance(obj, self.front_end.site.models.publisher.Page) and obj.ref == 'index':
        if isinstance(obj, self.front_end.site.models.publisher.Page) and obj.parent is None:
            if obj.publisher_tree.ref is not None:
                if obj.publisher_tree.ref == 'index':
                    return self.front_end.buildurl(**kwargs)
                return self.front_end.buildurl(obj.publisher_tree.ref, **kwargs)
        # if obj.ref:
        #     return self.front_end.buildurl(obj.ref, **kwargs)
        loc = obj.__class__._lino_publisher_location
        if loc is None:
            # logger.warning("No location for %s", obj.__class__)
            return None
        return self.front_end.buildurl(loc, str(obj.pk), **kwargs)
        # for i in PublisherViews.get_list_items():
        #     if isinstance(obj, i.table_class.model):
        #         # print("20230409", self.__class__, i)
        #         # return "/{}/{}".format(i.publisher_location, self.pk)
        #         add_user_language(kwargs, ar)
        #         # return buildurl("/" + i.publisher_location, str(self.pk), **dd.urlkwargs())
        #         return self.front_end.buildurl(i.publisher_location, str(obj.pk), **kwargs)
        if True:
            # leave the author of a blog entry unclickable when there is no
            # publisher view,
            return None
        return self.front_end.site.kernel.default_renderer.obj2url(ar, obj, **kwargs)

    def get_home_url(self, ar, *args, **kw):
        add_user_language(kw, ar)
        return self.front_end.build_plain_url(*args, **kw)

    def get_request_url(self, ar, *args, **kwargs):
        obj = ar.selected_rows[0]
        return self.obj2url(ar, obj, **kwargs)
        # return obj.publisher_url(ar, **kwargs)
