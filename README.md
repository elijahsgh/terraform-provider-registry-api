# Simple Terraform Registry Provider Protocol Server in FastAPI

## Purpose
This is a minimal example of implementing a private provider registry for terraform using the [Terraform Provider Registry Protocol](https://www.terraform.io/docs/internals/provider-registry-protocol.html) using [FastAPI](https://fastapi.tiangolo.com/). 

This experiment implements the protocol at an extremely minimal level that is only "good enough" to mirror existing provider registries. See the documentation linked above for all of the requirements for publishing your own providers or provider forks using this protocol in a well trusted non-public network.

For ease of development this example uses already published modules that have already been signed and have shasums, etc, available publicly. If possible you should consider publishing your provider in the public [Terraform Registry](https://registry.terraform.io/). If you are developing a provider see the great guides on [HashiCorp Learn](https://learn.hashicorp.com/tutorials/terraform/provider-setup) - including how to reference a provider locally without using a provider registry.

If in doubt you should consider local references to your custom provider and the [public terraform registry](https://registry.terraform.io/).

## Terraform Registry Requirements

Providers must have shasums generated and be GPG signed. These processes are outside of the scope of this very basic project that only implements the API.

Terraform does not support interacting with the registry without TLS.

### Generating your own certificates

Generate a local certificate with SAN extension. terraform (go) will complain if the certificate uses legacy CN. Do not forget this consideration when using public certificates.

```
openssl \
  req \
  -newkey rsa:2048 -nodes \
  -keyout key.pem \
  -x509 -days 36500 -out cert.pem \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost"
```
**Remember to put your certificate into trusted hosts or it will not work**

It is up to the reader to add these certificates to their trusted certificate store for their OS. I used Enterprise Linux which involves copy the certificate and using `update-ca-trust`.

Ideally you will not be using a local certificate generate for demonstration purposes.

### Modules referenced in this registry

Two versions of the hashicorp/local provider are used in this project (see `demo.tf`). You will need to download them for this to work.

```
mkdir providers
cd providers
wget https://releases.hashicorp.com/terraform-provider-local/2.1.0/terraform-provider-local_2.1.0_linux_amd64.zip
wget https://releases.hashicorp.com/terraform-provider-local/1.4.0/terraform-provider-local_1.4.0_linux_amd64.zip
```

Inside of `providers.py` you'll find some data structures that clone the fields required by the terraform registry provider protocol. **Note that I used localhost:8001 to serve these files and you will need to change that depending on your certificate, etc**. This is pretty terrible but good enough for a basic demonstration. :)

### Starting it up
`requirements.txt` is included as per usual python workflows.

If you're new to FastAPI and aren't sure how to get things started here is an example command line:

```
uvicorn main:app --port 8001 --reload --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

# Complete demo

```
$ uvicorn main:app --port 8001 --reload --ssl-keyfile=key.pem --ssl-certfile=cert.pem &
[1] 3647518
(env) [terraform-registry-api]$ INFO:     Uvicorn running on https://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [3647518] using statreload
INFO:     Started server process [3647524]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

(env) [terraform-registry-api]$ terraform init

Initializing the backend...

Initializing provider plugins...
- Finding localhost:8001/myproviders/local versions matching "2.1.0"...
INFO:     127.0.0.1:40786 - "GET /.well-known/terraform.json HTTP/1.1" 200 OK
INFO:     127.0.0.1:40790 - "GET /v1/providers/myproviders/local/versions HTTP/1.1" 200 OK
INFO:     127.0.0.1:40794 - "GET /v1/providers/myproviders/local/2.1.0/download/linux/amd64 HTTP/1.1" 200 OK
- Installing localhost:8001/myproviders/local v2.1.0...
INFO:     127.0.0.1:40800 - "GET /providers/terraform-provider-local_2.1.0_linux_amd64.zip HTTP/1.1" 200 OK
- Installed localhost:8001/myproviders/local v2.1.0 (signed by HashiCorp)

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!
```