#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2017, Alice Ferrazzi <alice.ferrazzi@gmail.com>
# Distributed under the terms of the GNU General Public License v2 or later


import uuid

import os
import werkzeug
from flask import jsonify, make_response
from flask_restful import Resource, reqparse, fields, marshal

from elivepatch_server.resources.livepatch import PaTch

pack_fields = {
    'KernelVersion': fields.String,
    'LivepatchStatus': fields.String,
    'UserID': fields.String

}

packs = {
    'id': 1,
    'KernelVersion': None,
    'LivepatchStatus': None,
    'UserID': None
}


def set_kernel_dir(uuid, kernel_ID):
    kernel_absolute_path = 'linux-' + str(kernel_ID) + '-gentoo'
    kernel_path = os.path.join('/tmp/', 'elivepatch-' + uuid, 'usr', 'src', kernel_absolute_path)
    lpatch.set_kernel_dir(kernel_path)

lpatch = PaTch()
kernel_dir = lpatch.get_kernel_dir()

class BuildLivePatch(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('KernelVersion', type=str, required=False,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('LivepatchStatus', type=str, required=False,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('UserID', type=str, required=False,
                                   help='No task title provided',
                                   location='json')
        super(BuildLivePatch, self).__init__()
        pass

    def get(self):
        # lpatch.build_livepatch(kernel_dir, kernel_dir + '/vmlinux')
        return {'packs': [marshal(pack, pack_fields) for pack in packs]}

    def post(self):
        args = self.reqparse.parse_args()
        if not args['UserID']:
            args['UserID'] = id_generate()
        else:
            print('UserID: ' + str(args['UserID']))
        if args['KernelVersion']:
            set_kernel_dir(args['UserID'], args['KernelVersion'])
            kernel_config = lpatch.get_config()
            kernel_patch = lpatch.get_patch()
            if kernel_config and kernel_patch:
                lpatch.set_lp_status('working')
                print("build livepatch: " + str(args))
                # check vmlinux presence if not rebuild the kernel
                lpatch.get_kernel_sources(args['UserID'], args['KernelVersion'])
                lpatch.build_livepatch(args['UserID'], 'vmlinux')
        pack = {
            'id': packs['id'] + 1,
            'KernelVersion': args['KernelVersion'],
            'LivepatchStatus': lpatch.livepatch_status,
            'UserID' : args['UserID']
        }
        return {'build_livepatch': marshal(pack, pack_fields)}, 201


class SendLivePatch(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('KernelVersion', type=str, required=False,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('UserID', type=str, required=False,
                                   help='No task title provided',
                                   location='json')
        super(SendLivePatch, self).__init__()
        pass

    def get(self):
        args = self.reqparse.parse_args()
        print("get livepatch: " + str(args))
        # check if is a new user
        if not args['UserID']:
            args['UserID'] = id_generate()
        else:
            print('UserID: ' + str(args['UserID']))
        # Getting livepatch build status
        with open('kpatch-1.ko', 'rb') as fp:
            response = make_response(fp.read())
            response.headers['content-type'] = 'application/octet-stream'
            return response

    def post(self):
        return make_response(jsonify({'message': 'These are not the \
        patches you are looking for'}), 403)


class GetFiles(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('KernelVersion', type=str, required=False,
                                   help='No task title provided',
                                   location='headers')
        self.reqparse.add_argument('UserID', type=str, required=False,
                                   help='No task title provided',
                                   location='headers')
        super(GetFiles, self).__init__()
        pass

    def get(self):
        return make_response(jsonify({'message': 'These are not the \
        patches you are looking for'}), 403)

    def post(self):
        args = self.reqparse.parse_args()
        if not args['UserID']:
            args['UserID'] = str(id_generate())
        else:
            print('UserID: ' + str(args['UserID']))
        parse = reqparse.RequestParser()
        parse.add_argument('patch', type=werkzeug.datastructures.FileStorage,
                           location='files')
        parse.add_argument('config', type=werkzeug.datastructures.FileStorage,
                           location='files')
        file_args = parse.parse_args()
        print("file get config: " + str(file_args))
        configFile = file_args['config']
        configFile_name = file_args['config'].filename

        patchFile = file_args['patch']
        patchFile_name = file_args['patch'].filename

        configFile_name = os.path.join('/tmp','elivepatch-' + args['UserID'], configFile_name)
        if not os.path.exists('/tmp/elivepatch-' + args['UserID']):
            os.makedirs('/tmp/elivepatch-' + args['UserID'])
        configFile.save(configFile_name)
        lpatch.set_config(configFile_name)

        patchFile_name = os.path.join('/tmp','elivepatch-' + args['UserID'], patchFile_name)
        if not os.path.exists('/tmp/elivepatch-' + args['UserID']):
            os.makedirs('/tmp/elivepatch-' + args['UserID'])
        patchFile.save(patchFile_name)
        lpatch.set_patch(patchFile_name)

        pack = {
           'id': packs['id'] + 1,
            'KernelVersion': None,
            'UserID' : args['UserID']
        }
        return {'get_config': marshal(pack, pack_fields)}, 201


class GetID(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('UserID', type=str, required=False,
                                   help='No task title provided',
                                   location='json')
        super(GetID, self).__init__()
        pass

    def get(self):
        return make_response(jsonify({'message': 'These are not the \
        patches you are looking for'}), 403)

    def post(self):
        args = self.reqparse.parse_args()
        print("get ID: " + str(args))


def id_generate():
    UserID = uuid.uuid4()
    return UserID
