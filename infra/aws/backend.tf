terraform {
  backend "s3" {
    bucket = "edn.tf-state"
    key    = "terraform/state/locust"
    dynamodb_table = "edn.tf-lock"
    region = "us-east-1"
  }
}

