# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Resoler for LOM PID-fields."""

from collections.abc import Callable

from invenio_pidstore.resolver import Resolver


class LOMResolver(Resolver):
    """PIDField resolver_cls for LOM drafts/records."""

    # overwrite default pid_type with "lomid"
    # class attribute wouldn't suffice, as instance-vars take precedence
    def __init__(
        self,
        pid_type: str = "lomid",
        object_type: str | None = None,
        getter: Callable | None = None,
        *,
        registered_only: bool = True,
    ) -> None:
        """Initialize resolver.

        callable[[<LOMClass with ancestor Record>, uuid.UUID, bool], <instance of passed-in class>]
        """
        super().__init__(pid_type, object_type, getter, registered_only)
