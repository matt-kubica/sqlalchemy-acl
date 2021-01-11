#!/bin/bash
docker run --name test-postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d postgres