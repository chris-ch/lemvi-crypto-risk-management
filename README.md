# lemvi-crypto-risk-management

## Project installation
> pip -r install local-requirements.txt

## Deploying indices on DataStore
> gcloud app deploy resources/index.yaml

## Prerequisites
Following environment variables are required:
- BITMEX_API_SECRET_KEY, BITMEX_API_ACCESS_KEY
- DERIBIT_API_SECRET_KEY, DERIBIT_API_ACCESS_KEY
- OKEX_API_SECRET_KEY, OKEX_API_ACCESS_KEY

- GOOGLE_CLOUD_PROJECT (including on GCE environment)
- NAMESPACE_PORTFOLIO for storing portfolio files such as orders and portfolio transactions

*GCE environment only:*
- GOOGLE_FUNCTION_SOURCE:
  - entrypoints.py for HTTP endpoints
  - subscribers.py for PubSub subscribers

## Topic Ids
- job-order-data-import
- job-wallet-data-import
