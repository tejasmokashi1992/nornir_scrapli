import pytest
from nornir.core.exceptions import NornirExecutionError
from scrapli.driver import GenericDriver
from scrapli.driver.core import IOSXEDriver
from scrapli.response import Response


def test_get_prompt(nornir, monkeypatch):
    from nornir_scrapli.tasks import get_prompt

    def mock_open(cls):
        pass

    def mock_get_prompt(cls):
        return "sea-ios-1#"

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "get_prompt", mock_get_prompt)

    result = nornir.run(task=get_prompt)
    assert result["sea-ios-1"].result == "sea-ios-1#"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_command(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_command

    def mock_open(cls):
        pass

    def mock_send_command(cls, command, strip_prompt):
        response = Response(host="fake_as_heck", channel_input=command)
        response._record_response("some stuff about whatever")
        return response

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_command", mock_send_command)

    result = nornir.run(task=send_command, command="show version")
    assert result["sea-ios-1"].result == "some stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_commands(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_commands

    def mock_open(cls):
        pass

    def mock_send_commands(cls, commands, strip_prompt):
        response = Response(host="fake_as_heck", channel_input=commands[0])
        response._record_response("some stuff about whatever")
        return [response]

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_commands", mock_send_commands)

    result = nornir.run(task=send_commands, commands=["show version"])
    assert result["sea-ios-1"][0].result == "some stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_commands_not_list(nornir_raise_on_error, monkeypatch):
    from nornir_scrapli.tasks import send_commands

    def mock_open(cls):
        pass

    def mock_acquire_priv(cls, desired_priv):
        pass

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "acquire_priv", mock_acquire_priv)

    with pytest.raises(NornirExecutionError) as exc:
        nornir_raise_on_error.run(task=send_commands, commands="show version")
    assert "expects a list of strings, got <class 'str'>" in str(exc.value)


def test_send_configs(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_configs

    def mock_open(cls):
        pass

    def mock_send_configs(cls, configs, strip_prompt):
        responses = []
        response = Response(host="fake_as_heck", channel_input=configs[0])
        response._record_response("some stuff about whatever")
        responses.append(response)
        response = Response(host="fake_as_heck", channel_input=configs[1])
        response._record_response("some stuff about whatever")
        responses.append(response)
        return [response]

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_configs", mock_send_configs)

    result = nornir.run(task=send_configs, configs=["interface loopback123", "description neat"])
    assert result["sea-ios-1"][0].result == "interface loopback123\nsome stuff about whatever"
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is True


def test_send_configs_dry_run(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_configs

    def mock_open(cls):
        pass

    def mock_acquire_priv(cls, priv):
        return

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "acquire_priv", mock_acquire_priv)

    result = nornir.run(
        task=send_configs, dry_run=True, configs=["interface loopback123", "description neat"],
    )
    assert result["sea-ios-1"].result is None
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is False


def test_send_configs_generic_driver(nornir_generic, monkeypatch):
    from nornir_scrapli.tasks import send_configs

    def mock_open(cls):
        pass

    monkeypatch.setattr(GenericDriver, "open", mock_open)

    result = nornir_generic.run(
        task=send_configs, dry_run=True, configs=["interface loopback123", "description neat"],
    )
    assert result["sea-ios-1"].result == "No config mode for 'generic' platform type"
    assert result["sea-ios-1"].failed is True
    assert result["sea-ios-1"].changed is False


def test_send_interactive(nornir, monkeypatch):
    from nornir_scrapli.tasks import send_interactive

    def mock_open(cls):
        pass

    def mock_send_interactive(cls, interact_events, failed_when_contains):
        response = Response(
            host="fake_as_heck", channel_input=", ".join([event[0] for event in interact_events]),
        )
        response._record_response("clear logg\nClear logging buffer [confirm]\n\ncsr1000v#")
        return response

    monkeypatch.setattr(IOSXEDriver, "open", mock_open)
    monkeypatch.setattr(IOSXEDriver, "send_interactive", mock_send_interactive)

    result = nornir.run(
        task=send_interactive,
        interact_events=[("clear logg", "are you sure blah blah"), ("y", "csr1000#")],
    )
    assert (
        result["sea-ios-1"].result.result
        == "clear logg\nClear logging buffer [confirm]\n\ncsr1000v#"
    )
    assert result["sea-ios-1"].failed is False
    assert result["sea-ios-1"].changed is True
