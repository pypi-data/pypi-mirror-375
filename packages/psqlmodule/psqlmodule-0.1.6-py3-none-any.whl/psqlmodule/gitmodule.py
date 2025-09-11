import os, json, sys, subprocess
from psqlmodule.inputmodule import *
import psqlmodule.logger, logging

class gitmodule():
    i = inputmodule()


    def __init__(self):
        ret = self.i.get_data()
        if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        self.data = ret['data']


    def git_clone(self, repo, branch, path='/tmp/'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            tmp_folder = os.path.join(path, os.path.basename(repo))
            tmp_folder = tmp_folder.rstrip('.git')
            subprocess.run(f'rm -rf {tmp_folder}', shell=True, check=True)
            subprocess.run(f'cd {path}; git clone {repo}; cd {tmp_folder}; git checkout {branch};', shell=True, check=True)
            ret_data['data'] = tmp_folder
        except:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def git_pull(self, repo):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self.i.get_data(key=repo)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            gitrepo = ret['data']['repo']
            subprocess.run('cd %s; git pull' %gitrepo, shell=True, check=True)
        except:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data
 
      
    def git_pull_k8s(self, repo):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self.i.get_data(key=repo)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            gitrepo = ret['data']['k8s_repo']
            subprocess.run('cd %s; git pull' %gitrepo, shell=True, check=True)
        except:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data
 
      
    def get_git_log(self, repo, level=1):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try: 
            ret = self.i.get_data(key=repo)
            if ret['data'] == 'failed': raise Exception(ret['err_msg'])
            gitrepo = ret['data']['repo']
            gitlog = None
            gitlog = subprocess.run('cd %s; git log -%s' %(gitrepo, level), shell=True, check=True, capture_output=True, text=True)
            gitlog = gitlog.stdout
            ret_data['data'] = gitlog
        except:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def get_commit_msg(self, repo):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self.git_pull(repo=repo)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.get_git_log(repo=repo)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            commit_msg = '\n'.join(ret['data'].split('\n')[4::])
            ret_data['data'] = commit_msg
        except:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def commit_build_version(self, build_version):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            version_file = self.data['version_file']
            repo = self.fe['repo']
            subprocess.run('cd %s; git add %s; git commit -m "Adding new build version = %s"; git push origin main' %(repo, version_file, build_version), shell=True, check=True) 
        except:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data
