import unittest
from unittest.mock import patch, MagicMock
from json import JSONDecodeError
from pygeai.lab.strategies.clients import ReasoningStrategyClient
from pygeai.core.common.exceptions import InvalidAPIResponseException


class TestReasoningStrategyClient(unittest.TestCase):
    """
    python -m unittest pygeai.tests.lab.strategies.test_clients.TestReasoningStrategyClient
    """
    def setUp(self):
        with patch('pygeai.core.base.clients.BaseClient.__init__', return_value=None):
            self.client = ReasoningStrategyClient()
        self.mock_response = MagicMock()
        self.client.api_service = MagicMock()
        self.project_id = "project-123"
        self.reasoning_strategy_id = "strat-123"
        self.reasoning_strategy_name = "TestStrategy"

    def test_list_reasoning_strategies_success(self):
        expected_response = {"strategies": [{"id": "strat-1", "name": "Strategy1"}]}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.list_reasoning_strategies(
            name="Strategy1",
            start="0",
            count="50",
            allow_external=True,
            access_scope="public"
        )

        self.assertEqual(result, expected_response)
        self.client.api_service.get.assert_called_once()
        call_args = self.client.api_service.get.call_args
        params = call_args[1]['params']
        self.assertEqual(params['name'], "Strategy1")
        self.assertEqual(params['start'], "0")
        self.assertEqual(params['count'], "50")
        self.assertTrue(params['allowExternal'])
        self.assertEqual(params['accessScope'], "public")

    def test_list_reasoning_strategies_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.mock_response.text = "Raw response text"
        self.mock_response.status_code = 500
        self.client.api_service.get.return_value = self.mock_response

        with self.assertRaises(InvalidAPIResponseException) as context:
            self.client.list_reasoning_strategies()

        self.client.api_service.get.assert_called_once()
        self.assertIn("Unable to list reasoning strategies", str(context.exception))

    def test_list_reasoning_strategies_invalid_access_scope(self):
        with self.assertRaises(ValueError) as context:
            self.client.list_reasoning_strategies(access_scope="invalid")

        self.assertEqual(str(context.exception), "Access scope must be either 'public' or 'private'.")

    def test_create_reasoning_strategy_success(self):
        name = "TestStrategy"
        system_prompt = "Test system prompt"
        access_scope = "public"
        strategy_type = "addendum"
        localized_descriptions = [{"language": "english", "description": "Test description"}]
        automatic_publish = True
        expected_response = {"id": "strat-123", "name": name}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.post.return_value = self.mock_response

        result = self.client.create_reasoning_strategy(
            project_id=self.project_id,
            name=name,
            system_prompt=system_prompt,
            access_scope=access_scope,
            strategy_type=strategy_type,
            localized_descriptions=localized_descriptions,
            automatic_publish=automatic_publish
        )

        self.assertEqual(result, expected_response)
        self.client.api_service.post.assert_called_once()
        call_args = self.client.api_service.post.call_args
        data = call_args[1]['data']['strategyDefinition']
        self.assertEqual(data['name'], name)
        self.assertEqual(data['systemPrompt'], system_prompt)
        self.assertEqual(data['accessScope'], access_scope)
        self.assertEqual(data['type'], strategy_type)
        self.assertEqual(data['localizedDescriptions'], localized_descriptions)
        self.assertIn("automaticPublish=true", call_args[1]['endpoint'])
        headers = call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)

    def test_create_reasoning_strategy_json_decode_error(self):
        name = "TestStrategy"
        system_prompt = "Test system prompt"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.mock_response.text = "Raw response text"
        self.mock_response.status_code = 500
        self.client.api_service.post.return_value = self.mock_response

        with self.assertRaises(InvalidAPIResponseException) as context:
            self.client.create_reasoning_strategy(
                project_id=self.project_id,
                name=name,
                system_prompt=system_prompt
            )

        self.client.api_service.post.assert_called_once()
        self.assertIn("Unable to create reasoning strategy", str(context.exception))

    def test_update_reasoning_strategy_success(self):
        name = "UpdatedStrategy"
        system_prompt = "Updated prompt"
        access_scope = "private"
        strategy_type = "addendum"
        localized_descriptions = [{"language": "english", "description": "Updated description"}]
        automatic_publish = True
        upsert = False
        expected_response = {"id": self.reasoning_strategy_id, "name": name}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.put.return_value = self.mock_response

        result = self.client.update_reasoning_strategy(
            project_id=self.project_id,
            reasoning_strategy_id=self.reasoning_strategy_id,
            name=name,
            system_prompt=system_prompt,
            access_scope=access_scope,
            strategy_type=strategy_type,
            localized_descriptions=localized_descriptions,
            automatic_publish=automatic_publish,
            upsert=upsert
        )

        self.assertEqual(result, expected_response)
        self.client.api_service.put.assert_called_once()
        call_args = self.client.api_service.put.call_args
        data = call_args[1]['data']['strategyDefinition']
        self.assertEqual(data['name'], name)
        self.assertEqual(data['systemPrompt'], system_prompt)
        self.assertEqual(data['accessScope'], access_scope)
        self.assertEqual(data['type'], strategy_type)
        self.assertEqual(data['localizedDescriptions'], localized_descriptions)
        self.assertIn("automaticPublish=true", call_args[1]['endpoint'])
        headers = call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)

    def test_update_reasoning_strategy_json_decode_error(self):
        name = "UpdatedStrategy"
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.mock_response.text = "Raw response text"
        self.mock_response.status_code = 500
        self.client.api_service.put.return_value = self.mock_response

        with self.assertRaises(InvalidAPIResponseException) as context:
            self.client.update_reasoning_strategy(
                project_id=self.project_id,
                reasoning_strategy_id=self.reasoning_strategy_id,
                name=name
            )

        self.client.api_service.put.assert_called_once()
        self.assertIn("Unable to update reasoning strategy", str(context.exception))

    def test_update_reasoning_strategy_invalid_access_scope(self):
        with self.assertRaises(ValueError) as context:
            self.client.update_reasoning_strategy(
                project_id=self.project_id,
                reasoning_strategy_id=self.reasoning_strategy_id,
                access_scope="invalid"
            )

        self.assertEqual(str(context.exception), "Access scope must be either 'public' or 'private'.")

    def test_update_reasoning_strategy_invalid_type(self):
        with self.assertRaises(ValueError) as context:
            self.client.update_reasoning_strategy(
                project_id=self.project_id,
                reasoning_strategy_id=self.reasoning_strategy_id,
                strategy_type="invalid"
            )

        self.assertEqual(str(context.exception), "Type must be 'addendum'.")

    def test_get_reasoning_strategy_success_with_id(self):
        expected_response = {"id": self.reasoning_strategy_id, "name": "TestStrategy"}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_reasoning_strategy(
            project_id=self.project_id,
            reasoning_strategy_id=self.reasoning_strategy_id
        )

        self.assertEqual(result, expected_response)
        self.client.api_service.get.assert_called_once()
        headers = self.client.api_service.get.call_args[1]['headers']
        self.assertEqual(headers['ProjectId'], self.project_id)

    def test_get_reasoning_strategy_success_with_name(self):
        expected_response = {"name": self.reasoning_strategy_name}
        self.mock_response.json.return_value = expected_response
        self.client.api_service.get.return_value = self.mock_response

        result = self.client.get_reasoning_strategy(
            project_id=self.project_id,
            reasoning_strategy_name=self.reasoning_strategy_name
        )

        self.assertEqual(result, expected_response)
        self.client.api_service.get.assert_called_once()

    def test_get_reasoning_strategy_json_decode_error(self):
        self.mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        self.mock_response.text = "Raw response text"
        self.mock_response.status_code = 500
        self.client.api_service.get.return_value = self.mock_response

        with self.assertRaises(InvalidAPIResponseException) as context:
            self.client.get_reasoning_strategy(
                project_id=self.project_id,
                reasoning_strategy_id=self.reasoning_strategy_id
            )

        self.client.api_service.get.assert_called_once()
        self.assertIn("Unable to retrieve reasoning strategy", str(context.exception))

    def test_get_reasoning_strategy_invalid_input(self):
        with self.assertRaises(ValueError) as context:
            self.client.get_reasoning_strategy(project_id=self.project_id)

        self.assertEqual(str(context.exception), "Either reasoning_strategy_id or reasoning_strategy_name must be provided.")

