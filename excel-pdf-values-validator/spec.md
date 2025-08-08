AI Validation UI & Workflow for Flex CTS - Specification

Overview

This document defines the behavior and implementation specification for a simple AI validation utility to be integrated with Flex CTS. The goal is to:

Generate semantic embeddings from output PDFs.

Validate Excel-derived values against semantically retrieved values from PDFs.

Use FastAPI endpoints to trigger backend logic.

Use pgVector/PostgreSQL as the vector store.

UI Requirements

A minimal single-screen application/UI should include:

Two Buttons:

Create Embeddings

Validate

One Result Textbox:

Displays validation results after a run

FastAPI Endpoints

1. POST /create-embeddings

Purpose: Ingest a selected PDF file, chunk it, create semantic embeddings, and store them in pgVector with metadata.

Client Behavior:

Prompts user to select PDF file.

Sends file to FastAPI.

Backend Behavior:

Parses the PDF.

Chunks content into semantically coherent groups (line- or section-based).

Embeds using bge-small-en or MiniLM (CPU-compatible).

Stores in pgVector with metadata:

config_id, file_name, pdf_path, chunk_text, embedding, created_at, etc.

Return: Success or failure status.

2. POST /validate

Purpose: Compare Excel values to the semantically closest chunks in the given PDF.

Client Behavior:

Prompts user to select:

PDF File

Excel File

Sends both to FastAPI

Backend Behavior:

Extracts output values from Excel.

Identifies the matching embedding record based on file name or config metadata.

Retrieves relevant chunks from pgVector.

Compares extracted values using regex + tolerance.

Generates a .txt result file.

Return:

The .txt result file as a streamed response.

Contents also returned as string for display in textbox.

Backend Stack

Language: Python (FastAPI)

Model: BAAI/bge-small-en-v1.5 or sentence-transformers/all-MiniLM-L6-v2

Vector Store: pgVector (inside PostgreSQL)

PDF Parsing: PyMuPDF (preferred)

Excel Parsing: openpyxl

Embedding: sentence-transformers

Chunk Strategy: 5-10 line blocks or layout-keyword anchored

PostgreSQL Schema (pgvector enabled)

CREATE TABLE pdf_chunks (
  id SERIAL PRIMARY KEY,
  config_id TEXT,
  file_name TEXT,
  chunk_text TEXT,
  embedding VECTOR(384),
  created_at TIMESTAMP DEFAULT now()
);

Result File Example

A .txt file is generated with this structure:

=== Validation Report ===
Config ID: BDN_16
PDF: BunkerDeliveryNote.pdf
Excel: output_parameters.xlsx

✔️ Gross Energy: Excel = 714, PDF = 714.0 [PASS]
❌ Net Energy: Excel = -2523, PDF = -2450 [FAIL]
...

Summary: 20 fields checked | 18 passed | 2 failed

Containerization Notes

All components should run inside a Docker container.

Python container should:

Include FastAPI

torch, sentence-transformers, PyMuPDF, openpyxl

Access the postgresql container with pgvector extension enabled

PostgreSQL:

Use official image with pgvector plugin

Mount a volume for persistence

Optionally use docker-compose to coordinate services

Output

A result file will be downloaded via the browser.

Contents are streamed back to the Angular textbox after the /validate endpoint completes.

Dependencies

Python 3.10+

sentence-transformers

PyMuPDF

openpyxl

psycopg2 / asyncpg

pgvector extension enabled in PostgreSQL

