# coding: utf-8
"""Testing utilities."""

import json

from django import forms
from django.core import management
from django.test import TestCase
from django.test.client import Client

from modoboa.lib import parameters


class ModoTestCase(TestCase):

    """All test cases must inherit from this one."""

    def setUp(self, username="admin", password="password"):
        management.call_command("load_initial_data")
        self.clt = Client()
        self.assertEqual(
            self.clt.login(username=username, password=password), True)

    def ajax_request(self, method, url, params=None, status=200):
        if params is None:
            params = {}
        response = getattr(self.clt, method)(
            url, params, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, status)
        return json.loads(response.content)

    def ajax_post(self, *args, **kwargs):
        return self.ajax_request('post', *args, **kwargs)

    def ajax_put(self, *args, **kwargs):
        return self.ajax_request('put', *args, **kwargs)

    def ajax_delete(self, *args, **kwargs):
        return self.ajax_request('delete', *args, **kwargs)

    def ajax_get(self, *args, **kwargs):
        return self.ajax_request('get', *args, **kwargs)


class TestParams(parameters.AdminParametersForm):
    app = "test"

    param1 = forms.CharField(label="Test", initial="toto")
    param2 = forms.IntegerField(label="Int", initial=42)

    def update_param2(self, value):
        raise RuntimeError("new value %d" % value)


class TestUserParams(parameters.UserParametersForm):
    app = "test"

    param1 = forms.CharField(label="Test", initial="titi")
    param2 = forms.IntegerField(label="Int", initial=42)

    def update_param2(self, value):
        raise RuntimeError("new value %d" % value)


class ParameterTestCase(TestCase):
    """Simple test cases for ``modoboa.lib.parameters`` module.
    """

    def setUp(self):
        from modoboa.core.models import User
        parameters.register(TestParams, "Test")
        parameters.register(TestUserParams, "TestUser")
        self.user = User.objects.create(username="tester")

    def test_register_form(self):
        self.assertIn("test", parameters._params['A'])

    def test_unregister(self):
        parameters.unregister("test")
        self.assertNotIn("test", parameters._params['A'])

    def test_get_parameter_form(self):
        self.assertIs(
            parameters.get_parameter_form('A', 'PARAM1', 'test'),
            TestParams
        )

    def test_save_admin(self):
        parameters.save_admin("PARAM1", "45", app="test")
        self.assertEqual(parameters.get_admin("PARAM1", app="test"), "45")

    def test_update_param(self):
        with self.assertRaisesRegexp(RuntimeError, "new value 35"):
            parameters.save_admin("PARAM2", 35, app="test")

    def test_get_admin(self):
        self.assertEqual(parameters.get_admin("PARAM1", "test"), "toto")
        with self.assertRaises(parameters.NotDefined):
            parameters.get_admin("TOTO", "test")

    def test_get_user(self):
        self.assertEqual(
            parameters.get_user(self.user, "PARAM1", "test"), "titi")
        with self.assertRaises(parameters.NotDefined):
            parameters.get_user(self.user, "TOTO", "test")

    def test_save_user(self):
        parameters.save_user(self.user, "PARAM1", "pouet", "test")
        self.assertEqual(
            parameters.get_user(self.user, "PARAM1", "test"), "pouet")
