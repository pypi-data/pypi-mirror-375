import io
import os
import sys
import json
import getopt
from logging.config import dictConfig
from typing import Dict, Any
from dotenv.main import DotEnv, load_dotenv
from contextlib import contextmanager

from .lib import logger


def _fix_dotenv():
    def my_get_stream(self):
        """重写python-dotenv读取文件的方法，使用utf-8，支持读取中文"""
        if isinstance(self.dotenv_path, io.StringIO):
            yield self.dotenv_path
        elif os.path.isfile(self.dotenv_path):
            with io.open(self.dotenv_path, encoding='utf-8') as stream:
                yield stream
        else:
            if self.verbose:
                print("File doesn't exist %s", self.dotenv_path)
            yield io.StringIO('')

    DotEnv._get_stream = contextmanager(my_get_stream)


def get_cmd_opts() -> Dict[str, Any]:
    """
    get commandline opts
    :return: cmd options
    """
    # get options
    # -a app / -e env / -t tag
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:],
            'a:s:f:e:t:',
            ['app=', 'script=', 'func=', 'env=', 'tag=']
        )
    except getopt.GetoptError as e:
        raise e
    t = {
        'app': '',
        'script': '',
        'func': 'start',
        'env': 'dev',
        'tag': ''
    }
    for o, a in opts:
        if o == '-e':
            t['env'] = a
        elif o == '-f':
            t['func'] = a
        elif o == '-s':
            t['script'] = a
        elif o == '-a':
            t['app'] = a
        elif o == '-t':
            t['tag'] = a
    return t


def load_cfg(app: str, script: str, func: str, env: str):
    """
    load configs
    :param func:
    :param script:
    :param app:
    :param env:
    :return:
    """
    if not env:
        raise Exception('env not specified')
    if not func:
        raise Exception('func not specified')
    if not script:
        raise Exception('script not specified')
    if not app:
        raise Exception('app not specified')
    script_file = script
    if script.endswith('.py'):
        script = script[:-3]
    if not script_file.endswith('.py'):
        script_file = f'{script}.py'
    assert os.path.exists(os.path.join(os.getcwd(), app, script_file))
    cfg_dir = os.path.join(app, 'cfg', env)
    assert os.path.isdir(cfg_dir)

    # env file
    env_file = os.path.join(cfg_dir, 'app.cfg')
    print(f"Loading env file from: {env_file}")
    load_dotenv(dotenv_path=env_file)

    # logger cfg
    logger_cfg_file = os.path.join(cfg_dir, 'logger.json')
    print(f"Loading logger config from: {logger_cfg_file}")
    logger_cfg = json.loads(open(logger_cfg_file, encoding='utf-8').read())
    assert isinstance(logger_cfg, dict)
    dictConfig(logger_cfg)

    return {
        'env': env,
        'app': app,
        'script': script,
        'script_file': script_file,
        'func': func,
        'log_config': logger_cfg,
        'env_file': env_file
    }


def init_config() -> Dict:
    _fix_dotenv()
    opts = get_cmd_opts()
    cfg = load_cfg(opts['app'], opts['script'], opts['func'], opts['env'])

    LOGGER = logger.get()
    LOGGER.info('================')
    LOGGER.info(cfg)
    LOGGER.info('================')

    return cfg
