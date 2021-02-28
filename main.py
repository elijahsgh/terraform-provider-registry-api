from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from providers import myproviders
import os
import json

app = FastAPI()

app.mount("/providers", StaticFiles(directory="providers"), name="providers")
hostname = os.environ.get('REGISTRY_HOSTNAME', 'localhost')

@app.get("/.well-known/terraform.json")
async def get_tfjson():
    providers = {
        "providers.v1": "/v1/providers/"
    }

    return providers

@app.get("/v1/providers")
async def get_providers():
    providers = {
        "meta": {},
        "providers": []
    }

    result_keys = ["id", "namespace", "name", "version"]

    for namespace in myproviders["namespaces"]:
        for provider in myproviders["providers"][namespace].keys():
            result = dict((k, myproviders["providers"][namespace][provider][k])
                for k in result_keys)
            providers["providers"].append(result)
    
    return providers

@app.get("/v1/providers/{namespace}/{ptype}/versions")
async def get_provider_versions(namespace, ptype):
    versions = {
        "id": f'{namespace}/{ptype}',
        "versions": [],
    }

    result_keys = ["version", "protocols", "platforms"]

    for provider in myproviders["providers"][namespace].keys():
        result = dict((k, myproviders["providers"][namespace][provider][k])
            for k in result_keys)
        versions["versions"].append(result)

    return versions

@app.get("/v1/providers/{namespace}/{ptype}/{version}/download/{os}/{arch}")
async def get_provider_downloads(namespace, ptype, version, os, arch):
    return myproviders["providers"][namespace][f'{namespace}/{ptype}/{version}']["download"][f'{os}/{arch}']