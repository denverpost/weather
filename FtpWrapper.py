#!/usr/bin/env python
# FTP files with python.
from ftplib import FTP

class FtpWrapper():
    """ class ftpWrapper handles FTP operations. Assumes the password is stored
        in a file named '.ftppass' in the class directory. 
        Currently this works best for uploading one or two files. Needs to be
        built out if it's going to handle large numbers of file uploads. 
        """

    def __init__(self, user, host, upload_dir, pass_path='.ftppass', port=21):
        self.user = user
        self.host = host
        self.upload_dir = upload_dir

        file_h = open(pass_path, 'r')
        self.password = file_h.read().strip()
        file_h.close

        self.port = port

    def ftp_callback(self, data):
        print
        print
        print
        print data
 
    def ftp_file(self, fn):
        """ Open a connection, read a file, upload that file.
            Requires the filename.
            """
        file_h = open(fn, 'r')
        #blocksize = len(file_h.read())
        #print file_h.read()
        blocksize = 4096
        ftp = FTP(self.host, self.user, self.password)
        ftp.cwd(self.upload_dir)
        try:
            ftp.storbinary('STOR %s' % fn, file_h, blocksize, self.ftp_callback)
            print 'SUCCESS: FTP\'d %s to %s' % (fn, self.host)
        except:
            print 'ERROR: Could not FTP-->STOR %s' % fn
        file_h.close
