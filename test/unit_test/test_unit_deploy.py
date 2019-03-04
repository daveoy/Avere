#!/usr/bin/python3
# Copyright (C) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE-CODE in the project root for license information.
# import json
import os
from datetime import datetime
from random import choice
from string import ascii_lowercase
from uuid import uuid4
import json
import pytest
import sys


@pytest.fixture
def setup(
    deploy_id=None,
    deploy_name="azurePySDK",
    location="westus2",
    resource_group=None,
    _fields={},
):
    """Testfields"""
    deploy_id = _fields.pop("deploy_id", deploy_id)
    deploy_name = _fields.pop("deploy_name", deploy_name)
    location = _fields.pop("location", location)
    resource_group = _fields.pop("resource_group", resource_group)

    if not deploy_id:
        deploy_id = (
            "av"
            + datetime.utcnow().strftime("%m%dx%H%M%S")
            + choice(ascii_lowercase)
        )

    if not resource_group:
        resource_group = deploy_id + "-rg"

    return {'deploy_id': deploy_id,
            'resource_group': resource_group}


class TestUnitDeploy:
    def test_json_vfxt_deploy(self, setup):
        # deploy template
        deploy_id = setup.get("deploy_id")
        resource_group = setup.get("resource_group")

        with open("src/vfxt/azuredeploy-auto.json") as tfile:
            schema = json.load(tfile)

        # The data to be tested:
        data = {
            "adminPassword": os.environ["AVERE_ADMIN_PW"],
            "avereBackedStorageAccountName": deploy_id + "sa",
            "avereClusterName": deploy_id + "-cluster",
            "avereClusterRole": "Avere Cluster Runtime Operator",
            "avereInstanceType": "Standard_E32s_v3",
            "avereNodeCount": 3,
            "controllerAdminUsername": "azureuser",
            "controllerAuthenticationType": "sshPublicKey",
            "controllerName": deploy_id + "-con",
            "controllerPassword": os.environ["AVERE_CONTROLLER_PW"],
            "controllerSSHKeyData": "string",
            "enableCloudTraceDebugging": True,
            "rbacRoleAssignmentUniqueId": str(uuid4()),
            "createVirtualNetwork": True,
            "virtualNetworkName": deploy_id + "-vnet",
            "virtualNetworkResourceGroup": resource_group,
            "virtualNetworkSubnetName": deploy_id + "-subnet",
        }

        testvalue = self.checkdata(schema, data)
        assert testvalue is True

    def test_json_vfxt_negative_deploy(self, setup):
        # deploy template
        deploy_id = setup.get("deploy_id")
        resource_group = setup.get("resource_group")
        with open("src/vfxt/azuredeploy-auto.json") as tfile:
            schema = json.load(tfile)

        # The data to be tested:
        data = {
            "adminPassword": os.environ["AVERE_ADMIN_PW"],
            "avereBackedStorageAccountName": deploy_id + "sa",
            "avereClusterName": deploy_id + "-cluster",
            "avereClusterRole": "Avere Cluster Runtime Operator",
            "avereInstanceType": "Standard_E32s_v3",
            "avereNodeCount": False,
            "controllerAdminUsername": "azureuser",
            "controllerAuthenticationType": "sshPublicKey",
            "controllerName": deploy_id + "-con",
            "controllerPassword": os.environ["AVERE_CONTROLLER_PW"],
            "controllerSSHKeyData": "string",
            "enableCloudTraceDebugging": 2,
            "rbacRoleAssignmentUniqueId": str(uuid4()),
            "createVirtualNetwork": True,
            "virtualNetworkName": deploy_id + "-vnet",
            "virtualNetworkResourceGroup": resource_group,
            "virtualNetworkSubnetName": deploy_id + "-subnet",
        }

        testvalue = self.checkdata(schema, data)
        assert testvalue is False

    def test_json_vdbench_deploy(self, setup):
        # deploy template
        deploy_id = setup.get("deploy_id")
        resource_group = setup.get("resource_group")
        with open("src/client/vmas/azuredeploy.json") as tfile:
            schema = json.load(tfile)

        # The data to be tested:
        data = {
            "uniquename": deploy_id,
            "sshKeyData": "sshPublicKey",
            "virtualNetworkResourceGroup": resource_group,
            "virtualNetworkName": deploy_id + "-vnet",
            "virtualNetworkSubnetName": deploy_id + "-subnet",
            "nfsCommaSeparatedAddresses": "10.0.0.4, 10.0.0.5",
            "vmCount": 12,
            "nfsExportPath": "/msazure",
            "bootstrapScriptPath": "/bootstrap/bootstrap.vdbench.sh",
        }

        testvalue = self.checkdata(schema, data)
        assert testvalue is True

    def test_json_vdbench_negative_deploy(self, setup):
        # deploy template
        deploy_id = setup.get("deploy_id")
        resource_group = setup.get("resource_group")
        with open("src/client/vmas/azuredeploy.json") as tfile:
            schema = json.load(tfile)

        # The data to be tested:
        data = {
            "uniquename": deploy_id,
            "sshKeyData": 2,
            "virtualNetworkResourceGroup": resource_group,
            "virtualNetworkName": True,
            "virtualNetworkSubnetName": deploy_id + "-subnet",
            "nfsCommaSeparatedAddresses": "10.0.0.4, 10.0.0.5",
            "vmCount": 12,
            "nfsExportPath": "/msazure",
            "bootstrapScriptPath": "/bootstrap/bootstrap.vdbench.sh",
        }

        testvalue = self.checkdata(schema, data)
        assert testvalue is False

    def checkdata(self, schema, data):
        schema_types = {}
        for k, v in schema["parameters"].items():
            if v["type"] == "securestring" or v["type"] == "string":
                type_str = "str"
            else:
                type_str = v["type"]
            schema_types[k] = {"type": type_str}

        testvalue = True
        for key, item in data.items():
            if isinstance(item, eval(schema_types[key]["type"])) or testvalue is False:
                testvalue = True
            else:
                testvalue = False
                break

        return testvalue


if __name__ == "__main__":
    pytest.main(sys.argv)