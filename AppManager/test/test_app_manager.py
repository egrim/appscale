import os
import sys
import unittest
from flexmock import flexmock

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
import app_manager
sys.path.append(os.path.join(os.path.dirname(__file__), "../../lib"))
import file_io
import appscale_info

class TestAppManager(unittest.TestCase):
  def test_start_app_badconfig(self):
    assert -1 == app_manager.start_app({})

  def test_start_app_goodconfig(self):
    configuration = {'app_name': 'test',
                     'app_port': 2000,
                     'language': 'python',
                     'load_balancer_ip': '127.0.0.1',
                     'load_balancer_port': 8080,
                     'xmpp_ip': '127.0.0.1',
                     'dblocations': ["127.0.0.1", "127.0.0.2"]}
    assert -1 != app_manager.start_app(configuration)

  def test_choose_db_location(self):
    db_locations = ['127.0.0.1']
    assert "127.0.0.1" == app_manager.choose_db_location(db_locations)
    db_locations = ['127.0.0.1', '127.0.0.2']
    assert app_manager.choose_db_location(db_locations) in db_locations
    self.assertRaises(ValueError, app_manager.choose_db_location, 
                      [])            

  def test_create_python_app_env(self):
    env_vars = app_manager.create_python_app_env('1', '2', '3') 
    assert '1' == env_vars['MY_IP_ADDRESS']
    assert '2' == env_vars['MY_PORT']
    assert '3' == env_vars['APPNAME']
    assert 0 < int(env_vars['GOMAXPROCS'])

  def test_create_python_start_cmd(self): 
    fake_secret = "XXXXXX"
    flexmock(appscale_info).should_receive('get_secret').and_return(fake_secret)
    flexmock(appscale_info).should_receive('get_private_ip')\
      .and_return('<private_ip>')
    db_locations = ['127.0.1.0', '127.0.2.0']
    app_id = 'testapp'
    cmd = app_manager.create_python_start_cmd(app_id,
                                             '127.0.0.1',
                                             '20000',
                                             '127.0.0.2',
                                             '8080',
                                             '127.0.0.3',
                                             db_locations)
    assert fake_secret in cmd
    assert app_id in cmd

  def test_create_python_stop_cmd(self): 
    fake_secret = "XXXXXX"
    port = "20000"
    flexmock(appscale_info).should_receive('get_secret').and_return(fake_secret)
    cmd = app_manager.create_python_stop_cmd(port)
    assert port in cmd 
    assert fake_secret in cmd 
    assert 'kill' in cmd

    # Test with a numerial port instead of a string
    port = 20000    
    cmd = app_manager.create_python_stop_cmd(port)
    assert str(port) in cmd 
 
  def test_stop_app(self):
    app_manager.stop_app('test')

  def test_get_app_listing(self):
    app_manager.get_app_listing()

if __name__ == "__main__":
  unittest.main()
