# lemvi-crypto-risk-management

## Project installation
> pip -r install local-requirements.txt

## Prerequisites
Following environment variables are required:
- BITMEX_API_SECRET_KEY, BITMEX_API_ACCESS_KEY
- DERIBIT_API_SECRET_KEY, DERIBIT_API_ACCESS_KEY
- OKEX_API_SECRET_KEY, OKEX_API_ACCESS_KEY

- GOOGLE_CLOUD_PROJECT (including on GCE environment)
- BUCKET_NAME_PORTFOLIO for storing portfolio files suach as orders and portfolio transactions

*GCE environment only:*
- GOOGLE_FUNCTION_SOURCE: entrypoints.py

## Topic Ids
- job-order-data-import
- job-wallet-data-import
