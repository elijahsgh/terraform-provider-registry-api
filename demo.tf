terraform {
    required_providers {
        local = {
            source = "localhost:8001/myproviders/local"
            version = "2.1.0"
        }
    }
}

provider local {}
