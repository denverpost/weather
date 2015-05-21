#!/usr/bin/env python
# FTP files with python.
import os
from ftplib import FTP

class FtpWrapper():
    """ class ftpWrapper handles FTP operations. 
        Assumes the password is stored in an env var named FTP_PASS
        Currently this works best for uploading one or two files. Needs to be
        built out if it's going to handle large numbers of file uploads. 
        """

    def __init__(self, **config, user, host, upload_dir, pass_path='.ftppass', port=21):
        """ config should look something like this:
            config = {
                user: username,
                host: host,
                port: 21,
                upload_dir: path
            }
            """
        self.config = config
        self.password = os.environ.get('FTP_PASS').strip()

    def ftp_callback(self, data):
        print
        print
        print
        print data
 
    def mkdir(self, path):
        """ Create a string of directories, if the dirs don't already exist.
            """
        pass

    def send_file(self, fn):
        """ Open a connection, read a file, upload that file.
            Requires the filename.
            """
        file_h = open(fn, 'r')
        #blocksize = len(file_h.read())
        #print file_h.read()
        blocksize = 4096
        ftp = FTP(self.config['host'], self.config['user'], self.password)
        ftp.cwd(self.config['upload_dir'])
        try:
            ftp.storbinary('STOR %s' % fn, file_h, blocksize, self.ftp_callback)
            print 'SUCCESS: FTP\'d %s to %s' % (fn, self.host)
        except:
            print 'ERROR: Could not FTP-->STOR %s' % fn
        file_h.close
