import re

import pytest

import notifiers

mock_name = 'mock_provider'


@pytest.mark.usefixtures('mock_provider')
class TestCLI:
    """CLI tests"""

    def test_bad_notify(self, cli_runner):
        """Test invalid notification usage"""
        cmd = f'{mock_name} notify'.split()
        result = cli_runner(cmd)
        assert result.exit_code == -1
        assert getattr(result, 'exception')

    def test_notify_sanity(self, cli_runner):
        """Test valid notification usage"""
        cmd = f'{mock_name} notify --required bar foo'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        assert 'Succesfully sent a notification' in result.output

    def test_providers(self, cli_runner):
        """Test providers command"""
        result = cli_runner(['providers'])
        assert result.exit_code == 0
        assert 'mock' in result.output

    def test_metadata(self, cli_runner):
        """Test metadata command"""
        cmd = f'{mock_name} metadata'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        assert '"base_url": "https://api.mock.com"' in result.output
        assert '"site_url": "https://www.mock.com"' in result.output
        assert '"name": "mock_provider"' in result.output

    def test_required(self, cli_runner):
        """Test required command"""
        cmd = f'{mock_name} required'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        assert 'required' in result.output

    def test_help(self, cli_runner):
        """Test help command"""
        cmd = f'{mock_name} notify --help'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        assert '--required' in result.output
        assert '--not-required' in result.output
        assert 'MESSAGE' in result.output

    def test_no_defaults(self, cli_runner):
        """Test defaults command"""
        cmd = 'pushover defaults'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        assert '{}' in result.output

    def test_defaults(self, cli_runner):
        """Test defaults command"""
        cmd = f'{mock_name} defaults'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        assert '"option_with_default": "foo"' in result.output

    def test_resources(self, cli_runner):
        cmd = f'{mock_name} resources'.split()
        result = cli_runner(cmd)
        assert result.exit_code == 0
        assert 'mock_rsrc' in result.output

    def test_piping_input(self, cli_runner):
        """Test piping in message"""
        cmd = f'{mock_name} notify --required foo'.split()
        result = cli_runner(cmd, input='bar')
        assert result.exit_code == 0
        assert 'Succesfully sent a notification' in result.output

    @pytest.mark.parametrize('prefix, command', [
        (None, f'{mock_name} notify'.split()),
        ('FOO_', f'--env-prefix FOO_ {mock_name} notify'.split())
    ])
    def test_environ(self, prefix, command, monkeypatch, cli_runner):
        """Test provider environ usage """
        prefix = prefix if prefix else 'NOTIFIERS_'
        monkeypatch.setenv(f'{prefix}MOCK_PROVIDER_REQUIRED', 'foo')
        monkeypatch.setenv(f'{prefix}MOCK_PROVIDER_MESSAGE', 'foo')
        result = cli_runner(command)
        assert result.exit_code == 0
        assert 'Succesfully sent a notification' in result.output

    def test_version_command(self, cli_runner):
        result = cli_runner(['--version'])
        assert result.exit_code == 0
        version_re = re.search('(\d+\.\d+\.\d+)', result.output)
        assert version_re
        assert version_re.group(1) == notifiers.__version__

    def test_multiple_option(self, cli_runner):
        cmd = f'{mock_name} notify --required foo --not-required baz --not-required piz bar'
        result = cli_runner(cmd.split())
        assert result.exit_code == 0
        assert 'Succesfully sent a notification' in result.output
