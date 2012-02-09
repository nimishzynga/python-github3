#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from unittest import TestCase

from mock import Mock

from pygithub3.core.client import Client
from pygithub3.core.result import Result, Page
from pygithub3.tests.utils.core import (mock_paginate_github_in_GET, request,
                                        mock_no_paginate_github_in_GET)


class ResultInitMixin(object):

    def setUp(self):
        self.c = Client()
        self.get_request = Mock(side_effect=self.mock)
        self.resource_loads = request.resource.loads
        self.c.get = self.get_request
        self.r = Result(self.c, request)

    def tearDown(self):
        self.resource_loads.reset_mock()  # It mocks class method

class TestResultWithPaginate(ResultInitMixin, TestCase):

    @property
    def mock(self):
        return mock_paginate_github_in_GET

    def test_iteration_CALLS(self):
        self.assertEqual(self.get_request.call_count, 0)
        self.assertEqual(self.resource_loads.call_count, 0)
        list(self.r)
        self.get_request.assert_called_once_with(request, page=1)

    def test_consumed_are_Pages(self):
        pages_that_are_Pages = len(
            filter(lambda page: isinstance(page, Page), list(self.r)))
        self.assertEqual(pages_that_are_Pages, 3, 'There are not 3 Pages objs')
        self.assertEqual(self.resource_loads.call_count, 1)

    def test_all_iteration_CALLS(self):
        self.r.all()
        self.assertEqual(self.get_request.call_count, 3)
        self.assertEqual(self.resource_loads.call_count, 3)

    def test_CACHE_with_renew_iterations(self):
        self.r.all()
        self.r.all()
        self.assertEqual(self.get_request.call_count, 3)
        self.assertEqual(len(self.r.getter.cache), 3)
        self.assertEqual(self.resource_loads.call_count, 3)

    def test_ITERATOR_calls(self):
        self.r.iterator()
        self.assertEqual(self.get_request.call_count, 0)
        self.assertEqual(self.resource_loads.call_count, 0)


class TestResultWithoutPaginate(ResultInitMixin, TestCase):

    @property
    def mock(self):
        return mock_no_paginate_github_in_GET

    def test_iteration_stop_at_1(self):
        self.r.next()
        self.assertRaises(StopIteration, self.r.next)

    def test_get_only_1page(self):
        self.r.all()
        self.assertEqual(self.get_request.call_count, 1)
        self.assertEqual(self.resource_loads.call_count, 1)
