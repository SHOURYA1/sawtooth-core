# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import os
import shutil
import tempfile
from collections import OrderedDict
from sawtooth_settings.processor.config.settings \
    import merge_settings_config
from sawtooth_settings.processor.config.settings \
    import load_toml_settings_config
from sawtooth_settings.processor.config.settings \
    import load_default_settings_config
from sawtooth_sdk.processor.exceptions import LocalConfigurationError
from sawtooth_processor_test.transaction_processor_test_case \
    import TransactionProcessorTestCase


class TestSettings(TransactionProcessorTestCase):

    def test_load_toml_settings_config(self):
        """The test case will create the toml file, write the content in the
           file and then instantiate the object using this file.
        """
        orig_environ = dict(os.environ)
        os.environ.clear()
        directory = tempfile.mkdtemp(prefix="test-path-config-")

        try:
            os.environ['SAWTOOTH_HOME'] = directory
            config_dir = os.path.join(directory, 'etc')
            os.mkdir(config_dir)
            filename = os.path.join(config_dir, 'families_settings.toml')
            with open(filename, 'w') as fd:
                fd.write('connect= "tcp://localhost:4004"')
                fd.write(os.linesep)

            config = load_toml_settings_config(filename)
            self.assertEqual(config.connect, "tcp://localhost:4004")

        finally:
            os.environ.clear()
            os.environ.update(orig_environ)
            shutil.rmtree(directory)

    def test_load_default_settings_config(self):
        """Tests the default configuration.
           connect = "tcp://localhost:4004"
        """
        settings = load_default_settings_config()
        self.assertEqual(settings.connect, 'tcp://localhost:4004')

    def test_load_toml_settings_config_filename_not_exists(self):
        """This test will test the condition when the toml is not present
           at the path provided.
        """
        orig_environ = dict(os.environ)
        os.environ.clear()
        directory = tempfile.mkdtemp(prefix="test-path-config-")

        try:
            os.environ['SAWTOOTH_HOME'] = directory
            config_dir = os.path.join(directory, 'etc')
            os.mkdir(config_dir)
            filename = os.path.join(config_dir, 'families_settings.toml')
            config = load_toml_settings_config(filename)
            self.assertEqual(config.connect, None)
        finally:
            os.environ.clear()
            os.environ.update(orig_environ)
            shutil.rmtree(directory)

    def test_invalid_load_toml_settings_config(self):
        """The test case will create the toml file write the invalid content in
           the file and then instantiate the object through this file.
        """
        orig_environ = dict(os.environ)
        os.environ.clear()
        directory = tempfile.mkdtemp(prefix="test-path-config-")

        try:
            os.environ['SAWTOOTH_HOME'] = directory
            config_dir = os.path.join(directory, 'etc')
            os.mkdir(config_dir)
            filename = os.path.join(config_dir, 'families_settings.toml')

            with open(filename, 'w') as fd:
                fd.write('invalid = " false value"')
                fd.write(os.linesep)

            with self.assertRaises(LocalConfigurationError):
                load_toml_settings_config(filename)

        finally:
            os.environ.clear()
            os.environ.update(orig_environ)
            shutil.rmtree(directory)

    def test_merge_settings_config(self):
        """This test will take SettingConfig object's list as input,merge them
           and then return a single object, also tests the _repr,to_dict(),
           to_toml_string() functions.
        """
        setting_conf_list = []
        for settings in range(0, 2):
            setting_conf_list.insert(settings, load_default_settings_config())
        load = merge_settings_config(setting_conf_list)
        dict_configs = OrderedDict([('connect', 'tcp://localhost:4004')])
        toml_str = ['connect = "tcp://localhost:4004"']
        self.assertEqual(load.connect, 'tcp://localhost:4004')
        settings_dict = merge_settings_config(setting_conf_list).to_dict()
        toml_string = merge_settings_config(setting_conf_list).to_toml_string()
        self.assertEqual(dict_configs, settings_dict)
        self.assertEqual(toml_str, toml_string)
