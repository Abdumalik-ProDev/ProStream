# Video Service - ProStream

Video service supporting uploads, background transcoding, HLS, and streaming.

## Quickstart (dev)

1. Copy `.env` and edit
2. Start local infra:
   ```bash
   docker-compose up -d db minio redis zookeeper kafka